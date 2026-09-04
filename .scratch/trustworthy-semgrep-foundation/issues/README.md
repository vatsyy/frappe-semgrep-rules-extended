# Corrected first implementation wave

Status: **approved by Vatsal on 2026-08-25** after the corrected wave and
canonical [specification](../../semgrep-rule-foundation/spec.md) received a
fresh independent read-only review. Tickets 01, 05 and 06 are complete; Tickets
02, 04 and 07 are now the active frontier, and every other ticket remains
dependency-gated.

The reviewed 16-ticket predecessor is preserved only as a
[non-canonical snapshot](../snapshots/pre-remediation-2026-08-23/README.md).
The readiness findings are in the
[second-pass audit](../audits/second-pass-readiness-review-2026-08-23.md).

## Active verified frontier

The genuine initial frontier is `{01, 04, 05}`:

- 01 establishes the smallest governance contract seam;
- 04 can correct the independent benchmark boundary without governance code; and
- 05 can pin the already-tested current engine without waiting for pilot evidence.

The principal graph is:

`01 → 02 → 03`

`{01,05} → 06 → 07 → {08,09}`

`{03,07} → 10 → {11,12}`

`{03,07,09} → 13 → 14 → 15 → {16→17,18→19,20→21,22→23} → 24`

`{04,05,07,09,24} → 25`

`{10,11,12,24,25,Vatsal milestone authorisation} → 26 → 27 → 28`, with
Ticket 27 also blocked by Ticket 08.

## Operational rules

- Preparation and independent decision are different tickets and different
  actors. One task cannot complete both for the same packet.
- Where second review is required, its reviewer is distinct from both the
  packet author and first reviewer; the decision ticket coordinates rather than
  impersonates those human judgements.
- Ticket 13 may substitute any provisional pilot candidate that fails entry.
  The activated identity must be recorded before its preparation ticket starts.
- Karam stays read-only through Ticket 25. Ticket 26 cannot start without a
  separately named file and milestone authorisation from Vatsal.
- No mutable Registry alias can enter Gate Evaluation. Auxiliary Karam inputs
  remain advisory until separately imported and immutably governed.
- A ticket may stop at an external human or milestone gate without weakening its
  acceptance criteria; it must not fabricate review or approval.
- Sampling may measure non-blocking outcomes, but blocking and Enforcement Set
  membership require a complete, mechanically validated Baseline Triage census
  of every current match and suppression. If that census cannot fit, defer,
  substitute or retain a non-blocking ceiling.

## Requirement ownership

| Material specification requirements | Owning tickets | Coverage |
|---|---:|---|
| I1 delivery sequence; T20 release boundary | 01–28 | covered |
| I2; T1–T4 repository acceptance and native tests | 01–05, 28 | covered |
| I3–I5; T8 canonical single scan and outputs | 06–10 | covered |
| I6–I12 catalogue, contracts, proof ceiling and mirror | 01, 03, 14–24, 28 | covered |
| I13–I18; T5 corpus, blindness, clusters and holdouts | 02, 13–24 | covered |
| I19–I20; T14, T17 Karam evidence, privacy and refresh | 02, 09, 13–24, 27 | covered |
| I21–I27; T6–T7, T18 scorecard and measurements | 01–02, 13–24 | covered |
| I28; T16 provisional benchmark boundary | 04, 25 | covered |
| I29–I31; T10–T11 target and parser coverage | 07–09 | covered |
| I32–I36 lifecycle, migrations, suspension and approval | 01–03, 11–12, 14–24 | covered |
| I37–I44 review cut, substitution and pilot | 13–24 | covered |
| I45; T19 approved Karam input and rollout contract | 09, 26–27 | covered |
| I46 weekly Compatibility Scan ownership | 08, 27–28 | covered |
| I47; T15 engine pin and post-pilot qualification | 05, 25–26 | covered |
| I48–I49; T9 gate failures and presentation | 10–12, 26 | covered |
| I50 Baseline Triage | 01–02, 10, 13–24 | covered: full census enforced for blocking; samples are non-blocking only |
| I51–I53; T12–T13 exceptions, override and rollback | 11–12, 27–28 | covered |
| I54 privacy | 02, 09, 14–28 | covered |
| I55 initial Review Cut completion | 24, 27–28 | covered |
| Schema migration and standard-change impact | 03, 12, 24 | covered |
| Holdout reveal and replenishment | 02, 15, 17, 19, 21, 23–24 | covered |
| Independent review and Vatsal approval hand-offs | 13–24, 26 | covered |
| Immutable pre-merge rule-tree identity | 06, 09, 25–28 | covered |

Any independent-review finding that changes this matrix must be corrected in the
specification and owning tickets before the wave can be approved.

## Measured post-Batch-01 review wave

Batch 01 was approved on 2026-08-26. The exact remaining cut contains 51 rules,
3,639 findings and 25 suppressions; the pilot and Batch 01 supplied 153 blind
cases across ten rules. Reviewer minutes were not captured, so the next batch
must measure them instead of inventing an elapsed-time estimate.

The canonical selection is
[`remaining-portfolio-plan-v1.json`](../../../governance/review-cuts/remaining-portfolio-plan-v1.json).
Only the next bounded host-boundary batch is ticketed:

`29 → 30`

It reviews `frappe-security-file-traversal` and `frappe-subprocess-exec` through
one complete source-evidence, rule-change, blind-review, adjudication and
verification slice. The later 49 rules deliberately have no batch placeholders;
Ticket 30 ends by recalibrating their queue from measured Batch 02 cost.
