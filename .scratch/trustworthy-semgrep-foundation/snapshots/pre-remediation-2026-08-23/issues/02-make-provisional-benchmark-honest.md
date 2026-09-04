# 02: Make the provisional benchmark honest

**What to build:** Preserve the useful Semgrep compatibility and performance
runner while ensuring none of its authored fixtures is presented or consumed as
independent acceptance evidence.

**Blocked by:** 01: Govern a reference Rule Candidate end to end.

**Status:** ready-for-agent

- [ ] The runner continues to detect missing, forbidden, and unexpected matches,
      parser errors, engine incompatibility, timeouts, scan cost, per-rule cost,
      and memory regressions.
- [ ] Its outputs and manifest no longer imply measured Rule Confidence,
      precision, recall, or blocking reliability.
- [ ] The eleven source-backed-replacement cases, three unresolved boundaries,
      and three unsupported security assertions retain their audited
      dispositions without being silently admitted.
- [ ] Pattern-mirroring fixtures are clearly separated from Ground-Truth Cases
      and may serve only native syntax or compatibility purposes.
- [ ] Source-backed replacements enter the corpus only through the governance
      workflow, required review, and immutable provenance.
- [ ] Repository acceptance proves the benchmark cannot act as a second
      scorecard or competing evidence system.
