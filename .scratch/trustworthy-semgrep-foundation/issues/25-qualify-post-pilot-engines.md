# 25: Qualify post-pilot engine transitions

**What to build:** Use real decided pilot evidence to evaluate exact engine
transitions without changing either the rules-CI or Karam pin merely because a
candidate version is newer.

**Blocked by:** 04: Make the provisional benchmark honest; 05: Pin the rules-CI
engine; 07: Inventory Analysis Targets and Scan Health; 09: Produce the advisory
Karam Milestone Scan; 24: Close the pilot Review Batch.

**Status:** proposed — independent wave review and renewed Vatsal approval required.

- [ ] The matrix records rules CI at `1.174.0`, Karam at `1.172.0`, and any
      proposed candidate as exact immutable versions with complete rule identities.
- [ ] Pinned and candidate engines run native tests, canonical public and Karam
      scans, parser coverage, performance guards and every affected real pilot case.
- [ ] Output, finding, label, coverage, timing and memory drift is reported
      without rewriting evidence or changing current pins.
- [ ] Karam may align to `1.174.0` only if its committed-tree and local evidence
      remains truthful; a newer rules-CI candidate requires the same gate.
- [ ] Any failed dimension preserves the existing pin and records the candidate
      as unqualified with the smallest affected evidence set.
- [ ] A successful transition appends exact provenance and approval before a
      later integration ticket consumes it.
