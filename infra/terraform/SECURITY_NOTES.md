# Checkov findings: accepted for this assignment

`checkov -d . --framework terraform` reports ~50 findings. Fixed vs. accepted, and why:

## Fixed
- Security group / rule descriptions (readability).
- S3 lifecycle: abort incomplete multipart uploads after 7 days.
- SNS topic encrypted with the AWS-managed key (`alias/aws/sns`), no extra cost.
- WAF: added the Linux and anonymous-IP managed rule sets.
- GitHub OIDC deploy policy: `ecs:RunTask`/`UpdateService`/`Describe*` scoped to this cluster's
  ARNs. `RegisterTaskDefinition`/`DescribeTaskDefinition` stay `"*"` — the ECS API does not support
  a resource ARN for them (documented AWS limitation, not an oversight).

## Accepted (cost or scope trade-off, not a mistake)
- **Customer-managed KMS keys** for ECR, CloudWatch Logs, ElastiCache, RDS Performance Insights,
  Secrets Manager, S3: using AWS-managed keys (default) avoids per-key monthly cost and rotation
  ops for a project this size. Revisit if compliance requires customer-managed keys.
- **Access logging** for the ALB and CloudFront: needs an extra S3 bucket and lifecycle policy;
  skipped for this assignment. CloudWatch Container Insights and the app's own JSON request logs
  (plan §6, `RequestContextMiddleware`) already give per-request visibility.
- **RDS Multi-AZ, deletion protection, enhanced monitoring, exported logs**: gated by
  `var.sizing` per environment (plan §15.5) — off in staging to keep it near USD 150/month, on in
  production (`envs/prod/terraform.tfvars`).
- **CloudFront default root object / origin failover / geo restriction**: not applicable — this is
  an SSR app and an API behind CloudFront, not a static site, and geo restriction isn't a stated
  requirement.
- **WAF logging configuration**: needs a Kinesis Data Firehose or CloudWatch Logs destination;
  left for a follow-up ticket, since the managed rule metrics already go to CloudWatch.

Full list: `checkov -d infra/terraform --framework terraform`.
