"""Existing-code routing, reviewer permissions and upgrade preservation."""
import json
import contextlib
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from dat.context import ROLES, role_path
from dat.installer import maintain
from dat.onboarding import STATE, record, status
from dat.policy import select
from dat.storage import Conflict
from dat.validation import validate

ROOT = Path(__file__).resolve().parents[1]
ROLE = "code-optimization-engineer"


class CodeOptimizationTests(unittest.TestCase):
    def test_optimization_review_does_not_dispatch_implementers_or_satisfy_review_gate(self):
        plan = select("CODE_OPTIMIZATION", "CRITICAL", areas=["frontend", "backend", "database"], delegation=True)
        self.assertEqual(plan["specialists"], [ROLE])
        self.assertTrue(plan["execution"]["read_only"])
        self.assertTrue(plan["execution"]["requires_existing_implementation"])
        self.assertFalse(plan["execution"]["review_independence_possible"])
        self.assertIn("independent_code_review", plan["gates"])

    def test_empty_project_selection_never_activates_optimizer(self):
        for risk in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
            with self.subTest(risk=risk):
                plan = select("NEW_PROJECT", risk, areas=["optimization"])
                self.assertNotIn(ROLE, plan["specialists"])
                self.assertFalse(plan["execution"]["requires_existing_implementation"])

    def test_authorized_refactoring_retains_domain_owners_and_checks(self):
        plan = select("REFACTORING", "MEDIUM", areas=["backend"])
        self.assertEqual(plan["specialists"], ["backend-developer", "qa-engineer", "code-review-engineer"])
        self.assertFalse(plan["execution"]["read_only"])

    def test_upgrade_adds_pending_role_without_rewriting_existing_analysis(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "project"
            maintain(ROOT, target, "codex")
            for role in ROLES:
                record(target, role, "not_applicable", "Harness baseline has no implemented application domain")
            state_path = target / STATE
            legacy = json.loads(state_path.read_text(encoding="utf-8"))
            legacy["roles"].pop(ROLE)
            legacy["integration_review"] = {"status": "verified", "binding": "selected-board"}
            legacy["user_note"] = "Preserve prior evidence and scope"
            state_path.write_text(json.dumps(legacy), encoding="utf-8")
            (target / role_path(ROLE)).unlink()
            previous = {role: (target / role_path(role)).read_bytes() for role in ROLES if role != ROLE}
            maintain(ROOT, target, "codex", action="update")
            updated = json.loads(state_path.read_text(encoding="utf-8"))
            for role, value in legacy["roles"].items():
                self.assertEqual(updated["roles"][role], value)
                self.assertEqual((target / role_path(role)).read_bytes(), previous[role])
            self.assertEqual(updated["integration_review"], legacy["integration_review"])
            self.assertEqual(updated["user_note"], legacy["user_note"])
            self.assertEqual(updated["roles"][ROLE]["status"], "pending")
            self.assertIn("BOOTSTRAP_PENDING", (target / role_path(ROLE)).read_text(encoding="utf-8"))
            self.assertEqual(status(target)["phase"], "pending")
            self.assertEqual(maintain(ROOT, target, "codex", action="update")["changed"], [])

    def test_unknown_onboarding_shape_is_preserved_and_blocks_upgrade(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "project"
            maintain(ROOT, target, "codex")
            path = target / STATE
            state = json.loads(path.read_text(encoding="utf-8"))
            state["roles"]["unknown-future-role"] = {"status": "pending"}
            path.write_text(json.dumps(state), encoding="utf-8")
            before = path.read_bytes()
            with self.assertRaisesRegex(Conflict, "Unsupported onboarding record"):
                maintain(ROOT, target, "codex", action="update")
            self.assertEqual(path.read_bytes(), before)

    def test_optimizer_cannot_be_made_writable_in_catalog(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "framework"
            shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            path = source / "agents/catalog.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            next(agent for agent in data["agents"] if agent["id"] == ROLE)["read_only"] = False
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertIn(f"{ROLE}: mandatory read_only safety policy disabled", validate(source)["errors"])

    def test_native_review_is_opt_in(self):
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/native_optimization_smoke.py")], capture_output=True, text=True, timeout=15)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(json.loads(proc.stdout)["status"], "not_run")

    def test_failed_native_turn_does_not_count_progress_as_a_final_review(self):
        from scripts import native_optimization_smoke as smoke
        events = [{"type": "item.completed", "item": {"type": "agent_message", "text": "Vou analisar o código."}},
                  {"type": "turn.failed", "error": {"message": "Synthetic usage limit"}}]
        with tempfile.TemporaryDirectory() as folder, patch.object(smoke.tempfile, "mkdtemp", return_value=folder), \
                patch.object(smoke.shutil, "which", return_value="codex"), \
                patch.object(smoke, "invoke", return_value=(1, "\n".join(json.dumps(e) for e in events), "")), \
                patch.object(sys, "argv", ["native_optimization_smoke.py", "--execute"]):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = smoke.main()
            result = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertFalse(result["checks"]["process_completed"])
        self.assertFalse(result["checks"]["final_response_present"])
        self.assertTrue(result["checks"]["project_unchanged"])
        self.assertEqual(result["native_errors"], ["Synthetic usage limit"])
