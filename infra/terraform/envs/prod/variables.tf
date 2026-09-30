variable "project" {
  type    = string
  default = "re-portal"
}

variable "environment" {
  type = string
}

variable "region" {
  type    = string
  default = "ap-southeast-1"
}

variable "azs" {
  type = list(string)
}

variable "vpc_cidr" {
  type = string
}

variable "zone_name" {
  type = string
}

variable "domain" {
  type = string
}

variable "github_repository" {
  type = string
}

variable "create_github_oidc_provider" {
  type = bool
}

variable "alert_email" {
  type = string
}

variable "monthly_budget_usd" {
  type = number
}

variable "sizing" {
  type = object({
    nat_per_az          = bool
    web                 = object({ cpu = number, memory = number, min = number, max = number })
    api                 = object({ cpu = number, memory = number, min = number, max = number })
    db_instance_class   = string
    db_multi_az         = bool
    db_backup_days      = number
    redis_node_type     = string
    redis_nodes         = number
    deletion_protection = bool
  })
}
