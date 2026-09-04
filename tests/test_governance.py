from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "check_governance.py"


def candidate_claim() -> dict[str, object]:
    return {
        "id": "validation-only.example",
        "rule_id": "frappe-validation-only-example",
        "rule_path": "tests/fixtures/validation-only.yml",
        "ownership": "noospheric",
        "provenance": {
            "kind": "validation-only",
            "source": "tests/test_governance.py",
        },
        "contract": {
            "claim": "A validation-only construct is present.",
            "claim_class": "deterministic-defect",
            "enforcement_ceiling": "blocking",
            "scope": {
                "languages": ["python"],
                "framework_versions": ["frappe-v16"],
                "paths": ["tests/fixtures"],
                "file_kinds": ["source"],
                "analysis_mode": "structural",
                "boundary": "single-file",
                "prerequisites": [],
                "exclusions": [],
            },
            "assumptions": [],
            "rule_confidence": {"status": "unmeasured"},
            "observed_construct": "Validation-only fixture construct.",
            "remediation_or_next_evidence": "Attach independently reviewed source evidence.",
            "limitations": ["Cannot provide admission evidence."],
            "provenance": ["tests/test_governance.py"],
            "references": ["CONTEXT.md"],
            "message": {
                "observation": "The validation-only construct was matched.",
                "claim": "The local syntax is present.",
                "non_claims": ["This is not acceptance evidence."],
                "next_action": "Collect source-backed evidence.",
            },
        },
        "state": {"lifecycle": "candidate", "outcome": None},
        "admission": None,
        "predecessors": [],
        "replacements": [],
    }


def admitted_claim(outcome: str, claim_class: str, ceiling: str) -> dict[str, object]:
    claim = candidate_claim()
    claim["id"] = f"admitted.{outcome}"
    claim["rule_id"] = f"frappe-admitted-{outcome}"
    claim["provenance"] = {
        "kind": "source-backed",
        "source": "frappe@example.py:1",
        "revision": "1" * 40,
    }
    contract = claim["contract"]
    assert isinstance(contract, dict)
    contract["claim_class"] = claim_class
    contract["enforcement_ceiling"] = ceiling
    contract["rule_confidence"] = {
        "status": "measured",
        "evidence_packet": "evidence/example-v1.json",
    }
    claim["state"] = {"lifecycle": "accepted", "outcome": outcome}
    claim["admission"] = {
        "universal_gates": {
            "truthful_claim": True,
            "complete_contract": True,
            "native_tests": True,
            "independent_positive": True,
            "independent_safe_near_miss": True,
            "declared_compatibility": True,
            "distinct_value": True,
        },
        "parser_scope_complete": True,
        "assumptions_established": True,
        "reviewed_false_positives": 0,
        "unresolved_cases": 0,
        "known_positive_cases": 1,
        "detected_known_positive_cases": 1,
        "holdout_passed": True,
        "independent_review": True,
        "vatsal_approval": True,
        "baseline_triage": {
            "population": "census",
            "matches_total": 1,
            "matches_triaged": 1,
            "suppressions_total": 0,
            "suppressions_triaged": 0,
        },
    }
    return claim


class GovernanceValidatorTest(unittest.TestCase):
    def run_validator(
        self,
        claims: list[dict[str, object]],
        *,
        retired_ids: list[str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        payload = {
            "schema_version": 1,
            "catalogue_id": "test-catalogue",
            "claims": claims,
            "retired_ids": retired_ids or [],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalogue.json"
            path.write_text(json.dumps(payload))
            return subprocess.run(
                [sys.executable, str(VALIDATOR), "--catalogue", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

    def test_validation_only_candidate_is_representable_but_not_admitted(self) -> None:
        result = self.run_validator([candidate_claim()])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 claim", result.stdout)

    def test_incomplete_rule_contract_is_rejected_actionably(self) -> None:
        claim = candidate_claim()
        del claim["contract"]["message"]  # type: ignore[index]

        result = self.run_validator([claim])

        self.assertEqual(result.returncode, 1)
        self.assertIn("contract.message is required", result.stderr)

    def test_each_truthful_outcome_has_a_valid_non_compensating_path(self) -> None:
        cases = {
            "blocking": admitted_claim("blocking", "deterministic-defect", "blocking"),
            "monitor": admitted_claim("monitor", "explicit-policy-violation", "monitor"),
            "audit": admitted_claim("audit", "review-hotspot", "audit"),
        }
        outside = candidate_claim()
        outside["id"] = "outside.example"
        outside["state"] = {"lifecycle": "candidate", "outcome": "outside-portfolio"}
        cases["outside-portfolio"] = outside

        for outcome, claim in cases.items():
            with self.subTest(outcome=outcome):
                result = self.run_validator([claim])
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_strong_evidence_cannot_compensate_for_incomplete_blocking_census(self) -> None:
        claim = admitted_claim("blocking", "deterministic-defect", "blocking")
        admission = claim["admission"]
        assert isinstance(admission, dict)
        census = admission["baseline_triage"]
        assert isinstance(census, dict)
        census["matches_triaged"] = 0

        result = self.run_validator([claim])

        self.assertEqual(result.returncode, 1)
        self.assertIn("complete Baseline Triage census", result.stderr)

    def test_policy_claim_cannot_block_without_identified_written_policy(self) -> None:
        claim = admitted_claim(
            "blocking", "explicit-policy-violation", "blocking"
        )

        result = self.run_validator([claim])

        self.assertEqual(result.returncode, 1)
        self.assertIn("identified written policy", result.stderr)

    def test_missing_universal_gate_cannot_be_hidden_by_other_true_values(self) -> None:
        claim = admitted_claim("monitor", "explicit-policy-violation", "monitor")
        admission = claim["admission"]
        assert isinstance(admission, dict)
        del admission["universal_gates"]["independent_safe_near_miss"]  # type: ignore[index]

        result = self.run_validator([claim])

        self.assertEqual(result.returncode, 1)
        self.assertIn("independent_safe_near_miss", result.stderr)

    def test_validation_only_source_cannot_be_accepted(self) -> None:
        claim = admitted_claim("monitor", "explicit-policy-violation", "monitor")
        claim["provenance"] = deepcopy(candidate_claim()["provenance"])

        result = self.run_validator([claim])

        self.assertEqual(result.returncode, 1)
        self.assertIn("validation-only provenance cannot admit a rule", result.stderr)

    def test_accepted_rule_requires_measured_confidence_evidence(self) -> None:
        claim = admitted_claim("audit", "review-hotspot", "audit")
        claim["contract"]["rule_confidence"] = {"status": "unmeasured"}  # type: ignore[index]

        result = self.run_validator([claim])

        self.assertEqual(result.returncode, 1)
        self.assertIn("measured Rule Confidence", result.stderr)

    def test_duplicate_and_retired_id_reuse_are_rejected(self) -> None:
        claim = candidate_claim()

        duplicate = self.run_validator([claim, deepcopy(claim)])
        reused = self.run_validator([claim], retired_ids=[str(claim["id"])])

        self.assertEqual(duplicate.returncode, 1)
        self.assertIn("duplicate claim id", duplicate.stderr)
        self.assertEqual(reused.returncode, 1)
        self.assertIn("reuses retired identity", reused.stderr)

    def test_upstream_parity_retirement_preserves_both_linked_identities(self) -> None:
        retired = candidate_claim()
        retired["id"] = "noospheric.redundant"
        retired["state"] = {"lifecycle": "retired", "outcome": "outside-portfolio"}
        retired["retirement"] = {
            "reason": "upstream-parity",
            "replacement": "upstream.equivalent",
        }
        retired["replacements"] = ["upstream.equivalent"]
        successor = candidate_claim()
        successor["id"] = "upstream.equivalent"
        successor["rule_id"] = "frappe-upstream-equivalent"
        successor["predecessors"] = ["noospheric.redundant"]

        result = self.run_validator(
            [retired, successor], retired_ids=["noospheric.redundant"]
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_urgency_cannot_bypass_admission(self) -> None:
        claim = admitted_claim("monitor", "explicit-policy-violation", "monitor")
        claim["urgency"] = "critical"
        admission = claim["admission"]
        assert isinstance(admission, dict)
        admission["universal_gates"]["independent_positive"] = False  # type: ignore[index]

        result = self.run_validator([claim])

        self.assertEqual(result.returncode, 1)
        self.assertIn("advisory-only", result.stderr)

    def test_urgent_candidate_requires_explicit_advisory_only_state(self) -> None:
        claim = candidate_claim()
        claim["urgency"] = "critical"
        claim["advisory_only"] = True

        result = self.run_validator([claim])

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_identities_paths_provenance_and_references_are_stable(self) -> None:
        invalid_claims = {
            "claim identity": ("id", "Invalid Identity"),
            "rule identity": ("rule_id", "Invalid Rule"),
            "rule path": ("rule_path", "../outside.yml"),
        }
        for label, (field, value) in invalid_claims.items():
            with self.subTest(field=label):
                claim = candidate_claim()
                claim[field] = value
                result = self.run_validator([claim])
                self.assertEqual(result.returncode, 1)
                self.assertIn(field, result.stderr)

        missing_reference = candidate_claim()
        missing_reference["contract"]["references"] = []  # type: ignore[index]
        result = self.run_validator([missing_reference])
        self.assertEqual(result.returncode, 1)
        self.assertIn("references", result.stderr)

    def test_retired_state_requires_canonical_retired_identity_record(self) -> None:
        claim = candidate_claim()
        claim["state"] = {"lifecycle": "retired", "outcome": "outside-portfolio"}

        result = self.run_validator([claim])

        self.assertEqual(result.returncode, 1)
        self.assertIn("recorded in retired_ids", result.stderr)

    def test_sampled_measurement_cannot_claim_exact_precision(self) -> None:
        claim = candidate_claim()
        claim["measurements"] = {
            "population": "sample",
            "precision": 1.0,
        }

        result = self.run_validator([claim])

        self.assertEqual(result.returncode, 1)
        self.assertIn("exact rates require an enumerated population", result.stderr)

    def test_malformed_scope_and_provenance_are_rejected_actionably(self) -> None:
        malformed_scope = candidate_claim()
        malformed_scope["contract"]["scope"]["languages"] = []  # type: ignore[index]
        malformed_provenance = candidate_claim()
        malformed_provenance["provenance"] = "invented"

        scope_result = self.run_validator([malformed_scope])
        provenance_result = self.run_validator([malformed_provenance])

        self.assertEqual(scope_result.returncode, 1)
        self.assertIn("scope.languages", scope_result.stderr)
        self.assertEqual(provenance_result.returncode, 1)
        self.assertIn("provenance must be an object", provenance_result.stderr)

    def test_malformed_lifecycle_returns_an_actionable_contract_error(self) -> None:
        claim = candidate_claim()
        claim["state"] = "candidate"

        result = self.run_validator([claim])

        self.assertEqual(result.returncode, 1)
        self.assertIn("state must be an object", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_blocking_requires_established_assumptions_and_real_positive_counts(self) -> None:
        missing_assumptions = admitted_claim(
            "blocking", "deterministic-defect", "blocking"
        )
        del missing_assumptions["admission"]["assumptions_established"]  # type: ignore[index]
        missing_counts = admitted_claim(
            "blocking", "deterministic-defect", "blocking"
        )
        del missing_counts["admission"]["known_positive_cases"]  # type: ignore[index]
        del missing_counts["admission"]["detected_known_positive_cases"]  # type: ignore[index]

        assumptions_result = self.run_validator([missing_assumptions])
        counts_result = self.run_validator([missing_counts])

        self.assertEqual(assumptions_result.returncode, 1)
        self.assertIn("blocking Admission Gate", assumptions_result.stderr)
        self.assertEqual(counts_result.returncode, 1)
        self.assertIn("known positive counts", counts_result.stderr)


if __name__ == "__main__":
    unittest.main()
