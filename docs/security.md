# Security

## Controls implemented by this demo
- **No secrets in repo**: `.gitignore` blocks `.env*`, keys, credentials, tfstate, and local-only files.
- **Auditability**: validations produce a deterministic report artifact (not committed) suitable for attaching to PRs.
- **Least privilege (design intent)**:
  - Delivery guardrails separate `plan` from `apply`
  - `apply` requires approval and is restricted to `main`
- **State safety (design intent)**:
  - Remote state + encryption + locking are required in example IaC intent

## Secrets handling
- This repo never prints `$GITHUB_TOKEN`.
- Demo inputs in `examples/` contain **sanitized** values only.
- Output artifacts are written to `artifacts/` (gitignored).

## Recommended extensions in a real org
- Use OIDC-based cloud auth in CI (avoid static keys)
- Add policy-as-code checks (OPA/Sentinel) aligned to your threat model
- Add SAST/secret scanning and IaC security scanning in CI

