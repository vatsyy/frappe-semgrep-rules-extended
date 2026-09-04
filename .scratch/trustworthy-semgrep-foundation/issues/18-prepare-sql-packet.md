# 18: Prepare pilot slot C — provisional SQL-format rule

**What to build:** Freeze an `authored` packet for the slot selected by Ticket
13, provisionally `frappe-sql-format-injection`, using a bounded cluster and
sampling plan rather than making one context inspect every raw match.

**Blocked by:** 13: Record the Review Cut and activate bounded pilot slots; 15:
Independently decide pilot slot A.

**Status:** resolved — bounded sample and authored non-blocking packet are frozen for Ticket 19.

- [ ] Ticket 13's selected identity is recorded; an unbounded review population
      causes visible deferral and substitution before this ticket starts.
- [ ] The draft claim distinguishes formatted SQL structure from attacker
      control, exploitability and allowlisted structural interpolation.
- [ ] Public positives, parameterised queries, static values, closed branches,
      safe near-misses, matches and suppressions are clustered with immutable provenance.
- [ ] Census or seeded sampling follows the declared cluster protocol with
      inclusion probabilities, denominators and a review plan that fits the slot.
- [ ] The packet separately records the complete current-match and suppression
      inventory and its triage completeness. Sampling can support only a
      non-blocking result unless every inventory item is triaged.
- [ ] Structural and same-function taint alternatives remain hypotheses within
      Semgrep CE's proof boundary; no detector mutation or outcome is preselected.
- [ ] Native tests, parser scope, compatibility, limitations, cost and a reviewer-
      supplied sealed allocation finish in a frozen `authored` packet only.
