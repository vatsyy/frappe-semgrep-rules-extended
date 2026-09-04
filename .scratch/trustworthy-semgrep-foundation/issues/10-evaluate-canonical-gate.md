# 10: Evaluate the canonical gate

**What to build:** Turn one structured portfolio scan into a deterministic
workflow result using only the immutable Enforcement Set, Scan Health and
verified inputs; exception and rollback mechanics remain later slices.

**Blocked by:** 03: Enforce append-only history and schema migrations; 07:
Inventory Analysis Targets and Scan Health.

**Status:** proposed — independent wave review and renewed Vatsal approval required.

- [ ] Gate Evaluation consumes exact provenance, catalogue, Enforcement Set,
      Coverage Baseline, target inventory and structured scan output.
- [ ] Enforcement Set validation rejects any blocking entry whose decided packet
      lacks a complete, current and verifiable Baseline Triage census of every
      match and suppression.
- [ ] It fails only for unverifiable inputs, invalid or incomplete execution,
      new or changed in-scope coverage failure, unexcepted Blocking Rule match,
      invalid required policy input, or missing required output.
- [ ] Monitor, audit, unaudited, advisory-lane, severity-only and unchanged
      inherited coverage results never independently fail.
- [ ] Finding and Scan Health status remain separate in structured and human output.
- [ ] Blocking annotations are concise; advisory detail remains in the full report.
- [ ] Boundary tests exercise every authorised failure and prove Semgrep
      `--error` and severity do not control the workflow exit status.
