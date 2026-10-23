"""Evidence parsing for opt-in smoke tests; never trusts a model's final claim."""
import json
import re

from .policy import REPORT_FIELDS, validate_report


def assess_discovery(events, *, require_question=True):
    """Check a normal discovery turn's format, not the truth of its advice."""
    messages, errors = [], []
    completed = False
    for event in events:
        item = event.get("item", {})
        if event.get("type") == "item.completed" and item.get("type") == "agent_message":
            messages.append(item.get("text", ""))
        if event.get("type") == "turn.completed":
            completed = True
        if event.get("type") == "turn.failed":
            errors.append("Native turn failed")
        if event.get("type") == "result":  # Claude stream-json final result
            completed = not event.get("is_error", False)
            if isinstance(event.get("result"), str):
                messages.append(event["result"])
    response = messages[-1].strip() if messages else ""
    if not completed or not response:
        errors.append("No completed user-facing response observed")
    candidates = [response] + re.findall(r"```(?:json)?\s*\n(.*?)\n```", response, re.S | re.I)
    internal_dump = False
    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except ValueError:
            continue
        if candidate == response and isinstance(data, (dict, list)):
            internal_dump = True
        elif isinstance(data, dict) and set(data).intersection(REPORT_FIELDS):
            internal_dump = True
    fields = "|".join(REPORT_FIELDS)
    if re.search(r"^\s*(?:[-*]\s*)?[*`\"']*(?:" + fields + r")[*`\"']*\s*:", response, re.M):
        internal_dump = True
    if internal_dump:
        errors.append("Internal report leaked into the normal user conversation")
    if require_question and "?" not in response:
        errors.append("No discovery question observed for the incomplete brief")
    return {"status": "passed" if not errors else "incomplete", "errors": errors,
            "internal_report_exposed": internal_dump, "asks_discovery_questions": "?" in response,
            "scope": ("Output format and presence of questions only; not a full advice-quality evaluation"
                      if require_question else "Output format only; approval semantics require manual review")}


def assess_codex(records):
    started, completed, reports = set(), set(), {}
    for record in records:
        payload = record.get("payload", {})
        item = payload.get("item", {})
        if item.get("type") == "SubAgentActivity":
            if item.get("kind") == "started":
                started.add(item.get("agent_thread_id"))
            elif item.get("kind") == "completed":
                completed.add(item.get("agent_thread_id"))
        if payload.get("type") == "agent_message" and payload.get("author", "").startswith("/root/"):
            for content in payload.get("content", []):
                text = content.get("text", "")
                if "Message Type: FINAL_ANSWER" in text and "Payload:\n" in text:
                    try:
                        report = json.loads(text.split("Payload:\n", 1)[1])
                    except (ValueError, IndexError):
                        continue
                    reports[payload["author"]] = report
    errors = []
    if len(started - {None}) != 1 or started != completed:
        errors.append("Exactly one started and completed native child was not observed")
    if len(reports) != 1:
        errors.append("Exactly one structured child report was not observed")
    else:
        report = next(iter(reports.values()))
        errors.extend(validate_report(report))
        if report.get("STATUS") != "completed":
            errors.append("Child report not completed")
        encoded = json.dumps(report)
        if "DAT_CONTEXT_1_0_0" not in encoded or "ZeroDivisionError" not in encoded:
            errors.append("Expected context marker/finding missing from specialist evidence")
    return {"status": "passed" if not errors else "incomplete", "native_children_started": len(started - {None}),
            "native_children_completed": len(completed - {None}), "child_reports": len(reports), "errors": errors,
            "native_named_profile_loaded": "NOT_VERIFIED_BY_ROLE_ENVELOPE_TEST"}
