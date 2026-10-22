"""Adapter contract tests; these do not invoke models or native client runtimes."""

import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import tomllib
import unittest

from dat.adapters import INSTRUCTION_FILES, PLATFORMS, render


ROOT = Path(__file__).resolve().parents[1]


def frontmatter(text):
    """Parse the deliberately small generated YAML subset without dependencies."""
    if not text.startswith("---\n"):
        raise AssertionError("Missing YAML frontmatter")
    front, body = text[4:].split("---\n", 1)
    result = {}
    for line in front.splitlines():
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith('"') or (value.startswith("[") and '"' in value):
            value = json.loads(value)
        elif value.startswith("["):
            value = [item.strip() for item in value[1:-1].split(",")]
        result[key] = value
    return result, body.lstrip()


class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "agents/catalog.json").read_text(encoding="utf-8"))

    def test_render_is_deterministic_and_contains_no_absolute_targets(self):
        for platform in PLATFORMS:
            for scope in ("project", "global"):
                if (platform, scope) == ("chatgpt", "global"):
                    continue
                with self.subTest(platform=platform, scope=scope):
                    files = render(ROOT, platform, scope)
                    self.assertEqual(files, render(ROOT, platform, scope))
                    for name, text in files.items():
                        self.assertFalse(PurePosixPath(name).is_absolute())
                        self.assertNotIn("..", PurePosixPath(name).parts)
                        self.assertNotIn("\\", name)
                        self.assertIsInstance(text, str)
                        self.assertTrue(text.endswith("\n"), name)
                    self.assertNotIn(".codex/config.toml", files)

    def test_native_agents_preserve_canonical_content(self):
        for platform in ("claude-code", "codex", "github-copilot"):
            files = render(ROOT, platform, "project")
            profiles = {name: text for name, text in files.items() if "/dat-" in name}
            self.assertEqual(len(profiles), 10)
            for agent in self.catalog["agents"]:
                suffix = ".toml" if platform == "codex" else ".agent.md" if platform == "github-copilot" else ".md"
                profile = next(text for name, text in profiles.items() if name.endswith(f"/dat-{agent['id']}{suffix}"))
                if platform == "codex":
                    data = tomllib.loads(profile)
                    body = data["developer_instructions"]
                    self.assertEqual(data["description"], agent["description"])
                    self.assertNotIn("model", data)
                    self.assertNotIn("sandbox_mode", data)
                    self.assertNotIn("approval_policy", data)
                else:
                    data, body = frontmatter(profile)
                self.assertEqual(data["name"], "dat-" + agent["id"])
                canonical = (ROOT / agent["definition"]).read_text(encoding="utf-8").strip()
                self.assertIn(canonical, body)
                self.assertIn("Shared operating contract", body)
                self.assertIn("Required specialist response types", body)
                self.assertIn("EVIDENCE, TESTS, RISKS, DECISIONS, QUESTIONS, and CONTEXT_UPDATES are JSON arrays", body)
                self.assertIn("Reject non-list report", body)
                self.assertIn("request a corrected response", body)
                self.assertIn("Canonical reference bundle", body)
                bundle_path = f".ai-team/framework/{platform}/{agent['definition']}"
                self.assertEqual(files[bundle_path].strip(), canonical)

    def test_reviewers_have_conservative_native_tool_restrictions(self):
        for agent in self.catalog["agents"]:
            identifier = agent["id"]
            codex = tomllib.loads(render(ROOT, "codex", "project")[f".codex/agents/dat-{identifier}.toml"])
            claude, _ = frontmatter(render(ROOT, "claude-code", "project")[f".claude/agents/dat-{identifier}.md"])
            copilot, _ = frontmatter(render(ROOT, "github-copilot", "project")[f".github/agents/dat-{identifier}.agent.md"])
            if agent["read_only"]:
                self.assertEqual(claude["tools"], ["Read", "Grep", "Glob"])
                self.assertEqual(copilot["tools"], ["read", "search"])
                self.assertTrue(all(value is False for value in codex["features"].values()))
                self.assertIn("not a complete filesystem", codex["developer_instructions"])
            else:
                self.assertNotIn("tools", claude)
                self.assertNotIn("tools", copilot)
                self.assertNotIn("features", codex)

    def test_main_conversation_omits_internal_schemas_but_keeps_runtime_and_roles(self):
        for platform in PLATFORMS:
            for scope in ("project", "global"):
                if (platform, scope) == ("chatgpt", "global"):
                    continue
                with self.subTest(platform=platform, scope=scope):
                    files = render(ROOT, platform, scope)
                    name = next((p for p in files if p in INSTRUCTION_FILES),
                                ".ai-team/chatgpt/project-instructions.md")
                    main = files[name]
                    self.assertNotIn("## Required specialist response types", main)
                    self.assertNotIn("### Internal delegation report", main)
                    self.assertNotIn("`STATUS`: string", main)
                    self.assertIn("### User conversation", main)
                    self.assertIn("## Communication rules", main)
                    self.assertIn("## Available specialist profiles", main)
                    runtime = (ROOT / f"adapters/{platform}/runtime.md").read_text().strip()
                    self.assertIn(runtime, main)
                    canonical = files[f".ai-team/framework/{platform}/agents/team-leader.md"]
                    self.assertIn("### Internal delegation report", canonical)
                    if platform == "codex":
                        profile = tomllib.loads(files[".codex/agents/dat-team-leader.toml"])
                        self.assertIn("`STATUS`: string", profile["developer_instructions"])

    def test_project_and_global_native_instruction_locations(self):
        expected = {
            "claude-code": ("CLAUDE.md", ".claude/CLAUDE.md"),
            "codex": ("AGENTS.md", ".codex/AGENTS.md"),
            "github-copilot": (".github/copilot-instructions.md", ".copilot/copilot-instructions.md"),
        }
        for platform, locations in expected.items():
            for scope, location in zip(("project", "global"), locations):
                files = render(ROOT, platform, scope)
                self.assertEqual(set(files) & INSTRUCTION_FILES, {location})
                self.assertIn("Team Leader in the main conversation", files[location])
                self.assertIn("explicitly requests such delegation", files[location])
                self.assertEqual(files[location].count("## Available specialist profiles"), 1)
        global_copilot = render(ROOT, "github-copilot", "global")
        self.assertEqual(len([p for p in global_copilot if p.startswith(".copilot/agents/")]), 10)
        self.assertFalse(any(p.startswith(".github/") for p in global_copilot))

    def test_codex_role_fallback_distinguishes_runtime_profile_and_permissions(self):
        files = render(ROOT, "codex", "project")
        for body in (files["AGENTS.md"], tomllib.loads(files[".codex/agents/dat-team-leader.toml"])["developer_instructions"]):
            self.assertIn("actual native subagent tool schema", body)
            self.assertIn("native delegated role with supplied definition", body)
            self.assertIn("does not automatically", body)
            self.assertIn("parent review session", body)
            self.assertIn("report enforcement as BLOCKED", body)
            self.assertIn("independent review as BLOCKED", body)

    def test_platform_bundles_do_not_conflict(self):
        projects = [set(render(ROOT, platform, "project")) for platform in PLATFORMS]
        for i, left in enumerate(projects):
            for right in projects[i + 1:]:
                self.assertFalse(left & right)

    def test_chatgpt_export_is_explicitly_manual_and_not_independent_role_switching(self):
        files = render(ROOT, "chatgpt", "project")
        setup = files[".ai-team/chatgpt/SETUP.md"]
        self.assertIn("upload", setup.lower())
        self.assertIn("does not automatically grant access", setup)
        reference = files[".ai-team/chatgpt/specialist-reference.md"]
        for agent in self.catalog["agents"]:
            self.assertIn((ROOT / agent["definition"]).read_text(encoding="utf-8").strip(), reference)
        self.assertIn("independent review as BLOCKED", reference)
        self.assertFalse(any(p in INSTRUCTION_FILES for p in files))
        with self.assertRaisesRegex(ValueError, "global filesystem"):
            render(ROOT, "chatgpt", "global")

    def test_invalid_platform_and_scope_fail_before_writing(self):
        with self.assertRaisesRegex(ValueError, "Unknown platform"):
            render(ROOT, "not-a-client", "project")
        with self.assertRaisesRegex(ValueError, "Unknown scope"):
            render(ROOT, "codex", "shared")

    def test_invalid_catalog_paths_and_identifiers_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            shutil.copytree(ROOT / "agents", source / "agents")
            catalog_path = source / "agents/catalog.json"
            for key, value in (("definition", "../private.md"), ("definition", "/tmp/private.md"), ("definition", "C:/private.md"), ("id", "../other"), ("read_only", "true")):
                catalog = json.loads(json.dumps(self.catalog))
                catalog["agents"][0][key] = value
                catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    render(source, "codex", "project")

    def test_copilot_oversize_prompt_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            shutil.copytree(ROOT / "agents", source / "agents")
            shutil.copytree(ROOT / "adapters", source / "adapters")
            (source / "agents/team-leader.md").write_text("x" * 30001, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "30,000 character"):
                render(source, "github-copilot", "project")

    def test_source_symlink_escape_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            shutil.copytree(ROOT / "agents", source / "agents")
            private = Path(tmp) / "private.md"
            private.write_text("outside source", encoding="utf-8")
            definition = source / self.catalog["agents"][0]["definition"]
            definition.unlink()
            try:
                definition.symlink_to(private)
            except (OSError, NotImplementedError):
                self.skipTest("Creating symlinks is unavailable on this host")
            with self.assertRaisesRegex(ValueError, "escapes framework root"):
                render(source, "codex", "project")

    def test_toml_and_yaml_roundtrip_quoted_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            shutil.copytree(ROOT / "agents", source / "agents")
            shutil.copytree(ROOT / "adapters", source / "adapters")
            catalog = json.loads(json.dumps(self.catalog))
            unusual = 'Contains "quoted" values: backslash \\ and Unicode café\nsecond line'
            catalog["agents"][0]["description"] = unusual
            (source / "agents/catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
            unicode_role = "# Team Leader\n\nVerificação: ação, café, € and 日本語.\n"
            (source / "agents/team-leader.md").write_text(unicode_role, encoding="utf-8")
            data = tomllib.loads(render(source, "codex", "project")[".codex/agents/dat-team-leader.toml"])
            self.assertEqual(data["description"], unusual)
            self.assertIn(unicode_role.strip(), data["developer_instructions"])
            data, body = frontmatter(render(source, "claude-code", "project")[".claude/agents/dat-team-leader.md"])
            self.assertEqual(data["description"], unusual)
            self.assertIn(unicode_role.strip(), body)
            bundle = render(source, "chatgpt", "project")
            self.assertEqual(bundle[".ai-team/framework/chatgpt/agents/team-leader.md"], unicode_role)
            self.assertIn(unicode_role.strip(), bundle[".ai-team/chatgpt/specialist-reference.md"])


if __name__ == "__main__":
    unittest.main()
