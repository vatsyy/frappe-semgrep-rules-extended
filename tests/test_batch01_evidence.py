from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_RULES = {
    "frappe-codeinjection-eval",
    "frappe-ssti",
    "frappe-subprocess-shell-true",
    "frappe-set-value-semantics",
    "unchecked-frappe-permission-call",
}


class Batch01EvidenceTest(unittest.TestCase):
    def load(self, relative: str) -> dict:
        return json.loads((ROOT / relative).read_text())

    def test_selection_evidence_and_decisions_cover_same_rules(self) -> None:
        selection = self.load("governance/review-cuts/portfolio-review-batch-01-v1.json")
        evidence = self.load("governance/review-batches/batch-01/evidence-v1.json")
        decisions = self.load("governance/review-batches/batch-01/decisions-v1.json")

        self.assertEqual({row["rule_id"] for row in selection["rules"]}, BATCH_RULES)
        self.assertEqual({row["rule_id"] for row in evidence["rules"]}, BATCH_RULES)
        self.assertEqual({row["rule_id"] for row in decisions["decisions"]}, BATCH_RULES)

    def test_review_counts_are_bounded_and_nonblocking(self) -> None:
        evidence = self.load("governance/review-batches/batch-01/evidence-v1.json")
        decisions = {
            row["rule_id"]: row
            for row in self.load("governance/review-batches/batch-01/decisions-v1.json")["decisions"]
        }

        for row in evidence["rules"]:
            self.assertLessEqual(row["sample"], row["population"])
            self.assertEqual(sum(row["labels"].values()), row["sample"])
            if row["sample"] < row["population"]:
                self.assertNotEqual(decisions[row["rule_id"]]["enforcement_ceiling"], "blocking")

    def test_new_rules_have_positive_and_negative_controls(self) -> None:
        decisions = self.load("governance/review-batches/batch-01/decisions-v1.json")
        fixture = (ROOT / "rules/custom/security/frappe_security.py").read_text()

        for rule_id in decisions["new_rules"]:
            self.assertIn(f"ruleid: {rule_id}", fixture)
            self.assertIn(f"ok: {rule_id}", fixture)

    def test_final_scan_preserves_sources_and_has_no_unanalysed_targets(self) -> None:
        comparison = self.load("governance/review-batches/batch-01/comparison-v1.json")

        self.assertTrue(comparison["source_identity_unchanged_for_all_seven_apps"])
        self.assertTrue(comparison["application_worktree_status_unchanged_for_all_seven_apps"])
        self.assertTrue(comparison["coverage"]["parser_error_count_unchanged"])
        self.assertEqual(comparison["coverage"]["unanalysed"], 0)
        self.assertEqual(
            {row["reviewed_rule"] for row in comparison["rule_comparisons"]},
            BATCH_RULES,
        )

    def test_approved_adjudication_freezes_evidence_and_keeps_candidates_nonblocking(self) -> None:
        adjudication = self.load("governance/review-batches/batch-01/adjudication-v1.json")

        self.assertEqual(adjudication["approval"]["owner"], "Vatsal")
        self.assertEqual(adjudication["approval"]["state"], "approved")
        self.assertEqual({row["rule_id"] for row in adjudication["decisions"]}, BATCH_RULES)
        self.assertEqual(
            {row["rule_id"]: row["outcome"] for row in adjudication["decisions"]},
            {
                "frappe-codeinjection-eval": "split",
                "frappe-ssti": "split",
                "frappe-subprocess-shell-true": "narrow",
                "frappe-set-value-semantics": "retire",
                "unchecked-frappe-permission-call": "audit-only",
            },
        )
        self.assertEqual(adjudication["admitted_rules"], [])
        self.assertFalse(adjudication["execution"]["executable_rule_tree_changed"])
        self.assertEqual(adjudication["execution"]["post_adjudication_scan"], "not-required")
        retained_scan = ROOT / adjudication["execution"]["retained_scan"] / "all-apps.json"
        retained = json.loads(retained_scan.read_text())
        for application in retained["applications"]:
            provenance = self.load(
                f"{adjudication['execution']['retained_scan']}/applications/"
                f"{application['name']}/provenance.json"
            )
            self.assertEqual(
                provenance["rules"]["content_sha256"],
                adjudication["execution"]["rules_content_sha256"],
            )

        for evidence_key in ("authored_decisions", "independent_review", "comparison"):
            evidence = adjudication[evidence_key]
            evidence_hash = hashlib.sha256((ROOT / evidence["path"]).read_bytes()).hexdigest()
            self.assertEqual(evidence_hash, evidence["sha256"])

    def test_remaining_plan_is_exact_and_only_tickets_the_next_batch(self) -> None:
        cut = self.load("governance/review-cuts/portfolio-review-cut-v1.json")
        pilot = self.load("governance/pilot/adjudication-v1.json")
        batch_01 = self.load("governance/review-batches/batch-01/adjudication-v1.json")
        plan = self.load("governance/review-cuts/remaining-portfolio-plan-v1.json")

        reviewed = {row["rule_id"] for row in pilot["decisions"]} | {
            row["rule_id"] for row in batch_01["decisions"]
        }
        remaining_rows = [row for row in cut["queue"] if row["rule_id"] not in reviewed]
        remaining_ids = {row["rule_id"] for row in remaining_rows}
        self.assertEqual(set(plan["remaining_cut"]["rule_ids"]), remaining_ids)
        self.assertEqual(plan["remaining_cut"]["rule_count"], len(remaining_rows))
        self.assertEqual(
            plan["remaining_cut"]["finding_count"],
            sum(row["match_count"] for row in remaining_rows),
        )
        self.assertEqual(
            plan["remaining_cut"]["suppression_count"],
            sum(row["suppression_count"] for row in remaining_rows),
        )

        next_batch_ids = {row["rule_id"] for row in plan["next_batch"]["rules"]}
        self.assertEqual(
            next_batch_ids,
            {"frappe-security-file-traversal", "frappe-subprocess-exec"},
        )
        self.assertLessEqual(next_batch_ids, remaining_ids)
        self.assertEqual(
            plan["later_candidates"]["rule_count"],
            len(remaining_ids - next_batch_ids),
        )
        self.assertEqual(plan["later_candidates"]["ticket_state"], "not-yet-ticketed")

        ticket_29 = (ROOT / ".scratch/trustworthy-semgrep-foundation/issues/29-prepare-host-boundary-review-batch.md").read_text()
        ticket_30 = (ROOT / ".scratch/trustworthy-semgrep-foundation/issues/30-independently-decide-host-boundary-review-batch.md").read_text()
        for rule_id in next_batch_ids:
            self.assertIn(rule_id, ticket_29)
        self.assertIn("29: Prepare the host-boundary Review Batch", ticket_30)

if __name__ == "__main__":
    unittest.main()
