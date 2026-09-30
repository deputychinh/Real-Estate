variable "name" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "security_group_id" {
  type = string
}

variable "node_type" {
  type    = string
  default = "cache.t4g.micro"
}

variable "nodes" {
  description = "1 = single node, 2+ = primary with replicas and automatic failover"
  type        = number
  default     = 1
}

variable "auth_token" {
  type      = string
  sensitive = true
}
