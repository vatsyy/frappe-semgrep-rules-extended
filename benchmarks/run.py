"""Run authored compatibility fixtures against the complete ruleset."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ROOT / "benchmarks"
CASES = BENCHMARKS / "cases"
MANIFEST = BENCHMARKS / "manifest.json"
FIXTURE_SUFFIXES = {".html", ".js", ".json", ".py", ".yaml", ".yml"}


class BenchmarkError(RuntimeError):
    """Raised when the manifest or Semgrep output violates the benchmark contract."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semgrep-command", default="semgrep")
    parser.add_argument("--rules", type=Path, default=ROOT / "rules")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or data.get("schema_version") != 2:
        raise BenchmarkError("manifest.json must declare schema_version: 2")
    if data.get("purpose") != "syntax-compatibility-regression":
        raise BenchmarkError(
            "manifest.json purpose must be syntax-compatibility-regression"
        )
    if not isinstance(data.get("cases"), list) or not data["cases"]:
        raise BenchmarkError("manifest.json must contain at least one case")
    return data


def version_tuple(value: str) -> tuple[int, int, int]:
    match = re.search(r"\b(\d+)\.(\d+)\.(\d+)\b", value)
    if not match:
        raise BenchmarkError(f"cannot parse Semgrep version from {value!r}")
    return tuple(int(part) for part in match.groups())


def stable_rule_id(check_id: str, declared_ids: set[str]) -> str:
    matches = [
        rule_id
        for rule_id in declared_ids
        if check_id == rule_id or check_id.endswith(f".{rule_id}")
    ]
    if matches:
        return max(matches, key=len)
    return check_id.rsplit(".", 1)[-1]


def validate_cases(
    cases: list[dict[str, Any]],
) -> tuple[dict[Path, dict[str, Any]], set[str]]:
    indexed: dict[Path, dict[str, Any]] = {}
    declared_ids: set[str] = set()
    case_ids: set[str] = set()

    for case in cases:
        case_id = case.get("id")
        relative = case.get("path")
        if not isinstance(case_id, str) or not case_id:
            raise BenchmarkError("every case requires a non-empty id")
        if case_id in case_ids:
            raise BenchmarkError(f"duplicate case id: {case_id}")
        case_ids.add(case_id)
        if not isinstance(relative, str):
            raise BenchmarkError(f"{case_id}: path must be a string")

        path = (BENCHMARKS / relative).resolve()
        if not path.is_relative_to(CASES.resolve()) or not path.is_file():
            raise BenchmarkError(
                f"{case_id}: fixture does not exist under benchmarks/cases"
            )
        if path in indexed:
            raise BenchmarkError(f"duplicate fixture path: {relative}")
        indexed[path] = case

        if not case.get("provenance") or not case.get("expectation_reason"):
            raise BenchmarkError(
                f"{case_id}: provenance and expectation_reason are required"
            )
        if case.get("fixture_role") != "authored-compatibility-fixture":
            raise BenchmarkError(
                f"{case_id}: fixture_role must be authored-compatibility-fixture"
            )
        if case.get("admission_eligible") is not False:
            raise BenchmarkError(f"{case_id}: admission_eligible must be false")
        if case.get("audit_disposition") not in {
            "source-backed-replacement-required",
            "unresolved-boundary",
            "syntax-regression-only",
        }:
            raise BenchmarkError(f"{case_id}: invalid audit_disposition")
        versions = case.get("observed_semgrep_versions")
        if not isinstance(versions, list) or not versions or any(
            not isinstance(value, str) or not re.fullmatch(r"\d+\.\d+\.\d+", value)
            for value in versions
        ):
            raise BenchmarkError(
                f"{case_id}: observed_semgrep_versions requires exact versions"
            )

        expected = case.get("expected")
        if not isinstance(expected, dict):
            raise BenchmarkError(f"{case_id}: expected must be a mapping")
        findings = expected.get("findings", [])
        absent = expected.get("absent", [])
        if not isinstance(findings, list) or not isinstance(absent, list):
            raise BenchmarkError(f"{case_id}: findings and absent must be lists")
        for finding in findings:
            if not isinstance(finding, dict) or not finding.get("rule_id"):
                raise BenchmarkError(f"{case_id}: every finding requires rule_id")
            forbidden_semantic_fields = {"tier", "confidence", "label", "outcome"}
            present = forbidden_semantic_fields & finding.keys()
            if present:
                raise BenchmarkError(
                    f"{case_id}: compatibility expectations cannot declare "
                    f"{', '.join(sorted(present))}"
                )
            declared_ids.add(finding["rule_id"])
        declared_ids.update(absent)

    fixtures = {
        path.resolve()
        for path in CASES.rglob("*")
        if path.is_file() and path.suffix in FIXTURE_SUFFIXES
    }
    missing = fixtures - set(indexed)
    if missing:
        paths = ", ".join(str(path.relative_to(BENCHMARKS)) for path in sorted(missing))
        raise BenchmarkError(f"fixtures missing from manifest: {paths}")
    return indexed, declared_ids


def run_semgrep(
    command_text: str, rules: Path, process_timeout: int
) -> tuple[str, dict[str, Any]]:
    command_prefix = shlex.split(command_text)
    if not command_prefix:
        raise BenchmarkError("--semgrep-command cannot be empty")
    version_result = subprocess.run(
        [*command_prefix, "--version"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=process_timeout,
    )
    version = version_result.stdout.strip()
    command = [
        *command_prefix,
        "scan",
        "--config",
        str(rules.resolve()),
        "--json",
        "--quiet",
        "--metrics=off",
        "--disable-version-check",
        "--time",
        str(CASES),
    ]
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=process_timeout,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        detail = result.stderr.strip() or result.stdout[:500]
        raise BenchmarkError(f"Semgrep did not return JSON: {detail}") from exc
    if result.returncode not in {0, 1}:
        raise BenchmarkError(
            result.stderr.strip() or f"Semgrep exited {result.returncode}"
        )
    return version, payload


def evaluate_performance(
    payload: dict[str, Any], budgets: dict[str, Any]
) -> tuple[list[str], dict[str, float]]:
    failures: list[str] = []
    timing = payload.get("time")
    if not isinstance(timing, dict):
        return ["Semgrep did not return --time measurements"], {}

    scan_seconds = float(timing.get("profiling_times", {}).get("total_time", 0))
    memory_mib = float(timing.get("max_memory_bytes", 0)) / (1024 * 1024)
    rule_ids = timing.get("rules", [])
    rule_totals = [0.0] * len(rule_ids)
    for target in timing.get("targets", []):
        for index, value in enumerate(target.get("match_times", [])):
            if index < len(rule_totals):
                rule_totals[index] += float(value)
    maximum_rule_seconds = max(rule_totals, default=0.0)
    maximum_rule_id = (
        stable_rule_id(rule_ids[rule_totals.index(maximum_rule_seconds)], set())
        if rule_totals
        else "<none>"
    )

    if scan_seconds > float(budgets["maximum_scan_seconds"]):
        failures.append(
            f"scan time {scan_seconds:.3f}s exceeds {budgets['maximum_scan_seconds']}s"
        )
    if maximum_rule_seconds > float(budgets["maximum_rule_match_seconds"]):
        failures.append(
            f"rule {maximum_rule_id} took {maximum_rule_seconds:.3f}s; "
            f"budget is {budgets['maximum_rule_match_seconds']}s"
        )
    if memory_mib > float(budgets["maximum_memory_mib"]):
        failures.append(
            f"memory {memory_mib:.1f} MiB exceeds {budgets['maximum_memory_mib']} MiB"
        )
    return failures, {
        "scan_seconds": scan_seconds,
        "maximum_rule_seconds": maximum_rule_seconds,
        "memory_mib": memory_mib,
    }


def evaluate(
    indexed: dict[Path, dict[str, Any]], declared_ids: set[str], payload: dict[str, Any]
) -> list[str]:
    failures: list[str] = []
    actual: dict[Path, set[str]] = {path: set() for path in indexed}

    for result in payload.get("results", []):
        path = (ROOT / result["path"]).resolve()
        if path not in indexed:
            failures.append(
                f"finding returned for unregistered fixture: {result['path']}"
            )
            continue
        actual[path].add(stable_rule_id(result["check_id"], declared_ids))

    for error in payload.get("errors", []):
        failures.append(
            f"Semgrep {error.get('type', 'error')} in {error.get('path', '<unknown>')}: "
            f"{error.get('message', '<no message>')}"
        )

    for path, case in indexed.items():
        expected = case["expected"]
        wanted = {finding["rule_id"] for finding in expected.get("findings", [])}
        absent = set(expected.get("absent", []))
        observed = actual[path]
        missing = wanted - observed
        forbidden = absent & observed
        unexpected = observed - wanted
        if missing:
            failures.append(
                f"{case['id']}: missing findings: {', '.join(sorted(missing))}"
            )
        if forbidden:
            failures.append(
                f"{case['id']}: forbidden findings: {', '.join(sorted(forbidden))}"
            )
        if unexpected:
            failures.append(
                f"{case['id']}: unexpected findings: {', '.join(sorted(unexpected))}"
            )
    return failures


def main() -> int:
    args = parse_args()
    try:
        manifest = load_manifest(args.manifest)
        indexed, declared_ids = validate_cases(manifest["cases"])
        if args.validate_only:
            print(f"Compatibility manifest valid: {len(indexed)} fixtures.")
            return 0
        budgets = manifest.get("performance")
        if not isinstance(budgets, dict):
            raise BenchmarkError("manifest.json must contain performance budgets")
        version, payload = run_semgrep(
            args.semgrep_command,
            args.rules,
            int(budgets["process_timeout_seconds"]),
        )
        minimum = version_tuple(str(manifest["minimum_semgrep_version"]))
        if version_tuple(version) < minimum:
            raise BenchmarkError(
                f"Semgrep {version} is older than required {manifest['minimum_semgrep_version']}"
            )
        failures = evaluate(indexed, declared_ids, payload)
        performance_failures, performance = evaluate_performance(payload, budgets)
        failures.extend(performance_failures)
    except (
        BenchmarkError,
        OSError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1

    print(
        f"Compatibility benchmark passed: {len(indexed)} fixtures on Semgrep {version}; "
        f"scan={performance['scan_seconds']:.3f}s, "
        f"max-rule={performance['maximum_rule_seconds']:.3f}s, "
        f"memory={performance['memory_mib']:.1f} MiB."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
