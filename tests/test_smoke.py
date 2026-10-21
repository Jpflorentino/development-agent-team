"""Simulated event-parser contracts, not native model execution."""
import json
import unittest

from dat.policy import REPORT_FIELDS
from dat.smoke import assess_codex, assess_discovery


def fixture(report):
    return [
        {"payload": {"item": {"type": "SubAgentActivity", "kind": "started", "agent_thread_id": "child"}}},
        {"payload": {"item": {"type": "SubAgentActivity", "kind": "completed", "agent_thread_id": "child"}}},
        {"payload": {"type": "agent_message", "author": "/root/reviewer", "content": [
            {"text": "Message Type: FINAL_ANSWER\nPayload:\n" + json.dumps(report)}]}}
    ]


class SmokeParserTests(unittest.TestCase):
    def report(self):
        report = {key: [] for key in REPORT_FIELDS}
        report.update(STATUS="completed", SUMMARY="Static review", EVIDENCE=["DAT_CONTEXT_1_0_0", "ZeroDivisionError"])
        return report

    def test_model_success_claim_without_tool_events_cannot_pass(self):
        self.assertEqual(assess_codex([{"payload": {"type": "agent_message", "text": "Success"}}])["status"], "incomplete")

    def test_invalid_native_child_envelope_cannot_pass(self):
        report = self.report()
        report["EVIDENCE"] = {"marker": "DAT_CONTEXT_1_0_0", "finding": "ZeroDivisionError"}
        result = assess_codex(fixture(report))
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("EVIDENCE must be a list", result["errors"])

    def test_completed_child_and_valid_report_pass_role_only(self):
        result = assess_codex(fixture(self.report()))
        self.assertEqual(result["status"], "passed", result)
        self.assertEqual(result["native_named_profile_loaded"], "NOT_VERIFIED_BY_ROLE_ENVELOPE_TEST")

    def test_unfinished_child_or_missing_marker_cannot_pass(self):
        report = self.report()
        report["EVIDENCE"] = ["Unrelated evidence"]
        events = fixture(report)
        del events[1]
        self.assertEqual(assess_codex(events)["status"], "incomplete")


class DiscoveryParserTests(unittest.TestCase):
    def assess(self, text, completed=True):
        events = [{"type": "item.completed", "item": {"type": "agent_message", "text": text}}]
        if completed:
            events.append({"type": "turn.completed"})
        return assess_discovery(events)

    def test_plain_recommendation_and_questions_pass(self):
        result = self.assess("Recomendo um site com páginas para a equipa e marcações.\n\nQue calendários usam atualmente?")
        self.assertEqual(result["status"], "passed")

    def test_original_internal_report_regression_is_rejected(self):
        report = {"STATUS": "completed", "SUMMARY": "Recomendo um site", "QUESTIONS": ["Que calendários usam?"]}
        for text in (json.dumps(report), "```json\n" + json.dumps(report) + "\n```",
                     "Recomendação:\n```json\n" + json.dumps(report) + "\n```",
                     "STATUS: completed\nSUMMARY: Site\nQUESTIONS: Que calendários usam?"):
            with self.subTest(text=text):
                self.assertTrue(self.assess(text)["internal_report_exposed"])
                self.assertEqual(self.assess(text)["status"], "incomplete")

    def test_progress_only_or_missing_questions_cannot_pass(self):
        self.assertEqual(self.assess("Vou analisar. Que calendários usam?", completed=False)["status"], "incomplete")
        self.assertEqual(self.assess("Recomendo um site.")["status"], "incomplete")

    def test_claude_error_cannot_be_treated_as_a_conversation(self):
        result = assess_discovery([{"type": "result", "result": "Not logged in", "is_error": True}])
        self.assertEqual(result["status"], "incomplete")
