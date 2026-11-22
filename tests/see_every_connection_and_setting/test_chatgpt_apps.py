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


if __name__ == "__main__":
    unittest.main()
