# Production: two tasks per service minimum, NAT per AZ, Multi-AZ database, Redis replica (plan §15.5).
environment                 = "prod"
azs                         = ["ap-southeast-1a", "ap-southeast-1b"]
vpc_cidr                    = "10.20.0.0/16"
zone_name                   = "example.com"        # replace
domain                      = "app.example.com"    # replace
github_repository           = "your-org/re-portal" # replace
create_github_oidc_provider = false                # already created by staging in the same account
alert_email                 = "alerts@example.com" # replace
monthly_budget_usd          = 450

sizing = {
  nat_per_az          = true
  web                 = { cpu = 512, memory = 1024, min = 2, max = 4 }
  api                 = { cpu = 512, memory = 1024, min = 2, max = 6 }
  db_instance_class   = "db.t4g.small"
  db_multi_az         = true
  db_backup_days      = 14
  redis_node_type     = "cache.t4g.small"
  redis_nodes         = 2
  deletion_protection = true
}
