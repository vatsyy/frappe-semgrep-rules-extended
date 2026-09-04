# Research Semgrep Community Edition proof boundaries

Type: research
Status: resolved

## Question

What can the Semgrep Community Edition versions in scope actually prove for
Python and JavaScript through structural patterns, metavariables, taint mode,
dataflow, interprocedural analysis, and mixed-template parsing, and where must
the Rule Quality Standard explicitly stop making claims?

## Answer

The primary-source review and version probes are recorded in
[Semgrep Community Edition proof boundaries](../research/semgrep-ce-proof-boundaries.md).
Semgrep CE can support bounded local structural, metavariable, constant-
propagation, and same-function taint claims when parsing and the rule model
succeed. It cannot by itself establish framework intent, permissions, async
dependence, query cardinality, exploitability, or cross-function/cross-file
taint reachability. Partial parsing is an Analysis Coverage Failure rather
than a clean negative; generic mode is suitable only for explicitly limited
monitor or audit claims, not as a native-AST substitute.
