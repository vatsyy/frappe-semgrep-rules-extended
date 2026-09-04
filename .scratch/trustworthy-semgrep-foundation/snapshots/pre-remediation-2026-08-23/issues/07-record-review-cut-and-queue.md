# 07: Record the Portfolio Review Cut and Review Queue

**What to build:** Freeze the latest locally available Rule Candidate cohort and
turn the pre-pilot Compatibility and Karam evidence into a finite,
risk- and evidence-led Review Queue.

**Blocked by:** 02: Make the provisional benchmark honest; 03: Produce a
complete Compatibility Scan; 04: Produce a complete advisory Karam Milestone
Scan; 05: Gate a canonical scan safely; 06: Pin and qualify Semgrep engines in
rules CI.

**Status:** ready-for-agent

- [ ] Noema assumes Vatsal updated local Frappe and ERPNext first, records their
      exact live branches, revisions, worktree states, and source hashes
      read-only, and never updates them.
- [ ] The Portfolio Review Cut records every current upstream, backported, and
      Noospheric Rule Candidate without grandfathering and does not assume the
      historical count remains current.
- [ ] Each queue entry records priority band and reason, intended Review Batch,
      entry prerequisites, parser scope, current match volume, estimated review
      load, and state without a numeric quality score.
- [ ] The five named pilot claims occupy the first Review Batch; later candidates
      remain ordered but are not converted into speculative implementation
      tickets.
- [ ] Candidates missing prerequisites remain visibly deferred and cannot
      disappear from the cut.
- [ ] New rules after the cut enter the normal lifecycle without reopening the
      finite initial cohort or acquiring acceptance automatically.
