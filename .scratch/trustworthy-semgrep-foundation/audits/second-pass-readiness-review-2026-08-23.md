# Second-pass readiness review: trustworthy Semgrep foundation

**Review date:** 2026-08-23  
**Review mode:** Read-only  
**Scope:** Foundation decisions, implementation specification, proposed 16-ticket first wave, live rules repository, and read-only Frappe, ERPNext, and Karam Finance integration context.

This is review evidence, not a normative source. Accepted corrections should be incorporated into the specification and affected tickets. Volatile observations below describe the exact local revisions and worktrees inspected; no repository, application, ticket status, branch, index, or source file was changed during the review.

## Verdict

**Not ready; foundational decisions remain open**

The policy is unusually thoughtful and the spec mostly preserves the Wayfinder decisions. The implementation wave is not yet safe to start because:

- the authoritative Karam scan inputs and CI target are undefined in live state;
- Ticket 01 is broad synthetic governance scaffolding, not a defensible end-to-end evidence slice;
- holdout sealing, blind review, human approval and reviewer hand-offs are not operationally represented;
- engine qualification is sequenced before real acceptance evidence exists; and
- fixed pilot tickets conflict with the documented substitution and evidence-led disposition rules.

## Critical findings

No P0 finding.

### P1 — The authoritative Karam scan contract is unresolved

**Affected artefacts:** committed `karam_finance@c49398c:.github/workflows/linter.yml:28-34`; WIP [quality.yml:57](../../../../karam_finance/.github/workflows/quality.yml#L57), [semgrep.yml:1](../../../../karam_finance/semgrep.yml#L1), [spec.md:36](../snapshots/pre-remediation-2026-08-23/spec.md#L36), [Ticket 14:12](../snapshots/pre-remediation-2026-08-23/issues/14-integrate-karam-catalogue-gating.md#L12).

**Evidence:** Karam HEAD contains a workflow that clones mutable upstream Frappe rules, installs unpinned Semgrep and consumes mutable `r/python.lang.correctness`. The working tree deletes that file and introduces an untracked replacement pinning Semgrep 1.172.0 and rules commit `24b6…`, but still consumes the Registry alias and an app-local rule outside the 61-rule catalogue. A current WIP scan produced:

- working 61-rule tree: 11 matches across four rules;
- immutable 59-rule CI pin: 11 matches across three rules;
- CI-shaped pinned scan plus current Registry pack: 25 matches, including 14 `string-concat-in-list` matches.

The specification’s statement that Karam “currently relies on `--error`” describes untracked WIP, not immutable HEAD.

**Consequence:** Ticket 14 cannot preserve existing behaviour, provide immutable inputs or guarantee that only catalogued blockers fail without silently dropping, separately retaining or governing these additional rule sources. It also overlaps private untracked CI work.

**Smallest correction:** resolve one explicit decision defining:

1. which Karam workflow is authoritative;
2. whether the app-local rule and Registry pack join the catalogue or remain a separate immutable advisory scan;
3. how the mutable Registry alias is pinned or removed; and
4. the user-approved file/milestone at which Ticket 14 may integrate.

### P1 — Ticket 01 is not a genuine tracer bullet

**Affected artefacts:** [Ticket 01:3](../snapshots/pre-remediation-2026-08-23/issues/01-govern-reference-rule-candidate.md#L3), [spec.md:245](../snapshots/pre-remediation-2026-08-23/spec.md#L245), [spec.md:283](../snapshots/pre-remediation-2026-08-23/spec.md#L283).

**Evidence:** the ticket attempts to build catalogue, schemas, Rule Contracts, Ground-Truth Cases, Evidence Packets, scorecard, lifecycle, append-only history, generated views and repository acceptance around invented test-only source. Yet universal admission requires independently labelled source-backed positive and safe near-miss evidence.

**Consequence:** it can test validators, but cannot prove that a real candidate traverses evidence collection, blind review and admission. Calling it end-to-end encourages a test-only exception or fabricated “independent” evidence—the circular benchmarking the plan is intended to prevent. It is also too large for one fresh implementation context.

**Smallest correction:** recast Ticket 01 honestly as a bounded schema/validator walking skeleton, then add one real public, source-backed candidate slice that exercises the review path without production enforcement. Do not require generated views unless a named consumer exists.

### P1 — Holdout and independent-review requirements are not operational

**Affected artefacts:** [Ground-Truth decision:66](../../semgrep-rule-foundation/issues/04-define-ground-truth-corpus-protocol.md#L66), [spec.md:257](../snapshots/pre-remediation-2026-08-23/spec.md#L257), [Ticket 08:21](../snapshots/pre-remediation-2026-08-23/issues/08-review-override-doctype-class.md#L21), [Ticket 13:15](../snapshots/pre-remediation-2026-08-23/issues/13-close-pilot-review-batch.md#L15).

**Evidence:** no ticket explicitly implements sealed 70/30 cluster allocation, label concealment, reveal-after-freeze, holdout replacement, original disagreement retention or an author→independent reviewer→Vatsal approval transition. Pilot tickets instead demand final dispositions within the same implementation ticket.

**Consequence:** the required oracle independence and approval separation cannot be demonstrated. A fresh agent can author a packet, but cannot legitimately complete its independent review or Vatsal approval.

**Smallest correction:** add explicit packet states and artefacts for `authored`, `blind-labelled`, `second-reviewed`, `adjudicated`, `approved`, and `decided`; split evidence preparation from independent review/approval. Add holdout sealing and replenishment acceptance criteria.

### P1 — Engine qualification is sequenced before qualifying evidence exists

**Affected artefacts:** [Ticket 06:7](../snapshots/pre-remediation-2026-08-23/issues/06-pin-and-qualify-semgrep-engines.md#L7), [Ticket 06:17](../snapshots/pre-remediation-2026-08-23/issues/06-pin-and-qualify-semgrep-engines.md#L17), [Ticket 07:7](../snapshots/pre-remediation-2026-08-23/issues/07-record-review-cut-and-queue.md#L7).

**Evidence:** Ticket 06 requires “affected acceptance evidence”, but precedes the pilot that creates the first real Evidence Packets. Ticket 07 then blocks the pilot on Ticket 06. Qualification is therefore either vacuous or logically cyclic. The live rules make this concrete: the working tree contains 61 rules while the immutable CI revision contains 59.

**Consequence:** the candidate engine could be declared qualified using only authored fixtures, then later encounter drift on real evidence.

**Smallest correction:** split Ticket 06 into:

- immediate exact pinning of the current rules-CI engine; and
- later candidate-engine qualification after pilot evidence exists.

Record an immutable PR SHA or content-addressed rule-tree hash for pre-merge candidate evidence.

### P2 — Pilot selection and disposition criteria conflict with the spec

**Affected artefacts:** [Ticket 07:23](../snapshots/pre-remediation-2026-08-23/issues/07-record-review-cut-and-queue.md#L23), [spec.md:370](../snapshots/pre-remediation-2026-08-23/spec.md#L370), [Ticket 11:21](../snapshots/pre-remediation-2026-08-23/issues/11-review-n-plus-one-read-in-loop.md#L21).

**Evidence:** the spec requires candidates lacking entry prerequisites to be substituted within their priority band. Ticket 07 nevertheless mandates all five named candidates in the batch, and Tickets 08–12 are already fixed. Ticket 11 further preassigns `audit` or `outside-portfolio`, while the spec says outcomes must not be preassigned.

**Consequence:** missing evidence or reviewer availability cannot trigger the promised substitution, and the N+1 review begins with its answer embedded in acceptance criteria.

**Smallest correction:** mark the five names as provisional until Ticket 07 proves every entry gate. Permit renaming/substitution of Tickets 08–12. Replace Ticket 11’s outcome clause with “the scorecard assigns the strongest truthful outcome permitted by the evidence and final claim class”.

### P2 — Several durable requirements have no owner

**Affected artefacts:** [governance decision:75](../../semgrep-rule-foundation/issues/10-define-rule-quality-standard-governance.md#L75), [Ground-Truth decision:69](../../semgrep-rule-foundation/issues/04-define-ground-truth-corpus-protocol.md#L69), [spec.md:387](../snapshots/pre-remediation-2026-08-23/spec.md#L387), [Ticket 15:22](../snapshots/pre-remediation-2026-08-23/issues/15-observe-pilot-rollout.md#L22).

**Evidence:** no ticket owns general schema migration, standard-change impact analysis and affected-rule suspension, weekly Compatibility Scan scheduling, holdout replacement after reveal, or the complete monthly/event-driven freshness path. Ticket 13 covers only defects discovered by the pilot; Ticket 15 performs one observation.

**Consequence:** the first wave could pass while long-term append-only history, schema evolution and freshness remain prose-only promises.

**Smallest correction:** assign these acceptance criteria explicitly to Tickets 01, 03, 13 and 15; do not create a new service or dashboard.

## Requirement-to-ticket coverage

`I` refers to Implementation Decisions and `T` to Testing Decisions in [spec.md:193](../snapshots/pre-remediation-2026-08-23/spec.md#L193) and [spec.md:426](../snapshots/pre-remediation-2026-08-23/spec.md#L426).

| Material requirement | Tickets | Status | Gap |
|---|---:|---|---|
| I1 delivery sequence | 01–16 | **conflicting** | Declared sequence exists, but Ticket 06 creates a real-evidence sequencing problem. |
| I2; T1–T3 aggregate repository seam and validation | 01, 02, 06, 07, 16 | **partially covered** | Ticket 01 is oversized; migration and trusted-history mechanics are underspecified. |
| I3–I5; T8 canonical single scan and stable outputs | 03, 05 | **covered** | Appropriate public command seam. |
| I6–I8 catalogue authority, schema and history | 01, 13, 16 | **partially covered** | General migrations and standard impact analysis lack ownership. |
| I9–I12; T4 claims, contracts, CE ceiling and mirror | 01, 08–12, 16 | **covered** | Mirror preservation is independently testable. |
| I13–I15 corpus provenance, discovery and blindness | 01, 04, 08–12 | **partially covered** | Blind-review workflow and all four discovery channels are not explicit. |
| I16–I18; T5, T7, T11 clusters, sampling, holdout and reductions | 01, 02, 08–12 | **missing** | No operational holdout sealing, reveal or replenishment owner. |
| I19–I20; T17 Karam evidence and refresh | 04, 15 | **partially covered** | WIP safety is strong; immutable milestone transition and complete refresh triggers are incomplete. |
| I21–I27; T6–T7, T18 scorecard and measurements | 01, 08–13 | **partially covered** | Synthetic Ticket 01 cannot prove real admission; large pilot populations exceed one context. |
| I28; T16 provisional benchmark | 02, 06 | **covered** | Correctly demoted to syntax/compatibility evidence. |
| I29–I31; T10–T11 coverage and templates | 03, 05 | **covered** | Live parser evidence supports the requirement. |
| I32–I34 lifecycle, changes and suspension | 01, 05, 13, 15 | **partially covered** | Urgent-advisory entry and upstream-parity retirement are not explicit. |
| I35–I36 atomic packets and approval | 08–13 | **conflicting** | Same-ticket final disposition does not model independent review and approval. |
| I37–I39 review cut and queue | 07, 13, 16 | **covered** | Dependency list is unnecessarily broad. |
| I40–I44 pilot, entry, exit and success | 07–13 | **conflicting** | Fixed membership contradicts substitution; Ticket 11 preselects its outcome. |
| I45; T19 Karam local and committed-tree rollout | 04, 14, 15 | **conflicting** | Authoritative CI/config/rule sources remain undecided. |
| I46 weekly compatibility schedule | 03, 15 | **missing** | Command and one scan exist; weekly execution has no owner. |
| I47; T15 engine upgrade | 06 | **conflicting** | Qualification occurs before non-synthetic acceptance evidence. |
| I48–I49; T9 gate failures and presentation | 05, 14 | **covered** | Failure conditions are explicitly bounded. |
| I50 baseline triage | 08–14 | **partially covered** | Feasible for blockers, but high-volume pilot tickets need sampling/review decomposition. |
| I51–I53; T12–T13 exceptions, override and rollback | 05, 15 | **covered** | Good separation and expiry semantics. |
| I54; T14 privacy | 04, 14, 16 | **covered** | Public/private output boundary is explicit. |
| I55; T20 first-wave completion | 15, 16 | **covered** | Correct stopping boundary if the earlier defects are repaired. |
| Live Karam rule/config sources | None | **missing** | App-local and Registry rules are outside the declared 61-rule authority. |

## Dependency review

### Declared frontier

The current graph has only **Ticket 01** ready:

`01 → {02,03} → {04,05} → 06 → 07 → {08,09,10,11,12} → 13 → 14 → 15 → 16`

Compatibility and advisory Karam scans are positioned early enough—Tickets 03 and 04 precede the review cut and pilot. Once their input authority is corrected, they can supply the intended pilot evidence.

### Incorrect or merely convenient edges

- `02 ← 01`: mostly convenient. Honest relabelling of the provisional benchmark can proceed independently; only admission of replacements needs governance.
- `06 ← 05`: Gate Evaluation is not required to pin the current engine.
- `07 ← 02,05,06`: these are governance conveniences, not necessary to freeze the cut. The genuine evidence dependencies are the governance schema, Compatibility Scan and Karam advisory scan.
- `15 ← 03`: transitively satisfied through Ticket 14; retaining it as a usage dependency is harmless but redundant.

### Missing dependencies or preconditions

- Candidate-engine qualification needs real pilot evidence or must be split from engine pinning.
- Tickets 08–12 need explicit independent-review availability and Vatsal-approval states.
- Ticket 14 needs a Vatsal-designated Karam CI file and resolved rule/config authority.
- Ticket 15 needs an actual milestone commit/pull request; it is an external observation gate, not immediately executable agent work.
- Pre-merge Evidence Packets need a defined immutable rule-tree identity.

### Slice quality

| Ticket | Assessment |
|---:|---|
| 01 | Horizontal, too large, and synthetic; not a genuine tracer bullet. |
| 02 | Small horizontal correction; independently verifiable. |
| 03 | Genuine vertical slice but large: scanner, target enumerator, parser normalisation, baseline and reporting should be internally staged. |
| 04 | Useful vertical slice and reasonably bounded after 03. |
| 05 | Vertical but too large; Gate Evaluation, exceptions/overrides and rollback are three demonstrable sub-slices. |
| 06 | Two slices incorrectly combined: pinning and later upgrade qualification. |
| 07 | Horizontal planning artefact, but independently verifiable once evidence exists. |
| 08 | Plausibly one context; current live match volume is small. |
| 09 | Too large: 222 current matches before clustering/sampling. |
| 10 | Too large: 194 current matches plus caller/role/domain review. |
| 11 | Too large: 639 current matches and runtime/query evidence. |
| 12 | Reasonably bounded at three current matches, but independent review must be separate. |
| 13 | Appropriate horizontal batch-close gate. |
| 14 | Genuine integration slice, but blocked by private WIP and unresolved CI authority. |
| 15 | Useful observational slice; depends on a real external milestone. |
| 16 | Appropriate first-wave release gate. |

The five candidates could ultimately receive defensible dispositions without manufacturing blockers, but not through the current one-ticket-per-candidate flow. The taxonomy legitimately limits a Performance Hypothesis to audit-only; embedding `audit/outside` in Ticket 11 before final claim review is still premature.

The wave stops at the right portfolio boundary: pilot, real observation, recalibrated queue, then another `to-tickets` pass. That next pass should create only the next bounded Review Batch, not tickets for the entire remaining portfolio.

## Live-state verification

### Revisions and worktrees

| Repository | Exact inspected state |
|---|---|
| Rules | `develop` at `24b6f6df8cbb57e599c92e88300c9bc8c66a4ffa`, equal to local `origin/develop`; 15 grouped status entries, or 9 tracked changes plus 62 untracked file paths. |
| Frappe | `version-16` at `9523516cac25992bc2cd810e1015df8994c257f5` (`v16.30.0`); clean, but ahead 1/behind 1 relative to the locally recorded `upstream/version-16` at `6a329d0…` (`v16.31.0`). No fetch was performed. |
| ERPNext | `version-16` at `21d187302045476f1ceb5d0d86219389ab1e75b8` (`v16.32.1`); one modified `banking/yarn.lock`; local tracking ref equal. |
| Karam Finance | `develop` at `c49398c9e2af3506ea1fe8a15d369afbab27b949`; no tracking branch recorded; 62 grouped entries, or 14 tracked changes plus 283 untracked file paths. Private WIP remained untouched. |

### Rules and tests

- Working tree: **61 rules** — 49 upstream, two backported, ten Noospheric.
- Immutable commit `24b6…`: **59 rules** — the two new untracked correctness/security rules are absent.
- `make test`: passed; configuration 61 rules; upstream 31/31, backports 2/2, custom 10/10.
- Mirror contract: all 24 upstream files byte-identical to recorded `b101a16e69df049b3fed1478bcc16223e957cca2`.
- Benchmark:
  - Semgrep 1.174.0: 17/17, 0.741 s, 0.023 s maximum rule time, 140.2 MiB.
  - Semgrep 1.172.0: 17/17, 0.870 s, 0.019 s maximum rule time, 154.8 MiB.
  - These remain authored-fixture regression results, not admission evidence.

### Engines and CI pins

- Active executable: `/opt/homebrew/bin/semgrep` **1.174.0**, `OSS`.
- Rules CI: `actions/checkout@v7`, full history, but `pip install semgrep` is unpinned.
- Committed Karam linter at HEAD: `checkout@v6`, `setup-python@v6`, `pre-commit/action@v3.0.0`, `actions/cache@v5`; Semgrep and cloned Frappe rules are unpinned; Registry alias is mutable.
- Untracked Karam `quality.yml`: Semgrep **1.172.0**, rules **`24b6…`**, but `r/python.lang.correctness` remains mutable.

### Current scan evidence

The current working 61-rule portfolio produced:

- 7,122 reported scanned paths;
- 4,675 Engine Matches: Frappe 1,873, ERPNext 2,791, Karam 11;
- eight parser failures: seven `PartialParsing`, one syntax error;
- five mixed/template JavaScript failures and three native-valid compatibility failures;
- no Karam parser failure.

Pilot match volumes were:

- `override-doctype-class`: 1;
- `frappe-sql-format-injection`: 222;
- `frappe-whitelisted-permission-bypass`: 194;
- `frappe-n-plus-one-read-in-loop`: 639;
- `frappe-async-array-callback-misuse`: 3.

There are 43 `nosemgrep` occurrences in Karam WIP, many using older rule IDs or bare suppressions; none confers approval.

The Semgrep proof-boundary decisions remain sound: current official documentation describes CE as per-file, taint tracking within a function or method, and generic mode as syntax-unaware with material limitations. [Semgrep glossary](https://docs.semgrep.dev/writing-rules/glossary), [taint overview](https://docs.semgrep.dev/writing-rules/data-flow/taint-mode/overview), [generic-mode limitations](https://docs.semgrep.dev/writing-rules/generic-pattern-matching).

### Historical observations

- **Still current at review time:** 61 working rules, 7,122 reported paths, eight parser failures, and the 11-match working-portfolio Karam scan all reproduced against unchanged source revisions.
- **Mis-scoped rather than stale:** the 11-match Karam observation excludes the app-local and Registry configurations and does not describe immutable Karam CI behaviour.
- **Stale/inaccurate wording:** Karam “currently relies on `--error`” applies only to untracked replacement CI, not committed HEAD.
- **Not current CI parity:** the immutable rules pin contains 59 rules, not the current 61-rule working tree.

No repository, ticket status, branch, index, application or source file was changed during the review. A temporary public-rules snapshot used to inspect the immutable pin was moved to Trash after use.

## Recommended corrections

1. Resolve the authoritative Karam workflow and complete rule-input set, including the local rule and Registry pack.
2. Define immutable identity for pre-merge candidate rules—PR commit SHA or complete content-addressed rule-tree hash.
3. Split Ticket 01 into bounded validator scaffolding and a real public source-backed tracer slice.
4. Split Ticket 06 into immediate pinning and post-pilot candidate-engine qualification; remove convenient dependencies from Ticket 07.
5. Make pilot membership provisional until entry gates pass; remove Ticket 11’s predetermined outcome.
6. Introduce explicit blind-label, holdout, independent-review and Vatsal-approval states; split high-volume evidence collection from final disposition.
7. Assign schema migration, standard impact analysis, holdout replenishment and weekly compatibility scheduling to named tickets.
8. Re-run the ticket-generation review only for this corrected first wave. Do not create later portfolio tickets yet.

## Go/no-go

**No-go. Ticket 01 should not begin now.**

The single next action is to resolve and record the **authoritative Karam Semgrep input/CI decision** against the live committed and WIP states. That decision determines the real portfolio boundary and is required before the spec and ticket DAG can be corrected safely.
