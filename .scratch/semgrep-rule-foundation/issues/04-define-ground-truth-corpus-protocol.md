# Define the Ground-Truth Corpus protocol

Type: grilling
Status: resolved
Blocked by: 01, 03

## Question

What exact admission, provenance, snapshotting, sampling, blind-labelling,
second-review, ambiguity, confidentiality, and refresh rules should govern the
Frappe, ERPNext, and Karam Finance Ground-Truth Corpus?

## Answer

### Population and snapshots

The Ground-Truth Corpus represents evolving Frappe v16 and ERPNext v16 Corpus
Product Lines plus the Karam Finance v15 reference and v16 refactor. Each result
applies to immutable Corpus Snapshots, not to all future code. Karam cases also
record module status as refactored, pending, or mixed.

Tracked snapshots use exact commits. Active Karam WIP remains read-only and may
produce Exploratory Cases identified by base commit, timestamp, source anchor,
and per-file content hash. It is not copied, archived, stashed, committed, or
counted in quality metrics by this effort; cases become durable ground truth at
the corresponding milestone commit.

A Corpus Refresh occurs when the local Bench advances Frappe or ERPNext, at
each Karam milestone, monthly against upstream when neither occurred, and
immediately for relevant security releases. It reuses unchanged cases,
discovers candidates in the delta, and revalidates changed locations without
rewriting historical results.

### Admission and provenance

One Ground-Truth Case represents one semantic candidate for one versioned Rule
Claim. Admission requires a stable snapshot; source anchor and content hash;
product, module, language, file kind, parser status, and Karam refactor status;
discovery channel; independent label and rationale; reviewer evidence and
timestamps; confidentiality class; and any parent/reduction lineage.

The frame combines four independent evidence channels: a census of current
Engine Matches, rule-independent candidate discovery for missed positives,
real safe near-misses, and known defects supported by fixes, tests, reviews, or
runtime evidence. Rule output may locate a candidate but never supplies its
Ground-Truth Label. Analysis Coverage Failures remain a parallel coverage
record rather than positive or negative cases.

### Labels and blindness

The Ground-Truth Labels are `claim-present`, `claim-absent`, `policy-only`, and
`unresolved`. `claim-absent` denies only the stated Rule Claim, not every
possible defect. Initial reviewers see the Rule Claim and necessary source
context but not the rule output, message, metadata, or another reviewer's
label.

### Sampling and holdout

Sampling is by Case Cluster, stratified by product, Rule Claim, language,
parser status, and Karam refactor status. Rare and high-risk cases and every
blocking candidate receive a census. Other strata receive a census up to 100
independent clusters; larger populations use 100 seeded random clusters, with
population sizes, inclusion probabilities, weighted estimates, and 95%
uncertainty reported. Small censuses describe only their admitted population.

Source-backed Case Clusters are split 70/30 between visible Development Cases
and a sealed Acceptance Holdout. A function, defect, parent case, and all its
reductions stay in one side. Holdout labels are revealed only after the rule is
frozen; revealed cases become regression cases and are replaced during the
next Corpus Refresh.

### Review and ambiguity

Independent blind second review covers every blocking-eligible case, holdout,
synthetic-equivalence decision, disagreement, unresolved case, and label
change. A seeded 20%, with at least ten cases per Rule Claim or a census when
fewer exist, covers the remaining monitor/audit Development Cases. Business
intent requires domain-owner confirmation, and blocking admission requires
human approval of the evidence packet.

Disagreements receive evidence-led adjudication; absent decisive evidence they
remain `unresolved`. Unresolved cases never silently become positives or
negatives and are reported through their rate and best/worst-case bounds,
separately from sampling uncertainty.

### Confidentiality, reductions, and staleness

Karam source, patches, snippets, and raw findings remain outside publishable
fixtures. Public artefacts use opaque case IDs and, where useful, sanitised
Synthetic Reductions. A reduction counts as evidence only when its
Source-Backed Case exists and two reviewers confirm preservation of the
decisive Frappe API, lifecycle, control/data flow, and framework semantics.
Invented scenarios and random DocTypes are syntax regression fixtures only.

A label carries forward only while the Rule Claim and semantic source hash are
unchanged. Changed source or claim becomes stale and is excluded pending
review; deleted source remains historical rather than current evidence.
