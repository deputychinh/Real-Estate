# The whole environment (plan §15). envs/staging and envs/prod only pass different variables.

locals {
  name          = "${var.project}-${var.environment}"
  origin_domain = "origin.${var.domain}"
  ssm_path      = "/${var.project}/${var.environment}/deploy"
  site_url      = "https://${var.domain}"
}

# ── Generated secrets (stored in Secrets Manager; the state bucket is encrypted and private) ──

resource "random_password" "db" {
  length  = 32
  special = false
}

resource "random_password" "redis" {
  length  = 48
  special = false
}

resource "random_password" "jwt" {
  length  = 64
  special = false
}

resource "random_password" "origin_verify" {
  length  = 40
  special = false
}

# ── Network, registry, data ──

module "network" {
  source     = "../modules/network"
  name       = local.name
  cidr       = var.vpc_cidr
  azs        = var.azs
  nat_per_az = var.sizing.nat_per_az
}

module "security_groups" {
  source = "../modules/security-groups"
  name   = local.name
  vpc_id = module.network.vpc_id
}

module "ecr" {
  source       = "../modules/ecr"
  project      = local.name
  force_delete = !var.sizing.deletion_protection
}

module "rds" {
  source              = "../modules/rds"
  name                = local.name
  subnet_ids          = module.network.data_subnet_ids
  security_group_id   = module.security_groups.rds_sg_id
  instance_class      = var.sizing.db_instance_class
  multi_az            = var.sizing.db_multi_az
  backup_days         = var.sizing.db_backup_days
  deletion_protection = var.sizing.deletion_protection
  password            = random_password.db.result
}

module "redis" {
  source            = "../modules/elasticache"
  name              = local.name
  subnet_ids        = module.network.data_subnet_ids
  security_group_id = module.security_groups.redis_sg_id
  node_type         = var.sizing.redis_node_type
  nodes             = var.sizing.redis_nodes
  auth_token        = random_password.redis.result
}

resource "aws_secretsmanager_secret" "app" {
  name                    = "${local.name}/app"
  recovery_window_in_days = var.sizing.deletion_protection ? 30 : 0
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    DATABASE_URL = "mysql+aiomysql://${module.rds.username}:${random_password.db.result}@${module.rds.endpoint}/${module.rds.database}"
    REDIS_URL    = "rediss://:${random_password.redis.result}@${module.redis.primary_endpoint}:6379/0"
    JWT_SECRET   = random_password.jwt.result
  })
}

# ── Certificates, load balancer, CDN ──

module "dns_cert" {
  source        = "../modules/dns-cert"
  zone_name     = var.zone_name
  domain        = var.domain
  origin_domain = local.origin_domain
  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }
}

module "alb" {
  source               = "../modules/alb"
  name                 = local.name
  vpc_id               = module.network.vpc_id
  subnet_ids           = module.network.public_subnet_ids
  security_group_id    = module.security_groups.alb_sg_id
  certificate_arn      = module.dns_cert.origin_certificate_arn
  origin_verify_secret = random_password.origin_verify.result
  deletion_protection  = var.sizing.deletion_protection
}

module "assets" {
  source        = "../modules/s3-assets"
  bucket_name   = "${local.name}-assets-${data.aws_caller_identity.current.account_id}"
  force_destroy = !var.sizing.deletion_protection
}

module "edge" {
  source                    = "../modules/edge"
  name                      = local.name
  domain                    = var.domain
  origin_domain             = local.origin_domain
  certificate_arn           = module.dns_cert.cloudfront_certificate_arn
  assets_bucket_domain_name = module.assets.bucket_regional_domain_name
  origin_verify_secret      = random_password.origin_verify.result
  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "assets" {
  statement {
    sid       = "CloudFrontRead"
    actions   = ["s3:GetObject"]
    resources = ["${module.assets.bucket_arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [module.edge.distribution_arn]
    }
  }
}

resource "aws_s3_bucket_policy" "assets" {
  bucket = module.assets.bucket_name
  policy = data.aws_iam_policy_document.assets.json
}

resource "aws_route53_record" "site" {
  for_each = toset(["A", "AAAA"])
  zone_id  = module.dns_cert.zone_id
  name     = var.domain
  type     = each.key
  alias {
    name                   = module.edge.domain_name
    zone_id                = module.edge.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "origin" {
  zone_id = module.dns_cert.zone_id
  name    = local.origin_domain
  type    = "A"
  alias {
    name                   = module.alb.dns_name
    zone_id                = module.alb.zone_id
    evaluate_target_health = true
  }
}

# ── Compute ──

module "cluster" {
  source = "../modules/ecs-cluster"
  name   = local.name
}

locals {
  app_secret = aws_secretsmanager_secret.app.arn
}

module "backend" {
  source                = "../modules/ecs-service"
  name                  = "${local.name}-backend"
  container_name        = "backend"
  image                 = "${module.ecr.repository_urls["backend"]}:${var.initial_image_tag}"
  port                  = 8000
  cpu                   = var.sizing.api.cpu
  memory                = var.sizing.api.memory
  min_count             = var.sizing.api.min
  max_count             = var.sizing.api.max
  cluster_arn           = module.cluster.cluster_arn
  cluster_name          = module.cluster.cluster_name
  namespace_arn         = module.cluster.namespace_arn
  service_connect_alias = "backend"
  subnet_ids            = module.network.app_subnet_ids
  security_group_id     = module.security_groups.api_sg_id
  target_group_arn      = module.alb.api_target_group_arn
  environment = {
    ENVIRONMENT           = var.environment == "prod" ? "production" : "staging"
    CORS_ORIGINS          = jsonencode([local.site_url])
    REFRESH_COOKIE_SECURE = "true"
    DATABASE_SSL_CA       = "/etc/ssl/rds-global-bundle.pem"
    LOG_LEVEL             = "INFO"
  }
  secrets = {
    DATABASE_URL = "${local.app_secret}:DATABASE_URL::"
    REDIS_URL    = "${local.app_secret}:REDIS_URL::"
    JWT_SECRET   = "${local.app_secret}:JWT_SECRET::"
  }
  secret_arns = [local.app_secret]
}

module "frontend" {
  source            = "../modules/ecs-service"
  name              = "${local.name}-frontend"
  container_name    = "frontend"
  image             = "${module.ecr.repository_urls["frontend"]}:${var.initial_image_tag}"
  port              = 3000
  cpu               = var.sizing.web.cpu
  memory            = var.sizing.web.memory
  min_count         = var.sizing.web.min
  max_count         = var.sizing.web.max
  cluster_arn       = module.cluster.cluster_arn
  cluster_name      = module.cluster.cluster_name
  namespace_arn     = module.cluster.namespace_arn
  subnet_ids        = module.network.app_subnet_ids
  security_group_id = module.security_groups.web_sg_id
  target_group_arn  = module.alb.web_target_group_arn
  environment = {
    NUXT_API_BASE_SERVER = "http://backend:8000/api/v1" # Service Connect, inside the VPC
    NUXT_PUBLIC_SITE_URL = local.site_url
  }
}

# ── Operations ──

module "monitoring" {
  source         = "../modules/monitoring"
  name           = local.name
  environment    = var.environment
  alert_email    = var.alert_email
  alb_arn_suffix = module.alb.arn_suffix
  target_group_arn_suffixes = {
    web = module.alb.web_target_group_arn_suffix
    api = module.alb.api_target_group_arn_suffix
  }
  rds_identifier             = module.rds.identifier
  redis_replication_group_id = module.redis.replication_group_id
  monthly_budget_usd         = var.monthly_budget_usd
}

module "github_oidc" {
  source              = "../modules/github-oidc"
  name                = local.name
  repository          = var.github_repository
  create_provider     = var.create_github_oidc_provider
  allowed_refs        = var.environment == "prod" ? ["refs/tags/v*"] : ["refs/heads/master"]
  ecr_repository_arns = module.ecr.repository_arns
  ssm_path            = "${local.ssm_path}/*"
  assets_bucket_arn   = module.assets.bucket_arn
  task_role_arns = [
    module.backend.execution_role_arn,
    module.backend.task_role_arn,
    module.frontend.execution_role_arn,
    module.frontend.task_role_arn,
  ]
}

module "deploy_params" {
  source = "../modules/deploy-params"
  path   = local.ssm_path
  parameters = {
    CLUSTER         = module.cluster.cluster_name
    ECR_REGISTRY    = module.ecr.registry
    ASSETS_BUCKET   = module.assets.bucket_name
    PRIVATE_SUBNETS = join(",", module.network.app_subnet_ids)
    API_SG          = module.security_groups.api_sg_id
    DOMAIN          = var.domain
    DISTRIBUTION_ID = module.edge.distribution_id
  }
}
