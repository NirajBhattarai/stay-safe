import json

from tests.support import ConfigCase, agent_home, run_home

USER = {"permissions": {"defaultMode": "default"}, "sshHostCommands": [{"id": "seed-id", "name": "seed-name", "command": "seed-dev create"}]}
PROJECT = {"sshHostCommands": [{"id": "seed-id", "name": "seed-name", "command": "seed-dev create"}]}
RISKS = [["settings-1:sshHostCommands", 'When you select a configured SSH connection to create a machine, Claude Desktop can run the connection’s `command` on your computer. Desktop connects to the host the command prints. Creating another machine for the same connection can run the command again.']]
MARKDOWN = [
    "Remove `sshHostCommands` from `~/.claude/settings.json`",
    "Claude Desktop ignores `sshHostCommands` in `.claude/settings.json`.",
    "read that script before you trust it.",
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

    def test_selected_file_reports_a_configured_command_beside_an_invalid_connection(self):
        home = agent_home(self.root, claude=json.dumps(USER))
        path = home / ".claude" / "settings.json"
        path.write_text(json.dumps({**USER, "sshHostCommands": [*USER["sshHostCommands"], {"id": "seed"}]}))
        def inspect(fmt):
            return run_home(home, "--agent", "claude", "--config", str(path), "--format", fmt)
        result = inspect("json")
        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        risk, = report["risks"]
        self.assertIn("Claude Desktop reads `sshHostCommands` from your user settings or from a managed file or policy on your computer.", risk["explanation"])
        self.assertEqual(set(report["inspection_gaps"]), {
            "settings-1: Connection 2 in sshHostCommands is missing command. Add the program and arguments that print the SSH host.",
            "settings-1: Connection 2 in sshHostCommands is missing name. Add the display name.",
        })
        markdown = inspect("markdown")
        self.assertEqual(markdown.returncode, 2)
        self.assertIn("Connection 2 in `sshHostCommands` is missing `command`.", markdown.stdout)
        self.assertNotIn("seed", result.stdout + markdown.stdout)
        path.write_text(json.dumps({**USER, "sshHostCommands": []}))
        result = inspect("json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["risks"], [])

    def test_user_hook_switch_changes_the_ssh_command_finding(self):
        home = agent_home(self.root, claude=json.dumps({**USER, "disableAllHooks": True}))
        result = run_home(home, "--agent", "claude", "--format", "json")
        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertEqual(report["risks"], [])
        self.assertIn("disableAllHooks is set to true.", report["inspection_gaps"][0])
        (home / ".claude/settings.json").write_text(json.dumps({**USER, "disableAllHooks": False}))
        result = run_home(home, "--agent", "claude", "--format", "json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual([r["entry"] for r in json.loads(result.stdout)["risks"]], ["settings-1:sshHostCommands"])
