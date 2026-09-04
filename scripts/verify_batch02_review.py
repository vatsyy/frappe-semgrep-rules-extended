"""Verify the frozen independent-review result for Portfolio Review Batch 02."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path


CASE_LABELS = {"confirmed-issue", "safe-near-miss", "intentional-policy", "unresolved"}
CLAIM_OUTCOMES = {"accept", "narrow", "split", "audit-only", "retire", "unresolved"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-input", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()

    review_bytes = args.review_input.read_bytes()
    mapping_bytes = args.mapping.read_bytes()
    review = json.loads(review_bytes)
    result = json.loads(args.result.read_text())
    expected_cases = {case["case_id"] for claim in review["claims"] for case in claim["cases"]}
    expected_claims = {claim["claim_id"] for claim in review["claims"]}

    require(result["schema_version"] == 1, "unexpected result schema version")
    require(result["batch_id"] == review["batch_id"], "batch identity changed")
    require(result["blind_input_sha256"] == hashlib.sha256(review_bytes).hexdigest(), "blind input identity changed")
    require(result["mapping_commitment_sha256"] == hashlib.sha256(mapping_bytes).hexdigest(), "mapping identity changed")
    require(result["reviewer_identity"] not in {"", "Noema", "pending"}, "reviewer identity is pending")
    require(result["reviewer_is_distinct_from_author"] is True, "reviewer is not independent")
    require(result["authored_material_seen_before_labels_frozen"] is False, "reviewer saw authored material")
    require(result["labels_frozen_at"] not in {"", "pending"}, "labels are not frozen")

    started = datetime.fromisoformat(result["started_at"])
    ended = datetime.fromisoformat(result["ended_at"])
    require(ended >= started, "review timing is reversed")
    require(isinstance(result["reviewer_minutes"], (int, float)) and result["reviewer_minutes"] > 0, "reviewer minutes are missing")

    cases = result["cases"]
    require(len(cases) == len(expected_cases), "case result count is incomplete")
    require(len({case["case_id"] for case in cases}) == len(cases), "duplicate case result")
    require({case["case_id"] for case in cases} == expected_cases, "case identities differ")
    require(all(case["label"] in CASE_LABELS for case in cases), "invalid or pending case label")
    require(all(case["basis"].strip() not in {"", "pending"} for case in cases), "case basis is missing")

    recommendations = result["claim_recommendations"]
    require(len(recommendations) == len(expected_claims), "claim recommendation count is incomplete")
    require({row["claim_id"] for row in recommendations} == expected_claims, "claim identities differ")
    require(all(row["outcome"] in CLAIM_OUTCOMES for row in recommendations), "invalid claim outcome")
    require(all(row["enforcement_ceiling"].strip() not in {"", "pending"} for row in recommendations), "enforcement ceiling is missing")
    require(all(row["rationale"].strip() not in {"", "pending"} for row in recommendations), "claim rationale is missing")
    print("Batch 02 independent blind review verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
