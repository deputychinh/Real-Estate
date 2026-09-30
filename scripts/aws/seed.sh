#!/usr/bin/env bash
# Usage: scripts/aws/seed.sh <env> [--reset] — load demo data with the running backend image.
source "$(dirname "$0")/_common.sh"
require aws jq
load_env "${1:-}"
[[ "$ENV" == "prod" ]] && die "demo data is for staging only"
task_def="$(aws ecs describe-services --cluster "$CLUSTER" --services "$(family backend)" \
  --query 'services[0].taskDefinition' --output text)"
run_backend_task "$task_def" python -m scripts.seed "${@:2}"
log "demo data loaded"
