from __future__ import annotations

from pathlib import Path

from ..model import CheckFailure
from ..tomlutil import load_toml


def check_reliability_readiness(
    service_catalog_path: Path,
    observability_path: Path,
    oncall_path: Path,
) -> list[CheckFailure]:
    catalog = load_toml(service_catalog_path)
    observability = load_toml(observability_path)
    oncall = load_toml(oncall_path)

    failures: list[CheckFailure] = []

    services = catalog.get("services")
    if not isinstance(services, list) or not services:
        failures.append(
            CheckFailure(
                code="REL_SERVICE_CATALOG_EMPTY",
                message="service_catalog.toml must define at least one [[services]] entry",
                path=str(service_catalog_path),
                pain_point="reliability_incidents",
            )
        )
        return failures

    signals = observability.get("signals", {})
    for sig in ("logs", "metrics", "traces"):
        if not isinstance(signals, dict) or signals.get(sig) is not True:
            failures.append(
                CheckFailure(
                    code="REL_SIGNAL_MISSING",
                    message=f"Observability must include {sig}=true",
                    path=str(observability_path),
                    pain_point="reliability_incidents",
                )
            )

    routing = observability.get("alert_routing", {})
    escalation = routing.get("escalation_minutes") if isinstance(routing, dict) else None
    if not isinstance(escalation, int) or not (1 <= escalation <= 15):
        failures.append(
            CheckFailure(
                code="REL_ESCALATION_INVALID",
                message="alert_routing.escalation_minutes must be an int between 1 and 15",
                path=str(observability_path),
                pain_point="reliability_incidents",
            )
        )

    for svc in services:
        if not isinstance(svc, dict):
            continue
        name = svc.get("name")
        runbook = svc.get("runbook")
        slo = svc.get("slo_availability")
        alerts = svc.get("alerts")

        if not isinstance(name, str) or not name.strip():
            failures.append(
                CheckFailure(
                    code="REL_SERVICE_NAME_REQUIRED",
                    message="Each service must define a name",
                    path=str(service_catalog_path),
                    pain_point="reliability_incidents",
                )
            )
            continue

        if not isinstance(runbook, str) or not Path(runbook).exists():
            failures.append(
                CheckFailure(
                    code="REL_RUNBOOK_REQUIRED",
                    message=f"Service {name} must reference an existing runbook path",
                    path=str(service_catalog_path),
                    pain_point="reliability_incidents",
                )
            )

        if not isinstance(slo, (int, float)) or not (90 <= float(slo) < 100):
            failures.append(
                CheckFailure(
                    code="REL_SLO_INVALID",
                    message=f"Service {name} must define a realistic availability SLO (90-99.999)",
                    path=str(service_catalog_path),
                    pain_point="reliability_incidents",
                )
            )

        if not isinstance(alerts, list) or not alerts:
            failures.append(
                CheckFailure(
                    code="REL_ALERTS_REQUIRED",
                    message=f"Service {name} must define at least one alert",
                    path=str(service_catalog_path),
                    pain_point="reliability_incidents",
                )
            )

    policy = oncall.get("policy", {})
    for key in ("primary_timeout_minutes", "secondary_timeout_minutes"):
        val = policy.get(key) if isinstance(policy, dict) else None
        if not isinstance(val, int) or not (5 <= val <= 15):
            failures.append(
                CheckFailure(
                    code="REL_ONCALL_TIMEOUT_INVALID",
                    message=f"On-call {key} must be 5-15 minutes",
                    path=str(oncall_path),
                    pain_point="reliability_incidents",
                )
            )

    return failures

