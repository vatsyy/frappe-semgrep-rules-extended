"""Verify rule ownership, metadata, fixtures and the immutable upstream mirror."""

from __future__ import annotations

import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "rules"
CUSTOM = RULES / "custom"
BACKPORTS = RULES / "backports"
UPSTREAM = RULES / "upstream" / "frappe"


RULE_ID = re.compile(r"(?m)^\s*-\s+id:\s*([A-Za-z0-9_.-]+)\s*$")


def rule_blocks(path: Path) -> list[tuple[str, str]]:
    text = path.read_text()
    matches = list(RULE_ID.finditer(text))
    return [
        (match.group(1), text[match.start() : matches[index + 1].start()])
        for index, match in enumerate(matches)
        if index + 1 < len(matches)
    ] + ([(matches[-1].group(1), text[matches[-1].start() :])] if matches else [])


def scalar(block: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s+{re.escape(key)}:\s*['\"]?([^'\"\s]+)", block)
    return match.group(1) if match else None


def has_annotation(targets: str, annotation: str, rule_id: str) -> bool:
    return bool(re.search(rf"(?:^|\s){annotation}:\s*{re.escape(rule_id)}(?:\s|$)", targets))


def check_owned_rule(
    rule_id: str, block: str, yaml_path: Path, ownership: str, errors: list[str]
) -> None:
    location = yaml_path.relative_to(ROOT)
    if not rule_id.startswith("frappe-"):
        errors.append(f"{location}: owned rule IDs must start with 'frappe-'")
        return

    if not re.search(r"(?m)^\s+metadata:\s*$", block):
        errors.append(f"{location}: {rule_id} requires metadata")
        return

    if ownership == "custom":
        expected_category = yaml_path.parent.name
        if scalar(block, "origin") != "custom":
            errors.append(f"{location}: {rule_id} requires metadata.origin: custom")
        if scalar(block, "category") != expected_category:
            errors.append(
                f"{location}: {rule_id} category must match directory '{expected_category}'"
            )
        if scalar(block, "confidence") not in {"LOW", "MEDIUM", "HIGH"}:
            errors.append(f"{location}: {rule_id} has invalid metadata.confidence")
        if not re.search(r"(?m)^\s+technology:\s*\[[^]]*\bfrappe\b[^]]*]", block):
            errors.append(f"{location}: {rule_id} requires metadata.technology: [frappe]")
    else:
        if not scalar(block, "origin"):
            errors.append(f"{location}: {rule_id} requires metadata.origin")
        if not scalar(block, "source_repository"):
            errors.append(f"{location}: {rule_id} requires metadata.source_repository")
        revision = scalar(block, "source_revision")
        if not revision or not re.fullmatch(r"[0-9a-f]{40}", revision):
            errors.append(f"{location}: {rule_id} requires a 40-character source_revision")

    targets = "\n".join(
        path.read_text(errors="replace")
        for path in sorted(yaml_path.parent.glob(f"{yaml_path.stem}.*"))
        if path.suffix not in {".yml", ".yaml", ".md"}
    )
    if not targets:
        errors.append(f"{location}: {rule_id} has no same-basename test target")
    elif not has_annotation(targets, "ruleid", rule_id):
        errors.append(f"{location}: {rule_id} has no positive ruleid fixture")
    elif not has_annotation(targets, "ok", rule_id):
        errors.append(f"{location}: {rule_id} has no negative ok fixture")


def check_rule_contract(errors: list[str]) -> int:
    occurrences: defaultdict[str, list[Path]] = defaultdict(list)
    rule_count = 0
    for yaml_path in sorted(RULES.rglob("*.yml")):
        blocks = rule_blocks(yaml_path)
        if not blocks:
            errors.append(f"{yaml_path.relative_to(ROOT)}: no rule IDs found")
        for rule_id, block in blocks:
            rule_count += 1
            occurrences[rule_id].append(yaml_path)
            if yaml_path.is_relative_to(CUSTOM):
                check_owned_rule(rule_id, block, yaml_path, "custom", errors)
            elif yaml_path.is_relative_to(BACKPORTS):
                check_owned_rule(rule_id, block, yaml_path, "backport", errors)

    for rule_id, paths in occurrences.items():
        if len(paths) > 1:
            locations = ", ".join(str(path.relative_to(ROOT)) for path in paths)
            errors.append(f"duplicate rule ID {rule_id}: {locations}")
    return rule_count


def git_output(*args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE
    ).stdout


def check_upstream_mirror(errors: list[str]) -> int:
    upstream_doc = (ROOT / "UPSTREAM.md").read_text()
    revision_match = re.search(
        r"Last organised upstream commit\s*\|\s*`([0-9a-f]{40})`", upstream_doc
    )
    if not revision_match:
        errors.append("UPSTREAM.md: cannot resolve the recorded upstream revision")
        return 0
    revision = revision_match.group(1)

    try:
        source_paths = [
            Path(line)
            for line in git_output("ls-tree", "-r", "--name-only", revision, "--", "rules")
            .decode()
            .splitlines()
        ]
    except subprocess.CalledProcessError:
        errors.append(f"UPSTREAM.md: recorded revision {revision} is unavailable in git history")
        return 0

    expected = {path.relative_to("rules") for path in source_paths}
    actual = {path.relative_to(UPSTREAM) for path in UPSTREAM.rglob("*") if path.is_file()}
    for missing in sorted(expected - actual):
        errors.append(f"rules/upstream/frappe/{missing}: missing upstream file")
    for extra in sorted(actual - expected):
        errors.append(f"rules/upstream/frappe/{extra}: not present in recorded upstream revision")

    for source_path in source_paths:
        relative = source_path.relative_to("rules")
        destination = UPSTREAM / relative
        if destination.is_file() and git_output("show", f"{revision}:{source_path}") != destination.read_bytes():
            errors.append(f"rules/upstream/frappe/{relative}: differs from recorded upstream")
    return len(source_paths)


def main() -> int:
    errors: list[str] = []
    rule_count = check_rule_contract(errors)
    upstream_file_count = check_upstream_mirror(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        f"Rule contract valid: {rule_count} unique rules; "
        f"{upstream_file_count} upstream files unchanged."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
