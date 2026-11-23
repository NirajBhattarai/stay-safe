"""Claude Code reports withhold commands, addresses and values in every format (issue #163)."""

import json

from tests.support import ConfigCase, ReportRuns

SETTINGS = {"permissions": {"defaultMode": "seed-mode-value", "allow": [
                "Bash(seed-command --token sk-seed-token)", "WebFetch(domain:seed-host.example)",
                "mcp__seed_server__seed_tool"], "deny": ["Bash(seed-denied)"],
                            "additionalDirectories": ["/seed-path"]},
            "sandbox": {"enabled": True, "network": {"allowedDomains": ["seed-domain.example"]}},
            "env": {"SEED_TOKEN": "seed-env-value"}, "apiKeyHelper": "seed-helper", "seed-key": "seed-value"}


class ClaudeReportSecretsTests(ConfigCase, ReportRuns):
    def test_claude_code_report_excludes_private_values(self):
        path = self.config(json.dumps(SETTINGS), "settings.json")
        for format_args in ((), ("--format", "json")):
            with self.subTest(format=format_args):
                run = self.run_cli("--agent", "claude", "--config", str(path), *format_args)
                self.assertEqual(run.returncode, 2)
                self.assertNotIn("seed", (run.stdout + run.stderr).lower())
                self.assertNotIn("sk-", run.stdout)
