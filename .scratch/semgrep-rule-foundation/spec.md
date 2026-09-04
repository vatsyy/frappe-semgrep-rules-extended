# Implement a trustworthy Semgrep rule foundation

Type: spec
Status: draft
Label: independent-review-required
Source: [Establish a trustworthy Semgrep rule foundation](map.md)

Revision: readiness remediation approved by Vatsal on 2026-08-23. This
specification and its implementation wave must receive a fresh independent
read-only review and renewed Vatsal approval before implementation begins.

## Problem Statement

The current Semgrep repository can validate rule syntax and authored fixtures,
but it cannot yet demonstrate that its 61 rules make truthful claims, provide
useful coverage, avoid unacceptable reviewer burden, or deserve their present
CI consequences. The provisional benchmark mirrors authored patterns rather
than independent semantic truth, none of its 17 cases qualifies unchanged for
acceptance evidence, parser failures are not modelled as first-class scan
health, and rules CI installs an unpinned engine. Karam Finance's committed HEAD
and private replacement-CI WIP describe different Semgrep inputs and failure
behaviour: the committed workflow uses mutable upstream and Registry inputs,
while the replacement pins part of the toolchain but still includes a mutable
Registry alias and an app-local rule outside the governed catalogue.

Vatsal needs a strong, reproducible foundation before expanding the portfolio.
Every upstream, backported, and Noospheric rule must be reviewed against real
Frappe, ERPNext, and Karam evidence without mutating the Frappe Upstream Mirror
or disturbing active Karam migration work. Matches must communicate only what
Semgrep Community Edition established, and only independently admitted Blocking
Rules and genuine Scan Health failures may stop a Karam milestone.

## Solution

Build a lightweight, version-controlled Rule Quality Standard around the
existing repository. A canonical Rule Portfolio Catalogue will hold one Rule
Contract and decision history per Rule Claim. An independent Ground-Truth
Corpus will retain reproducible, source-backed evidence and explicit coverage
gaps. A non-compensating Rule Quality Scorecard will admit each candidate as
blocking, monitor, audit, or outside the portfolio.

Preserve `make test` as the repository acceptance seam and add one canonical
application-scan command as the local and CI scan seam. The scan command will
run the complete portfolio once, inventory Analysis Targets, report Scan Health
separately, and perform deterministic Gate Evaluation from the immutable
Enforcement Set and valid exceptions. The existing benchmark runner remains a
syntax, compatibility, and performance-regression tool rather than ground
truth.

Create a finite Portfolio Review Cut from the latest locally available sources,
then validate the system through a five-claim pilot. Continue through bounded,
risk- and evidence-led Review Batches until every candidate in the cut has an
evidence-backed catalogue disposition. Rule-specific narrowing, splitting,
taint conversion, downgrading, replacement, or retirement will follow evidence
rather than being predetermined by this specification.

Use the approved Karam input contract: the governed rules-repository catalogue
is the sole blocking source; the Karam-local rule and Registry pack remain
separate advisory inputs until explicitly imported and immutably governed; no
mutable Registry alias participates in gating. Treat the private untracked
`quality.yml` as the intended future integration target, but do not change it
until Vatsal authorises the named integration milestone. Pin rules-repository CI
to Semgrep CE 1.174.0. Keep Karam on 1.172.0 until a post-pilot qualification
proves that a candidate engine preserves real acceptance and scan evidence.

## User Stories

1. As Vatsal, I want every current rule reviewed before acceptance, so that no
   rule receives trust merely because it already exists.
2. As Vatsal, I want the initial review to have a finite recorded cohort, so
   that an evolving upstream portfolio does not make completion impossible.
3. As Vatsal, I want Noema to assume my local Frappe and ERPNext apps are
   already updated, so that each review begins without a confirmation ceremony.
4. As Vatsal, I want Noema to record exact live revisions without updating my
   worktrees, so that evidence is reproducible and my repository state remains
   under my control.
5. As a Karam maintainer, I want the complete working tree scanned before each
   milestone pull request, so that untracked v16 migration work is not omitted.
6. As a Karam maintainer, I want committed CI to scan the pull-request tree
   independently, so that a local success assertion is never blindly trusted.
7. As a Karam maintainer, I want monitor and audit findings to remain visible
   without failing the milestone, so that investigation does not masquerade as
   blocking certainty.
8. As a Karam maintainer, I want a harmful blocker rolled back independently of
   application code, so that rule failure does not force an application revert.
9. As a rule author, I want one bounded Rule Claim per rule identity, so that a
   match never implies more than the engine established.
10. As a rule author, I want every claim to declare its proof assumptions and
    Rule Scope, so that unsupported framework or business assumptions are
    visible.
11. As a rule author, I want Rule Messages to distinguish observations, claims,
    non-claims, and next actions, so that developers receive truthful guidance.
12. As a rule author, I want native positive, negative, and tracked-gap tests,
    so that pattern behaviour remains stable without being confused with real
    precision evidence.
13. As a rule author, I want source-backed positive and safe near-miss cases, so
    that acceptance depends on real framework behaviour rather than invented
    DocTypes.
14. As a rule author, I want material claim or scope changes to trigger
    re-admission, so that historical evidence is not silently reused for a new
    detector.
15. As a rule author, I want wording-only corrections to receive focused review,
    so that harmless documentation maintenance does not force needless full
    re-admission.
16. As an independent reviewer, I want ground-truth labels hidden from rule
    output during initial review, so that the detector does not define its own
    oracle.
17. As an independent reviewer, I want disagreements and unresolved cases
    preserved explicitly, so that ambiguity is not forced into a false positive
    or negative.
18. As an independent reviewer, I want related cases kept in one Case Cluster,
    so that reductions of the same semantic issue cannot leak across
    development and holdout sets.
19. As an independent reviewer, I want blocking evidence double-reviewed, so
    that one author's judgement cannot independently approve its own rule.
20. As an independent reviewer, I want sampling frames, denominators, and
    uncertainty reported, so that precision and recall claims remain
    statistically honest.
21. As an independent reviewer, I want reviewer minutes and unique semantic
    issues measured, so that operational cost is considered alongside detection
    quality.
22. As a security reviewer, I want structural hotspots separated from proven
    source-to-sink violations, so that dangerous operations are not labelled as
    confirmed vulnerabilities without evidence.
23. As a security reviewer, I want urgent candidates to run advisory while
    evidence is assembled, so that urgency does not bypass admission.
24. As a security reviewer, I want Rule Exceptions to be narrow, owned, approved,
    and expiring, so that suppressions cannot become permanent hidden policy.
25. As Vatsal, I want sole approval of Emergency Workflow Overrides, so that a
    critical exception remains explicit, single-use, and accountable.
26. As a performance reviewer, I want static loop matches treated as Performance
    Hypotheses, so that query or request fan-out is not called a regression
    without runtime evidence.
27. As a performance reviewer, I want runtime and reviewer-cost baselines before
    setting new budgets, so that thresholds reflect the real portfolio rather
    than arbitrary percentages.
28. As a portfolio steward, I want one authoritative catalogue entry per Rule
    Claim, so that YAML metadata, reports, and CI cannot become competing truth.
29. As a portfolio steward, I want explicit schema versions and reviewed
    migrations, so that old decisions cannot be silently reinterpreted.
30. As a portfolio steward, I want append-only decision history, so that
    admissions, suspensions, replacements, exceptions, and retirements remain
    auditable.
31. As a portfolio steward, I want retired identities preserved and never
    reused, so that historical findings keep their meaning.
32. As a portfolio steward, I want generated views reproducible from canonical
    files, so that disposable reports do not become hidden sources of truth.
33. As a portfolio steward, I want every governed change reviewed atomically,
    so that rules, contracts, tests, evidence, catalogue outcomes, and
    compatibility impact cannot drift apart.
34. As a portfolio steward, I want affected rules re-admitted after a standard
    change, so that unaffected rules are not ceremonially re-reviewed.
35. As a Frappe maintainer, I want the Upstream Mirror preserved byte-for-byte,
    so that local governance never mutates Frappe-owned rule material.
36. As a Noospheric rule author, I want adaptations stored as separately owned
    rules with provenance, so that upstream ideas can be improved without
    obscuring ownership.
37. As a scan operator, I want one canonical scan command locally and in CI, so
    that engine versions, rules, targets, exclusions, and gate logic cannot
    drift between environments.
38. As a scan operator, I want every eligible Analysis Target independently
    inventoried, so that Semgrep's reported-path count is not mistaken for full
    coverage.
39. As a scan operator, I want partial parses and unsupported constructs reported
    as Analysis Coverage Failures, so that unanalysed code is never called clean.
40. As a scan operator, I want inherited coverage gaps baselined but visible, so
    that unrelated work is not blocked while coverage can only improve.
41. As a scan operator, I want new or changed in-scope coverage failures to fail
    Scan Health, so that analysis regressions cannot pass unnoticed.
42. As a scan operator, I want mixed-template JavaScript excluded from blocking
    native-JavaScript claims until validated transformation exists, so that
    generic matching cannot impersonate AST analysis.
43. As a release engineer, I want exact engine and rule revisions in every scan
    record, so that a result can be reproduced after tools evolve.
44. As a release engineer, I want rules CI to test the pinned engine and one
    candidate engine, so that upgrades are deliberate rather than accidental.
45. As a release engineer, I want Gate Evaluation independent of Semgrep
    severity and `--error`, so that only governed blockers and Scan Health can
    fail a required workflow.
46. As a pull-request reviewer, I want blocking matches annotated inline while
    audit details stay in the full report, so that the review surface remains
    actionable.
47. As a pull-request reviewer, I want unchanged advisory findings summarised as
    counts and trends, so that repeated noise does not hide new concerns.
48. As a privacy steward, I want raw Karam source and findings retained only in
    access-controlled evidence, so that public governance files reveal no
    private implementation details.
49. As a privacy steward, I want public evidence to use opaque IDs and immutable
    provenance links, so that decisions remain auditable without copying Karam
    source.
50. As Noema, I want a bounded Review Queue and explicit batch entry and exit
    gates, so that the 61-rule migration progresses without hidden deferrals.
51. As Noema, I want the five-rule pilot to exercise contrasting claim types and
    outcomes, so that the process is validated before larger batches begin.
52. As Noema, I want pilot success measured by defensible dispositions and
    reviewer cost rather than blocker count, so that evidence is never tuned to
    manufacture enforcement.
53. As Noema, I want later Review Batches capped and dynamically reprioritised,
    so that source changes and reviewer load can alter order without losing
    candidates.
54. As Noema, I want candidates missing prerequisites visibly deferred and
    replaced within their priority band, so that one incomplete packet does not
    stall the portfolio or disappear.
55. As Noospheric, I want every candidate in the Portfolio Review Cut to end as
    blocking, monitor, audit, or outside portfolio, so that the migration has a
    measurable completion condition.

## Implementation Decisions

1. **Delivery sequence**: implement bounded governance validators, append-only
   migrations, the honest benchmark boundary, the current-engine pin, and the
   canonical scan slices first. Record the Portfolio Review Cut and provisional
   pilot queue second. Exercise the complete path with one real public,
   source-backed pilot candidate, then prepare and independently decide the
   remaining pilot slots. Qualify a candidate engine only after real pilot
   Evidence Packets exist. Integrate and observe Karam last, then continue
   bounded Review Batches until the cut is complete.
2. **Repository acceptance seam**: retain `make test` as the highest repository
   acceptance command. Extend it to validate catalogue and evidence schemas,
   ownership, Rule Contracts, schema migrations, decision history, case-ledger
   integrity, cross-reference integrity, deterministic generated artefacts, the
   immutable Upstream Mirror, Semgrep configuration, and native rule tests.
3. **Canonical scan seam**: provide one application-scan command used by local
   Milestone Scans, application CI, and Compatibility Scans. It accepts or
   resolves an exact engine, immutable rule revision, catalogue, Enforcement
   Set, Analysis Target inventory, Coverage Baseline, exclusions, resource
   settings, and valid Rule Exceptions. A pre-merge rule tree is identified by
   an immutable pull-request commit SHA or a content hash covering every rule
   input; a mutable branch, alias, or partial repository pin is insufficient.
4. **Single engine execution**: the canonical command runs the complete Rule
   Portfolio once and consumes structured Semgrep output. A deterministic Gate
   Evaluation produces the workflow exit status; individual rule severity and
   Semgrep `--error` do not govern failure.
5. **Scan outputs**: every required scan produces a provenance record, complete
   structured findings, separate Scan Health, Gate Evaluation, and a concise
   human summary. Findings and Analysis Coverage Failures are never merged into
   one status.
6. **Catalogue authority**: the Rule Portfolio Catalogue is a lightweight,
   version-controlled, explicitly schema-versioned source with one current row
   per Rule Claim. Rule YAML, CI, reports, dashboards, and generated views are
   consumers.
7. **Catalogue content**: each row records stable identity, ownership,
   provenance, complete Rule Contract, lifecycle state, admitted outcome,
   Enforcement Ceiling, exact evidence counts where valid, parser coverage,
   engine and corpus versions, reviewer cost, decision date, and links to tests,
   evidence, predecessors, and replacements. Every canonical schema declares a
   version. A reviewed migration names its source and target versions, validates
   both representations, emits a deterministic result, records affected
   identities, and never silently reinterprets old data.
8. **Decision history**: admissions, re-admissions, suspensions, exceptions,
   replacements, standard-change impacts, holdout events, and retirements are
   append-only. Corrections supersede earlier entries rather than rewriting
   them. Repository acceptance verifies the trusted journal chain and rejects
   deletion, mutation, reordering, or reuse of a retired ID.
9. **Rule Claim model**: each rule identity establishes one Rule Claim belonging
   to Deterministic Defect, Proven Security Violation, Explicit Policy
   Violation, Review Hotspot, or Performance Hypothesis. Multiple patterns may
   share an identity only when claim, assumptions, and Enforcement Ceiling are
   identical.
10. **Rule Contract**: every candidate declares identity, ownership, bounded
    claim, class, Enforcement Ceiling, Rule Scope, assumptions, measured Rule
    Confidence, observed construct, remediation or next evidence, limitations,
    provenance, and references. Its Rule Message includes important non-claims.
11. **Proof ceiling**: Semgrep Community Edition may support parsed local
    structural and same-function taint claims, subject to the rule model. It may
    not be used alone to prove framework intent, permissions, async dependence,
    query cardinality, exploitability, or cross-function or cross-file flow.
12. **Upstream boundary**: Frappe-owned rules remain a byte-identical Upstream
    Mirror. Every local mutation or adaptation becomes a separately identified
    Noospheric Rule with provenance. Upstream contribution is optional.
13. **Ground-Truth Corpus**: store independently labelled Ground-Truth Cases
    against immutable Corpus Snapshots. Each case records the versioned claim,
    exact source provenance and hash, product, module, language, file kind,
    parser state, discovery channel, rationale, reviewers, timestamps,
    confidentiality class, and cluster or reduction lineage.
14. **Evidence channels**: corpus discovery combines a census of Engine Matches,
    rule-independent missed-positive discovery, real safe near-misses, and known
    defects supported by fixes, tests, reviews, or runtime evidence. Rule output
    may locate a case but never supplies its label.
15. **Labels and blindness**: use `claim-present`, `claim-absent`, `policy-only`,
    and `unresolved`. Initial reviewers see the Rule Claim and necessary source
    context but not rule output, rule metadata, or another reviewer's label.
    The author cannot act as that packet's independent labeller or reviewer.
16. **Clusters, samples, and holdouts**: sample by Case Cluster and stratify by
    product, claim, language, parser state, and Karam refactor status. Census
    rare, high-risk, and blocking populations. For other populations, census up
    to 100 independent clusters or use 100 seeded random clusters with inclusion
    probabilities and design-aware 95% uncertainty. An independent reviewer
    splits eligible source-backed clusters 70/30 into Development Cases and a
    sealed Acceptance Holdout. Before reveal, the public packet records the
    population hash, protocol version, allocation commitment, reviewer, and an
    access-controlled evidence reference—not the allocation seed or labels.
    After the rule and Development-Case decision freeze, reveal appends the seed,
    allocation manifest, labels, timestamp, and result without rewriting the
    commitment. A revealed holdout cluster becomes historical Development
    evidence and is replaced from the unrevealed eligible pool using a new
    commitment. If no replacement exists, the claim records a holdout deficit
    and cannot newly qualify for blocking.
17. **Independent review**: blind second review covers all blocking-eligible
    cases, holdouts, reductions, disagreements, unresolved cases, and label
    changes. Remaining monitor and audit Development Cases receive a seeded 20%
    review, with at least ten cases per claim or a census when fewer exist.
    A required second reviewer is distinct from the author and the first
    reviewer.
    Each individual label, disagreement, adjudication, and approval is retained
    append-only; adjudication adds a decision and never overwrites either
    reviewer's original judgement.
18. **Reductions**: a Synthetic Reduction counts as evidence only when it has a
    Source-Backed parent and two reviewers confirm that decisive framework,
    lifecycle, control-flow, and dataflow semantics were preserved. Invented
    examples remain native syntax fixtures only.
19. **Karam evidence**: active Karam WIP remains read-only and yields Exploratory
    Cases identified by base revision, timestamp, source anchor, and per-file
    hash. It is never copied, archived, stashed, committed, or counted in quality
    metrics by this work. Raw evidence remains in existing access-controlled
    storage. The corresponding milestone commit may later provide stable
    evidence, but only an immutable committed-tree rerun can promote it from
    exploratory status.
20. **Corpus Refresh**: refresh when local Frappe or ERPNext advances, at every
    Karam milestone, monthly when neither occurred, and immediately for relevant
    security releases. Reuse unchanged cases, discover changed candidates, and
    mark changed labels or claims stale rather than rewriting history. Each
    refresh records its trigger, exact source and rule identities, discovery
    channels exercised, reused and stale cases, holdout impact, and next due
    date. A one-off pilot observation does not satisfy the recurring contract.
21. **Scorecard shape**: implement the Rule Quality Scorecard as non-compensating
    Admission Gates, not a points total or weighted quality score. Ownership,
    severity, or strength in another dimension cannot offset a failed gate.
22. **Universal admission**: every Accepted Rule needs a truthful single claim,
    complete contract and message, passing native tests, independently labelled
    real positive and safe near-miss evidence, declared compatibility and parser
    scope, and distinct portfolio value.
23. **Blocking admission**: only a Deterministic Defect, Proven Security
    Violation, or written Explicit Policy Violation may block. It must establish
    every decisive assumption, completely parse its scope, have zero reviewed
    false positives and unresolved cases, detect every known claim-present case,
    pass its frozen holdout, complete a census and Baseline Triage of every
    current match and suppression, and receive independent review plus Vatsal's
    approval. A sample can inform non-blocking measurement but can never
    substitute for that blocking census.
24. **Monitor admission**: monitor requires every universal gate and a bounded,
    credible claim whose visible uncertainty or cost prevents blocking. Its
    message and measurements must expose false positives, false negatives,
    unresolved cases, and required context without overstating certainty.
25. **Audit admission**: audit requires every universal gate and useful evidence
    for a declared Review Hotspot or Performance Hypothesis. It must state the
    contextual or runtime evidence still required and never imply a confirmed
    defect.
26. **Outside portfolio**: a candidate remains outside when it fails a universal
    gate, exceeds the engine proof boundary, duplicates another claim, or has
    unacceptable compatibility or review cost. It may continue as explicitly
    unaudited advisory output during migration but is not an Accepted Rule.
27. **Measurements**: record exact confusion counts only for enumerated
    populations, along with unresolved and policy-only counts, parse coverage,
    unique semantic issues, raw matches, findings per kLoC, runtime, memory, and
    review minutes. Report justified intervals and unresolved sensitivity bounds
    separately; do not invent portfolio-wide percentage thresholds before the
    real baseline. Sampling supports monitor, audit and outside-portfolio
    evaluation; it does not satisfy blocking Baseline Triage.
28. **Existing benchmark**: retain its version probes and smoke budgets of 60
    seconds per process, 10 seconds per whole scan, 1 second per rule match, and
    1536 MiB. Treat these as regression guards only. None of its current 17
    cases is acceptance evidence unchanged: eleven need source-backed
    replacement, three remain unresolved boundaries, and three unsupported
    assertions leave the acceptance corpus.
29. **Analysis Target inventory**: independently classify every eligible target
    as fully analysed, partially analysed, unanalysed, or intentionally excluded.
    Semgrep's reported scanned paths are not the eligibility denominator.
30. **Coverage handling**: every parser error, skipped target, unsupported
    construct, timeout, and incomplete execution is Scan Health. Blocking
    requires complete in-scope analysis. Inherited gaps remain visible in a
    ratcheting Coverage Baseline; new or changed in-scope gaps fail the gate.
31. **Templates**: mixed Jinja or template JavaScript is outside blocking native
    JavaScript scope until a deterministic, source-mapped, branch-aware
    transformation or separate analyser is validated with Source-Backed Cases.
    Generic mode is audit-only. Native-valid parser failures remain explicit
    compatibility gaps.
32. **Lifecycle**: support candidate, evaluating, accepted, suspended, and
    retired states. Accepted state carries blocking, monitor, or audit outcome.
    No current rule is grandfathered. Evidence Packets separately progress
    through `authored`, `blind-labelled`, `second-reviewed`, `adjudicated`,
    `approved`, and `decided`; transitions require named actors, timestamps,
    immutable input identities, and the artefacts produced at that transition.
    A packet cannot skip a required state or let one actor satisfy incompatible
    authorship and independent-review roles.
33. **Change actions**: evidence determines retain, narrow, split, downgrade,
    replace, or retire. A changed claim, proof boundary, or detection meaning
    receives a new ID and full admission; unchanged-claim pattern tuning reruns
    affected evidence.
34. **Suspension and restoration**: loss of a blocking gate, refresh, or steward
    suspends blocking immediately while the strongest truthful advisory outcome
    may continue. Restoration requires corrected evidence, affected reruns,
    independent review, and renewed Vatsal approval. A Rule Quality Standard or
    schema change includes a deterministic impact analysis naming every affected
    rule and packet. Affected blockers suspend until migrated and re-admitted;
    unaffected decisions remain valid without ceremonial re-review.
35. **Governance Change Packet**: rule implementation, contract, tests, Evidence
    Packet, catalogue decision, and compatibility impact change atomically.
    Schema validation and automated checks never substitute for independent
    review. Preparation and independent decision are separate delivery slices:
    the author freezes immutable inputs and hands off an `authored` packet; a
    different reviewer performs blind labelling and second review; adjudication
    precedes the required approval; only then may a steward append `decided`.
36. **Approval**: Noospheric owns the standard. Vatsal approves standard and
    blocking changes. Monitor and audit decisions require independent
    Noospheric review. An author cannot independently approve the same packet;
    Noema may maintain, author, or independently review work Noema did not
    author. A ticket that authors a packet cannot claim completion of its
    independent review or Vatsal approval. The hand-off records reviewer
    availability at batch entry and blocks the decision slice until the named
    reviewer and, where required, Vatsal have acted.
37. **Portfolio Review Cut**: after Vatsal has updated local Frappe and ERPNext,
    Noema assumes the refresh and records the exact live state read-only. The
    cut freezes the candidate cohort; later rules use the normal lifecycle and
    do not restart the initial migration.
38. **Review Queue**: record priority band, ordering reason, intended batch,
    prerequisites, and state without a numeric priority score. Re-rank at batch
    boundaries after relevant refreshes.
39. **Priority order**: prefer new Karam or compatibility matches and Scan Health
    risks; high-consequence security and deterministic correctness claims with
    usable evidence; broad or costly candidates; remaining correctness and
    policy candidates; then lower-consequence translation, UX, code-quality,
    and no-hit performance hypotheses.
40. **Pilot**: the provisional first Review Batch names
    `override-doctype-class`, `frappe-sql-format-injection`,
    `frappe-whitelisted-permission-bypass`,
    `frappe-n-plus-one-read-in-loop`, and
    `frappe-async-array-callback-misuse`. Refresh their live evidence and apply
    every entry gate before activation. A named candidate that lacks evidence,
    independent-review availability, or a bounded review plan is visibly
    deferred and replaced by the next eligible candidate in the same priority
    band. Record the selected identity in its delivery ticket before work starts
    and do not preassign any outcome. The async-array candidate is the preferred
    real public tracer because public source-backed positive and safe-boundary
    evidence is already identified; it may also be substituted if its entry gate
    fails.
41. **Batch limits**: the pilot contains five Rule Claims; later batches contain
    at most eight and shrink when evidence complexity, match volume, or reviewer
    load requires it. Keep one active Review Batch and at most one decided batch
    awaiting enforcement observation. A pilot entrant must fit one bounded
    packet-preparation context and one separate bounded decision context after
    clustering and sampling. If the required review cannot be bounded, defer it
    rather than hiding reviewer work inside a nominally small ticket.
42. **Batch entry**: require a proposed single claim, draft contract, exact rule,
    engine and source state, native tests, identified real positive and safe
    near-miss candidates, known parser scope, estimated match and review volume,
    and an independent reviewer. Visibly defer incomplete candidates and
    substitute the next eligible candidate in the same band. Activation records
    the final candidate identity, preparation owner, independent reviewer,
    approval needs, immutable evidence identity, and recovery path in the ticket
    before evidence work begins.
43. **Batch exit**: every candidate must receive a catalogue disposition with
    its completed contract, Evidence Packet, compatibility and Scan Health
    result, reviewed matches and suppressions, reviewer-cost observation,
    independent review, and required approval. `Still evaluating` is not a
    completed batch outcome. The preparation slice ends at frozen `authored`;
    the separate decision slice must preserve blind labels and disagreements,
    reveal the holdout only after the required freeze, obtain approvals, append
    the decision, and then mark the packet `decided`.
44. **Pilot success**: success means five defensible dispositions, measured
    reviewer cost, and a validated or corrected process. It does not require a
    Blocking Rule.
45. **Karam rollout**: the governed rules-repository catalogue is the only
    blocking source. Karam's app-local rule and Registry pack remain separately
    reported advisory inputs until imported through governance and pinned by
    immutable content; a mutable Registry alias never participates in gating.
    The private untracked `quality.yml` is the intended future integration
    target, but remains read-only until Vatsal names and authorises the milestone
    and file. Every authorised Karam pull request then receives a full
    committed-tree scan, while every local Milestone Scan analyses the complete
    working tree and records hashes and worktree state. Diff information
    controls presentation, never analysis scope. Integration must preserve the
    existing advisory lanes explicitly rather than silently dropping or
    promoting them.
46. **Compatibility schedule**: a rules-repository automation owns a
    weekly read-only Compatibility Scan of immutable stable Frappe and ERPNext
    snapshots. It records its schedule, exact inputs, latest successful run,
    missed or failed runs, and next due time. Monthly and event-driven Corpus
    Refresh remains separately recorded. The policy does not modify or gate
    upstream workflows and does not require a new service or dashboard.
47. **Engine upgrade**: pin rules-repository CI to Semgrep CE 1.174.0 and record
    the complete rules identity. Keep Karam's authorised workflow on 1.172.0
    until post-pilot qualification. Current-engine pinning is an immediate,
    independently verifiable slice; candidate qualification is a later slice
    that runs native tests, compatibility, parser coverage, performance guards,
    canonical scans, and real affected acceptance evidence. An upgrade changes
    neither pin until all affected evidence passes and the decision is appended
    with exact provenance.
48. **Gate failures**: fail only when required inputs or provenance cannot be
    verified; configuration or execution is invalid or incomplete; a new or
    changed in-scope coverage failure occurs; an unexcepted Accepted Blocking
    Rule matches; an exception is invalid; or required outputs cannot be
    produced.
49. **Finding presentation**: annotate Blocking Rule matches inline, place Scan
    Health in the required summary, group changed monitor issues, retain audit
    findings in the full report, and summarise unchanged advisory findings as
    counts and trends.
50. **Baseline Triage**: before blocking promotion, classify every current match
    and suppression for that claim as fixed, independently false positive,
    validly excepted, or admission-blocking. Existing `nosemgrep` comments grant
    no approval. The scorecard and Enforcement Set validators reject blocking
    when this census is incomplete, sampled or unverifiable. A candidate whose
    census cannot fit the active batch is deferred, substituted or limited to a
    truthful non-blocking outcome.
51. **Rule Exceptions**: require the exact rule and source, rationale, evidence,
    owner, Vatsal approval, and an expiry date or event. Reject bare, broad,
    permanent, or automatically renewed suppressions.
52. **Emergency Workflow Override**: only Vatsal may approve a single-pull-
    request override for a critical change. It expires after merge and requires
    the canonical scan before the next non-emergency merge.
53. **Rollback**: restore the last known-good Enforcement Set while the harmful
    rule continues advisory. Preserve its evidence and history; do not delete
    the rule, hide Scan Health, or revert application code as a rule rollback.
54. **Privacy**: store raw Karam results and complete reports only in existing
    access-controlled CI evidence. Public artefacts retain opaque case IDs,
    decisions, provenance, and links without private source or snippets. Do not
    build encrypted snapshot infrastructure.
55. **Completion**: the initial Portfolio Review completes only when every
    candidate in the cut has a final disposition and every associated current
    match and suppression has been handled. Progressive enforcement waits one
    real Karam milestone and one Frappe or ERPNext Compatibility Scan between
    blocking batches without preventing the next review batch from starting.

## Testing Decisions

1. Tests assert externally visible contracts at the two confirmed seams rather
   than internal helper structure. Internal modules may be reorganised without
   changing tests when repository acceptance and canonical scan behaviour stay
   stable.
2. `make test` remains the single repository acceptance command and must fail
   deterministically for invalid schema versions, duplicate claim identities,
   incomplete Rule Contracts, broken references, contradictory current state,
   unreviewed or non-deterministic migrations, rewritten or reordered decision
   history, missing native tests, and any byte change to the Upstream Mirror.
3. Repository tests cover valid and invalid catalogue, corpus, Evidence Packet,
   Review Queue, Enforcement Set, Coverage Baseline, Rule Exception, and
   decision-history fixtures. They exercise source/target schema versions,
   migration impact manifests, journal-chain tampering, and retired-ID reuse.
   Minimal invented source may test syntax and validation only; it must never be
   presented as precision evidence.
4. Native Semgrep tests continue to verify positive patterns, negative
   boundaries, and tracked parser gaps for upstream, backported, and Noospheric
   rules independently.
5. Ground-truth tests verify provenance requirements, label vocabulary,
   blindness fields, cluster integrity, development/holdout separation,
   pre-reveal commitments, freeze-before-reveal, allocation reveal,
   replenishment or explicit deficit, reduction-parent links, original
   disagreement retention, packet-state transitions, role separation,
   staleness, confidentiality, and prohibition of mutable WIP in admission
   metrics.
6. Scorecard tests use table-driven evidence packets to prove every universal
   and tier-specific gate is non-compensating. A candidate failing one gate must
   not pass because another measurement is strong. A sampled or incomplete
   Baseline Triage must fail the blocking gate regardless of holdout, precision
   estimate, severity or Vatsal approval.
7. Measurement tests verify denominators, census versus sample treatment,
   Wilson or exact intervals where declared, cluster-aware calculations,
   unresolved best/worst bounds, and refusal to emit unsupported precision,
   recall, or false-positive-rate claims. They prove sampled evidence can support
   only non-blocking outcomes until the complete blocking census exists.
8. Canonical scan integration tests exercise one complete portfolio execution
   and assert stable structured outputs for findings, provenance, Scan Health,
   Gate Evaluation, and human summary.
9. Gate tests cover each authorised failure condition and prove that monitor,
   audit, unaudited, unchanged inherited coverage gaps, and Semgrep severity do
   not independently fail the workflow. Enforcement Set validation rejects any
   Blocking Rule whose decided packet lacks complete, current and verifiable
   Baseline Triage of every match and suppression.
10. Coverage tests distinguish fully analysed, partially analysed, unanalysed,
    and intentionally excluded targets. They prove partial and failed targets
    never count as clean negatives and that new in-scope gaps are distinguished
    from inherited baseline gaps.
11. Template tests use real source-backed semantics for acceptance. Generic-mode
    fixtures may test audit detection but cannot satisfy blocking native-parser
    coverage.
12. Exception tests cover exact-source applicability, source and rule changes,
    expiration, renewal, invalid broad scope, missing approval, and distinction
    from Emergency Workflow Overrides.
13. Rollback tests prove that selecting the last known-good Enforcement Set
    changes gate behaviour while leaving rule history, advisory reporting, and
    application source untouched.
14. Privacy tests ensure public outputs contain opaque Karam evidence IDs and
    provenance only, while raw findings and source locations remain confined to
    access-controlled outputs.
15. Current-engine tests prove rules CI installs exactly Semgrep CE 1.174.0 and
    Karam remains on 1.172.0 until authorised qualification. Later engine
    compatibility tests run the pinned and candidate versions against real
    post-pilot Evidence Packets. An upgrade cannot pass when native tests,
    parser coverage, scan cost, compatibility, canonical output, or affected
    acceptance evidence drifts.
16. The existing benchmark runner continues to test manifest integrity, syntax
    behaviour, unexpected findings and parser errors, version compatibility,
    timeout, scan-time, per-rule-time, and memory guards. Its output must never
    be consumed as an admission score.
17. Pilot acceptance uses the real latest locally available Frappe, ERPNext,
    and Karam states recorded at execution time. Karam WIP observations remain
    exploratory until a stable milestone snapshot exists. Pilot activation
    tests prove any failed entry gate caused visible deferral and same-band
    substitution rather than a hidden waiver.
18. Each pilot candidate must independently exercise batch entry, corpus
    evidence, scorecard evaluation, current match and suppression review,
    compatibility, reviewer-cost recording, independent review, and catalogue
    disposition. Tests and artefact validation prove preparation stopped at a
    frozen `authored` packet and that a distinct actor completed the decision
    states and required approval without a predetermined outcome. A pilot packet
    may become blocking only after a full current-match and suppression census;
    sampled packets remain non-blocking or are deferred and substituted.
19. Karam Milestone Scan verification is read-only with respect to business
    code and includes untracked files locally. CI independently verifies the
    committed pull-request tree using immutable inputs. Tests prove only the
    governed catalogue can block; the app-local rule and Registry pack remain
    visibly separate advisory lanes; no mutable Registry alias enters Gate
    Evaluation; and the target workflow cannot change before the named
    Vatsal-authorised milestone.
20. A release-readiness test records at least one real Karam milestone and one
    Frappe or ERPNext Compatibility Scan without false positives, unresolved
    blockers, or unexplained Scan Health regression before the next blocking
    batch is promoted. It also verifies weekly schedule ownership, refresh
    freshness, append-only observation history, exception expiry, and the tested
    last-known-good Enforcement Set rollback path.

## Out of Scope

- Mutating Frappe-maintained files inside the Upstream Mirror.
- Changing Frappe or ERPNext application source or gating their upstream CI.
- Changing Karam Finance business logic, cleaning its worktree, committing its
  WIP, or performing its v16 refactor. Later Karam CI integration is limited to
  the canonical Semgrep workflow and must preserve unrelated work.
- Adding TypeScript, Vue, Bash, Dockerfile, GitHub Actions, or other new-language
  rule portfolios during this implementation.
- Requiring Semgrep Pro, Semgrep Cloud, cross-file analysis, or proof beyond
  Semgrep Community Edition's validated boundaries.
- Building a database, governance web application, dashboard as a source of
  truth, second benchmark platform, encrypted snapshot store, or new secrets
  infrastructure.
- Treating invented examples, random DocTypes, or the 17 provisional cases as
  acceptance evidence without the required source-backed replacement and
  review.
- Predetermining whether an individual broad rule will be narrowed, split,
  converted to taint, downgraded, replaced, or retired before its Evidence
  Packet is complete.
- Bulk suppression cleanup unrelated to the candidate currently under Portfolio
  Review.
- Making upstream contribution mandatory or allowing an upstream contribution
  to mutate the local mirror.
- Automatically updating Vatsal's local Frappe, ERPNext, or Karam worktrees.
- Beads, Codex Desktop, agent configuration, or repository-assistant setup.

## Further Notes

- Noospheric owns the Rule Portfolio. Vatsal is the accountable human steward
  and final blocking approver; Noema is the operational Codex co-steward.
- The current observed inventory is 61 Rule Candidates: 49 upstream, two
  backported, and ten Noospheric rules. The implementation records a fresh
  Portfolio Review Cut rather than assuming those counts remain current.
- The exploratory Semgrep CE 1.174.0 scan reported 7,122 scanned paths and eight
  parser failures across the live corpora. This is evidence of known coverage
  boundaries, not a complete target denominator or a permanent baseline.
- A point-in-time Karam WIP scan found 11 Engine Matches across four rules and no
  parser error. Those observations informed pilot selection but are not
  Ground-Truth Labels and must be refreshed before review. The immutable rules
  pin at `24b6f6df8cbb57e599c92e88300c9bc8c66a4ffa` contains 59 rather than 61
  rules and also produced 11 Karam matches across three rules. A CI-shaped scan
  including the mutable Registry pack produced 25 matches. These differences
  are why the approved input lanes must remain explicit.
- Rules-repository CI is to pin Semgrep CE 1.174.0. Karam's private replacement
  CI remains on 1.172.0 until post-pilot qualification; neither observation is
  permission to modify Karam during planning remediation.
- The repository currently has an aggregate rule test command, ownership and
  upstream-mirror validation, native Semgrep tests, and a provisional benchmark
  runner. These are prior art to extend, not proof that the new governance
  contracts already exist.
- The implementation should preserve every unrelated tracked and untracked
  change in this dirty worktree.
- This specification collapses the linked decisions and evidence in
  [Establish a trustworthy Semgrep rule foundation](map.md). The next flow is
  `to-tickets`; implementation must not begin by treating the former Wayfinder
  decision tickets as build tickets. The corrected implementation wave remains
  proposed until a fresh independent review and renewed Vatsal approval.
