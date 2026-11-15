"""Readers can find results and limits without interpreting a missing section as success."""

import json
import subprocess
import sys

from tests.support import INCOMPLETE
from tests.support import ConfigCase, ROOT, section

# Four findings (commands_without_prompts; configured_program and self_described_tools on github;
# environment_inheritance by default) and two gaps (profiles, an unread setting), as in the issue's After example.
AFTER = ('approval_policy = "never"\nsandbox_mode = "read-only"\nprofile = "work"\nfuture_setting = 1\n'
         '[mcp_servers.github]\ncommand = "seed-command"\n')
EMPTY_FINDINGS = ("None of stay-safe's rules matched your settings. That doesn't mean your setup is safe: "
                  "see what stay-safe didn't check and what this report can't see, below.")
EMPTY_GAPS = ("stay-safe checked every setting it supports in the files it read. What this report can't see, below, "
              "still applies.")
HEADINGS = ["## Findings", "## Not checked", "## Your setup", "## Sources", "## What this report can't see"]
# Each limit says why and what to do (reading check, 2026-11-09).
CANT_SEE = [
    "- Settings chosen in the app or with command-line flags, and which profile Codex uses: these can override the "
    "files listed under Your setup, and stay-safe can't see them. Check them where you start Codex, and the "
    "`profile` setting in your config file.",
    "- Whether connections work, or what Codex actually allows when it runs: stay-safe only reads files; it doesn't "
    "start Codex or contact any service. Watch what Codex asks before it acts.",
    "- Private values such as commands, addresses and tokens are left out, but names like `github` are shown as "
    "written: names can identify a project or a person, so check them before sharing.",
]


class ReportLayoutTests(ConfigCase):
    def run_cli(self, text, format_name="markdown"):
        run = subprocess.run([sys.executable, "-B", "-m", "stay_safe", "--config", str(self.config(text)),
                              "--format", format_name], cwd=ROOT, env={}, text=True, capture_output=True, timeout=10)
        self.assertEqual(run.stderr, INCOMPLETE if run.returncode == 2 else "")
        return run

    def test_report_keeps_results_and_limits_visible(self):
        run = self.run_cli(AFTER)
        self.assertEqual(run.returncode, 2)
        self.assertIn("4 findings, 2 things not checked.", run.stdout)
        for heading in HEADINGS:
            self.assertTrue(section(run.stdout, heading.removeprefix("## ")))
        limits = section(run.stdout, "What this report can't see")
        for warning in CANT_SEE:
            self.assertIn(warning, limits)
        self.assertIn("docs/report.md#full-scope)", limits)

    def test_summary_counts_one_and_none_and_empty_sections_say_what_that_means(self):
        one = self.run_cli('approval_policy = "never"\nshell_environment_policy = { inherit = "none" }\n')
        self.assertEqual((one.returncode, one.stdout.splitlines()[2]), (2, "1 finding, 1 thing not checked."))
        none = self.run_cli('approval_policy = "on-request"\nsandbox_mode = "read-only"\n'
                            'shell_environment_policy = { inherit = "none" }\n')
        self.assertEqual((none.returncode, none.stdout.splitlines()[2]), (0, "0 findings, 0 things not checked."))
        self.assertEqual(section(none.stdout, "Findings"), EMPTY_FINDINGS)
        self.assertEqual(section(none.stdout, "Sources"), "No findings, so there are no rule sources to link.")
        self.assertEqual(section(none.stdout, "Not checked"),
                         EMPTY_GAPS)

    def test_empty_section_text_follows_its_own_section_and_the_count_includes_every_gap(self):
        self.require_no_system_folder()
        findings_only = self.run_cli('approval_policy = "never"\nsandbox_mode = "read-only"\n'
                                     'shell_environment_policy = { inherit = "none" }\n')
        self.assertEqual(findings_only.stdout.splitlines()[2], "1 finding, 0 things not checked.")
        self.assertNotIn(EMPTY_FINDINGS, section(findings_only.stdout, "Findings"))
        self.assertEqual(section(findings_only.stdout, "Not checked"), EMPTY_GAPS)
        gaps_only = self.run_cli('approval_policy = "on-request"\nshell_environment_policy = { inherit = "none" }\n')
        self.assertEqual(gaps_only.stdout.splitlines()[2], "0 findings, 1 thing not checked.")
        self.assertEqual(section(gaps_only.stdout, "Findings"), EMPTY_FINDINGS)
        self.assertNotIn(EMPTY_GAPS, section(gaps_only.stdout, "Not checked"))
        # A gap without a source label: a hooks.json file in the Codex home, beside a config file without gaps.
        home = self.root / "codex-home"
        home.mkdir()
        (home / "config.toml").write_text('approval_policy = "on-request"\nsandbox_mode = "read-only"\n'
                                          'shell_environment_policy = { inherit = "none" }\n')
        (home / "hooks.json").write_text("{}")
        runs = [subprocess.run([sys.executable, "-B", "-m", "stay_safe", "--format", f], cwd=ROOT,
                               env={"CODEX_HOME": str(home)}, text=True, capture_output=True, timeout=10)
                for f in ("json", "markdown")]
        self.assertEqual(len(json.loads(runs[0].stdout)["inspection_gaps"]), 1)
        self.assertEqual(runs[1].stdout.splitlines()[2], "0 findings, 1 thing not checked.")
