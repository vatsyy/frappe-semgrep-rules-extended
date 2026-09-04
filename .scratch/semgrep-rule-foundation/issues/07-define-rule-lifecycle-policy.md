# Define the Rule Lifecycle policy

Type: grilling
Status: resolved
Blocked by: 05, 06

## Question

Under what evidence and ownership conditions should an existing rule be
retained, narrowed, split, downgraded, replaced, contributed upstream, or
retired, and when may a new rule enter the Rule Portfolio?

## Answer

### Stewardship and ownership boundaries

Noospheric owns the Rule Portfolio. Vatsal is its accountable human steward and
final blocking approver; Noema is its operational Codex co-steward. Either may
author or independently review a rule or evidence packet, but the author cannot
approve the same work as its independent reviewer. Runtime provenance remains
explicit where technically relevant.

Frappe-maintained rules form an Upstream Mirror and remain byte-for-byte
unchanged. Every new or mutated rule is a separately identified Noospheric Rule
in a structurally separate ownership tier, even when it adapts an upstream
idea. Provenance is retained. Upstream contribution is optional and never
authorises mutation of the mirror.

### States, entry, and admission

The lifecycle is:

`candidate -> evaluating -> accepted (blocking, monitor, or audit) -> suspended -> retired`

A Rule Candidate needs a proposed Rule Claim, real source anchor, provenance,
expected claim class, likely Rule Scope, Noospheric stewardship, and an account
of its distinct value before investigation begins. Invented examples alone do
not justify candidacy. A candidate enters evaluation once its contract and
evidence packet are being assembled, and becomes accepted only after satisfying
the Rule Quality Scorecard for its assigned outcome.

None of the existing 61 rules is grandfathered. Each remains a Rule Candidate
until admitted, although current milestone scans may continue to report its
output as unaudited advisory evidence. A failed candidate remains outside the
governed Rule Portfolio and may re-enter evaluation only after new evidence or
a Material Rule Change addresses the failure.

Urgency never bypasses admission. An urgent security candidate may run
immediately as advisory audit output while evaluation is expedited; a confirmed
vulnerability is handled directly through the security process rather than by
pretending the rule has blocking precision.

### Retention and change decisions

At each evaluation or re-evaluation:

- **retain** a rule when its unchanged Rule Claim still passes every gate for
  its admitted outcome;
- **narrow** it when failures lie outside a smaller defensible Rule Scope;
- **split** it when one ID contains multiple claims, proof boundaries, or
  materially different assumptions;
- **downgrade** it when its claim remains truthful but its evidence no longer
  supports the current enforcement tier;
- **replace** it when another rule establishes the same claim more accurately,
  compatibly, or cheaply; and
- **retire** it when it lacks distinct value, evidence, compatibility,
  acceptable cost, or stewardship.

Any pattern, source, sink, sanitizer, scope, analysis-mode, or parser change
must rerun the affected evidence because it may alter matches. Pattern tuning
may retain the ID only when the Rule Claim, proof boundary, and material scope
remain unchanged. A changed claim, proof boundary, or detection meaning gets a
new ID and full admission. Pure wording, reference, or provenance corrections
need focused review but not full re-admission.

### Upstream evolution

Every Frappe update is imported into the Upstream Mirror without local
mutation. If it introduces a rule resembling a Noospheric Rule, compare their
claims and evidence rather than merging them:

- when equivalent, retain the upstream rule and retire the Noospheric duplicate
  only after local parity verification;
- when the Noospheric rule is materially stronger or different, retain both as
  distinct Rule Claims; and
- when an upstream idea is adapted or improved, keep the resulting rule in the
  Noospheric structure with its provenance and independent evidence.

### Freshness, suspension, and restoration

Re-evaluation is triggered by a Material Rule Change, a relevant Frappe or
ERPNext delta, a Corpus Refresh, Semgrep engine or parser changes, newly found
false positives or missed positives, changed policy or business intent, and an
upstream replacement. The agreed monthly and event-driven Corpus Refresh is
the freshness mechanism; only affected rules are re-evaluated. Unaffected
rules are not repeatedly audited without evidence of change.

If a blocking gate, required refresh, or stewardship condition lapses,
blocking is suspended immediately. The rule may continue only at the strongest
truthful advisory outcome supported by the remaining evidence; failure is
never silently waived. Restoration requires correcting the failure, rerunning
affected evidence, independent review, and renewed human approval. There is no
blocking grace period.

### Retirement record

Retirement stops active reporting but never rewrites history. The Rule
Portfolio Catalogue retains the ID, Rule Claim, reason, date, last evidence,
known limitations, historical findings, and predecessor or replacement links.
Retired IDs are never reused. Current state and decision links remain in the
existing catalogue rather than a new lifecycle application.
