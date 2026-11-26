import json

from tests.support import ConfigCase

VALID = {"sshHostCommands": [{"id": "seed-id", "name": "seed-name", "command": "seed-dev create"}]}
EXPECTED = [
    (None, {"sshHostCommands": [["command withheld", "Claude Desktop reads this setting from user settings or a managed file or policy on this computer."], True]}),
    ("user", {"sshHostCommands": [["command withheld"], True]}),
    ("project", {"sshHostCommands": [["Claude Desktop ignores this setting in project files."], False]}),
]
INVALID = [
    ("sshHostCommands", [{'id': 'seed', 'name': 'seed', 'command': ''}], "An sshHostCommands entry needs text in its command field."),
    ("sshHostCommands", [42], "Each sshHostCommands entry must be a JSON object."),
    ("sshHostCommands", {}, "sshHostCommands must be a list of connection entries."),
]


def read_file(*args, **kwargs):
    from stay_safe import claude
    return claude.read_file(*args, **kwargs)


class ClaudeSshHostCommandsTests(ConfigCase):
    def read(self, settings, scope=None):
        path = self.config(json.dumps({"permissions": {"defaultMode": "default"}, **settings}), "settings.json")
        return read_file(path, "settings-1", **({"scope": scope} if scope else {}))

    def programs(self, entries):
        return {entry["name"]: [entry["observations"], entry["facts"].get("configured_program")]
                for entry in entries if entry["kind"] == "program"}

    def test_ssh_host_commands_is_listed_with_its_command_withheld(self):
        for scope, expected in EXPECTED:
            with self.subTest(scope=scope):
                entries, gaps = self.read(VALID, scope)
                self.assertEqual(self.programs(entries), expected)
                self.assertEqual(gaps, [])
                self.assertNotIn("seed", json.dumps([entries, gaps]))

    def test_malformed_ssh_host_commands_names_the_setting(self):
        for name, value, message in INVALID:
            with self.subTest(name=name, value=value):
                entries, gaps = self.read({name: value})
                self.assertEqual(gaps, [f"settings-1: {message}"])
                self.assertEqual(self.programs(entries), {})
                self.assertNotIn("seed", json.dumps([entries, gaps]))
