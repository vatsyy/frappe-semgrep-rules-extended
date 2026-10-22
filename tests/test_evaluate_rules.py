from __future__ import annotations

import json
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.scan_public_snapshot import SnapshotScanError, snapshot_worktree

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/evaluate_rules.py"


class EvaluationCLITest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="evaluation tests ")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.apps = self.base / "apps"
        self.rules = self.base / "rules"
        self.rules.mkdir()
        self.baseline = self.base / "baseline"
        self.candidate = self.base / "candidate"
        for name in ("alpha", "beta"):
            app = self.apps / name
            app.mkdir(parents=True)
            self.git(app, "init", "-b", "main")
            self.git(app, "config", "user.name", "Evaluation Test")
            self.git(app, "config", "user.email", "evaluation@example.invalid")
            (app / "sample.py").write_text("print('committed')\nprint('second')\n")
            (app / ".semgrepignore").write_text("sample.py\n")
            self.git(app, "add", ".")
            self.git(app, "-c", "commit.gpgsign=false", "commit", "-m", "fixture")
            (app / "sample.py").write_text("print('working')\nprint('second')\n")
            (app / "extra.py").write_text("print('untracked')\n")
        self.write_rules()
        self.fake = self.base / "fake semgrep.py"
        self.fake.write_text(
            """import json, pathlib, sys, time
if '--version' in sys.argv:
    print('1.174.0')
    raise SystemExit(0)
source = pathlib.Path.cwd()
rules = pathlib.Path(sys.argv[sys.argv.index('--config') + 1])
if (source / 'timeout').exists():
    print('diagnostic before timeout', file=sys.stderr, flush=True)
    time.sleep(5)
if (source / 'malformed').exists():
    print('{}')
    raise SystemExit(0)
candidate = '# candidate' in (rules / 'rules.yml').read_text()
if (source / 'bad-finding').exists():
    print(json.dumps({'results': [{}], 'errors': [], 'paths': {'scanned': [], 'skipped': []}}))
    raise SystemExit(0)
message = ('after ' if candidate else 'before ') + (source / 'sample.py').read_text().splitlines()[0]
def finding(rule, line):
    return {'check_id': rule, 'path': 'sample.py',
            'start': {'line': line, 'col': 1}, 'end': {'line': line, 'col': 8},
            'extra': {'message': message, 'severity': 'WARNING'}}
errors = [{'type': 'PartialParsing', 'path': 'extra.py', 'message': 'parser gap'}] if (source / 'parser').exists() else []
scanned = ['sample.py'] if '# exclude-extra' in (rules / 'rules.yml').read_text() else ['extra.py', 'sample.py']
matches = [finding('keep', 1), finding('add' if candidate else 'remove', 2)]
if (source / 'multiple-arguments').exists():
    matches = []
    for argument in ('company', 'address', 'address'):
        if argument == 'company' and '# suppress-company' in (rules / 'rules.yml').read_text():
            continue
        match = finding('keep', 1)
        match['extra']['metavars'] = {'$ARG': {'abstract_content': argument}}
        match['extra']['message'] += ' ' + argument
        matches.append(match)
print(json.dumps({'version': '1.174.0',
    'results': matches,
    'errors': errors,
    'paths': {'scanned': scanned, 'skipped': [{'path': 'ignored.py', 'reason': 'semgrepignore_patterns_match'}]}}))
"""
        )
        self.semgrep = shlex.join([sys.executable, str(self.fake)])

    def git(self, app: Path, *args: str) -> bytes:
        return subprocess.check_output(
            ["git", "-C", str(app), *args], stderr=subprocess.DEVNULL
        )

    def write_rules(self, candidate: bool = False) -> None:
        lines = ["rules:", "# candidate" if candidate else "# baseline"]
        for rule_id in ("keep", "add" if candidate else "remove", "silent"):
            lines += [
                f"  - id: {rule_id}",
                "    languages: [python]",
                "    severity: WARNING",
                f"    message: {'after' if candidate else 'before'}",
                "    pattern: print(...)",
            ]
        (self.rules / "rules.yml").write_text("\n".join(lines) + "\n")

    def cli(self, *args: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *(str(arg) for arg in args)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def capture(self, *extra: object) -> subprocess.CompletedProcess[str]:
        return self.cli(
            "baseline",
            "--apps-root",
            self.apps,
            "--rules",
            self.rules,
            "--output",
            self.baseline,
            "--semgrep-command",
            self.semgrep,
            *extra,
        )

    def compare(self, *extra: object) -> subprocess.CompletedProcess[str]:
        return self.cli(
            "compare",
            self.baseline,
            "--rules",
            self.rules,
            "--output",
            self.candidate,
            "--semgrep-command",
            self.semgrep,
            *extra,
        )

    def load(self, run: Path, relative: str) -> dict:
        return json.loads((run / relative).read_text())

    def test_baseline_retains_inputs_commands_and_preserves_dirty_apps(self) -> None:
        app = self.apps / "alpha"
        ignored = app / ".agents"
        ignored.mkdir()
        (ignored / "notes.py").write_text("agent data")
        before = self.git(app, "status", "--porcelain=v1")
        result = self.capture("--app", "alpha", "--exclude", "*.generated.py")

        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = self.load(self.baseline, "manifest.json")
        self.assertEqual(list(manifest["applications"]), ["alpha"])
        self.assertEqual(manifest["engine"]["version"], "1.174.0")
        self.assertEqual((app / ".semgrepignore").read_text(), "sample.py\n")
        self.assertEqual(self.git(app, "status", "--porcelain=v1"), before)
        self.assertEqual(
            (self.baseline / "sources/alpha/sample.py").read_bytes(),
            (app / "sample.py").read_bytes(),
        )
        self.assertTrue((self.baseline / "sources/alpha/extra.py").exists())
        self.assertFalse((self.baseline / "sources/alpha/.agents").exists())
        command = self.load(self.baseline, "applications/alpha/command.json")
        self.assertEqual(command["argv"][:2], [sys.executable, str(self.fake)])
        self.assertEqual(command["cwd"], str(self.baseline / "sources/alpha"))
        self.assertIn("*.generated.py", command["argv"])
        self.assertIn("--oss-only", command["argv"])
        self.assertIn("| silent | 0 |", (self.baseline / "summary.md").read_text())

    def test_compare_uses_retained_source_and_reports_all_three_changes(self) -> None:
        self.assertEqual(self.capture().returncode, 0)
        # The worktrees can move or disappear after capture; compare must not use them.
        self.apps.rename(self.base / "moved-apps")
        self.write_rules(candidate=True)

        result = self.compare()

        self.assertEqual(result.returncode, 0, result.stderr)
        changes = self.load(self.candidate, "comparison.json")
        self.assertEqual(changes["rules"]["added"], ["add"])
        self.assertEqual(changes["rules"]["removed"], ["remove"])
        for app in ("alpha", "beta"):
            delta = changes["applications"][app]
            self.assertEqual([f["check_id"] for f in delta["added"]], ["add"])
            self.assertEqual([f["check_id"] for f in delta["removed"]], ["remove"])
            self.assertEqual(len(delta["changed"]), 1)
            self.assertTrue(delta["paths_identical"])
            self.assertIn(
                "print('working')", delta["changed"][0]["after"]["extra"]["message"]
            )

    def test_inspect_removed_findings_uses_candidate_retained_source(self) -> None:
        self.assertEqual(self.capture().returncode, 0)
        self.write_rules(candidate=True)
        self.assertEqual(self.compare().returncode, 0)
        result = self.cli(
            "inspect",
            self.candidate,
            "--rule",
            "remove",
            "--kind",
            "removed",
            "--limit",
            1,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("showing 1 of 2", result.stdout)
        self.assertIn("alpha/sample.py:2", result.stdout)
        self.assertIn("print('second')", result.stdout)
        self.assertNotIn("beta/sample.py", result.stdout)
        result = self.cli(
            "inspect",
            self.candidate,
            "--rule",
            "keep",
            "--kind",
            "changed",
            "--limit",
            1,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Before:", result.stdout)
        self.assertIn("After:", result.stdout)

    def test_self_comparison_is_empty_but_keeps_parser_gaps(self) -> None:
        (self.apps / "alpha/parser").touch()
        self.assertEqual(self.capture().returncode, 2)
        result = self.compare()
        self.assertEqual(result.returncode, 2, result.stderr)
        changes = self.load(self.candidate, "comparison.json")
        for app in ("alpha", "beta"):
            delta = changes["applications"][app]
            self.assertEqual(delta["added"], [])
            self.assertEqual(delta["removed"], [])
            self.assertEqual(delta["changed"], [])
        gap = changes["applications"]["alpha"]
        self.assertEqual(gap["health_before"]["errors"], gap["health_after"]["errors"])
        self.assertEqual(gap["paths_before"]["skipped"], gap["paths_after"]["skipped"])
        self.assertIn("**incomplete**", (self.candidate / "summary.md").read_text())

    def test_changed_scan_paths_remain_visible(self) -> None:
        self.assertEqual(self.capture().returncode, 0)
        with (self.rules / "rules.yml").open("a") as handle:
            handle.write("# exclude-extra\n")
        self.assertEqual(self.compare().returncode, 0)
        delta = self.load(self.candidate, "comparison.json")["applications"]["alpha"]
        self.assertFalse(delta["paths_identical"])
        self.assertIn("extra.py", delta["paths_before"]["scanned"])
        self.assertNotIn("extra.py", delta["paths_after"]["scanned"])

    def test_multiple_arguments_at_one_location_and_duplicates_are_preserved(
        self,
    ) -> None:
        # Real upstream type-hint findings share the whole function's location.
        (self.apps / "alpha/multiple-arguments").touch()
        self.assertEqual(self.capture().returncode, 0)
        self.assertEqual(self.compare().returncode, 0)
        delta = self.load(self.candidate, "comparison.json")["applications"]["alpha"]
        self.assertEqual(delta["unchanged"], 3)
        self.assertEqual(delta["changed"], [])
        shutil.rmtree(self.candidate)
        self.write_rules(candidate=True)
        with (self.rules / "rules.yml").open("a") as handle:
            handle.write("# suppress-company\n")
        self.assertEqual(self.compare().returncode, 0)
        delta = self.load(self.candidate, "comparison.json")["applications"]["alpha"]
        self.assertEqual(len(delta["removed"]), 1)
        self.assertEqual(len(delta["changed"]), 2)
        self.assertEqual(
            delta["removed"][0]["extra"]["metavars"]["$ARG"]["abstract_content"],
            "company",
        )

    def test_changed_inputs_or_results_are_rejected_without_creating_output(
        self,
    ) -> None:
        self.assertEqual(self.capture().returncode, 0)
        for relative in (
            "manifest.json",
            "sources/alpha/sample.py",
            "rules/rules.yml",
            "applications/alpha/semgrep.json",
        ):
            with self.subTest(relative=relative):
                path = self.baseline / relative
                original = path.read_bytes()
                path.write_bytes(original + b"\n")
                result = self.compare()
                self.assertEqual(result.returncode, 2)
                self.assertIn("changed", result.stderr)
                self.assertFalse(self.candidate.exists())
                path.write_bytes(original)

    def test_bad_engine_output_does_not_prevent_other_apps_from_scanning(self) -> None:
        for marker in ("malformed", "bad-finding"):
            with self.subTest(marker=marker):
                (self.apps / "alpha" / marker).touch()
                result = self.capture()
                self.assertEqual(result.returncode, 2, result.stderr)
                data = self.load(self.baseline, "applications/alpha/results.json")
                self.assertEqual(data["health"]["status"], "invalid")
                self.assertEqual(data["findings"], [])
                self.assertTrue(
                    (self.baseline / "applications/beta/semgrep.json").exists()
                )
                (self.apps / "alpha" / marker).unlink()
                shutil.rmtree(self.baseline)

    def test_timeout_retains_stderr_and_continues(self) -> None:
        (self.apps / "alpha/timeout").touch()
        result = self.capture("--process-timeout-seconds", 1)
        self.assertEqual(result.returncode, 2, result.stderr)
        health = self.load(self.baseline, "applications/alpha/results.json")["health"]
        self.assertIn("exceeded 1s", health["engine_error"])
        self.assertIn(
            "diagnostic before timeout",
            (self.baseline / "applications/alpha/semgrep.stderr.txt").read_text(),
        )
        self.assertTrue((self.baseline / "applications/beta/semgrep.json").exists())

    def test_existing_output_and_nested_inputs_are_rejected(self) -> None:
        self.baseline.mkdir()
        marker = self.baseline / "keep"
        marker.write_text("keep")
        self.assertEqual(self.capture().returncode, 2)
        self.assertEqual(marker.read_text(), "keep")
        for output in (self.apps / "alpha/output", self.rules / "output"):
            result = self.capture("--output", output)
            self.assertEqual(result.returncode, 2)
            self.assertIn("outside", result.stderr)
            self.assertFalse(output.exists())

    def test_wrong_engine_and_unknown_app_fail_before_capture(self) -> None:
        self.fake.write_text("print('1.175.0')\n")
        self.assertEqual(self.capture().returncode, 2)
        self.assertFalse(self.baseline.exists())
        result = self.capture("--app", "absent")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown application", result.stderr)

    def test_compare_cannot_write_into_live_app_or_baseline(self) -> None:
        self.assertEqual(self.capture().returncode, 0)
        for output in (self.apps / "alpha/output", self.baseline / "candidate"):
            result = self.compare("--output", output)
            self.assertEqual(result.returncode, 2)
            self.assertIn("outside", result.stderr)
            self.assertFalse(output.exists())

    def test_output_symlink_is_not_followed(self) -> None:
        destination = self.base / "elsewhere"
        self.baseline.symlink_to(destination)
        result = self.capture()
        self.assertEqual(result.returncode, 2)
        self.assertIn("symbolic link", result.stderr)
        self.assertFalse(destination.exists())

    def test_inspect_rejects_unknown_rules_and_zero_limit(self) -> None:
        self.assertEqual(self.capture().returncode, 0)
        result = self.cli("inspect", self.baseline, "--rule", "absent")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown rule", result.stderr)
        result = self.cli("inspect", self.baseline, "--rule", "keep", "--limit", 0)
        self.assertEqual(result.returncode, 2)
        self.assertIn("must be positive", result.stderr)
        result = self.cli("inspect", self.baseline, "--rule", "silent")
        self.assertEqual(result.returncode, 0)
        self.assertIn("search relevant source independently", result.stdout)

    def test_snapshot_detects_concurrent_content_changes_with_same_git_status(
        self,
    ) -> None:
        source = self.apps / "alpha"
        original_copy = shutil.copy2

        def edit_after_copy(src, dst, **kwargs):
            result = original_copy(src, dst, **kwargs)
            if Path(src).name == "sample.py":
                Path(src).write_text("print('another uncommitted value')\n")
            return result

        with patch(
            "scripts.scan_public_snapshot.shutil.copy2", side_effect=edit_after_copy
        ):
            with self.assertRaisesRegex(SnapshotScanError, "source content changed"):
                snapshot_worktree(source, self.base / "snapshot")


if __name__ == "__main__":
    unittest.main()
