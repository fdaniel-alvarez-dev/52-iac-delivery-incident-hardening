# Architecture

## What this repo demonstrates
This repository is a **portfolio-grade, deterministic demo** for three common platform pain points:

1. **Infrastructure drift & fragile IaC automation**
2. **Delivery friction in CI/CD**
3. **Reliability under real on-call pressure**

It does **not** provision cloud resources. It validates *intent* and *guardrails* using realistic, sanitized configuration inputs.

## Data flow
Inputs → checks → artifacts → runbooks

- **Inputs**: TOML configurations under `examples/`
  - IaC intent: environments + parity rules
  - Delivery intent: pipeline definition (validate/plan/apply)
  - Reliability intent: service catalog + observability + on-call policy
- **Checks**: `python -m portfolio_proof validate`
  - Fast, deterministic, and PR-friendly
- **Artifacts**: `python -m portfolio_proof report`
  - Human-readable report saved to `artifacts/report.md`
- **Runbooks**: `docs/runbooks/`
  - Concrete steps for drift, pipeline failures, and incident response

## Threat model notes (lightweight)
Primary threats this approach reduces:
- **Misconfiguration drift**: dev/prod divergence, unpinned versions, missing state locking.
- **Unsafe releases**: direct apply without approvals, missing validate/plan gates, uncontrolled concurrency.
- **Slow/chaotic incident response**: missing runbooks, weak signals, unclear escalation, missing SLOs.

What this repo intentionally does not cover:
- Vendor-specific signing/auth (AWS/GCP/Azure APIs) in stdlib-only mode
- Full policy-as-code engines (OPA/Conftest/Sentinel) — patterns are represented via deterministic checks

