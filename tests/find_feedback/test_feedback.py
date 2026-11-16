import json
import subprocess
import sys
import unittest

from tests.support import ROOT
from stay_safe.report import inspect, render

URL = "https://github.com/chalkbadger/stay-safe/issues/new/choose"
LABEL = "Report a problem or suggest an idea"


class FeedbackTests(unittest.TestCase):
    def test_reports_link_once_and_json_stays_a_document(self):
        sample = ROOT / "tests/runs_without_a_coding_agent/sample.toml"
        for path in (sample, ROOT / "missing-feedback-config.toml"):
            for fmt in ("markdown", "html"):
                with self.subTest(path=path, format=fmt):
                    output = render(inspect([path]), fmt)
                    self.assertEqual(output.count(URL), 1)
                    self.assertEqual(output.count(LABEL), 1)
                    link = f"[{LABEL}]({URL})" if fmt == "markdown" else f'<a href="{URL}">{LABEL}</a>'
                    self.assertIn(link, output)
            for args in ([], ["--format", "json"]):
                result = subprocess.run([sys.executable, "-B", "-m", "stay_safe", "--config", str(path), *args],
                                        cwd=ROOT, capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 0 if path == sample else 2)
                self.assertNotIn(URL, result.stderr)
                if args:
                    self.assertIsInstance(json.loads(result.stdout), dict)
                    self.assertNotIn(URL, result.stdout)
                else:
                    self.assertEqual(result.stdout.count(URL), 1)

    def test_argument_errors_link_once_without_echoing_private_arguments(self):
        private = "/private/customer-token/report.html"
        for args in (["--unknown", private], ["--save", private], ["--save", "--format", "json"],
                     ["--rules", private, "--rules", private]):
            with self.subTest(args=args):
                result = subprocess.run([sys.executable, "-B", "-m", "stay_safe", *args], cwd=ROOT,
                                        capture_output=True, text=True, timeout=20)
                self.assertEqual((result.returncode, result.stdout), (2, ""))
                self.assertEqual(result.stderr.count(LABEL + ": " + URL), 1)
                self.assertNotIn(private, result.stderr)
        help_run = subprocess.run([sys.executable, "-B", "-m", "stay_safe", "--help"], cwd=ROOT,
                                  capture_output=True, text=True, timeout=20)
        self.assertEqual((help_run.returncode, help_run.stderr), (0, ""))
