# 26: Integrate authorised catalogue-based Karam gating

**What to build:** At a separately named and Vatsal-authorised milestone, update
the intended private `quality.yml` workflow to use canonical committed-tree Gate
Evaluation while preserving Karam business code, migration WIP and auxiliary
advisory inputs.

**Blocked by:** 10: Evaluate the canonical gate; 11: Validate Rule Exceptions and
emergency overrides; 12: Prove Enforcement Set rollback and suspension; 24:
Close the pilot Review Batch; 25: Qualify post-pilot engine transitions; and
explicit Vatsal authorisation of the target file and milestone.

**Status:** proposed — Karam remains read-only until the external authorisation
gate.

- [ ] The authorised workflow uses the qualified exact engine, complete immutable
      rules identity, catalogue, target rules, resources and Gate Evaluation.
- [ ] The governed catalogue is the sole blocking source; the Karam-local rule
      and Registry pack remain visibly separate advisory lanes.
- [ ] No mutable Registry alias, Semgrep severity or `--error` participates in
      the required workflow exit status.
- [ ] Every pull request receives one complete committed-tree scan; diff data
      affects presentation only.
- [ ] Blocking findings are actionable, Scan Health prominent and advisory
      output privacy-preserving with full reports access-controlled.
- [ ] Only the authorised workflow integration is changed; Karam business logic
      and unrelated tracked or untracked migration work remain untouched.
