"""Exercise the physical module limit through the real Semgrep CLI."""

import json
import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE = ROOT / "rules/custom/maintainability/python_module_size.yml"


class PythonModuleSizeTest(unittest.TestCase):
    def scan(self, files):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            result = subprocess.run(
                [
                    *shlex.split(os.environ.get("SEMGREP", "semgrep")),
                    "scan",
                    "--config",
                    str(RULE),
                    "--json",
                    "--error",
                    "--metrics=off",
                    "--disable-version-check",
                    "--strict",
                    "--max-target-bytes=0",
                    "--no-git-ignore",
                    "--x-ignore-semgrepignore-files",
                    ".",
                ],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertIn(result.returncode, (0, 1), result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["errors"], [])
            return payload, result.returncode

    def test_rejects_1001_physical_lines(self):
        payload, status = self.scan({"oversized.py": b"# explanation\n" * 1001})
        self.assertEqual(status, 1)
        self.assertEqual(len(payload["results"]), 1)
        self.assertEqual(payload["results"][0]["start"]["line"], 1001)

    def test_boundary_counts_blank_and_comment_lines_with_or_without_final_newline(
        self,
    ):
        files = {"empty.py": b""}
        expected = set()
        for count in (999, 1000, 1001):
            for ending_name, ending in (
                ("lf", b"\n"),
                ("crlf", b"\r\n"),
                ("cr", b"\r"),
            ):
                for final in (False, True):
                    name = f"{ending_name}_{count}_{final}.py"
                    files[name] = ending.join(
                        [b"# comment", *([b""] * (count - 2)), b"pass"]
                    )
                    if final:
                        files[name] += ending
                    if count == 1001:
                        expected.add(name)
        payload, status = self.scan(files)
        self.assertEqual(status, 1)
        self.assertEqual({row["path"] for row in payload["results"]}, expected)
        self.assertEqual(len(payload["results"]), len(expected))

    def test_all_blank_lines_count_without_a_phantom_terminal_line(self):
        payload, _ = self.scan(
            {"allowed.py": b"\n" * 1000, "oversized.py": b"\n" * 1001}
        )
        self.assertEqual([row["path"] for row in payload["results"]], ["oversized.py"])

    def test_gate_includes_tests_ignored_and_large_python_files_only(self):
        long_file = (b"# " + b"x" * 1100 + b"\n") * 1001
        payload, status = self.scan(
            {
                "tests/test_long.py": long_file,
                "fixtures/long.py": b"# comment\n" * 1001,
                "ignored.py": b"# comment\n" * 1001,
                ".semgrepignore": b"ignored.py\nfixtures/\n",
                ".gitignore": b"ignored.py\n",
                "long.js": b"// comment\n" * 1001,
            }
        )
        self.assertEqual(status, 1)
        self.assertEqual(
            {row["path"] for row in payload["results"]},
            {"tests/test_long.py", "fixtures/long.py", "ignored.py"},
        )


if __name__ == "__main__":
    unittest.main()
