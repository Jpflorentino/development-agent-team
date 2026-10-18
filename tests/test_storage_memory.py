import base64
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dat import memory, storage
from dat.storage import Conflict, digest, locked, recover, safe_path, transaction


class StorageMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_rollback_after_write_failure(self):
        (self.root / "existing").write_bytes(b"old")
        original = storage.atomic
        def flaky(path, value):
            if path.name == "fail":
                raise OSError("injected failure")
            return original(path, value)
        with patch("dat.storage.atomic", side_effect=flaky):
            with self.assertRaises(OSError):
                transaction(self.root, {"existing": b"new", "fail": b"value"})
        self.assertEqual((self.root / "existing").read_bytes(), b"old")
        self.assertFalse((self.root / "fail").exists())
        self.assertEqual(storage.pending(self.root), [])

    def journal(self, value=b"after"):
        path = self.root / ".ai-team/.dat/transactions/interrupted/journal.json"
        path.parent.mkdir(parents=True)
        record = {"state": "applying", "changes": [{"path": "existing", "before": base64.b64encode(b"before").decode(),
                                                    "after_hash": digest(b"after")} ]}
        path.write_text(json.dumps(record))
        (self.root / "existing").write_bytes(value)
        return path

    def test_interrupted_recovery(self):
        path = self.journal()
        with self.assertRaises(Conflict):
            transaction(self.root, {"other": b"no"})
        self.assertEqual(len(recover(self.root, dry_run=True)), 1)
        self.assertEqual((self.root / "existing").read_bytes(), b"after")
        recover(self.root)
        self.assertEqual((self.root / "existing").read_bytes(), b"before")
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["state"], "recovered")

    def test_recovery_refuses_unrelated_edits(self):
        self.journal(b"user changed it")
        with self.assertRaises(Conflict):
            recover(self.root)
        self.assertEqual((self.root / "existing").read_bytes(), b"user changed it")

    def test_lock_prevents_concurrent_memory_writes(self):
        memory.init(self.root)
        with locked(self.root):
            with self.assertRaises(Conflict):
                memory.add(self.root, "DECISIONS", "Keep existing stack", "APPROVED")
            with self.assertRaises(Conflict):
                recover(self.root, unlock=True)

    def test_windows_unlock_never_signals_a_process(self):
        with locked(self.root):
            with patch("dat.storage.sys.platform", "win32"), patch("dat.storage.os.kill") as signal_process:
                with self.assertRaisesRegex(Conflict, "Windows"):
                    recover(self.root, unlock=True, dry_run=True)
                signal_process.assert_not_called()

    def test_memory_contexts_isolated_and_idempotent(self):
        self.assertTrue(memory.init(self.root))
        self.assertEqual(memory.init(self.root), [])
        before = memory.show(self.root)
        memory.add(self.root, "DECISIONS", "Keep PostgreSQL", "APPROVED", expected_hash=before["hash"])
        self.assertIn("Keep PostgreSQL", memory.show(self.root)["text"])
        self.assertNotIn("Keep PostgreSQL", memory.show(self.root, local=True)["text"])
        memory.add(self.root, "CURRENT_STATE", "Local test fixture", local=True)
        self.assertNotIn("Local test fixture", memory.show(self.root)["text"])
        other = self.root / "other"
        memory.init(other)
        self.assertNotIn("Keep PostgreSQL", memory.show(other)["text"])

    def test_stale_hash_cannot_overwrite_context(self):
        memory.init(self.root)
        old = memory.show(self.root)["hash"]
        memory.add(self.root, "DECISIONS", "Keep contracts", "APPROVED")
        with self.assertRaises(Conflict):
            memory.add(self.root, "DECISIONS", "Replace contracts", "PROPOSED", expected_hash=old)

    def test_compaction_preserves_decisions_and_removes_only_duplicates(self):
        memory.init(self.root)
        memory.add(self.root, "DECISIONS", "Keep contracts", "APPROVED")
        file = self.root / memory.filename()
        raw = file.read_text(encoding="utf-8")
        entry = next(line for line in raw.splitlines() if line.startswith("- ["))
        file.write_text(raw.replace(entry, entry + "\n" + entry))
        memory.compact(self.root)
        self.assertEqual(file.read_text(encoding="utf-8").count("Keep contracts"), 1)
        self.assertIn("APPROVED", file.read_text(encoding="utf-8"))

    def test_stale_detection_never_deletes(self):
        memory.init(self.root)
        memory.add(self.root, "KNOWN_ISSUES", "Revalidate fixture behavior")
        file = self.root / memory.filename()
        raw = file.read_text(encoding="utf-8")
        import re
        file.write_text(re.sub(r"\d{4}-\d{2}-\d{2}", "2020-01-01", raw))
        before = file.read_bytes()
        self.assertTrue(memory.stale(self.root, days=30))
        self.assertEqual(file.read_bytes(), before)

    def test_secrets_and_multiline_injection_rejected(self):
        memory.init(self.root)
        with self.assertRaises(Conflict):
            memory.add(self.root, "CURRENT_STATE", "password=synthetic-example")
        with self.assertRaises(ValueError):
            memory.add(self.root, "DECISIONS", "text\n## PROJECT\nreplacement")

    def test_context_privacy_ignore_and_dry_run(self):
        root = self.root / "new"
        memory.init(root, dry_run=True)
        self.assertFalse(root.exists())
        memory.init(root, share_context=True)
        ignores = (root / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("/.ai-team/context.local.md", ignores)
        self.assertNotIn("/.ai-team/context.md\n", ignores)

    def test_path_traversal_and_git_metadata_rejected(self):
        for name in ("../outside", ".git/config", "/absolute"):
            with self.subTest(name=name), self.assertRaises(Conflict):
                safe_path(self.root, name)

    def test_context_recovery_new_session(self):
        memory.init(self.root)
        memory.add(self.root, "CONSTRAINTS", "No production deployment")
        # No process-local state is required for another invocation.
        import subprocess, sys
        root = Path(__file__).resolve().parents[1]
        proc = subprocess.run([sys.executable, str(root / "scripts/dat.py"), "memory", "show", "--target", str(self.root)],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("No production deployment", json.loads(proc.stdout)["result"]["text"])
