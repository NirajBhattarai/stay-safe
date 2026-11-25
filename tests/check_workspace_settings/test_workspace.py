import io
import json
import os
import subprocess
import sys
from contextlib import chdir, redirect_stderr, redirect_stdout
from unittest.mock import patch

from stay_safe.cli import main
from tests.support import ConfigCase, INCOMPLETE, ROOT, finding_items, section


class WorkspaceSettingsTests(ConfigCase):
    def setUp(self):
        super().setUp()
        self.workspace = self.root.resolve() / "private-project-name"
        home = patch.dict(os.environ, {"HOME": str(self.root.resolve() / "user-home")})
        home.start()
        self.addCleanup(home.stop)
        self.workspace.mkdir()
        self.target = self.workspace / ".codex"
        self.target.mkdir()

    def settings(self, roots=None, *, mode='sandbox_mode="workspace-write"', name="config.toml", extra=""):
        lines = ['approval_policy="on-request"', 'shell_environment_policy={inherit="none"}', mode, extra]
        if roots is not None:
            lines += ["[sandbox_workspace_write]", "writable_roots=" + json.dumps(roots)]
        return self.config("\n".join(lines), name)

    def run_report(self, *paths, workspace=True, fmt="json", status=2):
        args = ["--agent", "codex", "--format", fmt]
        if workspace:
            args += ["--workspace", str(self.workspace)]
        for path in paths:
            args += ["--config", str(path)]
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                result = main(args)
            except SystemExit as error:
                result = error.code
        self.assertEqual((result, err.getvalue()), (status, INCOMPLETE if status == 2 else ""))
        self.assertNotIn("private-project-name", out.getvalue())
        self.assertNotIn(str(self.root), out.getvalue())
        return json.loads(out.getvalue()) if fmt == "json" else out.getvalue()

    def test_direct_grant_warns_once_and_keeps_the_unchecked_effects_visible(self):
        path = self.settings([str(self.target), str(self.target)])
        report = self.run_report(path)
        self.assertEqual([(r["rule"], r["entry"]) for r in report["risks"]],
                         [("writable_project_settings", "config-1:sandbox_workspace_write.writable_roots")])
        risk = report["risks"][0]
        self.assertIn("later trusted", risk["explanation"])
        self.assertEqual(len(report["inspection_gaps"]), 1)
        self.assertIn("other effects of extra folders", report["inspection_gaps"][0])
        markdown = self.run_report(path, fmt="markdown")
        finding, = finding_items(markdown)
        self.assertIn("later trusted", finding)
        self.assertIn("writable_roots", finding)
        self.assertIn("remove", finding.lower())
        self.assertIn("other effects of extra writable folders", section(markdown, "Not checked"))

    def test_removing_direct_grant_leaves_parent_sibling_lookalike_and_narrower_roots_without_a_warning(self):
        roots = [self.workspace, self.workspace.parent / "sibling", self.workspace / ".codex-backup",
                 self.target / "narrower"]
        self.assertEqual(self.run_report(self.settings([str(p) for p in roots] + [str(self.target)]))
                         ["risks"][0]["rule"], "writable_project_settings")
        report = self.run_report(self.settings([str(p) for p in roots]))
        self.assertEqual(report["risks"], [])
        self.assertIn("writable_roots", " ".join(report["inspection_gaps"]))

    def test_mode_and_roots_must_appear_in_the_same_selected_snapshot(self):
        eligible = self.settings()
        roots = self.settings([str(self.target)], mode="", name="roots.toml")
        report = self.run_report(eligible, roots)
        self.assertEqual(report["risks"], [])
        self.assertIn("config-2: sandbox_mode is absent", " ".join(report["inspection_gaps"]))
        eligible = self.settings([str(self.target)], name="eligible.toml")
        self.assertEqual([r["entry"] for r in self.run_report(roots, eligible)["risks"]],
                         ["config-2:sandbox_workspace_write.writable_roots"])

    def test_inactive_empty_invalid_and_profile_cases(self):
        root = [str(self.target)]
        for mode, roots, gap in [('sandbox_mode="read-only"', root, None),
                                 ('sandbox_mode="workspace-write"', [], None),
                                 ('sandbox_mode="workspace-write"', None, None),
                                 ('sandbox_mode="read-only"', 7, "invalid"),
                                 ('default_permissions=":workspace"', root, "profile"),
                                 ('default_permissions="private-profile"', root, "profile"),
                                 ('sandbox_mode="workspace-write"\nprofile="private-profile"', root, "profile")]:
            with self.subTest(mode=mode, roots=roots):
                report = self.run_report(self.settings(roots, mode=mode), status=2 if gap else 0)
                self.assertEqual(report["risks"], [])
                if gap:
                    self.assertIn(gap, " ".join(report["inspection_gaps"]).lower())

    def test_missing_workspace_and_unresolved_aliases_name_the_boundary(self):
        path = self.settings([str(self.target)])
        for fmt in ["json", "markdown"]:
            with chdir(self.workspace):
                report = self.run_report(path, workspace=False, fmt=fmt)
            if fmt == "json":
                self.assertEqual(report["risks"], [])
            gap = " ".join(report["inspection_gaps"]) if fmt == "json" else section(report, "Not checked")
            self.assertIn("--workspace", gap)
        err = io.StringIO()
        with chdir(self.workspace), redirect_stderr(err), redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as invalid:
                main(["--workspace", "", "--config", str(path)])
        self.assertEqual(invalid.exception.code, 2)
        self.assertIn("--workspace needs a directory", err.getvalue())
        alias = self.workspace / "private-alias"
        alias.symlink_to(self.target, target_is_directory=True)
        for candidate in [str(alias), "../private-project-name/.codex"]:
            report = self.run_report(self.settings([candidate]))
            self.assertEqual(report["risks"], [])
            self.assertRegex(" ".join(report["inspection_gaps"]).lower(), r"alias|symlink|relative")
        self.target.rmdir()
        self.target.symlink_to(self.root, target_is_directory=True)
        report = self.run_report(path)
        self.assertEqual(report["risks"], [])
        self.assertRegex(" ".join(report["inspection_gaps"]).lower(), r"alias|symlink")

    def test_user_codex_home_is_outside_the_project_settings_check(self):
        path = self.settings([str(self.target)])
        with patch.dict(os.environ, {"CODEX_HOME": str(self.target)}):
            report = self.run_report(path)
        self.assertEqual(report["risks"], [])
        self.assertIn("Codex home", " ".join(report["inspection_gaps"]))
        alias = self.root / "private-home-alias"
        alias.symlink_to(self.target, target_is_directory=True)
        with patch.dict(os.environ, {"CODEX_HOME": str(alias)}):
            report = self.run_report(path)
        self.assertEqual(report["risks"], [])
        self.assertIn("Codex home", " ".join(report["inspection_gaps"]))

    def test_workspace_compares_discovered_settings_without_opening_project_contents(self):
        home = self.root.resolve() / "private-codex-home"
        home.mkdir()
        self.settings([str(self.target)]).rename(home / "config.toml")
        for name in ["config.toml", "auth.json", "AGENTS.md"]:
            (self.target / name).write_text("private-project-contents", encoding="utf-8")
        script = """
import sys
from pathlib import Path
from stay_safe.cli import main

workspace = Path(sys.argv[1])
def guard(event, args):
    if event in ("open", "os.listdir", "os.scandir") and isinstance(args[0], str):
        path = Path(args[0])
        if path == workspace or workspace in path.parents:
            raise RuntimeError("opened project contents")
sys.addaudithook(guard)
raise SystemExit(main(["--agent", "codex", "--workspace", str(workspace), "--format", "json"]))
"""
        run = subprocess.run([sys.executable, "-B", "-c", script, str(self.workspace)],
                             cwd=ROOT, env={**os.environ, "CODEX_HOME": str(home)},
                             capture_output=True, text=True, timeout=10)
        self.assertEqual((run.returncode, run.stderr), (2, INCOMPLETE))
        self.assertNotIn("private-", run.stdout)
        self.assertEqual([r["rule"] for r in json.loads(run.stdout)["risks"]], ["writable_project_settings"])
