"""Deterministic orchestration contracts, not a model or agent runtime.

The caller supplies verified capabilities and explicit affected areas. No tool
is invoked and no authorization is granted by selecting a policy.
"""
from collections.abc import Mapping

MODES = (
    "NEW_PROJECT", "EXISTING_PROJECT", "FEATURE_DEVELOPMENT", "BUG_FIX",
    "CODE_REVIEW", "CODE_OPTIMIZATION", "ARCHITECTURE_REVIEW", "REFACTORING", "SECURITY_AUDIT",
    "DATABASE_OPTIMIZATION", "DESIGN", "TESTING", "DEPLOYMENT", "MODERNIZATION",
)
RISKS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
AREA_AGENTS = {
    "architecture": "software-architect", "design": "ui-ux-designer",
    "frontend": "frontend-developer", "backend": "backend-developer",
    "database": "database-engineer", "qa": "qa-engineer",
    "security": "security-engineer", "devops": "devops-engineer",
    "optimization": "code-optimization-engineer",
}
MODE_AGENTS = {
    "NEW_PROJECT": ("software-architect",),
    "CODE_REVIEW": ("code-review-engineer",),
    "CODE_OPTIMIZATION": ("code-optimization-engineer",),
    "ARCHITECTURE_REVIEW": ("software-architect",),
    "SECURITY_AUDIT": ("security-engineer",),
    "DATABASE_OPTIMIZATION": ("database-engineer",),
    "DESIGN": ("ui-ux-designer",), "TESTING": ("qa-engineer",),
    "DEPLOYMENT": ("devops-engineer",),
    "MODERNIZATION": ("software-architect",),
}
TASK_FIELDS = (
    "TASK_ID", "OBJECTIVE", "CONTEXT", "CONSTRAINTS", "FILES",
    "ACCEPTANCE_CRITERIA", "PERMISSIONS", "DEPENDENCIES", "EXPECTED_OUTPUT",
)
REPORT_FIELDS = (
    "STATUS", "SUMMARY", "FINDINGS", "CHANGES", "EVIDENCE", "TESTS", "RISKS",
    "DECISIONS", "QUESTIONS", "CONTEXT_UPDATES",
)
SEVERITIES = frozenset({"BLOCKER", "CRITICAL", "HIGH", "MEDIUM", "LOW", "SUGGESTION", "INFO"})
GATES = {
    "LOW": ("acceptance", "scope", "localized_validation", "relevant_tests"),
    "MEDIUM": ("code_review", "functional_validation"),
    "HIGH": ("independent_code_review", "affected_specialists", "sensitive_change_authorization"),
    "CRITICAL": ("deep_review", "security_validation", "rollback_assessment",
                 "authorization_confirmation", "appropriate_environment_tests", "operational_impact"),
}


def _risk(value):
    if value not in RISKS:
        raise ValueError(f"Unknown risk: {value!r}")
    return value


def select(mode, risk="LOW", areas=(), delegation=False, parallel=False):
    """Return a policy proposal; all gates still need execution and evidence.

    ``delegation`` and ``parallel`` describe capabilities verified by the caller.
    Parallel capability never waives ownership, isolation or dependency checks.
    Generic implementation modes leave area selection to the Team Leader.
    """
    if mode not in MODES:
        raise ValueError(f"Unknown mode: {mode!r}")
    _risk(risk)
    if not isinstance(delegation, bool) or not isinstance(parallel, bool):
        raise ValueError("delegation and parallel must be verified boolean capabilities")
    if isinstance(areas, str):
        raise ValueError("areas must be a sequence of explicit area names")
    areas = tuple(areas)
    if any(not isinstance(area, str) for area in areas):
        raise ValueError("Every area must be a string")
    unknown = set(areas).difference(AREA_AGENTS)
    if unknown:
        raise ValueError(f"Unknown areas: {sorted(unknown)!r}")
    specialists = list(MODE_AGENTS.get(mode, ()))
    # Review-only modes stay read-only. Domain implementers can be consulted by
    # the leader when necessary, rather than automatically being summoned.
    review_only = mode in {"CODE_REVIEW", "CODE_OPTIMIZATION", "ARCHITECTURE_REVIEW", "SECURITY_AUDIT"}
    if not review_only:
        specialists += [agent for area, agent in AREA_AGENTS.items() if area in areas and not (mode == "NEW_PROJECT" and area == "optimization")]
    if risk != "LOW" and not review_only:
        specialists.extend(("qa-engineer", "code-review-engineer"))
    if risk == "CRITICAL" and not review_only:
        specialists.append("security-engineer")
    specialists = list(dict.fromkeys(specialists))
    gates = list(GATES["LOW"])
    for level in RISKS[1:RISKS.index(risk) + 1]:
        gates.extend(GATES[level])
    return {
        "mode": mode, "risk": risk, "specialists": specialists, "gates": gates,
        "execution": {
            "strategy": "native_delegation" if delegation else "sequential_role_simulation",
            "parallel_capable": bool(delegation and parallel),
            "parallel_requires": ["independent_tasks", "agreed_contracts", "exclusive_file_ownership", "isolation"],
            "review_independence_possible": bool(delegation and "code-review-engineer" in specialists),
            "read_only": review_only,
            "requires_existing_implementation": "code-optimization-engineer" in specialists,
        },
    }


def _fields(value, fields):
    if not isinstance(value, Mapping):
        return ["Expected an object"]
    return [f"Missing {key}" for key in fields if key not in value]


def validate_task(task):
    """Validate delegation shape; permissions remain explicit and untrusted."""
    errors = _fields(task, TASK_FIELDS)
    if not isinstance(task, Mapping):
        return errors
    for key in ("TASK_ID", "OBJECTIVE", "EXPECTED_OUTPUT"):
        if key in task and (not isinstance(task[key], str) or not task[key].strip()):
            errors.append(f"{key} must be nonempty text")
    if "CONTEXT" in task:
        context = task["CONTEXT"]
        if not ((isinstance(context, str) and context.strip()) or
                (isinstance(context, Mapping) and context)):
            errors.append("CONTEXT must be nonempty text or a nonempty object")
    for key in ("CONSTRAINTS", "FILES", "ACCEPTANCE_CRITERIA", "PERMISSIONS", "DEPENDENCIES"):
        if key in task and (not isinstance(task[key], list) or any(not isinstance(x, str) for x in task[key])):
            errors.append(f"{key} must be a list of strings")
    if task.get("ACCEPTANCE_CRITERIA") == []:
        errors.append("ACCEPTANCE_CRITERIA must not be empty")
    return errors


def validate_report(report):
    """Validate specialist response shape without pretending evidence is true."""
    errors = _fields(report, REPORT_FIELDS)
    if not isinstance(report, Mapping):
        return errors
    if report.get("STATUS") not in ("completed", "blocked", "needs_clarification", "failed"):
        errors.append("Invalid STATUS")
    if "SUMMARY" in report and (not isinstance(report["SUMMARY"], str) or not report["SUMMARY"].strip()):
        errors.append("SUMMARY must be nonempty text")
    for key in REPORT_FIELDS[2:]:
        if key in report and not isinstance(report[key], list):
            errors.append(f"{key} must be a list")
    findings = report.get("FINDINGS", [])
    for index, finding in enumerate(findings if isinstance(findings, list) else []):
        if isinstance(finding, Mapping) and "severity" in finding:
            severity = finding["severity"]
            if not isinstance(severity, str) or severity.strip().upper() not in SEVERITIES:
                errors.append(f"FINDINGS[{index}].severity must be a recognized severity string")
    if report.get("STATUS") == "completed" and not report.get("EVIDENCE"):
        errors.append("Completed report requires EVIDENCE")
    return errors


def quality_gate(report, risk="LOW", independent_review=False):
    """Fail closed on missing central validation and declared blocking findings.

    Supplemental GATE_RESULTS maps each selected gate to a boolean. The leader
    must inspect evidence; setting booleans is no substitute for actual checks.
    """
    _risk(risk)
    if not isinstance(independent_review, bool):
        raise ValueError("independent_review must be a verified boolean")
    blockers = validate_report(report)
    if not isinstance(report, Mapping):
        return {"passed": False, "blockers": blockers}
    if report.get("STATUS") != "completed":
        blockers.append("Specialist task is not completed")
    for finding in report.get("FINDINGS", []) if isinstance(report.get("FINDINGS"), list) else []:
        severity = finding.get("severity") if isinstance(finding, Mapping) else None
        if isinstance(severity, str) and severity.strip().upper() in ("BLOCKER", "HIGH", "CRITICAL") and finding.get("resolved") is not True:
            blockers.append("Unresolved blocking finding")
    results = report.get("GATE_RESULTS", {})
    if not isinstance(results, Mapping):
        results = {}
    for level in RISKS[:RISKS.index(risk) + 1]:
        for gate in GATES[level]:
            if results.get(gate) is not True:
                blockers.append(f"Gate not satisfied: {gate}")
    if risk in {"HIGH", "CRITICAL"} and not independent_review:
        blockers.append("Independent review unavailable; sequential role simulation is insufficient")
    return {"passed": not blockers, "blockers": blockers}


def resolve_conflict(reports, attempts=0):
    """Return the next coordination step; never choose a winner by status alone."""
    if attempts < 0:
        raise ValueError("attempts must not be negative")
    if attempts >= 2:
        return "reassess_and_report_blocker"
    reports = tuple(reports)
    if not reports or any(validate_report(report) for report in reports):
        return "request_valid_reports"
    if any(report["STATUS"] != "completed" for report in reports):
        return "report_blocker_or_clarification"
    return "compare_evidence_and_route_to_owner"


def recovery(state):
    """Require current evidence after interruptions instead of trusting memory."""
    if state not in {"interrupted", "blocked", "completed"}:
        raise ValueError("Unknown recovery state")
    return ["read_context", "inspect_worktree", "verify_authorizations", "reconcile_evidence", "resume_dependencies"]
