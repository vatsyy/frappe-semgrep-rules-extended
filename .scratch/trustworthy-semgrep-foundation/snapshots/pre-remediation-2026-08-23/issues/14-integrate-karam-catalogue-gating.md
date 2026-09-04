# 14: Integrate catalogue-based Karam gating

**What to build:** Replace Karam Finance's severity-driven Semgrep behaviour
with the canonical committed-tree scan and the pilot's governed Enforcement
Set while preserving the application and its migration work.

**Blocked by:** 05: Gate a canonical scan safely; 06: Pin and qualify Semgrep
engines in rules CI; 13: Close the pilot Review Batch.

**Status:** ready-for-agent

- [ ] Karam CI uses the same exact Semgrep version, immutable rules revision,
      catalogue, target inventory rules, resource settings, and Gate Evaluation
      as the canonical local command.
- [ ] Every pull request receives one complete committed-application scan; diff
      information affects presentation but not analysis scope.
- [ ] Only an unexcepted admitted Blocking Rule, new or changed in-scope Scan
      Health failure, invalid execution, invalid exception, or unverifiable
      required input can fail the workflow.
- [ ] Blocking matches are actionable, Scan Health is prominent, changed monitor
      issues are grouped, audit results remain in the full report, and unchanged
      advisory results are summarised.
- [ ] Raw findings and reports remain access-controlled; public and concise CI
      output does not expose private Karam source.
- [ ] Karam business logic and unrelated tracked or untracked migration work are
      untouched.
