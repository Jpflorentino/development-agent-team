"""Real filesystem tests for the shared project brain and legacy migration."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from dat import memory
from dat.context import LEGACY_PRIVATE, LEGACY_SHARED, POINTER, resolve
from dat.installer import inspect, maintain
from dat.storage import Conflict

ROOT = Path(__file__).resolve().parents[1]


class ProjectContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / "My Project"

    def install(self, platform="codex", **options):
        return maintain(ROOT, self.target, platform, **options)

    def test_install_creates_one_primary_brain_and_personalizes_instructions(self):
        result = self.install()
        self.assertEqual(result["context_file"], "agents/my-project-context.md")
        self.assertEqual(list((self.target / "agents").glob("*-context.md")),
                         [self.target / "agents/my-project-context.md"])
        self.assertFalse((self.target / LEGACY_SHARED).exists())
        self.assertFalse((self.target / LEGACY_PRIVATE).exists())
        self.assertIn("agents/my-project-context.md", (self.target / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertNotIn("agents/<project>-context.md", (self.target / "AGENTS.md").read_text(encoding="utf-8"))
        import tomllib
        for profile in (self.target / ".codex/agents").glob("dat-*.toml"):
            body = tomllib.loads(profile.read_text(encoding="utf-8"))["developer_instructions"]
            self.assertIn("agents/my-project-context.md", body)
            self.assertNotIn("agents/<project>-context.md", body)
        self.assertIn("Bootstrap required", memory.show(self.target)["text"])

    def test_migration_preserves_legacy_shared_and_private_archives(self):
        path = self.target / LEGACY_SHARED
        path.parent.mkdir(parents=True)
        shared = b"# Existing context\n\n## DECISIONS\n- Approved data contract\n"
        private = b"Private environment facts; do not copy into shared context.\n"
        path.write_bytes(shared)
        (self.target / LEGACY_PRIVATE).write_bytes(private)
        self.install()
        brain = memory.show(self.target)["text"]
        self.assertIn(shared.decode(), brain)
        self.assertNotIn(private.decode(), brain)
        self.assertEqual(path.read_bytes(), shared)
        self.assertEqual((self.target / LEGACY_PRIVATE).read_bytes(), private)
        self.assertIn("## RECOVERY", brain)

    def test_modified_brain_survives_update_and_uninstall_without_manifest_conflict(self):
        self.install()
        memory.add(self.target, "REQUIREMENTS", "A user correction must survive updates")
        brain = self.target / resolve(self.target)
        before = brain.read_bytes()
        self.install(action="update")
        self.assertEqual(inspect(self.target)[0]["modified_or_missing"], [])
        self.install(action="uninstall")
        self.assertEqual(brain.read_bytes(), before)
        self.assertTrue((self.target / POINTER).exists())

    def test_platforms_share_one_brain(self):
        for platform in ("codex", "claude-code", "github-copilot", "chatgpt"):
            self.install(platform)
        self.assertEqual(len(list((self.target / "agents").glob("*-context.md"))), 1)
        self.assertEqual(memory.show(self.target)["file"], "agents/my-project-context.md")

    def test_existing_custom_brain_is_reused_without_overwriting(self):
        path = self.target / "agents/fit-escola-context.md"
        path.parent.mkdir(parents=True)
        value = "# Project knowledge\nUser-maintained decisions.\n"
        path.write_text(value, encoding="utf-8")
        self.install()
        self.assertEqual(memory.show(self.target)["file"], "agents/fit-escola-context.md")
        self.assertEqual(path.read_text(encoding="utf-8"), value)

    def test_ambiguous_brains_require_explicit_selection(self):
        folder = self.target / "agents"
        folder.mkdir(parents=True)
        for name in ("first-context.md", "second-context.md"):
            (folder / name).write_text(name, encoding="utf-8")
        with self.assertRaisesRegex(Conflict, "Multiple"):
            self.install()
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.install(context_file="agents/second-context.md")
        self.assertEqual(resolve(self.target), "agents/second-context.md")
        with self.assertRaisesRegex(Conflict, "different central context"):
            self.install(action="update", context_file="agents/first-context.md")

    def test_recorded_path_survives_project_folder_rename(self):
        self.install()
        renamed = self.target.with_name("Renamed")
        self.target.rename(renamed)
        self.assertEqual(resolve(renamed), "agents/my-project-context.md")
        memory.add(renamed, "CURRENT_STATE", "Project folder renamed")
        self.assertEqual(len(list((renamed / "agents").glob("*-context.md"))), 1)

    def test_dry_run_migration_does_not_write(self):
        path = self.target / LEGACY_SHARED
        path.parent.mkdir(parents=True)
        path.write_text("# Legacy project facts\n", encoding="utf-8")
        self.install(dry_run=True)
        self.assertFalse((self.target / POINTER).exists())
        self.assertFalse((self.target / "agents").exists())

    def test_global_install_does_not_create_a_home_project_brain(self):
        self.install(scope="global")
        self.assertFalse((self.target / POINTER).exists())
        self.assertFalse((self.target / "agents").exists())
        self.assertIn("agents/<project>-context.md", (self.target / ".codex/AGENTS.md").read_text(encoding="utf-8"))

    def test_context_path_rejects_escape_and_malformed_values(self):
        for value in ("../outside-context.md", "/tmp/outside-context.md", "agents/nested/name-context.md",
                      'agents/name"-context.md', "agents/.git/context.md"):
            with self.subTest(value=value), self.assertRaises(Conflict):
                memory.init(self.target, dry_run=True, context_file=value)

    def test_git_privacy_and_sharing_survive_other_platforms_and_uninstall(self):
        import shutil
        if not shutil.which("git"):
            self.skipTest("Git unavailable")
        self.target.mkdir()
        subprocess.run(["git", "init", "-q", str(self.target)], check=True)
        def ignored():
            return subprocess.run(["git", "-C", str(self.target), "check-ignore", "-q",
                                   "agents/my-project-context.md"]).returncode == 0
        self.install()
        self.assertTrue(ignored())
        self.install(action="update")
        self.assertTrue(ignored())
        memory.init(self.target)
        self.install("claude-code")
        self.assertTrue(ignored())
        self.install(action="uninstall")
        self.install("claude-code", action="uninstall")
        self.assertTrue(ignored())
        self.assertTrue((self.target / resolve(self.target)).exists())

    def test_entries_update_timestamp_and_preserve_approval(self):
        memory.init(self.target)
        memory.add(self.target, "DECISIONS", "Approved architecture", "APPROVED")
        memory.add(self.target, "RECOVERY", "Next step: discuss task allocation")
        text = memory.show(self.target)["text"]
        self.assertEqual(text.count("Last updated (UTC):"), 1)
        self.assertNotIn("\n\n\n", text.split("No secrets", 1)[0])
        self.assertIn("APPROVED", text)
        self.assertIn("Next step", text)

    def test_tampered_context_pointer_is_rejected(self):
        self.install()
        (self.target / POINTER).write_text("../outside-context.md\n", encoding="utf-8")
        with self.assertRaises(Conflict):
            memory.show(self.target)

    def test_profile_conflict_prevents_partial_memory_migration(self):
        self.install()
        brain = self.target / resolve(self.target)
        brain.unlink()
        (self.target / POINTER).unlink()
        legacy = self.target / LEGACY_SHARED
        legacy.write_text("# Legacy facts to preserve\n", encoding="utf-8")
        profile = self.target / ".codex/agents/dat-backend-developer.toml"
        profile.write_text("User customization", encoding="utf-8")
        with self.assertRaises(Conflict):
            self.install(action="update")
        self.assertFalse(brain.exists())
        self.assertFalse((self.target / POINTER).exists())
        self.assertEqual(legacy.read_text(encoding="utf-8"), "# Legacy facts to preserve\n")

    def test_possible_legacy_secret_is_not_copied(self):
        legacy = self.target / LEGACY_SHARED
        legacy.parent.mkdir(parents=True)
        legacy.write_text("password=synthetic-secret-fixture\n", encoding="utf-8")
        with self.assertRaisesRegex(Conflict, "credential"):
            self.install()
        self.assertFalse((self.target / "agents/my-project-context.md").exists())
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_windows_legacy_context_is_migrated_without_duplicate_sections(self):
        legacy = self.target / LEGACY_SHARED
        legacy.parent.mkdir(parents=True)
        raw = b"# Windows context\r\n\r\n## DECISIONS\r\n- Approved choice\r\n"
        legacy.write_bytes(raw)
        self.install()
        memory.add(self.target, "DECISIONS", "Keep that choice", "APPROVED")
        self.assertEqual(legacy.read_bytes(), raw)
        text = memory.show(self.target)["text"]
        self.assertEqual(text.count("## DECISIONS\n"), 1)
        self.assertIn("Approved choice", text)
        self.assertIn("Keep that choice", text)
