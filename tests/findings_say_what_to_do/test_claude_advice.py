"""Each Claude Code finding says what to change, where, and how to check (issue #163).

The advice follows the Claude Code docs: `default` "Prompts before most edits, shell commands, and network requests"
(https://code.claude.com/docs/en/permissions, "Permission modes"); `WebFetch(domain:example.com)` "Matches fetch
requests to example.com" (same page, "Use specifiers for fine-grained control"); a `--permission-mode` flag and managed
settings take precedence over user settings (https://code.claude.com/docs/en/permission-modes, "Which mode a session
starts in"; https://code.claude.com/docs/en/settings, "Settings precedence").
"""

import re

from tests.support import ConfigCase, agent_home, items, run_home, section

SETTINGS = ('{"permissions": {"defaultMode": "bypassPermissions", "allow": ["Bash(*)", "Bash(git push:*)", '
            '"WebFetch(domain:seed-host.example)"]}, "sandbox": {"enabled": true}}')


class ClaudeAdviceTests(ConfigCase):
    def test_each_claude_code_finding_says_what_to_change_where_and_how_to_check(self):
        home = agent_home(self.root, claude=SETTINGS)
        run = run_home(home, "--agent", "claude")
        self.assertEqual(run.returncode, 0, run.stderr)
        found = items(section(run.stdout, "Claude Code findings").split("\n\n", 1)[1])
        steps = [[p for p in item.split("\n\n") if p.startswith(("*What to do:*", "*Change it:*", "*Check:*"))]
                 for item in found]
        self.assertEqual(steps, [
            ["*What to do:* Set `permissions.defaultMode` to `default`, so Claude Code asks before most edits, shell "
             "commands and network requests. Commands your allow rules match still run without asking.",
             "*Change it:* `permissions.defaultMode` in `~/.claude/settings.json`, or ask Claude Code: \"Edit "
             "`~/.claude/settings.json` to set `permissions.defaultMode` to `default`; show only what you change.\"",
             "*Check:* Look for `defaultMode` under `permissions` in `~/.claude/settings.json`. A `--permission-mode` "
             "flag or managed settings can still choose another mode."],
            ["*What to do:* Remove this rule and allow only the commands you run often, for example "
             "`Bash(npm run test *)`.",
             "*Change it:* rule 1 of `permissions.allow` in `~/.claude/settings.json`, or ask Claude Code: \"Show me "
             "rule 1 of `permissions.allow` in `~/.claude/settings.json` and remove it; show only what you change.\"",
             "*Check:* Look at `permissions.allow` in `~/.claude/settings.json`."],
            ["*What to do:* Check that this rule covers only the commands you meant, and remove it if you no longer "
             "need it.",
             "*Change it:* rule 2 of `permissions.allow` in `~/.claude/settings.json`, or ask Claude Code: \"Show me "
             "rule 2 of `permissions.allow` in `~/.claude/settings.json` and remove it; show only what you change.\"",
             "*Check:* Look at `permissions.allow` in `~/.claude/settings.json`."],
            ["*What to do:* Check that you trust every page on that domain, and remove the rule if you no longer need it.",
             "*Change it:* rule 3 of `permissions.allow` in `~/.claude/settings.json`, or ask Claude Code: \"Show me "
             "rule 3 of `permissions.allow` in `~/.claude/settings.json` and remove it; show only what you change.\"",
             "*Check:* Look at `permissions.allow` in `~/.claude/settings.json`."],
        ])
        self.assertNotIn("seed-host", run.stdout)
        self.assertTrue(all(re.match(r"### Claude Code finding \d+\n\n", item) for item in found))
