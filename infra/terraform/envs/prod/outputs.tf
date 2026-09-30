output "site_url" {
  value = module.stack.site_url
}

output "cloudfront_domain" {
  value = module.stack.cloudfront_domain
}

output "ecr_repositories" {
  value = module.stack.ecr_repositories
}

output "github_deploy_role_arn" {
  value = module.stack.github_deploy_role_arn
}
