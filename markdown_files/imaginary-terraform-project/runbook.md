# Runbook

## Pre-Apply Checks

Run from the Terraform environment directory, for example `terraform/environments/prod`.

```bash
terraform fmt -check -recursive
terraform init
terraform validate
terraform plan -out=tfplan
```

For OpenTofu:

```bash
tofu fmt -check -recursive
tofu init
tofu validate
tofu plan -out=tfplan
```

## Plan Review Checklist

Before applying, verify the plan does not include unexpected replacement of:

- S3 static bucket
- CloudFront distribution
- Existing EC2 app instances
- Route 53 public records
- TLS certificates

Expected additive resources during ALB migration:

- ALB
- ALB listeners
- ALB listener rules
- Target groups
- Target group attachments
- Security group rules for ALB-to-EC2 traffic

## ALB Health Checks

Validate target health:

```bash
aws elbv2 describe-target-health \
  --target-group-arn "$TARGET_GROUP_ARN"
```

Expected:

- `TargetHealth.State` is `healthy`
- Health check path returns `200` or the configured success code
- Both `app-a` and `app-b` are registered

## Smoke Tests

Use the CloudFront hostname after cutover:

```bash
curl -I https://www.example.test/assets/app.css
curl -I https://www.example.test/api/healthz
curl -I https://www.example.test/
```

Expected:

- Static assets return cacheable responses.
- API health endpoint returns success.
- Root path returns application content.

## Monitoring During Cutover

Watch:

- CloudFront 4xx and 5xx rates
- ALB `HTTPCode_Target_5XX_Count`
- ALB `TargetResponseTime`
- ALB `UnHealthyHostCount`
- EC2 CPU and memory
- Application logs on `app-a` and `app-b`

## Rollback Commands

Rollback should use Terraform to restore the previous CloudFront behavior configuration.

Recommended flow:

```bash
terraform plan -out=rollback.tfplan
terraform apply rollback.tfplan
```

Emergency manual rollback, if approved:

1. Edit CloudFront behavior origin back to Caddy.
2. Record the manual change in the incident notes.
3. Import or reconcile the change back into Terraform immediately after service recovery.

## Evidence to Keep

For each migration attempt, save:

- Terraform or OpenTofu version
- Provider lock file
- Plan file checksum
- Apply logs
- CloudFront distribution config before and after
- ALB target health output
- Monitoring screenshots or metric links
- Incident notes, if rollback occurred

## Final Cleanup Validation

After removing Caddy:

```bash
terraform plan
```

Expected result:

- No references to the Caddy origin remain.
- No security group rules allow public traffic to the old Caddy router.
- CloudFront dynamic behavior points to ALB.
- S3 static behavior is unchanged.
