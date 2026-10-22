#!/usr/bin/env python3
"""Opt-in four-turn Codex conversation on a synthetic project, using account quota.

Checks output shape and file hashes mechanically. Phase semantics, language and
delegation evidence require manual transcript/session review. Never runs in CI.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11+ required")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dat.installer import maintain
from dat.memory import init
from dat.smoke import assess_discovery
from scripts.native_smoke import PLANNING_PROMPT, snapshot

TURNS = (
    ("initial_architecture", PLANNING_PROMPT),
    ("question_is_not_approval", "Porque recomendas essa arquitetura? Gostava de perceber "
     "a diferença entre arquitetura e framework, e se uma solução estática mais simples "
     "seria suficiente. Ainda estou a comparar opções."),
    ("architecture_only_approval", "Aprovo apenas esta arquitetura para a primeira versão: "
     "site estático em Astro, TypeScript e CSS, conteúdos em ficheiros locais e formulário "
     "demonstrativo sem transmitir dados. Sem backend, base de dados, contas ou serviços "
     "externos nesta versão. A integração real fica para depois. O que ficaria cada agente "
     "encarregado de fazer?"),
    ("deployment_discussion", "Antes de aprovar a execução dessas tarefas, quero discutir "
     "deployment e custos. Que opções fazem sentido para esta versão estática, quais os "
     "custos e limites relevantes e o que precisamos de decidir? Ainda não escolhi fornecedor "
     "nem autorizei contratar ou publicar nada."),
)


def invoke(command, prompt, folder, timeout):
    process = subprocess.Popen(command, cwd=folder, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, encoding="utf-8", start_new_session=os.name != "nt")
    try:
        stdout, stderr = process.communicate(prompt, timeout=timeout)
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        if os.name != "nt":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        stdout, stderr = process.communicate(timeout=10)
        return 124, stdout, stderr


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--timeout", type=int, default=240, help="Seconds per turn")
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({"status": "not_run", "reason": "Use --execute for real account-backed calls"}))
        return 0
    if not shutil.which("codex"):
        print(json.dumps({"status": "blocked", "reason": "Missing codex"}))
        return 2
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    root = Path(__file__).resolve().parents[1]
    artifacts = Path(tempfile.mkdtemp(prefix="dat-phase-smoke-"))
    folder = artifacts / "project"
    folder.mkdir()
    maintain(root, folder, "codex")
    init(folder)
    before = snapshot(folder)
    thread, results = None, []
    for index, (name, prompt) in enumerate(TURNS, 1):
        if thread is None:
            command = ["codex", "exec", "--ignore-user-config", "--skip-git-repo-check",
                       "--sandbox", "read-only", "--json", "--cd", str(folder), "-"]
        else:
            # Parent exec options explicitly preserve the read-only boundary on resume.
            command = ["codex", "exec", "--ignore-user-config", "--sandbox", "read-only",
                       "resume", "--skip-git-repo-check", "--json", thread, "-"]
        code, stdout, stderr = invoke(command, prompt, folder, args.timeout)
        (artifacts / f"{index}-{name}.jsonl").write_text(stdout, encoding="utf-8")
        (artifacts / f"{index}-{name}.stderr.txt").write_text(stderr, encoding="utf-8")
        events = [json.loads(line) for line in stdout.splitlines() if line.strip().startswith("{")]
        observed_thread = next((e.get("thread_id") for e in events if e.get("type") == "thread.started"), None)
        thread = thread or observed_thread
        assessment = assess_discovery(events)
        unchanged = before == snapshot(folder)
        errors = list(assessment["errors"])
        if code:
            errors.append(f"Native process failed or timed out: {code}")
        if not thread or (observed_thread and observed_thread != thread):
            errors.append("Same-session continuation not established")
        if not unchanged:
            errors.append("Synthetic project files changed before implementation approval")
        results.append({"turn": name, "exit_code": code, "project_files_unchanged": unchanged,
                        "format_check": assessment, "errors": errors})
        print(json.dumps({"turn": name, "mechanical_checks": "failed" if errors else "passed",
                          "artifacts": str(artifacts)}), flush=True)
        if errors:
            break
    summary = {
        "status": "ready_for_manual_review" if len(results) == len(TURNS) and not any(r["errors"] for r in results) else "incomplete",
        "native_session": thread, "artifacts": str(artifacts), "turns": results,
        "manual_review_required": [
            "Portuguese prose without activation or formatting reminders",
            "Initial Architect consultation and architecture approval request, without premature task dispatch",
            "Informational follow-up preserves the architecture approval boundary",
            "Architecture-only approval produces a proposed task table and asks to execute it; no implementation",
            "Deployment discussion consults DevOps as appropriate, verifies quoted prices and awaits scoped authorization",
            "Cross-check all claimed participation and any attempted writes against native session/tool events",
        ],
        "limitations": "Read-only sandbox is a backstop; file hashes and output format do not prove semantic compliance or future behavior.",
    }
    (artifacts / "assessment.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "ready_for_manual_review" else 2


if __name__ == "__main__":
    raise SystemExit(main())
