import json

from tests.support import ConfigCase, INCOMPLETE, copy_checkout, run_checkout, section


BASE = 'approval_policy="on-request"\nsandbox_mode="read-only"\nshell_environment_policy.inherit="none"\n'
SELECTOR = "The checked Codex version stops loading the configuration when it reads the top-level profile setting."
TABLES = ("Legacy profile tables do not select a profile. If this is the base user config, "
          "starting Codex with a matching --profile name stops configuration loading.")


class ProfileTests(ConfigCase):
    def test_selector_and_named_tables_report_different_loading_conditions(self):
        checkout = copy_checkout(self.root / "checkout")
        named = '[profiles.private-name]\nsandbox_mode="danger-full-access"\n'
        selector = 'profile="private-name"\n'
        for extra, expected in ((selector, SELECTOR), (selector + named, SELECTOR), (named, TABLES),
                                (named + '[profiles.other-private]\n', TABLES), ('profile=""\n', SELECTOR)):
            with self.subTest(extra=extra):
                path = str(self.config(BASE + extra))
                machine = run_checkout(checkout, "--config", path, "--format", "json", cwd=self.root)
                human = run_checkout(checkout, "--config", path, "--format", "markdown", cwd=self.root)
                self.assertEqual(json.loads(machine.stdout)["inspection_gaps"], ["config-1: " + expected])
                self.assertEqual(json.loads(machine.stdout)["risks"], [])
                message = section(human.stdout, "Not checked")
                self.assertEqual(message.count("*What to do:*"), 1)
                if expected == SELECTOR:
                    self.assertIn("**This file uses an old way to select a profile.**", message)
                    self.assertIn("stops when it reads this setting", message)
                    self.assertIn("Remove the `profile` setting.", message)
                    self.assertIn("`work.config.toml`", message)
                    self.assertIn("Remove the old table and start Codex with `--profile work`.", message)
                else:
                    self.assertIn("**This file defines a profile but doesn’t select it.**", message)
                    self.assertIn("If this is your main `config.toml`", message)
                    self.assertIn("matching", message)
                    self.assertIn("`--profile", message)
                for run in (human, machine):
                    self.assertEqual((run.returncode, run.stderr), (2, INCOMPLETE))
                    self.assertNotIn("private-name", run.stdout)
                    self.assertNotIn("other-private", run.stdout)

    def test_each_snapshot_keeps_its_own_profile_message_and_settings(self):
        checkout = copy_checkout(self.root / "checkout")
        one = self.config(BASE + 'profile="example"\nnotify=["example-program"]\n', "one.toml")
        two = self.config(BASE + '[profiles.example]\napproval_policy="never"\n', "two.toml")
        cli = ("--config", str(one), "--config", str(two))
        machine = run_checkout(checkout, *cli, "--format", "json", cwd=self.root)
        report = json.loads(machine.stdout)
        self.assertCountEqual(report["inspection_gaps"], ["config-1: " + SELECTOR, "config-2: " + TABLES])
        self.assertEqual([(r["entry"], r["rule"]) for r in report["risks"]], [("config-1:notify", "configured_program")])
        human = run_checkout(checkout, *cli, cwd=self.root)
        messages = section(human.stdout, "Not checked").split("*File `config-1`*")
        self.assertIn("**This file uses an old way to select a profile.**", messages[0])
        self.assertIn("**This file defines a profile but doesn’t select it.**", messages[1])
        self.assertIn("*File `config-2`*", messages[1])
        for run in (human, machine):
            self.assertEqual((run.returncode, run.stderr), (2, INCOMPLETE))
