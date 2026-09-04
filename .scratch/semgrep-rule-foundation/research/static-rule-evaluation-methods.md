# Defensible static-rule evaluation methods

Research date: 2026-08-22  
Scope: the current Frappe Semgrep rule portfolio and its Frappe, ERPNext and
Karam Finance corpora. This note is methodological; it changes no rules,
fixtures, CI or corpus files.

## Executive conclusion

Evaluate a rule claim against an independently labelled set of source-backed
cases. Do not let the rule's own annotations, current findings, or a hand-picked
set of matches define truth. Use Semgrep's native tests as fast regression tests,
but use a separate ground-truth ledger for quality measurement.

The defensible sequence is:

1. State one bounded Rule Claim and the unit of evaluation (usually one
   semantic candidate or one known defect, not one line or one file).
2. Freeze a sampling frame: corpus revisions, eligible files, parser status,
   languages, rule claims and provenance.
3. Label a stratified sample blind to rule output, retaining `confirmed`,
   `safe`, `policy/intended` and `unresolved` as distinct outcomes.
4. Run the rule and map findings to case IDs, deduplicating multiple matches for
   the same semantic issue.
5. Report precision, recall and coverage with denominators, sampling design and
   uncertainty; report ambiguity, parser failures and review effort separately.
6. Re-run the frozen set for every rule change and Semgrep-version change.

This separates three questions: did Semgrep match the syntax, is the claim true
in context, and should the result block a change? A rule may be useful as an
audit signal without proving a blocking defect.

## 1. Ground truth and the evaluation unit

### Use an explicit Rule Claim

Write the proposition a finding is allowed to establish before looking at the
rule output. Examples:

- “A value that may be controlled by an HTTP request reaches this SQL sink
  without the recognised parameterisation boundary.”
- “A child-row query is executed once per unbounded parent-row iteration.”
- “This code uses `forEach(async ...)` and then performs an operation whose
  correctness depends on all callbacks having completed.”

The claim must name its required context and its proof boundary. A structural
match such as `open(...)`, `shell=True`, or `forEach(async ...)` is not itself a
claim of traversal, command injection, or a race.

Johns et al.'s *Scanstud* describes systematic, fine-grained evaluation of
static-analysis tools using test cases and tool-specific results, which supports
making the case and claim the explicit units of comparison rather than treating
an aggregate warning count as quality ([Johns et al., 2011,
doi:10.1109/ICSTW.2011.32](https://doi.org/10.1109/ICSTW.2011.32)). Rutar et
al.'s comparison likewise evaluated multiple bug-finding tools over common code
and discusses non-overlapping warnings and trade-offs, not just one tool's raw
count ([Rutar, Almazan and Foster, 2005,
doi:10.1109/ISSRE.2004.1](https://doi.org/10.1109/ISSRE.2004.1)).

### Keep truth independent of the rule

For every case, record the source revision, application/module, language,
location, claim ID, behavioural rationale, expected class, reviewer evidence and
whether it is a source-backed case or a synthetic reduction. The expected class
must be decided before the rule is run, or by a reviewer who is blind to its
result. A synthetic reduction is admissible only after a source-backed parent
case and a review that the decisive behaviour was preserved.

NIST's Software Assurance Reference Dataset (SARD) is a useful precedent: it is
a repository of test programmes with documented weaknesses, and Juliet provides
paired bad and good source/sink examples rather than leaving the analyser to
declare its own oracle ([NIST, SARD](https://samate.nist.gov/SARD/); [NIST,
SAMATE overview](https://www.nist.gov/itl/csd/secure-systems-and-applications/samate)).
The OWASP Benchmark similarly ships an expected-results file: each test case has
an intentional CWE and an expected true/false result, and tool output is scored
against that file ([OWASP Benchmark project](https://owasp.org/www-project-benchmark/);
[BenchmarkJava README](https://github.com/OWASP-Benchmark/BenchmarkJava/blob/master/README.md)).
These are precedents for an external oracle, not permission to copy their
security labels into Frappe code.

The oracle problem is real: test results need an independent decision procedure,
and some behaviours cannot be classified from a test execution or syntax alone
([Barr et al., 2015, *The Oracle Problem in Software Testing*,
doi:10.1109/TSE.2014.2372785](https://doi.org/10.1109/TSE.2014.2372785)). For
Frappe, permissions, lifecycle ordering, query fan-out and intended background
work therefore need source context and, where relevant, runtime evidence.

### Do not force ambiguity into a binary label

Use at least these labels:

| Label | Meaning for measurement |
| --- | --- |
| `confirmed` | The Rule Claim is supported at the stated location and revision. |
| `safe` | The same-shaped code does not satisfy the claim under the stated context. |
| `policy/intended` | The pattern may violate a policy, but no defect or exploit is established. |
| `unresolved` | The available evidence cannot support a reproducible decision. |

`policy/intended` is not a false positive: it answers a different question from
“confirmed defect”. Keep enforcement tier (`blocking`, `monitor`, `audit`) as a
separate field. Exclude `unresolved` from the primary binary score and publish
its rate; optionally publish best/worst-case metric bounds with the assumptions
made explicit.

## 2. Sampling a representative corpus

### Build the sampling frame first

At a fixed revision, enumerate eligible files and candidate locations for each
Rule Claim, including parser failures and known safe near-misses. The frame must
retain application, module/refactor status, language, file type, rule claim,
candidate category, and source revision. Do not form the frame only from current
findings: that makes false negatives invisible.

For this repository, use a stratified design with strata at least by:

- application/corpus (Frappe, ERPNext, Karam Finance);
- language and parse status;
- Rule Claim and candidate type (known positive, safe near-miss, policy,
  performance hypothesis);
- module/refactor status where Karam is concerned.

Randomly select within each stratum and retain each stratum's population and
sample sizes. Take a census of rare, high-risk, newly introduced or
source-backed defect cases rather than risking their loss in a random sample.
If strata are sampled at different rates, use inclusion probabilities or
survey weights for portfolio estimates and report per-stratum results as well.

This is an applied design choice, not a claim that a single benchmark is
representative of all Python or JavaScript. State the intended population (the
admitted corpus and revisions), sampling frame, exclusions and refresh date.
NIST's experimental-design handbook begins with objectives and selection of an
appropriate design ([NIST/SEMATECH e-Handbook, “Choosing a Design”](https://www.itl.nist.gov/div898/handbook/pri/pri.htm));
Runeson et al.'s case-study guidance is a useful software-engineering precedent
for stating context and threats to validity ([Runeson et al., 2008,
doi:10.1007/s10664-008-9102-8](https://doi.org/10.1007/s10664-008-9102-8)).

### Avoid invalid pooling

Report both:

- **Per-claim metrics:** each rule's precision, recall, ambiguity, parse
  coverage and review cost.
- **Portfolio metrics:** a clearly defined micro/weighted aggregate, with the
  strata and weights shown.

Do not let a high-volume, low-value rule dominate a claim about the portfolio.
Do not use unlabelled code as a negative class: “Semgrep did not report it” is
not evidence that no defect exists. On naturally occurring code, recall is
estimable only for the known-positive/source-backed portion unless a credible
negative and missed-positive review process exists.

## 3. Metrics that answer different questions

For an independently labelled binary case set, use the usual confusion-matrix
counts:

| Metric | Formula | Meaning |
| --- | --- | --- |
| Precision (PPV) | `TP / (TP + FP)` | Of reported cases, how many satisfy the claim? |
| Recall (TPR) | `TP / (TP + FN)` | Of known claim-satisfying cases, how many were reported? |
| False-positive rate | `FP / (FP + TN)` | Of enumerated safe cases, how many were reported? |
| Coverage | `parseable eligible files / eligible files` | How much of the intended corpus was analysed? |

OWASP Benchmark documents the TP/FN/FP/TN definitions and the TPR/recall and
false-positive-rate formulas in its scoring specification ([OWASP Benchmark,
“Scoring”](https://owasp.org/www-project-benchmark/)). Use the same formulas,
but retain the case-level denominators and provenance.

Report `coverage`, `parse_error_count`, unsupported-language count and analysis
mode separately. A parser failure is neither a true negative nor a false
positive. Semgrep's own documentation also makes analysis power part of the
contract: default taint tracks within a function/method; `--pro-intrafile` and
Pro inter-file analysis extend the boundary ([Semgrep, “Taint analysis
overview”](https://semgrep.dev/docs/writing-rules/data-flow/taint-mode/overview.md)).
Record the engine/version and mode with every run, otherwise comparisons can
mistake a proof-boundary change for a rule improvement.

Accuracy is not a useful primary metric on a large, mostly unlabelled corpus:
the true-negative denominator is unknown and can make a rule that reports
nothing look good. For imbalanced labelled sets, precision-recall reporting is
more informative than ROC reporting alone ([Saito and Rehmsmeier, 2015,
doi:10.1371/journal.pone.0118432](https://doi.org/10.1371/journal.pone.0118432)).

For this portfolio, the scorecard should therefore show per Rule Claim:

`TP, FP, FN, TN (only where enumerated), precision, recall, FPR, parse coverage,
unresolved rate, policy/intended count, findings per kLoC, unique-issue count,
and review minutes.`

Findings per kLoC is a workload descriptor, not a quality score. Deduplicate
multiple matches that describe one semantic issue, while retaining raw finding
counts for operational cost.

## 4. Sampling error and confidence intervals

### Pre-specify the interval method

For a simple random sample of independent cases, report a 95% interval for each
proportion and its numerator/denominator. Do not use the textbook Wald interval
by default: Brown, Cai and DasGupta compare binomial interval methods and show
that its coverage can be poor; Wilson or an exact method is safer for small or
extreme proportions ([Brown, Cai and DasGupta, 2001, *Interval Estimation for a
Binomial Proportion*, doi:10.1214/ss/1009213286](https://doi.org/10.1214/ss/1009213286)).
For exact binomial limits, cite and use the Clopper-Pearson construction
([Clopper and Pearson, 1934, doi:10.1093/biomet/26.4.404](https://doi.org/10.1093/biomet/26.4.404)).

For stratified, weighted or clustered cases, do not pretend every match is an
independent Bernoulli trial. Use a survey-weighted variance estimator or a
bootstrap that resamples the independent unit (for example, the file or case
cluster, not individual lines). Efron's original bootstrap paper provides the
primary statistical basis for resampling-based uncertainty ([Efron, 1979,
*Bootstrap Methods: Another Look at the Jackknife*, doi:10.1214/AOS/1176344552](https://doi.org/10.1214/AOS/1176344552)).
The report must state the resampling unit and whether the interval is design- or
model-based.

If the entire admitted finite corpus is labelled, there is no sampling error
for that corpus; there is still label uncertainty, corpus drift and external
validity risk. Do not attach a sampling confidence interval merely because a
metric is a proportion.

### Make unresolved cases visible

For reported candidates, let `TPc` and `FPc` be confirmed counts and `Uc` the
unresolved count. A transparent sensitivity range is:

```text
precision_low  = TPc / (TPc + FPc + Uc)
precision_high = (TPc + Uc) / (TPc + FPc + Uc)
```

Use an analogous range for recall only after defining whether each unresolved
case is an unresolved ground-truth label or an unresolved rule outcome. Publish
the classification and never silently assign `unresolved` to the class that
makes the rule look best. Intervals for sampling error and ranges for semantic
ambiguity are different quantities and should not be merged.

## 5. Reviewer agreement and ambiguity

Use two independent reviewers for candidate labels on the calibration and
blocking subsets. Hide the rule's message where feasible during the first label
pass, show the source and claim contract, and record evidence. Adjudicate only
after both labels are stored; retain the original disagreement and adjudication
rationale.

Report raw agreement and a per-class confusion table. For two nominal reviewers,
also report Cohen's kappa ([Cohen, 1960, *A Coefficient of Agreement for Nominal
Scales*, doi:10.1177/001316446002000104](https://doi.org/10.1177/001316446002000104)).
For more than two reviewers, a multi-rater nominal agreement statistic such as
Fleiss's kappa is appropriate ([Fleiss, 1971, *Measuring Nominal Scale
Agreement Among Many Raters*](https://doi.org/10.1177/001316447101000204)). Do
not use kappa as a substitute for the raw counts: prevalence imbalance can make
agreement statistics difficult to interpret. `unresolved` and adjudication
rate are first-class quality signals.

## 6. Regression and version-drift testing

Semgrep's native rule tests are valuable fast checks. The first-party test
contract supports `ruleid` for expected findings, `ok` for expected non-findings,
and `todoruleid`/`todook` for explicitly tracked gaps; `semgrep --test` runs the
tests and `--validate` validates rule configuration ([Semgrep, “Test rules”](https://semgrep.dev/docs/writing-rules/testing-rules.md)).

Those annotations are authored alongside the rule, so they are regression
tests, not independent ground truth. The repository should keep a second
benchmark manifest/ledger whose labels and provenance are maintained separately.

For each run, freeze and record:

- source revision and corpus snapshot;
- rule file/config hash and Rule Claim version;
- Semgrep version, engine/mode, language/parser status and command;
- case IDs, finding-to-case mapping and deduplication policy;
- raw result artefact and scorecard version.

Run the pinned CI version and the candidate/current version over the same set.
Classify every difference as an intended rule change, parser/engine drift,
coverage change, changed ground truth, or unexplained regression. A changed
finding count without this classification is not evidence of improvement.

## 7. Reviewer cost and practical value

Precision and recall do not tell us whether a team can live with a rule. Measure
the review workload directly:

- active review minutes per candidate (median and p90, not only mean);
- candidates and unique issues per 1,000 lines or per changed file;
- independent-disagreement and adjudication rates;
- unresolved rate and time-to-resolution;
- confirmed defects found per reviewer hour;
- false-positive minutes per confirmed defect;
- parser/unsupported-file rate and rerun cost.

Keep raw candidate count and unique semantic issue count separate: duplicate
locations can inflate workload without increasing defects. Evaluate a proposed
blocking rule against its predecessor on the same cases and report the change in
confirmed findings, false-positive minutes and unresolved work—not just a lower
finding count.

This cost/utility emphasis is grounded in static-analysis adoption research.
Sadowski et al. report that a static-analysis project must provide developers a
benefit and an enjoyable/useful experience ([Sadowski et al., 2018, *Lessons
from Building Static Analysis Tools at Google*, doi:10.1145/3188720](https://doi.org/10.1145/3188720)).
Vassallo et al. study how developers engage with static-analysis tools across
contexts ([Vassallo et al., 2019, doi:10.1007/s10664-019-09750-5](https://doi.org/10.1007/s10664-019-09750-5)),
and their developer-perspective study highlights context, prioritisation and
warning relevance ([Vassallo et al., 2018, doi:10.1109/SANER.2018.8330195](https://doi.org/10.1109/SANER.2018.8330195)).
Ruthruff et al. explicitly study predicting accurate and actionable warnings,
which supports measuring actionability and review effort in addition to
classification metrics ([Ruthruff et al., 2008,
doi:10.1145/1368088.1368135](https://doi.org/10.1145/1368088.1368135)).

## 8. Proposed protocol for this repository

1. For each existing rule, write its Rule Claim, required context, proof
   boundary, intended tier and known exclusions.
2. Build the fixed-revision frame across Frappe, ERPNext and read-only Karam
   Finance. Include all current matches, safe near-misses, known defects and
   parser failures; do not copy Karam WIP verbatim into publishable fixtures.
3. Stratify and sample as above. Label independently, double-label the
   blocking candidates and preserve `unresolved`.
4. Run Semgrep only after the initial labels are recorded. Map and deduplicate
   findings by semantic case ID.
5. Publish a per-rule scorecard with confusion counts, Wilson/exact or
   design-aware intervals, ambiguity and reviewer-cost fields. Show both
   per-stratum and aggregate values.
6. Use `semgrep --test` for rule-local regression and the independent scorecard
   for acceptance. Run both pinned CI and candidate Semgrep versions.
7. Use the evidence to retain, narrow, split, downgrade, replace or retire a
   rule. Do not set blocking thresholds until the baseline denominators,
   reviewer cost and unresolved rate are known.

The first implementation decision should therefore be the Rule Claim and
sampling-frame schema, not a new async, N+1 or security matcher.

## Sources

- [Semgrep — Test rules](https://semgrep.dev/docs/writing-rules/testing-rules.md)
- [Semgrep — Taint analysis overview](https://semgrep.dev/docs/writing-rules/data-flow/taint-mode/overview.md)
- [OWASP Benchmark project and scoring](https://owasp.org/www-project-benchmark/)
- [OWASP BenchmarkJava README](https://github.com/OWASP-Benchmark/BenchmarkJava/blob/master/README.md)
- [NIST SAMATE/SARD](https://www.nist.gov/itl/csd/secure-systems-and-applications/samate)
- [Johns et al., *Scanstud* (2011)](https://doi.org/10.1109/ICSTW.2011.32)
- [Rutar, Almazan and Foster, *A Comparison of Bug Finding Tools for Java* (2005)](https://doi.org/10.1109/ISSRE.2004.1)
- [Tomassi et al., *Bugs in the Wild* (2018)](https://doi.org/10.1145/3236024.3275439)
- [Barr et al., *The Oracle Problem in Software Testing* (2015)](https://doi.org/10.1109/TSE.2014.2372785)
- [Runeson et al., case-study guidelines (2008)](https://doi.org/10.1007/s10664-008-9102-8)
- [Brown, Cai and DasGupta, binomial intervals (2001)](https://doi.org/10.1214/SS/1009213286)
- [Clopper and Pearson, exact binomial limits (1934)](https://doi.org/10.1093/biomet/26.4.404)
- [Efron, bootstrap methods (1979)](https://doi.org/10.1214/AOS/1176344552)
- [Cohen, nominal-scale agreement (1960)](https://doi.org/10.1177/001316446002000104)
- [Fleiss, multi-rater agreement (1971)](https://doi.org/10.1177/001316447101000204)
- [Saito and Rehmsmeier, precision-recall plots (2015)](https://doi.org/10.1371/journal.pone.0118432)
- [Sadowski et al., static-analysis adoption at Google (2018)](https://doi.org/10.1145/3188720)
- [Vassallo et al., developer engagement with static analysis (2019)](https://doi.org/10.1007/s10664-019-09750-5)
- [Vassallo et al., developer perspective and context (2018)](https://doi.org/10.1109/SANER.2018.8330195)
- [Ruthruff et al., actionable warnings (2008)](https://doi.org/10.1145/1368088.1368135)
- [NIST/SEMATECH e-Handbook — choosing a design](https://www.itl.nist.gov/div898/handbook/pri/pri.htm)
