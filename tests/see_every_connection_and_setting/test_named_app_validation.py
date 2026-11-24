"""App flag validation at the Codex pin, rust-v0.167.0 (issue #173).

codex-rs/config/src/types.rs:459-486,546-561,576-588 declares the template flags
as bool, named App flags as Option<bool>, and both as typed parts of AppsConfigToml.
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

    def test_invalid_flag_on_a_disabled_app_keeps_the_off_reason_and_only_the_validation_gap(self):
        checkout = copy_checkout(self.root / "checkout")
        base = 'approval_policy="on-request"\nsandbox_mode="read-only"\nshell_environment_policy.inherit="none"\n'
        settings = ('links={example={default_tools_approval_mode="prompt"}}\n'
                    '[apps.notes]\ndestructive_enabled=false\ndefault_tools_approval_mode="approve"\n')
        for route, config, reason, expected_risks in (
            ("named App off", '[apps.calendar]\nenabled=false\n', "disabled", [("config-1:apps.notes", "automatic_tools")]),
            ("Apps off", 'features.apps=false\n[apps.calendar]\n', "disabled by features.apps = false", []),
        ):
            for field in ("open_world_enabled", "destructive_enabled"):
                with self.subTest(route=route, field=field):
                    path = self.config(base + config + f'{field}="false"\n' + settings)
                    run = run_checkout(checkout, "--agent", "codex", "--config", str(path),
                                       "--format", "json", cwd=self.root)
                    report = json.loads(run.stdout)
                    calendar = next(entry for entry in report["catalog"] if entry["name"] == "apps.calendar")
                    self.assertIn(reason, calendar["observations"])
                    self.assertEqual(run.returncode, 2)
                    self.assertEqual(report["inspection_gaps"],
                                     [f"config-1: Codex cannot load this configuration file because apps.calendar.{field} is not a boolean."])
                    self.assertEqual([(r["entry"], r["rule"]) for r in report["risks"]], expected_risks)

    def test_both_flags_reject_the_file_and_preserve_independent_app_settings(self):
        checkout = copy_checkout(self.root / "checkout")
        top = 'approval_policy="on-request"\nsandbox_mode="read-only"\nshell_environment_policy.inherit="none"\n'
        sibling = '[apps.notes]\ndestructive_enabled=false\ndefault_tools_approval_mode="approve"\n'
        for name in ("calendar", "_default"):
            for field in ("open_world_enabled", "destructive_enabled"):
                with self.subTest(name=name, field=field):
                    path = self.config(top + f'[apps.{name}]\n{field}="false"\ndefault_tools_approval_mode="approve"\n'
                                       + sibling)
                    run = run_checkout(checkout, "--agent", "codex", "--config", str(path),
                                       "--format", "json", cwd=self.root)
                    report = json.loads(run.stdout)
                    self.assertEqual(run.returncode, 2)
                    self.assertEqual(report["inspection_gaps"],
                                     [f"config-1: Codex cannot load this configuration file because apps.{name}.{field} is not a boolean."])
                    entry = next(row for row in report["catalog"] if row["name"] == f"apps.{name}")
                    self.assertIn("Codex cannot load this configuration file", entry["observations"])
                    self.assertEqual([(r["entry"], r["rule"]) for r in report["risks"]],
                                     [("config-1:apps.notes", "automatic_tools")])

    def test_app_tool_load_errors_name_the_field_in_both_formats(self):
        # Codex rust-v0.167.0, codex-rs/config/src/types.rs (AppConfig and AppToolConfig).
        checkout = copy_checkout(self.root / "checkout")
        top = 'approval_policy="on-request"\nsandbox_mode="read-only"\n[apps.cal]\n'
        for field, reason, control in (
            ("default_tools_enabled", "is not a boolean", "false"),
            ("default_tools_approval_mode", "is not one of auto, prompt, writes, approve", '"prompt"'),
            ("tools.delete.enabled", "is not a boolean", "false"),
            ("tools.delete.approval_mode", "is not one of auto, prompt, writes, approve", '"prompt"'),
        ):
            message = f"Codex cannot load this configuration file because apps.cal.{field} {reason}."
            for enabled in ("false", "true"):
                for value in ('"yes"', control):
                    path = self.config(top + f"enabled={enabled}\n{field}={value}\n")
                    for fmt in ("json", "markdown"):
                        with self.subTest(field=field, enabled=enabled, value=value, fmt=fmt):
                            run = run_checkout(checkout, "--config", str(path), "--format", fmt, cwd=self.root)
                            invalid = value != control
                            self.assertEqual(run.returncode, 2 if invalid else 0)
                            self.assertNotRegex(run.stdout + run.stderr, r"\byes\b")
                            if fmt == "markdown":
                                self.assertIn(message if invalid else "0 things not checked", run.stdout)
                                continue
                            report = json.loads(run.stdout)
                            self.assertEqual(report["inspection_gaps"], ["config-1: " + message] if invalid else [])
                            if enabled == "false":
                                app = next(row for row in report["catalog"] if row["name"] == "apps.cal")
                                self.assertIn("disabled", app["observations"])
                                self.assertFalse(any(risk["entry"].startswith("config-1:apps.cal")
                                                     for risk in report["risks"]))
