from __future__ import annotations

import unittest

from scripts.compare_scan_findings import compare, records


def finding(rule: str, path: str, line: int, text: str) -> dict:
    return {"check_id": rule, "path": path, "start": {"line": line}, "extra": {"lines": text}}


class FindingComparisonTest(unittest.TestCase):
    def test_all_states_and_line_only_movement(self) -> None:
        before = records({"findings": [
            finding("r", "same.py", 1, "persist"),
            finding("r", "old.py", 2, "move"),
            finding("r", "gone.py", 3, "resolve"),
        ]})
        after = records({"findings": [
            finding("r", "same.py", 99, "persist"),
            finding("r", "new-path.py", 4, "move"),
            finding("r", "added.py", 5, "new"),
        ]})
        result = compare(before, after)
        self.assertEqual(result["counts"], {"persisting": 1, "moved": 1, "new": 1, "resolved": 1})

    def test_same_snippet_under_different_rule_is_not_moved(self) -> None:
        result = compare(
            records({"findings": [finding("old", "a.py", 1, "same")]}),
            records({"findings": [finding("new", "b.py", 1, "same")]}),
        )
        self.assertEqual(result["counts"], {"persisting": 0, "moved": 0, "new": 1, "resolved": 1})


if __name__ == "__main__":
    unittest.main()
