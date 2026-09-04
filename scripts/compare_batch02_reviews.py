"""Compare frozen authored and independent Batch 02 labels without overwriting either."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authored", type=Path, required=True)
    parser.add_argument("--independent", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    authored = json.loads(args.authored.read_text())
    independent = json.loads(args.independent.read_text())
    mapping = json.loads(args.mapping.read_text())
    queue = json.loads(args.queue.read_text())
    authored_cases = {row["case_id"]: row for row in authored["cases"]}
    independent_cases = {row["case_id"]: row for row in independent["cases"]}
    case_rules = {row["case_id"]: row["rule_id"] for row in queue["records"]}
    if set(authored_cases) != set(independent_cases) or set(authored_cases) != set(case_rules):
        raise ValueError("review case identities differ")

    disagreements = []
    pairs = Counter()
    for case_id in sorted(authored_cases):
        left = authored_cases[case_id]["label"]
        right = independent_cases[case_id]["label"]
        pairs[(left, right)] += 1
        if left != right:
            disagreements.append({
                "authored_label": left,
                "case_id": case_id,
                "independent_label": right,
                "rule_id": case_rules[case_id],
            })

    claim_rules = {row["claim_id"]: row["rule_id"] for row in mapping["claims"]}
    output = {
        "agreement": {
            "agreed_case_count": len(authored_cases) - len(disagreements),
            "case_count": len(authored_cases),
            "disagreed_case_count": len(disagreements),
            "label_pairs": [
                {"authored": left, "count": count, "independent": right}
                for (left, right), count in sorted(pairs.items())
            ],
        },
        "batch_id": authored["batch_id"],
        "claim_recommendations": [
            {**row, "rule_id": claim_rules[row["claim_id"]]}
            for row in independent["claim_recommendations"]
        ],
        "disagreements": disagreements,
        "independent_reviewer": independent["reviewer_identity"],
        "reviewer_minutes": independent["reviewer_minutes"],
        "schema_version": 1,
    }
    write_json(args.output, output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
