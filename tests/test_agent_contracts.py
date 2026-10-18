"""Keep native-role report instructions aligned with the executable contract."""
import json
import re
import unittest
from pathlib import Path

from dat.policy import REPORT_FIELDS, validate_report

ROOT = Path(__file__).resolve().parents[1]


class AgentContractTests(unittest.TestCase):
    def test_every_canonical_role_instructs_exact_report_field_types(self):
        catalog = json.loads((ROOT / "agents/catalog.json").read_text(encoding="utf-8"))
        for agent in catalog["agents"]:
            with self.subTest(agent=agent["id"]):
                text = (ROOT / agent["definition"]).read_text(encoding="utf-8")
                output = text.split("## Output format\n", 1)[1].split("## Communication rules\n", 1)[0]
                self.assertIn("`STATUS`: string", output)
                self.assertIn("`SUMMARY`: nonempty string", output)
                for field in REPORT_FIELDS[2:]:
                    self.assertIn(f"`{field}`: list", output)
                self.assertIn("Use `[]` for an empty list", output)
                self.assertIn("never as replacements for the list itself", output)
                self.assertNotIn("or “none”", output)

    def test_documented_specialist_example_passes_real_report_validator(self):
        text = (ROOT / "docs/orchestration.md").read_text(encoding="utf-8")
        response = text.split("## Specialist response\n", 1)[1].split("## Central validation", 1)[0]
        examples = re.findall(r"```json\n(.*?)\n```", response, re.S)
        self.assertTrue(examples, "A concrete valid report example is required")
        for example in examples:
            report = json.loads(example)
            self.assertEqual(set(report), set(REPORT_FIELDS))
            self.assertEqual(validate_report(report), [])
            for field in REPORT_FIELDS[2:]:
                self.assertIsInstance(report[field], list)
        self.assertIsInstance(json.loads(examples[0])["EVIDENCE"][0], dict)
        self.assertIsInstance(json.loads(examples[0])["TESTS"][0], dict)


if __name__ == "__main__":
    unittest.main()
