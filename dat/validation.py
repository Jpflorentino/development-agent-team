"""Offline validation and local environment diagnostics; no model calls."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

from . import __version__
from .adapters import _catalog, render
from .installer import PLATFORMS, inspect
from .storage import pending, safe_path

IDS = {"team-leader", "software-architect", "ui-ux-designer", "frontend-developer", "backend-developer",
       "database-engineer", "qa-engineer", "security-engineer", "devops-engineer", "code-review-engineer"}
HEADINGS = ("Identity", "Description", "Mission", "Responsibilities", "Competencies", "Authority limits",
            "Activation conditions", "Do not activate", "Dependencies", "Required tools", "Permissions",
            "Input format", "Output format", "Communication rules", "Quality criteria", "Completion criteria",
            "Error handling", "Context updates")


def validate(root: Path):
    errors, checks = [], []
    try:
        agents = _catalog(root)
        if {a["id"] for a in agents} != IDS or len(agents) != 10:
            errors.append("Catalog must contain exactly the ten required agents")
        catalog = json.loads((root / "agents/catalog.json").read_text(encoding="utf-8"))
        if catalog["version"] != __version__:
            errors.append("Catalog/package version mismatch")
        for agent in agents:
            text = (root / agent["definition"]).read_text(encoding="utf-8")
            for heading in HEADINGS:
                if not re.search(r"^## " + re.escape(heading) + r"\s*$", text, re.M):
                    errors.append(f"{agent['id']}: missing {heading}")
            if not set(agent["dependencies"]).issubset(IDS):
                errors.append(f"{agent['id']}: invalid dependency")
            if agent["id"] in ("security-engineer", "code-review-engineer") and agent["read_only"] is not True:
                errors.append(f"{agent['id']}: mandatory read_only safety policy disabled")
        checks.append("canonical_roles_and_metadata")
        for platform in PLATFORMS:
            for scope in ("project", "global"):
                if platform == "chatgpt" and scope == "global":
                    continue
                files = render(root, platform, scope)
                for name, text in files.items():
                    safe_path(Path("/validation-root"), name)
                    if not text.strip():
                        errors.append(f"Empty rendered file: {name}")
                    if name.endswith(".toml"):
                        parsed = tomllib.loads(text)
                        if not all(parsed.get(key) for key in ("name", "description", "developer_instructions")):
                            errors.append(f"Incomplete native TOML: {name}")
                        if any(f"dat-{role}.toml" in name for role in ("security-engineer", "code-review-engineer")):
                            if any(parsed.get("features", {}).get(key) is not False for key in
                                   ("shell_tool", "apps", "plugins", "request_permissions_tool")):
                                errors.append(f"Missing supported reviewer capability restrictions: {name}")
                    if any(f"dat-{role}." in name for role in ("security-engineer", "code-review-engineer")):
                        if platform == "claude-code" and "tools: [Read, Grep, Glob]" not in text:
                            errors.append(f"Missing Claude reviewer tool allowlist: {name}")
                        if platform == "github-copilot" and 'tools: ["read", "search"]' not in text:
                            errors.append(f"Missing Copilot reviewer tool allowlist: {name}")
                if platform != "chatgpt":
                    profiles = [p for p in files if "/agents/dat-" in p]
                    if len(profiles) != 10:
                        errors.append(f"{platform}/{scope}: expected ten native profiles")
                checks.append(f"render:{platform}:{scope}")
        for name in ("README.md", "LICENSE", "docs/architecture.md", "docs/orchestration.md", "docs/agents.md",
                     "docs/security.md", "docs/compatibility.md", "docs/installation.md", "docs/context-management.md",
                     "docs/contributing.md", "docs/platform-sources.md", "docs/pt-PT/README.md",
                     "templates/project-context.md", "templates/project-context.local.md"):
            if not (root / name).is_file():
                errors.append(f"Missing required document: {name}")
        # Local Markdown file references, not web links or headings.
        for path in root.rglob("*.md"):
            if ".git" in path.parts or ".ai-team" in path.parts:
                continue
            for ref in re.findall(r"\]\(([^)\s]+)\)", path.read_text(encoding="utf-8")):
                if "://" in ref or ref.startswith("#"):
                    continue
                ref = ref.split("#", 1)[0]
                if ref and not (path.parent / ref).exists():
                    errors.append(f"Broken local reference in {path.relative_to(root)}: {ref}")
        checks.append("documents_and_references")
    except (ValueError, KeyError, OSError, TypeError) as error:
        errors.append(f"{type(error).__name__}: {error}")
    return {"kind": "structural_validation", "version": __version__, "checks": checks, "errors": errors,
            "native_execution": "NOT_TESTED_BY_THIS_COMMAND"}


def doctor(source: Path, target: Path):
    runtimes, warnings, errors = {}, [], []
    for binary in ("codex", "claude", "copilot", "git"):
        executable = shutil.which(binary)
        if executable:
            try:
                proc = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=10)
                runtimes[binary] = {"available": True, "exit_code": proc.returncode,
                                    "version": proc.stdout.strip()[:250]}
            except (OSError, subprocess.TimeoutExpired) as error:
                runtimes[binary] = {"available": True, "version_error": type(error).__name__}
        else:
            runtimes[binary] = {"available": False}
            warnings.append(f"Optional runtime missing: {binary}")
    installations = []
    try:
        installations = inspect(target)
        if any(item["modified_or_missing"] for item in installations):
            errors.append("Managed files changed or missing; inspect modified_or_missing")
        if safe_path(target, ".ai-team/.dat/lock").exists():
            warnings.append("Maintenance/memory lock present; inspect owner before recover --unlock")
        if pending(target):
            errors.append("Interrupted transaction requires recover")
        config = safe_path(target, ".codex/config.toml")
        if config.is_file():
            tomllib.loads(config.read_text(encoding="utf-8"))
        for path in safe_path(target, ".codex/agents").glob("dat-*.toml"):
            raw = safe_path(target, path.relative_to(target).as_posix()).read_text(encoding="utf-8")
            tomllib.loads(raw)
    except (ValueError, KeyError, OSError, TypeError) as error:
        errors.append(f"Installation/config inspection: {type(error).__name__}: {error}")
    parent = target
    while not parent.exists() and parent != parent.parent:
        parent = parent.parent
    writable = os.access(parent, os.W_OK)
    if not writable:
        errors.append("Target/nearest existing parent is not writable")
    framework = validate(source)
    errors.extend(framework["errors"])
    return {"kind": "local_diagnostic", "python": sys.version.split()[0], "target": str(target),
            "target_writable": writable, "runtimes": runtimes, "installations": installations,
            "warnings": warnings, "errors": errors, "adapters": framework["checks"],
            "authentication": "NOT_CHECKED; version detection does not prove authentication",
            "native_execution": "NOT_TESTED_BY_THIS_COMMAND"}
