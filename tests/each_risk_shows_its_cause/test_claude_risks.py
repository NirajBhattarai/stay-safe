"""Each Claude Code warning names its rule, setting and incidents (issue #163).

Which settings carry which risk follows harnesses/claude-code.md: `bypassPermissions` "Skips permission prompts"
(https://code.claude.com/docs/en/permissions, "Permission modes"), and an allow rule lets matching calls run without
a prompt (same page, "Manage permissions"). Incident IDs are the rules' own, in stay_safe/rules.py.
"""

import json

import re

from tests.support import ConfigCase, ReportRuns, items, section, without_rule_links

SETTINGS = {"permissions": {"defaultMode": "bypassPermissions", "allow": ["Bash", "Bash(git push:*)", "WebFetch"]},
            "sandbox": {"enabled": True}}


class ClaudeRiskTests(ConfigCase, ReportRuns):
    def test_each_claude_code_warning_names_its_rule_setting_and_incidents(self):
        path = self.config(json.dumps(SETTINGS), "settings.json")
        run = self.run_cli("--agent", "claude", "--config", str(path), "--format", "json")
        self.assertEqual((run.returncode, run.stderr), (0, ""))
        report = json.loads(run.stdout)
        self.assertEqual([(risk["rule"], risk["entry"], risk["incidents"], risk["configured_evidence"])
                          for risk in report["risks"]], [
            ("commands_without_prompts", "settings-1:permissions.defaultMode", ["I2", "I3", "I24"],
             ["bypassPermissions"]),
            ("saved_approval", "settings-1:permissions.allow.1", ["I26", "I30"], ["tool: Bash", "broad: every command"]),
            ("saved_approval", "settings-1:permissions.allow.2", ["I26", "I30"], ["tool: Bash", "program: git"]),
            ("network_access", "settings-1:permissions.allow.3", ["I15", "I21"], ["tool: WebFetch", "every address"]),
        ])
        self.assertTrue(all(risk["interpretation_source"] is None or
                            risk["interpretation_source"].endswith("/harnesses/claude-code.md") for risk in report["risks"]))

        run = self.run_cli("--agent", "claude", "--config", str(path))
        text = without_rule_links(run.stdout)
        found = items(section(text, "Claude Code findings").split("\n\n", 1)[1])
        self.assertTrue(all(re.match(r"### Claude Code finding \d+\n\n", item) for item in found))
        heads = [item.split("\n\n")[1].split("** ", 1)[0] + "**" for item in found]
        self.assertEqual(heads, [
            "**With these settings, Claude Code runs commands and edits files without asking you.**",
            "**An allow rule lets Claude Code run every shell command without asking you.**",
            "**An allow rule lets Claude Code run matching shell commands without asking you.**",
            "**An allow rule lets Claude Code fetch any web address without asking you.**",
        ])
        for rule, setting in (("commands_without_prompts", "settings-1:permissions.defaultMode"),
                              ("saved_approval", "settings-1:permissions.allow.2"),
                              ("network_access", "settings-1:permissions.allow.3")):
            self.assertIn(f"*Rule `{rule}` · setting `{setting}`", text)
