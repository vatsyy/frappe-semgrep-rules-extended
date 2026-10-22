"""Retain Semgrep baselines, compare rules on identical source, and inspect findings."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import shutil
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from check_rule_contract import rule_blocks
from scan_all_apps import AllAppsScanError, discover_apps
from scan_public_snapshot import (
    DEFAULT_EXCLUSIONS,
    PINNED_SEMGREP,
    ROOT,
    SNAPSHOT_EXCLUDED_PREFIXES,
    SnapshotScanError,
    hash_tree,
    install_canonical_ignore,
    run_git,
    scan_snapshot,
    semgrep_version,
    snapshot_worktree,
    validate_worktree_source,
    worktree_state,
    write_json,
)

DEFAULT_SEMGREP = f"uv tool run --from semgrep=={PINNED_SEMGREP} semgrep"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise SnapshotScanError(f"expected a JSON object: {path}")
    return value


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def harness_identity() -> dict[str, str]:
    return {
        name: file_hash(Path(__file__).parent / name)
        for name in (
            "evaluate_rules.py",
            "scan_public_snapshot.py",
            "scan_all_apps.py",
            "check_rule_contract.py",
        )
    }


def inside(root: Path, relative: str) -> Path:
    """Resolve recorded paths without allowing an artefact to escape its input."""
    path = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise SnapshotScanError(f"unsafe relative path: {relative}")
    if not path.resolve().is_relative_to(root.resolve()):
        raise SnapshotScanError(f"path leaves input directory: {relative}")
    return path


def rules_identity(rules: Path) -> dict[str, Any]:
    digest, count = hash_tree(rules)
    inventory = {}
    for path in sorted(rules.rglob("*")):
        if path.suffix not in {".yml", ".yaml"} or not path.is_file():
            continue
        for rule_id, block in rule_blocks(path):
            if rule_id in inventory:
                raise SnapshotScanError(f"duplicate rule ID: {rule_id}")
            inventory[rule_id] = {
                "path": path.relative_to(rules).as_posix(),
                "sha256": hashlib.sha256(block.encode()).hexdigest(),
            }
    if not inventory:
        raise SnapshotScanError(f"no rule IDs found in {rules}")
    return {"sha256": digest, "file_count": count, "inventory": inventory}


def verify_run(run: Path) -> dict[str, Any]:
    if (
        file_hash(run / "manifest.json")
        != (run / "manifest.sha256").read_text().strip()
    ):
        raise SnapshotScanError("retained manifest changed")
    manifest = read_json(run / "manifest.json")
    if manifest.get("schema_version") != 1:
        raise SnapshotScanError("unsupported or incomplete evaluation manifest")
    if manifest["engine"]["version"] != PINNED_SEMGREP:
        raise SnapshotScanError(f"evaluation requires Semgrep CE {PINNED_SEMGREP}")
    if hash_tree(run / "rules")[0] != manifest["rules"]["sha256"]:
        raise SnapshotScanError("retained rules changed; create a new baseline")
    if not manifest["applications"]:
        raise SnapshotScanError("evaluation contains no applications")
    for name, app in manifest["applications"].items():
        source = inside(run / "sources", name)
        if hash_tree(source)[0] != app["analysis_sha256"]:
            raise SnapshotScanError(f"retained source changed: {name}")
        if hash_tree(inside(run / "applications", name))[0] != app["results_sha256"]:
            raise SnapshotScanError(f"retained scan results changed: {name}")
    if "comparison_sha256" in manifest:
        if file_hash(run / "comparison.json") != manifest["comparison_sha256"]:
            raise SnapshotScanError("retained comparison changed")
    return manifest


def validate_settings(settings: dict[str, Any]) -> None:
    for key in ("jobs", "timeout", "process_timeout_seconds"):
        if not isinstance(settings[key], int) or settings[key] < 1:
            raise SnapshotScanError(f"{key} must be a positive integer")
    if (
        not isinstance(settings["max_memory_mib"], int)
        or settings["max_memory_mib"] < 0
    ):
        raise SnapshotScanError("max_memory_mib must be non-negative")
    if not isinstance(settings["exclusions"], list) or any(
        not isinstance(value, str) for value in settings["exclusions"]
    ):
        raise SnapshotScanError("exclusions must be a list of strings")


def result_data(run: Path, name: str) -> dict[str, Any]:
    return read_json(inside(run / "applications", name) / "results.json")


def finding_key(finding: dict[str, Any]) -> tuple:
    return (
        finding["check_id"],
        finding["path"],
        finding["start"]["line"],
        finding["start"]["col"],
        finding["end"]["line"],
        finding["end"]["col"],
        json.dumps(finding.get("extra", {}).get("metavars", {}), sort_keys=True),
    )


def details(finding: dict[str, Any]) -> dict[str, Any]:
    return {
        key: finding.get("extra", {}).get(key)
        for key in ("message", "severity", "metadata", "fix", "fix_regex")
    }


def index_findings(findings: list[dict[str, Any]]) -> dict[tuple, dict[str, Any]]:
    """Keep distinct bindings and repeated matches at the same source location."""
    occurrences: Counter[tuple] = Counter()
    indexed = {}
    for finding in sorted(
        findings, key=lambda f: (finding_key(f), json.dumps(details(f), sort_keys=True))
    ):
        key = finding_key(finding)
        indexed[(*key, occurrences[key])] = finding
        occurrences[key] += 1
    return indexed


def compare_runs(
    baseline: Path, candidate: Path, before: dict[str, Any], after: dict[str, Any]
) -> dict[str, Any]:
    """Compare locations and rule claims; retain scan-health changes separately."""
    comparison: dict[str, Any] = {"applications": {}, "rules": {}}
    old_rules = before["rules"]["inventory"]
    new_rules = after["rules"]["inventory"]
    comparison["rules"] = {
        "added": sorted(new_rules.keys() - old_rules.keys()),
        "removed": sorted(old_rules.keys() - new_rules.keys()),
        "modified": sorted(
            key
            for key in old_rules.keys() & new_rules.keys()
            if old_rules[key] != new_rules[key]
        ),
    }
    for name in before["applications"]:
        old = result_data(baseline, name)
        new = result_data(candidate, name)
        old_findings = index_findings(old["findings"])
        new_findings = index_findings(new["findings"])
        common = old_findings.keys() & new_findings.keys()
        comparison["applications"][name] = {
            "added": [
                new_findings[k]
                for k in sorted(new_findings.keys() - old_findings.keys())
            ],
            "removed": [
                old_findings[k]
                for k in sorted(old_findings.keys() - new_findings.keys())
            ],
            "changed": [
                {"before": old_findings[k], "after": new_findings[k]}
                for k in sorted(common)
                if details(old_findings[k]) != details(new_findings[k])
            ],
            "unchanged": sum(
                details(old_findings[k]) == details(new_findings[k]) for k in common
            ),
            "health_before": old["health"],
            "health_after": new["health"],
            "paths_before": old["paths"],
            "paths_after": new["paths"],
            "paths_identical": old["paths"] == new["paths"],
        }
    return comparison


def write_report(
    output: Path, manifest: dict[str, Any], comparison: dict | None
) -> None:
    counts: Counter[str] = Counter()
    lines = [
        "# Rule evaluation",
        "",
        f"Semgrep CE {PINNED_SEMGREP}. Analysis: **{manifest['status']}**.",
        "",
        "Matches are unreviewed evidence. Counts do not measure precision or recall.",
        "",
        "| Application | Findings | Analysis errors | Scanned | Skipped |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name in manifest["applications"]:
        data = result_data(output, name)
        counts.update(f["check_id"] for f in data["findings"])
        health, paths = data["health"], data["paths"]
        errors = len(health["errors"]) + bool(health["engine_error"])
        if not health["execution_complete"] and not errors:
            errors = 1
        lines.append(
            f"| {name} | {len(data['findings'])} | {errors} | "
            f"{len(paths.get('scanned', []))} | {len(paths.get('skipped', []))} |"
        )
    lines += ["", "## Findings by rule", "", "| Rule | Matches |", "| --- | ---: |"]
    for rule_id in sorted(manifest["rules"]["inventory"]):
        lines.append(f"| {rule_id} | {counts[rule_id]} |")
    lines += [
        "",
        "Zero matches means no positive example was reported, not that a rule is accurate.",
    ]
    if comparison is not None:
        lines += [
            "",
            "## Changes on identical source",
            "",
            "| Application | Added | Removed | Changed message/metadata/fix | Same paths |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
        for name, changes in comparison["applications"].items():
            lines.append(
                f"| {name} | {len(changes['added'])} | {len(changes['removed'])} | "
                f"{len(changes['changed'])} | {changes['paths_identical']} |"
            )
        for kind, rule_ids in comparison["rules"].items():
            lines += ["", f"Rules {kind}: " + (", ".join(rule_ids) or "none") + "."]
        lines += [
            "",
            "Parser errors remain analysis gaps even when unchanged. A disappearing finding",
            "may be a regression, exclusion change or removed rule; inspect it before accepting.",
        ]
    lines += [
        "",
        "Use inspect for bounded source context. Raw JSON, stderr, skipped paths and",
        "exact commands remain under applications/. Inputs are retained in sources/",
        "and rules/; manifest.json records hashes, source identities and settings.",
    ]
    (output / "summary.md").write_text("\n".join(lines) + "\n")


def evaluate(args: argparse.Namespace) -> Path:
    if args.output.is_symlink():
        raise SnapshotScanError(f"output is a symbolic link: {args.output}")
    output, rules = args.output.resolve(), args.rules.resolve()
    if output.exists() or output.is_symlink():
        raise SnapshotScanError(f"output exists and will not be overwritten: {output}")
    before = None
    if args.action == "baseline":
        apps = discover_apps(args.apps_root, {ROOT.name})
        if args.app:
            unknown = set(args.app) - {app.name for app in apps}
            if unknown:
                raise SnapshotScanError(
                    f"unknown application(s): {', '.join(sorted(unknown))}"
                )
            apps = [app for app in apps if app.name in args.app]
        settings = {
            "jobs": args.jobs,
            "timeout": args.timeout,
            "max_memory_mib": args.max_memory_mib,
            "process_timeout_seconds": args.process_timeout_seconds,
            "exclusions": sorted(set(DEFAULT_EXCLUSIONS) | set(args.exclude)),
        }
        protected = [rules, *apps]
    else:
        args.baseline = args.baseline.resolve()
        before = verify_run(args.baseline)
        if before["harness"] != harness_identity():
            raise SnapshotScanError("evaluation code changed; capture a new baseline")
        settings = before["settings"]
        protected = [
            rules,
            args.baseline,
            *(Path(app["path"]) for app in before["applications"].values()),
        ]
        apps = []
    if any(output.is_relative_to(path.resolve()) for path in protected):
        raise SnapshotScanError(
            "output must be outside application, rules and baseline inputs"
        )
    validate_settings(settings)
    command = shlex.split(args.semgrep_command)
    if not command:
        raise SnapshotScanError("Semgrep command cannot be empty")
    version = semgrep_version(command)
    identity = rules_identity(rules)
    output.mkdir(parents=True)
    shutil.copytree(rules, output / "rules")
    if hash_tree(output / "rules")[0] != identity["sha256"]:
        raise SnapshotScanError("rule inputs changed during capture")
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "engine": {"name": "semgrep-ce", "version": version},
        "harness": harness_identity(),
        "settings": settings,
        "rules": identity,
        "applications": {},
        "snapshot_excluded_prefixes": list(SNAPSHOT_EXCLUDED_PREFIXES),
    }
    (output / "sources").mkdir()
    (output / "applications").mkdir()
    if before is None:
        for app in apps:
            source = output / "sources" / app.name
            info = validate_worktree_source(app)
            info.update(
                {"path": str(app), "branch": run_git(app, "branch", "--show-current")}
            )
            status = worktree_state(app)
            source_hash, count, status_hash = snapshot_worktree(app, source)
            if (
                hashlib.sha256(status).hexdigest() != status_hash
                or run_git(app, "rev-parse", "HEAD") != info["revision"]
            ):
                raise SnapshotScanError(
                    f"source Git identity changed during capture: {app.name}"
                )
            info.update(
                {
                    "content_sha256": source_hash,
                    "file_count": count,
                    "status_sha256": status_hash,
                }
            )
            info["original_semgrepignore_sha256"] = install_canonical_ignore(
                source, settings["exclusions"]
            )
            (output / f"{app.name}.status").write_bytes(status)
            info["analysis_sha256"] = hash_tree(source)[0]
            manifest["applications"][app.name] = info
    else:
        manifest["baseline"] = str(args.baseline)
        manifest["baseline_manifest_sha256"] = file_hash(
            args.baseline / "manifest.json"
        )
        for name, info in before["applications"].items():
            source = inside(output / "sources", name)
            shutil.copytree(inside(args.baseline / "sources", name), source)
            if hash_tree(source)[0] != info["analysis_sha256"]:
                raise SnapshotScanError(
                    f"baseline source changed during copying: {name}"
                )
            manifest["applications"][name] = {
                k: v for k, v in info.items() if k != "results_sha256"
            }

    for name, info in manifest["applications"].items():
        source = inside(output / "sources", name)
        destination = inside(output / "applications", name)
        destination.mkdir()
        print(f"Scanning {name}...", flush=True)
        findings, health = scan_snapshot(
            source,
            output / "rules",
            destination,
            command,
            **settings,
            verbose=True,
        )
        try:
            raw = read_json(destination / "semgrep.json")
            paths = raw.get("paths", {})
            if not isinstance(paths, dict) or any(
                not isinstance(paths.get(key), list) for key in ("scanned", "skipped")
            ):
                raise SnapshotScanError(
                    "Semgrep did not report scanned and skipped paths"
                )
        except (ValueError, SnapshotScanError) as exc:
            paths = {}
            health["status"] = "invalid"
            health["errors"].append({"type": "invalid-output", "message": str(exc)})
        write_json(
            destination / "results.json",
            {"findings": findings, "health": health, "paths": paths},
        )
        if hash_tree(source)[0] != info["analysis_sha256"]:
            raise SnapshotScanError(f"retained source changed during scanning: {name}")
        info["results_sha256"] = hash_tree(destination)[0]
    if hash_tree(output / "rules")[0] != identity["sha256"]:
        raise SnapshotScanError("retained rules changed during scanning")
    manifest["status"] = (
        "complete"
        if all(
            result_data(output, name)["health"]["status"] == "valid"
            for name in manifest["applications"]
        )
        else "incomplete"
    )
    comparison = None
    if before is not None:
        verify_run(args.baseline)
        comparison = compare_runs(args.baseline, output, before, manifest)
        write_json(output / "comparison.json", comparison)
        manifest["comparison_sha256"] = file_hash(output / "comparison.json")
        if before["status"] != "complete":
            manifest["status"] = "incomplete"
    write_json(output / "manifest.json", manifest)
    (output / "manifest.sha256").write_text(file_hash(output / "manifest.json") + "\n")
    write_report(output, manifest, comparison)
    return output


def inspect(args: argparse.Namespace) -> None:
    run = args.run.resolve()
    manifest = verify_run(run)
    comparison = (
        read_json(run / "comparison.json") if "comparison_sha256" in manifest else None
    )
    known = set(manifest["rules"]["inventory"])
    if comparison:
        known.update(comparison["rules"]["removed"])
    if args.rule not in known:
        raise SnapshotScanError(f"unknown rule: {args.rule}")
    if args.kind != "all" and comparison is None:
        raise SnapshotScanError("--kind requires a comparison run")
    selected = []
    for name in manifest["applications"]:
        if args.app and name != args.app:
            continue
        if args.kind == "all":
            records = [(f, None) for f in result_data(run, name)["findings"]]
        else:
            findings = comparison["applications"][name][args.kind]
            if args.kind == "changed":
                records = [(f["after"], f["before"]) for f in findings]
            else:
                records = [(f, None) for f in findings]
        selected.extend(
            (name, f, old) for f, old in records if f["check_id"] == args.rule
        )
    if args.app and args.app not in manifest["applications"]:
        raise SnapshotScanError(f"unknown application: {args.app}")
    print(
        f"{args.rule}: showing {min(args.limit, len(selected))} of {len(selected)} {args.kind} matches."
    )
    print(
        f"Analysis: {manifest['status']}. No precision/recall conclusion follows from these counts."
    )
    for name, finding, old in selected[: args.limit]:
        path = inside(inside(run / "sources", name), finding["path"])
        line = finding["start"]["line"]
        print(f"\n{name}/{finding['path']}:{line}")
        if old is not None:
            print("Before: " + json.dumps(details(old), sort_keys=True))
            print("After: " + json.dumps(details(finding), sort_keys=True))
        else:
            print(finding.get("extra", {}).get("message", ""))
        text = path.read_text(errors="replace").splitlines()
        for number in range(
            max(1, line - args.context), min(len(text), line + args.context) + 1
        ):
            print(f"{number:>5} {'>' if number == line else ' '} {text[number - 1]}")
    if not selected:
        print(
            "No matching examples here; search relevant source independently for missed cases."
        )


def positive(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be positive")
    return number


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    baseline = commands.add_parser(
        "baseline", help="capture and scan current application worktrees"
    )
    compare = commands.add_parser(
        "compare", help="scan candidate rules on a baseline's retained source"
    )
    view = commands.add_parser(
        "inspect", help="show findings with retained source context"
    )
    for command in (baseline, compare):
        command.add_argument(
            "--output",
            type=Path,
            required=True,
            help="new directory, preferably in scan-results/",
        )
        command.add_argument(
            "--rules",
            type=Path,
            default=ROOT / "rules",
            help="rule directory to evaluate",
        )
        command.add_argument("--semgrep-command", default=DEFAULT_SEMGREP)
    baseline.add_argument("--apps-root", type=Path, default=ROOT.parent)
    baseline.add_argument(
        "--app",
        action="append",
        help="application name; repeat to select several (default: all)",
    )
    baseline.add_argument("--exclude", action="append", default=[])
    baseline.add_argument("--jobs", type=positive, default=4)
    baseline.add_argument("--timeout", type=positive, default=30)
    baseline.add_argument("--max-memory-mib", type=int, default=0)
    baseline.add_argument("--process-timeout-seconds", type=positive, default=1800)
    compare.add_argument("baseline", type=Path)
    view.add_argument("run", type=Path)
    view.add_argument("--rule", required=True, help="exact rule ID")
    view.add_argument("--app")
    view.add_argument(
        "--kind", choices=("all", "added", "removed", "changed"), default="all"
    )
    view.add_argument("--limit", type=positive, default=20)
    view.add_argument("--context", type=positive, default=3)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.action == "inspect":
            inspect(args)
            return 0
        output = evaluate(args)
        manifest = read_json(output / "manifest.json")
        print(f"Evaluation: {output / 'summary.md'}")
        if manifest["status"] != "complete":
            print(
                "Analysis is incomplete; retained errors must be reviewed.",
                file=sys.stderr,
            )
            return 2
        return 0
    except (
        SnapshotScanError,
        AllAppsScanError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
