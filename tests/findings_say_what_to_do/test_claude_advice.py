"""Each Claude Code finding says what to change, where, and how to check (issue #163).

The advice follows the Claude Code docs: `default` "Prompts before most edits, shell commands, and network requests"
(https://code.claude.com/docs/en/permissions, "Permission modes"); `WebFetch(domain:example.com)` "Matches fetch
requests to example.com" (same page, "Use specifiers for fine-grained control"); a `--permission-mode` flag and managed
settings take precedence over user settings (https://code.claude.com/docs/en/permission-modes, "Which mode a session
starts in"; https://code.claude.com/docs/en/settings, "Settings precedence").
"""

import json
import re

from tests.support import ConfigCase, agent_home, items, run_home, section

SETTINGS = ('{"permissions": {"defaultMode": "bypassPermissions", "allow": ["Bash(*)", "Bash(git push:*)", '
            '"WebFetch(domain:seed-host.example)"]}, "sandbox": {"enabled": false}}')


class ClaudeAdviceTests(ConfigCase):
    def test_each_claude_code_finding_says_what_to_change_where_and_how_to_check(self):
        home = agent_home(self.root, claude=SETTINGS)
        run = run_home(home, "--agent", "claude")
        self.assertEqual(run.returncode, 0, run.stderr)
        found = items(section(run.stdout, "Claude Code findings").split("\n\n", 1)[1])
        steps = [[p for p in item.split("\n\n") if p.startswith(("*What to do:*", "*Change it:*", "*Check:*"))]
                 for item in found]
        self.assertEqual(steps, [
            ["*What to do:* Set `permissions.defaultMode` to `default` to leave bypass mode. Review any separate allow "
             "rules for actions you want to approve yourself.",
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
            ["*What to do:* Check that you trust the domains this rule covers, and remove the rule if you no longer need it.",
             "*Change it:* rule 3 of `permissions.allow` in `~/.claude/settings.json`, or ask Claude Code: \"Show me "
             "rule 3 of `permissions.allow` in `~/.claude/settings.json` and remove it; show only what you change.\"",
             "*Check:* Look at `permissions.allow` in `~/.claude/settings.json`."],
        ])
        self.assertNotIn("seed-host", run.stdout)
        self.assertTrue(all(re.match(r"### Claude Code finding \d+\n\n", item) for item in found))

    def test_all_domain_rule_gets_broad_advice_and_distinct_evidence(self):
        home = agent_home(self.root)
        for rule, scope in (("WebFetch", "every address"), ("WebFetch(domain:*)", "every domain"),
                            ("WebFetch(domain:private.example)", "addresses withheld")):
            with self.subTest(rule=rule):
                path = self.config(json.dumps({"permissions": {"defaultMode": "default", "allow": [rule]}}))
                args = ("--agent", "claude", "--config", str(path))
                report = json.loads(run_home(home, *args, "--format", "json").stdout)
                risk, = report["risks"]
                self.assertIn(scope, risk["configured_evidence"])
                text = run_home(home, *args).stdout
                finding = section(text, "Claude Code findings")
                advice = next(p for p in finding.split("\n\n") if p.startswith("*What to do:*"))
                if rule == "WebFetch":
                    self.assertIn("Remove", advice)
                    self.assertNotIn("domain:", advice)
                elif rule == "WebFetch(domain:*)":
                    self.assertIn("Remove", advice)
                    self.assertNotIn("limit it to", advice)
                    self.assertNotIn("domain:", advice)
                    for version in ("v2.1.172", "v2.1.186"):
                        self.assertIn(version, risk["explanation"])
                    self.assertIn(risk["explanation"], finding)
                else:
                    self.assertIn("trust", advice)
                self.assertNotIn("private.example", text)

    def test_switching_mode_explains_the_sandbox_approval_left_in_each_file(self):
        # https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/settings-reference.md#L1359-L1368
        home = agent_home(self.root)
        args = ["--agent", "claude"]
        paths = []
        for i, sandbox in enumerate(({"enabled": True, "autoAllowBashIfSandboxed": True},
                                     {"enabled": True, "autoAllowBashIfSandboxed": False},
                                     {"enabled": True}, {"enabled": False, "autoAllowBashIfSandboxed": True},
                                     {"enabled": True, "autoAllowBashIfSandboxed": "bad"})):
            path = self.config(json.dumps({"permissions": {"defaultMode": "bypassPermissions"}, "sandbox": sandbox}),
                               f"selected-{i}.json")
            args.extend(("--config", str(path)))
            paths.append(path)
        report = run_home(home, *args)
        self.assertEqual(report.returncode, 2)  # The third file omits auto-approval and the fifth has an invalid value.
        findings = items(section(report.stdout, "Claude Code findings").split("\n\n", 1)[1])
        self.assertEqual(len(findings), 5)
        self.assertIn("autoAllowBashIfSandboxed", findings[0])
        self.assertIn("without a prompt", findings[0])
        self.assertNotIn("autoAllowBashIfSandboxed", findings[1])
        self.assertIn("v2.1.324", findings[2])
        self.assertNotIn("autoAllowBashIfSandboxed", findings[3])
        self.assertIn("autoAllowBashIfSandboxed", findings[4])
        self.assertIn("invalid", findings[4])
        self.assertNotIn("v2.1.324", findings[4])
        encoded = json.loads(run_home(home, *args, "--format", "json").stdout)
        for i, (finding, risk) in enumerate(zip(findings, encoded["risks"], strict=True)):
            self.assertIn(f"<settings-{i + 1}>", finding)
            self.assertIn(risk["explanation"], finding)
        # Apply the mode edit. The same file still explicitly selects sandbox auto-approval.
        selected = json.loads(paths[0].read_text())
        selected["permissions"]["defaultMode"] = "default"
        paths[0].write_text(json.dumps(selected))
        after = json.loads(run_home(home, "--agent", "claude", "--config", str(paths[0]), "--format", "json").stdout)
        self.assertEqual(after["risks"], [])
        self.assertIn(("sandbox.autoAllowBashIfSandboxed", ["true"]),
                      [(e["name"], e["observations"]) for e in after["catalog"]])

    def test_auto_mode_advice_identifies_bash_auto_approval_that_survives_the_edit(self):
        # https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/settings-reference.md#L1359-L1368
        home = agent_home(self.root)
        settings = {"permissions": {"defaultMode": "auto"},
                    "sandbox": {"enabled": True, "autoAllowBashIfSandboxed": True}}
        enabled = self.config(json.dumps(settings), "enabled.json")
        regular = {**settings, "sandbox": {"enabled": True, "autoAllowBashIfSandboxed": False}}
        disabled = self.config(json.dumps(regular), "disabled.json")
        args = ("--agent", "claude", "--config", str(enabled))
        before = run_home(home, *args, "--config", str(disabled))
        self.assertEqual(before.returncode, 2, before.stderr)
        warning, control = items(section(before.stdout, "Claude Code not checked").split("\n\n", 1)[1])
        self.assertIn("Not checked: auto mode", warning)
        self.assertIn("*File `settings-1`*", warning)
        self.assertIn("`permissions.defaultMode` to `default`", warning)
        self.assertIn("sandbox.autoAllowBashIfSandboxed", warning)
        self.assertIn("eligible sandboxed Bash commands can still run without a prompt", warning)
        self.assertIn("false", warning)
        self.assertIn("regular permission checks", warning)
        self.assertIn("Not checked: auto mode", control)
        self.assertIn("*File `settings-2`*", control)
        self.assertNotIn("without a prompt", control)

        settings["permissions"]["defaultMode"] = "default"
        enabled.write_text(json.dumps(settings))
        after = run_home(home, *args, "--format", "json")
        self.assertEqual(after.returncode, 0, after.stderr)
        report = json.loads(after.stdout)
        self.assertEqual(report["risks"], [])
        self.assertEqual(report["inspection_gaps"], [])
        self.assertIn(("sandbox.autoAllowBashIfSandboxed", ["true"]),
                      [(entry["name"], entry["observations"]) for entry in report["catalog"]])
