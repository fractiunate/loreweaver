# Architecture

## Current State

```text
Users
  |
  v
CloudFront CDN
  |-----------------------------> S3 static website bucket
  |
  v
EC2 instance: caddy-router
  |-----------------------------> EC2 instance: app-a
  |-----------------------------> EC2 instance: app-b
```

### Components

- **CloudFront CDN** terminates public HTTP(S) at the edge.
- **S3 static bucket** hosts static assets such as HTML, CSS, JavaScript, and images.
- **Caddy router EC2 instance** routes dynamic paths to backend instances.
- **EC2 app instances** run application services.

### Current Routing Example

| Path | Current Destination |
| --- | --- |
| `/assets/*` | S3 via CloudFront origin |
| `/static/*` | S3 via CloudFront origin |
| `/api/*` | CloudFront -> Caddy EC2 -> app EC2 instances |
| `/*` | CloudFront -> Caddy EC2 -> app EC2 instances |

### Current Risks

- Caddy router is a single point of failure.
- Manual Caddy config changes can drift from Terraform state.
- TLS, health checks, routing, and instance registration are split across custom config and AWS resources.
- Scaling app instances requires Caddy config coordination.

## Target State

```text
Users
  |
  v
CloudFront CDN
  |-----------------------------> S3 static bucket
  |
  v
Application Load Balancer
  |-----------------------------> Target group: app-a
  |-----------------------------> Target group: app-b
```

### Target Components

- **CloudFront** remains the public edge and caching layer.
- **S3** remains the static origin.
- **ALB** becomes the managed dynamic origin and request router.
- **EC2 instances** are registered into one or more target groups.

### Target Routing Example

| Path | Target Destination |
| --- | --- |
| `/assets/*` | CloudFront -> S3 origin |
| `/static/*` | CloudFront -> S3 origin |
| `/api/*` | CloudFront -> ALB -> API target group |
| `/*` | CloudFront -> ALB -> web target group |

## Security Groups

| Resource | Ingress | Egress |
| --- | --- | --- |
| CloudFront | Public viewer traffic | ALB/S3 origins |
| ALB | HTTPS from CloudFront-managed prefix list or allowed CIDRs | EC2 app ports |
| EC2 apps | App port from ALB security group only | Required outbound dependencies |
| S3 bucket | CloudFront Origin Access Control only | N/A |

## Terraform Refactor Intent

The Terraform refactor should separate concerns:

- `modules/networking` for VPC, subnets, route tables, and security groups
- `modules/compute` for EC2 instances and instance profiles
- `modules/static-site` for S3 bucket, policies, and website assets metadata
- `modules/cdn` for CloudFront distributions, origins, cache behaviors, and certificates
- `modules/alb-routing` for ALB, listeners, listener rules, target groups, and attachments
