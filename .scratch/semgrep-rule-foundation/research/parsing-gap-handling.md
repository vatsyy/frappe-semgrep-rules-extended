# Parsing-gap handling for the Rule Portfolio

Research date: 2026-08-22
Live engine: Semgrep CE 1.174.0 (`OSS`)
Scope: Python, JavaScript, JSON, and mixed Jinja/template boundaries in the
Frappe, ERPNext, and read-only Karam Finance corpus.

## Decision

Parser coverage is an independently inventoried scan-health result, not a
property inferred from findings or Semgrep's exit status. Every intended
Analysis Target is classified as fully analysed, partially analysed,
unanalysed, or intentionally excluded. Partial and failed targets never count
as clean negatives.

The programme should baseline inherited gaps, fail scan health on new or
changed in-scope gaps, and exclude mixed-template files from blocking native
JavaScript claims until a validated template-aware transformation or separate
language analysis supplies complete coverage. Generic mode remains audit-only.

## Primary-source boundary

Semgrep's first-party documentation describes CE structural analysis as
language-parser based and generic mode as token/indentation matching rather
than native AST analysis. Its dataflow documentation also warns that the
AST-to-IL translation is incomplete for some constructs. The tagged parser
source represents recoverable skipped/error regions as `PartialParsing`
instead of necessarily rejecting the whole target.

The consequence is asymmetric:

- a finding from a successfully parsed region remains an Engine Match that can
  be reviewed against its Rule Claim;
- absence of a finding cannot be treated as evidence about a partial or failed
  region; and
- successful process completion does not establish full target coverage.

The earlier version probes and primary-source review are recorded in
[Semgrep Community Edition proof boundaries](semgrep-ce-proof-boundaries.md).

## Live portfolio evidence

A read-only scan used the working rules tree and:

```text
semgrep scan --config rules --json --metrics=off --disable-version-check \
  --timeout 10 --max-memory 1536 --exclude node_modules \
  --exclude public/dist <frappe>/frappe <erpnext>/erpnext \
  <karam_finance>/karam_finance
```

The source states were:

| Product | Branch | Base revision | Working state |
| --- | --- | --- | --- |
| Frappe | `version-16` | `9523516cac25992bc2cd810e1015df8994c257f5` | clean |
| ERPNext | `version-16` | `21d187302045476f1ceb5d0d86219389ab1e75b8` | one dirty entry |
| Karam Finance | `develop` | `c49398c9e2af3506ea1fe8a15d369afbab27b949` | 62 dirty entries; read-only exploratory evidence |

The rules tree was based at
`24b6f6df8cbb57e599c92e88300c9bc8c66a4ffa` with 15 dirty entries. These facts
make the run exploratory evidence, not an immutable acceptance result.

Semgrep reported 7,122 scanned paths and eight parser failures: seven
`PartialParsing` records and one `Syntax error`. Its JSON contained no skipped
path inventory, so 7,122 is not a defensible denominator for all eligible
targets.

| Failure class | Count | Evidence |
| --- | ---: | --- |
| Mixed Jinja or generator-template JavaScript | 5 | Native Node 26.7.0 also rejected the unrendered source; failures occurred in Frappe/ERPNext template or boilerplate JavaScript. |
| Semgrep compatibility gap on native-valid source | 3 | Python 3.14.7 parsed both affected Python files and Node parsed the affected minified JavaScript, while Semgrep reported incomplete parsing. |
| Karam Finance parser failure | 0 | No parser error was emitted for the read-only Karam target tree in this run. |

A separate lexical discovery found 23 JavaScript files containing Jinja-like
delimiters—18 in Frappe and five in ERPNext—and 324 HTML files containing
template delimiters. This is a discovery inventory, not proof that every file
fails parsing or that delimiter-free templates are fully understood.

The live JSON also demonstrates that `error.type` is not uniform: the syntax
failure used a string, while partial parsing used a structured value containing
the affected spans. A future health collector must normalise both forms and
retain the spans rather than reducing them to a generic error count.

## Coverage inventory

Semgrep's reported scanned paths cannot be the sole denominator because
ignored, excluded, unsupported, oversized, timed-out, or undiscovered targets
may be absent. For each Rule Claim and Corpus Snapshot, independently enumerate
the Analysis Targets implied by its Rule Scope and record:

- product, revision, path, content hash, language and file kind;
- rule claim and analysis mode intended for the target;
- engine version and exact invocation;
- status: `full`, `partial`, `failed`, or `excluded`;
- parser error kind and exact spans where available;
- exclusion reason and approving steward;
- whether the gap is inherited, new, changed, or resolved; and
- the next analysis or review action.

Publish counts for all four statuses by product, language, file kind, and Rule
Claim. An aggregate ratio may describe workload, but it must not hide a gap in
a rare or high-risk stratum and cannot replace exact file-level reporting.

An intentional exclusion is outside a claim only when the Rule Scope names and
justifies it. It remains in the inventory and never becomes a clean negative.
Vendored/minified assets and source generators should be classified by their
actual role rather than silently treated as ordinary application JavaScript.

## Enforcement handling

### Blocking claims

Blocking requires complete analysis of every target inside the declared Rule
Scope. An unexpected partial or failed parse in a changed in-scope target is a
scan-health failure even when the rule reports no finding. A positive Engine
Match from a fully parsed region may still be reviewed, but it does not make
the rest of the target clean.

Known inherited gaps are baselined and remain visible. They do not block an
unrelated change, but they cannot sit inside the claimed blocking scope. A
change to a baselined target or error span requires fresh handling before the
scan can be called complete. Resolving a gap ratchets the baseline down; it is
not silently reintroduced later.

### Monitor and audit claims

Monitor and audit rules may operate on partial targets only when the Rule
Contract declares the limitation and the scan reports the gap beside any
matches. Their non-findings carry no negative evidence for the unanalysed
region. Generic-mode template rules are audit-only because they do not supply
native JavaScript or template AST semantics.

### Source error versus engine gap

For native Python or JavaScript, reproduce the failure on the pinned and
candidate Semgrep versions, then validate syntax using the authoritative native
parser without executing the source. A native-parser failure is a source
syntax problem as well as an Analysis Coverage Failure; native-parser success
identifies an engine compatibility gap. Neither is silently suppressed.

## Mixed-template handling

Treat Jinja-bearing JavaScript, JavaScript embedded in HTML/Jinja, and
JavaScript generator templates as mixed-template targets, not ordinary native
JavaScript. Until dedicated coverage is validated:

1. exclude them from blocking native-JavaScript Rule Scopes;
2. inventory and report them as explicit coverage boundaries;
3. use generic matching only for labelled audit hypotheses; and
4. require template-aware review or an appropriate separate analyser for
   security-sensitive changes.

A future transformation may support blocking only if it is deterministic,
retains source-to-generated mappings, covers relevant template branches,
produces parser-valid artefacts, and is validated with Source-Backed Cases.
Blindly stripping delimiters or substituting dummy literals is not equivalent
evidence. This requirement does not authorise building such infrastructure in
the current map.

## Baseline and reporting

The first portfolio audit establishes the Coverage Baseline against immutable
Corpus Snapshots. Each monthly or event-driven Corpus Refresh compares the new
inventory with that baseline:

- new or expanded in-scope failures are scan-health failures;
- unchanged inherited failures remain visible and non-clean;
- resolved failures are removed from the active baseline; and
- exclusions change only through a reviewed Rule Scope decision.

The compact scan-health report contains total targets and the four status
counts, new/changed/resolved gaps, exact affected paths and spans, affected Rule
Claims, engine/mode/snapshot provenance, and required action. Findings and scan
health remain separate outputs. The later CI enforcement ticket decides how
these outcomes map to workflow exit conditions.

## Sources

Primary Semgrep sources, accessed 2026-08-22:

- [Semgrep CE language support](https://docs.semgrep.dev/semgrep-ce-languages.md)
- [Generic pattern matching](https://docs.semgrep.dev/writing-rules/generic-pattern-matching.md)
- [Dataflow design trade-offs](https://docs.semgrep.dev/writing-rules/data-flow/data-flow-overview.md#design-trade-offs)
- [Semgrep v1.173.0 target parser](https://github.com/semgrep/semgrep/blob/v1.173.0/src/parsing/Parse_target.ml)

Local evidence came from Semgrep CE 1.174.0 JSON output and read-only native
syntax checks over the exact source states recorded above.
