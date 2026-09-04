"""Build a deterministic real-source review queue for a selected rule batch."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


def cluster(rule_id: str, finding: dict[str, Any]) -> str:
    lines = finding.get("extra", {}).get("lines", "")
    metavars = finding.get("extra", {}).get("metavars", {})
    if rule_id == "frappe-codeinjection-eval":
        match = re.search(r"\b(safe_exec|safe_eval|eval|exec|get_attr|frappe\.call)\s*\(", lines)
        return match.group(1) if match else "dynamic-call"
    if rule_id == "frappe-ssti":
        argument = metavars.get("$ARG", {}).get("abstract_content", "").strip()
        if argument.startswith(('"', "'")):
            source = "literal"
        elif argument.endswith(("_path", "_template")) or "path" in argument:
            source = "path-variable"
        elif "." in argument:
            source = "attribute"
        else:
            source = "variable"
        restriction = "restricted" if "restrict_globals=True" in lines else "default-globals"
        return f"{source}:{restriction}"
    if rule_id == "frappe-subprocess-shell-true":
        return "interpolated-shell" if re.search(r"(?:^|[=(])\s*f['\"]", lines) else "static-shell"
    if rule_id == "frappe-set-value-semantics":
        return "none-name" if ", None," in lines else "doctype-as-name"
    if rule_id == "unchecked-frappe-permission-call":
        return "boolean-expression" if re.search(r"\b(?:or|and)\b", lines) else "standalone"
    return "unclassified"


def identity(application: str, finding: dict[str, Any]) -> str:
    value = "\0".join((
        finding["check_id"],
        application,
        finding["path"],
        str(finding["start"]["line"]),
        finding.get("extra", {}).get("lines", ""),
    ))
    return hashlib.sha256(value.encode()).hexdigest()


def source_context(source: Path, start: int, end: int, radius: int) -> str:
    lines = source.read_text(errors="replace").splitlines()
    first = max(1, start - radius)
    last = min(len(lines), end + radius)
    return "\n".join(f"{line_number}: {lines[line_number - 1]}" for line_number in range(first, last + 1))


def build(batch: Path, scan: Path, apps_root: Path, per_cluster: int, radius: int) -> dict[str, Any]:
    selection = json.loads(batch.read_text())
    rule_ids = {row["rule_id"] for row in selection["rules"]}
    populations: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for app_dir in sorted((scan / "applications").iterdir()):
        findings = json.loads((app_dir / "findings.json").read_text())["findings"]
        for finding in findings:
            if finding["check_id"] not in rule_ids:
                continue
            record = {
                "case_id": identity(app_dir.name, finding),
                "rule_id": finding["check_id"],
                "application": app_dir.name,
                "path": finding["path"],
                "line": finding["start"]["line"],
                "end_line": finding["end"]["line"],
                "cluster": cluster(finding["check_id"], finding),
                "matched_text": finding.get("extra", {}).get("lines", ""),
            }
            populations[finding["check_id"]].append(record)

    records: list[dict[str, Any]] = []
    for rule_id in sorted(rule_ids):
        population = populations[rule_id]
        if len(population) <= 20:
            chosen = population
        else:
            groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
            for record in population:
                groups[(record["application"], record["cluster"])].append(record)
            chosen = [
                record
                for group in groups.values()
                for record in sorted(group, key=lambda item: item["case_id"])[:per_cluster]
            ]
        for record in chosen:
            source = apps_root / record["application"] / record["path"]
            record["context"] = source_context(source, record["line"], record["end_line"], radius)
            record["review"] = {"label": "pending", "basis": "pending"}
            records.append(record)

    return {
        "schema_version": 1,
        "batch_id": selection["batch_id"],
        "scan": selection["baseline_scan"],
        "sampling": {
            "complete_population_limit": 20,
            "method": "complete at or below limit; otherwise first SHA-256 identities per application-and-structure cluster",
            "per_cluster": per_cluster,
        },
        "populations": {rule_id: len(populations[rule_id]) for rule_id in sorted(rule_ids)},
        "sample_counts": {
            rule_id: sum(record["rule_id"] == rule_id for record in records) for rule_id in sorted(rule_ids)
        },
        "records": sorted(records, key=lambda item: (item["rule_id"], item["application"], item["cluster"], item["case_id"])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--scan", type=Path, required=True)
    parser.add_argument("--apps-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--per-cluster", type=int, default=3)
    parser.add_argument("--context-radius", type=int, default=12)
    args = parser.parse_args()
    if args.per_cluster < 1 or args.context_radius < 1:
        parser.error("sample and context sizes must be positive")
    payload = build(
        args.batch.resolve(), args.scan.resolve(), args.apps_root.resolve(),
        args.per_cluster, args.context_radius,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"Portfolio review queue written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
