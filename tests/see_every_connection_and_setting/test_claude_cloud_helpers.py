import json

from tests.support import ConfigCase

VALID = {"awsAuthRefresh": "seed-aws-sso", "awsCredentialExport": "seed-aws-export", "gcpAuthRefresh": "seed-gcloud", "otelHeadersHelper": "/seed/otel-headers"}
EXPECTED = [
    (None, {"awsAuthRefresh": [["command withheld"], True], "awsCredentialExport": [["command withheld"], True], "gcpAuthRefresh": [["command withheld"], True], "otelHeadersHelper": [["command withheld"], True]}),
    ("user", {"awsAuthRefresh": [["command withheld"], True], "awsCredentialExport": [["command withheld"], True], "gcpAuthRefresh": [["command withheld"], True], "otelHeadersHelper": [["command withheld"], True]}),
    ("project", {"awsAuthRefresh": [["command withheld", "project settings"], True], "awsCredentialExport": [["command withheld", "project settings"], True], "gcpAuthRefresh": [["command withheld", "project settings"], True], "otelHeadersHelper": [["command withheld", "project settings"], True]}),
]
INVALID = [
    ("awsAuthRefresh", "", "awsAuthRefresh is not a nonempty command; it was not evaluated."),
    ("awsCredentialExport", 1, "awsCredentialExport is not a nonempty command; it was not evaluated."),
    ("gcpAuthRefresh", None, "gcpAuthRefresh is not a nonempty command; it was not evaluated."),
    ("otelHeadersHelper", {"cmd": "seed"}, "otelHeadersHelper is not a nonempty command; it was not evaluated."),
]


def read_file(*args, **kwargs):
    from stay_safe import claude
    return claude.read_file(*args, **kwargs)


class ClaudeCloudHelpersTests(ConfigCase):
    def read(self, settings, scope=None):
        path = self.config(json.dumps({"permissions": {"defaultMode": "default"}, **settings}), "settings.json")
        return read_file(path, "settings-1", **({"scope": scope} if scope else {}))

    def programs(self, entries):
        return {entry["name"]: [entry["observations"], entry["facts"].get("configured_program")]
                for entry in entries if entry["kind"] == "program"}

    def test_cloud_helpers_is_listed_with_its_command_withheld(self):
        for scope, expected in EXPECTED:
            with self.subTest(scope=scope):
                entries, gaps = self.read(VALID, scope)
                self.assertEqual(self.programs(entries), expected)
                self.assertEqual(gaps, [])
                self.assertNotIn("seed", json.dumps([entries, gaps]))

    def test_malformed_cloud_helpers_names_the_setting(self):
        for name, value, message in INVALID:
            with self.subTest(name=name, value=value):
                entries, gaps = self.read({name: value})
                self.assertEqual(gaps, [f"settings-1: {message}"])
                self.assertEqual(self.programs(entries), {})
                self.assertNotIn("seed", json.dumps([entries, gaps]))
