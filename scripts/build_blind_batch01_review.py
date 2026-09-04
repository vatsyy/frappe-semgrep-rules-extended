"""Build a label-free independent-review packet for Portfolio Review Batch 01."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


CLAIMS = {
    "frappe-codeinjection-eval": ("A", "Dynamic Python execution and dispatch calls"),
    "frappe-ssti": ("B", "Server-side template rendering calls"),
    "frappe-subprocess-shell-true": ("C", "Subprocess calls with a shell enabled"),
    "frappe-set-value-semantics": ("D", "Database value mutation calls"),
    "unchecked-frappe-permission-call": ("E", "Permission-check expression use"),
}


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def blind_context(context: str) -> str:
    """Remove suppression annotations that reveal a rule identity or prior judgement."""
    return "\n".join(
        line for line in context.splitlines() if not re.search(r"(?:no)?semgrep", line, re.IGNORECASE)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--review-input", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--result-template", type=Path, required=True)
    args = parser.parse_args()

    queue = json.loads(args.queue.read_text())
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in queue["records"]:
        groups[record["rule_id"]].append(record)
    if set(groups) != set(CLAIMS):
        raise ValueError(f"unexpected Batch 01 rule set: {sorted(groups)}")

    claims = []
    mapping_claims = []
    for rule_id, records in sorted(groups.items(), key=lambda item: CLAIMS[item[0]][0]):
        claim_id, title = CLAIMS[rule_id]
        cases = [
            {
                "application": record["application"],
                "case_id": record["case_id"],
                "context": blind_context(record["context"]),
                "line": record["line"],
                "path": record["path"],
            }
            for record in sorted(records, key=lambda item: item["case_id"])
        ]
        claims.append({"claim_id": claim_id, "title": title, "cases": cases})
        mapping_claims.append(
            {
                "claim_id": claim_id,
                "population": queue["populations"][rule_id],
                "rule_id": rule_id,
                "selected_cases": len(cases),
            }
        )

    mapping = {
        "batch_id": queue["batch_id"],
        "claims": mapping_claims,
        "sampling": queue["sampling"],
        "schema_version": 1,
    }
    mapping_bytes = canonical_bytes(mapping)
    review = {
        "batch_id": queue["batch_id"],
        "instructions": {
            "blindness": "Use this packet and its source contexts only. Do not inspect rule YAML, fixtures, authored evidence, authored decisions, comparisons, the original queue, or the opaque-claim mapping before returning final labels.",
            "case_labels": ["confirmed-issue", "safe-near-miss", "intentional-policy", "unresolved"],
            "case_task": "Label every case and give a concise source-based basis.",
            "claim_outcomes": ["accept", "narrow", "split", "audit-only", "retire", "unresolved"],
            "claim_task": "Recommend one outcome and enforcement ceiling for every opaque claim, based only on the reviewed sample.",
            "limits": "Static source context may establish a structural concern but cannot prove runtime exploitability, frequency, latency, or business impact.",
        },
        "mapping_commitment_sha256": hashlib.sha256(mapping_bytes).hexdigest(),
        "claims": claims,
        "schema_version": 1,
    }
    review_bytes = canonical_bytes(review)
    result_template = {
        "batch_id": queue["batch_id"],
        "blind_input_sha256": hashlib.sha256(review_bytes).hexdigest(),
        "mapping_commitment_sha256": hashlib.sha256(mapping_bytes).hexdigest(),
        "reviewer_identity": "pending",
        "reviewer_is_distinct_from_author": False,
        "authored_material_seen_before_labels_frozen": False,
        "labels_frozen_at": "pending",
        "cases": [
            {"basis": "pending", "case_id": case["case_id"], "label": "pending"}
            for claim in claims
            for case in claim["cases"]
        ],
        "claim_recommendations": [
            {
                "claim_id": claim["claim_id"],
                "enforcement_ceiling": "pending",
                "outcome": "pending",
                "rationale": "pending",
            }
            for claim in claims
        ],
        "schema_version": 1,
    }

    for path in (args.review_input, args.mapping, args.result_template):
        path.parent.mkdir(parents=True, exist_ok=True)
    args.review_input.write_bytes(review_bytes)
    args.mapping.write_bytes(mapping_bytes)
    args.result_template.write_bytes(canonical_bytes(result_template))
    print(f"Blind review input written: {args.review_input}")
    print(f"Opaque-claim mapping commitment written: {args.mapping}")
    print(f"Blind review result template written: {args.result_template}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
