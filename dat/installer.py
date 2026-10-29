"""Idempotent, ownership-aware platform installation."""
from __future__ import annotations

import json
from contextlib import nullcontext
from pathlib import Path

from . import __version__
from .storage import Conflict, digest, locked, read, safe_path, transaction

PLATFORMS = ("claude-code", "codex", "github-copilot", "chatgpt")
INSTRUCTIONS = ("AGENTS.md", "CLAUDE.md", "copilot-instructions.md", ".gitignore")


def markers(platform: str, filename: str) -> tuple[bytes, bytes]:
    if filename == ".gitignore":
        return f"# DAT:BEGIN:{platform}\n".encode(), f"# DAT:END:{platform}\n".encode()
    return f"<!-- DAT:BEGIN:{platform} -->\n".encode(), f"<!-- DAT:END:{platform} -->\n".encode()


def split_block(content: bytes, platform: str, filename: str):
    begin, end = markers(platform, filename)
    if content.count(begin) != content.count(end) or content.count(begin) > 1:
        raise Conflict(f"Malformed managed block: {filename}")
    if begin not in content:
        return content, None, b""
    start = content.index(begin)
    stop = content.index(end) + len(end)
    if stop <= start:
        raise Conflict(f"Malformed managed block: {filename}")
    return content[:start], content[start:stop], content[stop:]


def block(platform: str, filename: str, value: str) -> bytes:
    begin, end = markers(platform, filename)
    return begin + value.rstrip().encode("utf-8") + b"\n" + end


def state_path(platform: str, scope: str) -> str:
    return f".ai-team/.dat/{platform}-{scope}.json"


def load_state(target: Path, platform: str, scope: str):
    raw = read(target, state_path(platform, scope))
    if raw is None:
        return None
    state = json.loads(raw)
    if state.get("platform") != platform or state.get("scope") != scope or state.get("schema") != 1:
        raise Conflict("Installation manifest has an unsupported identity/schema.")
    for path in state["files"]:
        safe_path(target, path)
    return state


def ignored_files(rendered, share_agents, share_context):
    ignores = {"/.ai-team/.dat/", "/.ai-team/context.local.md"}
    if not share_agents:
        ignores.update("/" + path for path in rendered if path != ".gitignore")
    return "\n".join(sorted(ignores)) + "\n"


def context_shared(target: Path):
    return False  # Consumer memory is now always private, including older opt-ins.


def privacy_ignore(target: Path, share_context=False):
    """Persistent local memory safety, including after platform uninstallation.

    Kept with retained memory/recovery data. Never remove this block during
    adapter uninstall: journals can contain preexisting user configuration.
    """
    path = ".ai-team/.gitignore"
    current = read(target, path) or b""
    prefix, managed, suffix = split_block(current, "privacy", ".gitignore")
    # Prior sharing opt-ins are overridden; preserve unrelated custom lines.
    lines = managed.decode().splitlines()[1:-1] if managed else []
    lines = [line for line in lines if line not in (".dat/", "context.local.md", "context.md")]
    value = "\n".join([".dat/", "context.local.md", "context.md"] + lines) + "\n"
    separator = b"" if managed or not prefix else (b"\n" if prefix.endswith(b"\n") else b"\n\n")
    return path, prefix + separator + block("privacy", ".gitignore", value) + suffix


def central_privacy(target: Path, context_file: str, share_context=False):
    """Retain context privacy independently of adapter ownership/uninstallation."""
    path = "agents/.gitignore"
    current = read(target, path) or b""
    prefix, managed, suffix = split_block(current, "context", ".gitignore")
    lines = managed.decode().splitlines()[1:-1] if managed else []
    entry = "/" + Path(context_file).name
    lines = [line for line in lines if line not in (entry, "/contexts/")]
    lines.extend([entry, "/contexts/"])
    lines = list(dict.fromkeys(lines))
    value = "\n".join(lines) + "\n"
    content = prefix + suffix
    separator = b"" if not content or content.endswith(b"\n") else b"\n"
    return path, content + separator + block("context", ".gitignore", value)


def root_privacy(current):
    """Persistent exclusions, independent of adapter uninstall and legacy opt-ins."""
    from .privacy import PRIVATE_PATTERNS
    prefix, managed, suffix = split_block(current, "local-privacy", ".gitignore")
    content = prefix + suffix
    separator = b"" if not content or content.endswith(b"\n") else b"\n"
    value = "\n".join("/" + p for p in PRIVATE_PATTERNS) + "\n"
    return content + separator + block("local-privacy", ".gitignore", value)


def remove_entry(target, path, entry, platform):
    current = read(target, path)
    if current is None:
        return None
    if entry["kind"] == "owned":
        if digest(current) != entry["hash"]:
            raise Conflict(f"Customized managed file: {path}. Preserve/rename your changes and retry; no force overwrite is offered.")
        return None
    prefix, managed, suffix = split_block(current, platform, path)
    if managed is None or digest(managed) != entry["hash"]:
        raise Conflict(f"Customized/missing managed block: {path}")
    # Separator was introduced by us only when appending to an existing file.
    separator = bytes.fromhex(entry.get("separator", ""))
    if separator and prefix.endswith(separator):
        prefix = prefix[:-len(separator)]
    result = prefix + suffix
    return result if result or entry.get("preexisting") else None


def maintain(source: Path, target: Path, platform: str, scope="project", action="install",
             dry_run=False, share_agents=False, share_context=False, context_file=None):
    from .adapters import render
    if platform not in PLATFORMS or scope not in ("project", "global"):
        raise ValueError("Unknown platform or scope")
    if share_agents or share_context:
        raise ValueError("Consumer agents and contexts are local-only; sharing flags are no longer supported")
    target = target.absolute()
    if scope == "project" and action != "uninstall":
        from .privacy import require_untracked
        require_untracked(target)
    safe_path(target, ".ai-team/.dat/check")
    with nullcontext() if dry_run else locked(target):
        old = load_state(target, platform, scope)
        if action == "update" and old is None:
            raise Conflict("No managed installation found; run install first.")
        changes = {}
        if action == "uninstall":
            if old is None:
                return {"version": None, "changed": [], "action": action, "dry_run": dry_run}
            for path, entry in old["files"].items():
                changes[path] = remove_entry(target, path, entry, platform)
            if scope == "project":
                privacy_path, privacy_value = privacy_ignore(target, old.get("share_context", False))
                changes[privacy_path] = privacy_value
            changes[state_path(platform, scope)] = None
            changed = transaction(target, changes, dry_run)
            return {"version": old["version"], "action": action, "changed": changed, "dry_run": dry_run,
                    "memory": "Preserved shared/role contexts, onboarding metadata, legacy contexts and private recovery backups"}
        # Override legacy sharing opt-ins on repeat installs and upgrades.
        share_agents = share_context = False
        if scope == "project":
            from .memory import prepare
            context_file, memory_changes = prepare(target, context_file)
            changes.update(memory_changes)
            path, value = central_privacy(target, context_file, share_context)
            changes[path] = value
        elif context_file is not None:
            raise ValueError("Global installation cannot select a project context file")
        rendered = render(source, platform, scope, context_file=context_file)
        if scope == "project":
            rendered[".gitignore"] = ignored_files(rendered, share_agents, share_context)
            privacy_path, privacy_value = privacy_ignore(target, share_context)
            changes[privacy_path] = privacy_value
        entries = {}
        for path, text in rendered.items():
            safe_path(target, path)
            current = read(target, path)
            previous = old["files"].get(path) if old else None
            is_block = Path(path).name in INSTRUCTIONS
            if is_block:
                prefix, managed, suffix = split_block(current or b"", platform, path)
                if previous:
                    if managed is None or digest(managed) != previous["hash"]:
                        raise Conflict(f"Customized managed block: {path}")
                elif managed is not None:
                    raise Conflict(f"Unowned managed block already exists: {path}; recover its manifest first.")
                new_block = block(platform, path, text)
                separator = b"" if managed is not None or not prefix else (b"\n" if prefix.endswith(b"\n") else b"\n\n")
                changes[path] = prefix + separator + new_block + suffix
                entries[path] = {"kind": "block", "hash": digest(new_block),
                                 "preexisting": previous["preexisting"] if previous else current is not None,
                                 "separator": previous.get("separator", "") if previous else separator.hex()}
            else:
                if previous:
                    if digest(current) != previous["hash"]:
                        raise Conflict(f"Customized or missing managed file: {path}")
                elif current is not None:
                    raise Conflict(f"Existing unowned file: {path}; choose another name/target instead of overwriting.")
                value = text.encode("utf-8")
                changes[path] = value
                entries[path] = {"kind": "owned", "hash": digest(value)}
        if old:
            for path in old["files"].keys() - entries.keys():
                changes[path] = remove_entry(target, path, old["files"][path], platform)
        manifest = {"schema": 1, "version": __version__, "platform": platform, "scope": scope,
                    "share_agents": share_agents, "share_context": share_context, "files": entries}
        changes[state_path(platform, scope)] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
        if scope == "project":
            value = root_privacy(changes[".gitignore"])
            changes = {".gitignore": value, **{p: v for p, v in changes.items() if p != ".gitignore"}}
        changed = transaction(target, changes, dry_run)
        return {"action": action, "version": __version__, "previous_version": old["version"] if old else None,
                "platform": platform, "scope": scope, "changed": changed, "dry_run": dry_run,
                "context_file": context_file,
                "sharing": {"agents": share_agents, "context": share_context}}


def inspect(target: Path):
    results = []
    folder = safe_path(target, ".ai-team/.dat")
    if not folder.exists():
        return results
    manifests = [folder / f"{platform}-{scope}.json" for platform in PLATFORMS for scope in ("project", "global")]
    for path in sorted(p for p in manifests if p.exists()):
        state = json.loads(read(target, str(path.relative_to(target))))
        errors = []
        for name, entry in state["files"].items():
            current = read(target, name)
            if entry["kind"] == "block":
                _, current, _ = split_block(current or b"", state["platform"], name)
            if digest(current) != entry["hash"]:
                errors.append(name)
        results.append({"platform": state["platform"], "scope": state["scope"], "version": state["version"],
                        "modified_or_missing": errors})
    return results
