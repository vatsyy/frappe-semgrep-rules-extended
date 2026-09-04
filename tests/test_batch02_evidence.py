from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BATCH_RULES = {"frappe-security-file-traversal", "frappe-subprocess-exec"}
NEW_RULES = {"frappe-whitelisted-direct-file-path", "frappe-interpolated-execute-in-shell"}


class Batch02EvidenceTest(unittest.TestCase):
    def load(self, relative: str) -> dict:
        return json.loads((ROOT / relative).read_text())

    def test_selection_queue_review_evidence_and_decisions_are_complete(self) -> None:
        selection = self.load("governance/review-cuts/portfolio-review-batch-02-v1.json")
        queue = self.load(".scratch/trustworthy-semgrep-foundation/batches/batch-02-review-queue-v1.json")
        review = self.load("governance/review-batches/batch-02/authored-review-v1.json")
        evidence = self.load("governance/review-batches/batch-02/evidence-v1.json")
        decisions = self.load("governance/review-batches/batch-02/decisions-v1.json")

        self.assertEqual({row["rule_id"] for row in selection["rules"]}, BATCH_RULES)
        self.assertEqual({row["rule_id"] for row in queue["records"]}, BATCH_RULES)
        self.assertEqual({row["rule_id"] for row in evidence["rules"]}, BATCH_RULES)
        self.assertEqual({row["rule_id"] for row in decisions["decisions"]}, BATCH_RULES)
        queue_ids = [row["case_id"] for row in queue["records"]]
        review_ids = [row["case_id"] for row in review["cases"]]
        self.assertEqual(len(queue_ids), 56)
        self.assertEqual(len(queue_ids), len(set(queue_ids)))
        self.assertEqual(set(queue_ids), set(review_ids))
        self.assertNotIn("unresolved", {row["label"] for row in review["cases"]})

    def test_sampled_claims_remain_nonblocking(self) -> None:
        evidence = {row["rule_id"]: row for row in self.load("governance/review-batches/batch-02/evidence-v1.json")["rules"]}
        decisions = {row["rule_id"]: row for row in self.load("governance/review-batches/batch-02/decisions-v1.json")["decisions"]}
        self.assertLess(evidence["frappe-security-file-traversal"]["sample"], evidence["frappe-security-file-traversal"]["population"])
        for rule_id in BATCH_RULES:
            self.assertEqual(decisions[rule_id]["enforcement_ceiling"], "audit-only")

    def test_new_rules_have_positive_and_negative_controls(self) -> None:
        fixture = (ROOT / "rules/custom/security/frappe_security.py").read_text()
        decisions = self.load("governance/review-batches/batch-02/decisions-v1.json")
        self.assertEqual(set(decisions["new_rules"]), NEW_RULES)
        for rule_id in NEW_RULES:
            self.assertIn(f"ruleid: {rule_id}", fixture)
            self.assertIn(f"ok: {rule_id}", fixture)

    def test_authored_scan_preserves_all_sources_and_parser_accounting(self) -> None:
        comparison = self.load("governance/review-batches/batch-02/comparison-v1.json")
        before = self.load(f"{comparison['before_scan']}/all-apps.json")
        after = self.load(f"{comparison['after_scan']}/all-apps.json")
        before_apps = {row["name"]: row for row in before["applications"]}
        after_apps = {row["name"]: row for row in after["applications"]}

        self.assertEqual(set(before_apps), set(after_apps))
        self.assertEqual(len(after_apps), 7)
        for name in before_apps:
            self.assertEqual(before_apps[name]["source"]["content_sha256"], after_apps[name]["source"]["content_sha256"])
            self.assertEqual(before_apps[name]["source"]["status_sha256"], after_apps[name]["source"]["status_sha256"])
        self.assertEqual(sum(row["error_count"] for row in before_apps.values()), 14)
        self.assertEqual(sum(row["error_count"] for row in after_apps.values()), 14)
        self.assertEqual(after["finding_count"] - before["finding_count"], 5)

    def test_blind_packet_is_committed_and_rule_identity_free(self) -> None:
        input_path = ROOT / ".scratch/trustworthy-semgrep-foundation/batches/batch-02-blind-review-input-v1.json"
        mapping_path = ROOT / ".scratch/trustworthy-semgrep-foundation/batches/batch-02-claim-mapping-v1.json"
        result = self.load(".scratch/trustworthy-semgrep-foundation/batches/batch-02-blind-review-result-v1.json")
        packet_text = input_path.read_text()
        mapping_hash = hashlib.sha256(mapping_path.read_bytes()).hexdigest()

        self.assertNotIn("frappe-security-file-traversal", packet_text)
        self.assertNotIn("frappe-subprocess-exec", packet_text)
        self.assertNotIn("nosemgrep", packet_text.lower())
        self.assertNotIn("noqa: semgrep", packet_text.lower())
        self.assertEqual(result["mapping_commitment_sha256"], mapping_hash)
        self.assertEqual(result["blind_input_sha256"], hashlib.sha256(input_path.read_bytes()).hexdigest())
        self.assertEqual(len(result["cases"]), 56)
        self.assertNotEqual(result["reviewer_identity"], "Noema")
        self.assertTrue(result["reviewer_is_distinct_from_author"])
        self.assertFalse(result["authored_material_seen_before_labels_frozen"])
        self.assertEqual(len({row["case_id"] for row in result["cases"]}), 56)
        self.assertGreater(result["reviewer_minutes"], 0)

    def test_independent_comparison_preserves_both_reviews(self) -> None:
        authored = self.load("governance/review-batches/batch-02/authored-review-v1.json")
        independent = self.load(".scratch/trustworthy-semgrep-foundation/batches/batch-02-blind-review-result-v1.json")
        comparison = self.load("governance/review-batches/batch-02/independent-comparison-v1.json")

        self.assertEqual(comparison["agreement"]["case_count"], 56)
        self.assertEqual(
            comparison["agreement"]["agreed_case_count"] + comparison["agreement"]["disagreed_case_count"],
            56,
        )
        self.assertEqual({row["case_id"] for row in authored["cases"]}, {row["case_id"] for row in independent["cases"]})
        self.assertEqual({row["enforcement_ceiling"] for row in comparison["claim_recommendations"]}, {"audit-only"})

    def test_focused_audit_covers_only_settled_candidates_and_preserves_sources(self) -> None:
        audit = self.load("governance/review-batches/batch-02/focused-rule-audit-v1.json")
        scan = self.load(f"{audit['scan']['path']}/all-apps.json")
        prior = self.load("scan-results/batch-02-authored-20260826/all-apps.json")

        self.assertEqual(set(audit["audit_scope"]), NEW_RULES)
        self.assertEqual(len(audit["findings"]), 11)
        self.assertEqual(audit["interpretation"]["confirmed_structural_issue_count"], 10)
        self.assertEqual(audit["interpretation"]["safe_near_miss_count"], 1)
        self.assertEqual(sum(row["error_count"] for row in scan["applications"]), 14)
        self.assertEqual(
            {row["name"]: (row["source"]["content_sha256"], row["source"]["status_sha256"]) for row in scan["applications"]},
            {row["name"]: (row["source"]["content_sha256"], row["source"]["status_sha256"]) for row in prior["applications"]},
        )
        karam = next(row for row in scan["applications"] if row["name"] == "karam_finance")
        self.assertEqual(karam["finding_count"], 9)


if __name__ == "__main__":
    unittest.main()
