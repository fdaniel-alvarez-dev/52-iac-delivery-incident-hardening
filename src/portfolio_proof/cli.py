from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path

from .engine import run_checks
from .report import write_report


@dataclass(frozen=True)
class ExitCodes:
    ok: int = 0
    validation_failed: int = 2
    usage: int = 64


def _default_examples_dir() -> Path:
    return Path("examples")


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="portfolio_proof",
        description="IaC/Delivery/Reliability guardrail demo (stdlib-only).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    report_p = sub.add_parser("report", help="Generate a human-readable artifacts report (Markdown).")
    report_p.add_argument("--examples", type=Path, default=_default_examples_dir())
    report_p.add_argument("--out", type=Path, default=Path("artifacts/report.md"))

    validate_p = sub.add_parser("validate", help="Validate example inputs; exit non-zero on violations.")
    validate_p.add_argument("--examples", type=Path, default=_default_examples_dir())

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    # Guardrail: never print GITHUB_TOKEN (or any secret-looking env var).
    os.environ.pop("GITHUB_TOKEN", None)

    results = run_checks(args.examples)

    if args.cmd == "report":
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_report(args.out, args.examples, results)
        return ExitCodes.ok

    if args.cmd == "validate":
        if results.failures:
            for failure in results.failures:
                print(f"FAIL: {failure.code} - {failure.message} ({failure.path})")
            return ExitCodes.validation_failed
        print("OK: all controls satisfied")
        return ExitCodes.ok

    return ExitCodes.usage

