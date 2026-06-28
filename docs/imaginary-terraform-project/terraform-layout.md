# Terraform Layout

## Proposed Repository Structure

```text
terraform/
  environments/
    prod/
      main.tf
      variables.tf
      outputs.tf
      versions.tf
      backend.tf
      terraform.tfvars
  modules/
    networking/
      main.tf
      variables.tf
      outputs.tf
    compute/
      main.tf
      variables.tf
      outputs.tf
    static-site/
      main.tf
      variables.tf
      outputs.tf
    cdn/
      main.tf
      variables.tf
      outputs.tf
    alb-routing/
      main.tf
      variables.tf
      outputs.tf
```

## Environment Composition

The `prod` environment wires modules together:

```text
networking -> compute
networking -> alb-routing
compute -> alb-routing target attachments
static-site -> cdn static origin
alb-routing -> cdn dynamic origin
cdn -> public DNS record
```

## Module Responsibilities

### `networking`

Owns:

- VPC
- Public and private subnets
- Internet gateway and NAT, if required
- Route tables
- Security groups shared by ALB and EC2 instances

### `compute`

Owns:

- 2 EC2 instances
- IAM instance profiles
- User data/bootstrap references
- App instance tags
- Optional Elastic IPs only if explicitly required

Recommended instance names:

- `app-a`
- `app-b`

### `static-site`

Owns:

- S3 bucket
- Bucket versioning
- Server-side encryption
- Public access block
- Bucket policy for CloudFront Origin Access Control

The bucket should not be public.

### `cdn`

Owns:

- CloudFront distribution
- S3 origin
- ALB origin
- Cache behaviors by path
- TLS certificate association
- Optional Route 53 alias record

### `alb-routing`

Owns:

- Application Load Balancer
- HTTPS listener
- HTTP-to-HTTPS redirect listener, if needed
- Target groups
- Listener rules
- Health checks
- Target attachments for the two EC2 instances

## Resource Address Stability

Prefer `for_each` keyed by stable names over `count` indexes:

```hcl
locals {
  app_instances = {
    app-a = { role = "web" }
    app-b = { role = "api" }
  }
}
```

This avoids identity churn if a third instance is added later.

## Suggested Refactor Sequence

1. Introduce modules without changing resource behavior.
2. Add `moved` blocks for any renamed resources.
3. Add ALB resources behind CloudFront but do not route production traffic yet.
4. Attach EC2 instances to ALB target groups.
5. Shift CloudFront dynamic origin from Caddy EC2 to ALB.
6. Remove Caddy routing only after rollback window expires.
