"""Render canonical agents into documented native formats, without side effects.

Returned paths are relative to a project root or a user home directory. The
installer owns conflict detection and managed-block merging of instruction files.
"""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re


PLATFORMS = ("claude-code", "codex", "github-copilot", "chatgpt")
SCOPES = ("project", "global")
INSTRUCTION_FILES = frozenset({
    "CLAUDE.md", ".claude/CLAUDE.md", "AGENTS.md", ".codex/AGENTS.md",
    ".github/copilot-instructions.md", ".copilot/copilot-instructions.md",
})


def _read(root: Path, relative: str) -> str:
    """Read a contained source file, rejecting traversal and symlink escapes."""
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or "\\" in relative or ":" in relative:
        raise ValueError(f"Unsafe adapter source path: {relative}")
    source = root / relative
    if not source.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Adapter source escapes framework root: {relative}")
    return source.read_text(encoding="utf-8")


def _catalog(root: Path) -> list[dict]:
    catalog = json.loads(_read(root, "agents/catalog.json"))
    if not isinstance(catalog, dict):
        raise ValueError("Catalog must be an object")
    agents = catalog.get("agents")
    if not isinstance(agents, list) or not agents:
        raise ValueError("Catalog must contain a nonempty agents list")
    seen = set()
    for agent in agents:
        if not isinstance(agent, dict):
            raise ValueError("Each catalog entry must be an object")
        identifier = agent.get("id", "")
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", identifier):
            raise ValueError(f"Invalid agent ID: {identifier!r}")
        if identifier in seen:
            raise ValueError(f"Duplicate agent ID: {identifier}")
        seen.add(identifier)
        for key in ("name", "description", "definition"):
            if not isinstance(agent.get(key), str) or not agent[key].strip():
                raise ValueError(f"Agent {identifier} needs a nonempty {key}")
        if not isinstance(agent.get("read_only"), bool):
            raise ValueError(f"Agent {identifier} needs boolean read_only")
        definition = _read(root, agent["definition"])
        if not definition.strip():
            raise ValueError(f"Empty definition for {identifier}")
    if "team-leader" not in seen:
        raise ValueError("Catalog must contain team-leader")
    return agents


def _quote(value: str) -> str:
    # JSON basic strings are also valid YAML scalars and TOML basic strings.
    return json.dumps(value, ensure_ascii=False)


def _common(root: Path, platform: str, scope: str) -> str:
    base = _read(root, "adapters/common.md").strip()
    platform_text = _read(root, f"adapters/{platform}/runtime.md").strip()
    bundle = f".ai-team/framework/{platform}" if scope == "project" else f"~/.ai-team/framework/{platform}"
    return (
        f"{base}\n\n{platform_text}\n\nCanonical reference bundle: `{bundle}/`.\n"
        "Relative documentation links in the verbatim role below resolve from the "
        "bundle's agents/ directory; open its canonical role file for those links.\n"
    )


def _body(root: Path, agent: dict, common: str) -> str:
    return (
        f"{common}\nCanonical role ID: `{agent['id']}`. Native ID: `dat-{agent['id']}`.\n\n"
        + _read(root, agent["definition"]).strip() + "\n"
    )


def _bundle(root: Path, agents: list[dict], platform: str) -> dict[str, str]:
    files = {f".ai-team/framework/{platform}/agents/catalog.json": _read(root, "agents/catalog.json")}
    for agent in agents:
        files[f".ai-team/framework/{platform}/{agent['definition']}"] = _read(root, agent["definition"])
    for name in ("orchestration", "security", "context-management"):
        relative = f"docs/{name}.md"
        if (root / relative).is_file():
            files[f".ai-team/framework/{platform}/{relative}"] = _read(root, relative)
    return files


def _instructions(root: Path, agents: list[dict], common: str) -> str:
    leader = next(a for a in agents if a["id"] == "team-leader")
    roster = "\n".join(f"- `dat-{a['id']}`: {a['description']}" for a in agents if a != leader)
    return (
        "# Development Agent Team\n\n"
        "Act as the Team Leader in the main conversation for coordinated engineering work. "
        "Use native specialist delegation when available and useful; this instruction explicitly "
        "requests such delegation. Keep short or dependent tasks in the main conversation. "
        "If delegation is unavailable, perform explicitly labelled sequential role passes.\n\n"
        + _body(root, leader, common) + "\n## Available specialist profiles\n\n" + roster + "\n"
    )


def render(root: Path, platform: str, scope: str) -> dict[str, str]:
    """Return installable file text for a documented platform and installation scope.

    ChatGPT project output is a manual import bundle, not a native installation.
    No global filesystem installation mechanism is documented for ordinary ChatGPT.
    """
    root = Path(root)
    if platform not in PLATFORMS:
        raise ValueError(f"Unknown platform: {platform}")
    if scope not in SCOPES:
        raise ValueError(f"Unknown scope: {scope}")
    if platform == "chatgpt" and scope == "global":
        raise ValueError("ChatGPT has no verified global filesystem agent installation; use project scope to export a manual import bundle")
    agents = _catalog(root)
    common = _common(root, platform, scope)
    files = _bundle(root, agents, platform)
    instructions = _instructions(root, agents, common)
    if platform == "chatgpt":
        prefix = ".ai-team/chatgpt"
        files[f"{prefix}/project-instructions.md"] = instructions
        files[f"{prefix}/specialist-reference.md"] = "\n\n---\n\n".join(
            _body(root, agent, common) for agent in agents
        )
        protocols = [text for name, text in files.items() if name.startswith(
            ".ai-team/framework/chatgpt/docs/"
        )]
        if protocols:
            files[f"{prefix}/specialist-reference.md"] += (
                "\n\n# Bundled operating references\n\n" + "\n\n---\n\n".join(protocols)
            )
        files[f"{prefix}/SETUP.md"] = _read(root, "adapters/chatgpt/SETUP.md")
        return files
    if platform == "claude-code":
        directory = ".claude/agents"
        instruction_path = "CLAUDE.md" if scope == "project" else ".claude/CLAUDE.md"
        for agent in agents:
            front = f"---\nname: dat-{agent['id']}\ndescription: {_quote(agent['description'])}\nmodel: inherit\n"
            if agent["read_only"]:
                front += "tools: [Read, Grep, Glob]\n"
            files[f"{directory}/dat-{agent['id']}.md"] = front + "---\n\n" + _body(root, agent, common)
    elif platform == "codex":
        instruction_path = "AGENTS.md" if scope == "project" else ".codex/AGENTS.md"
        for agent in agents:
            text = (
                f"name = {_quote('dat-' + agent['id'])}\n"
                f"description = {_quote(agent['description'])}\n"
                f"developer_instructions = {_quote(_body(root, agent, common))}\n"
            )
            if agent["read_only"]:
                text += "\n[features]\nshell_tool = false\napps = false\nplugins = false\nrequest_permissions_tool = false\n"
            files[f".codex/agents/dat-{agent['id']}.toml"] = text
    else:
        directory = ".github/agents" if scope == "project" else ".copilot/agents"
        instruction_path = ".github/copilot-instructions.md" if scope == "project" else ".copilot/copilot-instructions.md"
        for agent in agents:
            front = f"---\nname: dat-{agent['id']}\ndescription: {_quote(agent['description'])}\n"
            if agent["read_only"]:
                front += 'tools: ["read", "search"]\n'
            # Profiles embed shared policy because CLI subagents do not inherit
            # repository custom instructions by default. No CLI-only key needed.
            body = _body(root, agent, common)
            if len(body) > 30000:
                raise ValueError(f"Copilot profile exceeds documented 30,000 character limit: {agent['id']}")
            files[f"{directory}/dat-{agent['id']}.agent.md"] = front + "---\n\n" + body
    files[instruction_path] = instructions
    return files
