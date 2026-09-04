"""Build the deterministic real-source queue for host-boundary Review Batch 02."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


FILE_RULE = "frappe-security-file-traversal"
PROCESS_RULE = "frappe-subprocess-exec"
SOURCE_SUFFIXES = {".html", ".js", ".json", ".py", ".ts", ".vue"}


def identity(kind: str, application: str, rule_id: str, path: str, line: int, text: str) -> str:
    value = "\0".join((kind, rule_id, application, path, str(line), text))
    return hashlib.sha256(value.encode()).hexdigest()


def access_mode(lines: str) -> str:
    if re.search(r"open\([^\n]*,\s*['\"](?:w|a|x|wb|ab|xb|w\+|a\+)", lines):
        return "write"
    if re.search(r"open\([^\n]*,\s*['\"](?:r|rb|r\+)", lines):
        return "read-explicit"
    return "default-read"


def path_form(lines: str) -> str:
    match = re.search(r"open\((.*)", lines, re.DOTALL)
    argument = match.group(1).strip() if match else lines
    if re.match(r"(?:[rubfRUBF]*)['\"]", argument):
        return "literal"
    if "os.path.join" in argument or "Path(" in argument or "pathlib." in argument:
        return "constructed"
    if any(name in argument for name in ("frappe.get_", "get_site_path", "get_app_path")):
        return "framework-path"
    if "[" in argument or ".get(" in argument or re.match(r"(?:self\.|\w+\.)", argument):
        return "attribute-or-index"
    return "variable"


def file_cluster(lines: str) -> str:
    return f"{access_mode(lines)}:{path_form(lines)}"


def process_cluster(lines: str) -> str:
    call = re.search(r"subprocess\.(run|Popen|call|check_call|check_output)", lines)
    operation = call.group(1) if call else "subprocess"
    if re.search(r"subprocess\.\w+\(\s*\[", lines):
        argument = "literal-list"
    elif re.search(r"subprocess\.\w+\(\s*['\"]", lines):
        argument = "literal-string"
    else:
        argument = "dynamic-expression"
    return f"{operation}:{argument}"


def source_context(source: Path, start: int, end: int, radius: int) -> str:
    lines = source.read_text(errors="replace").splitlines()
    first = max(1, start - radius)
    last = min(len(lines), end + radius)
    return "\n".join(
        f"{line_number}: {lines[line_number - 1]}"
        for line_number in range(first, last + 1)
    )


def tracked_files(repo: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode(errors="replace").strip())
    return [repo / raw.decode() for raw in result.stdout.split(b"\0") if raw]


def qualified_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = qualified_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def independent_discovery_records(apps_root: Path, applications: list[str], radius: int) -> list[dict[str, Any]]:
    records = []
    for application in applications:
        repo = apps_root / application
        for source in tracked_files(repo):
            if (
                source.suffix != ".py"
                or not source.is_file()
                or source.name.startswith("test_")
                or "tests" in source.parts
            ):
                continue
            source_text = source.read_text(errors="replace")
            source_lines = source_text.splitlines()
            try:
                tree = ast.parse(source_text)
            except SyntaxError:
                continue
            relative = source.relative_to(repo).as_posix()
            for function in (
                node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            ):
                parameters = {
                    argument.arg
                    for argument in (
                        *function.args.posonlyargs,
                        *function.args.args,
                        *function.args.kwonlyargs,
                    )
                }
                decorators = {
                    qualified_name(decorator.func if isinstance(decorator, ast.Call) else decorator)
                    for decorator in function.decorator_list
                }
                for call in (node for node in ast.walk(function) if isinstance(node, ast.Call)):
                    call_name = qualified_name(call.func)
                    if (
                        "frappe.whitelist" in decorators
                        and call_name == "open"
                        and call.args
                        and isinstance(call.args[0], ast.Name)
                        and call.args[0].id in parameters
                    ):
                        line = source_lines[call.lineno - 1]
                        records.append({
                            "application": application,
                            "case_id": identity("independent-search", application, FILE_RULE, relative, call.lineno, line),
                            "cluster": "whitelisted-direct-parameter",
                            "context": source_context(source, call.lineno, getattr(call, "end_lineno", call.lineno), radius),
                            "end_line": getattr(call, "end_lineno", call.lineno),
                            "line": call.lineno,
                            "matched_text": line,
                            "path": relative,
                            "record_type": "independent-search",
                            "review": {"basis": "pending", "label": "pending"},
                            "rule_id": FILE_RULE,
                        })
                    if (
                        call_name in {"execute_in_shell", "frappe.utils.execute_in_shell"}
                        and call.args
                        and isinstance(call.args[0], ast.JoinedStr)
                    ):
                        line = source_lines[call.lineno - 1]
                        records.append({
                            "application": application,
                            "case_id": identity("independent-search", application, PROCESS_RULE, relative, call.lineno, line),
                            "cluster": "interpolated-shell-helper",
                            "context": source_context(source, call.lineno, getattr(call, "end_lineno", call.lineno), radius),
                            "end_line": getattr(call, "end_lineno", call.lineno),
                            "line": call.lineno,
                            "matched_text": line,
                            "path": relative,
                            "record_type": "independent-search",
                            "review": {"basis": "pending", "label": "pending"},
                            "rule_id": PROCESS_RULE,
                        })
    return records


def suppression_records(apps_root: Path, applications: list[str], rule_ids: set[str], radius: int) -> list[dict[str, Any]]:
    records = []
    for application in applications:
        repo = apps_root / application
        for source in tracked_files(repo):
            if source.suffix not in SOURCE_SUFFIXES or not source.is_file():
                continue
            lines = source.read_text(errors="replace").splitlines()
            for line_number, line in enumerate(lines, start=1):
                if "nosemgrep" not in line:
                    continue
                for rule_id in rule_ids:
                    if rule_id not in line:
                        continue
                    relative = source.relative_to(repo).as_posix()
                    records.append({
                        "application": application,
                        "case_id": identity("suppression", application, rule_id, relative, line_number, line),
                        "cluster": "suppression",
                        "context": source_context(source, line_number, line_number, radius),
                        "end_line": line_number,
                        "line": line_number,
                        "matched_text": line,
                        "record_type": "suppression",
                        "review": {"basis": "pending", "label": "pending"},
                        "rule_id": rule_id,
                        "path": relative,
                    })
    return records


def build(selection_path: Path, scan: Path, apps_root: Path, radius: int) -> dict[str, Any]:
    selection = json.loads(selection_path.read_text())
    expected_rules = {FILE_RULE, PROCESS_RULE}
    if {row["rule_id"] for row in selection["rules"]} != expected_rules:
        raise ValueError("Batch 02 selection does not contain the two host-boundary rules")

    populations: dict[str, list[dict[str, Any]]] = defaultdict(list)
    applications = sorted(path.name for path in (scan / "applications").iterdir() if path.is_dir())
    for application in applications:
        findings = json.loads((scan / "applications" / application / "findings.json").read_text())["findings"]
        for finding in findings:
            rule_id = finding["check_id"]
            if rule_id not in expected_rules:
                continue
            lines = finding.get("extra", {}).get("lines", "")
            path = finding["path"]
            start = finding["start"]["line"]
            end = finding["end"]["line"]
            cluster = file_cluster(lines) if rule_id == FILE_RULE else process_cluster(lines)
            populations[rule_id].append({
                "application": application,
                "case_id": identity("finding", application, rule_id, path, start, lines),
                "cluster": cluster,
                "context": source_context(apps_root / application / path, start, end, radius),
                "end_line": end,
                "line": start,
                "matched_text": lines,
                "path": path,
                "record_type": "finding",
                "review": {"basis": "pending", "label": "pending"},
                "rule_id": rule_id,
            })

    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in populations[FILE_RULE]:
        groups[(record["application"], record["cluster"])].append(record)
    selected_file = [
        record
        for group in sorted(groups)
        for record in sorted(groups[group], key=lambda item: item["case_id"])[:2]
    ]
    suppressions = suppression_records(apps_root, applications, expected_rules, radius)
    discoveries = independent_discovery_records(apps_root, applications, radius)
    records = selected_file + populations[PROCESS_RULE] + suppressions + discoveries
    records.sort(key=lambda item: (item["rule_id"], item["record_type"], item["application"], item["cluster"], item["case_id"]))

    if not 40 <= len(records) <= 60:
        raise ValueError(f"Batch 02 selected {len(records)} cases outside the 40–60 contract")
    return {
        "schema_version": 1,
        "batch_id": selection["batch_id"],
        "scan": selection["baseline_scan"],
        "sampling": {
            "file_traversal": "first two SHA-256 identities per application, access-mode and path-form cluster",
            "subprocess_exec": "complete current census",
            "suppressions": "complete current census",
        },
        "finding_populations": {rule_id: len(populations[rule_id]) for rule_id in sorted(expected_rules)},
        "suppression_populations": {
            rule_id: sum(record["rule_id"] == rule_id for record in suppressions)
            for rule_id in sorted(expected_rules)
        },
        "independent_discovery_counts": {
            rule_id: sum(record["rule_id"] == rule_id for record in discoveries)
            for rule_id in sorted(expected_rules)
        },
        "sample_counts": {
            rule_id: sum(record["rule_id"] == rule_id for record in records)
            for rule_id in sorted(expected_rules)
        },
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--scan", type=Path, required=True)
    parser.add_argument("--apps-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--context-radius", type=int, default=12)
    args = parser.parse_args()
    if args.context_radius < 1:
        parser.error("context radius must be positive")
    payload = build(
        args.selection.resolve(),
        args.scan.resolve(),
        args.apps_root.resolve(),
        args.context_radius,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"Host-boundary review queue written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
