#!/usr/bin/env bash
# Usage: scripts/aws/sync-static.sh <env> <tag> — publish Nuxt static assets to S3 before the release.
source "$(dirname "$0")/_common.sh"
require aws docker
load_env "${1:-}"
TAG="${2:?tag required}"

tmp="$(mktemp -d)"
cid="$(docker create "$(image_uri frontend "$TAG")")"
trap 'docker rm -f "$cid" >/dev/null; rm -rf "$tmp"' EXIT
docker cp "$cid:/app/.output/public" "$tmp/public"

# Hashed bundles: cached for a year and never deleted (pages still open may request old ones).
aws s3 sync "$tmp/public/_nuxt" "s3://$ASSETS_BUCKET/_nuxt" --cache-control "public,max-age=31536000,immutable"
aws s3 sync "$tmp/public" "s3://$ASSETS_BUCKET" --exclude "_nuxt/*" --cache-control "public,max-age=300"
log "static assets synced to s3://$ASSETS_BUCKET"
