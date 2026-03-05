# Runbook: CI/CD Delivery Guardrails (Slow/Flaky Pipelines, Risky Releases)

## Trigger
- Pipeline allows direct apply without approval
- Missing validate/plan/apply separation
- Releases are risky, slow, or frequently rolled back

## Immediate actions (first 15 minutes)
1. Freeze applies to production branches until guardrails are restored.
2. Confirm validate/plan stages are running on every PR.
3. Ensure apply requires explicit approval and is restricted to `main`.

## Diagnosis
- Check that the pipeline has stages: `validate`, `plan`, `apply`.
- Confirm timeouts are set and concurrency is controlled.
- Confirm a plan artifact is produced and reviewed before apply.

## Remediation
- Update pipeline intent (`examples/ci/pipeline.toml`) to restore required gates.
- Add retries/timeouts for flaky steps and reduce blast radius with smaller deploy units.

## Prevention
- Make `portfolio_proof validate` a required status check on PRs.
- Keep “golden pipeline” definitions versioned and reviewed like code.

