# Redis 7 replication group: TLS in transit, AUTH token, encrypted at rest.
# One node in staging; primary + replica with automatic failover in production.

resource "aws_elasticache_subnet_group" "this" {
  name       = var.name
  subnet_ids = var.subnet_ids
}

resource "aws_elasticache_replication_group" "this" {
  replication_group_id       = var.name
  description                = "Cache, rate limits and token revocation for ${var.name}"
  engine                     = "redis"
  engine_version             = "7.1"
  node_type                  = var.node_type
  num_cache_clusters         = var.nodes
  automatic_failover_enabled = var.nodes > 1
  multi_az_enabled           = var.nodes > 1
  port                       = 6379
  subnet_group_name          = aws_elasticache_subnet_group.this.name
  security_group_ids         = [var.security_group_id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = var.auth_token
  snapshot_retention_limit   = var.nodes > 1 ? 3 : 0
  apply_immediately          = true
}
