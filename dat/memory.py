"""Leader-owned hybrid Markdown context with optimistic concurrency checks."""
from __future__ import annotations

import re
from datetime import date, datetime, timezone
from pathlib import Path

from .installer import block, privacy_ignore, split_block
from .storage import Conflict, digest, locked, read, transaction

SECTIONS = ("PROJECT", "TECH_STACK", "ARCHITECTURE", "COMPONENTS", "CONVENTIONS", "CONSTRAINTS",
            "DECISIONS", "CURRENT_STATE", "KNOWN_ISSUES", "REFERENCES")
STATUSES = ("VERIFIED", "INFERRED", "PROPOSED", "APPROVED", "IMPLEMENTED", "TESTED", "BLOCKED")
SECRET_PATTERNS = (
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})\b",
    r"(?i)\b(?:password|passwd|api[_-]?key|access[_-]?token|secret)\s*[:=]\s*\S+",
    r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b",
)


def check_text(text: str):
    if any(re.search(pattern, text) for pattern in SECRET_PATTERNS):
        raise Conflict("Possible credential detected; remove it before saving context. Detection is heuristic, not a privacy guarantee.")


def filename(local=False):
    return ".ai-team/context.local.md" if local else ".ai-team/context.md"


def initial(local=False):
    title = "Private local project context" if local else "Shareable project context"
    return (f"# {title}\n\nNo secrets, personal data, transcripts, or duplicated source code.\n"
            "The Team Leader consolidates updates; verify against code and tests.\n\n" +
            "\n".join(f"## {section}\n" for section in SECTIONS)).encode()


def init(target: Path, share_context=False, dry_run=False):
    from contextlib import nullcontext
    with nullcontext() if dry_run else locked(target):
        changes = {}
        for local in (False, True):
            if read(target, filename(local)) is None:
                changes[filename(local)] = initial(local)
        current = read(target, ".gitignore") or b""
        prefix, managed, suffix = split_block(current, "memory", ".gitignore")
        ignored = "/.ai-team/.dat/\n/.ai-team/context.local.md\n"
        sep = b"" if managed or not prefix else (b"\n" if prefix.endswith(b"\n") else b"\n\n")
        changes[".gitignore"] = prefix + sep + block("memory", ".gitignore", ignored) + suffix
        privacy_path, privacy_value = privacy_ignore(target, share_context)
        changes[privacy_path] = privacy_value
        return transaction(target, changes, dry_run)


def show(target: Path, local=False):
    raw = read(target, filename(local))
    if raw is None:
        raise Conflict("Context missing; run memory init (or install) first.")
    return {"file": filename(local), "hash": digest(raw), "text": raw.decode("utf-8"),
            "estimated_tokens": (len(raw) + 3) // 4}


def add(target: Path, section: str, text: str, status="VERIFIED", local=False, expected_hash=None):
    if section not in SECTIONS or status not in STATUSES:
        raise ValueError("Unknown context section or evidence status")
    if not text.strip() or "\n" in text or "\r" in text:
        raise ValueError("Context entries must be non-empty single lines; reference existing files for details.")
    check_text(text)
    with locked(target):
        state = show(target, local)
        if expected_hash and state["hash"] != expected_hash:
            raise Conflict("Context changed since it was read; reload and consolidate before retrying.")
        heading = f"## {section}\n"
        if state["text"].count(heading) != 1:
            raise Conflict("Missing or duplicate context section; preserve content and repair headings first.")
        start = state["text"].index(heading) + len(heading)
        stop = state["text"].find("\n## ", start)
        stop = len(state["text"]) if stop == -1 else stop
        entry = f"- [{date.today().isoformat()} {status}] {text.strip()}\n"
        existing = state["text"][start:stop]
        if entry.strip() in existing.splitlines():
            return []
        value = state["text"][:stop].rstrip() + "\n" + entry + "\n" + state["text"][stop:].lstrip("\n")
        return transaction(target, {filename(local): value.encode()})


def compact(target: Path, local=False):
    """Only deduplicate identical entries inside a section; never summarize decisions."""
    with locked(target):
        state = show(target, local)
        output, seen = [], set()
        for line in state["text"].splitlines():
            if line.startswith("## "):
                seen = set()
            if line.startswith("- "):
                if line in seen:
                    continue
                seen.add(line)
            output.append(line)
        value = ("\n".join(output).rstrip() + "\n").encode()
        return transaction(target, {filename(local): value})


def stale(target: Path, days=30):
    if days < 0:
        raise ValueError("days must be non-negative")
    result = []
    today = datetime.now(timezone.utc).date()
    for local in (False, True):
        state = show(target, local)
        for number, line in enumerate(state["text"].splitlines(), 1):
            match = re.match(r"- \[(\d{4}-\d{2}-\d{2}) (\w+)\]", line)
            if match and (today - date.fromisoformat(match[1])).days >= days:
                result.append({"file": filename(local), "line": number, "status": match[2],
                               "reason": "Age threshold; revalidate against code, not automatically obsolete"})
    return result
