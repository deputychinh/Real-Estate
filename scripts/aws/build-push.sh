#!/usr/bin/env bash
# Usage: scripts/aws/build-push.sh <env> <tag> — build both images for linux/amd64 and push to ECR.
source "$(dirname "$0")/_common.sh"
require aws docker
load_env "${1:-}"
TAG="${2:?tag required}"

aws ecr get-login-password | docker login --username AWS --password-stdin "$ECR_REGISTRY"
for svc in "${SERVICES[@]}"; do
  log "build $svc:$TAG"
  docker buildx build --platform linux/amd64 --push -t "$(image_uri "$svc" "$TAG")" "$ROOT_DIR/$svc"
done
