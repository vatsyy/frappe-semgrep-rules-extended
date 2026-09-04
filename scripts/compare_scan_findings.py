"""Compare two retained finding sets without treating line movement as churn."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def records(payload: dict) -> list[dict[str, str]]:
    result = []
    occurrences: dict[tuple[str, str, str], int] = defaultdict(int)
    ordered = sorted(payload["findings"], key=lambda item: (
        item["check_id"], str(item["path"]), item.get("extra", {}).get("lines", "").strip(),
        item.get("start", {}).get("line", 0), item.get("start", {}).get("col", 0),
    ))
    for finding in ordered:
        rule = finding["check_id"]
        path = str(finding["path"]).removeprefix("./")
        snippet = finding.get("extra", {}).get("lines", "").strip()
        shape = (rule, path, snippet)
        ordinal = occurrences[shape]
        occurrences[shape] += 1
        result.append({
            "rule_id": rule,
            "path_id": digest(path),
            "snippet_id": digest(snippet),
            "finding_id": digest(f"{rule}\0{path}\0{snippet}\0{ordinal}"),
        })
    return sorted(result, key=lambda item: item["finding_id"])


def compare(before: list[dict[str, str]], after: list[dict[str, str]]) -> dict:
    old = {item["finding_id"]: item for item in before}
    new = {item["finding_id"]: item for item in after}
    persisting = sorted(old.keys() & new.keys())
    old_only = [old[key] for key in sorted(old.keys() - new.keys())]
    new_only = [new[key] for key in sorted(new.keys() - old.keys())]
    by_shape: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for item in new_only:
        by_shape[(item["rule_id"], item["snippet_id"])].append(item)
    moved = []
    resolved = []
    consumed: set[str] = set()
    for item in old_only:
        candidates = by_shape[(item["rule_id"], item["snippet_id"])]
        candidate = next((x for x in candidates if x["finding_id"] not in consumed), None)
        if candidate:
            consumed.add(candidate["finding_id"])
            moved.append({"before": item["finding_id"], "after": candidate["finding_id"]})
        else:
            resolved.append(item["finding_id"])
    introduced = [item["finding_id"] for item in new_only if item["finding_id"] not in consumed]
    return {
        "persisting": persisting,
        "moved": moved,
        "new": sorted(introduced),
        "resolved": sorted(resolved),
        "counts": {
            "persisting": len(persisting), "moved": len(moved),
            "new": len(introduced), "resolved": len(resolved),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    old = json.loads(args.before.read_text())
    new = json.loads(args.after.read_text())
    result = {"schema_version": 1, "before_scan_id": old["scan_id"],
              "after_scan_id": new["scan_id"], **compare(records(old), records(new))}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"Finding comparison written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
