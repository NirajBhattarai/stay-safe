"""Model provider sign-in and AWS credential commands are programs the report flags."""

from stay_safe.report import inspect

BASE = 'approval_policy="on-request"\nsandbox_mode="read-only"\n'


def risks(text):
    report = inspect([text])
    return [(r["rule"], r["entry"]) for r in report["risks"]], report


def test_provider_auth_command_is_a_program_risk():
    text = BASE + '[model_providers.corp.auth]\ncommand="private-export"\n'
    got, report = risks(text)
    assert ("configured_program", "config-1:model_providers.corp") in got, got
    assert report["inspection_gaps"] == []


def test_provider_auth_without_command_stays_a_gap():
    text = BASE + '[model_providers.corp.auth]\nenvironment_id="local"\n'
    got, report = risks(text)
    assert ("configured_program", "config-1:model_providers.corp") not in got, got
    assert report["inspection_gaps"] == ["config-1: Model-provider command-backed authentication is outside reader coverage."]


def test_provider_aws_credential_commands_are_program_risks():
    text = (
        BASE
        + '[model_providers.amazon-bedrock.aws]\n'
        'credential_export.command="/usr/bin/export-aws"\n'
        'auth_refresh.command="aws"\n'
    )
    got, report = risks(text)
    assert ("configured_program", "config-1:model_providers.amazon-bedrock") in got, got
    assert report["inspection_gaps"] == []


def test_provider_aws_credential_without_command_stays_a_gap():
    text = BASE + '[model_providers.amazon-bedrock.aws]\nregion="us-east-1"\n'
    got, report = risks(text)
    assert ("configured_program", "config-1:model_providers.amazon-bedrock") not in got, got
    assert report["inspection_gaps"] == [
        "config-1: Model-provider setting aws.auth_refresh was not checked for a credential command.",
        "config-1: Model-provider setting aws.credential_export was not checked for a credential command.",
    ]
