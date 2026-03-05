from __future__ import annotations

from pathlib import Path

import tomllib


def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        data = tomllib.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Unexpected TOML root type: {type(data)}")
    return data


def get_key(data: dict, dotted: str):
    cur = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur

