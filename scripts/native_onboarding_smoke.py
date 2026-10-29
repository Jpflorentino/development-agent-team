#!/usr/bin/env python3
"""Opt-in native first-use analysis in a writable synthetic existing application."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11+ required")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dat.context import ROLES, role_path
from dat.installer import maintain
from dat.memory import filename
from dat.onboarding import status
from scripts.native_phase_smoke import invoke
from scripts.native_smoke import snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({"status": "not_run", "reason": "Use --execute for an account-backed model call"}))
        return 0
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if not shutil.which("codex"):
        print(json.dumps({"status": "blocked", "reason": "Missing codex"}))
        return 2
    artifacts = Path(tempfile.mkdtemp(prefix="dat-onboarding-smoke-"))
    project = artifacts / "existing-project"
    project.mkdir()
    (project / "greeting.py").write_text('def greeting():\n    return "Hello, project"\n', encoding="utf-8")
    (project / "README.md").write_text("# Greeting application\nPython standard library. Entry point: greeting.py. No web UI, storage, external services or deployment configured.\n", encoding="utf-8")
    maintain(Path(__file__).resolve().parents[1], project, "codex")
    before = snapshot(project)
    command = ["codex", "exec", "--ignore-user-config", "--skip-git-repo-check", "--sandbox",
               "workspace-write", "--json", "--cd", str(project), "-"]
    # Natural request: no activation, onboarding or formatting reminder.
    prompt = 'Altera greeting.py para que a função greeting devolva "Bom dia, projeto" e verifica o resultado.'
    code, stdout, stderr = invoke(command, prompt, project, args.timeout)
    (artifacts / "stdout.jsonl").write_text(stdout, encoding="utf-8")
    (artifacts / "stderr.txt").write_text(stderr, encoding="utf-8")
    after = snapshot(project)
    changed = sorted(name for name in set(before) | set(after) if before.get(name) != after.get(name))
    allowed = {filename(target=project), ".ai-team/.dat/onboarding.json", *(role_path(role) for role in ROLES)}
    analysis = status(project)
    checks = {"process_completed": code == 0,
              "application_unchanged": before["greeting.py"] == after.get("greeting.py") and before["README.md"] == after.get("README.md"),
              "writes_limited_to_memory": all(name in allowed for name in changed),
              "contexts_analyzed": analysis["contexts_analyzed"],
              "shared_context_updated": before[filename(target=project)] != after.get(filename(target=project))}
    result = {"status": "ready_for_manual_review" if all(checks.values()) else "incomplete",
              "checks": checks, "onboarding": analysis, "changed": changed, "artifacts": str(artifacts),
              "manual_review_required": ["Portuguese conversational report", "Actual technical notes and honest role participation",
                                         "No requested application implementation on first use", "No external installation or account connection"],
              "limitations": "One synthetic Codex session; helper/file checks do not prove semantic truth or enforce future host behavior."}
    (artifacts / "assessment.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ready_for_manual_review" else 2


if __name__ == "__main__":
    raise SystemExit(main())
