import io
import json
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from stay_safe.cli import main

from tests.support import ConfigCase, REPORT, copy_checkout, run_checkout

SETTINGS = {"permissions": {"defaultMode": "seed-mode-value", "allow": [
                "Bash(seed-command --token sk-seed-token)", "WebFetch(domain:seed-host.example)",
                "mcp__seed_server__seed_tool"], "deny": ["Bash(seed-denied)"],
                            "additionalDirectories": ["/seed-path"]},
            "sandbox": {"enabled": True, "network": {"allowedDomains": ["seed-domain.example"]}},
            "env": {"SEED_TOKEN": "seed-env-value"}, "apiKeyHelper": "seed-helper", "seed-key": "seed-value"}


class ClaudeReportSecretsTests(ConfigCase):
    def test_claude_code_report_excludes_private_values(self):
        path = self.config(json.dumps(SETTINGS), "settings.json")
        checkout = copy_checkout(self.root / "checkout")
        args = ("--agent", "claude", "--config", str(path))
        for flags in (("--format", "json"), ("--format", "markdown"), ("--save",)):
            with self.subTest(flags=flags):
                run = run_checkout(checkout, *args, *flags, cwd=checkout)
                self.assertEqual(run.returncode, 2)
                self.assertIn("Claude Code", run.stdout)
                content = run.stdout + run.stderr
                if flags == ("--save",):
                    html = (checkout / REPORT).read_text()
                    self.assertIn("Claude Code finding 1", html)
                    content += html
                self.assertNotIn("seed", content.lower())
        terminal = io.StringIO()
        with patch.object(terminal, "isatty", return_value=True), redirect_stdout(terminal), \
             redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(main(args), 2)
        self.assertIn("Claude Code finding 1", terminal.getvalue())
        self.assertNotIn("seed", (terminal.getvalue() + errors.getvalue()).lower())
