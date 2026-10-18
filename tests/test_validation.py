import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from dat.validation import validate

ROOT = Path(__file__).resolve().parents[1]


class ValidationTests(unittest.TestCase):
    def test_repository_structure(self):
        self.assertEqual(validate(ROOT)["errors"], [])

    def test_cli_structured_output_and_version(self):
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/dat.py"), "validate"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["status"], "success")
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/dat.py"), "--version"], capture_output=True, text=True)
        self.assertEqual(proc.stdout.strip(), "1.0.0")

    def test_cli_reports_conflict_as_error(self):
        with tempfile.TemporaryDirectory() as folder:
            proc = subprocess.run([sys.executable, str(ROOT / "scripts/dat.py"), "update", "--platform", "codex", "--target", folder],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(json.loads(proc.stderr)["status"], "error")

    def test_validator_rejects_disabled_mandatory_read_only_roles(self):
        import shutil
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "framework"
            shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            path = source / "agents/catalog.json"
            catalog = json.loads(path.read_text())
            for agent in catalog["agents"]:
                if agent["id"] in ("security-engineer", "code-review-engineer"):
                    agent["read_only"] = False
            path.write_text(json.dumps(catalog))
            errors = validate(source)["errors"]
            self.assertTrue(any("mandatory read_only" in message for message in errors), errors)
