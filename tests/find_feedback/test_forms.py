import json
import unittest

from tests.support import ROOT


class FeedbackFormTests(unittest.TestCase):
    def test_forms_collect_context_without_requiring_a_report(self):
        required = {
            "challenge": {"finding", "revision", "disputed-claim", "evidence"},
            "error": {"attempt", "error"},
            "idea": {"goal", "change"},
        }
        for name, expected in required.items():
            with self.subTest(form=name):
                form = json.loads((ROOT / ".github/ISSUE_TEMPLATE" / (name + ".yml")).read_text())
                self.assertTrue(form["name"].strip())
                self.assertTrue(form["description"].strip())
                fields = [f for f in form["body"] if f["type"] != "markdown"]
                ids = [f["id"] for f in fields]
                self.assertEqual(len(ids), len(set(ids)))
                self.assertIn("report", ids)
                self.assertEqual({f["id"] for f in fields if f.get("validations", {}).get("required") is True}, expected)
                for field in fields:
                    self.assertRegex(field["id"], r"^[A-Za-z0-9_-]+$")
                    self.assertTrue(field["attributes"]["label"].strip())
                    if field["id"] in expected | {"report"}:
                        self.assertEqual(field["type"], "textarea")
                guidance = " ".join(f["attributes"]["value"] for f in form["body"] if f["type"] == "markdown")
                self.assertIn("Do not include credentials, raw private configuration", guidance)
                self.assertIn("names", guidance)

    def test_finding_field_explains_how_to_share_a_warning_with_private_names(self):
        form = json.loads((ROOT / ".github/ISSUE_TEMPLATE/challenge.yml").read_text())
        finding = next(field for field in form["body"] if field.get("id") == "finding")
        help_text = finding["attributes"]["description"]
        before, ids, after = help_text.partition("rule ID, entry ID, and exact")
        self.assertIn("private names", before)
        self.assertIn("rerun stay-safe on a sample config with made-up names and use that report", before)
        self.assertTrue(ids, help_text)
        self.assertIn("For a missed warning, say what you expected.", after)
