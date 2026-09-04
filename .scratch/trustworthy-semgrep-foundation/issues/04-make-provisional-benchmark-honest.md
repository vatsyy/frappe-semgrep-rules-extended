# 04: Make the provisional benchmark honest

**What to build:** Preserve the useful Semgrep compatibility and performance
runner while ensuring none of its authored fixtures is presented or consumed as
independent acceptance evidence.

**Blocked by:** None after corrected-wave approval.

**Status:** ready — approved by Vatsal on 2026-08-25.

- [ ] The runner still detects missing, forbidden and unexpected matches, parser
      errors, engine incompatibility, timeouts, scan cost, per-rule cost and
      memory regressions.
- [ ] Outputs and the manifest cannot imply Rule Confidence, precision, recall,
      blocking reliability or scorecard admission.
- [ ] The eleven replacement-needed cases, three unresolved boundaries and
      three unsupported assertions retain their audited dispositions.
- [ ] Pattern-mirroring fixtures are explicitly separated from Ground-Truth
      Cases and remain native syntax or compatibility tests only.
- [ ] Source-backed replacements can enter the corpus only through immutable
      provenance, blind review and the governance workflow.
- [ ] `make test` proves the runner cannot become a competing evidence system.
