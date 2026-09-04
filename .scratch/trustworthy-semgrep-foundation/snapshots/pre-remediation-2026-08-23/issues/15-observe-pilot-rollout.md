# 15: Observe the pilot rollout on real scans

**What to build:** Exercise the pilot through one real Karam milestone and one
fresh Frappe or ERPNext Compatibility Scan, then promote, suspend, or correct
its Enforcement Set from observed evidence.

**Blocked by:** 03: Produce a complete Compatibility Scan; 14: Integrate
catalogue-based Karam gating.

**Status:** ready-for-agent

- [ ] A real Karam milestone records the canonical full local scan and the
      independent committed-tree CI result with exact provenance.
- [ ] A fresh stable Frappe or ERPNext Compatibility Scan records findings,
      coverage, performance, and affected corpus evidence read-only.
- [ ] False positives, unresolved blocking cases, reviewer cost, and unexplained
      Scan Health regressions are explicitly assessed.
- [ ] A harmful or stale blocker restores the last known-good Enforcement Set
      and continues advisory until corrected and re-approved.
- [ ] Successful blockers retain Vatsal approval and an immutable observation
      record; monitor and audit outcomes remain non-blocking.
- [ ] The Corpus Refresh reuses unchanged cases, revalidates changed cases, and
      preserves historical evidence.
