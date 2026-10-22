from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "python314_compatibility.py"
TEMPLATE_STRING_FIXTURE = (
    ROOT / "tests" / "fixtures" / "python314_template_string.py"
)
RULES = ROOT / "rules" / "custom"


def annotations(kind: str) -> set[tuple[str, int]]:
    lines = FIXTURE.read_text().splitlines()
    return {
        (line.split(f"# {kind}: ", 1)[1].strip(), number + 1)
        for number, line in enumerate(lines, start=1)
        if f"# {kind}: " in line
    }


class Python314RuleCompatibilityTest(unittest.TestCase):
    def scan(self, fixture: Path) -> subprocess.CompletedProcess[str]:
        semgrep = shlex.split(os.environ.get("SEMGREP", "semgrep"))
        with tempfile.TemporaryDirectory(prefix="python314-semgrep-") as directory:
            target = Path(directory) / fixture.name
            shutil.copyfile(fixture, target)
            return subprocess.run(
                [
                    *semgrep,
                    "scan",
                    "--config",
                    str(RULES),
                    "--json",
                    "--quiet",
                    "--metrics=off",
                    "--disable-version-check",
                    "--no-rewrite-rule-ids",
                    str(target),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

    def test_modern_syntax_preserves_rule_findings_and_safe_cases(self) -> None:
        result = self.scan(FIXTURE)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["errors"], [])
        actual = {
            (finding["check_id"], finding["start"]["line"])
            for finding in payload["results"]
        }
        self.assertEqual(annotations("expect") - actual, set())
        self.assertEqual(annotations("safe") & actual, set())

    @unittest.expectedFailure
    def test_template_strings_parse_without_scan_health_warnings(self) -> None:
        result = self.scan(TEMPLATE_STRING_FIXTURE)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["errors"], [])


if __name__ == "__main__":
    unittest.main()
