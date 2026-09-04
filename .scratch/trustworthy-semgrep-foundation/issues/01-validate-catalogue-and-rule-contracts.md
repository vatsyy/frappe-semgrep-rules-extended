# 01: Validate catalogue and Rule Contract foundations

**What to build:** Add the smallest versioned governance seam that can represent
one Rule Claim, its Rule Contract, ownership, provenance, lifecycle and current
catalogue state without pretending that test fixtures are admission evidence.

**Blocked by:** None after corrected-wave approval.

**Status:** completed on 2026-08-25 — `make test` passed with 61 valid rules,
18 governance tests and an unchanged 24-file Frappe Upstream Mirror.

- [x] Versioned catalogue, Rule Contract, lifecycle and current-state schemas
      have one documented canonical location and stable identities.
- [x] `make test` validates required claims, classes, Enforcement Ceilings, Rule
      Scope, assumptions, messages, ownership, provenance and references.
- [x] Duplicate identities, contradictory current state, incomplete contracts,
      retired-ID reuse and competing sources of truth fail with actionable errors.
- [x] Table-driven fixtures prove blocking, monitor, audit and outside-portfolio
      gates are non-compensating and reject unsupported measurements.
- [x] Blocking validation requires a complete current-match and suppression
      census with every item triaged; sampled or incomplete packets cannot enter
      an Enforcement Set regardless of other evidence or approval.
- [x] Invented source is labelled validation-only and cannot create an Accepted
      Rule or measured Rule Confidence.
- [x] Existing ownership checks and the byte-identical Frappe Upstream Mirror
      remain part of the aggregate acceptance seam.
- [x] Urgent candidates may enter only as explicit unaudited advisory output;
      no urgency field or severity can bypass admission.
- [x] Upstream parity may retire a redundant Noospheric adaptation only through
      an appended replacement/retirement event that preserves both identities.
- [x] No generated view is required without a named consumer; any introduced
      view is deterministic, disposable and reproducible from canonical files.
