import json
from pathlib import Path

from stay_safe.report import inspect
from tests.support import ConfigCase, INCOMPLETE, ROOT, run_checkout


FIXTURE = Path(__file__).with_name("inline-env.toml")
BASE = 'approval_policy="on-request"\nsandbox_mode="read-only"\nshell_environment_policy.inherit="none"\nfeatures.apps=false\n'
STDIO = 'command="private-command"\ndefault_tools_approval_mode="prompt"\n'
HTTP = 'url="https://example.invalid"\ndefault_tools_approval_mode="approve"\n'


class InlineMcpTests(ConfigCase):
    def test_inline_env_and_reference_control_keep_the_program_finding(self):
        text = FIXTURE.read_text(encoding="utf-8")
        reference = text.split("[mcp_servers.example.env]")[0] + 'env_vars=["EXAMPLE_TOKEN"]\n'
        for path, gaps in ((FIXTURE, ["config-1: mcp_servers.example.env contains inline values. Check the entries for credentials."]),
                           (self.config(reference), [])):
            with self.subTest(path=path):
                run = run_checkout(ROOT, "--config", str(path), "--format", "json", cwd=self.root)
                report = json.loads(run.stdout)
                self.assertEqual(report["inspection_gaps"], gaps)
                self.assertEqual([(r["rule"], r["entry"]) for r in report["risks"]],
                                 [("configured_program", "config-1:mcp_servers.example")])
                self.assertEqual((run.returncode, run.stderr), (2, INCOMPLETE) if gaps else (0, ""))

    def test_each_populated_field_names_its_snapshot_and_server_once(self):
        text = BASE + '[mcp_servers."team.api"]\n' + HTTP + 'http_headers={One="first",Two="second"}\n'
        text += '[mcp_servers.local]\n' + STDIO + 'env={Private="first",Another="second"}\n'
        paths = [self.config(text, "one.toml"), self.config(text, "two.toml")]
        report = inspect(paths)
        expected = [f'config-{n}: mcp_servers.{field} contains inline values. Check the entries for credentials.'
                    for n in (1, 2) for field in ('"team.api".http_headers', 'local.env')]
        self.assertCountEqual(report["inspection_gaps"], expected)
        self.assertIn(("automatic_tools", 'config-2:mcp_servers."team.api"'),
                      [(r["rule"], r["entry"]) for r in report["risks"]])

    def test_only_enabled_compatible_populated_tables_get_the_credentials_advice(self):
        for transport, controls in ((STDIO, ('env={}', '', 'env_vars=["REF"]', 'enabled=false\nenv={Private="hidden"}')),
                                    (HTTP, ('http_headers={}', '', 'env_http_headers={Key="REF"}\nbearer_token_env_var="REF"',
                                            'enabled=false\nhttp_headers={Private="hidden"}'))):
            for fields in controls:
                with self.subTest(transport=transport, fields=fields):
                    report = inspect([self.config(BASE + "[mcp_servers.local]\n" + transport + fields)])
                    self.assertEqual(report["inspection_gaps"], [])
        for config in (STDIO + 'http_headers={Private="hidden"}', HTTP + 'env={Private="hidden"}',
                       'command="private"\nurl="ignored"\nenv={Private="hidden"}'):
            with self.subTest(config=config):
                gaps = inspect([self.config(BASE + "[mcp_servers.local]\n" + config)])["inspection_gaps"]
                self.assertFalse(any("credentials" in g for g in gaps))
        hidden = inspect([self.config(BASE + '[mcp_servers."sk-private"]\n' + STDIO + 'env={Private="hidden"}')])
        self.assertEqual(hidden["inspection_gaps"], [
            "config-1: mcp_servers contains a name that cannot be included in a shareable report."])

    def test_rejected_inline_maps_keep_the_other_servers_finding(self):
        for field, transport in (("env", STDIO), ("http_headers", HTTP)):
            for malformed in ('"private-value"', '{private_member=12}'):
                with self.subTest(field=field, malformed=malformed):
                    text = BASE + "[mcp_servers.good]\n" + STDIO + "[mcp_servers.bad]\n" + transport + field + "=" + malformed
                    report = inspect([self.config(text)])
                    self.assertEqual(report["inspection_gaps"], [
                        f"config-1: Codex cannot load this configuration because mcp_servers.bad.{field} must be a table of strings."])
                    self.assertEqual([(r["rule"], r["entry"]) for r in report["risks"]],
                                     [("configured_program", "config-1:mcp_servers.good")])
