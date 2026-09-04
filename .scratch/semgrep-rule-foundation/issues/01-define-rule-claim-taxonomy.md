# Define the Rule Claim taxonomy

Type: grilling
Status: resolved

## Question

What claim categories, required fields, terminology, and enforcement limits
must every rule declare so that a match never communicates more certainty than
Semgrep has established?

## Answer

Each rule establishes exactly one Rule Claim. Several patterns may share a rule
ID only when they have the same claim, assumptions, and Enforcement Ceiling.

Semgrep produces an Engine Match. Independent review turns it into a Reviewed
Finding with one Disposition: confirmed, credible, audit, false positive, or
unresolved. Analysis Coverage Failures remain scan-health results, never clean
findings or true negatives.

Every rule belongs to exactly one claim class:

- Deterministic Defect;
- Proven Security Violation;
- Explicit Policy Violation;
- Review Hotspot; or
- Performance Hypothesis.

Deterministic Defects and Proven Security Violations are blocking-eligible only
after satisfying the Rule Quality Scorecard. Explicit Policy Violations monitor
by default and may block only under identified written policy. Review Hotspots
and Performance Hypotheses are audit-only. New Analysis Coverage Failures may
gate scan health separately from inherited gaps.

A blocking claim requires every decisive assumption to be matched or guaranteed
by its Rule Scope. Local pattern absence cannot establish global absence.
Severity expresses potential consequence, not CI enforcement; CWE and OWASP
references classify rather than prove risk.

Every rule requires a Rule Contract covering identity, ownership, one bounded
claim, class, Enforcement Ceiling, Rule Scope, assumptions, Rule Confidence,
observed construct, remediation or next evidence, limitations, provenance, and
references. Its Rule Message states the observation, bounded claim, important
non-claims, and next action.

The Rule Portfolio Catalogue is the authoritative repository-owned contract
source for every rule, including immutable upstream rules. Rules without a
complete contract may be evaluated but cannot block or monitor until the
scorecard admits them as Accepted Rules.
