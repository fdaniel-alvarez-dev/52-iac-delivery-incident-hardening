from __future__ import annotations

import re
from pathlib import Path

from ..model import CheckFailure
from ..tomlutil import get_key, load_toml

_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+].+)?$")


def _is_pinned_version(value) -> bool:
    if not isinstance(value, str):
        return False
    if value.strip().lower() in {"latest", "*", ""}:
        return False
    return bool(_SEMVER.match(value.strip()))


def check_iac_controls(dev_path: Path, prod_path: Path, parity_rules_path: Path) -> list[CheckFailure]:
    dev = load_toml(dev_path)
    prod = load_toml(prod_path)
    parity = load_toml(parity_rules_path)

    failures: list[CheckFailure] = []

    tf_ver = get_key(dev, "terraform.required_version")
    if not _is_pinned_version(tf_ver):
        failures.append(
            CheckFailure(
                code="IAC_TERRAFORM_VERSION_NOT_PINNED",
                message="Terraform required_version must be a pinned semver (e.g., 1.6.6)",
                path=str(dev_path),
                pain_point="iac_drift",
            )
        )

    aws_ver = get_key(dev, "providers.aws.version")
    if not _is_pinned_version(aws_ver):
        failures.append(
            CheckFailure(
                code="IAC_PROVIDER_VERSION_NOT_PINNED",
                message="Provider versions must be pinned (no floating versions)",
                path=str(dev_path),
                pain_point="iac_drift",
            )
        )

    module_ver = get_key(dev, "modules.network.version")
    if not _is_pinned_version(module_ver):
        failures.append(
            CheckFailure(
                code="IAC_MODULE_VERSION_NOT_PINNED",
                message="Module versions must be pinned (no floating branches/tags)",
                path=str(dev_path),
                pain_point="iac_drift",
            )
        )

    for env_name, env_data, env_file in [("dev", dev, dev_path), ("prod", prod, prod_path)]:
        backend = get_key(env_data, "state.backend")
        encryption = get_key(env_data, "state.encryption")
        lock_table = get_key(env_data, "state.lock_table")
        if backend not in {"s3", "remote"}:
            failures.append(
                CheckFailure(
                    code="IAC_STATE_BACKEND_UNSAFE",
                    message=f"State backend must be remote (s3/remote); got {backend!r}",
                    path=str(env_file),
                    pain_point="iac_drift",
                )
            )
        if encryption is not True:
            failures.append(
                CheckFailure(
                    code="IAC_STATE_ENCRYPTION_REQUIRED",
                    message="Remote state encryption must be enabled",
                    path=str(env_file),
                    pain_point="iac_drift",
                )
            )
        if not isinstance(lock_table, str) or not lock_table.strip():
            failures.append(
                CheckFailure(
                    code="IAC_STATE_LOCKING_REQUIRED",
                    message=f"Remote state locking must be configured for {env_name}",
                    path=str(env_file),
                    pain_point="iac_drift",
                )
            )

    required_equal = parity.get("required_equal", [])
    allowed_different = set(parity.get("allowed_different", []))

    if not isinstance(required_equal, list) or not all(isinstance(x, str) for x in required_equal):
        failures.append(
            CheckFailure(
                code="IAC_PARITY_RULES_INVALID",
                message="parity_rules.toml must define required_equal as a list of dotted keys",
                path=str(parity_rules_path),
                pain_point="iac_drift",
            )
        )
        return failures

    for dotted_key in required_equal:
        dev_v = get_key(dev, dotted_key)
        prod_v = get_key(prod, dotted_key)
        if dev_v != prod_v:
            failures.append(
                CheckFailure(
                    code="IAC_ENV_PARITY_DRIFT",
                    message=f"Key must match across envs: {dotted_key} (dev={dev_v!r}, prod={prod_v!r})",
                    path=str(parity_rules_path),
                    pain_point="iac_drift",
                )
            )

    # Catch unexpected drift: keys present in both but different and not explicitly allowed.
    for dotted_key in [
        "workload.instance_type",
        "workload.instance_count",
        "state.region",
        "providers.aws.version",
    ]:
        if dotted_key in allowed_different:
            continue
        dev_v = get_key(dev, dotted_key)
        prod_v = get_key(prod, dotted_key)
        if dev_v is not None and prod_v is not None and dev_v != prod_v:
            failures.append(
                CheckFailure(
                    code="IAC_UNEXPECTED_DRIFT",
                    message=f"Unexpected drift not allowed by parity rules: {dotted_key}",
                    path=str(parity_rules_path),
                    pain_point="iac_drift",
                )
            )

    return failures
