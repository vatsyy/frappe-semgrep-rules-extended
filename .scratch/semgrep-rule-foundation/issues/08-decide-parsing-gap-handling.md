# Decide parsing-gap handling

Type: research
Status: resolved
Blocked by: 02

## Question

How should the programme measure and handle files Semgrep only partially parses
or cannot analyse, particularly JavaScript containing Jinja, without silently
treating unanalysed code as clean?

## Answer

The primary-source boundary, live CE 1.174.0 portfolio scan, and handling
policy are recorded in
[Parsing-gap handling for the Rule Portfolio](../research/parsing-gap-handling.md).

Independently inventory every Analysis Target and classify it as fully
analysed, partially analysed, unanalysed, or intentionally excluded. Partial
and failed targets are Analysis Coverage Failures, never clean negatives;
Semgrep's scanned-path list is not a sufficient eligibility denominator.

Blocking requires complete analysis inside the declared Rule Scope. New or
changed in-scope failures fail scan health, while inherited gaps remain visible
in a ratcheting Coverage Baseline and cannot support blocking claims. Monitor
and audit rules may report matches from partial targets only with explicit
limitations; their non-findings carry no negative evidence for unanalysed
regions.

Mixed Jinja/template JavaScript is excluded from blocking native-JavaScript
scope until a deterministic, source-mapped, branch-aware transformation or
separate language analysis is validated with Source-Backed Cases. Generic mode
is audit-only. Native-valid source that Semgrep cannot parse is recorded as an
engine compatibility gap rather than suppressed.

The live exploratory scan reported eight parser failures among 7,122 reported
scanned paths: five mixed/template JavaScript targets and three native-valid
Semgrep compatibility gaps. Karam Finance produced no parser failure in that
run. Findings and scan health remain separate outputs; CI wiring belongs to the
rollout ticket.
