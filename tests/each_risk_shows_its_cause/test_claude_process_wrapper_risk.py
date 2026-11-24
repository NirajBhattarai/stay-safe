import json

from tests.support import ConfigCase, agent_home, run_home

USER = {"permissions": {"defaultMode": "default"}, "processWrapper": "/seed/corp-launcher --flag"}
PROJECT = {"processWrapper": "/seed/corp-launcher --flag"}
RISKS = [
    ["settings-1:processWrapper", "This file's `processWrapper` setting runs a command on your computer."],
]
MARKDOWN = [
    "*Change it:* `processWrapper` in `~/.claude/settings.json`",
    "*Check:* In `~/.claude/settings.json`, `processWrapper` holds the command it runs. If it runs a script file, check that file too. Find out who wrote it before you trust it.\n",
    "- `processWrapper`: ignored in project settings; applies only from user or managed settings",
]


class ClaudeProcessWrapperRiskTests(ConfigCase):
    def test_process_wrapper_finding_names_its_file_and_withholds_the_command(self):
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
