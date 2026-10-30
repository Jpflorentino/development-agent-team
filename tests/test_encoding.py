"""Keep project text portable when the platform default is Windows cp1252."""
import ast
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_test_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tests" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EncodingTests(unittest.TestCase):
    def test_project_text_io_declares_its_encoding(self):
        missing = []
        for folder in ("dat", "scripts", "tests"):
            for path in (ROOT / folder).rglob("*.py"):
                for node in ast.walk(ast.parse(path.read_bytes())):
                    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                        continue
                    method = node.func.attr
                    if method in ("read_text", "write_text"):
                        index = 0 if method == "read_text" else 1
                    elif method in ("open", "fdopen"):
                        if method == "open" and isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                            continue  # os.open uses file flags and produces no text stream.
                        mode_index = 0 if method == "open" else 1
                        mode = next((k.value for k in node.keywords if k.arg == "mode"),
                                    node.args[mode_index] if len(node.args) > mode_index else ast.Constant("r"))
                        if isinstance(mode, ast.Constant) and isinstance(mode.value, str) and "b" in mode.value:
                            continue
                        index = 2 if method == "open" else 3
                    else:
                        continue
                    explicit = any(k.arg == "encoding" for k in node.keywords) or len(node.args) > index
                    if not explicit:
                        missing.append(f"{path.relative_to(ROOT)}:{node.lineno} {method}")
        self.assertEqual(missing, [], "Project text must not depend on the platform encoding")

    def test_windows_default_reproductions_preserve_utf8_memory_and_bundles(self):
        storage = load_test_module("test_storage_memory")
        tasks = load_test_module("test_task_management")
        read, write = Path.read_text, Path.write_text

        def legacy_read(path, encoding=None, errors=None, **kwargs):
            return read(path, encoding=encoding or "cp1252", errors=errors, **kwargs)

        def legacy_write(path, data, encoding=None, errors=None, **kwargs):
            return write(path, data, encoding=encoding or "cp1252", errors=errors, **kwargs)

        suite = unittest.TestSuite([
            storage.StorageMemoryTests("test_compaction_preserves_decisions_and_removes_only_duplicates"),
            storage.StorageMemoryTests("test_stale_detection_never_deletes"),
            tasks.TaskManagementTests("test_all_installed_surfaces_bundle_the_task_management_protocol"),
        ])
        with patch.object(Path, "read_text", legacy_read), patch.object(Path, "write_text", legacy_write):
            result = unittest.TestResult()
            suite.run(result)
        self.assertTrue(result.wasSuccessful(), "\n".join(detail for _, detail in result.errors + result.failures))
