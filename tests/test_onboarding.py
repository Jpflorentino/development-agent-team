"""Real context/privacy operations and offline provider evidence; no live providers."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from dat import memory, onboarding
from dat.context import ROLES, role_path
from dat.discovery import scan
from dat.installer import inspect, maintain, state_path
from dat.privacy import inspect_git
from dat.storage import Conflict

ROOT = Path(__file__).resolve().parents[1]


class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project"

    def install(self, **kwargs):
        return maintain(ROOT, self.project, "codex", **kwargs)

    def source(self):
        self.project.mkdir(parents=True, exist_ok=True)
        (self.project / "app.py").write_text("def greeting():\n    return 'Hello'\n", encoding="utf-8")

    def test_all_private_role_contexts_start_pending(self):
        self.install()
        self.assertEqual(len(list((self.project / "agents/contexts").glob("*-context.md"))), len(ROLES))
        state = onboarding.status(self.project)
        self.assertEqual(state["phase"], "pending")
        self.assertFalse(state["contexts_analyzed"])
        self.assertEqual(inspect(self.project)[0]["modified_or_missing"], [])

    def test_memory_roles_match_canonical_catalog(self):
        catalog = json.loads((ROOT / "agents/catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(set(ROLES), {role["id"] for role in catalog["agents"]})

    def test_unreadable_existing_git_metadata_does_not_bypass_privacy(self):
        self.project.mkdir()
        (self.project / ".git").mkdir()
        failure = subprocess.CompletedProcess([], 128, "", "Git state unavailable")
        with patch("dat.privacy.shutil.which", return_value="git"), patch("dat.privacy.subprocess.run", return_value=failure):
            with self.assertRaisesRegex(Conflict, "privacy is unverified"):
                inspect_git(self.project)

    def test_completed_analysis_requires_real_notes_and_source_evidence(self):
        self.source()
        self.install()
        with self.assertRaisesRegex(Conflict, "actual technical context"):
            onboarding.record(self.project, "software-architect", "completed", "Inspected code", ["app.py"])
        path = self.project / role_path("software-architect")
        path.write_text("# Architecture context\n\n## STATUS\ncompleted\n\n## BOUNDARIES\nPython module in app.py; no external persistence.\n", encoding="utf-8")
        with self.assertRaisesRegex(Conflict, "source references"):
            onboarding.record(self.project, "software-architect", "completed", "Inspected code")
        onboarding.record(self.project, "software-architect", "completed", "Inspected code", ["app.py"])
        self.assertEqual(onboarding.status(self.project)["roles"]["software-architect"]["status"], "completed")

    def test_context_references_are_supplementary_not_application_evidence(self):
        self.source()
        self.install()
        role = "software-architect"
        (self.project / role_path(role)).write_text("## STATUS\ncompleted\n\n## BOUNDARIES\nPython module in app.py.\n", encoding="utf-8")
        with self.assertRaisesRegex(Conflict, "inspected source references"):
            onboarding.record(self.project, role, "completed", "Inspected code", [role_path(role)])
        onboarding.record(self.project, role, "completed", "Inspected code", ["app.py", role_path(role)])
        self.assertEqual(onboarding.status(self.project)["errors"], [])
        with self.assertRaises(Conflict):
            onboarding.record(self.project, role, "completed", "Inspected code", ["app.py", "AGENTS.md"])

    def test_non_applicable_reasons_and_role_notes_survive_upgrade(self):
        self.install()
        for role in ROLES:
            onboarding.record(self.project, role, "not_applicable", "No application exists yet; domain not available")
        state = onboarding.status(self.project)
        self.assertTrue(state["contexts_analyzed"])
        before = (self.project / role_path("qa-engineer")).read_bytes()
        self.install(action="update")
        self.assertEqual((self.project / role_path("qa-engineer")).read_bytes(), before)
        self.install(action="uninstall")
        self.assertEqual((self.project / role_path("qa-engineer")).read_bytes(), before)

    def test_templates_or_missing_sources_do_not_prove_completion(self):
        self.install()
        state = onboarding.load(self.project)
        for role in ROLES:
            state["roles"][role] = {"status": "completed", "summary": "Claimed complete", "sources": ["missing.py"]}
        (self.project / onboarding.STATE).write_text(json.dumps(state), encoding="utf-8")
        result = onboarding.status(self.project)
        self.assertFalse(result["contexts_analyzed"])
        self.assertTrue(any("template" in error for error in result["errors"]))
        self.assertTrue(any("source" in error for error in result["errors"]))

    def test_empty_notes_cannot_be_marked_complete(self):
        self.source()
        self.install()
        (self.project / role_path("software-architect")).write_text("# Architecture\n\n## STATUS\ncompleted\n\n## BOUNDARIES\n", encoding="utf-8")
        with self.assertRaisesRegex(Conflict, "actual notes"):
            onboarding.record(self.project, "software-architect", "completed", "Claimed analysis", ["app.py"])

    def test_provider_detection_is_evidence_only_and_skips_secrets_dependencies(self):
        self.source()
        (self.project / "package.json").write_text(json.dumps({"dependencies": {"@vercel/analytics": "1", "@supabase/supabase-js": "2"}, "scripts": {"private": "secret-value"}}), encoding="utf-8")
        (self.project / "vercel.json").write_text("{}", encoding="utf-8")
        (self.project / ".env").write_text("SECRET=never-read-this-value", encoding="utf-8")
        generated = self.project / "node_modules/fake"
        generated.mkdir(parents=True)
        (generated / "wrangler.toml").write_text("ignored", encoding="utf-8")
        result = scan(self.project)
        self.assertEqual({c["provider"] for c in result["integration_candidates"]}, {"Vercel", "Supabase"})
        self.assertNotIn("secret-value", json.dumps(result))
        self.assertNotIn("never-read-this-value", json.dumps(result))
        self.assertTrue(all(not c["installation_authorized"] and c["catalog_availability"] == "not_checked" for c in result["integration_candidates"]))

    def test_scan_reports_partial_coverage_and_invalid_manifest(self):
        self.source()
        (self.project / "package.json").write_text("invalid json", encoding="utf-8")
        self.assertTrue(scan(self.project)["warnings"])
        result = scan(self.project, max_files=1)
        self.assertTrue(any("partial" in warning for warning in result["warnings"]))

    @unittest.skipUnless(shutil.which("git"), "Git required")
    def test_all_consumer_artifacts_remain_ignored_after_uninstall(self):
        self.project.mkdir()
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        self.install()
        for name in ("AGENTS.md", ".codex/agents/dat-team-leader.toml", "agents/project-context.md",
                     role_path("software-architect"), onboarding.STATE):
            self.assertEqual(subprocess.run(["git", "check-ignore", "-q", name], cwd=self.project).returncode, 0, name)
        self.install(action="uninstall")
        self.assertEqual(subprocess.run(["git", "check-ignore", "-q", role_path("qa-engineer")], cwd=self.project).returncode, 0)

    @unittest.skipUnless(shutil.which("git"), "Git required")
    def test_tracked_context_blocks_install_without_touching_index_or_files(self):
        path = self.project / "agents/project-context.md"
        path.parent.mkdir(parents=True)
        path.write_text("# Private context already tracked\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        subprocess.run(["git", "add", "agents/project-context.md"], cwd=self.project, check=True)
        before = subprocess.check_output(["git", "ls-files", "--stage"], cwd=self.project)
        with self.assertRaisesRegex(Conflict, "already tracked"):
            self.install()
        self.assertEqual(subprocess.check_output(["git", "ls-files", "--stage"], cwd=self.project), before)
        self.assertFalse((self.project / "AGENTS.md").exists())
        self.assertEqual(inspect_git(self.project)["tracked_private_files"], ["agents/project-context.md"])
