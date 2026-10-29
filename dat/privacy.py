"""Consumer-installation publication preflight; never edits Git's index/history."""
import fnmatch
from pathlib import Path
import shutil
import subprocess

from .storage import Conflict

PRIVATE_PATTERNS = (
    "agents/*-context.md", "agents/contexts/", ".ai-team/",
    ".codex/agents/", ".claude/agents/", ".github/agents/", ".copilot/agents/",
    "AGENTS.md", "CLAUDE.md", ".codex/AGENTS.md", ".claude/CLAUDE.md",
    ".github/copilot-instructions.md", ".copilot/copilot-instructions.md",
)


def protected(name):
    name = name.replace("\\", "/")
    return any(name.startswith(p) if p.endswith("/") else fnmatch.fnmatchcase(name, p)
               for p in PRIVATE_PATTERNS)


def inspect_git(target: Path):
    if not target.is_dir() or not shutil.which("git"):
        return {"git_available": bool(shutil.which("git")), "repository": False, "tracked_private_files": []}
    try:
        probe = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=target,
                               capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Conflict("Cannot inspect Git state; publication privacy is unverified") from error
    if probe.returncode:
        if any((parent / ".git").exists() for parent in (target, *target.parents)):
            raise Conflict("Git metadata exists but repository state cannot be inspected; publication privacy is unverified")
        return {"git_available": True, "repository": False, "tracked_private_files": []}
    try:
        proc = subprocess.run(["git", "ls-files", "-z", "--", "."], cwd=target,
                              capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Conflict("Cannot inspect tracked files; publication privacy is unverified") from error
    if proc.returncode:
        raise Conflict("Cannot inspect tracked files; publication privacy has not been established")
    names = proc.stdout.decode("utf-8").split("\0")
    return {"git_available": True, "repository": True,
            "tracked_private_files": sorted(n for n in names if n and protected(n))}


def require_untracked(target: Path):
    result = inspect_git(target)
    if result["tracked_private_files"]:
        raise Conflict("Agent/context files are already tracked: " + ", ".join(result["tracked_private_files"]) +
                       ". Ignore rules cannot unpublish them. Review untracking and any existing remote copies before installing; no Git index/history is changed automatically.")
    return result
