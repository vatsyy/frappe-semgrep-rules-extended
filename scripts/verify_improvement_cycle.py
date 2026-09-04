"""Mechanically verify the four-point Semgrep improvement cycle evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN = ROOT / "scan-results/all-apps-20260825-v2"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def parser_baseline() -> None:
    baseline = load(ROOT / "governance/coverage/baseline-v1.json")
    gaps = load(ROOT / "governance/coverage/parser-gap-decisions-v1.json")["gaps"]
    assert len(baseline["applications"]) == 7
    targets = [target for app in baseline["applications"] for target in app["targets"]]
    assert len(targets) == 8496 and len({target["id"] for target in targets}) == 8496
    assert not [target for target in targets if target["status"] == "unanalysed"]
    assert len(gaps) == 14
    classes = {name: sum(gap["classification"] == name for gap in gaps) for name in {
        "mixed-template", "generated-or-vendor", "native-valid-engine-gap"}}
    assert classes == {"mixed-template": 9, "generated-or-vendor": 2, "native-valid-engine-gap": 3}
    print("parser baseline verification passed")


def longitudinal() -> None:
    artifact = load(ROOT / "governance/coverage/karam-baseline-self-comparison-v1.json")
    assert artifact["counts"] == {"persisting": 11, "moved": 0, "new": 0, "resolved": 0}
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "tests.test_compare_scan_findings"],
        cwd=ROOT, check=False, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    print("longitudinal comparison verification passed")


def karam_reviews() -> None:
    reviews = load(ROOT / ".scratch/trustworthy-semgrep-foundation/reviews/karam-findings-20260825.json")
    findings = load(SCAN / "applications/karam_finance/findings.json")["findings"]
    expected = {(f["check_id"], f["path"], f["start"]["line"]) for f in findings}
    actual = {(r["rule_id"], r["path"], r["line"]) for r in reviews["reviews"]}
    assert reviews["review_count"] == len(reviews["reviews"]) == 11
    assert actual == expected
    assert all(r["basis"].strip() and r["decision"].strip() for r in reviews["reviews"])
    print("Karam review verification passed")


def rule_decisions() -> None:
    decisions = load(ROOT / "governance/coverage/karam-rule-decisions-v1.json")
    comparison = load(ROOT / "governance/coverage/karam-rule-review-comparison-v1.json")
    assert {d["rule_id"] for d in decisions["decisions"]} == {
        "frappe-n-plus-one-read-in-loop", "frappe-whitelisted-permission-bypass",
        "frappe-sql-format-injection", "override-doctype-class",
    }
    assert decisions["new_rules"] == []
    assert comparison["counts"] == {"persisting": 7, "moved": 0, "new": 1, "resolved": 4}
    current = load(ROOT / "scan-results/karam-finance-20260825-reviewed-v3/findings.json")
    assert current["finding_count"] == 8
    fixture = (ROOT / "rules/custom/performance/frappe_performance.py").read_text()
    rule = (ROOT / "rules/custom/performance/frappe_performance.yml").read_text()
    assert "UPDATE `tabToDo`" in fixture and "(?:update|delete|insert|alter|drop|truncate|replace)" in rule
    print("rule decision verification passed")


def source_preservation() -> None:
    aggregate = load(SCAN / "all-apps.json")
    for app in aggregate["applications"]:
        repo = ROOT.parent / app["name"]
        result = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            check=True, capture_output=True,
        )
        current = hashlib.sha256(result.stdout).hexdigest()
        assert current == app["source"]["status_sha256"], f"{app['name']} worktree changed"
    print("source preservation verification passed")


CHECKS = {
    "parser-baseline": parser_baseline,
    "longitudinal": longitudinal,
    "karam-reviews": karam_reviews,
    "rule-decisions": rule_decisions,
    "source-preservation": source_preservation,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", choices=CHECKS, required=True)
    args = parser.parse_args()
    try:
        CHECKS[args.check]()
    except (AssertionError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
