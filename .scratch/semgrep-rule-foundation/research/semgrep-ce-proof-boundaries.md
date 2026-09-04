# Semgrep Community Edition proof boundaries

Research date: 2026-08-22
Versions probed: Semgrep CE 1.172.0 and 1.173.0
Scope: the Python and JavaScript rule portfolio, with particular attention to
Frappe APIs, taint/dataflow claims and Jinja embedded in JavaScript. This note
changes no rules, benchmark files, CI, applications or corpus files.

## Executive conclusion

Semgrep CE is strong at finding a stated syntactic shape in a successfully
parsed file, and it has useful but deliberately limited dataflow support. It
is not a whole-program proof engine.

The Rule Quality Standard should therefore distinguish these claims:

| Analysis | CE can support | CE cannot establish on its own |
| --- | --- | --- |
| Structural pattern | A code shape, AST relationship, metavariable equality or scoped occurrence in one parsed file | Runtime intent, execution order, cardinality, permissions, async completion or a call-graph path |
| Constant propagation | Some constant-equivalent expressions, including simple aliases | General value reasoning, arbitrary aliases, object shape or framework semantics |
| Taint/dataflow | A source-to-sink candidate within one function, subject to the rule's source/sink/propagator model | Sound vulnerability proof, all paths, arbitrary aliasing, cross-function or cross-file flow in CE |
| Interprocedural/interfile | CE has documented single-file cross-function constant propagation, but not Pro interprocedural taint or interfile analysis | Whole-program/cross-file taint or constant-flow claims; these are Pro analyses |
| Generic mode | Token/indentation patterns in mixed or unsupported text | JavaScript/Python AST semantics, robust multi-line language parsing or a replacement for a native parser |

This is not a claim that current findings are mostly false positives. It is a
claim about the maximum proposition a finding can honestly support. A broad
structural match may be a valuable monitor or audit signal while remaining too
weak to block a change.

## 1. Structural patterns: precise local shape, not behaviour

Semgrep rules operate on parsed syntax. `pattern`, `patterns`,
`pattern-either`, `pattern-inside`, `pattern-not` and related operators combine
positive and negative matched ranges. The documented evaluation order is:

1. evaluate positive patterns and intersect their ranges/metavariable
   bindings;
2. subtract ranges matched by negative patterns;
3. apply metavariable conditionals;
4. focus the result on selected metavariables.

See [Rule structure syntax, operators and evaluation strategy](https://docs.semgrep.dev/writing-rules/rule-syntax.md#patterns).

Consequences for this repository:

- `pattern-inside` can restrict a database call to a loop or function body, but
  it does not prove that the loop is unbounded, that the call executes once per
  row, or that the result is expensive.
- `pattern-not` removes a syntactic overlap. It does not prove that another
  branch, wrapper or runtime guard makes the operation safe.
- A sequence written with `...` is scoped by the preceding pattern; it is not a
  control-flow graph and does not model completion, exceptions or event-loop
  scheduling. See [ellipsis scope](https://docs.semgrep.dev/writing-rules/pattern-syntax.md#ellipsis-operator-scope).
- A rule matching `items.forEach(async (...) => { ... })` can establish that
  shape. It cannot establish that a later statement depends on all callbacks,
  nor that the callbacks are intentionally fire-and-forget. That distinction
  needs source-backed classification and, for a blocking claim, stronger local
  evidence than the shape alone.
- Likewise, `frappe.db.get_value(...)` inside a loop is a per-loop query
  candidate, not proof of N+1 runtime behaviour. Query count, row count and
  batching remain outside CE's static proof.

The pattern engine also applies documented equivalences such as import aliasing,
constant propagation and associative/commutative matching. These increase
coverage but can broaden the set of code considered equivalent; they must be
included in rule tests where the distinction matters. See [pattern
equivalences](https://docs.semgrep.dev/writing-rules/pattern-syntax.md#equivalences)
and [rule options](https://docs.semgrep.dev/writing-rules/rule-syntax.md#options).

## 2. Metavariables: syntactic binding with bounded scope

Metavariables capture code nodes and can be reused across a `patterns` formula.
In search mode, same-named metavariables unify within that formula. The
documentation explicitly distinguishes this from taint source/sink unification:
metavariables in `pattern-sources` and `pattern-sinks` do not unify by default;
`taint_unify_mvars: true` is required when that relation is intended. See
[metavariable unification](https://docs.semgrep.dev/writing-rules/pattern-syntax.md#metavariable-unification).

Typed metavariables are not a general type system. Semgrep documents that type
inference is single-file, shallow, and guaranteed only for local variables and
arguments; fields, array elements and literal types have limited support. See
[typed metavariables](https://docs.semgrep.dev/writing-rules/pattern-syntax.md#typed-metavariables).

The practical contract is:

- use metavariable equality to connect syntactic pieces in one matched scope;
- use `metavariable-pattern`, `metavariable-regex` and
  `metavariable-comparison` to constrain the captured syntax;
- do not describe a metavariable as an authenticated user, a safe path, a
  bounded collection or a Frappe DocType unless the rule has an independently
  justified analysis for that fact;
- do not expect a typed metavariable to resolve imports, subclasses or fields
  across files in CE.

Semgrep's own rule-options source records the defaults relevant to this
portfolio: constant propagation is enabled by default, taint metavariable
unification is disabled by default, and JavaScript `let`/`const` are treated as
`var` for matching. See the tagged v1.173.0
[`Rule_options.atd`](https://github.com/semgrep/semgrep/blob/v1.173.0/interfaces/Rule_options.atd#L35-L81).

## 3. Constant propagation and dataflow

Semgrep documents an intraprocedural dataflow engine for constant propagation,
taint tracking and symbolic propagation. Its stated trade-offs are important:

- no path sensitivity: potential paths are considered even when infeasible;
- no general pointer or shape analysis: non-trivial aliasing may be missed,
  array/data-structure elements are not generally tracked, and field
  sensitivity is limited for taint;
- no soundness guarantee: `eval`-like effects are ignored rather than modelled
  with worst-case assumptions;
- the AST-to-intermediate-language translation is incomplete for some language
  constructs, and unsupported constructs may be ignored without making the
  analysis fail.

See [dataflow engine overview and design trade-offs](https://docs.semgrep.dev/writing-rules/data-flow/data-flow-overview.md#design-trade-offs)
and [dataflow status](https://docs.semgrep.dev/writing-rules/data-flow/data-flow-overview.md#data-flow-status).

This means a constant-propagation match can be a useful local fact, but it is
not evidence that the analyser understands the surrounding Frappe data model.
For example, a literal DocType name propagated through a local variable is
different from proving that a dynamically selected DocType is authorised.

### Taint mode

Taint rules define source, sink, sanitizer and optional propagator patterns.
Semgrep reports a sink when a tainted value reaches it under that model. The
taint documentation states that propagation is within a function or method for
the CE-style analysis. Taint propagators themselves are intraprocedural, and
the documented interprocedural section labels cross-function taint as a Pro
feature. See [taint analysis overview](https://docs.semgrep.dev/writing-rules/data-flow/taint-mode/overview.md).

Additional proof limits relevant to security rules:

- a non-exact source marks subexpressions as sources; use `exact: true` when
  the source boundary must be narrow;
- a sanitizer pattern can mark all subexpressions of its match as sanitised;
  its shape must therefore be tested against nested sinks;
- custom propagators do not cross function boundaries in CE;
- a finding contains one displayed taint trace even when several possible paths
  exist;
- source/sink names do not imply that Frappe's wrappers, request objects or
  permission checks have the desired security semantics.

For this repo, a CE taint rule may support a claim such as “this recognised
request-derived value reaches this recognised SQL/shell/template sink within
this function without a recognised sanitizer”. It may not be worded as “this
endpoint is exploitable” when the value crosses an unmodelled helper, file or
framework boundary.

## 4. Interprocedural and interfile boundary

Semgrep's product documentation distinguishes CE from Semgrep Code:

- CE provides single-file, cross-function constant propagation, single-function
  taint analysis and semantic analysis;
- cross-file constant propagation and cross-file/cross-function taint are
  AppSec Platform analyses; CE's documented cross-function constant propagation
  remains single-file and construct-dependent, not a whole-program proof;
- CE cannot track data beyond a single function or file and may therefore have
  more false positives.

See [Semgrep AppSec Platform versus Community Edition, scanning and analyses](https://docs.semgrep.dev/semgrep-pro-vs-oss.md#scanning-and-analyses),
[CE language matrix](https://docs.semgrep.dev/semgrep-ce-languages.md), and the
language-specific [JavaScript](https://docs.semgrep.dev/languages/javascript.md#javascript-support-in-semgrep-ce)
and [Python](https://docs.semgrep.dev/languages/python.md#python-support-in-semgrep-ce)
pages.

The open-source v1.173.0 engine type makes this split explicit: `OSS` is the
Community Edition engine, while `PRO` carries `Intraprocedural`,
`Interprocedural` and `Interfile` analysis flavours. See
[`Engine_type.ml`](https://github.com/semgrep/semgrep/blob/v1.173.0/src/osemgrep/core/Engine_type.ml#L33-L58).

### Version probes

Read-only probes were run with `uvx --from semgrep==1.172.0` and
`uvx --from semgrep==1.173.0` against temporary files outside the repository.
Both versions reported `engine_requested: OSS` and produced the same result:

| Probe | CE 1.172.0 | CE 1.173.0 | Interpretation |
| --- | --- | --- | --- |
| `source()` and `sink(value)` in one Python function | Match at the sink | Match at the sink | Same-function taint is available when the source/sink patterns fit |
| `source()` in `route()` passed to `sink(value)` in `wrapper()` | No match | No match | CE did not prove the cross-function call chain |
| Source helper in one Python file passed to sink in another | No match | No match | CE did not prove the cross-file flow |
| `SECRET = "secret"; sink(SECRET)` against `sink("secret")` | Match | Match | Basic constant propagation works in this case |

The probes are compatibility checks, not accepted benchmark cases. They do not
prove that every Python or JavaScript construct behaves identically. They do
support setting the default contract for the repository: unless a future run
explicitly uses a licensed Pro engine, no rule may claim cross-function or
cross-file taint reachability.

## 5. Python and JavaScript in this repository

Python and JavaScript are native CE languages for structural matching. CE's
documented analyses for each are single-file, cross-function constant
propagation, single-function taint and semantic analysis. Framework-specific
analysis and cross-file dataflow are not part of that CE contract. The current
CE pages also warn that framework-specific Pro rules may fail to return findings
when run under CE.

Implications for Frappe rules:

- Frappe's permission, DocType lifecycle, database and client-form semantics
  must be encoded explicitly in local patterns and evidence; Semgrep will not
  infer them from the framework name.
- A wrapper such as `frappe.call`, a whitelisted Python method, or a helper that
  eventually reaches `frappe.db.sql` is not an end-to-end taint path in CE
  unless the relevant source, propagator and sink all fit the same-function
  model.
- A structural rule can identify a likely framework operation and label it as
  a candidate. It should not use a vulnerability severity/message that implies
  a reachability proof it cannot perform.
- Test Python and JavaScript separately. Similar-looking syntax does not imply
  identical AST/dataflow support, especially around async functions, callbacks,
  destructuring, decorators, comprehensions and framework wrappers.

The rule metadata should record at least `analysis` (`structural`, `constprop`,
`taint-ce` or `generic`), the analysis scope (`file` or `function`), required
parser status, and the intended enforcement tier. That makes an accidental
`--pro`/`--pro-intrafile` run visible rather than silently changing the claim.

## 6. Jinja embedded in JavaScript

Frappe assets can contain Jinja delimiters in files that are otherwise scanned
as JavaScript. A Jinja expression such as `{{ report_json }}` is not JavaScript
syntax. The v1.173.0 parser source shows that the JavaScript target is parsed
using the TypeScript tree-sitter parser (TSX dialect) with a JavaScript Pfff
fallback; there is no Jinja-aware JavaScript parser in this CE path. See
[`Parse_target.ml`](https://github.com/semgrep/semgrep/blob/v1.173.0/src/parsing/Parse_target.ml#L98-L108).

The parser represents skipped/error tokens as `PartialParsing` errors rather
than necessarily discarding the whole file. See
[`Parse_target.ml`](https://github.com/semgrep/semgrep/blob/v1.173.0/src/parsing/Parse_target.ml#L40-L50).
Consequently, a finding outside the error span can still be emitted, but the
AST/dataflow coverage of the error region is not a proof. A partial-parse file
must not be counted as a clean negative, and a blocking rule must not silently
ignore the parse error.

### Version probes for mixed syntax

The temporary JavaScript probe was:

```javascript
const report = {{ report_json }};
frappe.call({ method: "x" });
```

With a structural `frappe.call(...)` rule, both CE 1.172.0 and 1.173.0:

- emitted one finding for the later call;
- emitted a `PartialParsing` error covering the Jinja expression (line 1,
  columns 17–32).

Running the same structural probe in `generic` mode emitted one finding and no
parser error for this tiny example. That does not make generic mode a native
JavaScript replacement. Official documentation says generic mode tokenises
words/punctuation and indentation, limits ordinary ellipses to ten lines, and
has only single-word metavariables; it explicitly warns that result quality can
vary and that the mode does not understand the language syntax. See [generic
pattern matching](https://docs.semgrep.dev/writing-rules/generic-pattern-matching.md).

For the current corpus, choose one of these explicit policies before treating
Jinja-bearing files as coverage:

1. preprocess/render the template into a parser-valid artefact and retain the
   source-to-generated mapping;
2. scan native JavaScript and Jinja/template content as separate languages;
3. use generic mode only for a labelled monitor/audit rule with a known loss of
   AST precision; or
4. exclude the file from a blocking claim and report the parse gap.

Do not silently treat a partial JavaScript parse as a full negative result.

## 7. Rule Quality Standard consequences

The foundation audit should apply these acceptance rules:

1. **State the proof boundary in the claim.** “Matches a database call inside
   a loop” and “proves an N+1 defect” are different claims.
2. **Record the engine and parser status.** Every scorecard entry should retain
   Semgrep version, `OSS`/`PRO` engine, language, file and parse errors.
3. **Keep tiers separate from severity.** Blocking requires a deterministic
   local claim with complete parsing; monitor can carry a credible but
   incomplete policy/taint concern; audit is appropriate for performance and
   broad hotspots.
4. **Use source-backed boundary cases.** For async callbacks, pair the real
   dependent-child-row case with the real independent fire-and-forget case.
   For N+1, pair a per-record query with batching and write-in-loop cases. For
   SQL, shell, filesystem and templates, distinguish source-to-sink flow from
   API/policy use.
5. **Do not use a synthetic fixture as an oracle.** A reduction is admissible
   only when its parent source case and decisive behaviour are recorded.
6. **Measure parser coverage separately.** Parse errors are neither false
   positives nor true negatives; they are an analysis-coverage result.
7. **Do not promise whole-program coverage from CE.** If a candidate depends on
   a helper, import, wrapper or framework lifecycle outside the file/function,
   classify it as `unresolved`, `monitor` or `audit` until another source of
   evidence closes the gap.

## Residual uncertainty

- The official documentation is a moving page; the probes pin the two versions
  in this repository but do not prove all constructs or future releases.
- A small probe cannot estimate precision or recall. Real Frappe, ERPNext and
  read-only Karam cases still need independent semantic labels.
- Taint precision depends on the exact source, sink, sanitizer and propagator
  patterns. A same-function “no finding” may be a missing rule model rather
  than evidence of safety.
- Parser recovery is construct-dependent. The Jinja probe establishes a
  partial-parse boundary, not a universal percentage of lost JavaScript AST.
- Runtime query counts, rows read, permission enforcement and intended
  fire-and-forget behaviour require source review and, where material, runtime
  validation outside Semgrep CE.

## Sources

All sources below are first-party Semgrep documentation or source at the tagged
v1.173.0 release, accessed 2026-08-22.

- [Semgrep CE versus AppSec Platform](https://docs.semgrep.dev/semgrep-pro-vs-oss.md)
- [Semgrep CE language matrix](https://docs.semgrep.dev/semgrep-ce-languages.md)
- [JavaScript support](https://docs.semgrep.dev/languages/javascript.md)
- [Python support](https://docs.semgrep.dev/languages/python.md)
- [Rule pattern syntax](https://docs.semgrep.dev/writing-rules/pattern-syntax.md)
- [Rule structure syntax](https://docs.semgrep.dev/writing-rules/rule-syntax.md)
- [Dataflow engine overview](https://docs.semgrep.dev/writing-rules/data-flow/data-flow-overview.md)
- [Taint analysis overview](https://docs.semgrep.dev/writing-rules/data-flow/taint-mode/overview.md)
- [Generic pattern matching](https://docs.semgrep.dev/writing-rules/generic-pattern-matching.md)
- [v1.173.0 engine types](https://github.com/semgrep/semgrep/blob/v1.173.0/src/osemgrep/core/Engine_type.ml)
- [v1.173.0 rule options](https://github.com/semgrep/semgrep/blob/v1.173.0/interfaces/Rule_options.atd)
- [v1.173.0 target parser](https://github.com/semgrep/semgrep/blob/v1.173.0/src/parsing/Parse_target.ml)
- [v1.173.0 taint rule test](https://github.com/semgrep/semgrep/blob/v1.173.0/cli/tests/default/e2e/rules/taint.yaml)
- [v1.173.0 intrafile taint test](https://github.com/semgrep/semgrep/blob/v1.173.0/cli/tests/default/e2e/rules/taint_intrafile.yaml)
- [v1.173.0 intrafile taint target](https://github.com/semgrep/semgrep/blob/v1.173.0/cli/tests/default/e2e/targets/taint/taint_intrafile.py)
