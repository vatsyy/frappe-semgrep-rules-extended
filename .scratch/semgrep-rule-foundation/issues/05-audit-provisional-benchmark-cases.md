# Audit the provisional benchmark cases

Type: task
Status: resolved
Blocked by: 04

## Question

Applying the accepted Ground-Truth Corpus protocol, which of the 17 provisional
benchmark cases qualify unchanged, require a source-backed replacement, expose
a useful unresolved boundary, or must be removed?

## Answer

The detailed first-pass review is recorded in
[Provisional benchmark case audit](../audits/provisional-benchmark-cases.md).
None of the 17 cases qualifies unchanged as independent ground truth: eleven
need source-backed replacements, three preserve useful unresolved boundaries,
and three unsupported security assertions must leave the acceptance corpus.
The runner remains useful for compatibility and syntax regression, and all 17
draft cases still pass on Semgrep CE 1.174.0, but that result does not measure
precision, recall, or blocking reliability. Required blind second review is
deferred to corpus implementation; no case was admitted by this audit.
