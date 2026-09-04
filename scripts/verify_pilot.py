"""Verify the evidence-led five-rule pilot against retained source artefacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUT_PATH = ROOT / "governance/review-cuts/portfolio-review-cut-v1.json"
CUT_SCAN = ROOT / "scan-results/pilot-review-cut-20260825"
FINAL_SCAN = ROOT / "scan-results/pilot-adjudicated-20260825"
PILOTS = {
    "frappe-async-array-callback-misuse",
    "override-doctype-class",
    "frappe-sql-format-injection",
    "frappe-whitelisted-permission-bypass",
    "frappe-n-plus-one-read-in-loop",
}


def load(path: Path) -> dict:
    value = json.loads(path.read_text())
    assert isinstance(value, dict), path
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def status_hash(repo: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        check=True, capture_output=True,
    )
    return hashlib.sha256(result.stdout).hexdigest()


def review_cut() -> None:
    cut = load(CUT_PATH)
    aggregate = load(CUT_SCAN / "all-apps.json")
    queue = cut["queue"]
    assert cut["rule_count"] == len(queue) == 61
    assert len({item["rule_id"] for item in queue}) == 61
    assert set(cut["activated_rule_ids"]) == PILOTS
    assert {item["rule_id"] for item in queue if item["state"] == "activated"} == PILOTS
    assert sum(item["state"] == "queued" for item in queue) == 56
    assert len(cut["sources"]) == aggregate["application_count"] == 7
    assert cut["scan"]["finding_count"] == aggregate["finding_count"]
    assert cut["pilot_governance"]["independent_reviewer"] == "pending-vatsal-authorisation"
    assert cut["pilot_governance"]["approval_owner"] == "Vatsal"
    for item in queue:
        assert item["match_count"] == aggregate["findings_by_rule"].get(item["rule_id"], 0)
        assert item["priority_reason"] and item["parser_scope"] and item["review_load"]
        assert item["intended_batch"] in {"five-rule-pilot", "post-pilot-unsequenced"}
    for source in cut["sources"]:
        provenance = load(CUT_SCAN / "applications" / source["name"] / "provenance.json")
        assert source["scan_id"] == provenance["scan_id"]
        assert source["content_sha256"] == provenance["source"]["content_sha256"]
        assert source["status_sha256"] == provenance["source"]["status_sha256"]
        assert status_hash(ROOT.parent / source["name"]) == source["status_sha256"]
    baseline = load(ROOT / "governance/coverage/pilot-review-cut-baseline-v1.json")
    assert not [
        target for app in baseline["applications"] for target in app["targets"]
        if target["status"] == "unanalysed"
    ]
    print("Portfolio Review Cut verification passed")


def evidence_packets() -> None:
    directory = ROOT / "governance/pilot/evidence"
    packets = [load(path) for path in sorted(directory.glob("*.json"))]
    assert len(packets) == 5
    assert {packet["rule_id"] for packet in packets} == PILOTS
    for packet in packets:
        assert packet["schema_version"] == 1
        assert packet["review_cut_id"] == load(CUT_PATH)["cut_id"]
        assert packet["claim"] and packet["non_claims"]
        assert packet["engine_match_census"]["population"] >= len(packet["review_sample"])
        assert packet["safe_near_misses"] and packet["missed_positive_search"]
        assert packet["source_evidence"] and packet["limitations"]
        assert packet["review_state"] in {"authored", "reviewed"}
    print("pilot evidence verification passed")


def decisions() -> None:
    data = load(ROOT / "governance/pilot/decisions-v1.json")
    rows = data["decisions"]
    assert {row["rule_id"] for row in rows} == PILOTS
    allowed = {"retain", "narrow", "split", "replace", "audit-only", "retire", "new-rule"}
    assert all(row["outcome"] in allowed for row in rows)
    assert all(row["evidence_packet"] and row["rationale"] and row["enforcement_ceiling"] for row in rows)
    assert data["new_rules"] == [
        "frappe-n-plus-one-read-in-comprehension", "frappe-whitelisted-raw-sql"
    ]
    rule_text = "\n".join(path.read_text() for path in sorted((ROOT / "rules/custom").rglob("*.yml")))
    assert all(f"id: {rule_id}" in rule_text for rule_id in data["new_rules"])
    print("pilot decision verification passed")


def regression_controls() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "tests.test_pilot_evidence"],
        cwd=ROOT, check=False, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    decisions()
    print("pilot regression-control verification passed")


def all_app_scan() -> None:
    aggregate = load(FINAL_SCAN / "all-apps.json")
    assert aggregate["application_count"] == 7
    cut = load(CUT_PATH)
    assert {app["name"] for app in aggregate["applications"]} == {s["name"] for s in cut["sources"]}
    rule_hashes = set()
    for app in aggregate["applications"]:
        provenance = load(FINAL_SCAN / "applications" / app["name"] / "provenance.json")
        rule_hashes.add(provenance["rules"]["content_sha256"])
        assert provenance["source"]["content_sha256"] == next(
            s["content_sha256"] for s in cut["sources"] if s["name"] == app["name"]
        )
    assert len(rule_hashes) == 1
    print("current all-app scan verification passed")


def comparison() -> None:
    data = load(ROOT / "governance/pilot/comparison-v1.json")
    assert set(data["rules"]) == PILOTS
    for rule_id, row in data["rules"].items():
        assert set(row) >= {"before", "after", "delta", "persisting", "new", "resolved", "moved"}
        assert row["after"] - row["before"] == row["delta"]
        assert min(row["before"], row["after"], row["persisting"], row["new"], row["resolved"], row["moved"]) >= 0
    assert data["coverage"]["before_unanalysed"] == 0
    assert data["coverage"]["after_unanalysed"] == 0
    print("pilot comparison verification passed")


def preservation() -> None:
    cut = load(CUT_PATH)
    for source in cut["sources"]:
        assert status_hash(ROOT.parent / source["name"]) == source["status_sha256"], source["name"]
    result = subprocess.run(
        [sys.executable, "scripts/check_rule_contract.py"], cwd=ROOT,
        check=False, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "upstream files unchanged" in result.stdout
    print("source and mirror preservation verification passed")


def independent_review() -> None:
    input_path = ROOT / ".scratch/trustworthy-semgrep-foundation/pilot/blind-review-input-v1.json"
    allocation_path = ROOT / ".scratch/trustworthy-semgrep-foundation/pilot/allocation-v1.json"
    result_path = ROOT / ".scratch/trustworthy-semgrep-foundation/pilot/blind-review-result-v1.json"
    blind_bytes = input_path.read_bytes()
    allocation_bytes = allocation_path.read_bytes()
    blind = json.loads(blind_bytes)
    result = load(result_path)
    expected_cases = {
        case["case_id"] for claim in blind["claims"] for case in claim["cases"]
    }
    require(result["blind_input_sha256"] == hashlib.sha256(blind_bytes).hexdigest(), "blind input identity changed")
    require(result["allocation_commitment_sha256"] == hashlib.sha256(allocation_bytes).hexdigest(), "allocation commitment changed")
    require(result["reviewer_identity"] not in {"", "Noema", "pending"}, "independent reviewer identity is pending")
    require(result["reviewer_is_distinct_from_author"] is True, "reviewer is not distinct from Noema")
    require(result["authored_material_seen_before_labels_frozen"] is False, "reviewer saw authored material before labels froze")
    require(result["labels_frozen_at"] not in {"", "pending"}, "blind labels are not frozen")
    cases = result["cases"]
    require({case["case_id"] for case in cases} == expected_cases, "reviewed case identities do not match the frozen input")
    require(len(cases) == len(expected_cases) == 99, "all 99 cases must be reviewed")
    allowed_labels = {"confirmed-issue", "safe-near-miss", "intentional-policy", "unresolved"}
    require(all(case["label"] in allowed_labels and case["basis"].strip() and case["basis"] != "pending" for case in cases), "every case needs an allowed label and source-backed basis")
    recommendations = result["claim_recommendations"]
    require({row["claim_id"] for row in recommendations} == {"A", "B", "C", "D", "E"}, "all five claim recommendations are required")
    allowed_outcomes = {"retain", "narrow", "split", "replace", "audit-only", "retire", "new-rule"}
    require(all(row["outcome"] in allowed_outcomes and row["rationale"].strip() and row["rationale"] != "pending" for row in recommendations), "every claim needs an allowed outcome and rationale")
    print("independent blind review verification passed")


def approval() -> None:
    data = load(ROOT / "governance/pilot/adjudication-v1.json")
    authored = data["authored_decisions"]
    reviewed = data["independent_review"]
    approval_data = data["approval"]
    authored_path = ROOT / authored["path"]
    reviewed_path = ROOT / reviewed["path"]
    require(hashlib.sha256(authored_path.read_bytes()).hexdigest() == authored["sha256"], "authored decisions changed after adjudication")
    require(hashlib.sha256(reviewed_path.read_bytes()).hexdigest() == reviewed["sha256"], "independent review changed after adjudication")
    require(reviewed["reviewer"] == load(reviewed_path)["reviewer_identity"] == "Kepler", "reviewer provenance mismatch")
    require(approval_data == {"owner": "Vatsal", "approved_on": "2026-08-25", "statement": "I approve.", "state": "approved"}, "Vatsal approval is incomplete")
    rows = data["decisions"]
    require({row["rule_id"] for row in rows} == PILOTS, "all five adjudicated outcomes are required")
    require(all(row["enforcement_ceiling"] == "audit-only" for row in rows), "pilot outcomes must remain audit-only")
    require(data["new_rules"] == [
        "frappe-async-foreach-callback",
        "frappe-malformed-sql-placeholder-list",
        "frappe-n-plus-one-read-in-comprehension",
        "frappe-whitelisted-raw-sql",
    ], "adjudicated rule split is incomplete")
    rule_text = "\n".join(path.read_text() for path in sorted((ROOT / "rules/custom").rglob("*.yml")))
    require(all(f"id: {rule_id}" in rule_text for rule_id in data["new_rules"]), "an adjudicated rule is missing")
    print("Vatsal pilot approval verification passed")


CHECKS = {
    "review-cut": review_cut,
    "evidence-packets": evidence_packets,
    "decisions": decisions,
    "regression-controls": regression_controls,
    "all-app-scan": all_app_scan,
    "comparison": comparison,
    "preservation": preservation,
    "independent-review": independent_review,
    "approval": approval,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", choices=CHECKS, required=True)
    args = parser.parse_args()
    try:
        CHECKS[args.check]()
    except (AssertionError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
