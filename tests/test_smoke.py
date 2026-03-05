from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON = str(REPO_ROOT / ".venv/bin/python")


class SmokeTests(unittest.TestCase):
    def test_validate_examples_ok(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
        cp = subprocess.run(
            [PYTHON, "-m", "portfolio_proof", "validate", "--examples", str(REPO_ROOT / "examples")],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        self.assertEqual(cp.returncode, 0, cp.stdout)
        self.assertIn("OK: all controls satisfied", cp.stdout)

    def test_report_generates_markdown(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "report.md"
            cp = subprocess.run(
                [PYTHON, "-m", "portfolio_proof", "report", "--examples", str(REPO_ROOT / "examples"), "--out", str(out)],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
            self.assertEqual(cp.returncode, 0, cp.stdout)
            self.assertTrue(out.exists())
            content = out.read_text(encoding="utf-8")
            self.assertIn("IaC / Delivery / Incident Hardening Report", content)
            self.assertIn("Validation results", content)

