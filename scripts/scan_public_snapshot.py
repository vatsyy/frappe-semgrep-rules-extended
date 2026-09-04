"""Scan one immutable public Git snapshot with the complete local rule tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
PINNED_SEMGREP = "1.174.0"
DEFAULT_EXCLUSIONS = ("node_modules", "*.min.js", "*.min.css")
SNAPSHOT_EXCLUDED_PREFIXES = (".agents/", ".codex/", ".scratch/", "node_modules/")


class SnapshotScanError(RuntimeError):
    """Raised when immutable scan inputs or outputs are invalid."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", type=Path, required=True)
    parser.add_argument("--source-mode", choices=("commit", "worktree"), default="commit")
    parser.add_argument("--source-revision")
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rules", type=Path, default=ROOT / "rules")
    parser.add_argument("--catalogue", type=Path, default=ROOT / "governance/catalogue.json")
    parser.add_argument("--semgrep-command", default="semgrep")
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--max-memory-mib", type=int, default=0)
    parser.add_argument("--process-timeout-seconds", type=int, default=1800)
    return parser.parse_args()


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SnapshotScanError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def validate_source(repo: Path, revision: str) -> dict[str, str]:
    repo = repo.resolve()
    if not repo.is_dir() or run_git(repo, "rev-parse", "--is-inside-work-tree") != "true":
        raise SnapshotScanError(f"source repository is invalid: {repo}")
    if not FULL_SHA.fullmatch(revision):
        raise SnapshotScanError("source revision must be an exact 40-character commit SHA")
    resolved = run_git(repo, "rev-parse", f"{revision}^{{commit}}")
    if resolved != revision:
        raise SnapshotScanError("source revision did not resolve to the exact requested commit")
    remotes = run_git(repo, "remote").splitlines()
    remote_records: list[tuple[str, str]] = []
    for remote in remotes:
        url = run_git(repo, "remote", "get-url", remote)
        if url.startswith(("https://", "git@github.com:")):
            remote_records.append((remote, url))
    if not remote_records:
        raise SnapshotScanError("source requires a public HTTPS or GitHub remote")
    containing_refs = run_git(
        repo,
        "for-each-ref",
        "--contains",
        revision,
        "--format=%(refname)",
        "refs/remotes",
        "refs/tags",
    ).splitlines()
    if not containing_refs:
        raise SnapshotScanError(
            "source revision is not reachable from a fetched remote ref or tag"
        )
    return {
        "mode": "commit",
        "remote_name": remote_records[0][0],
        "remote_url": remote_records[0][1],
        "revision": revision,
        "tree": run_git(repo, "rev-parse", f"{revision}^{{tree}}"),
        "reachable_ref": min(containing_refs),
    }


def validate_worktree_source(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    if not repo.is_dir() or run_git(repo, "rev-parse", "--is-inside-work-tree") != "true":
        raise SnapshotScanError(f"source repository is invalid: {repo}")
    revision = run_git(repo, "rev-parse", "HEAD")
    remotes = run_git(repo, "remote").splitlines()
    remote_name = remotes[0] if remotes else None
    remote_url = run_git(repo, "remote", "get-url", remote_name) if remote_name else None
    return {
        "mode": "worktree",
        "remote_name": remote_name,
        "remote_url": remote_url,
        "revision": revision,
        "tree": run_git(repo, "rev-parse", "HEAD^{tree}"),
    }


def hash_tree(path: Path) -> tuple[str, int]:
    if not path.is_dir():
        raise SnapshotScanError(f"input tree does not exist: {path}")
    digest = hashlib.sha256()
    count = 0
    for item in sorted(path.rglob("*")):
        if item.is_symlink():
            raise SnapshotScanError(f"symbolic links are not permitted in rule inputs: {item}")
        if not item.is_file():
            continue
        relative = item.relative_to(path).as_posix().encode()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        content = item.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
        count += 1
    if count == 0:
        raise SnapshotScanError(f"input tree contains no files: {path}")
    return digest.hexdigest(), count


def semgrep_version(command: list[str]) -> str:
    result = subprocess.run(
        [*command, "--version"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SnapshotScanError(result.stderr.strip() or "cannot execute Semgrep")
    version = result.stdout.strip()
    if version != PINNED_SEMGREP:
        raise SnapshotScanError(
            f"Semgrep {version!r} is not the qualified {PINNED_SEMGREP} engine"
        )
    return version


def archive_snapshot(repo: Path, revision: str, destination: Path) -> None:
    archive = destination.parent / "source.tar"
    result = subprocess.run(
        ["git", "-C", str(repo), "archive", "--format=tar", "-o", str(archive), revision],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SnapshotScanError(result.stderr.strip() or "cannot archive source revision")
    destination.mkdir()
    try:
        with tarfile.open(archive) as source:
            source.extractall(destination, filter="data")
    finally:
        archive.unlink(missing_ok=True)


def worktree_state(repo: Path) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise SnapshotScanError(result.stderr.decode(errors="replace").strip())
    return result.stdout


def snapshot_worktree(repo: Path, destination: Path) -> tuple[str, int, str]:
    before = worktree_state(repo)
    listed = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        check=False,
        capture_output=True,
    )
    if listed.returncode != 0:
        raise SnapshotScanError(listed.stderr.decode(errors="replace").strip())
    destination.mkdir()
    copied = 0
    for raw_relative in listed.stdout.split(b"\0"):
        if not raw_relative:
            continue
        relative = raw_relative.decode()
        if relative.startswith(SNAPSHOT_EXCLUDED_PREFIXES):
            continue
        source = repo / relative
        if not source.exists():
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target, follow_symlinks=True)
        copied += 1
    after = worktree_state(repo)
    if after != before:
        raise SnapshotScanError("source worktree changed while its snapshot was created")
    content_hash, hashed_files = hash_tree(destination)
    if copied != hashed_files:
        raise SnapshotScanError("worktree snapshot file count is inconsistent")
    return content_hash, copied, hashlib.sha256(before).hexdigest()


def stable_scan_id(
    source_name: str,
    source_identity: str,
    rules_hash: str,
    catalogue_hash: str,
) -> str:
    identity = f"{source_name}\0{source_identity}\0{rules_hash}\0{catalogue_hash}"
    digest = hashlib.sha256(identity.encode()).hexdigest()
    return f"{source_name}-{source_identity[:12]}-{digest[:12]}"


def normalise_results(results: object) -> list[dict[str, Any]]:
    if not isinstance(results, list) or any(not isinstance(item, dict) for item in results):
        raise SnapshotScanError("Semgrep JSON results must be a list of objects")
    return sorted(
        results,
        key=lambda item: (
            str(item.get("path", "")),
            int(item.get("start", {}).get("line", 0)),
            int(item.get("start", {}).get("col", 0)),
            str(item.get("check_id", "")),
        ),
    )


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def install_canonical_ignore(snapshot: Path, exclusions: list[str]) -> str | None:
    """Replace implicit/app-local scan ignores inside the disposable snapshot."""
    ignore = snapshot / ".semgrepignore"
    original_hash = hashlib.sha256(ignore.read_bytes()).hexdigest() if ignore.exists() else None
    ignore.write_text("\n".join(exclusions) + "\n")
    return original_hash


def error_kind(error: dict[str, Any]) -> str:
    value = error.get("type", "error")
    if isinstance(value, list) and value:
        return str(value[0])
    return str(value)


def write_summary(
    path: Path,
    provenance: dict[str, Any],
    findings: list[dict[str, Any]],
    health: dict[str, Any],
) -> None:
    by_rule = Counter(str(item.get("check_id", "<unknown>")) for item in findings)
    lines = [
        f"# Canonical scan: {provenance['scan_id']}",
        "",
        f"- Source: `{provenance['source']['name']}` at `{provenance['source']['revision']}`",
        f"- Engine: Semgrep CE `{provenance['engine']['version']}`",
        f"- Rule-tree SHA-256: `{provenance['rules']['content_sha256']}`",
        f"- Findings: {len(findings)} advisory matches",
        f"- Scan Health: **{health['status']}**",
        "- Gate Evaluation: not performed by Ticket 06",
        "",
        "Findings do not fail this command and Semgrep severity is not policy.",
        "",
        "## Findings by rule",
        "",
    ]
    if by_rule:
        lines.extend(f"- `{rule_id}`: {count}" for rule_id, count in sorted(by_rule.items()))
    else:
        lines.append("- None")
    if health["errors"]:
        lines.extend(("", "## Scan Health errors", ""))
        lines.extend(
            f"- {error_kind(error)}: {error.get('path', '<unknown>')}"
            for error in health["errors"]
        )
    path.write_text("\n".join(lines) + "\n")


def execute(args: argparse.Namespace) -> tuple[int, Path]:
    output = args.output.resolve()
    if output.exists():
        raise SnapshotScanError(f"output already exists and will not be overwritten: {output}")
    if min(args.jobs, args.timeout, args.process_timeout_seconds) < 1 or args.max_memory_mib < 0:
        raise SnapshotScanError("resource settings must be positive; max memory may be zero")

    rules = args.rules.resolve()
    catalogue = args.catalogue.resolve()
    if args.source_mode == "commit":
        if args.source_revision is None:
            raise SnapshotScanError("commit mode requires --source-revision")
        source = validate_source(args.source_repo, args.source_revision)
    else:
        if args.source_revision is not None:
            raise SnapshotScanError("worktree mode uses a content hash, not --source-revision")
        source = validate_worktree_source(args.source_repo)
    command = shlex.split(args.semgrep_command)
    if not command:
        raise SnapshotScanError("Semgrep command cannot be empty")
    version = semgrep_version(command)
    rules_hash, rules_files = hash_tree(rules)
    catalogue_bytes = catalogue.read_bytes()
    catalogue_data = json.loads(catalogue_bytes)
    if catalogue_data.get("schema_version") != 1:
        raise SnapshotScanError("catalogue must use schema version 1")
    catalogue_hash = hashlib.sha256(catalogue_bytes).hexdigest()
    exclusions = sorted(set(DEFAULT_EXCLUSIONS) | set(args.exclude))
    output.parent.mkdir(parents=True, exist_ok=True)

    with (
        tempfile.TemporaryDirectory(prefix="semgrep-public-snapshot-") as temporary,
        tempfile.TemporaryDirectory(
            prefix=".canonical-scan-", dir=output.parent
        ) as staging,
    ):
        temporary_path = Path(temporary)
        snapshot = temporary_path / "source"
        rules_snapshot = temporary_path / "rules"
        staged_output = Path(staging) / "output"
        staged_output.mkdir()
        if args.source_mode == "commit":
            archive_snapshot(args.source_repo.resolve(), source["revision"], snapshot)
            source_identity = source["revision"]
        else:
            source_identity, source_files, status_hash = snapshot_worktree(
                args.source_repo.resolve(), snapshot
            )
            source.update(
                {
                    "content_sha256": source_identity,
                    "file_count": source_files,
                    "status_sha256": status_hash,
                }
            )
        scan_id = stable_scan_id(
            args.source_name, source_identity, rules_hash, catalogue_hash
        )
        original_ignore_hash = install_canonical_ignore(snapshot, exclusions)
        shutil.copytree(rules, rules_snapshot)
        copied_rules_hash, copied_rules_files = hash_tree(rules_snapshot)
        if (copied_rules_hash, copied_rules_files) != (rules_hash, rules_files):
            raise SnapshotScanError("rule inputs changed while their snapshot was created")
        (staged_output / "catalogue.json").write_bytes(catalogue_bytes)

        scan_command = [
            *command,
            "scan",
            "--config",
            str(rules_snapshot),
            "--json",
            "--quiet",
            "--metrics=off",
            "--disable-version-check",
            "--no-git-ignore",
            "--no-rewrite-rule-ids",
            "--time",
            "--jobs",
            str(args.jobs),
            "--timeout",
            str(args.timeout),
            "--max-memory",
            str(args.max_memory_mib),
        ]
        for exclusion in exclusions:
            scan_command.extend(("--exclude", exclusion))
        scan_command.append(".")

        raw_path = staged_output / "semgrep.json"
        with raw_path.open("w") as raw:
            try:
                result = subprocess.run(
                    scan_command,
                    cwd=snapshot,
                    check=False,
                    stdout=raw,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=args.process_timeout_seconds,
                )
                engine_error = None
            except subprocess.TimeoutExpired as exc:
                result = None
                engine_error = f"Semgrep exceeded {args.process_timeout_seconds}s: {exc}"

        stderr = "" if result is None else result.stderr
        (staged_output / "semgrep.stderr.txt").write_text(stderr)
        try:
            raw_payload = json.loads(raw_path.read_text()) if result is not None else {}
        except json.JSONDecodeError as exc:
            raw_payload = {}
            engine_error = f"Semgrep did not produce valid JSON: {exc}"
        errors = raw_payload.get("errors", [])
        if not isinstance(errors, list):
            errors = [{"type": "invalid-output", "message": "errors was not a list"}]
        findings = normalise_results(raw_payload.get("results", []))
        complete = result is not None and result.returncode == 0 and not engine_error
        status = "valid" if complete and not errors else "invalid"

        provenance = {
            "schema_version": 1,
            "scan_id": scan_id,
            "generated_at": datetime.now(UTC).isoformat(),
            "engine": {"name": "semgrep-ce", "version": version},
            "rules": {
                "path": "rules",
                "content_sha256": rules_hash,
                "file_count": rules_files,
            },
            "catalogue": {
                "path": "governance/catalogue.json",
                "catalogue_id": catalogue_data.get("catalogue_id"),
                "schema_version": catalogue_data["schema_version"],
                "content_sha256": catalogue_hash,
            },
            "source": {"name": args.source_name, **source},
            "exclusions": exclusions,
            "ignore_policy": {
                "mode": "canonical-explicit",
                "source_semgrepignore_sha256": original_ignore_hash,
            },
            "resource_settings": {
                "jobs": args.jobs,
                "timeout_seconds_per_rule": args.timeout,
                "max_memory_mib": args.max_memory_mib,
                "process_timeout_seconds": args.process_timeout_seconds,
            },
            "engine_settings": {
                "metrics": "off",
                "version_check": False,
                "git_ignore": False,
                "rewrite_rule_ids": False,
            },
            "portfolio_execution": "complete-rule-tree-once",
        }
        findings_payload = {
            "schema_version": 1,
            "scan_id": scan_id,
            "finding_count": len(findings),
            "findings": findings,
        }
        health = {
            "schema_version": 1,
            "scan_id": scan_id,
            "status": status,
            "execution_complete": complete,
            "engine_exit_code": None if result is None else result.returncode,
            "engine_error": engine_error,
            "errors": errors,
            "finding_count": len(findings),
        }
        write_json(staged_output / "provenance.json", provenance)
        write_json(staged_output / "findings.json", findings_payload)
        write_json(staged_output / "scan-health.json", health)
        write_summary(staged_output / "summary.md", provenance, findings, health)
        staged_output.replace(output)

    return (0 if status == "valid" else 2), output


def main() -> int:
    args = parse_args()
    try:
        status, output = execute(args)
    except (SnapshotScanError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Canonical snapshot scan outputs: {output}")
    if status:
        print(f"ERROR: Scan Health is invalid; inspect {output / 'scan-health.json'}", file=sys.stderr)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
