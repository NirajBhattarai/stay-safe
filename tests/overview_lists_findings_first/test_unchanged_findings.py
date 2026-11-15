"""Finding words remain the pre-overview words, independent of order or numbered headings.

Expected wording reuses the existing, unchanged issue-based expectations, not renderer output.
This exact test is also run on the PR's original base.
"""

import re

from stay_safe.report import inspect, render
from tests.findings_say_what_to_do.test_plain_findings import EXPECTED, HOW, RULES
from tests.findings_say_what_to_do.test_what_to_do import EXPECTED as ADVICE
from tests.support import ConfigCase, FIRST, SECOND


class UnchangedFindingTests(ConfigCase):
    def test_every_detailed_finding_keeps_its_original_words(self):
        report = inspect([self.config(FIRST, "first.toml"), self.config(SECOND, "second.toml")],
                         rules_path=self.config(RULES, "selected.rules"))
        markdown = render(report, "markdown")
        body = markdown.split("\n## Findings\n\n", 1)[1].split("\n\n## Not checked\n", 1)[0]
        body = body.split("\n\n", 1)[1]  # Shared orientation, tested separately.
        found = [re.sub(r"^### Finding \d+\n\n", "", block)
                 for block in body.split("\n\n---\n\n")]
        expected = []
        self.assertEqual({(r["rule"], r["entry"]) for r in report["risks"]}, set(EXPECTED))
        for risk in report["risks"]:
            key = (risk["rule"], risk["entry"])
            citations = ", ".join(f"[{i}]({report['incident_links'][i]})" for i in risk["incidents"])
            kind = "rules entry" if risk["entry"].startswith("rules-") else "setting"
            expected.append("\n\n".join([
                EXPECTED[key],
                f"*How it has gone wrong:* {HOW[risk['rule']]} {citations} (reported, not verified).",
                ADVICE[key],
                f"*Rule `{risk['rule']}` · {kind} `{risk['entry']}` = `{'; '.join(risk['configured_evidence'])}`*",
            ]))
        self.assertCountEqual(found, expected)
