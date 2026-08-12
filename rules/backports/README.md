# Backported rules

This directory contains rules maintained by another identified Frappe
repository but not yet available from `frappe/semgrep-rules`.

Each backport must record its source repository and immutable source revision.
Keep its rule IDs aligned with the source so audit findings and suppressions
remain portable. Do not modify a backport silently; either refresh it from its
source or move a deliberately divergent rule into `rules/custom/` under a new
ID.

Remove a backport when `frappe/semgrep-rules` adopts the same rule ID.
