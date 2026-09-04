# Define the Rule Quality Scorecard

Type: grilling
Status: resolved
Blocked by: 01, 02, 03, 04

## Question

Which measurements, thresholds, uncertainty treatment, performance budgets,
compatibility requirements, and enforcement gates determine whether a rule may
block, monitor, audit, or remain outside the accepted Rule Portfolio?

## Answer

The Rule Quality Scorecard is a claim-level set of mandatory Admission Gates,
not a weighted or numeric score. It applies equally to upstream, backported,
and custom rules through the Rule Portfolio Catalogue. Ownership does not
exempt a rule from evaluation, and strength in one area cannot compensate for
a failed gate elsewhere.

### Universal admission gates

Every Accepted Rule must have:

1. a truthful, single Rule Claim no stronger than its machine-established
   evidence;
2. a complete Rule Contract and Rule Message;
3. passing native Semgrep positive, negative, and tracked-gap tests;
4. independently labelled, Source-Backed positive and safe near-miss evidence;
5. declared engine, analysis-mode, language, and parser compatibility; and
6. distinct portfolio value rather than a duplicate or weaker restatement of
   another accepted claim.

A rule failing any universal gate remains outside the governed Rule Portfolio.
It may continue to appear in current milestone scans as unaudited advisory
output, but it cannot block and must not be presented as an Accepted Rule.

### Enforcement decisions

**Blocking** is available only to a Deterministic Defect, a Proven Security
Violation, or an Explicit Policy Violation backed by an identified written
policy. The rule must also establish every decisive assumption within its Rule
Scope; completely parse its intended scope; produce zero reviewed false
positives and zero unresolved cases; detect every known claim-present case;
pass its frozen Acceptance Holdout; and receive independent review plus human
approval of the evidence packet. These are absolute gates, not rounded
percentage targets.

**Monitor** requires all universal gates and a bounded credible claim whose
remaining uncertainty or reviewer burden prevents blocking. False positives,
false negatives, and unresolved cases are permitted only when their exact
counts and operational cost are visible and the message does not overstate
what the rule established. Explicit Policy Violations default here unless the
blocking policy gate is met. A blocking-eligible claim that misses a blocking
gate may monitor only if the weaker status and wording remain truthful.

**Audit** requires all universal gates and evidence that the rule usefully
identifies a declared Review Hotspot, Performance Hypothesis, or other
recall-first investigation target. Its output must state the contextual or
runtime evidence still required. Audit status never implies a confirmed defect
and is not converted into blocking through severity alone.

**Outside portfolio** applies when a universal gate fails, the claim exceeds
the engine's proof boundary, compatibility or review cost is unacceptable, or
the rule adds no distinct value. Exclusion is a governance result, not a claim
that the underlying code is safe.

### Measurements and uncertainty

Record exact `TP`, `FP`, `FN`, and `TN` only where the corresponding population
was enumerated, together with unresolved and policy-only counts, parse
coverage, unique semantic issues, raw Engine Matches, findings per kLoC, and
review minutes. Precision, recall, and false-positive rate may be derived where
their denominators are valid; none is a composite quality score.

Do not invent portfolio-wide percentage thresholds before the first real
portfolio audit establishes a baseline. For an independent probability
sample, report the numerator, denominator, and a pre-declared 95% Wilson or
exact interval. Use design-aware cluster or stratified uncertainty where the
sample design requires it. A census has no sampling interval for that admitted
finite population. Report unresolved-case best/worst sensitivity bounds
separately from sampling uncertainty.

### Compatibility, coverage, and cost

Evidence records the exact Semgrep version, Community Edition analysis mode,
invocation, rule revision, and Corpus Snapshot. Test the repository's pinned CE
version and the proposed candidate version before an engine upgrade; mutable
labels such as `latest` are not reproducible acceptance evidence.

Blocking requires complete parser coverage across the declared Rule Scope.
Monitor and audit rules may declare explicit exclusions, but every parser
error, skipped target, and unsupported construct remains an Analysis Coverage
Failure and is reported separately from findings.

Retain the existing smoke-test safety budgets—60-second process timeout,
10-second whole scan, 1-second maximum rule match, and 1536 MiB memory—as
regression guards, not evidence of acceptable real-world cost. During the first
portfolio audit, measure per-rule and whole-scan runtime, peak memory, finding
volume, and review time on the real corpus. Set or revise operational budgets
only from that baseline rather than choosing premature percentage limits.

### Storage

Store one compact Rule Portfolio Catalogue row per Rule Claim, covering its
identity and ownership, contract status, admitted outcome, exact counts,
coverage, engine/corpus versions, review cost, decision date, and links to the
native tests and evidence packet. This extends the agreed catalogue; it does
not justify a scorecard application, a second benchmark system, or new
infrastructure.
