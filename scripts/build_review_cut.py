"""Freeze a finite Semgrep Portfolio Review Cut from canonical scan evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from check_rule_contract import RULE_ID, rule_blocks, scalar
from scan_public_snapshot import hash_tree, snapshot_worktree

ROOT = Path(__file__).resolve().parents[1]
PILOTS = {
    "frappe-async-array-callback-misuse": "public correctness tracer with three current matches",
    "override-doctype-class": "upstream compatibility policy with one current match",
    "frappe-sql-format-injection": "security hotspot requiring structure-versus-data adjudication",
    "frappe-whitelisted-permission-bypass": "authorisation hotspot at a Frappe trust boundary",
    "frappe-n-plus-one-read-in-loop": "high-volume performance claim requiring boundedness evidence",
}


class ReviewCutError(RuntimeError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ReviewCutError(f"expected object: {path}")
    return value


def git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True,
        text=not binary,
    )
    return result.stdout


def languages(block: str) -> list[str]:
    match = re.search(r"(?m)^\s+languages:\s*\[([^]]+)]", block)
    return sorted(part.strip().strip("'\"") for part in match.group(1).split(",")) if match else []


def origin(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if relative.startswith("rules/upstream/frappe/"):
        return "frappe-upstream"
    if relative.startswith("rules/backports/"):
        return "noospheric-backport"
    return "noospheric-custom"


def source_suppressions(apps_root: Path, app_records: list[dict[str, Any]], rule_ids: set[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    import tempfile

    for app in app_records:
        repo = apps_root / app["name"]
        with tempfile.TemporaryDirectory(prefix=f"review-cut-{app['name']}-") as directory:
            snapshot = Path(directory) / "source"
            content_hash, _, status_hash = snapshot_worktree(repo, snapshot)
            source = app["source"]
            if (content_hash, status_hash) != (source["content_sha256"], source["status_sha256"]):
                raise ReviewCutError(f"{app['name']}: source drifted after canonical scan")
            for file in snapshot.rglob("*"):
                if not file.is_file():
                    continue
                try:
                    lines = file.read_text(errors="strict").splitlines()
                except (UnicodeDecodeError, OSError):
                    continue
                for line in lines:
                    if "nosemgrep" not in line:
                        continue
                    for rule_id in rule_ids:
                        if re.search(rf"(?<![A-Za-z0-9_.-]){re.escape(rule_id)}(?![A-Za-z0-9_.-])", line):
                            counts[rule_id] += 1
    return counts


def build(scan: Path, apps_root: Path) -> dict[str, Any]:
    aggregate = load(scan / "all-apps.json")
    if aggregate["application_count"] != 7:
        raise ReviewCutError("review cut requires exactly seven application repositories")
    provenances = {
        app["name"]: load(scan / "applications" / app["name"] / "provenance.json")
        for app in aggregate["applications"]
    }
    rule_hashes = {p["rules"]["content_sha256"] for p in provenances.values()}
    if len(rule_hashes) != 1:
        raise ReviewCutError("applications were not scanned with one rule-tree identity")

    definitions: list[dict[str, Any]] = []
    for yaml_path in sorted((ROOT / "rules").rglob("*.yml")):
        for rule_id, block in rule_blocks(yaml_path):
            definitions.append({
                "rule_id": rule_id,
                "definition_path": yaml_path.relative_to(ROOT).as_posix(),
                "definition_sha256": hashlib.sha256(block.encode()).hexdigest(),
                "origin": origin(yaml_path),
                "languages": languages(block),
                "severity": scalar(block, "severity") or "unspecified",
                "category": scalar(block, "category") or "upstream-unspecified",
            })
    if len(definitions) != 61 or len({d["rule_id"] for d in definitions}) != 61:
        raise ReviewCutError("current rule portfolio is not the expected unique 61-rule set")

    suppressions = source_suppressions(
        apps_root, aggregate["applications"], {d["rule_id"] for d in definitions}
    )
    app_counts: dict[str, Counter[str]] = {}
    for app in aggregate["applications"]:
        findings = load(scan / "applications" / app["name"] / "findings.json")
        app_counts[app["name"]] = Counter(f["check_id"] for f in findings["findings"])

    queue = []
    for definition in sorted(definitions, key=lambda item: item["rule_id"]):
        rule_id = definition["rule_id"]
        count = int(aggregate["findings_by_rule"].get(rule_id, 0))
        pilot = rule_id in PILOTS
        complete_census = count <= 30
        queue.append({
            **definition,
            "match_count": count,
            "matches_by_application": {
                app: app_counts[app].get(rule_id, 0) for app in sorted(app_counts)
            },
            "suppression_count": suppressions[rule_id],
            "priority_band": "pilot" if pilot else "post-pilot",
            "priority_reason": PILOTS.get(rule_id, "queued without a preselected outcome after the pilot cut"),
            "prerequisites": ["coverage-baseline-v1", "canonical-current-worktree-scan"],
            "parser_scope": "native-language-only; declared coverage gaps remain inherited and visible",
            "review_load": "complete-current-census" if complete_census else "clustered-seeded-sample",
            "baseline_triage_complete": False,
            "enforcement_ceiling": "non-blocking" if not complete_census else "undecided",
            "state": "activated" if pilot else "queued",
            "intended_batch": "five-rule-pilot" if pilot else "post-pilot-unsequenced",
        })

    sources = []
    for app in aggregate["applications"]:
        repo = apps_root / app["name"]
        provenance = provenances[app["name"]]
        sources.append({
            "name": app["name"],
            "branch": str(git(repo, "branch", "--show-current")).strip(),
            "revision": provenance["source"]["revision"],
            "tree": provenance["source"]["tree"],
            "content_sha256": provenance["source"]["content_sha256"],
            "status_sha256": provenance["source"]["status_sha256"],
            "scan_id": provenance["scan_id"],
            "scan_health": app["status"],
        })

    rules_hash, rule_files = hash_tree(ROOT / "rules")
    if rules_hash not in rule_hashes:
        raise ReviewCutError("current rule tree drifted after the canonical scan")
    identity = hashlib.sha256(
        (rules_hash + "\0" + "\0".join(source["scan_id"] for source in sources)).encode()
    ).hexdigest()
    return {
        "schema_version": 1,
        "cut_id": f"portfolio-review-cut-{identity[:16]}",
        "rules_repository": {
            "branch": str(git(ROOT, "branch", "--show-current")).strip(),
            "revision": str(git(ROOT, "rev-parse", "HEAD")).strip(),
            "rules_content_sha256": rules_hash,
            "rule_file_count": rule_files,
        },
        "scan": {
            "path": scan.relative_to(ROOT).as_posix(),
            "finding_count": aggregate["finding_count"],
            "status": aggregate["status"],
            "engine": next(iter(provenances.values()))["engine"],
        },
        "sources": sources,
        "rule_count": len(queue),
        "activated_rule_ids": sorted(PILOTS),
        "queue": queue,
        "pilot_governance": {
            "owner": "Noospheric",
            "author": "Noema",
            "independent_reviewer": "pending-vatsal-authorisation",
            "approval_owner": "Vatsal",
            "review_required": True,
            "discovery_channels": [
                "complete engine-match and suppression census",
                "rule-independent missed-positive search",
                "real safe near-miss search",
                "known defect, fix, test, review, and runtime evidence where available",
            ],
            "failed_entry_recovery": "defer visibly and substitute only from the same priority band",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan", type=Path, required=True)
    parser.add_argument("--apps-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = build(args.scan.resolve(), args.apps_root.resolve())
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    except (ReviewCutError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(f"Portfolio Review Cut written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
