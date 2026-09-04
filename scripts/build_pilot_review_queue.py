"""Build a deterministic, stratified private source-review queue for pilot rules."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

PILOTS = {
    "frappe-async-array-callback-misuse",
    "override-doctype-class",
    "frappe-sql-format-injection",
    "frappe-whitelisted-permission-bypass",
    "frappe-n-plus-one-read-in-loop",
}
SMALL = {"frappe-async-array-callback-misuse", "override-doctype-class"}


def cluster(rule_id: str, finding: dict[str, Any]) -> str:
    lines = finding.get("extra", {}).get("lines", "")
    metavars = finding.get("extra", {}).get("metavars", {})
    if rule_id == "frappe-async-array-callback-misuse":
        match = re.search(r"\.(forEach|filter|find|some|every|sort)\s*\(", lines)
        return match.group(1) if match else "async-array-callback"
    if rule_id == "override-doctype-class":
        return "controller-override"
    if rule_id == "frappe-sql-format-injection":
        if ".format(" in lines:
            return "format-call"
        return "f-string"
    if rule_id == "frappe-whitelisted-permission-bypass":
        if "frappe.get_all" in lines:
            return "get-all"
        if "frappe.get_list" in lines:
            return "get-list-ignore"
        if "ignore_permissions" in lines:
            return "document-ignore"
        return "other-bypass"
    return metavars.get("$READ", {}).get("abstract_content") or (
        "frappe.get_doc" if "$DOCTYPE" in metavars else "frappe.db.sql"
    )


def identity(app: str, finding: dict[str, Any]) -> str:
    value = "\0".join((
        finding["check_id"], app, finding["path"],
        str(finding["start"]["line"]), finding.get("extra", {}).get("lines", ""),
    ))
    return hashlib.sha256(value.encode()).hexdigest()


def context(source: Path, start: int, end: int, radius: int = 12) -> tuple[int, str]:
    lines = source.read_text(errors="replace").splitlines()
    first = max(1, start - radius)
    last = min(len(lines), end + radius)
    return first, "\n".join(f"{line_no}: {lines[line_no - 1]}" for line_no in range(first, last + 1))


def build(scan: Path, apps_root: Path, per_cluster: int) -> dict[str, Any]:
    populations: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for app_dir in sorted((scan / "applications").iterdir()):
        payload = json.loads((app_dir / "findings.json").read_text())
        for finding in payload["findings"]:
            rule_id = finding["check_id"]
            if rule_id not in PILOTS:
                continue
            record = {
                "id": identity(app_dir.name, finding),
                "rule_id": rule_id,
                "application": app_dir.name,
                "path": finding["path"],
                "line": finding["start"]["line"],
                "end_line": finding["end"]["line"],
                "cluster": cluster(rule_id, finding),
                "matched_text": finding.get("extra", {}).get("lines", ""),
            }
            populations[rule_id].append(record)

    selected: list[dict[str, Any]] = []
    for rule_id, records in sorted(populations.items()):
        if rule_id in SMALL:
            chosen = records
        else:
            groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
            for record in records:
                groups[(record["application"], record["cluster"])].append(record)
            chosen = []
            for group in groups.values():
                chosen.extend(sorted(group, key=lambda item: item["id"])[:per_cluster])
        for record in chosen:
            source = apps_root / record["application"] / record["path"]
            first, text = context(source, record["line"], record["end_line"])
            record["context_first_line"] = first
            record["context"] = text
            record["review"] = {"decision": "pending", "basis": "pending"}
            selected.append(record)

    return {
        "schema_version": 1,
        "sampling": {
            "method": "complete for populations <=30; otherwise first three SHA-256 identities per application-and-structure cluster",
            "per_cluster": per_cluster,
        },
        "populations": {rule: len(records) for rule, records in sorted(populations.items())},
        "sample_counts": {
            rule: sum(record["rule_id"] == rule for record in selected) for rule in sorted(populations)
        },
        "records": sorted(selected, key=lambda item: (item["rule_id"], item["application"], item["cluster"], item["id"])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan", type=Path, required=True)
    parser.add_argument("--apps-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--per-cluster", type=int, default=3)
    args = parser.parse_args()
    if args.per_cluster < 1:
        print("ERROR: --per-cluster must be positive")
        return 2
    payload = build(args.scan.resolve(), args.apps_root.resolve(), args.per_cluster)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"Pilot review queue written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
