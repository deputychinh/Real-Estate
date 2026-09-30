#!/usr/bin/env bash
# Usage: scripts/aws/deploy.sh <staging|prod> [tag]   (tag defaults to the current git SHA)
# build → push → register task defs → sync assets → migrate → release (backend first) → wait → smoke test
source "$(dirname "$0")/_common.sh"
require aws docker jq git curl
load_env "${1:-}"
TAG="${2:-$(git -C "$ROOT_DIR" rev-parse --short=12 HEAD)}"
if [[ -n "$(git -C "$ROOT_DIR" status --porcelain)" && -z "${ALLOW_DIRTY:-}" ]]; then
  die "working tree is dirty; commit first or set ALLOW_DIRTY=1"
fi

log "deploying $TAG to $ENV"
"$SCRIPT_DIR/build-push.sh" "$ENV" "$TAG"

backend_def="$(register_task_def backend "$TAG")"
frontend_def="$(register_task_def frontend "$TAG")"
log "task definitions: $backend_def, $frontend_def"

"$SCRIPT_DIR/sync-static.sh" "$ENV" "$TAG"     # assets first: new HTML must find its bundles
"$SCRIPT_DIR/migrate.sh" "$ENV" "$backend_def" # stop here if the schema change fails

# Backend first: the new frontend may call new endpoints.
aws ecs update-service --cluster "$CLUSTER" --service "$(family backend)" --task-definition "$backend_def" >/dev/null
aws ecs update-service --cluster "$CLUSTER" --service "$(family frontend)" --task-definition "$frontend_def" >/dev/null
log "waiting for services to become stable…"
aws ecs wait services-stable --cluster "$CLUSTER" --services "$(family backend)" "$(family frontend)"

"$SCRIPT_DIR/smoke-test.sh" "$ENV"
log "$TAG is live on https://$DOMAIN"
