"""Dependency-free maintenance entry point with JSON results."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, memory
from .installer import PLATFORMS, maintain
from .policy import MODES, RISKS, select
from .storage import Conflict, recover
from .validation import doctor, validate

ROOT = Path(__file__).resolve().parent.parent


def parser():
    cli = argparse.ArgumentParser(description="Development Agent Team offline maintenance (Python 3.11+)")
    cli.add_argument("--version", action="version", version=__version__)
    commands = cli.add_subparsers(dest="command", required=True)
    for action in ("install", "update", "uninstall"):
        sub = commands.add_parser(action)
        sub.add_argument("--platform", required=True, choices=PLATFORMS)
        sub.add_argument("--scope", default="project", choices=("project", "global"))
        sub.add_argument("--target", type=Path)
        sub.add_argument("--dry-run", action="store_true")
        if action != "uninstall":
            sub.add_argument("--share-agents", action="store_true")
            sub.add_argument("--share-context", action="store_true")
    sub = commands.add_parser("validate")
    sub.add_argument("--source", type=Path, default=ROOT)
    sub = commands.add_parser("doctor")
    sub.add_argument("--target", type=Path, default=Path.cwd())
    sub = commands.add_parser("recover")
    sub.add_argument("--target", type=Path, default=Path.cwd())
    sub.add_argument("--unlock", action="store_true")
    sub.add_argument("--dry-run", action="store_true")
    sub = commands.add_parser("select", help="Contract/simulation policy only; does not execute agents")
    sub.add_argument("--mode", required=True, choices=MODES)
    sub.add_argument("--risk", default="LOW", choices=RISKS)
    sub.add_argument("--areas", nargs="*", default=[])
    sub.add_argument("--delegation", action="store_true", help="Caller has verified native delegation")
    sub.add_argument("--parallel", action="store_true", help="Caller has verified concurrency")
    context = commands.add_parser("memory").add_subparsers(dest="memory_command", required=True)
    for action in ("init", "show", "add", "compact", "stale"):
        sub = context.add_parser(action)
        sub.add_argument("--target", type=Path, default=Path.cwd())
        if action in ("show", "add", "compact"):
            sub.add_argument("--local", action="store_true")
        if action == "init":
            sub.add_argument("--share-context", action="store_true")
            sub.add_argument("--dry-run", action="store_true")
        if action == "add":
            sub.add_argument("--section", choices=memory.SECTIONS, required=True)
            sub.add_argument("--status", choices=memory.STATUSES, default="VERIFIED")
            sub.add_argument("--text", required=True)
            sub.add_argument("--expected-hash")
        if action == "stale":
            sub.add_argument("--days", type=int, default=30)
    return cli


def run(args):
    if args.command in ("install", "update", "uninstall"):
        target = args.target or (Path.home() if args.scope == "global" else Path.cwd())
        return maintain(ROOT, target.absolute(), args.platform, args.scope, args.command, args.dry_run,
                        getattr(args, "share_agents", False), getattr(args, "share_context", False))
    if args.command == "validate":
        return validate(args.source)
    if args.command == "doctor":
        return doctor(ROOT, args.target.absolute())
    if args.command == "select":
        return select(args.mode, args.risk, args.areas, args.delegation, args.parallel)
    if args.command == "recover":
        return {"recovered": recover(args.target.absolute(), args.unlock, args.dry_run), "dry_run": args.dry_run}
    if args.command == "memory":
        target = args.target.absolute()
        if args.memory_command == "init":
            return {"changed": memory.init(target, args.share_context, args.dry_run)}
        if args.memory_command == "show":
            return memory.show(target, args.local)
        if args.memory_command == "add":
            return {"changed": memory.add(target, args.section, args.text, args.status, args.local, args.expected_hash)}
        if args.memory_command == "compact":
            return {"changed": memory.compact(target, args.local)}
        if args.memory_command == "stale":
            return {"stale_candidates": memory.stale(target, args.days)}
    raise ValueError("Unsupported command")


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = run(args)
        errors = result.get("errors", [])
        warnings = result.get("warnings", [])
        status = "error" if errors else "warning" if warnings else "success"
        output = {"status": status, "summary": f"{args.command}: {status}", "result": result,
                  "next_actions": ["Resolve reported errors and rerun the same command"] if errors else [],
                  "artifacts": result.get("changed", [])}
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 2 if errors else 0
    except (Conflict, ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"status": "error", "summary": str(error), "next_actions": [
            "Inspect the conflict/cause; preserve local changes before retrying",
            "Stop if ownership or authorization cannot be established"], "artifacts": []}, indent=2), file=sys.stderr)
        return 2
