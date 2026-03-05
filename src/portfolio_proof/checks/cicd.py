from __future__ import annotations

from pathlib import Path

from ..model import CheckFailure
from ..tomlutil import load_toml


def check_cicd_guardrails(pipeline_path: Path) -> list[CheckFailure]:
    pipeline = load_toml(pipeline_path)
    failures: list[CheckFailure] = []

    stages = pipeline.get("stages", {})
    if not isinstance(stages, dict):
        return [
            CheckFailure(
                code="CICD_PIPELINE_INVALID",
                message="pipeline.toml must define [stages.*] tables",
                path=str(pipeline_path),
                pain_point="cicd_delivery",
            )
        ]

    for required in ("validate", "plan", "apply"):
        if required not in stages:
            failures.append(
                CheckFailure(
                    code="CICD_STAGE_MISSING",
                    message=f"Missing required stage: {required}",
                    path=str(pipeline_path),
                    pain_point="cicd_delivery",
                )
            )

    validate = stages.get("validate", {})
    plan = stages.get("plan", {})
    apply = stages.get("apply", {})

    validate_steps = set(validate.get("steps", []) if isinstance(validate, dict) else [])
    for step in ("format", "lint", "unit_tests", "terraform_validate"):
        if step not in validate_steps:
            failures.append(
                CheckFailure(
                    code="CICD_VALIDATE_GATES_MISSING",
                    message=f"Validate stage must include step: {step}",
                    path=str(pipeline_path),
                    pain_point="cicd_delivery",
                )
            )

    plan_steps = set(plan.get("steps", []) if isinstance(plan, dict) else [])
    if "terraform_plan" not in plan_steps:
        failures.append(
            CheckFailure(
                code="CICD_PLAN_MISSING",
                message="Plan stage must run terraform_plan",
                path=str(pipeline_path),
                pain_point="cicd_delivery",
            )
        )

    artifacts = set(plan.get("produces_artifacts", []) if isinstance(plan, dict) else [])
    if "planfile" not in artifacts:
        failures.append(
            CheckFailure(
                code="CICD_PLAN_ARTIFACT_MISSING",
                message="Plan stage must produce a plan artifact for review",
                path=str(pipeline_path),
                pain_point="cicd_delivery",
            )
        )

    if not isinstance(apply, dict) or apply.get("requires_approval") is not True:
        failures.append(
            CheckFailure(
                code="CICD_APPLY_APPROVAL_REQUIRED",
                message="Apply stage must require explicit approval",
                path=str(pipeline_path),
                pain_point="cicd_delivery",
            )
        )

    allowed_branches = apply.get("allowed_branches", []) if isinstance(apply, dict) else []
    if "main" not in allowed_branches:
        failures.append(
            CheckFailure(
                code="CICD_APPLY_BRANCH_RESTRICTION",
                message="Apply stage must be restricted to main",
                path=str(pipeline_path),
                pain_point="cicd_delivery",
            )
        )

    metadata = pipeline.get("metadata", {})
    max_parallel = metadata.get("max_parallel") if isinstance(metadata, dict) else None
    if max_parallel != 1:
        failures.append(
            CheckFailure(
                code="CICD_CONCURRENCY_REQUIRED",
                message="Pipeline must control concurrency for IaC (max_parallel=1)",
                path=str(pipeline_path),
                pain_point="cicd_delivery",
            )
        )

    return failures

