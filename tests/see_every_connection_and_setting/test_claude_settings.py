"""The Claude Code reader's catalog and gaps, against the meanings in harnesses/claude-code.md (issue #163).

Expected meanings come from the Claude Code docs, not the reader:
- Modes: https://code.claude.com/docs/en/permissions, "Permission modes" (`default`, `acceptEdits`, `plan`, `auto`,
  `dontAsk`, `bypassPermissions`); https://code.claude.com/docs/en/permission-modes, "Available modes" (`manual` is an
  alias for `default`) and "Which mode a session starts in" (the built-in default depends on the surface and version).
- Rules: https://code.claude.com/docs/en/permissions, "Match all uses of a tool" (`Bash`, `WebFetch`), "`Bash(*)` is
  equivalent to `Bash`", "Wildcard patterns" (`Bash(ls:*)` matches the same commands as `Bash(ls *)`), and "Manage
  permissions" (deny, then ask, then allow; the first match decides).
- Sandbox: https://code.claude.com/docs/en/sandboxing, "The sandbox is off by default".
- ~/.claude.json: https://code.claude.com/docs/en/settings, "It holds your account details, MCP server
  configurations, per-project state such as trust decisions".
"""

import json
import os
from unittest.mock import patch

from tests.support import ConfigCase


def read_file(*args, **kwargs):
    # Imported when called, so on a base without the reader each test fails on its missing behavior.
    from stay_safe import claude
    return claude.read_file(*args, **kwargs)


def claude_gaps(*args, **kwargs):
    from stay_safe import cli
    return cli.claude_gaps(*args, **kwargs)

ALLOW = ["Bash", "Bash(*)", "Bash(git push:*)", "Bash(seed-private-command --token sk-seed)",
         "WebFetch", "WebFetch(domain:seed-private-host.example)"]


class ClaudeSettingsTests(ConfigCase):
    def read(self, settings, discovered=False):
        path = self.config(json.dumps(settings) if not isinstance(settings, str) else settings, "settings.json")
        return read_file(path, "settings-1", discovered=discovered)

    def catalog(self, entries):
        return {entry["name"]: (entry["observations"], {k for k, v in entry["facts"].items() if v}) for entry in entries}

    def test_each_permission_mode_is_listed_and_only_bypass_runs_without_asking(self):
        for mode in ("default", "manual", "acceptEdits", "plan", "dontAsk", "bypassPermissions", "auto"):
            with self.subTest(mode=mode):
                entries, gaps = self.read({"permissions": {"defaultMode": mode}, "sandbox": {"enabled": True}})
                facts = {"commands_without_prompts"} if mode == "bypassPermissions" else set()
                self.assertEqual(self.catalog(entries)["permissions.defaultMode"], ([mode], facts))
                self.assertEqual(gaps, ["settings-1: permissions.defaultMode is auto; a classifier decides which "
                                        "actions run without asking, and its decisions are not assessed."]
                                 if mode == "auto" else [])

    def test_absent_and_invalid_modes_are_gaps_not_guesses(self):
        absent = ("settings-1: permissions.defaultMode is absent; Claude Code's built-in mode depends on how it "
                  "starts and its version, so it was not inferred.")
        invalid = "settings-1: permissions.defaultMode is unsupported or invalid; its value was withheld."
        for settings, gap in (({}, absent), ({"permissions": {}}, absent),
                              ({"permissions": {"defaultMode": "yolo"}}, invalid),
                              ({"permissions": {"defaultMode": True}}, invalid)):
            with self.subTest(settings=settings):
                entries, gaps = self.read(settings)
                self.assertNotIn("permissions.defaultMode", self.catalog(entries))
                self.assertEqual(gaps, [gap])

    def test_allow_rules_for_shell_commands_and_web_fetches(self):
        entries, gaps = self.read({"permissions": {"defaultMode": "default", "allow": ALLOW + ["Read(./src/**)"]},
                                   "sandbox": {"enabled": False}})
        catalog = self.catalog(entries)
        self.assertEqual([catalog[f"permissions.allow.{n}"] for n in range(1, 7)], [
            (["tool: Bash", "broad: every command"], {"saved_approval"}),
            (["tool: Bash", "broad: every command"], {"saved_approval"}),
            (["tool: Bash", "program: git"], {"saved_approval"}),
            (["tool: Bash"], {"saved_approval"}),
            (["tool: WebFetch", "every address"], {"network_access"}),
            (["tool: WebFetch", "addresses withheld"], {"network_access"}),
        ])
        self.assertNotIn("permissions.allow.7", catalog)
        self.assertEqual(catalog["sandbox.enabled"], (["false"], set()))
        self.assertEqual(gaps, ["settings-1: permissions.allow contains rules for tools outside reader coverage; "
                                "they were not evaluated."])

    def test_ask_and_deny_rules_and_uncovered_settings_are_gaps(self):
        entries, gaps = self.read({"permissions": {"defaultMode": "plan", "allow": ["Bash"], "deny": ["Bash(rm *)"],
                                                   "additionalDirectories": ["/seed-private-path"]},
                                   "hooks": {"PreToolUse": []}, "env": {"TOKEN": "seed-secret"},
                                   "seed-private-key": 1, "theme": "dark", "model": "opus"})
        self.assertEqual(self.catalog(entries)["sandbox.enabled"], (["false (default)"], set()))
        self.assertEqual(gaps, sorted([
            "settings-1: permissions contains fields outside reader coverage; their values were withheld.",
            "settings-1: permissions.ask or permissions.deny contains rules; Claude Code checks them before allow "
            "rules, and they were not inspected.",
            "settings-1: Settings outside reader coverage were not evaluated: env, hooks and other fields whose "
            "names were withheld.",
        ]))
        self.assertNotIn("seed-", json.dumps([entries, gaps]))

    def test_unreadable_files_give_a_gap_and_no_entries(self):
        bad = ("settings-1: Settings file is missing, unreadable, a symlink, or not a JSON object; "
               "raw errors were withheld.")
        for text in ("{not json", "[]", '"text"'):
            with self.subTest(text=text):
                self.assertEqual(self.read(text), ([], [bad]))
        link = self.root / "link.json"
        link.symlink_to(self.config("{}", "target.json"))
        self.assertEqual(read_file(link, "settings-1"), ([], [bad]))
        self.assertEqual(read_file(self.root / "missing.json", "settings-1"), ([], [bad]))
        entries, gaps = read_file(self.root / "missing.json", "settings-1", discovered=True)
        self.assertEqual(self.catalog(entries)["settings"], (["absent"], set()))

    def test_folder_contents_claude_code_loads_are_named_without_their_contents(self):
        home = self.root / "home"
        claude = home / ".claude"
        for name in ("skills/seed-skill", "plugins/seed-plugin", "agents", "commands"):
            (claude / name).mkdir(parents=True)
        (claude / "agents" / "seed-agent.md").write_text("seed", encoding="utf-8")
        (claude / "remote-settings.json").write_text("{}", encoding="utf-8")
        (home / ".claude.json").write_text('{"oauthAccount": "seed-account"}', encoding="utf-8")
        with patch.dict(os.environ, {"HOME": str(home)}, clear=True):
            gaps = claude_gaps(claude, managed=[self.root / "no-managed-folder"])
        self.assertEqual(gaps, [
            "Claude Code home: ~/.claude.json exists and was not inspected; it holds MCP servers and per-project "
            "trust decisions.",
            "Claude Code home: remote-settings.json exists; settings your organization manages remotely were not "
            "inspected.",
            "Claude Code home: agents holds items that were not inspected.",
            "Claude Code home: plugins holds items that were not inspected.",
            "Claude Code home: skills holds items that were not inspected.",
        ])
        managed = self.root / "managed"
        managed.mkdir()
        (managed / "managed-settings.json").write_text("{}", encoding="utf-8")
        with patch.dict(os.environ, {"HOME": str(self.root / "empty")}, clear=True):
            self.assertEqual(claude_gaps(self.root / "empty", managed=[managed]),
                             ["Managed settings: a Claude Code managed settings file exists and was not inspected."])
