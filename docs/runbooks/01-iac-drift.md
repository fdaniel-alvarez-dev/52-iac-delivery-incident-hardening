# Runbook: IaC Drift & Automation Hardening

## Trigger
- `portfolio_proof validate` fails for IaC controls
- Unexpected differences between `dev` and `prod` intent
- Plan output shows changes that were not reviewed

## Immediate actions (first 15 minutes)
1. Stop automated applies; require manual approval on the next `apply`.
2. Generate a fresh report: `make demo` and review `artifacts/report.md`.
3. Compare environment intent (dev vs prod) and confirm allowed differences only.

## Diagnosis
- Verify Terraform and provider versions are pinned.
- Verify remote state is configured with encryption and locking.
- Confirm module versions are pinned (no floating branches/tags).

## Remediation
- Update versions in `examples/iac/env_*.toml` (or your org’s equivalents).
- Narrow allowed drift rules; treat any new drift as a review item.
- Enforce the validate/plan/apply workflow in CI/CD (see Runbook 02).

## Prevention
- Gate merges on `portfolio_proof validate` (or equivalent policy checks).
- Require approvals for `apply`.
- Keep environment parity rules explicit and version-controlled.

