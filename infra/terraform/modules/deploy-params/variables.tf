variable "path" {
  description = "e.g. /re-portal/staging/deploy"
  type        = string
}

variable "parameters" {
  type = map(string)
}
