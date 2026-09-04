from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.scan_all_apps import AllAppsScanError, discover_apps, write_summary

ROOT = Path(__file__).resolve().parents[1]


class AllAppsScanContractTest(unittest.TestCase):
    def test_discovery_is_sorted_and_excludes_the_rules_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("wiki", "frappe", "frappe-semgrep-rules-extended"):
                (root / name / ".git").mkdir(parents=True)
            (root / "not-a-repository").mkdir()

            apps = discover_apps(root, {"frappe-semgrep-rules-extended"})

            self.assertEqual([app.name for app in apps], ["frappe", "wiki"])

    def test_empty_apps_directory_fails_actionably(self) -> None:
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaisesRegex(AllAppsScanError, "no Git application"),
        ):
            discover_apps(Path(directory), set())

    def test_summary_keeps_findings_and_scan_health_distinct(self) -> None:
        aggregate = {
            "schema_version": 1,
            "status": "invalid",
            "application_count": 1,
            "finding_count": 3,
            "findings_by_rule": {"candidate-rule": 3},
            "applications": [
                {
                    "name": "example",
                    "status": "invalid",
                    "finding_count": 3,
                    "error_count": 1,
                    "source": {"content_sha256": "a" * 64},
                }
            ],
            "failures": ["example: Scan Health invalid"],
        }
        with tempfile.TemporaryDirectory() as directory:
            summary = Path(directory) / "summary.md"

            write_summary(summary, aggregate)

            content = summary.read_text()
            self.assertIn("3", content)
            self.assertIn("Scan Health: **invalid**", content)
            self.assertIn("not confirmed defects", content)

    def test_schema_covers_the_stable_aggregate_contract(self) -> None:
        schema = json.loads(
            (ROOT / "governance/schemas/all-apps-scan-v1.json").read_text()
        )

        self.assertEqual(schema["schema_version"], 1)
        self.assertEqual(
            set(schema["required"]),
            {
                "status",
                "application_count",
                "finding_count",
                "findings_by_rule",
                "applications",
                "failures",
            },
        )


if __name__ == "__main__":
    unittest.main()
