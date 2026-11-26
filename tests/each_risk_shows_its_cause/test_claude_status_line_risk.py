import json

from tests.support import ConfigCase, agent_home, run_home

USER = {"permissions": {"defaultMode": "default"}}
PROJECT = {"statusLine": {"type": "command", "command": "seed-status --token sk-seed", "padding": 1}}
HEADLINE = 'After you trust the workspace, Claude Code can run the command in `statusLine` to draw the status line. Trust inherited from a parent folder also counts.'


class ClaudeStatusLineRiskTests(ConfigCase):
    def test_status_line_finding_names_its_file_and_withholds_the_command(self):
        home = agent_home(self.root, claude=json.dumps(USER))
        project = self.root / "repo"
        (project / ".claude").mkdir(parents=True)
        (project / ".claude" / "settings.json").write_text(json.dumps(PROJECT), encoding="utf-8")
        run = run_home(home, "--agent", "claude", "--format", "json", cwd=project)
        report = json.loads(run.stdout)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual([(risk["entry"], risk["explanation"]) for risk in report["risks"]],
                         [("settings-2:statusLine", HEADLINE)])
        self.assertEqual({risk["rule"] for risk in report["risks"]}, {"configured_program"})
        markdown = run_home(home, "--agent", "claude", cwd=project).stdout
        self.assertIn("Remove `statusLine` from `.claude/settings.json` using a text editor.", markdown)
        self.assertIn("`statusLine.command`", markdown)
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
        self.assertEqual(report["inspection_gaps"], [
            "disableAllHooks suppresses the statusLine command in the inspected settings. Managed settings may supply their own command."
        ])
        settings.write_text(json.dumps({"disableAllHooks": False}), encoding="utf-8")
        run = run_home(home, "--agent", "claude", "--format", "json", cwd=project)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual([risk["entry"] for risk in json.loads(run.stdout)["risks"]], ["settings-1:statusLine"])

    def test_precedence_fallback_trust_and_independent_files(self):
        home = agent_home(self.root, claude=json.dumps({**USER, **PROJECT}))
        user_file = home / ".claude/settings.json"
        project = self.root / "repo"
        path = project / ".claude/settings.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({**USER, **PROJECT}))
        user, shared = "settings-1:statusLine", "settings-2:statusLine"

        def inspect(*extra):
            run = run_home(home, "--agent", "claude", "--format", "json", *extra, cwd=project)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertNotIn("seed", run.stdout)
            report = json.loads(run.stdout)
            return ({r["entry"]: r["explanation"] for r in report["risks"]},
                    {e["id"]: e["observations"] for e in report["catalog"] if e["name"] == "statusLine"})

        risks, entries = inspect()
        self.assertEqual(risks, {shared: HEADLINE})
        self.assertEqual(set(entries), {user, shared})
        self.assertIn("overridden by settings-2", entries[user])
        risks, _ = inspect("--config", str(user_file), "--config", str(path))
        self.assertEqual(risks, {user: HEADLINE, shared: HEADLINE})
        path.write_text("{}")
        risks, _ = inspect()
        self.assertEqual(risks, {user: HEADLINE})
        path.write_text(json.dumps({"statusLine": {}}))
        run = run_home(home, "--agent", "claude", cwd=project)
        self.assertEqual(run.returncode, 2)
        self.assertIn("Set `statusLine.type` to `command` and put the command you want to run in `statusLine.command`, or remove `statusLine`.", run.stdout)
