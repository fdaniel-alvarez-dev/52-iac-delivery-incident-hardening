# 52-iac-delivery-incident-hardening

Portfolio-grade, deterministic demo that hardens three real platform pain points:

1. **Infrastructure drift & fragile automation** (IaC that diverges across environments and breaks easily)
2. **Delivery friction** (slow/flaky CI/CD and risky releases)
3. **Reliability under on-call pressure** (reduce incident frequency and MTTR; make failures boring)

## Architecture (inputs → checks → outputs → runbooks)
- **Inputs**: sanitized, realistic TOML under `examples/`
- **Checks**: `python -m portfolio_proof validate` enforces guardrails
- **Outputs**: `python -m portfolio_proof report` writes `artifacts/report.md` (gitignored)
- **Runbooks**: operational playbooks in `docs/runbooks/`

## Quick start
```bash
make setup
make demo
```

Then open `artifacts/report.md`.

## Demo (what to look for)
The generated report maps directly to the pain points:
- IaC drift prevention: pinned versions, remote state encryption/locking, explicit dev/prod parity rules
- Delivery guardrails: validate/plan/apply separation, plan artifacts, approvals, concurrency control
- Incident readiness: SLO + alerts + signals (logs/metrics/traces) + runbook linkage

Try failing it on purpose:
```bash
PYTHONPATH=src .venv/bin/python -m portfolio_proof validate --examples examples/invalid
```

## Security
- No secrets are committed; `.gitignore` blocks `.env*`, keys, credentials, tfstate, local-only notes.
- The demo never prints `$GITHUB_TOKEN`.
- Artifacts are written to `artifacts/` (gitignored).

## Out of scope (intentional)
- Provisioning real cloud resources (this repo validates intent/guardrails deterministically)
- Vendor-specific policy engines (OPA/Sentinel); this repo demonstrates the approach in stdlib-only Python

