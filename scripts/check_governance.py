"""Validate the versioned Rule Portfolio Catalogue contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOGUE = ROOT / "governance" / "catalogue.json"
SCHEMAS = ROOT / "governance" / "schemas"


class GovernanceError(ValueError):
    """Raised when a governance artefact violates its public contract."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE)
    return parser.parse_args()


def load_catalogue(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise GovernanceError(f"{path}: cannot load catalogue: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise GovernanceError(f"{path}: schema_version must be 1")
    catalogue_schema = load_schema("catalogue")
    require_fields(data, catalogue_schema["required"], "catalogue")
    if not isinstance(data.get("catalogue_id"), str) or not data["catalogue_id"]:
        raise GovernanceError(f"{path}: catalogue_id must be a non-empty string")
    if not isinstance(data.get("claims"), list):
        raise GovernanceError(f"{path}: claims must be a list")
    if not isinstance(data.get("retired_ids"), list) or not all(
        isinstance(value, str) and value for value in data["retired_ids"]
    ):
        raise GovernanceError(f"{path}: retired_ids must be a list of identities")
    return data


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMAS / f"{name}-v1.json"
    try:
        schema = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise GovernanceError(f"{path}: cannot load schema: {exc}") from exc
    if schema.get("schema_version") != 1:
        raise GovernanceError(f"{path}: schema_version must be 1")
    return schema


def require_fields(value: object, fields: list[str], location: str) -> None:
    if not isinstance(value, dict):
        raise GovernanceError(f"{location} must be an object")
    for field in fields:
        if field not in value:
            raise GovernanceError(f"{location}.{field} is required")


def require_non_empty_strings(value: object, location: str) -> None:
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise GovernanceError(f"{location} must contain non-empty strings")


def validate_contract(
    contract: dict[str, Any], schema: dict[str, Any], location: str
) -> None:
    for field in ("claim", "observed_construct", "remediation_or_next_evidence"):
        if not isinstance(contract[field], str) or not contract[field].strip():
            raise GovernanceError(f"{location}.{field} must be a non-empty string")
    require_fields(contract["scope"], schema["scope_required"], f"{location}.scope")
    scope = contract["scope"]
    for field in ("languages", "framework_versions", "paths", "file_kinds"):
        require_non_empty_strings(scope[field], f"{location}.scope.{field}")
    for field in ("prerequisites", "exclusions"):
        if not isinstance(scope[field], list):
            raise GovernanceError(f"{location}.scope.{field} must be a list")
    for field in ("analysis_mode", "boundary"):
        if not isinstance(scope[field], str) or not scope[field].strip():
            raise GovernanceError(f"{location}.scope.{field} must be a non-empty string")
    for field in ("assumptions", "limitations", "provenance", "references"):
        if not isinstance(contract[field], list):
            raise GovernanceError(f"{location}.{field} must be a list")
    require_fields(contract["message"], schema["message_required"], f"{location}.message")
    message = contract["message"]
    for field in ("observation", "claim", "next_action"):
        if not isinstance(message[field], str) or not message[field].strip():
            raise GovernanceError(f"{location}.message.{field} must be a non-empty string")
    if not isinstance(message["non_claims"], list):
        raise GovernanceError(f"{location}.message.non_claims must be a list")
    confidence = contract["rule_confidence"]
    if not isinstance(confidence, dict) or confidence.get("status") not in {
        "unmeasured",
        "measured",
    }:
        raise GovernanceError(f"{location}.rule_confidence has an invalid status")


def require_complete_census(admission: dict[str, Any], location: str) -> None:
    census = admission.get("baseline_triage")
    if not isinstance(census, dict) or census.get("population") != "census":
        raise GovernanceError(f"{location} requires a complete Baseline Triage census")
    for total, triaged in (
        ("matches_total", "matches_triaged"),
        ("suppressions_total", "suppressions_triaged"),
    ):
        if (
            not isinstance(census.get(total), int)
            or census[total] < 0
            or census.get(triaged) != census[total]
        ):
            raise GovernanceError(
                f"{location} requires a complete Baseline Triage census"
            )


def validate_state(claim: dict[str, Any], location: str) -> None:
    lifecycle_schema = load_schema("lifecycle")
    state = claim["state"]
    require_fields(state, ["lifecycle", "outcome"], f"{location}.state")
    lifecycle = state["lifecycle"]
    outcome = state["outcome"]
    if lifecycle not in lifecycle_schema["lifecycle_states"]:
        raise GovernanceError(f"{location}.state.lifecycle is invalid")
    allowed_outcomes = {
        "candidate": {None, "outside-portfolio"},
        "evaluating": {None},
        "accepted": {"blocking", "monitor", "audit"},
        "suspended": {"monitor", "audit", "outside-portfolio"},
        "retired": {"outside-portfolio"},
    }
    if outcome not in allowed_outcomes[lifecycle]:
        raise GovernanceError(
            f"{location}.state contradicts lifecycle {lifecycle!r}"
        )

    admission = claim["admission"]
    if lifecycle != "accepted":
        if admission is not None:
            raise GovernanceError(f"{location}.admission is only valid for accepted rules")
        return
    provenance = claim["provenance"]
    if not isinstance(provenance, dict):
        raise GovernanceError(f"{location}.provenance must be an object")
    if provenance.get("kind") == "validation-only":
        raise GovernanceError(f"{location}: validation-only provenance cannot admit a rule")
    if not isinstance(admission, dict):
        raise GovernanceError(f"{location}.admission is required for accepted rules")
    gates = admission.get("universal_gates")
    contract_schema = load_schema("rule-contract")
    if not isinstance(gates, dict):
        raise GovernanceError(f"{location}.admission.universal_gates must be an object")
    for gate in contract_schema["universal_gates"]:
        if gates.get(gate) is not True:
            raise GovernanceError(
                f"{location}: every universal Admission Gate must pass; "
                f"missing or false: {gate}"
            )

    contract = claim["contract"]
    confidence = contract["rule_confidence"]
    if confidence.get("status") != "measured" or not isinstance(
        confidence.get("evidence_packet"), str
    ) or not confidence["evidence_packet"].strip():
        raise GovernanceError(
            f"{location}: accepted rules require measured Rule Confidence evidence"
        )
    tier_rank = {"audit": 1, "monitor": 2, "blocking": 3}
    if tier_rank[outcome] > tier_rank[contract["enforcement_ceiling"]]:
        raise GovernanceError(f"{location}: outcome exceeds its Enforcement Ceiling")
    if outcome == "blocking":
        if contract["claim_class"] not in {
            "deterministic-defect",
            "proven-security-violation",
            "explicit-policy-violation",
        }:
            raise GovernanceError(f"{location}: claim class is not blocking-eligible")
        if (
            contract["claim_class"] == "explicit-policy-violation"
            and not isinstance(admission.get("written_policy"), str)
        ):
            raise GovernanceError(
                f"{location}: blocking policy claims require an identified written policy"
            )
        required = (
            "assumptions_established",
            "parser_scope_complete",
            "holdout_passed",
            "independent_review",
            "vatsal_approval",
        )
        if any(admission.get(field) is not True for field in required):
            raise GovernanceError(f"{location}: every blocking Admission Gate must pass")
        if admission.get("reviewed_false_positives") != 0 or admission.get("unresolved_cases") != 0:
            raise GovernanceError(f"{location}: blocking requires zero false positives and unresolved cases")
        known = admission.get("known_positive_cases")
        detected = admission.get("detected_known_positive_cases")
        if (
            not isinstance(known, int)
            or isinstance(known, bool)
            or known < 1
            or not isinstance(detected, int)
            or isinstance(detected, bool)
        ):
            raise GovernanceError(
                f"{location}: blocking requires real known positive counts"
            )
        if known != detected:
            raise GovernanceError(f"{location}: blocking must detect every known positive case")
        require_complete_census(admission, location)


def validate_claims(catalogue: dict[str, Any]) -> None:
    current_state = load_schema("current-state")
    contract_schema = load_schema("rule-contract")
    claim_ids: set[str] = set()
    rule_ids: set[str] = set()
    retired_ids = set(catalogue["retired_ids"])
    for index, claim in enumerate(catalogue["claims"]):
        location = f"claims[{index}]"
        require_fields(claim, current_state["required_claim_fields"], location)
        if claim["id"] in claim_ids:
            raise GovernanceError(f"duplicate claim id: {claim['id']}")
        require_fields(claim["state"], ["lifecycle", "outcome"], f"{location}.state")
        lifecycle = claim["state"]["lifecycle"]
        if claim["id"] in retired_ids and lifecycle != "retired":
            raise GovernanceError(f"{location} reuses retired identity {claim['id']}")
        if claim["rule_id"] in rule_ids:
            raise GovernanceError(f"duplicate rule id: {claim['rule_id']}")
        claim_ids.add(claim["id"])
        rule_ids.add(claim["rule_id"])
        if claim["ownership"] not in current_state["ownership"]:
            raise GovernanceError(f"{location}.ownership is invalid")
        if not isinstance(claim["provenance"], dict):
            raise GovernanceError(f"{location}.provenance must be an object")
        require_fields(
            claim["contract"],
            contract_schema["required"],
            f"{location}.contract",
        )
        contract = claim["contract"]
        validate_contract(contract, contract_schema, f"{location}.contract")
        if contract["claim_class"] not in contract_schema["claim_classes"]:
            raise GovernanceError(f"{location}.contract.claim_class is invalid")
        if contract["enforcement_ceiling"] not in contract_schema["enforcement_tiers"]:
            raise GovernanceError(f"{location}.contract.enforcement_ceiling is invalid")
        if contract["claim_class"] in {"review-hotspot", "performance-hypothesis"} and contract["enforcement_ceiling"] != "audit":
            raise GovernanceError(f"{location}: claim class has an audit Enforcement Ceiling")
        measurements = claim.get("measurements")
        if (
            isinstance(measurements, dict)
            and measurements.get("population") != "enumerated"
            and any(
                name in measurements
                for name in ("precision", "recall", "false_positive_rate")
            )
        ):
            raise GovernanceError(
                f"{location}: exact rates require an enumerated population"
            )
        validate_state(claim, location)

    for index, claim in enumerate(catalogue["claims"]):
        retirement = claim.get("retirement")
        if not isinstance(retirement, dict) or retirement.get("reason") != "upstream-parity":
            continue
        replacement = retirement.get("replacement")
        if replacement not in claim.get("replacements", []):
            raise GovernanceError(
                f"claims[{index}]: upstream-parity retirement must preserve its replacement link"
            )
        successors = [item for item in catalogue["claims"] if item.get("id") == replacement]
        if not successors or claim["id"] not in successors[0].get("predecessors", []):
            raise GovernanceError(
                f"claims[{index}]: upstream-parity successor must preserve its predecessor link"
            )


def main() -> int:
    args = parse_args()
    try:
        catalogue = load_catalogue(args.catalogue)
        validate_claims(catalogue)
    except GovernanceError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    count = len(catalogue["claims"])
    noun = "claim" if count == 1 else "claims"
    print(f"Governance valid: {count} {noun}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
