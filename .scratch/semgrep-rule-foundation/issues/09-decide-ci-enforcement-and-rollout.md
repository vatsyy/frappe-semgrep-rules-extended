# Decide CI enforcement and rollout

Type: grilling
Status: resolved
Blocked by: 06, 07, 08

## Question

How should accepted blocking, monitor, and audit rules enter diff scans,
scheduled full scans, compatibility checks, exception handling, and rollback
without overwhelming reviewers or hiding regressions?

## Answer

### Rollout boundary

Semgrep remains a required gate before every Karam Finance milestone pull
request. Current scans continue throughout migration, but only the immutable
Enforcement Set and Scan Health may fail the workflow. Monitor, audit, and
unaudited rules still run and require review without acquiring blocking power
from severity or historical behaviour.

Enforcement begins only in Noospheric-controlled applications, starting with
Karam Finance. Frappe and ERPNext remain read-only compatibility and evidence
corpora; this policy neither changes nor blocks their upstream workflows.

Every current upstream, backported, and Noospheric rule must receive a complete
Portfolio Review covering its Rule Claim, Rule Contract, scope, tests,
provenance, parser coverage, distinct value, real matches, and associated
suppressions. No rule is grandfathered. Review proceeds in controlled batches:
a fully reviewed batch may enter its admitted outcomes while the remaining
rules continue as explicitly unaudited advisory rules. The rollout is not
complete until every rule has a blocking, monitor, audit, or outside-portfolio
disposition.

### Scan topology and reproducibility

One canonical command defines local and CI behaviour. It uses the same exact
Semgrep version, immutable rules revision, Rule Portfolio Catalogue, Analysis
Target inventory, exclusions, resource settings, and Gate Evaluation logic.
Application CI never consumes mutable branches or `latest` evidence.

The schedule is:

- every Karam pull request receives one full-application scan; its merge-base
  diff controls presentation, not what is analysed;
- every local Milestone Scan analyses the complete working tree, including
  untracked files, and records file hashes and worktree state before dispatch;
- CI independently scans the committed pull-request tree and never trusts a
  local success assertion;
- stable Frappe and ERPNext snapshots receive weekly Compatibility Scans; and
- monthly, milestone, release, and relevant security events trigger the
  previously agreed Corpus Refresh and affected portfolio revalidation.

Rules CI tests the pinned engine and one proposed candidate engine. An upgrade
occurs only after native tests, compatibility, parser coverage, performance
guards, and affected acceptance evidence pass on the candidate.

### Gate Evaluation

Semgrep runs the complete rule portfolio once and emits structured output. A
deterministic Gate Evaluation combines that output with the immutable
Enforcement Set, Scan Health, Coverage Baseline, and valid Rule Exceptions.
Semgrep severity and `--error` do not decide governance directly.

A required scan fails only for:

- failure to obtain or verify the pinned engine, rules, catalogue, or target
  inventory;
- invalid configuration, incompatible versions, timeout, memory exhaustion,
  or incomplete execution;
- a new or changed in-scope Analysis Coverage Failure;
- an unexcepted Engine Match from an Accepted Blocking Rule;
- an expired, invalid, or inapplicable Rule Exception; or
- failure to produce the required provenance and Scan Health record.

Monitor, audit, and unaudited matches never fail the gate. Unchanged inherited
coverage gaps remain visible and non-clean but do not fail unrelated changes.
The gate's exit status and its full evidence report are both required outputs.

### Baseline triage and reviewer load

Before a blocker enters the Enforcement Set, a full Baseline Triage classifies
every existing match and suppression for that rule. Each must be fixed,
independently labelled false positive, covered by an approved Rule Exception,
or prevent blocking admission. Existing `nosemgrep` comments confer no approval.

Pull-request presentation is tiered:

- Blocking Rule matches receive actionable inline annotations;
- Scan Health failures appear in the required summary;
- new or changed monitor matches are grouped by semantic issue;
- audit findings remain in the full report rather than routine inline noise;
  and
- unchanged advisory findings appear as counts and trends unless affected by
  the change.

If monitor volume is not reviewable, the rule remains audit or outside the
portfolio. Each batch records unique issues, false positives, unresolved cases,
and reviewer time; no percentage budget is invented before the real baseline.
A subsequent enforcement batch waits until the current batch completes at
least one real Karam milestone and one Frappe/ERPNext Compatibility Scan with
no false positive, unresolved blocker, or unexplained Scan Health regression.

### Exceptions, suppressions, and emergency override

A Rule Exception is source-specific and identifies the exact blocking rule,
rationale, evidence, owner, Vatsal's approval, and an expiry event or date. It
cannot survive the next relevant source change, rule change, Corpus Refresh, or
milestone review without fresh evidence and explicit renewal. Bare, file-wide,
directory-wide, permanent, and automatically renewed suppressions are
prohibited. Monitor and audit dispositions normally live in review evidence
rather than source comments.

Every existing suppression is reviewed with its rule during the mandatory
Portfolio Review; there is no unrelated bulk cleanup of Karam WIP. A rule
cannot enter its admitted outcome until all associated suppressions are
triaged.

Only Vatsal may approve an Emergency Workflow Override when a critical change
cannot obtain a valid Gate Evaluation. It is limited to the exact pull request
and stated reason, expires immediately after merge, and requires the canonical
scan before the next non-emergency merge. It is not a Rule Exception and never
becomes `nosemgrep`.

### Regression, rollback, and evidence privacy

A new Frappe or ERPNext parser gap, false positive, missed positive, or claim
drift triggers re-evaluation and may suspend the affected rule in Noospheric's
Enforcement Set. It does not alter upstream repositories.

When an enforced blocker proves harmful, restore the last known-good
Enforcement Set immediately while continuing to run the affected rule as
advisory. Do not delete the rule, rewrite its history, revert application code,
or hide a Scan Health failure. Re-enforcement requires corrected evidence,
independent review, and renewed Vatsal approval.

The private pull-request check contains a concise result; raw Semgrep JSON and
the full report remain access-controlled CI artefacts. The repository retains
only catalogue decisions, provenance, and evidence links. Raw Karam source and
private findings are never copied into public fixtures. Existing repository
access controls are sufficient; no encrypted snapshot system is required.
