import unittest

from stay_safe.report import inspect, render
from tests.support import CHATGPT_APPS, ConfigCase

# Meaning and sources: harnesses/codex.md row `features.apps` `omitted`.
TOP = 'approval_policy="on-request"\nsandbox_mode="read-only"\n'


def connection(report):
    return [(e["id"], e["kind"], e["observations"]) for e in report["catalog"] if e["name"] == "features.apps"]


class ChatGptAppsTests(ConfigCase):
    def test_configuration_without_apps_false_names_the_chatgpt_apps_connection(self):
        for case, text in {"no features table": TOP, "empty features table": TOP + "[features]\n",
                           "apps = true": TOP + "[features]\napps=true\n"}.items():
            with self.subTest(case=case):
                report = inspect([self.config(text)])
                self.assertEqual(connection(report), [("config-1:features.apps", "MCP server", CHATGPT_APPS)])
                self.assertEqual(report["inspection_gaps"], [])
                self.assertEqual([r for r in report["risks"] if r["entry"] == "config-1:features.apps"], [])

    def test_absent_default_configuration_names_the_chatgpt_apps_connection(self):
        report = inspect([self.root / "missing.toml"], discovered=True)
        self.assertEqual(connection(report), [("config-1:features.apps", "MCP server", CHATGPT_APPS)])

    def test_apps_false_gives_no_chatgpt_apps_connection(self):
        report = inspect([self.config(TOP + "[features]\napps=false\n")])
        self.assertEqual(connection(report), [])
        self.assertNotIn("ChatGPT", render(report))
        self.assertEqual(report["inspection_gaps"], [])

    def test_chatgpt_apps_connection_says_whether_apps_not_named_can_change_data(self):
        # Issue #139: an app the file does not name follows apps._default, then Codex's default of true
        # (openai/codex 086ccc8, connectors/src/app_tool_policy.rs L174-L185 and L287-L294; config/src/types.rs
        # L471-L476 gives a template without the field true as well).
        base = CHATGPT_APPS[:3]
        for template, last in [
            ("", "apps not named in this file: destructive tools enabled by Codex default"),
            ('[apps._default]\ndefault_tools_approval_mode="prompt"\n',
             "apps not named in this file: destructive tools enabled by Codex default"),
            ("[apps._default]\ndestructive_enabled=false\n",
             "apps not named in this file: destructive tools disabled by apps._default.destructive_enabled"),
            ("[apps._default]\ndestructive_enabled=true\n",
             "apps not named in this file: destructive tools enabled by apps._default.destructive_enabled"),
            ("[apps._default]\nenabled=false\n", "apps not named in this file: disabled by apps._default.enabled"),
        ]:
            with self.subTest(template=template):
                report = inspect([self.config(TOP + template)])
                self.assertEqual(connection(report), [("config-1:features.apps", "MCP server", base + [last])])
                self.assertEqual([r for r in report["risks"] if r["entry"] == "config-1:features.apps"], [])
                self.assertIn("ChatGPT Apps connection", render(report))

    def test_invalid_template_leaves_apps_not_named_unknown_and_keeps_its_gap(self):
        # Review of #139: Codex's schema requires booleans and a table (config/src/types.rs at 086ccc8), so an
        # invalid value is not Codex's default. The row says unknown, and the invalid-value gap stays.
        base = CHATGPT_APPS[:3]
        for template, last, gap in [
            ('[apps._default]\ndestructive_enabled="yes"\n', "apps not named in this file: destructive tools unknown",
             "config-1: apps has an invalid destructive_enabled flag."),
            ('[apps._default]\nenabled="yes"\n', "apps not named in this file: settings unknown",
             "config-1: apps has an invalid boolean; its behavior is unknown."),
            ("[apps]\n_default=7\n", "apps not named in this file: settings unknown",
             "config-1: apps._default must be a table."),
            ("apps=7\n", "apps not named in this file: settings unknown", "config-1: apps must be a table."),
        ]:
            with self.subTest(template=template):
                report = inspect([self.config(TOP + template)])
                self.assertEqual(connection(report), [("config-1:features.apps", "MCP server", base + [last])])
                self.assertIn(gap, report["inspection_gaps"])
                self.assertNotIn("Codex default", render(report).split("ChatGPT Apps connection")[1].split("\n")[0])


if __name__ == "__main__":
    unittest.main()
