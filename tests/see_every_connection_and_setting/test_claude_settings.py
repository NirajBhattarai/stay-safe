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

from tests.support import ConfigCase


def read_file(*args, **kwargs):
    # Imported when called, so on a base without the reader each test fails on its missing behavior.
    from stay_safe import claude
    return claude.read_file(*args, **kwargs)


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
                entries, gaps = self.read({"permissions": {"defaultMode": mode}, "sandbox": {"enabled": False}})
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
                              ({"permissions": {"defaultMode": True}}, invalid),
                              ({"permissions": {"defaultMode": None}}, invalid)):
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
            "settings-1: permissions.deny contains rules that can take precedence over allow. Their matches were not checked.",
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
        # Claude settings use strict JSON. Python's decoder otherwise accepts these three constants.
        # https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/settings.md#L132
        template = '{"permissions":{"defaultMode":"default","allow":["Bash"]},"cleanupPeriodDays":%s}'
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                self.assertEqual(self.read(template % token), ([], [bad]))
        self.assertEqual(self.read('{"permissions":{"allow":[NaN]}}'), ([], [bad]))
        entries, gaps = self.read(template % "30")
        self.assertEqual(gaps, [])
        self.assertIn("permissions.allow.1", self.catalog(entries))
        link = self.root / "link.json"
        link.symlink_to(self.config("{}", "target.json"))
        self.assertEqual(read_file(link, "settings-1"), ([], [bad]))
        self.assertEqual(read_file(self.root / "missing.json", "settings-1"), ([], [bad]))
        entries, gaps = read_file(self.root / "missing.json", "settings-1", discovered=True)
        self.assertEqual(self.catalog(entries)["settings"], (["absent"], set()))


    def test_malformed_permission_lists_and_sandbox_fields_name_the_field(self):
        for group, key, value in (("permissions", "ask", False), ("permissions", "deny", {}),
                                  ("permissions", "ask", [None]), ("sandbox", "enabled", None)):
            with self.subTest(key=key, value=value):
                settings = {"permissions": {"defaultMode": "default"}, "sandbox": {}}
                settings[group][key] = value
                entries, gaps = self.read(settings)
                self.assertEqual(len(gaps), 1)
                self.assertIn(f"{group}.{key}", gaps[0])
                self.assertNotIn(f"{group}.{key}", self.catalog(entries))

    def test_sandbox_approval_is_version_dependent_only_when_enabled_and_unset(self):
        for value in (None, True, False):
            with self.subTest(value=value):
                sandbox = {"enabled": True}
                if value is not None:
                    sandbox["autoAllowBashIfSandboxed"] = value
                entries, gaps = self.read({"permissions": {"defaultMode": "default"}, "sandbox": sandbox})
                self.assertEqual(self.catalog(entries)["sandbox.enabled"], (["true"], set()))
                if value is None:
                    self.assertEqual(len(gaps), 1)
                    self.assertIn("v2.1.324", gaps[0])
                    self.assertIn("sandbox.autoAllowBashIfSandboxed", gaps[0])
                else:
                    self.assertEqual(gaps, [])
                    self.assertEqual(self.catalog(entries)["sandbox.autoAllowBashIfSandboxed"],
                                     ([str(value).lower()], set()))

    def test_ask_only_rules_name_the_unchecked_list_without_a_finding(self):
        entries, gaps = self.read({"permissions": {"defaultMode": "default", "ask": ["Bash(git status)"]}})
        self.assertFalse(any(any(entry["facts"].values()) for entry in entries))
        self.assertEqual(gaps, ["settings-1: permissions.ask contains rules that can take precedence over allow. "
                                "Their matches were not checked."])
