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
        keys = ("credential_export", "auth_refresh")
        for selected in (False, True):
            for settings in ((), keys[:1], keys[1:], keys):
                with self.subTest(selected=selected, settings=settings):
                    text = COMPLETE + ('model_provider="amazon-bedrock"\n' if selected else "")
                    text += '[model_providers.amazon-bedrock.aws]\nregion="us-west-2"\n'
                    for key in settings:
                        command = "aws" if key == "auth_refresh" else "private-export"
                        text += f'[model_providers.amazon-bedrock.aws.{key}]\ncommand="{command}"\nargs=["private-arg"]\n'
                    run = run_checkout(checkout, "--config", str(self.config(text)), cwd=self.root)
                    self.assertEqual(run.returncode, 2 if settings or selected else 0)
                    gaps = section(run.stdout, "Not checked")
                    for key in keys:
                        self.assertEqual(f"aws.{key}" in gaps, key in settings)
                    self.assertNotIn("private-arg", run.stdout)
                    self.assertNotIn("private-export", run.stdout)
        auth = self.config(COMPLETE + '[model_providers.corp.auth]\ncommand="private-export"\n')
        control = run_checkout(checkout, "--config", str(auth), cwd=self.root)
        self.assertEqual(control.returncode, 2)
        self.assertIn("a model provider's sign-in command", section(control.stdout, "Not checked"))

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
