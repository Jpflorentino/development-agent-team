#!/usr/bin/env python3
"""Opt-in read-only Codex review of an existing synthetic implementation or empty project."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11+ required")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dat.context import ROLES, ROLE_SECTIONS, role_path
from dat.installer import maintain
from dat.memory import add, filename
from dat.onboarding import record
from scripts.native_phase_smoke import invoke
from scripts.native_smoke import snapshot

SOURCE = '''def subtotal(items):
    total = 0
    for item in items:
        if item["price"] > 0:
            total = total + item["price"]
    return total


def reported_total(items):
    total = 0
    for item in items:
        if item["price"] > 0:
            total += item["price"]
    return total


def unique_ids(rows):
    result = []
    for row in rows:
        if row["id"] not in result:
            result.append(row["id"])
    return result
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--scenario", choices=("existing", "empty"), default="existing")
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({"status": "not_run", "reason": "Use --execute for an account-backed synthetic read-only review"}))
        return 0
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if not shutil.which("codex"):
        print(json.dumps({"status": "blocked", "reason": "Missing codex"}))
        return 2
    artifacts = Path(tempfile.mkdtemp(prefix="dat-optimization-smoke-"))
    project = artifacts / "project"
    project.mkdir()
    root = Path(__file__).resolve().parents[1]
    if args.scenario == "existing":
        (project / "totals.py").write_text(SOURCE, encoding="utf-8")
        (project / "README.md").write_text("# Existing synthetic implementation\nPython standard library. Prices and IDs are integers; preserve positive-only totals and first-occurrence ID ordering. No external services or public API changes authorized. No benchmark or production workload exists.\n", encoding="utf-8")
    maintain(root, project, "codex")
    if args.scenario == "existing":
        for role in ROLES:
            if role in ("team-leader", "backend-developer", "qa-engineer", "code-optimization-engineer"):
                notes = "## STATUS\ncompleted\n\n" + "\n".join(
                    f"## {heading}\nHarness-inspected baseline: totals.py implements integer positive-price totals and ordered unique integer IDs. No benchmark evidence or changes approved; no previous model participation claimed.\n"
                    for heading in ROLE_SECTIONS[role])
                (project / role_path(role)).write_text(notes, encoding="utf-8")
                record(project, role, "completed", "Harness prepared existing implementation baseline", ["totals.py", "README.md"])
            else:
                record(project, role, "not_applicable", "No relevant UI, storage, operations or security boundary in this bounded synthetic baseline", ["totals.py", "README.md"])
        add(project, "PROJECT", "Existing Python totals and unique-ID implementation in totals.py; scope is review only.")
        add(project, "CONSTRAINTS", "Preserve positive-only integer totals and first-occurrence order of integer IDs. No application changes, dependency installation or measured speedup claims without evidence.")
        add(project, "CURRENT_STATE", "Harness-inspected baseline complete. No benchmarks exist; current request seeks a cleanup/optimization review, not implementation.")
        brain = project / filename(target=project)
        brain.write_text(brain.read_text(encoding="utf-8").replace("Bootstrap required: fill unknown sections from inspected evidence, never invented facts.", "Established baseline prepared by the harness from actual synthetic sources."), encoding="utf-8")
    before = snapshot(project)
    prompt = ('Revê o código já implementado em totals.py: procura duplicação, formas mais simples de o manter e trabalho desnecessário. '
              'Quero perceber o benefício, os riscos e como validar cada proposta antes de decidir alterações.') if args.scenario == "existing" else (
              'Quero uma revisão para limpeza, simplificação e otimização do código já implementado neste projeto.')
    command = ["codex", "exec", "--ignore-user-config", "--skip-git-repo-check", "--sandbox", "read-only", "--json", "--cd", str(project), "-"]
    code, stdout, stderr = invoke(command, prompt, project, args.timeout)
    (artifacts / "stdout.jsonl").write_text(stdout, encoding="utf-8")
    (artifacts / "stderr.txt").write_text(stderr, encoding="utf-8")
    events = [json.loads(line) for line in stdout.splitlines() if line.strip().startswith("{")]
    completed = any(e.get("type") == "turn.completed" for e in events)
    messages = [e["item"]["text"] for e in events if e.get("type") == "item.completed" and e.get("item", {}).get("type") == "agent_message"]
    # A progress message before a failed turn is not a final review response.
    answer = messages[-1] if messages and completed else ""
    try:
        parsed = json.loads(answer)
    except ValueError:
        parsed = None
    checks = {"process_completed": code == 0 and completed, "project_unchanged": snapshot(project) == before,
              "final_response_present": bool(answer), "conversational_response": not isinstance(parsed, (dict, list))}
    result = {"status": "ready_for_manual_review" if all(checks.values()) else "incomplete", "scenario": args.scenario,
              "checks": checks, "artifacts": str(artifacts), "process_exit_code": code,
              "native_errors": [e.get("message") or e.get("error", {}).get("message") for e in events if e.get("type") in ("error", "turn.failed")],
              "manual_review_required": ["Portuguese response without raw specialist JSON", "Existing: actual source locations, justified cleanup and behavior constraints",
                                         "Existing: optimization role participation labelled honestly; no unmeasured performance gains", "Empty: missing implementation explained, no invented findings or optimizer activation",
                                         "Read-only tools/sandbox are a backstop; inspect actual events, not only hashes"],
              "limitations": "Synthetic Codex scenario only. Mechanical format/hash checks do not establish reasoning quality, independent delegation or behavior on other hosts."}
    (artifacts / "assessment.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
