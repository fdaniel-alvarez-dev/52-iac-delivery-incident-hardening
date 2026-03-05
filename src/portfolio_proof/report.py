from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .model import CheckResults


def _pain_point_title(pain_point: str) -> str:
    return {
        "iac_drift": "Infrastructure drift & fragile IaC automation",
        "cicd_delivery": "Delivery friction (CI/CD) & risky releases",
        "reliability_incidents": "Reliability under on-call pressure (observability + MTTR)",
        "traceability": "Traceability & input completeness",
    }.get(pain_point, pain_point)


def write_report(out_path: Path, examples_dir: Path, results: CheckResults) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines: list[str] = []

    lines.append("# IaC / Delivery / Incident Hardening Report")
    lines.append("")
    lines.append(f"- Generated (UTC): `{now}`")
    lines.append(f"- Examples dir: `{examples_dir}`")
    lines.append(f"- Result: **{'PASS' if results.ok else 'FAIL'}**")
    lines.append("")

    lines.append("## What this demonstrates")
    lines.append("")
    lines.append("- IaC drift prevention via pinned versions, safe remote state, and explicit dev/prod parity rules.")
    lines.append("- CI/CD guardrails via validate/plan/apply gates, plan artifacts, approvals, and concurrency control.")
    lines.append("- Incident readiness via SLOs, alert coverage, observability signal checks, and runbook linkage.")
    lines.append("")

    lines.append("## Validation results")
    lines.append("")
    if results.ok:
        lines.append("- ✅ All controls satisfied for the provided examples.")
    else:
        lines.append(f"- ❌ {len(results.failures)} control(s) violated.")
        lines.append("")
        grouped: dict[str, list] = {}
        for f in results.failures:
            grouped.setdefault(f.pain_point, []).append(f)
        for pain_point, failures in grouped.items():
            lines.append(f"### {_pain_point_title(pain_point)}")
            lines.append("")
            for f in failures:
                lines.append(f"- **{f.code}**: {f.message} (`{f.path}`)")
            lines.append("")

    lines.append("## Runbooks")
    lines.append("")
    lines.append("- `docs/runbooks/01-iac-drift.md`")
    lines.append("- `docs/runbooks/02-ci-cd-guardrails.md`")
    lines.append("- `docs/runbooks/03-incident-mttr.md`")
    lines.append("")

    lines.append("## Next steps (how you’d use this in a real org)")
    lines.append("")
    lines.append("- Run `portfolio_proof validate` in CI on every PR, blocking merges on violations.")
    lines.append("- Treat parity rules as a contract: dev/prod divergence must be explicit and reviewed.")
    lines.append("- Extend checks to match your cloud baseline (OIDC auth, policy-as-code, scanning).")
    lines.append("")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

