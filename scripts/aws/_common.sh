#!/usr/bin/env bash
# Shared helpers for scripts/aws/*. Source it; do not execute it.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC2034  # shared variables, used by the scripts that source this file
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
readonly PROJECT="re-portal"
# shellcheck disable=SC2034
readonly SERVICES=(backend frontend)
export AWS_REGION="${AWS_REGION:-ap-southeast-1}"
export AWS_PAGER=""

log() { printf '\033[1;34m[%s]\033[0m %s\n' "$(date +%H:%M:%S)" "$*"; }
die() { printf '\033[1;31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }
require() { for cmd in "$@"; do command -v "$cmd" >/dev/null || die "missing tool: $cmd"; done; }

# load_env <staging|prod> — exports CLUSTER, ECR_REGISTRY, ASSETS_BUCKET, PRIVATE_SUBNETS, API_SG,
# DOMAIN from SSM (/re-portal/<env>/deploy/*), written by the Terraform module deploy-params.
load_env() {
  ENV="${1:-}"
  [[ "$ENV" =~ ^(staging|prod)$ ]] || die "env must be 'staging' or 'prod' (got '${ENV}')"
  local prefix="/${PROJECT}/${ENV}/deploy" name value
  while IFS=$'\t' read -r name value; do
    [[ -n "$name" ]] && export "${name##*/}=${value}"
  done < <(aws ssm get-parameters-by-path --path "$prefix" --query 'Parameters[].[Name,Value]' --output text)
  for var in CLUSTER ECR_REGISTRY ASSETS_BUCKET PRIVATE_SUBNETS API_SG DOMAIN; do
    [[ -n "${!var:-}" ]] || die "missing SSM parameter ${prefix}/${var}; run 'scripts/aws/infra.sh apply ${ENV}' first"
  done
}

family() { echo "${PROJECT}-${ENV}-$1"; }                     # ECS service == task family
image_uri() { echo "${ECR_REGISTRY}/${PROJECT}-${ENV}-$1:$2"; } # ECR repo per environment

# register_task_def <service> <tag> — clone the current task definition with a new image; print its ARN.
register_task_def() {
  local svc="$1" tag="$2" current
  current="$(aws ecs describe-task-definition --task-definition "$(family "$svc")" --query taskDefinition --output json)"
  jq --arg img "$(image_uri "$svc" "$tag")" '
      .containerDefinitions[0].image = $img
      | del(.taskDefinitionArn, .revision, .status, .requiresAttributes,
            .compatibilities, .registeredAt, .registeredBy)' <<<"$current" |
    aws ecs register-task-definition --cli-input-json file:///dev/stdin \
      --query taskDefinition.taskDefinitionArn --output text
}

# run_backend_task <task-def-arn> <command...> — one-off Fargate task (migrations, seed); fails on non-zero exit.
run_backend_task() {
  local task_def="$1"
  shift
  local command_json task_arn exit_code
  command_json="$(jq -cn '$ARGS.positional' --args "$@")"
  task_arn="$(aws ecs run-task --cluster "$CLUSTER" --launch-type FARGATE \
    --task-definition "$task_def" \
    --network-configuration "awsvpcConfiguration={subnets=[${PRIVATE_SUBNETS}],securityGroups=[${API_SG}],assignPublicIp=DISABLED}" \
    --overrides "{\"containerOverrides\":[{\"name\":\"backend\",\"command\":${command_json}}]}" \
    --query 'tasks[0].taskArn' --output text)"
  log "one-off task $task_arn: $*"
  aws ecs wait tasks-stopped --cluster "$CLUSTER" --tasks "$task_arn"
  exit_code="$(aws ecs describe-tasks --cluster "$CLUSTER" --tasks "$task_arn" \
    --query 'tasks[0].containers[0].exitCode' --output text)"
  [[ "$exit_code" == "0" ]] || die "'$*' failed (exit ${exit_code}); see log group /ecs/$(family backend)"
}
