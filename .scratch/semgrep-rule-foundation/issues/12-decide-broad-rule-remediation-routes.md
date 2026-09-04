# Decide broad-rule remediation routes

Type: grilling
Status: closed
Disposition: out of scope
Assignee: Noema
Blocked by: 11

## Question

For the broad Rule Candidates exposed by the ordered Portfolio Review, which
specific claims should retain or narrow structural matching, split into
separate claims, use Semgrep CE taint analysis, remain audit-only, or leave the
Rule Portfolio, and what evidence supports each route?

## Answer

Rule-specific remediation choices belong to Portfolio Review implementation,
not to this planning map. The agreed Rule Quality Standard requires each choice
to follow a completed Rule Contract, independently labelled Ground-Truth
Corpus evidence, native tests, compatibility and Scan Health results, match and
suppression review, and the Rule Quality Scorecard. None of those per-rule
Evidence Packets exists yet, and the provisional benchmark has zero cases
admissible unchanged.

Predetermining that a specific candidate should use taint analysis, narrower
structural matching, audit-only reporting, or retirement would therefore
bypass the evidence gates and risk inventing a mutation to justify the plan.
The lifecycle already defines the allowed routes: retain, narrow, split,
downgrade, replace, or retire; Semgrep CE proof boundaries determine whether a
structural or same-function taint implementation can support the resulting
Rule Claim.

The implementation begins with the five-candidate pilot defined by
`Define the existing-rule review order`. Each candidate receives its own
evidence-led disposition through a Governance Change Packet. Later Review
Batches use the same process. These outcomes do not need another foundational
decision ticket.
