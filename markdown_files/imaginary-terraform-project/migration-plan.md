# Migration Plan: Caddy Router to ALB

## Objective

Move dynamic traffic routing from a Caddy process running on one EC2 instance to an AWS Application Load Balancer, while keeping CloudFront as the public entrypoint.

## Migration Principles

- Keep rollback simple until the new path is stable.
- Avoid destructive Terraform changes during routing cutover.
- Use reviewed plan artifacts before apply.
- Keep old Caddy router available until validation passes.
- Prefer additive changes first, cleanup later.

## Phase 0: Discovery

Capture the current Caddy behavior before changing infrastructure.

Checklist:

- Export Caddy route config.
- List all hostnames and path matchers.
- Identify upstream app ports.
- Record current health check endpoints.
- Record CloudFront origin and cache behavior settings.
- Confirm EC2 instances can receive traffic directly from an ALB security group.

Deliverables:

- Route mapping table
- Health check table
- Rollback DNS/origin values

## Phase 1: Terraform Refactor Without Traffic Change

Create or reorganize modules while preserving behavior.

Tasks:

1. Split existing resources into modules.
2. Add `moved` blocks for any resource address changes.
3. Keep CloudFront dynamic origin pointing at `caddy-router`.
4. Run `terraform plan` and verify no replacement of existing critical resources.

Acceptance criteria:

- No EC2 replacement.
- No S3 bucket replacement.
- No CloudFront distribution replacement.
- State addresses are stable after refactor.

## Phase 2: Add ALB in Parallel

Provision ALB resources without serving production traffic.

Tasks:

1. Create ALB in public subnets.
2. Create target groups for web and API traffic.
3. Attach `app-a` and `app-b` to target groups.
4. Add ALB security group allowing CloudFront-origin traffic or controlled test CIDRs.
5. Configure listener rules equivalent to Caddy routes.
6. Validate target health.

Acceptance criteria:

- ALB target groups report healthy targets.
- Direct test requests to ALB return expected responses.
- Caddy production route remains unchanged.

## Phase 3: CloudFront Origin Cutover

Change the CloudFront dynamic origin from Caddy EC2 to ALB.

Tasks:

1. Add ALB as a CloudFront origin.
2. Update `/api/*` and default behavior to use ALB origin.
3. Keep S3 behaviors unchanged.
4. Apply during a low-traffic window.
5. Monitor CloudFront 4xx/5xx, ALB target response time, and app logs.

Acceptance criteria:

- Static content still resolves from S3.
- Dynamic requests are served through ALB.
- Error rates stay within normal range.
- No unexpected cache behavior changes.

## Phase 4: Stabilization

Keep Caddy available as a rollback path for a defined window, for example 24-72 hours.

Tasks:

- Compare ALB logs against previous Caddy access patterns.
- Confirm app instances receive balanced traffic.
- Confirm health checks are stable.
- Confirm deploy workflow does not depend on Caddy reloads.

## Phase 5: Cleanup

After the rollback window expires:

1. Remove CloudFront origin references to Caddy.
2. Remove Caddy security group ingress.
3. Stop Caddy process.
4. Remove Caddy package/config from instance bootstrap.
5. Retire the `caddy-router` EC2 instance if it has no remaining purpose.
6. Remove obsolete Terraform variables and outputs.

## Rollback Plan

If errors spike after cutover:

1. Revert CloudFront dynamic behaviors to the Caddy origin.
2. Invalidate affected paths only if cache behavior caused stale errors.
3. Keep ALB resources in place for diagnosis.
4. Review ALB target health, listener rules, security groups, and app logs.
5. Reattempt cutover after fixing the root cause.

Do not destroy ALB resources as the first rollback action; routing rollback is faster and safer.
