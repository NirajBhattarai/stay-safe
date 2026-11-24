import json

from tests.support import ConfigCase, agent_home, run_home

USER = {"permissions": {"defaultMode": "default"}, "sshHostCommands": [{"id": "seed-id", "name": "seed-name", "command": "seed-dev create"}]}
PROJECT = {"sshHostCommands": [{"id": "seed-id", "name": "seed-name", "command": "seed-dev create"}]}
RISKS = [
    ["settings-1:sshHostCommands", "This file's `sshHostCommands` setting runs a command on your computer."],
]
MARKDOWN = [
    "*Change it:* `sshHostCommands` in `~/.claude/settings.json`",
    "*Check:* In `~/.claude/settings.json`, `sshHostCommands` holds the command it runs. If it runs a script file, check that file too. Find out who wrote it before you trust it.\n",
    "- `sshHostCommands`: ignored in project settings; applies only from user or managed settings",
]


class ClaudeSshHostCommandsRiskTests(ConfigCase):
    def test_ssh_host_commands_finding_names_its_file_and_withholds_the_command(self):
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
