#!/usr/bin/env python3
"""Opt-in writable synthetic test of automatic central-memory maintenance."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11+ required")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dat.installer import maintain
from dat.memory import add, filename
from dat.context import ROLES, ROLE_SECTIONS, role_path
from dat.onboarding import record
from scripts.native_phase_smoke import invoke
from scripts.native_smoke import snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({"status": "not_run", "reason": "Use --execute for an account-backed model call"}))
        return 0
    if not shutil.which("codex"):
        print(json.dumps({"status": "blocked", "reason": "Missing codex"}))
        return 2
    artifacts = Path(tempfile.mkdtemp(prefix="dat-memory-smoke-"))
    project = artifacts / "synthetic-project"
    project.mkdir()
    source = Path(__file__).resolve().parents[1]
    maintain(source, project, "codex")
    (project / "greeting.py").write_text('def greeting():\n    return "Hello, project"\n', encoding="utf-8")
    add(project, "PROJECT", "CENTRAL_BRAIN_MARKER: synthetic greeting application.")
    add(project, "TECH_STACK", "Python standard library; application source: greeting.py.")
    add(project, "CURRENT_STATE", "The greeting currently returns Hello, project; update this fact when it changes.")
    add(project, "CONSTRAINTS", "Only greeting.py and the shared/role context files may be edited; no network, dependencies or publication.")
    # This fixture tests later memory maintenance, not first-use onboarding.
    for role in ROLES:
        if role in ("team-leader", "backend-developer", "qa-engineer"):
            # Real baseline notes for this synthetic fixture, not invented model participation.
            notes = (f"# {role} technical context\n\n## STATUS\ncompleted\n\n"
                     "Prepared fixture baseline; no independent agent execution claimed.\n\n" +
                     "\n".join(f"## {heading}\nPython standard-library module greeting.py; greeting() takes no arguments and returns Hello, project. "
                               "No persistence, HTTP, external services or tests configured. Keep the existing signature.\n"
                               for heading in ROLE_SECTIONS[role]))
            (project / role_path(role)).write_text(notes, encoding="utf-8")
            record(project, role, "completed", "Synthetic baseline prepared from greeting.py by the harness", ["greeting.py"])
        else:
            record(project, role, "not_applicable", "No relevant UI, persistence, infrastructure or review scope in this synthetic established baseline", ["greeting.py"])
    brain = filename(target=project)
    import re
    brain_path = project / brain
    seeded = brain_path.read_text(encoding="utf-8").replace(
        "Bootstrap required: fill unknown sections from inspected evidence, never invented facts.",
        "Established synthetic baseline prepared by the harness from greeting.py; onboarding complete. No model participation claimed.")
    brain_path.write_text(re.sub(r"^Last updated \(UTC\): .*", "Last updated (UTC): 2000-01-01T00:00:00+00:00",
                                seeded, flags=re.M), encoding="utf-8")
    before = snapshot(project)
    command = ["codex", "exec", "--ignore-user-config", "--skip-git-repo-check", "--sandbox",
               "workspace-write", "--json", "--cd", str(project), "-"]
    # No activation, formatting or memory-update reminder in this user prompt.
    prompt = 'Altera a função greeting em greeting.py para devolver exatamente "Bom dia, projeto". Verifica o resultado.'
    code, stdout, stderr = invoke(command, prompt, project, args.timeout)
    (artifacts / "stdout.jsonl").write_text(stdout, encoding="utf-8")
    (artifacts / "stderr.txt").write_text(stderr, encoding="utf-8")
    after = snapshot(project)
    changed = sorted(name for name in set(before) | set(after) if before.get(name) != after.get(name))
    text = (project / brain).read_text(encoding="utf-8")
    content = (project / "greeting.py").read_text(encoding="utf-8")
    # Inspect the synthetic source without executing arbitrary model-written code.
    import ast
    try:
        tree = ast.parse(content)
    except SyntaxError:
        tree = ast.Module(body=[], type_ignores=[])
    returns = [n.value.value for n in ast.walk(tree) if isinstance(n, ast.Return)
               and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)]
    checks = {
        "process_completed": code == 0,
        "expected_greeting": returns == ["Bom dia, projeto"],
        "central_brain_updated": before[brain] != after.get(brain),
        "prior_knowledge_preserved": "CENTRAL_BRAIN_MARKER" in text,
        "new_behavior_recorded": "Bom dia, projeto" in text,
        "affected_technical_context_updated": before[role_path("backend-developer")] != after.get(role_path("backend-developer")) and
            "Bom dia, projeto" in (project / role_path("backend-developer")).read_text(encoding="utf-8"),
        "old_timestamp_refreshed": "2000-01-01T00:00:00+00:00" not in text and "Last updated (UTC):" in text,
        "edits_limited_to_task_and_brain": all(name in {"greeting.py", brain} or name.startswith("agents/contexts/") or
            (name.startswith("__pycache__/") and name.endswith(".pyc")) for name in changed),
        "no_new_legacy_context": not (project / ".ai-team/context.md").exists(),
    }
    result = {"status": "passed" if all(checks.values()) else "incomplete", "checks": checks,
              "changed": changed, "artifacts": str(artifacts),
              "limitations": "One synthetic native session; manually inspect actual reads, checks, timestamp and memory content. Not a background watcher or a guarantee for all hosts."}
    (artifacts / "assessment.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
