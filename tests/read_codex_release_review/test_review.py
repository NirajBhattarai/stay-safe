import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]


class ReviewTests(unittest.TestCase):
    def test_scan_record_links_to_field_dispositions_and_pinned_sources(self):
        state = json.loads((ROOT / "docs/codex-scan-state.json").read_text())
        review = ROOT / "docs" / state.get("field_reviews", {}).get("rust-v0.172.0", "missing-review")
        self.assertTrue(review.is_file(), "The scan record must link to the reviewed release.")
        text = review.read_text()
        sources = dict(re.findall(r"^\[([\w-]+)\]: (\S+)$", text, re.MULTILINE))
        groups = (
            ("apps.*.tools.*.approvals_reviewer", "named gap", "reviewer"),
            ("plugins.*.apps.*.tools.*.approvals_reviewer", "plugins", "overlays"),
            ("features.guardianv3.reviewer.retrieval_instructions", "features", "board"),
            ("features.connector_tool_result_passthrough", "features", "request"),
            ("features.realtime_frames_local", "features", "enrollment"),
            ("profiles.*.", "profiles", "profile-layer"),
            ("tui.keymap.agents.previous_group[]", "no gap", "navigation"),
        )
        for field, disposition, source in groups:
            with self.subTest(field=field):
                row = next((line for line in text.splitlines() if f"`{field}`" in line and line.startswith("| ")), "")
                self.assertIn(disposition, row)
                self.assertIn(f"][{source}]", row)
                self.assertRegex(sources.get(source, ""), r"^https://github\.com/openai/codex/blob/"
                                 r"3d86e43b075adeba2193ec5c22ac92f55afd82e6/.+#L\d+-L\d+$")
