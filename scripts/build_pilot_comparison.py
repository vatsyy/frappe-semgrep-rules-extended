"""Compare pilot-rule findings and coverage across two canonical all-app scans."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from compare_scan_findings import compare, records

PILOTS = {
    "frappe-async-array-callback-misuse",
    "override-doctype-class",
    "frappe-sql-format-injection",
    "frappe-whitelisted-permission-bypass",
    "frappe-n-plus-one-read-in-loop",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def combined(scan: Path) -> dict:
    aggregate = load(scan / "all-apps.json")
    findings = []
    scan_ids = []
    for app in aggregate["applications"]:
        payload = load(scan / "applications" / app["name"] / "findings.json")
        scan_ids.append(payload["scan_id"])
        for finding in payload["findings"]:
            finding = dict(finding)
            finding["path"] = f"{app['name']}/{finding['path']}"
            findings.append(finding)
    return {"scan_id": "+".join(scan_ids), "findings": findings}


def coverage_counts(path: Path) -> dict[str, int]:
    baseline = load(path)
    statuses: dict[str, int] = {}
    for app in baseline["applications"]:
        for name, count in app["counts"].items():
            statuses[name] = statuses.get(name, 0) + count
    return statuses


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--before-coverage", type=Path, required=True)
    parser.add_argument("--after-coverage", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    before = combined(args.before)
    after = combined(args.after)
    before_records = records(before)
    after_records = records(after)
    rules = {}
    for rule_id in sorted(PILOTS):
        old = [item for item in before_records if item["rule_id"] == rule_id]
        new = [item for item in after_records if item["rule_id"] == rule_id]
        drift = compare(old, new)
        rules[rule_id] = {
            "before": len(old), "after": len(new), "delta": len(new) - len(old),
            **drift["counts"],
        }
    old_counts = coverage_counts(args.before_coverage)
    new_counts = coverage_counts(args.after_coverage)
    introduced = {}
    for rule_id in (
        "frappe-async-foreach-callback",
        "frappe-malformed-sql-placeholder-list",
        "frappe-n-plus-one-read-in-comprehension",
        "frappe-whitelisted-raw-sql",
    ):
        introduced[rule_id] = sum(item["rule_id"] == rule_id for item in after_records)
    payload = {
        "schema_version": 1,
        "before_scan": args.before.as_posix(),
        "after_scan": args.after.as_posix(),
        "rules": rules,
        "introduced_rules": introduced,
        "coverage": {
            "before_unanalysed": old_counts.get("unanalysed", 0),
            "after_unanalysed": new_counts.get("unanalysed", 0),
            "before_fully_analysed": old_counts.get("fully-analysed", 0),
            "after_fully_analysed": new_counts.get("fully-analysed", 0),
            "before_partially_analysed": old_counts.get("partially-analysed", 0),
            "after_partially_analysed": new_counts.get("partially-analysed", 0),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"Pilot comparison written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
