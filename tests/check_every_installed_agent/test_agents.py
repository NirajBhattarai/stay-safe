"""A default run reports every coding agent whose folder exists; --agent selects them (issue #163).

Claude Code keeps user settings in ~/.claude/settings.json, and CLAUDE_CONFIG_DIR moves that folder
(https://code.claude.com/docs/en/settings, "Settings files and who they affect" and "Find or create your settings
files"). Codex keeps its settings in ~/.codex/config.toml, as tests/see_every_connection_and_setting/test_home.py cites.
"""

import json
from pathlib import Path

from tests.support import FEEDBACK, INCOMPLETE, ConfigCase, agent_home, run_home

CODEX = 'approval_policy = "never"\nsandbox_mode = "read-only"\n'
CLAUDE = '{"permissions": {"defaultMode": "bypassPermissions"}, "sandbox": {"enabled": true}}'
MANAGED = (Path("/Library/Application Support/ClaudeCode"), Path("/etc/claude-code"))


class AgentSelectionTests(ConfigCase):
    def setUp(self):
        super().setUp()
        self.require_no_system_folder()
        # A subprocess run reads the real managed-settings folders, which no patch can reach.
        for folder in MANAGED:
            if folder.exists():
                self.fail(f"{folder} exists and this subprocess default run reads it; run without it.")

    def json_run(self, home, *args, **env):
        run = run_home(home, "--format", "json", *args, **env)
        self.assertEqual(run.stderr, INCOMPLETE if run.returncode == 2 else "")
        return run.returncode, json.loads(run.stdout)

    def test_default_run_reports_every_installed_agent(self):
        home = agent_home(self.root, codex=CODEX, claude=CLAUDE)
        status, report = self.json_run(home)
        self.assertEqual([part["harness"] for part in report["reports"]], ["Codex", "Claude Code"])
        codex, claude = report["reports"]
        # Exit status 2 means some report has a gap, whichever agent it belongs to.
        self.assertEqual(status, 2 if codex["inspection_gaps"] or claude["inspection_gaps"] else 0)
        self.assertIn(("config-1:approval_policy", "commands_without_prompts"),
                      {(risk["entry"], risk["rule"]) for risk in codex["risks"]})
        self.assertEqual([(risk["entry"], risk["rule"]) for risk in claude["risks"]],
                         [("settings-1:permissions.defaultMode", "commands_without_prompts")])
        self.assertEqual(claude["inspection_gaps"], [])

        run = run_home(home)
        self.assertEqual((run.returncode, run.stderr), (status, INCOMPLETE if status else ""))
        self.assertEqual([line for line in run.stdout.splitlines() if line.startswith("# ")],
                         ["# Codex configuration diagnostic", "# Claude Code configuration diagnostic"])
        self.assertIn("**With these settings, Claude Code runs commands and edits files without asking you.**",
                      run.stdout)

    def test_without_a_claude_folder_the_default_run_is_the_codex_report(self):
        home = agent_home(self.root, codex=CODEX)
        for format_args in ((), ("--format", "json")):
            default, chosen = run_home(home, *format_args), run_home(home, "--agent", "codex", *format_args)
            self.assertEqual((default.returncode, default.stdout, default.stderr),
                             (chosen.returncode, chosen.stdout, chosen.stderr))
        self.assertEqual(json.loads(default.stdout)["harness"], "Codex")
        self.assertNotIn("Claude Code", default.stdout)

    def test_agent_claude_reports_only_claude_code(self):
        home = agent_home(self.root, codex=CODEX, claude=CLAUDE)
        status, report = self.json_run(home, "--agent", "claude")
        self.assertEqual((status, report["harness"]), (0, "Claude Code"))
        self.assertEqual([entry["id"] for entry in report["catalog"]],
                         ["settings-1:permissions.defaultMode", "settings-1:sandbox.enabled"])

    def test_claude_config_dir_selects_the_claude_folder(self):
        home = agent_home(self.root, claude='{"permissions": {"defaultMode": "plan"}}')
        moved = self.root / "moved"
        moved.mkdir()
        (moved / "settings.json").write_text(CLAUDE, encoding="utf-8")
        status, report = self.json_run(home, "--agent", "claude", CLAUDE_CONFIG_DIR=str(moved))
        self.assertEqual(status, 0)
        self.assertEqual(report["catalog"][0]["observations"], ["bypassPermissions"])

    def test_agent_claude_without_its_folder_says_nothing_was_inspected(self):
        home = agent_home(self.root, codex=CODEX)
        status, report = self.json_run(home, "--agent", "claude")
        self.assertEqual(status, 2)
        self.assertEqual((report["catalog"], report["risks"]), ([], []))
        self.assertEqual(report["inspection_gaps"][0],
                         "Claude Code home: ~/.claude was not found; no Claude Code files were inspected.")
        status, report = self.json_run(home, "--agent", "claude", CLAUDE_CONFIG_DIR=str(self.root / "missing"))
        self.assertEqual(report["inspection_gaps"][0],
                         "Claude Code home: $CLAUDE_CONFIG_DIR was not found; no Claude Code files were inspected.")

    def test_selected_files_need_exactly_one_agent_and_rules_need_codex(self):
        home = agent_home(self.root)
        settings = self.config(CLAUDE, "settings.json")
        cases = [
            (("--agent", "codex", "--agent", "claude", "--config", str(settings)),
             "--config needs one --agent: choose codex or claude.\n"),
            (("--agent", "claude", "--rules", str(settings)), "--rules reads Codex files only.\n"),
            (("--agent", "cursor",), "Invalid arguments. Use --help.\n"),
        ]
        for args, message in cases:
            with self.subTest(args=args[:-1]):
                run = run_home(home, *args)
                self.assertEqual((run.returncode, run.stdout, run.stderr), (2, "", message + FEEDBACK))
                self.assertNotIn(str(settings), run.stderr)
        status, report = self.json_run(home, "--agent", "claude", "--config", str(settings))
        self.assertEqual((status, report["harness"], report["risks"][0]["entry"]),
                         (0, "Claude Code", "settings-1:permissions.defaultMode"))
