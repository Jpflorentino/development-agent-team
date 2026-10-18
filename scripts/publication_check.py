#!/usr/bin/env python3
"""Conservative publication checks; heuristic scan, not a secret-free guarantee."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = {
    "private_key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "github_token": r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b",
    "openai_key": r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b",
    "aws_access_key": r"\bAKIA[A-Z0-9]{16}\b",
    "jwt": r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b",
    "local_home_path": r"(?:/Users/[A-Za-z0-9_.-]+/|C:\\Users\\[A-Za-z0-9_.-]+\\)",
}


def main():
    proc = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True)
    if proc.returncode:
        print(json.dumps({"status": "error", "reason": "Initialize and stage the intended publication first"}))
        return 2
    paths = [name for name in proc.stdout.decode().split("\0") if name]
    findings = []
    for name in paths:
        path = ROOT / name
        if path.is_symlink():
            findings.append({"file": name, "rule": "unexpected_symlink"})
            continue
        public_template = name == "templates/project-context.local.md"
        if name.startswith(".ai-team/") or (name.endswith((".local.md", ".pem", ".key")) and not public_template) or Path(name).name.startswith(".env"):
            findings.append({"file": name, "rule": "private_artifact"})
        indexed = subprocess.run(["git", "show", f":{name}"], cwd=ROOT, capture_output=True)
        if indexed.returncode:
            findings.append({"file": name, "rule": "unreadable_index_object"})
            continue
        raw = indexed.stdout
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            findings.append({"file": name, "rule": "binary_requires_manual_review"})
            continue
        for rule, pattern in RULES.items():
            for match in re.finditer(pattern, text):
                findings.append({"file": name, "line": text[:match.start()].count("\n") + 1, "rule": rule})
    if not paths:
        findings.append({"rule": "no_tracked_files"})
    print(json.dumps({"status": "error" if findings else "success", "files_scanned": len(paths),
                      "findings": findings, "limitations": "Heuristic patterns only; review staged content and tracking state"}, indent=2))
    return 2 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
