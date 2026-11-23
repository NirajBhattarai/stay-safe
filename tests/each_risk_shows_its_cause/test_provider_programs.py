"""Model provider sign-in and AWS credential commands are programs the report flags."""
from stay_safe.report import inspect, markdown
from tests.support import ConfigCase

BASE = 'approval_policy="on-request"\nsandbox_mode="read-only"\n'


class ProviderProgramTests(ConfigCase):
    def risks(self, text):
        report = inspect([self.config(text)])
        return [(r["rule"], r["entry"]) for r in report["risks"]], report

    def test_provider_auth_command_is_a_program_risk(self):
        got, report = self.risks(BASE + '[model_providers.corp.auth]\ncommand="private-export"\n')
        self.assertIn(("configured_program", "config-1:model_providers.corp"), got)
        self.assertEqual(report["inspection_gaps"],
                         ["config-1: Model-provider command-backed authentication is outside reader coverage."])

    def test_provider_auth_without_command_stays_a_gap(self):
        got, report = self.risks(BASE + '[model_providers.corp.auth]\nenvironment_id="local"\n')
        self.assertNotIn(("configured_program", "config-1:model_providers.corp"), got)
        self.assertEqual(report["inspection_gaps"],
                         ["config-1: Model-provider command-backed authentication is outside reader coverage."])

    def test_provider_aws_credential_commands_are_program_risks(self):
        got, report = self.risks(BASE + '[model_providers.amazon-bedrock.aws]\n'
                                   'credential_export.command="/usr/bin/export-aws"\nauth_refresh.command="aws"\n')
        self.assertIn(("configured_program", "config-1:model_providers.amazon-bedrock"), got)
        self.assertEqual(report["inspection_gaps"], [
            "config-1: Model-provider setting aws.auth_refresh was not checked for a credential command.",
            "config-1: Model-provider setting aws.credential_export was not checked for a credential command.",
        ])

    def test_provider_aws_credential_without_command_stays_a_gap(self):
        got, report = self.risks(BASE + '[model_providers.amazon-bedrock.aws]\nregion="us-east-1"\n'
                                   'credential_export={}\nauth_refresh={}\n')
        self.assertNotIn(("configured_program", "config-1:model_providers.amazon-bedrock"), got)
        self.assertEqual(report["inspection_gaps"], [
            "config-1: Model-provider setting aws.auth_refresh was not checked for a credential command.",
            "config-1: Model-provider setting aws.credential_export was not checked for a credential command.",
        ])

    def test_provider_program_finding_has_its_own_headline_and_advice(self):
        # Each sign-in table requires `command` and rejects unknown fields (openai/codex 086ccc8,
        # protocol/src/config_types.rs L570-L576; model-provider-info/src/lib.rs L238-L290), so the advice removes the
        # whole table rather than the `command` line, and names the AWS tables as well as `auth`.
        for table in ("auth", "aws.credential_export", "aws.auth_refresh"):
            with self.subTest(table=table):
                page = markdown(inspect([self.config(BASE + f'[model_providers.corp.{table}]\ncommand="private-export"\n')]))
                self.assertIn("**Your `corp` model provider can start a program on your computer.**", page)
                self.assertNotIn("Review this setting yourself", page)
                self.assertNotIn("See the cited incidents", page)
                self.assertIn("delete the `auth`, `aws.credential_export` or `aws.auth_refresh` table", page)
                self.assertNotIn("private-export", page)
