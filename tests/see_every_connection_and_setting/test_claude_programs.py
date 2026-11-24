import json
import os
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from stay_safe.cli import main
from tests.support import INCOMPLETE, ConfigCase, agent_home, run_home

HOOK = {"SessionStart": [{"hooks": [{"type": "command", "command": "seed-hook-command --token sk-seed"}]}]}
EVENTS = ("SessionStart", "UserPromptSubmit", "PreToolUse", "PermissionRequest", "PostToolUse", "PostToolBatch",
          "SubagentStart", "SubagentStop", "TaskCreated", "TaskCompleted", "Stop", "SessionEnd")


def read_file(*args, **kwargs):
    from stay_safe import claude
    return claude.read_file(*args, **kwargs)


class ClaudeProgramSettingsTests(ConfigCase):
    def read(self, settings, scope=None):
        path = self.config(json.dumps(settings), "settings.json")
        return read_file(path, "settings-1", **({"scope": scope} if scope else {}))

    def programs(self, entries):
        return {entry["name"]: (entry["observations"], entry["facts"].get("configured_program"))
                for entry in entries if entry["kind"] == "hook"}

    def test_a_command_hook_on_any_event_is_listed_with_its_command_withheld(self):
        for event in EVENTS:
            with self.subTest(event=event):
                hooks = {event: [{"matcher": "*", "hooks": [{"type": "command", "command": "seed-hook-command"}]}]}
                entries, gaps = self.read({"permissions": {"defaultMode": "default"}, "hooks": hooks})
                decides = ["on PreToolUse or PermissionRequest: can approve or change tool calls"]
                expected = ["command withheld", *(decides if event in ("PreToolUse", "PermissionRequest") else [])]
                self.assertEqual(self.programs(entries), {"hooks": (expected, True)})
                self.assertEqual(gaps, [])
                self.assertNotIn("seed", json.dumps([entries, gaps]))

    def test_project_settings_mark_hooks_and_take_the_mode_from_other_files(self):
        entries, gaps = self.read({"hooks": HOOK}, "project")
        self.assertEqual(self.programs(entries), {"hooks": (["command withheld", "project settings"], True)})
        self.assertEqual(gaps, [])
        self.assertEqual([entry["name"] for entry in entries], ["hooks"])
        self.assertNotIn("seed", json.dumps([entries, gaps]))

    def test_disable_all_hooks_turns_off_hooks_in_the_same_file(self):
        entries, gaps = self.read({"permissions": {"defaultMode": "default"}, "hooks": HOOK, "disableAllHooks": True})
        self.assertEqual(self.programs(entries),
                         {"hooks": (["command withheld", "turned off by disableAllHooks in this file"], False)})
        self.assertIn(("disableAllHooks", ["true"]), [(e["name"], e["observations"]) for e in entries])

        entries, gaps = self.read({"hooks": HOOK, "disableAllHooks": "yes"})
        self.assertEqual(self.programs(entries)["hooks"], (["command withheld"], True))
        self.assertIn("settings-1: disableAllHooks has an invalid boolean; its behavior is unknown.", gaps)

    def test_http_hooks_send_data_out_and_prompt_hooks_are_listed_without_a_finding(self):
        hooks = {"PreToolUse": [{"hooks": [{"type": "http", "url": "https://seed-host.example/hook"}]}],
                 "Stop": [{"hooks": [{"type": "prompt", "prompt": "seed prompt"}, {"type": "agent", "prompt": "seed"}]}]}
        entries, gaps = self.read({"permissions": {"defaultMode": "default"}, "hooks": hooks}, "project")
        found = {e["name"]: (e["observations"], {k for k, v in e["facts"].items() if v}) for e in entries
                 if e["kind"] == "hook"}
        self.assertEqual(found, {
            "hooks.http": (["HTTP hook", "address withheld",
                            "on PreToolUse or PermissionRequest: can approve or change tool calls", "project settings"],
                           {"network_access"}),
            "hooks.prompt": (["prompt or agent hook; prompt withheld", "project settings"], set())})
        self.assertEqual(gaps, [])
        self.assertNotIn("seed", json.dumps([entries, gaps]))

        entries, _ = self.read({"hooks": hooks, "disableAllHooks": True})
        self.assertEqual([e["facts"] for e in entries if e["name"] == "hooks.http"], [{"network_access": False}])

    def test_malformed_hooks_name_the_field(self):
        cases = {
            "hooks is not an object of hook events; its hooks were not evaluated.": {"hooks": []},
            "hooks contains an event that is not a list of matcher groups; it was not evaluated.":
                {"hooks": {"SessionStart": {}}},
            "hooks contains a matcher group without a list of handlers; it was not evaluated.":
                {"hooks": {"SessionStart": [{"matcher": "x"}]}},
            "hooks contains a handler that is not a valid hook; it was not evaluated.":
                {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "  "}, {"type": "http"},
                                                       {"type": "prompt", "prompt": ""}, {"type": "seed"}]}]}},
            "hooks contains MCP tool hooks, which call a tool on an MCP server without asking you; that server was "
            "not evaluated.":
                {"hooks": {"Stop": [{"hooks": [{"type": "mcp_tool", "server": "seed", "tool": "seed-tool"}]}]}},
        }
        for message, settings in cases.items():
            with self.subTest(message=message):
                entries, gaps = self.read({"permissions": {"defaultMode": "default"}, **settings})
                self.assertEqual(gaps, [f"settings-1: {message}"])
                self.assertEqual(self.programs(entries), {})
                self.assertNotIn("seed", json.dumps([entries, gaps]))

    def test_unreadable_project_folder_is_a_named_gap(self):
        home = agent_home(self.root, claude='{"permissions": {"defaultMode": "default"}}')
        project = self.root / "repo"
        (project / ".claude").mkdir(parents=True)
        (project / ".claude" / "settings.json").write_text(json.dumps({"hooks": HOOK}), encoding="utf-8")
        original = os.listdir

        def listdir(path):
            if Path(path) == Path(".claude"):
                raise PermissionError(13, "Permission denied")
            return original(path)

        previous = os.getcwd()
        self.addCleanup(os.chdir, previous)
        os.chdir(project)
        output, errors = StringIO(), StringIO()
        with patch.dict(os.environ, {"HOME": str(home)}, clear=True), \
                patch("stay_safe.cli.os.listdir", listdir), redirect_stdout(output), redirect_stderr(errors):
            status = main(["--agent", "claude", "--format", "json"])
        self.assertEqual((status, errors.getvalue()), (2, INCOMPLETE))
        report = json.loads(output.getvalue())
        self.assertEqual(report["sources_read"], ["settings-1"])
        self.assertEqual(report["inspection_gaps"],
                         ["The project's .claude folder could not be checked; its settings were not inspected."])
        self.assertEqual(report["risks"], [])
        self.assertNotIn("seed", json.dumps(report))

    def test_discovery_reads_the_project_file_in_the_current_folder_once(self):
        home = agent_home(self.root, claude='{"permissions": {"defaultMode": "default"}}')
        project = self.root / "repo"
        (project / ".claude").mkdir(parents=True)
        (project / ".claude" / "settings.json").write_text(json.dumps({"hooks": HOOK}), encoding="utf-8")
        run = run_home(home, "--agent", "claude", "--format", "json", cwd=project)
        report = json.loads(run.stdout)
        self.assertEqual((run.returncode, report["sources_read"]), (0, ["settings-1", "settings-2"]))

        run = run_home(home, "--agent", "claude", "--format", "json", cwd=home)
        self.assertEqual(json.loads(run.stdout)["sources_read"], ["settings-1"])
