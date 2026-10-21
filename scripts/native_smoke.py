#!/usr/bin/env python3
"""Opt-in real-client smoke. May use account quota; never run in offline CI.

Temporary synthetic fixtures only. Raw transcripts stay in that temporary folder,
outside the public repository. No auth/config files are copied or modified.
"""
import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11+ required")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dat.installer import maintain
from dat.memory import init
from dat.smoke import assess_codex, assess_discovery

PROMPT = """This is an explicitly authorized read-only native-agent smoke test on synthetic data.
Act as Team Leader. Do not edit files, invoke external services, commit, or install tools.
Read .ai-team/context.md and fixture.py, then use the actual native delegation tool
exactly once to invoke the installed dat-code-review-engineer custom agent.
Pass the fixture's actual source and a full delegation envelope to the reviewer,
because that agent deliberately lacks shell access. Ask for one consequential bug
with code evidence and the context marker. Wait for completion. Do not use a generic
agent, sequential simulation, or merely claim delegation: if the named agent or
native tool is unavailable return BLOCKED and explain.
Fixture acceptance: the reviewer should find division by zero for an empty list.
Finally return JSON with keys status, native_agent, marker, finding, tests_run,
delegation_evidence. Tests_run should say not run unless you ran a real test.
Do not ask for follow-up or perform any remediation.
"""

ROLE_PROMPT = """This is an explicitly authorized read-only native-agent smoke test on synthetic data.
Act as Team Leader. Do not edit files, invoke external services, commit, or install tools.
Read .ai-team/context.md and fixture.py. If your native delegation tool can select
dat-code-review-engineer, use it. If it cannot select named profiles, read
.ai-team/framework/codex/agents/code-review-engineer.md and pass that COMPLETE
canonical role instruction plus the COMPLETE actual source and context marker to
exactly one real native child through collaboration.spawn_agent (or the available
native equivalent). Use all delegation contract fields. This fallback is authorized.
The child inherits this read-only parent session. Require the full specialist report.
Wait for completion. Identify the empty-list division-by-zero defect with evidence.
Do not simulate a subagent. Do not claim the named profile was loaded if the role
was supplied as instructions to a generic native child. If no real delegation is
possible report BLOCKED.
Finally return JSON keys status, dispatch_method, native_profile_loaded, marker,
finding, tests_run, delegation_evidence. Do not run tests; do not remediate.
Before accepting the child, validate the protocol: STATUS and SUMMARY are strings;
FINDINGS, CHANGES, EVIDENCE, TESTS, RISKS, DECISIONS, QUESTIONS, CONTEXT_UPDATES
are ALL lists, including EVIDENCE and TESTS. Objects are list elements, not field
values. Ask that same child to correct an invalid envelope before finalizing.
"""

DISCOVERY_PROMPT = """Quero começar um projeto do zero: um site para uma empresa
fictícia de fisioterapia ao domicílio chamada Movimento em Casa. Quero apresentar a equipa, mostrar
um perfil de cada fisioterapeuta e permitir que as pessoas escolham uma profissional
e marquem uma sessão na disponibilidade dela. Ainda não escolhemos tecnologia nem
temos código da aplicação. Não sei se faz mais sentido uma landing page ou um site
completo. Qual é a tua opinião e o que precisas de saber antes de avançarmos?
Nesta fase quero apenas discutir a proposta, sem criar a aplicação, instalar
dependências, ligar serviços externos ou executar marcações reais.
"""


def snapshot(folder):
    return {path.relative_to(folder).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in folder.rglob("*") if path.is_file() and path.name not in ("stdout.jsonl", "stderr.txt")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=("codex", "claude-code"), required=True)
    parser.add_argument("--execute", action="store_true", help="Authorize the model call using your configured account")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--dispatch", choices=("profile", "role-envelope"), default="profile")
    parser.add_argument("--scenario", choices=("review", "discovery"), default="review")
    args = parser.parse_args()
    binary = "claude" if args.platform == "claude-code" else "codex"
    if not args.execute:
        print(json.dumps({"status": "not_run", "reason": "Use --execute for an actual account-backed smoke"}))
        return 0
    if not shutil.which(binary):
        print(json.dumps({"status": "blocked", "reason": f"Missing {binary}"}))
        return 2
    root = Path(__file__).resolve().parents[1]
    folder = Path(tempfile.mkdtemp(prefix=f"dat-smoke-{args.platform}-")).resolve()
    maintain(root, folder, args.platform)
    init(folder)
    if args.scenario == "review":
        (folder / "fixture.py").write_text("def average(values):\n    return sum(values) / len(values)\n", encoding="utf-8")
        with (folder / ".ai-team/context.md").open("a", encoding="utf-8") as stream:
            stream.write("\n- VERIFIED synthetic smoke marker: DAT_CONTEXT_1_0_0\n")
    before = snapshot(folder)
    if binary == "codex":
        command = [binary, "exec", "--ignore-user-config", "--skip-git-repo-check", "--sandbox", "read-only",
                   "--json", "--cd", str(folder), "-"]
    else:
        command = [binary, "--print", "--agent", "dat-team-leader", "--setting-sources", "project",
                   "--strict-mcp-config", "--permission-mode", "dontAsk", "--tools", "Read,Glob,Grep,Agent",
                   "--output-format", "stream-json", "--verbose", "--no-session-persistence"]
    try:
        prompt = DISCOVERY_PROMPT if args.scenario == "discovery" else ROLE_PROMPT if args.dispatch == "role-envelope" else PROMPT
        process = subprocess.Popen(command, cwd=folder, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, encoding="utf-8", start_new_session=os.name != "nt")
        try:
            stdout, stderr = process.communicate(prompt, timeout=args.timeout)
        except subprocess.TimeoutExpired:
            if os.name != "nt":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            stdout, stderr = process.communicate(timeout=10)
            (folder / "stdout.jsonl").write_text(stdout, encoding="utf-8")
            (folder / "stderr.txt").write_text(stderr, encoding="utf-8")
            print(json.dumps({"status": "blocked", "reason": "timeout", "fixture": str(folder)}))
            return 2
        (folder / "stdout.jsonl").write_text(stdout, encoding="utf-8")
        (folder / "stderr.txt").write_text(stderr, encoding="utf-8")
        assessment = {"status": "not_assessed"}
        events = [json.loads(line) for line in stdout.splitlines() if line.strip().startswith("{")]
        if args.scenario == "discovery":
            assessment = assess_discovery(events)
            assessment["project_files_unchanged"] = before == snapshot(folder)
            if not assessment["project_files_unchanged"]:
                assessment["errors"].append("Project files changed during discussion-only discovery")
                assessment["status"] = "incomplete"
        elif binary == "codex" and args.dispatch == "role-envelope":
            thread = next((event["thread_id"] for event in events if event.get("type") == "thread.started"), None)
            if thread:
                home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
                logs = list((home / "sessions").glob(f"**/*-{thread}.jsonl"))
                if len(logs) == 1:
                    records = [json.loads(line) for line in logs[0].read_text(encoding="utf-8").splitlines()]
                    assessment = assess_codex(records)
        print(json.dumps({"status": "completed_process" if process.returncode == 0 else "blocked_or_failed",
                          "exit_code": process.returncode, "platform": args.platform, "dispatch": args.dispatch, "fixture": str(folder),
                          "scenario": args.scenario,
                          "transcript": str(folder / "stdout.jsonl"),
                          "assessment": assessment,
                          "note": "Inspect tool events before classifying native delegation as tested"}, indent=2))
        return 2 if assessment["status"] == "incomplete" else process.returncode
    except subprocess.TimeoutExpired as error:
        for name, raw in (("stdout.jsonl", error.stdout), ("stderr.txt", error.stderr)):
            (folder / name).write_bytes(raw if isinstance(raw, bytes) else (raw or "").encode())
        print(json.dumps({"status": "blocked", "reason": "timeout", "fixture": str(folder)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
