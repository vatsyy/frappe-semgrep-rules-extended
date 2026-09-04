"""Run the canonical worktree scan across every Git repository in an apps directory."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCANNER = ROOT / "scripts" / "scan_public_snapshot.py"


class AllAppsScanError(RuntimeError):
    """Raised when the aggregate scan cannot be reproduced safely."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apps-root", type=Path, default=ROOT.parent)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--exclude-repo", action="append", default=[ROOT.name])
    parser.add_argument("--semgrep-command", default="semgrep")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--max-memory-mib", type=int, default=0)
    parser.add_argument("--process-timeout-seconds", type=int, default=1800)
    return parser.parse_args()


def discover_apps(apps_root: Path, excluded: set[str]) -> list[Path]:
    apps = [
        path
        for path in apps_root.resolve().iterdir()
        if path.is_dir() and (path / ".git").exists() and path.name not in excluded
    ]
    if not apps:
        raise AllAppsScanError(f"no Git application repositories found in {apps_root}")
    return sorted(apps, key=lambda path: path.name)


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise AllAppsScanError(f"cannot load canonical output {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise AllAppsScanError(f"canonical output is not an object: {path}")
    return payload


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_summary(path: Path, aggregate: dict[str, Any]) -> None:
    lines = [
        "# All-apps canonical Semgrep scan",
        "",
        f"- Applications: {aggregate['application_count']}",
        f"- Advisory matches: {aggregate['finding_count']}",
        f"- Scan Health: **{aggregate['status']}**",
        "",
        "Matches are unreviewed advisory evidence, not confirmed defects.",
        "Semgrep severity does not govern this result.",
        "",
        "## Applications",
        "",
        "| Application | Source identity | Findings | Scan Health | Errors |",
        "|---|---|---:|---|---:|",
    ]
    for app in aggregate["applications"]:
        source = app.get("source", {})
        identity = source.get("content_sha256", source.get("revision", "<missing>"))
        lines.append(
            f"| `{app['name']}` | `{str(identity)[:12]}` | {app['finding_count']} | "
            f"{app['status']} | {app['error_count']} |"
        )
    lines.extend(("", "## Findings by rule", ""))
    if aggregate["findings_by_rule"]:
        lines.extend(
            f"- `{rule_id}`: {count}"
            for rule_id, count in aggregate["findings_by_rule"].items()
        )
    else:
        lines.append("- None")
    path.write_text("\n".join(lines) + "\n")


def execute(args: argparse.Namespace) -> tuple[int, Path]:
    output = args.output.resolve()
    if output.exists():
        raise AllAppsScanError(f"output already exists and will not be overwritten: {output}")
    apps = discover_apps(args.apps_root, set(args.exclude_repo))
    output.parent.mkdir(parents=True, exist_ok=True)
    app_records: list[dict[str, Any]] = []
    all_rules: Counter[str] = Counter()
    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix=".all-apps-scan-", dir=output.parent) as staging:
        staged_output = Path(staging) / "output"
        applications_output = staged_output / "applications"
        diagnostics_output = staged_output / "diagnostics"
        applications_output.mkdir(parents=True)
        diagnostics_output.mkdir()
        for app in apps:
            print(f"Scanning {app.name}...", flush=True)
            app_output = applications_output / app.name
            command = [
                sys.executable,
                str(SCANNER),
                "--source-repo",
                str(app),
                "--source-mode",
                "worktree",
                "--source-name",
                app.name,
                "--output",
                str(app_output),
                "--semgrep-command",
                args.semgrep_command,
                "--jobs",
                str(args.jobs),
                "--timeout",
                str(args.timeout),
                "--max-memory-mib",
                str(args.max_memory_mib),
                "--process-timeout-seconds",
                str(args.process_timeout_seconds),
            ]
            result = subprocess.run(
                command,
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            (diagnostics_output / f"{app.name}.stdout.txt").write_text(result.stdout)
            (diagnostics_output / f"{app.name}.stderr.txt").write_text(result.stderr)
            if not app_output.is_dir():
                failures.append(f"{app.name}: canonical scan produced no outputs")
                app_records.append(
                    {
                        "name": app.name,
                        "status": "invalid",
                        "finding_count": 0,
                        "error_count": 1,
                        "source": {},
                        "process_exit_code": result.returncode,
                    }
                )
                continue
            provenance = load_json(app_output / "provenance.json")
            health = load_json(app_output / "scan-health.json")
            findings = load_json(app_output / "findings.json")
            for finding in findings.get("findings", []):
                all_rules[str(finding.get("check_id", "<unknown>"))] += 1
            error_count = len(health.get("errors", []))
            status = str(health.get("status", "invalid"))
            if status != "valid":
                failures.append(f"{app.name}: Scan Health {status} ({error_count} errors)")
            app_records.append(
                {
                    "name": app.name,
                    "scan_id": provenance.get("scan_id"),
                    "status": status,
                    "finding_count": findings.get("finding_count", 0),
                    "error_count": error_count,
                    "source": provenance.get("source", {}),
                    "process_exit_code": result.returncode,
                }
            )

        aggregate = {
            "schema_version": 1,
            "status": "valid" if not failures else "invalid",
            "application_count": len(app_records),
            "finding_count": sum(int(app["finding_count"]) for app in app_records),
            "findings_by_rule": dict(sorted(all_rules.items())),
            "applications": app_records,
            "failures": failures,
        }
        write_json(staged_output / "all-apps.json", aggregate)
        write_summary(staged_output / "summary.md", aggregate)
        staged_output.replace(output)

    return (0 if not failures else 2), output


def main() -> int:
    args = parse_args()
    try:
        status, output = execute(args)
    except (AllAppsScanError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"All-apps scan outputs: {output}")
    if status:
        print(f"ERROR: aggregate Scan Health is invalid; inspect {output / 'summary.md'}", file=sys.stderr)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
