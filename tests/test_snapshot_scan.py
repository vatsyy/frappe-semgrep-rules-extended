from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANNER = ROOT / "scripts" / "scan_public_snapshot.py"


class CanonicalSnapshotScanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.rules = self.base / "rules"
        self.catalogue = self.base / "catalogue.json"
        self.output = self.base / "output"
        self.source.mkdir()
        self.rules.mkdir()
        self.run_git("init", "-b", "main")
        self.run_git("config", "user.name", "Snapshot Test")
        self.run_git("config", "user.email", "snapshot@example.invalid")
        (self.source / "sample.py").write_text("print('committed')\n")
        self.run_git("add", "sample.py")
        self.run_git("commit", "-m", "public snapshot")
        self.revision = self.run_git("rev-parse", "HEAD").stdout.strip()
        self.run_git("remote", "add", "upstream", "https://github.com/frappe/erpnext.git")
        self.run_git("update-ref", "refs/remotes/upstream/main", self.revision)
        (self.source / "sample.py").write_text("print('uncommitted work')\n")
        (self.rules / "rule.yml").write_text(
            "rules:\n"
            "  - id: snapshot-test\n"
            "    languages: [python]\n"
            "    message: snapshot\n"
            "    severity: INFO\n"
            "    pattern: print(...)\n"
        )
        self.catalogue.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "catalogue_id": "snapshot-test",
                    "claims": [],
                    "retired_ids": [],
                }
            )
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.source), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def fake_semgrep(self, *, errors: list[dict[str, object]] | None = None) -> Path:
        executable = self.base / f"fake-semgrep-{len(list(self.base.glob('fake-*')))}"
        payload = {
            "version": "1.174.0",
            "results": [
                {
                    "check_id": "snapshot-test",
                    "path": "sample.py",
                    "start": {"line": 1, "col": 1, "offset": 0},
                    "end": {"line": 1, "col": 19, "offset": 18},
                    "extra": {"message": "snapshot", "severity": "INFO"},
                }
            ],
            "errors": errors or [],
        }
        executable.write_text(
            "#!/usr/bin/env python3\n"
            "import json, pathlib, sys\n"
            "root = pathlib.Path(__file__).parent\n"
            "if '--version' in sys.argv:\n"
            "    print('1.174.0')\n"
            "    raise SystemExit(0)\n"
            "count = root / 'execution-count'\n"
            "count.write_text(str(int(count.read_text()) + 1) if count.exists() else '1')\n"
            f"print(json.dumps({payload!r}))\n"
        )
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
        return executable

    def run_scanner(
        self,
        semgrep: Path,
        *,
        revision: str | None = None,
        output: Path | None = None,
        source_mode: str = "commit",
    ) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            str(SCANNER),
            "--source-repo",
            str(self.source),
            "--source-mode",
            source_mode,
            "--source-name",
            "erpnext",
            "--rules",
            str(self.rules),
            "--catalogue",
            str(self.catalogue),
            "--semgrep-command",
            str(semgrep),
            "--output",
            str(output or self.output),
        ]
        if source_mode == "commit":
            command.extend(("--source-revision", revision or self.revision))
        return subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def test_complete_scan_runs_once_and_preserves_source_wip(self) -> None:
        before_status = self.run_git("status", "--porcelain=v1").stdout
        before_content = (self.source / "sample.py").read_bytes()
        semgrep = self.fake_semgrep()

        result = self.run_scanner(semgrep)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.base / "execution-count").read_text(), "1")
        self.assertEqual(self.run_git("status", "--porcelain=v1").stdout, before_status)
        self.assertEqual((self.source / "sample.py").read_bytes(), before_content)
        self.assertEqual(
            {path.name for path in self.output.iterdir()},
            {
                "catalogue.json",
                "findings.json",
                "provenance.json",
                "scan-health.json",
                "semgrep.json",
                "semgrep.stderr.txt",
                "summary.md",
            },
        )
        findings = json.loads((self.output / "findings.json").read_text())
        health = json.loads((self.output / "scan-health.json").read_text())
        provenance = json.loads((self.output / "provenance.json").read_text())
        raw = json.loads((self.output / "semgrep.json").read_text())
        contracts = {
            "scan-findings-v1.json": findings,
            "scan-health-v1.json": health,
            "scan-provenance-v1.json": provenance,
        }
        for schema_name, payload in contracts.items():
            with self.subTest(schema=schema_name):
                schema = json.loads(
                    (ROOT / "governance" / "schemas" / schema_name).read_text()
                )
                self.assertEqual(payload["schema_version"], schema["schema_version"])
                self.assertTrue(set(schema["required"]) <= payload.keys())
        self.assertEqual(findings["finding_count"], 1)
        self.assertEqual(findings["findings"], raw["results"])
        self.assertEqual(health["status"], "valid")
        self.assertEqual(provenance["source"]["revision"], self.revision)
        self.assertEqual(provenance["portfolio_execution"], "complete-rule-tree-once")
        self.assertEqual(provenance["ignore_policy"]["mode"], "canonical-explicit")
        self.assertNotIn(str(self.base), json.dumps(provenance))
        self.assertIn("Findings do not fail", (self.output / "summary.md").read_text())

    def test_worktree_mode_includes_modified_and_untracked_source(self) -> None:
        (self.source / "new.py").write_text("print('untracked')\n")
        before_status = self.run_git("status", "--porcelain=v1").stdout
        semgrep = self.fake_semgrep()

        result = self.run_scanner(semgrep, source_mode="worktree")

        self.assertEqual(result.returncode, 0, result.stderr)
        provenance = json.loads((self.output / "provenance.json").read_text())
        self.assertEqual(provenance["source"]["mode"], "worktree")
        self.assertEqual(provenance["source"]["file_count"], 2)
        self.assertRegex(provenance["source"]["content_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(self.run_git("status", "--porcelain=v1").stdout, before_status)

    def test_source_semgrepignore_is_replaced_only_inside_snapshot(self) -> None:
        ignore = self.source / ".semgrepignore"
        ignore.write_text("tests/\n")
        before = ignore.read_bytes()
        semgrep = self.fake_semgrep()

        result = self.run_scanner(semgrep, source_mode="worktree")

        self.assertEqual(result.returncode, 0, result.stderr)
        provenance = json.loads((self.output / "provenance.json").read_text())
        self.assertEqual(
            provenance["ignore_policy"]["source_semgrepignore_sha256"],
            __import__("hashlib").sha256(before).hexdigest(),
        )
        self.assertEqual(ignore.read_bytes(), before)

    def test_mutable_revision_is_rejected_before_execution(self) -> None:
        semgrep = self.fake_semgrep()

        result = self.run_scanner(semgrep, revision="main")

        self.assertEqual(result.returncode, 2)
        self.assertIn("exact 40-character commit SHA", result.stderr)
        self.assertFalse((self.base / "execution-count").exists())

    def test_scan_health_errors_fail_but_retain_structured_outputs(self) -> None:
        semgrep = self.fake_semgrep(
            errors=[{"type": "Parse error", "path": "sample.py", "message": "invalid"}]
        )

        result = self.run_scanner(semgrep)

        self.assertEqual(result.returncode, 2)
        self.assertTrue((self.output / "semgrep.json").is_file())
        health = json.loads((self.output / "scan-health.json").read_text())
        self.assertEqual(health["status"], "invalid")
        self.assertEqual(health["finding_count"], 1)

    def test_existing_output_is_never_overwritten(self) -> None:
        self.output.mkdir()
        marker = self.output / "keep.txt"
        marker.write_text("preserve")
        semgrep = self.fake_semgrep()

        result = self.run_scanner(semgrep)

        self.assertEqual(result.returncode, 2)
        self.assertIn("will not be overwritten", result.stderr)
        self.assertEqual(marker.read_text(), "preserve")


if __name__ == "__main__":
    unittest.main()
