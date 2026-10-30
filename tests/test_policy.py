"""Contract/simulation tests; these tests do not execute models or subagents."""
import unittest

from dat.policy import (GATES, MODES, REPORT_FIELDS, RISKS, TASK_FIELDS,
                        quality_gate, recovery, resolve_conflict, select,
                        validate_report, validate_task)


def report():
    value = {field: [] for field in REPORT_FIELDS}
    value.update(STATUS="completed", SUMMARY="Implemented scoped change",
                 EVIDENCE=["src/api.py:20 inspected"],
                 GATE_RESULTS={gate: True for gates in GATES.values() for gate in gates})
    return value


class PolicyTests(unittest.TestCase):
    def test_small_frontend_change_avoids_whole_team(self):
        result = select("FEATURE_DEVELOPMENT", areas=["frontend"])
        self.assertEqual(result["specialists"], ["frontend-developer"])
        self.assertEqual(result["execution"]["strategy"], "sequential_role_simulation")
        self.assertFalse(result["execution"]["review_independence_possible"])

    def test_endpoint_uses_explicit_areas(self):
        self.assertEqual(select("FEATURE_DEVELOPMENT", "MEDIUM", ["backend", "database"])["specialists"],
                         ["backend-developer", "database-engineer", "qa-engineer", "code-review-engineer"])

    def test_auth_risk_uses_security_only_when_affected(self):
        result = select("FEATURE_DEVELOPMENT", "HIGH", ["backend", "security"], delegation=True, parallel=True)
        self.assertIn("independent_code_review", result["gates"])
        self.assertTrue(result["execution"]["review_independence_possible"])
        self.assertNotIn("review_independent", result["execution"])
        self.assertTrue(result["execution"]["parallel_capable"])
        self.assertIn("isolation", result["execution"]["parallel_requires"])

    def test_parallel_requires_real_delegation(self):
        self.assertFalse(select("NEW_PROJECT", parallel=True)["execution"]["parallel_capable"])

    def test_all_modes_and_risks_have_contracts(self):
        for mode in MODES:
            for risk in RISKS:
                result = select(mode, risk)
                self.assertEqual(len(result["specialists"]), len(set(result["specialists"])))
                self.assertIn("acceptance", result["gates"])

    def test_review_mode_is_read_only(self):
        for mode, specialist in [("CODE_REVIEW", "code-review-engineer"),
                                 ("CODE_OPTIMIZATION", "code-optimization-engineer"),
                                 ("ARCHITECTURE_REVIEW", "software-architect"),
                                 ("SECURITY_AUDIT", "security-engineer")]:
            with self.subTest(mode=mode):
                result = select(mode, "CRITICAL", areas=["backend", "frontend", "database"])
                self.assertEqual(result["specialists"], [specialist])
                self.assertTrue(result["execution"]["read_only"])

    def test_invalid_selections_rejected(self):
        for args in [("GUESS",), ("BUG_FIX", "RISKY"), ("BUG_FIX", "LOW", ["unknown"]), ("BUG_FIX", "LOW", "frontend")]:
            with self.assertRaises(ValueError):
                select(*args)

    def test_capabilities_and_areas_reject_ambiguous_input(self):
        with self.assertRaises(ValueError):
            select("CODE_REVIEW", delegation="false")
        with self.assertRaises(ValueError):
            select("FEATURE_DEVELOPMENT", parallel=1)
        with self.assertRaises(ValueError):
            select("FEATURE_DEVELOPMENT", areas=["frontend", {}])

    def test_delegation_requires_complete_contract(self):
        value = {field: [] for field in TASK_FIELDS}
        value.update(TASK_ID="T1", OBJECTIVE="Fix validation", CONTEXT="Existing API",
                     ACCEPTANCE_CRITERIA=["Invalid input returns 400"], EXPECTED_OUTPUT="Diff and test evidence")
        self.assertEqual(validate_task(value), [])
        del value["PERMISSIONS"]
        self.assertIn("Missing PERMISSIONS", validate_task(value))

    def test_completed_claim_requires_evidence(self):
        value = report()
        value["EVIDENCE"] = []
        self.assertIn("Completed report requires EVIDENCE", validate_report(value))

    def test_delegation_rejects_missing_or_malformed_context(self):
        value = {field: [] for field in TASK_FIELDS}
        value.update(TASK_ID="T1", OBJECTIVE="Compare architecture", ACCEPTANCE_CRITERIA=["Explain tradeoffs"],
                     EXPECTED_OUTPUT="Evidence-backed proposal")
        for context in (None, False, 42, {}, [], "", "   "):
            with self.subTest(context=context):
                value["CONTEXT"] = context
                self.assertIn("CONTEXT must be nonempty text or a nonempty object", validate_task(value))
        for context in ("Known product brief", {"brief": "Known product brief"}):
            value["CONTEXT"] = context
            self.assertEqual(validate_task(value), [])

    def test_blocking_severity_is_case_and_whitespace_insensitive(self):
        for severity in ("HIGH", "high", " High ", "critical", "blocker"):
            with self.subTest(severity=severity):
                value = report()
                value["FINDINGS"] = [{"severity": severity, "resolved": False}]
                result = quality_gate(value)
                self.assertFalse(result["passed"])
                self.assertIn("Unresolved blocking finding", result["blockers"])
        value["FINDINGS"][0]["resolved"] = True
        self.assertTrue(quality_gate(value)["passed"])

    def test_malformed_or_unknown_severity_fails_closed(self):
        for severity in (None, [], {}, 1, "", "unknown"):
            with self.subTest(severity=severity):
                value = report()
                value["FINDINGS"] = [{"severity": severity, "resolved": True}]
                self.assertFalse(quality_gate(value)["passed"])
                self.assertTrue(any("severity" in error for error in validate_report(value)))
        for severity in ("medium", "low", "suggestion", "info"):
            value["FINDINGS"][0] = {"severity": severity}
            self.assertTrue(quality_gate(value)["passed"])

    def test_gate_requires_real_independent_review_at_high_risk(self):
        self.assertFalse(quality_gate(report(), "HIGH")["passed"])
        self.assertTrue(quality_gate(report(), "HIGH", independent_review=True)["passed"])
        with self.assertRaises(ValueError):
            quality_gate(report(), "HIGH", independent_review="false")

    def test_gate_rejects_failures_missing_authorization_and_findings(self):
        value = report()
        value["GATE_RESULTS"]["authorization_confirmation"] = False
        value["FINDINGS"] = [{"severity": "BLOCKER", "resolved": False}]
        result = quality_gate(value, "CRITICAL", independent_review=True)
        self.assertFalse(result["passed"])
        self.assertIn("Unresolved blocking finding", result["blockers"])
        self.assertIn("Gate not satisfied: authorization_confirmation", result["blockers"])

    def test_gate_fails_closed(self):
        self.assertFalse(quality_gate(None)["passed"])
        value = report()
        del value["GATE_RESULTS"]
        self.assertFalse(quality_gate(value)["passed"])
        value["STATUS"] = "blocked"
        self.assertFalse(quality_gate(value)["passed"])

    def test_conflict_correction_is_bounded(self):
        self.assertEqual(resolve_conflict([report()]), "compare_evidence_and_route_to_owner")
        self.assertEqual(resolve_conflict([{}]), "request_valid_reports")
        self.assertEqual(resolve_conflict([]), "request_valid_reports")
        self.assertEqual(resolve_conflict([report()], 2), "reassess_and_report_blocker")

    def test_blocked_specialist_returns_control_to_leader(self):
        for status in ("blocked", "needs_clarification", "failed"):
            value = report()
            value["STATUS"] = status
            self.assertEqual(resolve_conflict([value]), "report_blocker_or_clarification")
            self.assertEqual(resolve_conflict(iter([value])), "report_blocker_or_clarification")

    def test_recovery_revalidates_context_and_permissions(self):
        self.assertIn("inspect_worktree", recovery("interrupted"))
        self.assertIn("verify_authorizations", recovery("blocked"))


if __name__ == "__main__":
    unittest.main()
