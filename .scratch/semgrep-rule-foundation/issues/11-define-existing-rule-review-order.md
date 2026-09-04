# Define the existing-rule review order

Type: grilling
Status: resolved
Assignee: Noema
Blocked by: 10

## Question

In what risk- and evidence-led sequence, batch size, and entry and exit criteria
should the current 61 Rule Candidates receive their mandatory Portfolio Review,
while keeping Karam milestone review load bounded and producing useful admitted
outcomes early?

## Answer

### Review basis and finite cut

Vatsal normally updates the local Frappe and ERPNext applications before asking
Noema to begin. Noema assumes that refresh has occurred, does not ask for a
confirmation ceremony, and never pulls, switches, cleans, or otherwise updates
those worktrees. Noema records their exact live branches, revisions, worktree
states, and relevant source hashes read-only. A concrete freshness
contradiction is reported rather than silently repaired or described as latest.

Each review begins from the newest locally available Frappe, ERPNext, Karam
Finance, rules, and Semgrep state. `latest` selects what should be inspected; it
is not reproducible evidence. Every Evidence Packet records exact commits,
engine versions, timestamps, and, for active Karam WIP, per-file hashes. The
complete Karam worktree, including untracked v16 migration work, participates
in discovery and triage. Mutable WIP remains exploratory until its corresponding
milestone commit can supply stable admission evidence.

After the initial refresh, record a Portfolio Review Cut containing the exact
Rule Candidate inventory. Its finite cohort defines completion of this initial
migration. Rules introduced later enter the normal candidate lifecycle without
reopening completed reviews and without gaining grandfathered acceptance.
Relevant source changes may still stale and requeue affected evidence under the
existing lifecycle policy.

### Ordering model

Review priority combines current operational exposure, consequence if a claim
is wrong, and readiness of independent real evidence. Ownership tier, YAML
severity, file order, and category alone never determine priority. Upstream,
backported, and Noospheric candidates use the same ordering criteria; upstream
immutability changes available remediation rather than review obligation.

Maintain one small version-controlled Review Queue for the Portfolio Review
Cut. For each candidate it records the priority band and reason, intended
Review Batch, entry prerequisites, and review state. It does not invent a
numeric quality or priority score and does not compete with catalogue
dispositions.

After the pilot, the dynamic priority bands are:

1. new Karam or compatibility matches and Scan Health risks;
2. high-consequence security and deterministic correctness claims with usable
   real evidence;
3. broad or high-volume candidates imposing substantial reviewer cost;
4. remaining correctness and explicit-policy candidates; and
5. lower-consequence translation, UX, code-quality, and no-hit performance
   hypotheses.

Re-rank at each relevant refresh and batch boundary. A security release,
serious Scan Health regression, or confirmed high-consequence defect may
interrupt an active queue. Ordinary upstream churn waits for the next batch
boundary.

### Pilot and batch size

The first Review Batch contains five deliberately contrasting candidates:

- `override-doctype-class`;
- `frappe-sql-format-injection`;
- `frappe-whitelisted-permission-bypass`;
- `frappe-n-plus-one-read-in-loop`; and
- `frappe-async-array-callback-misuse`.

The first four had current Karam WIP matches when this route was decided; the
fifth had promising real ERPNext correctness evidence without a current Karam
match. This mixture exercises upstream and Noospheric ownership, Python and
JavaScript, active and zero-match candidates, and plausible blocking, monitor,
audit, and outside-portfolio outcomes. The implementation refreshes the live
evidence before review rather than treating these point-in-time observations as
Ground-Truth Labels.

The pilot contains five Rule Claims. Later batches contain at most eight and
shrink when evidence complexity or match volume is high. Batch size counts Rule
Claims, not YAML files, and never expands merely to satisfy a schedule.

### Entry and substitution

A candidate may enter a Review Batch only with:

- one proposed Rule Claim and a draft Rule Contract;
- exact rule, engine, and source states;
- passing native positive, negative, and tracked-gap tests;
- identified Source-Backed positive and safe near-miss candidates;
- a known parser and Rule Scope boundary;
- an estimated live match volume and reviewer load; and
- an available independent reviewer.

If one rule ID contains several claims, propose the split before batch entry.
If a selected candidate lacks an entry prerequisite, keep it visibly queued
with the gap recorded and substitute the next eligible candidate from the same
priority band. Repeated deferral never removes a candidate from the Portfolio
Review Cut.

### Exit, load, and cadence

A Review Batch is complete only when every included candidate has a Rule
Portfolio Catalogue disposition of blocking, monitor, audit, or outside
portfolio. Each decision must carry its completed Rule Contract, Evidence
Packet, compatibility and Scan Health result, reviewed current matches and
suppressions, independent review, reviewer-cost observation, and required
approval. `Still evaluating` is not an exit state; insufficient evidence
produces an explicit outside-portfolio decision that may re-enter later with
new evidence.

The pilot succeeds by producing five defensible dispositions, measuring real
reviewer cost, and validating or exposing faults in the review process. It need
not admit a Blocking Rule.

Only one Review Batch is active at a time. Once its catalogue decisions are
complete, the next batch may begin while an enforcement promotion waits for
the required Karam milestone and Frappe or ERPNext Compatibility Scan. Keep at
most one decided batch awaiting that observation. If match volume cannot be
responsibly reviewed before the next Karam milestone, stop expanding the
current batch and shrink the next one. Monitor and audit backlog does not block
the milestone, and no incompletely reviewed candidate gains blocking power.

The initial Portfolio Review is complete only when every candidate in the
Portfolio Review Cut has a final catalogue disposition and all associated
current matches and suppressions have been handled under the agreed protocol.
