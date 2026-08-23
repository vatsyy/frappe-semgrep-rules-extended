# Frappe Semgrep Rules Extended

## Language

**Rule Portfolio**: The complete set of Semgrep rules evaluated and governed by
this repository, regardless of whether a rule is upstream, backported, or
custom. _Avoid_: Ruleset when referring only to one ownership tier

**Rule Claim**: The single, precisely bounded proposition a rule's match can
establish without additional evidence. _Avoid_: Finding message, vulnerability

**Engine Match**: A location where Semgrep found the structure or dataflow
specified by a rule, before contextual judgement. _Avoid_: Finding, defect

**Reviewed Finding**: An Engine Match classified using source context and
independent evidence. _Avoid_: Raw match

**Disposition**: The reviewed status of an Engine Match. Confirmed satisfies the
Rule Claim; credible retains a decisive unproved assumption; audit establishes
only the declared hotspot or hypothesis; false positive does not satisfy the
claim; unresolved lacks sufficient agreement or evidence. _Avoid_: Severity

**Deterministic Defect**: A Rule Claim establishing incorrect language or
framework behaviour without needing contextual or runtime evidence. _Avoid_:
Code smell

**Proven Security Violation**: A Rule Claim establishing a security failure
through a fully machine-established source-to-sink flow, authorisation bypass,
unsafe configuration, or equivalent security invariant. _Avoid_: Dangerous
operation

**Explicit Policy Violation**: A Rule Claim establishing use of an operation
that an identified policy prohibits regardless of exploitability. _Avoid_:
Vulnerability

**Review Hotspot**: A Rule Claim identifying a dangerous operation that
requires contextual inspection before its risk is known. _Avoid_: Confirmed
defect

**Performance Hypothesis**: A Rule Claim identifying possible scaling
behaviour that requires runtime evidence. _Avoid_: Performance regression

**Analysis Coverage Failure**: A parser error, unsupported construct, skipped
target, or other condition preventing intended analysis. It is not a rule
finding. _Avoid_: Clean scan

**Analysis Target**: A source file or validated generated artefact that a Rule
Scope requires the declared engine and analysis mode to process. _Avoid_:
Scanned path

**Scan Health**: The independently reported completeness of intended analysis,
separate from whether any Engine Matches were produced. _Avoid_: Finding count

**Milestone Scan**: The required full-application analysis completed before a
Karam milestone is dispatched as a pull request. _Avoid_: Diff scan

**Compatibility Scan**: A read-only full scan of a stable Frappe or ERPNext
snapshot used to detect rule, engine, and parser drift without enforcing on
the upstream product. _Avoid_: Upstream CI gate

**Baseline Triage**: The review of every existing match and suppression for a
candidate blocker before it enters the Enforcement Set. _Avoid_: Legacy waiver

**Portfolio Review**: The mandatory claim-level evaluation of every current
rule and its associated matches and suppressions until each receives an
admitted or outside-portfolio disposition. _Avoid_: Sample audit, grandfathering

**Review Batch**: A bounded group of Rule Candidates receiving Portfolio Review
together while each Rule Claim retains its own evidence and disposition.
_Avoid_: Ruleset release, bulk acceptance

**Portfolio Review Cut**: The exact, provenance-recorded Rule Candidate
inventory whose dispositions define completion of one Portfolio Review effort.
Later candidates follow the normal lifecycle without reopening the completed cut.
_Avoid_: Forever-current rule count, grandfathered baseline

**Review Queue**: The version-controlled ordering record for one Portfolio
Review Cut, including each candidate's priority reason, intended Review Batch,
prerequisites, and review state. _Avoid_: Quality ranking, acceptance ledger

**Enforcement Set**: The immutable selection of Accepted Blocking Rules and
scan-health conditions authorised to fail a required workflow. Monitor, audit,
and unaudited rules are not members. _Avoid_: Error-severity rules

**Gate Evaluation**: The deterministic combination of Semgrep output, the
Enforcement Set, Scan Health, and valid Rule Exceptions into a required
workflow result. _Avoid_: `semgrep --error`, severity gate

**Rule Exception**: A source-specific, time-bounded human authorisation not to
enforce one Blocking Rule match, with its rationale and evidence preserved.
_Avoid_: `nosemgrep`, false-positive label

**Enforcement Rollback**: Restoration of the last known-good Enforcement Set
while the affected rule continues as advisory and its history is preserved.
_Avoid_: Rule deletion, application revert

**Emergency Workflow Override**: A Vatsal-approved, one-PR bypass used only
when a critical change cannot obtain a valid Gate Evaluation. It is not a Rule
Exception. _Avoid_: Permanent bypass, `nosemgrep`

**Coverage Baseline**: The snapshot-bound inventory of known Analysis Coverage
Failures used to distinguish inherited gaps from new, changed, or resolved
gaps. A baselined gap remains unanalysed. _Avoid_: Accepted parse error

**Validated Transformation**: A deterministic conversion of mixed-template
source into parser-valid Analysis Targets with preserved source mappings and
relevant template branches. _Avoid_: Jinja stripping, dummy substitution

**Blocking Rule**: A precision-first rule whose claim is sufficiently reliable
to prevent a change from proceeding. _Avoid_: High-severity hotspot

**Monitor Rule**: A rule that reports a credible policy or medium-confidence
concern without preventing a change. _Avoid_: Soft blocker

**Audit Rule**: A recall-first rule that identifies code requiring human or
runtime investigation without claiming a confirmed defect. _Avoid_: Failed
check, vulnerability

**Enforcement Ceiling**: The strongest enforcement tier a Rule Claim class may
reach after satisfying the Rule Quality Scorecard. _Avoid_: Severity

**Rule Contract**: The required declaration of a rule's identity, ownership,
claim, class, Enforcement Ceiling, scope, assumptions, confidence, observed
construct, remediation or next evidence, limitations, provenance, and
references. _Avoid_: YAML schema

**Rule Scope**: The language and framework versions, paths, file kinds,
analysis mode and boundary, machine-guaranteed prerequisites, and exclusions
within which a Rule Claim is valid. _Avoid_: Paths include list

**Rule Portfolio Catalogue**: The repository-owned governance source containing
the authoritative Rule Contract for every upstream, backported, and custom
rule without modifying mirrored upstream files. _Avoid_: Rule configuration

**Evidence Packet**: The reviewable collection of tests, Ground-Truth Corpus
results, compatibility evidence, costs, and provenance supporting one
catalogue decision. _Avoid_: Benchmark score, generated report

**Governance Change Packet**: The atomic review unit containing every affected
rule, Rule Contract, test, Evidence Packet, catalogue decision, and
compatibility impact. _Avoid_: Rule-only pull request, metadata follow-up

**Rule Stewardship**: Noospheric's continuing accountability for the Rule
Portfolio, exercised by Vatsal as human steward and approver and Noema as
operational Codex co-steward. _Avoid_: Agent ownership, unowned rule

**Upstream Mirror**: Frappe-maintained rule material reproduced byte-for-byte
and never locally mutated. _Avoid_: Local base rules

**Noospheric Rule**: A new or modified rule owned by Noospheric and kept
distinct from the Upstream Mirror, including one informed by upstream work.
_Avoid_: Mutated upstream rule

**Accepted Rule**: A rule with a complete Rule Contract that the Rule Quality
Scorecard has admitted to the governed Rule Portfolio. Mere presence in the
repository does not imply acceptance. _Avoid_: Existing rule

**Rule Candidate**: A proposed or existing rule awaiting admission or
re-admission through the Rule Quality Scorecard. Advisory execution does not
make it an Accepted Rule. _Avoid_: New rule, grandfathered rule

**Material Rule Change**: A change to a Rule Claim, Rule Scope, proof boundary,
or detection meaning that requires re-admission. _Avoid_: Pattern edit

**Suspended Rule**: A previously Accepted Rule whose evidence no longer
supports its admitted outcome and which cannot block pending re-evaluation.
_Avoid_: Temporarily accepted rule

**Retired Rule**: A historically catalogued Rule Claim that is no longer
active; its identity and replacement history remain preserved. _Avoid_: Deleted
rule

**Rule Confidence**: The measured reliability of a Rule Claim within its
declared scope. It does not express severity or exploitability. _Avoid_: Author
confidence

**Rule Quality Scorecard**: The claim-level set of non-compensating Admission
Gates that assigns blocking, monitor, audit, or outside-portfolio status. It is
not a points total. _Avoid_: Quality score

**Admission Gate**: A mandatory evidence condition for a particular
enforcement tier that cannot be offset by strength elsewhere. _Avoid_: Scored
criterion

**Outside-Portfolio Rule**: A rule excluded from the governed Rule Portfolio
because its claim, evidence, compatibility, cost, or distinct value is
insufficient. _Avoid_: Disabled finding

**Rule Message**: The explanation of the observed construct, bounded Rule
Claim, important non-claims, and remediation or next investigation presented
with an Engine Match. _Avoid_: Vulnerability label

**Corpus Product Line**: A continuously evolving source lineage admitted as an
evaluation population, such as a supported Frappe or ERPNext branch. Its states
are measured through Corpus Snapshots. _Avoid_: Latest code

**Corpus Snapshot**: An immutable, provenance-recorded state of a Corpus
Product Line or private worktree against which cases and results remain
reproducible. _Avoid_: Live corpus, current checkout

**Corpus Refresh**: Admission of a new Corpus Snapshot together with discovery
and revalidation of cases affected by its changes, while historical evidence
remains immutable. _Avoid_: Benchmark rerun

**Ground-Truth Corpus**: The versioned collection of independently classified
cases drawn from admitted Corpus Snapshots. New snapshots extend or revalidate
the corpus without rewriting historical evidence. _Avoid_: Benchmark fixtures

**Ground-Truth Case**: A case classified independently of the rule output that
will later be measured against it. _Avoid_: Matching fixture

**Case Cluster**: Ground-Truth Cases sharing one semantic source, defect, or
reduction lineage and therefore kept together during sampling and dataset
splitting. _Avoid_: Matching lines

**Ground-Truth Label**: The rule-blind classification of a Ground-Truth Case as
claim-present, claim-absent, policy-only, or unresolved. Analysis Coverage
Failures are recorded separately. _Avoid_: Finding disposition

**Development Case**: A Ground-Truth Case whose label is visible while a rule
is designed or calibrated. _Avoid_: Training fixture

**Acceptance Holdout**: A sealed set of Case Clusters used only after a rule
candidate is frozen, then replaced once revealed. _Avoid_: Hidden unit test

**Exploratory Case**: A source-backed candidate from a mutable worktree that
may guide discovery but is excluded from quality metrics until admitted from a
stable Corpus Snapshot. _Avoid_: Ground truth

**Source-Backed Case**: A Ground-Truth Case derived from observed Frappe,
ERPNext, Karam Finance, or another explicitly admitted corpus location, with
its provenance retained. _Avoid_: Representative example without provenance

**Synthetic Reduction**: A minimal fixture that preserves the decisive
behaviour of a Source-Backed Case while removing unrelated application detail.
_Avoid_: Invented example, random DocType

**Rule Quality Standard**: The decision-complete contract governing Rule
Claims, evidence, evaluation, enforcement, compatibility, and rollout across
the Rule Portfolio. _Avoid_: Benchmark suite
