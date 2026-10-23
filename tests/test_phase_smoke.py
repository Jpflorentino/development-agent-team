"""Exercise the multi-turn test harness with simulated CLI events, not models."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import native_phase_smoke as smoke


def reply(thread="fixture-session"):
    return 0, "\n".join(json.dumps(event) for event in (
        {"type": "thread.started", "thread_id": thread},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "Proposta para discussão. Aprova?"}},
        {"type": "turn.completed"},
    )), ""


class PhaseSmokeTests(unittest.TestCase):
    def run_fixture(self, invoke):
        with tempfile.TemporaryDirectory() as tmp:
            artifacts = Path(tmp) / "artifacts"
            artifacts.mkdir()
            with patch.object(smoke.tempfile, "mkdtemp", return_value=str(artifacts)), \
                 patch.object(smoke.shutil, "which", return_value="codex"), \
                 patch.object(smoke, "invoke", side_effect=invoke) as native, \
                 patch.object(smoke.sys, "argv", ["native_phase_smoke.py", "--execute"]), \
                 contextlib.redirect_stdout(io.StringIO()):
                code = smoke.main()
            result = json.loads((artifacts / "assessment.json").read_text())
            return code, result, native.call_args_list

    def test_same_session_continues_read_only_and_requires_manual_review(self):
        code, result, calls = self.run_fixture(lambda *args: reply())
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 4)
        self.assertEqual(result["status"], "ready_for_manual_review")
        for index, call in enumerate(calls):
            command = call.args[0]
            self.assertEqual(command[command.index("--sandbox") + 1], "read-only")
            if index:
                self.assertIn("resume", command)
                self.assertIn("fixture-session", command)
        self.assertTrue(result["manual_review_required"])

    def test_usage_failure_stops_without_claiming_phase_success(self):
        def limited(*args):
            return 1, json.dumps({"type": "turn.failed", "error": {"message": "Usage limit"}}), ""
        code, result, calls = self.run_fixture(limited)
        self.assertEqual(code, 2)
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(len(calls), 1)

    def test_explanation_without_question_does_not_abort_audit(self):
        count = 0
        def explain(*args):
            nonlocal count
            count += 1
            code, stdout, stderr = reply()
            if count == 2:
                stdout = stdout.replace("Aprova?", "Continuamos em discussão, sem implementar.")
            return code, stdout, stderr
        code, result, calls = self.run_fixture(explain)
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 4)
        self.assertFalse(result["turns"][1]["format_check"]["asks_discovery_questions"])

    def test_project_mutation_stops_conversation(self):
        def mutate(command, prompt, folder, timeout):
            (folder / "unexpected.txt").write_text("Unexpected application change")
            return reply()
        code, result, calls = self.run_fixture(mutate)
        self.assertEqual(code, 2)
        self.assertFalse(result["turns"][0]["project_files_unchanged"])
        self.assertEqual(len(calls), 1)

    def test_changed_session_is_not_accepted_as_continuation(self):
        identifiers = iter(("fixture-session", "different-session"))
        code, result, calls = self.run_fixture(lambda *args: reply(next(identifiers)))
        self.assertEqual(code, 2)
        self.assertEqual(len(calls), 2)
        self.assertIn("Same-session continuation not established", result["turns"][-1]["errors"])

    def test_execution_is_opt_in(self):
        with patch.object(smoke.sys, "argv", ["native_phase_smoke.py"]), \
             patch.object(smoke, "invoke") as native, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(smoke.main(), 0)
        native.assert_not_called()
