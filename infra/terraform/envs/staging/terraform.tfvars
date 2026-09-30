# Staging: smallest sizes, single NAT, no Multi-AZ (plan §15.5, ≈ USD 150/month).
environment                 = "staging"
azs                         = ["ap-southeast-1a", "ap-southeast-1b"]
vpc_cidr                    = "10.10.0.0/16"
zone_name                   = "example.com"         # replace with your hosted zone
domain                      = "staging.example.com" # replace
github_repository           = "your-org/re-portal"  # replace
create_github_oidc_provider = true
alert_email                 = "alerts@example.com" # replace
monthly_budget_usd          = 180

sizing = {
  nat_per_az          = false
  web                 = { cpu = 256, memory = 512, min = 1, max = 2 }
  api                 = { cpu = 256, memory = 512, min = 1, max = 2 }
  db_instance_class   = "db.t4g.micro"
  db_multi_az         = false
  db_backup_days      = 7
  redis_node_type     = "cache.t4g.micro"
  redis_nodes         = 1
  deletion_protection = false
}
