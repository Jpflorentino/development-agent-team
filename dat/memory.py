"""Leader-owned central project knowledge with optimistic concurrency checks."""
from __future__ import annotations

import re
from datetime import date, datetime, timezone
from pathlib import Path

from .installer import block, privacy_ignore, split_block
from .context import LEGACY_PRIVATE, LEGACY_SHARED, POINTER, resolve
from .storage import Conflict, digest, locked, read, transaction

SECTIONS = ("PROJECT", "TECH_STACK", "ARCHITECTURE", "COMPONENTS", "CONVENTIONS", "CONSTRAINTS",
            "REQUIREMENTS", "WORKFLOWS", "DATA_MODEL", "INTEGRATIONS", "SECURITY_PRIVACY",
            "DEPLOYMENT_COSTS", "DECISIONS", "CURRENT_STATE", "KNOWN_ISSUES", "RECOVERY", "REFERENCES")
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


def filename(local=False, target=None):
    # The no-target form remains a legacy path helper for existing integrations.
    return LEGACY_PRIVATE if local else resolve(Path(target)) if target is not None else LEGACY_SHARED


def initial(local=False, project=None):
    title = "Private legacy project context" if local else f"{project or 'Project'} — agent context"
    return (f"# {title}\n\nNo secrets, personal data, transcripts, or duplicated source code.\n"
            "The Team Leader maintains shared facts here. Read this and your own agents/contexts/<role>-context.md first; inspect relevant source to verify facts.\n"
            "Bootstrap required: fill unknown sections from inspected evidence, never invented facts.\n\n" +
            "\n".join(f"## {section}\n" for section in SECTIONS)).encode()


def prepare(target: Path, context_file=None):
    """Plan memory creation/migration inside the caller's transaction and lock."""
    path = resolve(target, context_file)
    changes = {POINTER: (path + "\n").encode()}
    if read(target, path) is None:
        legacy = read(target, LEGACY_SHARED)
        if legacy is not None:
            check_text(legacy.decode("utf-8"))
        value = legacy if legacy is not None else initial(project=target.name)
        if legacy is not None:
            text = value.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
            text = text.rstrip("\n") + "\n"
            value = text.encode("utf-8")
            missing = [section for section in SECTIONS if f"## {section}\n" not in text]
            if missing:
                value = value.rstrip() + b"\n\n" + "\n".join(f"## {section}\n" for section in missing).encode()
        changes[path] = value
    from .onboarding import prepare as prepare_roles
    changes.update(prepare_roles(target, path))
    return path, changes


def init(target: Path, share_context=False, dry_run=False, context_file=None):
    from contextlib import nullcontext
    from .installer import central_privacy
    if share_context:
        raise ValueError("Consumer agent contexts are local-only; --share-context is no longer supported")
    from .privacy import require_untracked
    require_untracked(target)
    with nullcontext() if dry_run else locked(target):
        path, changes = prepare(target, context_file)
        current = read(target, ".gitignore") or b""
        prefix, managed, suffix = split_block(current, "memory", ".gitignore")
        ignored = "/.ai-team/.dat/\n/.ai-team/context.local.md\n"
        sep = b"" if managed or not prefix else (b"\n" if prefix.endswith(b"\n") else b"\n\n")
        changes[".gitignore"] = prefix + sep + block("memory", ".gitignore", ignored) + suffix
        privacy_path, privacy_value = privacy_ignore(target, share_context)
        changes[privacy_path] = privacy_value
        privacy_path, privacy_value = central_privacy(target, path, share_context)
        changes[privacy_path] = privacy_value
        from .installer import root_privacy
        value = root_privacy(changes[".gitignore"])
        changes = {".gitignore": value, **{p: v for p, v in changes.items() if p != ".gitignore"}}
        return transaction(target, changes, dry_run)


def show(target: Path, local=False):
    path = filename(local, target)
    raw = read(target, path)
    if raw is None:
        raise Conflict("Context missing; run memory init (or install) first. --local accesses retained legacy private context only.")
    text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return {"file": path, "hash": digest(raw), "text": text.rstrip("\n") + "\n",
            "estimated_tokens": (len(raw) + 3) // 4}


def add(target: Path, section: str, text: str, status="VERIFIED", local=False, expected_hash=None):
    if section not in SECTIONS or status not in STATUSES:
        raise ValueError("Unknown context section or evidence status")
    if not text.strip() or "\n" in text or "\r" in text:
        raise ValueError("Context entries must be non-empty single lines; reference existing files for details.")
    check_text(text)
    with locked(target):
        state = show(target, local)
        if expected_hash is not None and state["hash"] != expected_hash:
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
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        value = re.sub(r"^Last updated \(UTC\): .*\n", "", value, flags=re.M)
        title, _, rest = value.partition("\n")
        value = title + f"\n\nLast updated (UTC): {stamp}\n\n" + rest.lstrip("\n")
        return transaction(target, {filename(local, target): value.encode()})


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
        return transaction(target, {filename(local, target): value})


def stale(target: Path, days=30):
    if days < 0:
        raise ValueError("days must be non-negative")
    result = []
    today = datetime.now(timezone.utc).date()
    for local in (False, True):
        if local and read(target, LEGACY_PRIVATE) is None:
            continue
        state = show(target, local)
        for number, line in enumerate(state["text"].splitlines(), 1):
            match = re.match(r"- \[(\d{4}-\d{2}-\d{2}) (\w+)\]", line)
            if match and (today - date.fromisoformat(match[1])).days >= days:
                result.append({"file": filename(local, target), "line": number, "status": match[2],
                               "reason": "Age threshold; revalidate against code, not automatically obsolete"})
    return result
