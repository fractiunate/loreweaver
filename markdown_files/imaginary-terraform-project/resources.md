# Resource Inventory

## Compute

| Name | Type | Purpose | Notes |
| --- | --- | --- | --- |
| `app-a` | EC2 | Primary app node | Registered with ALB target group |
| `app-b` | EC2 | Secondary app node | Registered with ALB target group |
| `caddy-router` | EC2 | Legacy dynamic traffic router | Retired after migration |

## Storage

| Name | Type | Purpose | Notes |
| --- | --- | --- | --- |
| `static-site-bucket` | S3 | Static web assets | Private bucket; CloudFront-only access |

## Edge and Routing

| Name | Type | Purpose | Notes |
| --- | --- | --- | --- |
| `site-cdn` | CloudFront | Public CDN and TLS edge | Multiple origins: S3 and ALB |
| `app-alb` | ALB | Managed dynamic traffic router | Replaces Caddy router |
| `web-targets` | Target group | Default web traffic | Contains app EC2 instances |
| `api-targets` | Target group | API traffic | May point to same instances initially |

## DNS

| Record | Target | Purpose |
| --- | --- | --- |
| `www.example.test` | CloudFront alias | Public site entrypoint |
| `origin-app.example.test` | ALB DNS name or internal alias | Optional origin-only reference |

## Example Listener Rules

| Priority | Condition | Action |
| --- | --- | --- |
| 10 | Path `/api/*` | Forward to `api-targets` |
| 20 | Path `/healthz` | Forward to `web-targets` |
| 100 | Default | Forward to `web-targets` |

## Example CloudFront Behaviors

| Behavior | Origin | Cache Policy |
| --- | --- | --- |
| `/assets/*` | S3 | Long TTL immutable assets |
| `/static/*` | S3 | Long TTL static content |
| `/api/*` | ALB | Caching disabled |
| `Default (*)` | ALB | Short TTL or caching disabled |

## Ownership Boundaries

- Terraform owns AWS resources, security groups, listener rules, and target attachments.
- Application deployment owns app binaries and service lifecycle on EC2.
- CI/CD owns static asset upload to S3.
- Caddy config becomes temporary legacy state during migration and is deleted after cutover.
