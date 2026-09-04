# 05: Gate a canonical scan safely

**What to build:** Extend the canonical scan from advisory reporting to a
deterministic, reversible workflow gate that responds only to the immutable
Enforcement Set, Scan Health, and valid human authorisations.

**Blocked by:** 01: Govern a reference Rule Candidate end to end; 03: Produce a
complete Compatibility Scan.

**Status:** ready-for-agent

- [ ] Gate Evaluation consumes one structured portfolio scan together with the
      exact catalogue, Enforcement Set, Coverage Baseline, target inventory, and
      Rule Exceptions.
- [ ] It fails only for unverifiable inputs or provenance, invalid or incomplete
      execution, a new or changed in-scope coverage failure, an unexcepted
      Accepted Blocking Rule match, an invalid exception, or missing required
      outputs.
- [ ] Monitor, audit, unaudited, severity-only, and unchanged inherited coverage
      results never independently fail the workflow.
- [ ] Rule Exceptions are exact-source, rule-specific, evidence-backed,
      Vatsal-approved, expiring, and invalidated by relevant source, rule,
      corpus, or milestone changes.
- [ ] Emergency Workflow Overrides are Vatsal-approved, single-PR, expire after
      merge, and remain distinct from Rule Exceptions and `nosemgrep`.
- [ ] Restoring the last known-good Enforcement Set changes gate behaviour while
      preserving rule history, Scan Health, advisory reporting, and application
      source.
- [ ] Tests cover every authorised failure, exception, override, expiry, and
      rollback path at the canonical command boundary.
