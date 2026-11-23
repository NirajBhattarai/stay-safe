"""Each tool-approval or destructive-tool risk appears once, on the entry that sets or inherits it.

Expected placement: archived issue #51 and ../../harnesses/codex.md. A tool block without its
own approval_mode uses its server's or app's mode, and `apps._default` deserializes
into Codex's separate AppsDefaultConfig ("Default settings that apply to all apps"),
not into the map of named apps:
https://github.com/openai/codex/blob/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/config/src/types.rs
"""

from stay_safe.report import inspect
from tests.support import ConfigCase


BASE = 'approval_policy="on-request"\nsandbox_mode="read-only"\n'
TOOL_RULES = {"automatic_tools", "destructive_tools", "self_described_tools"}


class SingleAttributionTests(ConfigCase):
    def assert_tool_risks(self, tail, expected):
        report = inspect([self.config(BASE + tail)])
        self.assertEqual(sorted((r["rule"], r["entry"]) for r in report["risks"] if r["rule"] in TOOL_RULES),
                         sorted((rule, "config-1:" + entry) for rule, entry in expected))
        self.assertEqual(report["inspection_gaps"], [])
        return report

    def test_inherited_mode_is_reported_on_the_server_or_app_only(self):
        for tail, expected in [
            ('[mcp_servers.r]\ncommand="x"\n[mcp_servers.r.tools.read]\noutput_token_limit=5',
             [("self_described_tools", "mcp_servers.r")]),
            ('[mcp_servers.r]\nurl="https://example.com"\ndefault_tools_approval_mode="approve"\n'
             '[mcp_servers.r.tools.read]\noutput_token_limit=5\n[mcp_servers.r.tools.write]\noutput_token_limit=5',
             [("automatic_tools", "mcp_servers.r")]),
            ('[mcp_servers.r]\nurl="https://example.com"\ndefault_tools_approval_mode="writes"\n'
             'enabled_tools=["read"]\n[mcp_servers.r.tools.read]\noutput_token_limit=5',
             [("self_described_tools", "mcp_servers.r")]),
            # A tool's own enabled = true also lets it run if destructive (archived issue #63).
            ('[apps.files]\ndefault_tools_approval_mode="approve"\n[apps.files.tools.read]\nenabled=true',
             [("automatic_tools", "apps.files"), ("destructive_tools", "apps.files"), ("destructive_tools", "apps.files.tools.read")]),
            ('[apps.files]\n[apps.files.tools.read]\nenabled=true',
             [("self_described_tools", "apps.files"), ("destructive_tools", "apps.files"), ("destructive_tools", "apps.files.tools.read")]),
            ('[apps.files]\ndefault_tools_enabled=false\ndefault_tools_approval_mode="approve"\n'
             '[apps.files.tools.read]\nenabled=true\n[apps.files.tools.write]',
             [("automatic_tools", "apps.files"), ("destructive_tools", "apps.files.tools.read")]),
            ('[apps._default]\ndefault_tools_approval_mode="approve"\n[apps.files]\n[apps.files.tools.read]\nenabled=true',
             [("automatic_tools", "apps._default"), ("automatic_tools", "apps.files"), ("destructive_tools", "apps.files"), ("destructive_tools", "apps.files.tools.read")]),
        ]:
            with self.subTest(tail=tail):
                self.assert_tool_risks(tail, expected)

    def test_tool_that_sets_its_own_mode_is_reported_on_the_tool_only(self):
        approve = ["configured enabled", "tool approval: approve"]
        for tail, expected, observations in [
            ('[mcp_servers.r]\nurl="https://example.com"\ndefault_tools_approval_mode="prompt"\n'
             '[mcp_servers.r.tools.write]\napproval_mode="approve"\n[mcp_servers.r.tools.read]\noutput_token_limit=5',
             [("automatic_tools", "mcp_servers.r.tools.write")], approve),
            ('[apps.files]\ndefault_tools_approval_mode="prompt"\n'
             '[apps.files.tools.write]\napproval_mode="approve"\n[apps.files.tools.read]\nenabled=true',
             [("automatic_tools", "apps.files.tools.write"), ("destructive_tools", "apps.files"),
              ("destructive_tools", "apps.files.tools.read")], approve),
            ('[mcp_servers.r]\nurl="https://example.com"\ndefault_tools_approval_mode="approve"\nenabled_tools=["write"]\n'
             '[mcp_servers.r.tools.write]\napproval_mode="approve"',
             [("automatic_tools", "mcp_servers.r.tools.write")], approve),
            ('[apps.files]\ndefault_tools_enabled=false\ndefault_tools_approval_mode="approve"\n'
             '[apps.files.tools.write]\nenabled=true\napproval_mode="approve"',
             [("automatic_tools", "apps.files.tools.write"), ("destructive_tools", "apps.files.tools.write")],
             ["configured enabled", "enabled even if destructive", "tool approval: approve"]),
        ]:
            with self.subTest(tail=tail):
                report = self.assert_tool_risks(tail, expected)
                tool = expected[0][1]
                self.assertEqual([e["observations"] for e in report["catalog"] if e["name"] == tool], [observations])

    def test_tool_entries_keep_their_observations_without_inherited_risks(self):
        report = self.assert_tool_risks(
            '[mcp_servers.r]\ncommand="x"\ndefault_tools_approval_mode="approve"\n[mcp_servers.r.tools.read]\noutput_token_limit=5',
            [("automatic_tools", "mcp_servers.r")])
        self.assertEqual([e["observations"] for e in report["catalog"] if e["name"] == "mcp_servers.r.tools.read"],
                         [["configured enabled", "tool approval: approve"]])

    def test_app_template_approval_applies_to_unnamed_apps_and_inherited_risks_to_enabled_named_apps(self):
        # Codex gives an app the file does not name the template's approval mode and destructive_enabled
        # (openai/codex 086ccc8, connectors/src/app_tool_policy.rs L263-L270 and L287-L294), so the template
        # carries those risks once; a named app that inherits them carries its own.
        template = '[apps._default]\ndefault_tools_approval_mode="approve"\ndestructive_enabled=true\n'
        unnamed = [("automatic_tools", "apps._default"), ("destructive_tools", "apps._default")]
        for tail, expected in [
            ('', []),
            ('[apps.files]', [("automatic_tools", "apps.files"), ("destructive_tools", "apps.files")]),
            ('[apps.files]\ndefault_tools_approval_mode="prompt"\ndestructive_enabled=false', []),
            ('[apps.files]\nenabled=false', []),
            ('[apps.files]\ndefault_tools_enabled=false\n[apps.files.tools.read]\nenabled=false', []),
            ('[apps.files]\ndefault_tools_enabled=false\n[apps.files.tools.read]', []),
            ('[apps.files]\nenabled=false\n[apps.mail]\ndefault_tools_approval_mode="prompt"\ndestructive_enabled=false', []),
        ]:
            with self.subTest(tail=tail):
                report = self.assert_tool_risks(template + tail, unnamed + expected)
                self.assertEqual([e["observations"] for e in report["catalog"] if e["name"] == "apps._default"],
                                 [["configured enabled", "applies to apps not named in this file",
                                   "destructive tools enabled by apps._default.destructive_enabled",
                                   "tool approval: approve"]])

    def test_app_template_gives_no_risk_when_unnamed_apps_are_off_or_it_sets_no_risky_value(self):
        # Codex turns off apps the file does not name when apps._default.enabled is false (app_tool_policy.rs
        # L174-L185), and features.apps = false removes Apps (harnesses/codex.md row features.apps false). Codex's
        # own defaults for those apps are a setup line, not a finding.
        for template in ['[apps._default]\nenabled=false\ndefault_tools_approval_mode="approve"\ndestructive_enabled=true\n',
                         '[features]\napps=false\n[apps._default]\ndefault_tools_approval_mode="approve"\ndestructive_enabled=true\n',
                         '[apps._default]\ndefault_tools_approval_mode="prompt"\ndestructive_enabled=false\n',
                         '[apps._default]\ndefault_tools_approval_mode="writes"\n',
                         '[apps._default]\n']:
            with self.subTest(template=template):
                self.assert_tool_risks(template, [])
