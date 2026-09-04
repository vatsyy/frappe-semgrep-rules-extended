# 02: Validate evidence, holdout and review states

**What to build:** Add versioned Ground-Truth Case and Evidence Packet contracts
that make provenance, blindness, clustering, sampling, holdout integrity,
privacy and actor separation mechanically visible.

**Blocked by:** 01: Validate catalogue and Rule Contract foundations.

**Status:** ready — Ticket 01 completed on 2026-08-25.

- [ ] Case, cluster, reduction, sample, holdout, Evidence Packet and review-event
      schemas validate immutable source, rule, engine and corpus identities.
- [ ] Packet transitions enforce `authored`, `blind-labelled`, `second-reviewed`,
      `adjudicated`, `approved` and `decided` with named compatible actors.
- [ ] Holdout validation covers population hashes, sealed allocation commitments,
      freeze-before-reveal, appended seeds and labels, and replenishment or an
      explicit blocking-ineligible deficit.
- [ ] Original labels and disagreements remain immutable when adjudication adds
      a later decision.
- [ ] Reduction parents, discovery channels, denominators, inclusion
      probabilities, uncertainty and unsupported-metric refusal are tested.
- [ ] Evidence Packets distinguish sampled measurement frames from the complete
      current-match and suppression inventory, record census completeness, and
      make an incomplete census mechanically blocking-ineligible.
- [ ] Public fixtures contain no private Karam source; invented cases remain
      validator tests and cannot satisfy universal admission.
