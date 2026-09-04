"""Build an independent target and parser-coverage baseline from retained scans."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from scan_public_snapshot import snapshot_worktree

ROOT = Path(__file__).resolve().parents[1]
ELIGIBLE_SUFFIXES = {".cjs", ".js", ".json", ".jsx", ".mjs", ".py", ".ts", ".tsx"}
LANGUAGES = {
    ".cjs": "javascript",
    ".js": "javascript",
    ".json": "json",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
}


class CoverageBaselineError(RuntimeError):
    """Raised when retained scan evidence cannot support a coverage baseline."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan", type=Path, required=True)
    parser.add_argument("--apps-root", type=Path, required=True)
    parser.add_argument(
        "--decisions",
        type=Path,
        default=ROOT / "governance/coverage/parser-gap-decisions-v1.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def load_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise CoverageBaselineError(f"expected an object: {path}")
    return data


def target_id(application: str, path: str) -> str:
    return hashlib.sha256(f"{application}\0{path}".encode()).hexdigest()


def excluded(path: str, patterns: list[str]) -> bool:
    return any(
        fnmatch.fnmatch(path, pattern)
        or fnmatch.fnmatch(Path(path).name, pattern)
        or f"/{pattern}/" in f"/{path}/"
        for pattern in patterns
    )


def build(args: argparse.Namespace) -> dict[str, Any]:
    aggregate = load_object(args.scan / "all-apps.json")
    decisions = load_object(args.decisions)
    decision_index = {
        (gap["application"], gap["path"]): gap for gap in decisions["gaps"]
    }
    observed_gaps: set[str] = set()
    applications: list[dict[str, Any]] = []
    target_ids: set[str] = set()

    for app_record in aggregate["applications"]:
        application = app_record["name"]
        app_scan = args.scan / "applications" / application
        provenance = load_object(app_scan / "provenance.json")
        semgrep = load_object(app_scan / "semgrep.json")
        scanned = {str(path).removeprefix("./") for path in semgrep["paths"]["scanned"]}
        errors = {
            str(error.get("path", "")).removeprefix("./"): error
            for error in semgrep.get("errors", [])
        }
        decided_error_paths = {
            path for (owner, path), _gap in decision_index.items() if owner == application
        }
        if set(errors) != decided_error_paths:
            raise CoverageBaselineError(
                f"{application}: parser decisions do not match retained errors"
            )
        patterns = list(provenance["exclusions"])
        source_repo = args.apps_root / application

        with tempfile.TemporaryDirectory(prefix=f"coverage-{application}-") as directory:
            snapshot = Path(directory) / "source"
            content_hash, _, status_hash = snapshot_worktree(source_repo, snapshot)
            source = provenance["source"]
            if content_hash != source["content_sha256"] or status_hash != source["status_sha256"]:
                raise CoverageBaselineError(
                    f"{application}: source no longer matches retained scan identity"
                )
            targets: list[dict[str, Any]] = []
            for file in sorted(snapshot.rglob("*")):
                if not file.is_file() or file.suffix.lower() not in ELIGIBLE_SUFFIXES:
                    continue
                relative = file.relative_to(snapshot).as_posix()
                identity = target_id(application, relative)
                if identity in target_ids:
                    raise CoverageBaselineError(f"duplicate target identity: {identity}")
                target_ids.add(identity)
                gap = decision_index.get((application, relative))
                if gap is not None:
                    status = "partially-analysed"
                    observed_gaps.add(gap["id"])
                elif relative in scanned:
                    status = "fully-analysed"
                elif excluded(relative, patterns):
                    status = "intentionally-excluded"
                else:
                    status = "unanalysed"
                target = {
                    "id": identity,
                    "content_sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
                    "language": LANGUAGES[file.suffix.lower()],
                    "status": status,
                }
                if gap is not None:
                    target["gap_id"] = gap["id"]
                targets.append(target)

        counts: dict[str, int] = {}
        for target in targets:
            counts[target["status"]] = counts.get(target["status"], 0) + 1
        applications.append(
            {
                "name": application,
                "source_content_sha256": provenance["source"]["content_sha256"],
                "target_count": len(targets),
                "counts": dict(sorted(counts.items())),
                "targets": targets,
            }
        )

    declared_gaps = {gap["id"] for gap in decisions["gaps"]}
    if observed_gaps != declared_gaps:
        missing = ", ".join(sorted(declared_gaps - observed_gaps)) or "none"
        raise CoverageBaselineError(f"declared parser gaps not observed: {missing}")
    return {
        "schema_version": 1,
        "baseline_id": "all-apps-semgrep-ce-1.174.0-v1",
        "engine": "semgrep-ce-1.174.0",
        "rules_content_sha256": load_object(
            args.scan / "applications" / aggregate["applications"][0]["name"] / "provenance.json"
        )["rules"]["content_sha256"],
        "parser_gap_decisions": "governance/coverage/parser-gap-decisions-v1.json",
        "applications": applications,
    }


def main() -> int:
    args = parse_args()
    try:
        baseline = build(args)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n")
    except (CoverageBaselineError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(f"Coverage baseline written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
