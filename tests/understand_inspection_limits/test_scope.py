from stay_safe.report import inspect, render
from tests.support import ConfigCase, full_scope


class ScopeTests(ConfigCase):
    def test_the_full_scope_holds_every_scope_line(self):
        report = inspect([self.config('approval_policy = "on-request"\nsandbox_mode = "read-only"\n')])
        self.assertIn("docs/report.md#full-scope)", render(report, "markdown"))
        full = " ".join(full_scope().split())
        self.assertIn("Connection reachability, authentication, active tools and effective permissions are not tested.",
                      full)
        for line in report["scope"] + ["Local modifications to the checkout or unzipped release are not checked; the JSON report's "
                                       "`tool_revision` and `rules_revision` fingerprints identify the files that ran."]:
            with self.subTest(limit=line):
                self.assertIn(" ".join(line.split()), full)
