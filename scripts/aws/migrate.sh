#!/usr/bin/env bash
# Usage: scripts/aws/migrate.sh <env> <backend-task-def-arn>
# Runs Alembic with the NEW image before traffic moves. Migrations must stay backward compatible
# (expand/contract), because the old code keeps serving until the release finishes.
source "$(dirname "$0")/_common.sh"
require aws jq
load_env "${1:-}"
run_backend_task "${2:?task definition ARN required}" alembic upgrade head
log "migrations applied"
