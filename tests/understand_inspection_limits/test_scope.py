from stay_safe.report import inspect, render
from tests.support import ConfigCase, copy_checkout, full_scope, run_checkout, section


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

    def test_selected_rules_file_is_named_when_it_has_no_saved_approvals(self):
        # Alhibb: https://github.com/chalkbadger/stay-safe/issues/109#issuecomment-7009857808
        checkout = copy_checkout(self.root / "checkout")
        rules = self.root / "selected.rules"
        quiet = 'approval_policy="on-request"\nsandbox_mode="read-only"\nshell_environment_policy={inherit="none"}\n'
        for config, content, select_rules, status, named, empty in (
            (None, "", True, 0, True, True), (None, "  # removed\n\n", True, 0, True, True),
            (quiet, "", True, 0, True, True), (quiet + "unknown_setting=true\n", "", True, 2, True, True),
            (quiet, "", False, 0, False, False),
            (None, 'prefix_rule(pattern=["git"], decision="allow")\n', True, 0, True, False),
            (None, "unsupported_rule()\n", True, 2, True, False), (None, None, True, 2, False, False),
        ):
            with self.subTest(config=config, content=content, select_rules=select_rules):
                if content is None:
                    rules.unlink(missing_ok=True)
                else:
                    rules.write_text(content, encoding="utf-8")
                args = ["--config", str(self.config(config))] if config is not None else []
                if select_rules:
                    args.extend(["--rules", str(rules)])
                run = run_checkout(checkout, *args, "--format", "markdown", cwd=self.root)
                self.assertEqual(run.returncode, status)
                intro, heading, _ = run.stdout.partition("\n\n## Findings\n\n")
                self.assertTrue(heading)
                self.assertEqual("your saved approvals (`rules-1`)" in intro, named)
                self.assertEqual("your Codex settings (`config-1`)" in intro, config is not None)
                self.assertEqual("no saved approvals" in intro.lower(), empty)
                if status == 0:
                    self.assertIn("0 things not checked", intro)
                if content is None:
                    self.assertIn("doesn't exist", section(run.stdout, "Not checked"))
                elif content and not empty and status == 0:
                    self.assertIn("rules-1:prefix_rule.1", section(run.stdout, "Findings"))
