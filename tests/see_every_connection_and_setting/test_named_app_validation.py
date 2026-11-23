"""Named App validation at the Codex pin, rust-v0.167.0 (issue #173).

codex-rs/config/src/types.rs:546-561 declares AppConfig.open_world_enabled as
Option<bool>. The file describes Notes independently of Calendar's load error.
"""
import json

from tests.support import ConfigCase, copy_checkout, run_checkout


class NamedAppValidationTests(ConfigCase):
    def test_invalid_open_world_flag_names_the_app_and_preserves_its_sibling(self):
        checkout = copy_checkout(self.root / "checkout")
        config = ('approval_policy="on-request"\nsandbox_mode="workspace-write"\n'
                  'shell_environment_policy.inherit="none"\n[apps.calendar]\n'
                  'destructive_enabled=true\nopen_world_enabled=')
        notes = '\n[apps.notes]\ndestructive_enabled=false\ndefault_tools_approval_mode="approve"\n'
        child = '\n[apps.calendar.tools.erase]\nenabled=true\napproval_mode="approve"\n'
        notes_risk = ("config-1:apps.notes", "automatic_tools")
        calendar_risks = {("config-1:apps.calendar", "destructive_tools"),
                          ("config-1:apps.calendar", "self_described_tools")}
        for value, extra, valid in (('"false"', '', False), ('0', child, False),
                                    ('false', '', True), ('true', '', True)):
            with self.subTest(value=value):
                path = self.config(config + value + extra + notes)
                run = run_checkout(checkout, "--agent", "codex", "--config", str(path),
                                   "--format", "json", cwd=self.root)
                report = json.loads(run.stdout)
                self.assertEqual(run.returncode, 0 if valid else 2)
                observed = {(r["entry"], r["rule"]) for r in report["risks"]}
                self.assertEqual(observed, {notes_risk} | (calendar_risks if valid else set()))
                if valid:
                    self.assertEqual(report["inspection_gaps"], [])
                else:
                    self.assertEqual(len(report["inspection_gaps"]), 1)
                    gap = report["inspection_gaps"][0]
                    self.assertIn("calendar", gap)
                    self.assertIn("open_world_enabled", gap)
                    self.assertIn("bool", gap.lower())
