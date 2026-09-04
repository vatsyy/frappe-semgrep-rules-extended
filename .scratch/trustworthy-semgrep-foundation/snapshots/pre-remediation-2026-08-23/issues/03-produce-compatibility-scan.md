# 03: Produce a complete Compatibility Scan

**What to build:** Give Noospheric one canonical read-only command that scans a
stable Frappe or ERPNext snapshot once and returns reproducible findings,
Analysis Target coverage, Scan Health, provenance, and a concise summary without
gating the upstream product.

**Blocked by:** 01: Govern a reference Rule Candidate end to end.

**Status:** ready-for-agent

- [ ] The command uses an exact Semgrep version, immutable rules revision,
      catalogue, exclusions, resource settings, and recorded source snapshot.
- [ ] Every eligible Analysis Target is classified as fully analysed, partially
      analysed, unanalysed, or intentionally excluded independently of Semgrep's
      scanned-path count.
- [ ] Parser failures, skipped targets, unsupported constructs, timeouts, and
      incomplete execution appear as Scan Health rather than findings or clean
      negatives.
- [ ] A ratcheting Coverage Baseline distinguishes inherited gaps from new,
      changed, and resolved gaps.
- [ ] Mixed-template JavaScript and native-valid compatibility gaps receive the
      agreed explicit coverage treatment; generic mode cannot satisfy blocking
      native-parser scope.
- [ ] The command emits stable structured findings, provenance, Scan Health, and
      human-readable summary outputs while leaving Frappe and ERPNext unchanged.
- [ ] Integration tests exercise the complete command boundary rather than its
      internal helpers.
