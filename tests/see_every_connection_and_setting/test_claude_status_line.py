import json

from tests.support import ConfigCase

VALID = {"statusLine": {"type": "command", "command": "seed-status --token sk-seed", "padding": 1}}
EXPECTED = [
    (None, {"statusLine": [["command withheld"], True]}),
    ("user", {"statusLine": [["command withheld"], True]}),
    ("project", {"statusLine": [["command withheld", "project settings"], True]}),
]
INVALID = [
    ("statusLine", {"type": "static", "command": "seed"}, "statusLine needs type \"command\" and a command string containing more than whitespace."),
    ("statusLine", {"type": "command", "command": " "}, "statusLine needs type \"command\" and a command string containing more than whitespace."),
    ("statusLine", "seed-status", "statusLine needs type \"command\" and a command string containing more than whitespace."),
]


def read_file(*args, **kwargs):
    from stay_safe import claude
    return claude.read_file(*args, **kwargs)


class ClaudeStatusLineTests(ConfigCase):
    def read(self, settings, scope=None):
        path = self.config(json.dumps({"permissions": {"defaultMode": "default"}, **settings}), "settings.json")
        return read_file(path, "settings-1", **({"scope": scope} if scope else {}))

    def programs(self, entries):
        return {entry["name"]: [entry["observations"], entry["facts"].get("configured_program")]
                for entry in entries if entry["kind"] == "program"}

    def test_status_line_is_listed_with_its_command_withheld(self):
        for scope, expected in EXPECTED:
            with self.subTest(scope=scope):
                entries, gaps = self.read(VALID, scope)
                self.assertEqual(self.programs(entries), expected)
                self.assertEqual(gaps, [])
                self.assertNotIn("seed", json.dumps([entries, gaps]))

        entries, gaps = self.read({**VALID, "disableAllHooks": True}, "user")
        self.assertEqual(self.programs(entries), {"statusLine": [["command withheld", "turned off by disableAllHooks in this file"], False]})

    def test_malformed_status_line_names_the_setting(self):
        for name, value, message in INVALID:
            with self.subTest(name=name, value=value):
                entries, gaps = self.read({name: value})
                self.assertEqual(gaps, [f"settings-1: {message}"])
                self.assertEqual(self.programs(entries), {})
                self.assertNotIn("seed", json.dumps([entries, gaps]))
