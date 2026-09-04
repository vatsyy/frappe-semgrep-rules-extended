# 09: Produce the advisory Karam Milestone Scan

**What to build:** Run the canonical boundary read-only against the complete
private Karam worktree and make the approved blocking and advisory input lanes
explicit before pilot selection.

**Blocked by:** 07: Inventory Analysis Targets and Scan Health.

**Status:** proposed — independent wave review and renewed Vatsal approval required.

- [ ] The governed rules-repository catalogue is scanned as one explicitly
      unaudited, non-blocking lane against tracked and untracked Karam files.
- [ ] The Karam-local rule and Registry pack are reported in separate advisory
      lanes; their results cannot enter Gate Evaluation or admission metrics.
- [ ] A mutable Registry alias is labelled non-reproducible and records resolved
      provenance where available; it never becomes a blocking input.
- [ ] The scan records exact base revision, worktree state, timestamps, file
      hashes, target coverage, matches, suppressions, cost and review-volume inputs.
- [ ] Raw Karam findings remain access-controlled; public artefacts contain only
      opaque IDs and non-sensitive provenance.
- [ ] No Karam file is edited, copied into public fixtures, archived, stashed,
      committed, cleaned or treated as stable ground truth.
