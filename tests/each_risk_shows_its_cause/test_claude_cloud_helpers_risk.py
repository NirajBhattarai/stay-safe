import json

from tests.support import ConfigCase, agent_home, run_home

USER = {"permissions": {"defaultMode": "default"}}
PROJECT = {"awsAuthRefresh": "seed-aws-sso", "awsCredentialExport": "seed-aws-export", "gcpAuthRefresh": "seed-gcloud", "otelHeadersHelper": "/seed/otel-headers"}
RISKS = [
    ["settings-2:awsAuthRefresh", "This file's `awsAuthRefresh` setting runs a command on your computer. Claude Code runs it from a project's settings in a `claude -p` run, or when you trusted a parent folder whose trust extends to this folder, without asking you to trust this folder."],
    ["settings-2:awsCredentialExport", "This file's `awsCredentialExport` setting runs a command on your computer. Claude Code runs it from a project's settings in a `claude -p` run, or when you trusted a parent folder whose trust extends to this folder, without asking you to trust this folder."],
    ["settings-2:gcpAuthRefresh", "This file's `gcpAuthRefresh` setting runs a command on your computer. Claude Code runs it from a project's settings in a `claude -p` run, or when you trusted a parent folder whose trust extends to this folder, without asking you to trust this folder."],
    ["settings-2:otelHeadersHelper", "This file's `otelHeadersHelper` setting runs a command on your computer. Claude Code runs it from a project's settings in a `claude -p` run, or when you trusted a parent folder whose trust extends to this folder, without asking you to trust this folder."],
]
MARKDOWN = [
    "*Change it:* `awsAuthRefresh` in `.claude/settings.json`",
    "*Check:* In `.claude/settings.json`, `awsAuthRefresh` holds the command it runs. If it runs a script file, check that file too. Find out who wrote it before you trust it. In a git repository, `git log -p -- .claude/` shows who changed the settings and scripts there.",
]


class ClaudeCloudHelpersRiskTests(ConfigCase):
    def test_cloud_helpers_finding_names_its_file_and_withholds_the_command(self):
        home = agent_home(self.root, claude=json.dumps(USER))
        project = self.root / "repo"
        (project / ".claude").mkdir(parents=True)
        (project / ".claude" / "settings.json").write_text(json.dumps(PROJECT), encoding="utf-8")
        run = run_home(home, "--agent", "claude", "--format", "json", cwd=project)
        report = json.loads(run.stdout)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertCountEqual([[risk["entry"], risk["explanation"]] for risk in report["risks"]], RISKS)
        self.assertEqual({risk["rule"] for risk in report["risks"]}, {"configured_program"})
        markdown = run_home(home, "--agent", "claude", cwd=project).stdout
        for line in MARKDOWN:
            self.assertIn(line, markdown)
        self.assertNotIn("seed", (run.stdout + markdown).lower())
