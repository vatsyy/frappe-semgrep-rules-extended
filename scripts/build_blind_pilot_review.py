"""Build label-free review input and a frozen 70/30 allocation commitment."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

CLAIMS = {
    "frappe-async-array-callback-misuse": ("A", "Async array-callback semantics"),
    "override-doctype-class": ("B", "DocType controller-override compatibility"),
    "frappe-sql-format-injection": ("C", "Formatted SQL structure or data risk"),
    "frappe-whitelisted-permission-bypass": ("D", "Whitelisted permission-bypass boundary"),
    "frappe-n-plus-one-read-in-loop": ("E", "Database read per iterative item"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--review-input", type=Path, required=True)
    parser.add_argument("--allocation", type=Path, required=True)
    parser.add_argument("--result-template", type=Path, required=True)
    args = parser.parse_args()
    queue = json.loads(args.queue.read_text())
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in queue["records"]:
        groups[record["rule_id"]].append(record)

    review_claims = []
    allocations = {}
    for rule_id, records in sorted(groups.items(), key=lambda item: CLAIMS[item[0]][0]):
        claim_id, title = CLAIMS[rule_id]
        cases = []
        ranked = sorted(records, key=lambda item: hashlib.sha256(("pilot-allocation-v1\0" + item["id"]).encode()).hexdigest())
        development_count = len(ranked) if len(ranked) == 1 else (len(ranked) * 7) // 10
        allocations[claim_id] = {
            "development": [item["id"] for item in ranked[:development_count]],
            "holdout": [item["id"] for item in ranked[development_count:]],
            "deficit": "single-case population cannot supply both partitions" if len(ranked) == 1 else None,
        }
        for record in sorted(records, key=lambda item: item["id"]):
            cases.append({
                "case_id": record["id"],
                "application": record["application"],
                "path": record["path"],
                "line": record["line"],
                "context": record["context"],
                "label": "pending",
                "basis": "pending",
            })
        review_claims.append({"claim_id": claim_id, "title": title, "cases": cases})

    allocation = {
        "schema_version": 1,
        "method": "SHA-256-ranked 70/30 development/holdout allocation committed before independent labels",
        "allocations": allocations,
    }
    allocation_bytes = (json.dumps(allocation, indent=2, sort_keys=True) + "\n").encode()
    review = {
        "schema_version": 1,
        "instructions": "Label each case from source context only. Do not inspect rule YAML, authored evidence packets, decisions or allocation until labels are frozen.",
        "allocation_commitment_sha256": hashlib.sha256(allocation_bytes).hexdigest(),
        "claims": review_claims,
    }
    args.review_input.parent.mkdir(parents=True, exist_ok=True)
    args.allocation.parent.mkdir(parents=True, exist_ok=True)
    args.review_input.write_text(json.dumps(review, indent=2, sort_keys=True) + "\n")
    args.allocation.write_bytes(allocation_bytes)
    result_template = {
        "schema_version": 1,
        "blind_input_sha256": hashlib.sha256((json.dumps(review, indent=2, sort_keys=True) + "\n").encode()).hexdigest(),
        "allocation_commitment_sha256": hashlib.sha256(allocation_bytes).hexdigest(),
        "reviewer_identity": "pending",
        "reviewer_is_distinct_from_author": False,
        "authored_material_seen_before_labels_frozen": False,
        "labels_frozen_at": "pending",
        "cases": [
            {"case_id": case["case_id"], "label": "pending", "basis": "pending"}
            for claim in review_claims for case in claim["cases"]
        ],
        "claim_recommendations": [
            {"claim_id": claim_id, "outcome": "pending", "enforcement_ceiling": "pending", "rationale": "pending"}
            for claim_id in ("A", "B", "C", "D", "E")
        ],
    }
    args.result_template.parent.mkdir(parents=True, exist_ok=True)
    args.result_template.write_text(json.dumps(result_template, indent=2, sort_keys=True) + "\n")
    print(f"Blind review input written: {args.review_input}")
    print(f"Allocation commitment written: {args.allocation}")
    print(f"Blind review result template written: {args.result_template}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
