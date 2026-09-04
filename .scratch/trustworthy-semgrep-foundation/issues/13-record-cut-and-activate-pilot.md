# 13: Record the Review Cut and activate bounded pilot slots

**What to build:** Freeze the current candidate cohort, turn real Compatibility
and Karam observations into a finite Review Queue, and activate exactly five
eligible pilot slots without waiving prerequisites or preselecting outcomes.

**Blocked by:** 03: Enforce append-only history and schema migrations; 07:
Inventory Analysis Targets and Scan Health; 09: Produce the advisory Karam
Milestone Scan.

**Status:** resolved — `portfolio-review-cut-a7e727dc92a640cb` freezes all 61
candidates and activates the five approved pilot slots with Vatsal as reviewer.

- [x] Exact live Frappe, ERPNext, Karam and rules branches, revisions, worktree
      states, source hashes and scan identities are recorded read-only; no update
      or pull is performed.
- [x] Every upstream, backported and Noospheric candidate enters the finite cut
      without grandfathering or assuming the historical count remains current.
- [x] Queue entries record priority band and reason, prerequisites, parser scope,
      match volume, review load, state and intended batch without numeric scoring.
- [x] The five named candidates are provisional; each must have a bounded
      preparation plan, independent reviewer and required evidence before activation.
- [x] Entry records whether a complete current-match and suppression census can
      fit the slot. Without one, the candidate is visibly capped at non-blocking
      for this batch or deferred and substituted; this ceiling is not a
      predetermined catalogue outcome.
- [x] Each activated slot has a discovery plan covering the Engine Match census,
      rule-independent missed-positive search, real safe near-misses and known
      defect/fix/test/review/runtime sources, with unavailable channels explicit.
- [x] A failed entry gate causes visible deferral and same-band substitution; the
      activated identity, owners, approval needs and recovery path are recorded
      in its existing pilot-slot ticket before work starts.
- [x] Later candidates remain queued without speculative mutations, dispositions
      or implementation tickets.
