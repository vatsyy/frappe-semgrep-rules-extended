from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
MAKEFILE = ROOT / "Makefile"
GOVERNANCE = ROOT / "governance" / "README.md"
PINNED_SEMGREP = "1.174.0"


class RulesCIContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text()
        cls.makefile = MAKEFILE.read_text()
        cls.governance = GOVERNANCE.read_text()

    def test_semgrep_engine_is_exactly_pinned_and_verified(self) -> None:
        pins = re.findall(
            r'^\s*SEMGREP_VERSION:\s*"([^"]+)"\s*$',
            self.workflow,
            re.MULTILINE,
        )

        self.assertEqual(pins, [PINNED_SEMGREP])
        self.assertIn('pip install "semgrep==${SEMGREP_VERSION}"', self.workflow)
        self.assertIn('test "$(semgrep --version)" = "${SEMGREP_VERSION}"', self.workflow)
        self.assertNotRegex(self.workflow, r"pip install\s+semgrep(?:\s|$)")

    def test_ci_records_complete_immutable_provenance(self) -> None:
        required = (
            "git rev-parse HEAD",
            "git rev-parse HEAD:rules",
            "semgrep --version",
        )
        for value in required:
            with self.subTest(value=value):
                self.assertIn(value, self.workflow)

    def test_make_test_is_the_single_repository_acceptance_entrypoint(self) -> None:
        self.assertEqual(self.workflow.count("make test"), 1)
        self.assertIn("id: repository", self.workflow)
        self.assertRegex(self.makefile, r"(?m)^\.PHONY:.*\btest-ci\b")
        for target in (
            "check-contract",
            "check-governance",
            "test-governance",
            "test-benchmark",
            "test-ci",
            "test-scan-contract",
            "test-all-apps-contract",
            "validate",
            "test-upstream",
            "test-backports",
            "test-custom",
        ):
            with self.subTest(target=target):
                self.assertRegex(self.makefile, rf"(?m)^test:.*\b{re.escape(target)}\b")

    def test_summary_keeps_failure_boundaries_distinct(self) -> None:
        required = (
            "if: always()",
            "steps.engine.outcome",
            "steps.provenance.outcome",
            "steps.repository.outcome",
            "Analysis Coverage: not evaluated by rules CI",
        )
        for value in required:
            with self.subTest(value=value):
                self.assertIn(value, self.workflow)

    def test_engine_changes_require_post_pilot_qualification_and_a_decision(self) -> None:
        self.assertIn("Ticket 25", self.governance)
        self.assertIn("appended governance\ndecision", self.governance)


if __name__ == "__main__":
    unittest.main()
