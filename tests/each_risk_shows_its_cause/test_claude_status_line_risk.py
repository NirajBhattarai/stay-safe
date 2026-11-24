import json

from tests.support import ConfigCase, agent_home, run_home

USER = {"permissions": {"defaultMode": "default"}}
PROJECT = {"statusLine": {"type": "command", "command": "seed-status --token sk-seed", "padding": 1}}
RISKS = [
    ["settings-2:statusLine", "This file's `statusLine` setting runs a command on your computer. Claude Code runs it from a project's settings only after you trust the folder; a trusted parent folder also counts."],
]
MARKDOWN = [
    "*Change it:* `statusLine` in `.claude/settings.json`",
    "*Check:* In `.claude/settings.json`, `statusLine` holds the command it runs. If it runs a script file, check that file too. Find out who wrote it before you trust it. In a git repository, `git log -p -- .claude/` shows who changed the settings and scripts there.",
]


class ClaudeStatusLineRiskTests(ConfigCase):
    def test_status_line_finding_names_its_file_and_withholds_the_command(self):
        home = agent_home(self.root, claude=json.dumps(USER))
        project = self.root / "repo"
        (project / ".claude").mkdir(parents=True)
        (project / ".claude" / "settings.json").write_text(json.dumps(PROJECT), encoding="utf-8")
        run = run_home(home, "--agent", "claude", "--format", "json", cwd=project)
        report = json.loads(run.stdout)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertCountEqual([[risk["entry"], risk["explanation"]] for risk in report["risks"]], RISKS)
        self.assertEqual({risk["rule"] for risk in report["risks"]}, {"configured_program"})
        markdown = run_home(home, "--agent", "claude", cwd=project).stdout
        for line in MARKDOWN:
            self.assertIn(line, markdown)
        self.assertNotIn("seed", (run.stdout + markdown).lower())

    def test_a_project_disable_all_hooks_turns_off_a_user_status_line(self):
        home = agent_home(self.root, claude=json.dumps({**USER, **PROJECT}))
        project = self.root / "repo"
        (project / ".claude").mkdir(parents=True)
        settings = project / ".claude" / "settings.json"
        settings.write_text(json.dumps({"disableAllHooks": True}), encoding="utf-8")
        report = json.loads(run_home(home, "--agent", "claude", "--format", "json", cwd=project).stdout)
        entries = {entry["name"]: entry["observations"] for entry in report["catalog"]}
        self.assertEqual(entries["statusLine"], ["command withheld", "turned off by disableAllHooks in settings-2"])
        self.assertEqual(report["risks"], [])
        self.assertEqual(len(report["inspection_gaps"]), 1)
        settings.write_text(json.dumps({"disableAllHooks": False}), encoding="utf-8")
        run = run_home(home, "--agent", "claude", "--format", "json", cwd=project)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual([risk["entry"] for risk in json.loads(run.stdout)["risks"]], ["settings-1:statusLine"])
