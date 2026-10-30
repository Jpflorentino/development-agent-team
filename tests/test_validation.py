import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from dat.validation import doctor, validate

ROOT = Path(__file__).resolve().parents[1]


class ValidationTests(unittest.TestCase):
    def test_doctor_warns_when_managed_installation_is_absent(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as folder, patch("dat.validation.shutil.which", return_value=None):
            result = doctor(ROOT, Path(folder))
        self.assertEqual(result["installations"], [])
        self.assertIn("No managed agent installation found in this target", result["warnings"])
        self.assertEqual(result["errors"], [])

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
            catalog = json.loads(path.read_text(encoding="utf-8"))
            for agent in catalog["agents"]:
                if agent["id"] in ("security-engineer", "code-review-engineer", "code-optimization-engineer"):
                    agent["read_only"] = False
            path.write_text(json.dumps(catalog), encoding="utf-8")
            errors = validate(source)["errors"]
            self.assertTrue(any("mandatory read_only" in message for message in errors), errors)

    def test_unicode_context_works_with_ascii_console_encoding(self):
        import os
        from dat import memory
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            memory.init(target)
            memory.add(target, "PROJECT", "Engenharia em português — 日本語")
            env = dict(os.environ, PYTHONIOENCODING="ascii")
            proc = subprocess.run([sys.executable, str(ROOT / "scripts/dat.py"), "memory", "show", "--target", folder],
                                  capture_output=True, env=env)
            self.assertEqual(proc.returncode, 0, proc.stderr.decode("ascii"))
            result = json.loads(proc.stdout.decode("ascii"))
            self.assertIn("português — 日本語", result["result"]["text"])
