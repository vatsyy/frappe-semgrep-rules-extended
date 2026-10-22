"""Check expected rule matches across the authored regression cases."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ROOT / "benchmarks"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semgrep-command", default="semgrep")
    args = parser.parse_args()
    cases = json.loads((BENCHMARKS / "manifest.json").read_text())
    expected = {
        str(Path("benchmarks") / path): set(case["findings"])
        for path, case in cases.items()
    }
    files = {
        str(path.relative_to(ROOT))
        for path in (BENCHMARKS / "cases").rglob("*")
        if path.is_file()
        and path.suffix in {".py", ".js", ".html", ".json", ".yaml", ".yml"}
    }
    if files != expected.keys():
        print(f"Fixture inventory mismatch: {sorted(files ^ expected.keys())}")
        return 1
    result = subprocess.run(
        [
            *shlex.split(args.semgrep_command),
            "scan",
            "--config",
            "rules",
            "--json",
            "--quiet",
            "--metrics=off",
            "--disable-version-check",
            "--no-rewrite-rule-ids",
            "benchmarks/cases",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode:
        print(result.stderr)
        return 1
    payload = json.loads(result.stdout)
    if payload.get("errors"):
        print(json.dumps(payload["errors"], indent=2))
        return 1
    actual = {path: set() for path in expected}
    for finding in payload["results"]:
        actual.setdefault(finding["path"], set()).add(finding["check_id"])
    failures = []
    for path in sorted(expected.keys() | actual.keys()):
        wanted, observed = expected.get(path, set()), actual.get(path, set())
        if wanted != observed:
            failures.append(
                f"{path}: missing {sorted(wanted - observed)}; unexpected {sorted(observed - wanted)}"
            )
    for failure in failures:
        print(failure)
    if not failures:
        print(f"Regression cases passed: {len(expected)} fixtures.")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
