import json

from tests.support import ConfigCase

VALID = {"fileSuggestion": {"type": "command", "command": "~/seed/file-index.sh"}}
EXPECTED = [
    (None, {"fileSuggestion": [["command withheld"], True]}),
    ("user", {"fileSuggestion": [["command withheld"], True]}),
    ("project", {"fileSuggestion": [["command withheld", "project settings; runs after workspace trust"], True]}),
]
INVALID = [
    ("fileSuggestion", {"command": "seed"}, "fileSuggestion is not a command object with a nonempty command; it was not evaluated."),
    ("fileSuggestion", {"type": "command"}, "fileSuggestion is not a command object with a nonempty command; it was not evaluated."),
    ("fileSuggestion", [], "fileSuggestion is not a command object with a nonempty command; it was not evaluated."),
]


def read_file(*args, **kwargs):
    from stay_safe import claude
    return claude.read_file(*args, **kwargs)


class ClaudeFileSuggestionTests(ConfigCase):
    def read(self, settings, scope=None):
        path = self.config(json.dumps({"permissions": {"defaultMode": "default"}, **settings}), "settings.json")
        return read_file(path, "settings-1", **({"scope": scope} if scope else {}))

    def programs(self, entries):
        return {entry["name"]: [entry["observations"], entry["facts"].get("configured_program")]
                for entry in entries if entry["kind"] == "program"}

    def test_file_suggestion_is_listed_with_its_command_withheld(self):
        for scope, expected in EXPECTED:
            with self.subTest(scope=scope):
                entries, gaps = self.read(VALID, scope)
                self.assertEqual(self.programs(entries), expected)
                self.assertEqual(gaps, [])
                self.assertNotIn("seed", json.dumps([entries, gaps]))

        entries, gaps = self.read({**VALID, "disableAllHooks": True}, "user")
        self.assertEqual(self.programs(entries), {"fileSuggestion": [["command withheld", "turned off by disableAllHooks in this file"], False]})

    def test_malformed_file_suggestion_names_the_setting(self):
        for name, value, message in INVALID:
            with self.subTest(name=name, value=value):
                entries, gaps = self.read({name: value})
                self.assertEqual(gaps, [f"settings-1: {message}"])
                self.assertEqual(self.programs(entries), {})
                self.assertNotIn("seed", json.dumps([entries, gaps]))
