# Maintainability rules

`frappe-python-module-too-many-lines` reports Python modules exceeding 1,000
physical lines, including comments, docstrings and blank lines. A final newline
does not add a phantom line. LF, CRLF and legacy CR line endings are supported.
This is a repository policy check, not a claim that every large module is faulty.

The same-basename fixture deliberately exceeds the limit. Generated CLI cases in
`tests/test_python_module_size.py` cover 999/1,000/1,001 lines, final newlines,
large files, ignored paths, tests and non-Python files. `make test` collects them;
`SEMGREP` selects the executable for these tests as well as the other checks.

For a physical-size gate, use `--max-target-bytes=0 --no-git-ignore
--x-ignore-semgrepignore-files` so scan exclusions cannot silently omit modules.
The last option is internal to Semgrep; keep the scanner pinned and run these
CLI tests before upgrading it. Normal scans using this rule retain their normal
target-selection policy. Legacy CR files are counted correctly, but Semgrep's
displayed line number follows its own newline handling.
