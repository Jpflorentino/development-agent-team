"""Small transactional file store with conservative conflict detection.

Journals are private installation recovery data, never task/agent messages.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import socket
import sys
import tempfile
import uuid
from contextlib import contextmanager
from pathlib import Path


class Conflict(ValueError):
    """Refuse to overwrite a file or escape the installation root."""


def digest(value: bytes | None) -> str | None:
    return hashlib.sha256(value).hexdigest() if value is not None else None


def safe_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or not path.parts or any(p in ("..", ".git") for p in path.parts):
        raise Conflict(f"Unsafe managed path: {relative}")
    # Refuse symlinks at/below the selected root. Ancestors may be OS aliases
    # (macOS /var -> /private/var); those are outside the managed boundary.
    result = root / path
    for entry in (result, *result.parents):
        if entry.is_symlink():
            raise Conflict(f"Symlink is not a managed file: {entry}")
        if entry == root:
            break
    if root.absolute() not in result.absolute().parents:
        raise Conflict(f"Path escapes target: {relative}")
    return result


def read(root: Path, relative: str) -> bytes | None:
    path = safe_path(root, relative)
    if path.exists() and not path.is_file():
        raise Conflict(f"Expected regular file: {relative}")
    return path.read_bytes() if path.exists() else None


def atomic(path: Path, value: bytes | None) -> None:
    if value is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    old_mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
    fd, name = tempfile.mkstemp(prefix=".dat-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(name, old_mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def locked(root: Path):
    path = safe_path(root, ".ai-team/.dat/lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise Conflict("Maintenance/memory lock exists; inspect doctor, then recover --unlock if its process has stopped.") from error
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump({"pid": os.getpid(), "host": socket.gethostname()}, stream)
        yield
    finally:
        path.unlink(missing_ok=True)


def pending(root: Path) -> list[Path]:
    folder = safe_path(root, ".ai-team/.dat/transactions")
    if not folder.exists():
        return []
    found = []
    for path in sorted(folder.glob("*/journal.json")):
        safe_path(root, str(path.relative_to(root)))
        if json.loads(path.read_text(encoding="utf-8"))["state"] == "applying":
            found.append(path)
    return found


def transaction(root: Path, changes: dict[str, bytes | None], dry_run=False) -> list[str]:
    changes = {name: value for name, value in changes.items() if read(root, name) != value}
    if dry_run or not changes:
        return list(changes)
    if pending(root):
        raise Conflict("Interrupted transaction found. Run recover before another write.")
    entries = []
    for name, value in changes.items():
        before = read(root, name)
        entries.append({"path": name, "before": base64.b64encode(before).decode() if before is not None else None,
                        "after_hash": digest(value)})
    journal = safe_path(root, f".ai-team/.dat/transactions/{uuid.uuid4().hex}/journal.json")
    record = {"state": "applying", "changes": entries}
    atomic(journal, json.dumps(record, indent=2).encode())
    applied = []
    try:
        for entry in entries:
            atomic(safe_path(root, entry["path"]), changes[entry["path"]])
            applied.append(entry)
        record["state"] = "committed"
        atomic(journal, json.dumps(record, indent=2).encode())
    except BaseException:
        for entry in reversed(applied):
            value = base64.b64decode(entry["before"]) if entry["before"] is not None else None
            atomic(safe_path(root, entry["path"]), value)
        record["state"] = "rolled_back"
        atomic(journal, json.dumps(record, indent=2).encode())
        raise
    return list(changes)


def recover(root: Path, unlock=False, dry_run=False) -> list[str]:
    lock = safe_path(root, ".ai-team/.dat/lock")
    if unlock and lock.exists():
        if sys.platform == "win32":
            raise Conflict("Automatic stale-lock removal is unavailable on Windows. Verify the process has stopped, then remove only .ai-team/.dat/lock manually.")
        owner = json.loads(lock.read_text(encoding="utf-8"))
        if owner["host"] != socket.gethostname():
            raise Conflict("Lock belongs to another host; verify owner manually before recovery.")
        try:
            os.kill(owner["pid"], 0)
        except ProcessLookupError:
            if not dry_run:
                lock.unlink()
        else:
            raise Conflict("Lock owner is still running; refusing to unlock.")
    if dry_run:
        return [str(p.relative_to(root)) for p in pending(root)]
    with locked(root):
        paths = pending(root)
        # Validate every rollback before changing anything.
        for path in paths:
            for entry in json.loads(path.read_text(encoding="utf-8"))["changes"]:
                before = base64.b64decode(entry["before"]) if entry["before"] is not None else None
                if digest(read(root, entry["path"])) not in (digest(before), entry["after_hash"]):
                    raise Conflict(f"Recovery conflict: {entry['path']}; preserve your edits before retrying.")
        for path in paths:
            record = json.loads(path.read_text(encoding="utf-8"))
            for entry in reversed(record["changes"]):
                before = base64.b64decode(entry["before"]) if entry["before"] is not None else None
                atomic(safe_path(root, entry["path"]), before)
            record["state"] = "recovered"
            atomic(path, json.dumps(record, indent=2).encode())
        return [str(p.relative_to(root)) for p in paths]
