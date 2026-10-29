"""Evidence-record helpers for initial analysis, not an agent execution service."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .context import ROLES, ROLE_SECTIONS, role_path
from .storage import Conflict, locked, read, safe_path, transaction

STATE = ".ai-team/.dat/onboarding.json"
STATUSES = ("pending", "completed", "not_applicable", "blocked")


def initial_role(role, project, common):
    sections = ("STATUS", "SCOPE", *ROLE_SECTIONS[role], "RISKS", "REFERENCES")
    return (f"# {project} — {role} technical context\n\nCommon facts and accepted decisions: `{common}`.\n"
            "Private project memory. No credentials, personal data, copied code or transcripts.\n"
            "Only this role's assigned writer edits this file; the leader saves read-only reviewers' proposals.\n\n"
            + "\n".join(f"## {s}\n" + ("BOOTSTRAP_PENDING\n" if s == "STATUS" else "") for s in sections)).encode()


def prepare(target, common):
    changes = {}
    for role in ROLES:
        path = role_path(role)
        if read(target, path) is None:
            changes[path] = initial_role(role, target.name, common)
    if read(target, STATE) is None:
        state = {"schema": 1, "phase": "pending", "roles": {
            role: {"status": "pending", "summary": "", "sources": []} for role in ROLES},
            "integration_review": {}}
        changes[STATE] = (json.dumps(state, indent=2) + "\n").encode()
    return changes


def load(target):
    raw = read(target, STATE)
    if raw is None:
        raise Conflict("Onboarding record missing; install/update or initialize project memory first")
    state = json.loads(raw)
    if not isinstance(state, dict) or state.get("schema") != 1 or not isinstance(state.get("roles"), dict) or set(state["roles"]) != set(ROLES):
        raise Conflict("Unsupported or incomplete onboarding record; preserve it and reconcile before continuing")
    return state


def _has_notes(raw, role):
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for heading in ROLE_SECTIONS[role]:
        match = re.search(r"^## " + re.escape(heading) + r"[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        if match and any(line.strip() and not line.lstrip().startswith("<!--") and
                         line.strip().upper() not in ("TODO", "UNKNOWN", "BOOTSTRAP_PENDING")
                         for line in match[1].splitlines()):
            return True
    return False


def status(target):
    state = load(target)
    errors = []
    for role, value in state["roles"].items():
        if not isinstance(value, dict) or value.get("status") not in STATUSES:
            errors.append(f"{role}: invalid analysis status")
            continue
        raw = read(target, role_path(role))
        if raw is None:
            errors.append(f"{role}: context missing")
        if value["status"] in ("completed", "not_applicable"):
            if not isinstance(value.get("summary"), str) or not value["summary"].strip():
                errors.append(f"{role}: missing summary/reason")
            if raw is not None and b"BOOTSTRAP_PENDING" in raw:
                errors.append(f"{role}: context is still a template")
            if value["status"] == "completed" and raw is not None and not _has_notes(raw, role):
                errors.append(f"{role}: technical context has no domain notes")
            sources = value.get("sources")
            if not isinstance(sources, list) or any(not isinstance(s, str) for s in sources):
                errors.append(f"{role}: malformed source evidence")
            else:
                primary = False
                for name in sources:
                    try:
                        primary = _source(target, name, allow_context=True) or primary
                    except (Conflict, ValueError):
                        errors.append(f"{role}: missing or unsafe source evidence")
                if value["status"] == "completed" and not primary:
                    errors.append(f"{role}: completed analysis needs application/documentation source evidence")
    ready = not errors and all(v.get("status") in ("completed", "not_applicable") for v in state["roles"].values() if isinstance(v, dict))
    phase = "ready" if ready else "blocked" if errors or any(isinstance(v, dict) and v.get("status") == "blocked" for v in state["roles"].values()) else "pending"
    return {"phase": phase, "contexts_analyzed": ready, "roles": state["roles"],
            "integration_review": state.get("integration_review", {}), "errors": errors,
            "authorization": "Advisory evidence record; not user approval or a pre-tool execution gate"}


def _source(target, name, allow_context=False):
    from .privacy import protected
    context = name in {role_path(role) for role in ROLES}
    if (protected(name) and not (context and allow_context)) or Path(name).name.startswith(".env") or Path(name).suffix in (".pem", ".key") or not safe_path(target, name).is_file():
        raise Conflict("Analysis evidence must reference existing non-secret application/documentation files")
    # A role may reference its written notes as an additional artifact, but those
    # notes never establish inspected application evidence on their own.
    return not context


def record(target, role, analysis_status, summary, sources=()):
    role_path(role)
    if analysis_status not in STATUSES[1:] or not isinstance(summary, str) or not summary.strip() or "\n" in summary or "\r" in summary:
        raise ValueError("Provide a completed/not_applicable/blocked analysis and a meaningful summary")
    from .memory import check_text
    check_text(summary)
    sources = list(sources)
    primary = [_source(target, name, allow_context=True) for name in sources]
    if analysis_status == "completed" and not any(primary):
        raise Conflict("Completed analysis requires inspected source references")
    with locked(target):
        state = load(target)
        raw = read(target, role_path(role))
        if raw is None:
            raise Conflict("Role context missing")
        changes = {}
        if analysis_status == "not_applicable":
            changes[role_path(role)] = (f"# {role} technical context\n\nLast updated (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n\n## STATUS\nnot_applicable\n\n## SCOPE\n{summary}\n\n## REFERENCES\n" + "\n".join(sources) + "\n").encode()
        elif analysis_status == "completed" and b"BOOTSTRAP_PENDING" in raw:
            raise Conflict("Write the actual technical context before recording completed analysis")
        if analysis_status == "completed" and not _has_notes(raw, role):
            raise Conflict("Technical context needs actual notes under its domain headings")
        check_text(raw.decode("utf-8"))
        state["roles"][role] = {"status": analysis_status, "summary": summary, "sources": sources,
                                "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        state["phase"] = "ready" if all(v["status"] in ("completed", "not_applicable") for v in state["roles"].values()) else "pending"
        changes[STATE] = (json.dumps(state, indent=2) + "\n").encode()
        return transaction(target, changes)
