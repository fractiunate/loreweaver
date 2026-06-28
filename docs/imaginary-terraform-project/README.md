# Imaginary Terraform Project: Edge Web Platform

This sample documentation describes a Terraform-managed AWS platform with:

- 2 EC2 instances for application services
- 1 S3 static website bucket
- 1 CDN in front of static and dynamic origins
- A legacy Caddy router on EC2
- A target refactor to an Application Load Balancer (ALB) for load balancing and traffic routing

## Documents

| File | Purpose |
| --- | --- |
| [architecture.md](architecture.md) | Current and target architecture overview |
| [terraform-layout.md](terraform-layout.md) | Suggested Terraform module and environment layout |
| [resources.md](resources.md) | Resource inventory and ownership notes |
| [migration-plan.md](migration-plan.md) | Step-by-step Caddy-to-ALB migration plan |
| [runbook.md](runbook.md) | Operational checks, rollback, and validation commands |

## Assumptions

- Runtime: Terraform >= 1.6 or OpenTofu >= 1.6
- AWS provider: `hashicorp/aws` >= 5.x
- Environment: imaginary `prod` account in one AWS region
- CDN: CloudFront
- Static hosting: private S3 bucket accessed through CloudFront Origin Access Control
- Dynamic routing target: ALB forwarding to EC2 target groups

## High-Level Goal

Replace the single EC2-hosted Caddy router with AWS-managed ALB routing while keeping CloudFront as the public edge entrypoint. The migration should avoid resource identity churn, reduce single-instance routing risk, and keep rollback simple until traffic proves stable.
