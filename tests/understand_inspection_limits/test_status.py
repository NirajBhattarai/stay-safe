"""Expected status explanation comes from stay-safe issue #18, not production text."""
import io
import json
from unittest.mock import patch

from stay_safe.cli import main
from tests.support import FEEDBACK, ConfigCase, copy_checkout, run_checkout, section


EXPLANATION = "Inspection incomplete (exit 2). See the report for what wasn't checked.\n"
COMPLETE = 'approval_policy = "on-request"\nsandbox_mode = "read-only"\n'


class StatusTests(ConfigCase):
    def test_stdio_header_helper_names_the_rejected_setting(self):
        # Codex rust-v0.167.0, mcp_types.rs:513-548 (linked from issue #155).
        checkout = copy_checkout(self.root / "checkout")
        config = COMPLETE + 'shell_environment_policy.inherit="core"\n[mcp_servers."docs.local"]\n'
        command = 'command="private-server"\n'
        url = 'url="https://example.invalid/mcp"\n'
        helper = 'http_headers_helper="private-helper"\n'
        reason = ("config-1: Codex cannot load this configuration because stdio MCP server "
                  "docs.local sets http_headers_helper.")
        for settings, gaps, program in ((command + helper, [reason], False), ('command=""\n' + helper, [reason], False),
                                        (command + helper + 'enabled=false\n', [reason], False), (command, [], True),
                                        (url + helper, [], True), (url, [], False)):
            with self.subTest(settings=settings):
                path = str(self.config(config + settings))
                run = run_checkout(checkout, "--config", path, "--format", "json", cwd=self.root)
                report = json.loads(run.stdout)
                self.assertEqual(report["inspection_gaps"], gaps)
                self.assertEqual(run.returncode, 2 if gaps else 0)
                programs = [risk["entry"] for risk in report["risks"] if risk["rule"] == "configured_program"]
                self.assertEqual(programs, ['config-1:mcp_servers."docs.local"'] if program else [])
                if gaps:
                    human = run_checkout(checkout, "--config", path, "--format", "markdown", cwd=self.root)
                    explanation = section(human.stdout, "Not checked")
                    self.assertIn("Codex can't load this configuration", explanation)
                    self.assertIn("the `docs.local` server", explanation.lower())
                    self.assertIn("remove `http_headers_helper`", explanation.lower())
                    self.assertNotIn("starts a program on your computer", section(human.stdout, "Your setup"))
                    for private in ("private-server", "private-helper"):
                        self.assertNotIn(private, run.stdout + human.stdout)

    def test_aws_credentials_name_each_unchecked_command(self):
        # NirajBhattarai: https://github.com/chalkbadger/stay-safe/issues/109#issuecomment-7003842313
        # openai/codex 086ccc8 codex-rs/model-provider-info/src/lib.rs L241–260, L308–324.
        checkout = copy_checkout(self.root / "checkout")
        quiet = COMPLETE + 'shell_environment_policy={inherit="none"}\nfeatures.apps=false\n'
        keys = ("credential_export", "auth_refresh")
        generic = "config-1: Configuration contains fields outside reader coverage; their values were withheld."
        for selected in (False, True):
            for settings, inline in (((), None), (keys[:1], None), (keys[1:], None), (keys, None),
                                     (keys, "{}"), (keys[:1], '"private-arg"'), (keys[1:], '"private-arg"')):
                with self.subTest(selected=selected, settings=settings, inline=inline):
                    text = quiet + ('model_provider="amazon-bedrock"\n' if selected else "")
                    text += '[model_providers.amazon-bedrock.aws]\nregion="us-west-2"\n'
                    for key in settings:
                        if inline is None:
                            text += f'[model_providers.amazon-bedrock.aws.{key}]\ncommand="private-{key}"\nargs=["private-arg"]\n'
                        else:
                            text += f'{key}={inline}\n'
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

        # The two providers in the second file each contribute a gap.
        malformed = self.config(quiet + '[model_providers.corp]\naws=false\n', "bad.toml")
        other = self.config(quiet + '[model_providers.first.aws.credential_export]\n'
                            '[model_providers.second.aws.auth_refresh]\n')
        args = ("--config", str(malformed), "--config", str(other))
        report = run_checkout(checkout, *args, "--format", "json", cwd=self.root)
        self.assertEqual(report.returncode, 2)
        self.assertCountEqual(json.loads(report.stdout)["inspection_gaps"], [
            "config-1: aws must be a table.",
            "config-2: Model-provider setting aws.auth_refresh was not checked for a credential command.",
            "config-2: Model-provider setting aws.credential_export was not checked for a credential command."])
        output = section(run_checkout(checkout, *args, cwd=self.root).stdout, "Not checked")
        self.assertIn("**Not checked: your `aws` settings.**", output)

    def test_app_auto_reviewer_is_named_as_unchecked(self):
        # NirajBhattarai: https://github.com/chalkbadger/stay-safe/issues/109#issuecomment-7094703327
        app = COMPLETE + 'shell_environment_policy={inherit="none"}\n[apps.calendar]\ndefault_tools_approval_mode="prompt"\n'
        gap = ("config-1: App approvals_reviewer is not evaluated; Codex may let a reviewer decide an app's tool calls "
               "instead of asking you.")
        cases = [(app + 'approvals_reviewer="auto_review"\n', [gap]),
                 (app + 'approvals_reviewer="guardian_subagent"\n', [gap]),
                 (app.replace("[apps.calendar]", '[apps._default]\napprovals_reviewer="auto_review"\n[apps.calendar]'), [gap]),
                 (app + 'approvals_reviewer="user"\n', []),
                 (app, [])]
        checkout = copy_checkout(self.root / "checkout")
        for text, expected in cases:
            with self.subTest(config=text):
                path = str(self.config(text))
                human = run_checkout(checkout, "--config", path, cwd=self.root)
                report = json.loads(run_checkout(checkout, "--config", path, "--format", "json", cwd=self.root).stdout)
                self.assertEqual(report["inspection_gaps"], expected)
                self.assertEqual((human.returncode, human.stderr), (2, EXPLANATION) if expected else (0, ""))
                if expected:
                    self.assertIn("**Not checked: an app's approval reviewer.**", section(human.stdout, "Not checked"))

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
