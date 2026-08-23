from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "benchmarks" / "run.py"
MANIFEST = ROOT / "benchmarks" / "manifest.json"


class BenchmarkContractTest(unittest.TestCase):
    def run_validation(self, manifest: Path = MANIFEST) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--validate-only",
                "--manifest",
                str(manifest),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_manifest_is_explicitly_compatibility_only(self) -> None:
        result = self.run_validation()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Compatibility manifest valid: 17 fixtures", result.stdout)

    def test_runner_reports_fixture_behaviour_without_admission_tiers(self) -> None:
        result = subprocess.run(
            [sys.executable, str(RUNNER)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Compatibility benchmark passed: 17 fixtures", result.stdout)
        self.assertNotIn("blocking=", result.stdout)
        self.assertNotIn("monitor=", result.stdout)
        self.assertNotIn("audit=", result.stdout)

    def test_manifest_refuses_admission_language_and_mutable_versions(self) -> None:
        base = json.loads(MANIFEST.read_text())
        mutations = (
            (
                "tier",
                lambda data: data["cases"][0]["expected"]["findings"][0].update(
                    {"tier": "blocking"}
                ),
                "cannot declare tier",
            ),
            (
                "admission eligibility",
                lambda data: data["cases"][0].update({"admission_eligible": True}),
                "admission_eligible must be false",
            ),
            (
                "mutable version",
                lambda data: data["cases"][0].update(
                    {"observed_semgrep_versions": ["latest"]}
                ),
                "requires exact versions",
            ),
        )
        for name, mutate, expected_error in mutations:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                data = deepcopy(base)
                mutate(data)
                path = Path(directory) / "manifest.json"
                path.write_text(json.dumps(data))

                result = self.run_validation(path)

                self.assertEqual(result.returncode, 2)
                self.assertIn(expected_error, result.stderr)


if __name__ == "__main__":
    unittest.main()
