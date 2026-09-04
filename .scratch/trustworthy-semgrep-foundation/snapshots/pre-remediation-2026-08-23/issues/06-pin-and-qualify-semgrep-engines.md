# 06: Pin and qualify Semgrep engines in rules CI

**What to build:** Make repository CI reproduce local acceptance with an exact
Semgrep Community Edition version while exercising one proposed candidate
engine before any upgrade is adopted.

**Blocked by:** 02: Make the provisional benchmark honest; 03: Produce a
complete Compatibility Scan; 05: Gate a canonical scan safely.

**Status:** ready-for-agent

- [ ] Rules CI installs an exact pinned Semgrep version and never consumes a
      mutable engine label.
- [ ] The aggregate repository acceptance command remains the single required
      rules check and covers governance, native tests, compatibility regression,
      and the immutable Upstream Mirror.
- [ ] One proposed candidate engine runs native tests, canonical compatibility,
      parser coverage, performance guards, and affected acceptance evidence.
- [ ] Candidate drift is reported without changing the pinned production engine
      or silently rewriting evidence.
- [ ] An engine upgrade requires all affected checks and evidence to pass and is
      recorded with exact provenance.
- [ ] CI outputs are deterministic enough to distinguish implementation failure,
      engine drift, and Analysis Coverage Failure.
