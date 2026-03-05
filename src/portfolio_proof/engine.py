from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .checks.cicd import check_cicd_guardrails
from .checks.iac import check_iac_controls
from .checks.reliability import check_reliability_readiness
from .model import CheckFailure, CheckResults


@dataclass(frozen=True)
class Inputs:
    iac_dev: Path
    iac_prod: Path
    iac_parity: Path
    cicd_pipeline: Path
    reliability_service_catalog: Path
    reliability_observability: Path
    reliability_oncall: Path


def _resolve_inputs(examples_dir: Path) -> Inputs:
    base = examples_dir
    return Inputs(
        iac_dev=base / "iac/env_dev.toml",
        iac_prod=base / "iac/env_prod.toml",
        iac_parity=base / "iac/parity_rules.toml",
        cicd_pipeline=base / "ci/pipeline.toml",
        reliability_service_catalog=base / "reliability/service_catalog.toml",
        reliability_observability=base / "reliability/observability.toml",
        reliability_oncall=base / "reliability/oncall.toml",
    )


def _missing_inputs(inputs: Inputs) -> list[CheckFailure]:
    missing: list[CheckFailure] = []
    for path in inputs.__dict__.values():
        if not Path(path).exists():
            missing.append(
                CheckFailure(
                    code="INPUT_MISSING",
                    message="Required example input is missing",
                    path=str(path),
                    pain_point="traceability",
                )
            )
    return missing


def run_checks(examples_dir: Path) -> CheckResults:
    inputs = _resolve_inputs(examples_dir)
    failures = _missing_inputs(inputs)
    if failures:
        return CheckResults(failures=failures)

    failures.extend(check_iac_controls(inputs.iac_dev, inputs.iac_prod, inputs.iac_parity))
    failures.extend(check_cicd_guardrails(inputs.cicd_pipeline))
    failures.extend(
        check_reliability_readiness(
            inputs.reliability_service_catalog,
            inputs.reliability_observability,
            inputs.reliability_oncall,
        )
    )
    return CheckResults(failures=failures)

