"""Real filesystem tests in temporary project/home directories."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dat.installer import inspect, maintain, state_path
from dat.storage import Conflict

ROOT = Path(__file__).resolve().parents[1]


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / "project"

    def install(self, platform="codex", **kwargs):
        return maintain(ROOT, self.target, platform, **kwargs)

    def test_clean_repeat_update_remove_all_platform_scopes(self):
        for platform in ("codex", "claude-code", "github-copilot", "chatgpt"):
            for scope in ("project", "global"):
                if platform == "chatgpt" and scope == "global":
                    continue
                with self.subTest(platform=platform, scope=scope):
                    self.target = Path(self.temp.name) / f"{platform}-{scope}"
                    self.assertTrue(self.install(platform, scope=scope)["changed"])
                    self.assertEqual(self.install(platform, scope=scope)["changed"], [])
                    self.assertEqual(self.install(platform, scope=scope, action="update")["changed"], [])
                    self.assertEqual(inspect(self.target)[0]["modified_or_missing"], [])
                    self.assertTrue(self.install(platform, scope=scope, action="uninstall")["changed"])
                    self.assertEqual(inspect(self.target), [])
                    self.assertEqual(self.install(platform, scope=scope, action="uninstall")["changed"], [])

    def test_dry_run_creates_nothing(self):
        preview = self.install(dry_run=True)
        self.assertTrue(preview["changed"])
        self.assertFalse(self.target.exists())

    def test_existing_instruction_and_gitignore_restored_byte_for_byte(self):
        self.target.mkdir()
        originals = {"AGENTS.md": b"Existing instructions without newline", ".gitignore": b"bin/\r\n"}
        for name, content in originals.items():
            (self.target / name).write_bytes(content)
        self.install()
        self.install(action="uninstall")
        for name, content in originals.items():
            self.assertEqual((self.target / name).read_bytes(), content)

    def test_customizations_outside_block_survive_update_and_remove(self):
        self.install()
        instructions = self.target / "AGENTS.md"
        instructions.write_bytes(b"User prefix\n\n" + instructions.read_bytes() + b"\nUser suffix\n")
        self.install(action="update")
        self.install(action="uninstall")
        self.assertEqual(instructions.read_bytes(), b"User prefix\n\n\nUser suffix\n")

    def test_managed_file_modification_blocks_all_changes(self):
        self.install()
        profile = self.target / ".codex/agents/dat-backend-developer.toml"
        profile.write_text("user customization", encoding="utf-8")
        original = (self.target / "AGENTS.md").read_bytes()
        for action in ("install", "update", "uninstall"):
            with self.assertRaises(Conflict):
                self.install(action=action)
            self.assertEqual(profile.read_text(), "user customization")
            self.assertEqual((self.target / "AGENTS.md").read_bytes(), original)

    def test_existing_unowned_profile_is_not_adopted_or_overwritten(self):
        profile = self.target / ".codex/agents/dat-team-leader.toml"
        profile.parent.mkdir(parents=True)
        profile.write_text("unowned", encoding="utf-8")
        with self.assertRaises(Conflict):
            self.install()
        self.assertEqual(profile.read_text(), "unowned")
        self.assertFalse((self.target / "AGENTS.md").exists())

    def test_modified_managed_block_is_conflict(self):
        self.install()
        instructions = self.target / "AGENTS.md"
        instructions.write_text(instructions.read_text().replace("# Development Agent Team", "# Customized"))
        with self.assertRaises(Conflict):
            self.install(action="update")

    def test_upgrade_replaces_managed_content_and_detects_version(self):
        self.install()
        state = self.target / state_path("codex", "project")
        value = json.loads(state.read_text())
        value["version"] = "0.9.0"
        state.write_text(json.dumps(value))
        from dat.adapters import render
        modified = render(ROOT, "codex", "project")
        path = ".codex/agents/dat-team-leader.toml"
        modified[path] += "\n# upgraded\n"
        with patch("dat.adapters.render", return_value=modified):
            result = self.install(action="update")
        self.assertEqual(result["previous_version"], "0.9.0")
        self.assertIn("# upgraded", (self.target / path).read_text())

    def test_platform_coexistence_and_selective_uninstall(self):
        self.install("codex")
        self.install("claude-code")
        self.install("github-copilot")
        self.install("codex", action="uninstall")
        self.assertTrue((self.target / ".claude/agents/dat-team-leader.md").exists())
        self.assertTrue((self.target / ".github/agents/dat-team-leader.agent.md").exists())
        self.assertEqual(len(inspect(self.target)), 2)
        self.assertTrue(all(not item["modified_or_missing"] for item in inspect(self.target)))

    def test_private_and_sharing_options(self):
        self.install()
        ignored = (self.target / ".gitignore").read_text()
        self.assertIn("/.codex/agents/dat-team-leader.toml", ignored)
        self.assertIn("context.md", (self.target / ".ai-team/.gitignore").read_text())
        self.install(action="update", share_agents=True, share_context=True)
        ignored = (self.target / ".gitignore").read_text()
        self.assertNotIn("/.codex/agents/", ignored)
        self.assertNotIn("/.ai-team/context.md\n", ignored)
        self.assertNotIn("context.md\n", (self.target / ".ai-team/.gitignore").read_text())
        self.assertIn("/.ai-team/context.local.md", ignored)
        self.install(action="update")
        self.assertEqual((self.target / ".gitignore").read_text(), ignored)

    def test_uninstall_preserves_memory_and_unrelated_files(self):
        self.install()
        context = self.target / ".ai-team/context.md"
        context.write_text("approved decision")
        unrelated = self.target / "application.py"
        unrelated.write_text("print('existing')")
        self.install(action="uninstall")
        self.assertEqual(context.read_text(), "approved decision")
        self.assertTrue(unrelated.exists())

    def test_missing_update_and_global_chatgpt_fail_explicitly(self):
        with self.assertRaises(Conflict):
            self.install(action="update")
        with self.assertRaisesRegex(ValueError, "ChatGPT"):
            self.install("chatgpt", scope="global")

    def test_no_consumer_planning_or_task_protocol_files(self):
        result = self.install()
        self.assertFalse(any(Path(name).name in {"plan.md", "progress.md", "task.json"} for name in result["changed"]))

    def test_git_privacy_survives_uninstall_and_sharing_is_project_wide(self):
        import shutil, subprocess
        if not shutil.which("git"):
            self.skipTest("Git not installed")
        self.target.mkdir()
        subprocess.run(["git", "init", "-q", str(self.target)], check=True)
        self.install()
        from dat import memory
        memory.init(self.target)
        def ignored(name):
            return subprocess.run(["git", "-C", str(self.target), "check-ignore", "-q", name]).returncode == 0
        self.assertTrue(ignored(".ai-team/context.md"))
        self.install(action="update", share_context=True)
        self.assertFalse(ignored(".ai-team/context.md"))
        memory.init(self.target)
        self.assertFalse(ignored(".ai-team/context.md"))
        self.install("claude-code")
        self.assertFalse(ignored(".ai-team/context.md"))
        self.install(action="uninstall")
        self.install("claude-code", action="uninstall")
        self.assertTrue(ignored(".ai-team/context.local.md"))
        self.assertTrue(ignored(".ai-team/.dat/transactions/private/journal.json"))

    def test_uninstall_without_memory_init_keeps_backups_and_context_ignored(self):
        import shutil, subprocess
        if not shutil.which("git"):
            self.skipTest("Git not installed")
        self.target.mkdir()
        subprocess.run(["git", "init", "-q", str(self.target)], check=True)
        self.install()
        self.install(action="uninstall")
        for path in (".ai-team/context.local.md", ".ai-team/context.md", ".ai-team/.dat/private"):
            self.assertEqual(subprocess.run(["git", "-C", str(self.target), "check-ignore", "-q", path]).returncode, 0)

    def test_memory_share_option_updates_existing_install_choice(self):
        self.install()
        from dat import memory
        memory.init(self.target, share_context=True)
        self.install(action="update")
        self.assertNotIn("context.md\n", (self.target / ".ai-team/.gitignore").read_text())

    @unittest.skipIf(__import__("os").name == "nt", "Windows symlink creation can require privileges")
    def test_symlink_target_is_rejected(self):
        real = Path(self.temp.name) / "real"
        real.mkdir()
        self.target.symlink_to(real, target_is_directory=True)
        with self.assertRaises(Conflict):
            self.install()
        self.assertEqual(list(real.iterdir()), [])
