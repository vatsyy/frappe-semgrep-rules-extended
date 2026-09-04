# 12: Prove Enforcement Set rollback and suspension

**What to build:** Make a harmful blocker independently reversible while its
history and advisory signal remain visible and application source stays untouched.

**Blocked by:** 10: Evaluate the canonical gate.

**Status:** proposed — independent wave review and renewed Vatsal approval required.

- [ ] The last-known-good Enforcement Set has an immutable identity and a tested
      selection path independent of rule deletion or application rollback.
- [ ] Selecting it changes Gate Evaluation while preserving complete findings,
      Scan Health, advisory reporting and decision history.
- [ ] Loss of a blocking gate, affected refresh or steward action appends an
      immediate suspension and strongest truthful advisory outcome.
- [ ] Restoration requires corrected evidence, affected reruns, independent
      review and renewed Vatsal approval.
- [ ] Standard and schema impact manifests suspend only affected blockers.
- [ ] Tests exercise promotion, harmful-blocker rollback, suspension and
      restoration without modifying application code or the Upstream Mirror.
