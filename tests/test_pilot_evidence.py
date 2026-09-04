from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOTS = {
    "frappe-async-array-callback-misuse",
    "override-doctype-class",
    "frappe-sql-format-injection",
    "frappe-whitelisted-permission-bypass",
    "frappe-n-plus-one-read-in-loop",
}


class PilotEvidenceContractTest(unittest.TestCase):
    def load(self, relative: str) -> dict:
        return json.loads((ROOT / relative).read_text())

    def test_review_cut_and_packets_cover_exactly_five_rules(self) -> None:
        cut = self.load("governance/review-cuts/portfolio-review-cut-v1.json")
        packets = [
            json.loads(path.read_text())
            for path in sorted((ROOT / "governance/pilot/evidence").glob("*.json"))
        ]

        self.assertEqual(set(cut["activated_rule_ids"]), PILOTS)
        self.assertEqual({packet["rule_id"] for packet in packets}, PILOTS)
        counts = {row["rule_id"]: row["match_count"] for row in cut["queue"]}
        for packet in packets:
            self.assertEqual(packet["engine_match_census"]["population"], counts[packet["rule_id"]])
            self.assertGreater(packet["engine_match_census"]["reviewed"], 0)
            self.assertTrue(packet["safe_near_misses"])
            self.assertTrue(packet["missed_positive_search"])

    def test_decisions_reference_existing_packets_and_changed_claims(self) -> None:
        decisions = self.load("governance/pilot/decisions-v1.json")

        self.assertEqual({row["rule_id"] for row in decisions["decisions"]}, PILOTS)
        for row in decisions["decisions"]:
            self.assertTrue((ROOT / row["evidence_packet"]).is_file())
        self.assertEqual(
            decisions["new_rules"],
            ["frappe-n-plus-one-read-in-comprehension", "frappe-whitelisted-raw-sql"],
        )

        performance_fixture = (ROOT / "rules/custom/performance/frappe_performance.py").read_text()
        security_fixture = (ROOT / "rules/custom/security/frappe_security.py").read_text()
        for rule_id, fixture in (
            ("frappe-n-plus-one-read-in-comprehension", performance_fixture),
            ("frappe-whitelisted-raw-sql", security_fixture),
        ):
            self.assertIn(f"ruleid: {rule_id}", fixture)
            self.assertIn(f"ok: {rule_id}", fixture)

    def test_incomplete_censuses_cannot_be_blocking(self) -> None:
        packets = {
            payload["rule_id"]: payload
            for payload in (
                json.loads(path.read_text())
                for path in (ROOT / "governance/pilot/evidence").glob("*.json")
            )
        }
        decisions = {
            row["rule_id"]: row
            for row in self.load("governance/pilot/decisions-v1.json")["decisions"]
        }

        for rule_id, packet in packets.items():
            if not packet["engine_match_census"]["complete"]:
                self.assertNotEqual(decisions[rule_id]["enforcement_ceiling"], "blocking")

    def test_approved_adjudication_references_frozen_review_and_rules(self) -> None:
        adjudication = self.load("governance/pilot/adjudication-v1.json")

        self.assertEqual(adjudication["approval"]["owner"], "Vatsal")
        self.assertEqual(adjudication["approval"]["state"], "approved")
        self.assertEqual({row["rule_id"] for row in adjudication["decisions"]}, PILOTS)
        self.assertTrue(all(row["enforcement_ceiling"] == "audit-only" for row in adjudication["decisions"]))

        fixtures = {
            "frappe-async-foreach-callback": ROOT / "rules/custom/correctness/frappe_correctness.js",
            "frappe-malformed-sql-placeholder-list": ROOT / "rules/custom/correctness/frappe_correctness.py",
            "frappe-n-plus-one-read-in-comprehension": ROOT / "rules/custom/performance/frappe_performance.py",
            "frappe-whitelisted-raw-sql": ROOT / "rules/custom/security/frappe_security.py",
        }
        self.assertEqual(set(adjudication["new_rules"]), set(fixtures))
        for rule_id, fixture in fixtures.items():
            self.assertIn(f"ruleid: {rule_id}", fixture.read_text())


if __name__ == "__main__":
    unittest.main()
