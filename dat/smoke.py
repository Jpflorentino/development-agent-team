"""Evidence parsing for opt-in smoke tests; never trusts a model's final claim."""
import json

from .policy import validate_report


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
