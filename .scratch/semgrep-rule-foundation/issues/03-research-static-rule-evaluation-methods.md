# Research defensible static-rule evaluation methods

Type: research
Status: resolved

## Question

Which primary-source methods and metrics provide a defensible way to evaluate
static-analysis rules for precision, recall, ambiguity, sampling error,
regression, and reviewer cost without allowing the current rules to define
their own ground truth?

## Answer

The primary-source review is recorded in
[Defensible static-rule evaluation methods](../research/static-rule-evaluation-methods.md).
It establishes an independent, claim-centred oracle; frozen and stratified
sampling frames; separate precision, recall, coverage, ambiguity and reviewer
cost measures; design-aware uncertainty; double review for blocking subsets;
and distinct native regression tests versus independent acceptance evidence.
Thresholds must follow this repository's measured baseline rather than being
invented upfront.
