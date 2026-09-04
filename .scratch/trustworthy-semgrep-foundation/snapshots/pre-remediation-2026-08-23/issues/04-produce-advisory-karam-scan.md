# 04: Produce a complete advisory Karam Milestone Scan

**What to build:** Use the canonical scan boundary against the latest complete
Karam Finance worktree so the pilot receives current match, coverage, cost, and
privacy-safe evidence before any candidate gains enforcement power.

**Blocked by:** 03: Produce a complete Compatibility Scan.

**Status:** ready-for-agent

- [ ] The local scan analyses the complete Karam worktree, including untracked
      v16 migration files, and records exact base revision, worktree state,
      timestamps, and relevant file hashes.
- [ ] No Karam file is changed, copied into public fixtures, archived, stashed,
      committed, cleaned, or treated as stable ground truth.
- [ ] Current Engine Matches, suppressions, parser coverage, runtime, memory,
      unique issues, and review-volume inputs are captured for pilot triage.
- [ ] All rule output remains explicitly unaudited advisory evidence; severity
      and `--error` cannot fail this scan.
- [ ] Raw Karam findings stay access-controlled while public artefacts use opaque
      evidence identifiers and non-sensitive provenance.
- [ ] A committed-tree mode can reproduce the same scan contract for later CI
      integration without trusting the local result.
