import json
from pathlib import Path
import re

from tests.support import ConfigCase, copy_checkout, run_checkout


DOCS = Path(__file__).resolve().parents[2] / "docs"


class ReviewTests(ConfigCase):
    def review(self):
        record = json.loads((DOCS / "codex-scan-state.json").read_text())
        return (DOCS / record["field_reviews"]["rust-v0.172.0"]).read_text()

    def test_scan_record_links_to_field_dispositions_and_pinned_sources(self):
        text = self.review()
        sources = dict(re.findall(r"^\[([\w-]+)\]: (\S+)$", text, re.MULTILINE))
        rows = {}
        for line in text.splitlines():
            if line.startswith("| "):
                settings, explanation = line.strip("|").split("|")
                for field in re.findall(r"`([^`]+)`", settings):
                    rows[field] = explanation
        feature_gap = "Stay-safe gives the general `features` gap."
        groups = (
            (["apps.*.tools.*.approvals_reviewer"], "either automatic value produces a named gap", "reviewer"),
            (["plugins.*.apps.*.tools.*.approvals_reviewer"], "whole `plugins` section under “Not checked.”", "overlays"),
            (["features.guardianv3.housekeeper", "features.guardianv3.housekeeper.routing_instructions",
              "features.guardianv3.housekeeper.batch_timeout_ms"], feature_gap, "housekeeper"),
            (["features.guardianv3.reviewer", "features.guardianv3.reviewer.retrieval_instructions",
              "features.guardianv3.max_instruction_tokens"], feature_gap, "board"),
            (["features.guardianv3.message_board_in_memory"], feature_gap, "resume"),
            (["features.connector_tool_result_passthrough"], feature_gap, "capture"),
            (["features.realtime_frames_local"], feature_gap, "enrollment"),
            (["profiles.*."], "same `profiles` gap for a table alone", "profile-layer"),
            (["tui.keymap", "tui.keymap.agents", "tui.keymap.agents.next_group", "tui.keymap.agents.next_group[]",
              "tui.keymap.agents.previous_group", "tui.keymap.agents.previous_group[]"],
             "outside its permissions report and gives no gap", "navigation"),
        )
        for fields, disposition, source in groups:
            for field in fields:
                with self.subTest(field=field):
                    self.assertIn(disposition, rows[field])
                    self.assertIn(f"][{source}]", rows[field])
            self.assertRegex(sources[source], r"^https://github\.com/openai/codex/blob/"
                             r"3d86e43b075adeba2193ec5c22ac92f55afd82e6/.+#L\d+-L\d+$")
        profile_features = {f"profiles.*.{field}" for field in rows if field.startswith("features.")}
        self.assertEqual(len(profile_features), 9)
        self.assertIn("The schema repeats all nine inside legacy profile tables.", rows["profiles.*."])

    def test_published_example_reports_match_the_cli(self):
        example = self.review().split("## App tool example\n", 1)[1]
        config = re.search(r"```toml\n(.*?)```", example, re.DOTALL)
        markdown = re.search(r"^> (\*\*Not checked:.*)$", example, re.MULTILINE)
        machine = re.search(r"```json\n(.*?)```", example, re.DOTALL)
        path = str(self.config(config[1]))
        checkout = copy_checkout(self.root / "checkout")
        human_run = run_checkout(checkout, "--config", path, "--format", "markdown", cwd=self.root)
        json_run = run_checkout(checkout, "--config", path, "--format", "json", cwd=self.root)
        self.assertEqual((human_run.returncode, json_run.returncode), (2, 2))
        self.assertIn(markdown[1], human_run.stdout.splitlines())
        self.assertEqual(json.loads(machine[1]), json.loads(json_run.stdout)["inspection_gaps"])
