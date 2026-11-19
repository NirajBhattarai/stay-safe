"""Expected status explanation comes from stay-safe issue #18, not production text."""
import io
import json
from unittest.mock import patch

from stay_safe.cli import main
from tests.support import FEEDBACK, ConfigCase, copy_checkout, run_checkout, section


EXPLANATION = "Inspection incomplete (exit 2). See the report for what wasn't checked.\n"
COMPLETE = 'approval_policy = "on-request"\nsandbox_mode = "read-only"\n'


class StatusTests(ConfigCase):
    def test_aws_credentials_name_each_unchecked_command(self):
        # NirajBhattarai: https://github.com/chalkbadger/stay-safe/issues/109#issuecomment-7003842313
        # openai/codex 086ccc8 codex-rs/model-provider-info/src/lib.rs L241–260, L308–324.
        checkout = copy_checkout(self.root / "checkout")
        quiet = COMPLETE + 'shell_environment_policy={inherit="none"}\nfeatures.apps=false\n'
        keys = ("credential_export", "auth_refresh")
        generic = "config-1: Configuration contains fields outside reader coverage; their values were withheld."
        for selected in (False, True):
            for settings, empty in (((), False), (keys[:1], False), (keys[1:], False), (keys, False), (keys, True)):
                with self.subTest(selected=selected, settings=settings, empty=empty):
                    text = quiet + ('model_provider="amazon-bedrock"\n' if selected else "")
                    text += '[model_providers.amazon-bedrock.aws]\nregion="us-west-2"\n'
                    for key in settings:
                        text += f'[model_providers.amazon-bedrock.aws.{key}]\n'
                        if not empty:
                            text += f'command="private-{key}"\nargs=["private-arg"]\n'
                    path = str(self.config(text))
                    human = run_checkout(checkout, "--config", path, cwd=self.root)
                    machine = run_checkout(checkout, "--config", path, "--format", "json", cwd=self.root)
                    expected = [generic] if selected else []
                    for key in settings:
                        label = f"aws.{key}"
                        expected.append(f"config-1: Model-provider setting {label} was not checked for a credential command.")
                        self.assertIn(f"**Not checked: `{label}`.** Stay-safe did not check this setting for a credential "
                                      f"command.\n\n*What to do:* Review `{label}` in your config file.\n\n*File `config-1`*",
                                      section(human.stdout, "Not checked"))
                    report = json.loads(machine.stdout)
                    self.assertCountEqual(report["inspection_gaps"], expected)
                    self.assertEqual(report["risks"], [])
                    self.assertEqual(section(human.stdout, "Not checked").count("**Not checked:"), len(expected))
                    for run in (human, machine):
                        self.assertEqual((run.returncode, run.stderr), (2, EXPLANATION) if expected else (0, ""))
                        for private in ("private-arg", "private-auth_refresh", "private-credential_export"):
                            self.assertNotIn(private, run.stdout)
        auth = self.config(quiet + '[model_providers.corp.auth]\ncommand="private-export"\n')
        control = run_checkout(checkout, "--config", str(auth), cwd=self.root)
        self.assertEqual(control.returncode, 2)
        self.assertIn("a model provider's sign-in command", section(control.stdout, "Not checked"))

        # A malformed AWS group and a valid command in a different file remain distinct.
        malformed = self.config(quiet + '[model_providers.corp]\naws=false\n', "bad.toml")
        other = self.config(quiet + '[model_providers.first]\n[model_providers.second.aws.auth_refresh]\n')
        args = ("--config", str(malformed), "--config", str(other))
        report = run_checkout(checkout, *args, "--format", "json", cwd=self.root)
        self.assertEqual(report.returncode, 2)
        self.assertCountEqual(json.loads(report.stdout)["inspection_gaps"], [
            "config-1: aws must be a table.",
            "config-2: Model-provider setting aws.auth_refresh was not checked for a credential command."])
        output = section(run_checkout(checkout, *args, cwd=self.root).stdout, "Not checked")
        self.assertIn("**Not checked: your `aws` settings.**", output)

    def test_reports_with_gaps_explain_exit_two_on_stderr_only(self):
        checkout = copy_checkout(self.root / "checkout")
        private = self.config('private_key = "secret-value"\n', "private-input-name.toml")
        for args in (["--format", "markdown"], ["--format", "json"], ["--save"]):
            with self.subTest(args=args):
                run = run_checkout(checkout, "--config", str(private), *args, cwd=self.root)
                self.assertEqual((run.returncode, run.stderr), (2, EXPLANATION))
                self.assertNotIn(EXPLANATION.strip(), run.stdout)
                for secret in (str(private), "private-input-name", "secret-value"):
                    self.assertNotIn(secret, run.stdout + run.stderr)
                if "json" in args:
                    self.assertTrue(json.loads(run.stdout)["inspection_gaps"])
                else:
                    self.assertIn("## Not checked", run.stdout)

    def test_complete_reports_and_invalid_arguments_do_not_get_the_explanation(self):
        checkout = copy_checkout(self.root / "checkout")
        config = self.config(COMPLETE)
        for format_name in ("markdown", "json"):
            with self.subTest(format=format_name):
                run = run_checkout(checkout, "--config", str(config), "--format", format_name, cwd=self.root)
                self.assertEqual((run.returncode, run.stderr), (0, ""))
        for args, expected in ((["--unknown"], "Invalid arguments. Use --help.\n" + FEEDBACK),
                               (["--format", "json", "--save"], "--save can't be combined with --format json. Use --help.\n" + FEEDBACK)):
            with self.subTest(args=args):
                run = run_checkout(checkout, *args, cwd=self.root)
                self.assertEqual((run.returncode, run.stdout, run.stderr), (2, "", expected))

    def test_report_is_flushed_before_the_explanation_is_written(self):
        config = self.config("")
        events = []

        class Output(io.StringIO):
            def flush(self):
                events.append(("flushed", self.getvalue()))

        class Errors(io.StringIO):
            def write(self, text):
                events.append(("stderr", text))
                return super().write(text)

        with patch("sys.stdout", Output()), patch("sys.stderr", Errors()):
            status = main(["--config", str(config), "--format", "json"])
        self.assertEqual(status, 2)
        self.assertEqual([kind for kind, text in events], ["flushed", "stderr"])
        self.assertTrue(json.loads(events[0][1])["inspection_gaps"])
        self.assertEqual(events[1][1], EXPLANATION)
