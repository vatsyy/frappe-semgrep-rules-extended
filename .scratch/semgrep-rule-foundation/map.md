# Establish a trustworthy Semgrep rule foundation

Label: wayfinder:map
Status: resolved

## Destination

Produce a decision-complete Rule Quality Standard and improvement route for the
current Rule Portfolio, so later implementation can proceed without reopening
foundational questions about claims, evidence, evaluation, enforcement, or
rollout.

## Notes

- This map plans; it does not change production rules, CI, or application code.
- Initial scope is the current 61-rule portfolio across Frappe, ERPNext, and
  Karam Finance: Python, JavaScript, JSON, and known Jinja parsing boundaries.
- Blocking rules are precision-first; monitor rules represent credible policy
  or medium-confidence concerns; audit rules are recall-first hotspots.
- Ground truth is labelled independently of rule output. Synthetic reductions
  require a source-backed parent case and preserved decisive behaviour.
- Karam Finance is a read-only corpus. Its WIP must not be copied verbatim into
  publishable fixtures or modified by this effort.
- `rules/upstream/frappe/` remains byte-identical. Every new or mutated rule is
  Noospheric-owned and structurally separate, with provenance and distinct
  value; upstream contribution is optional.
- Static performance matches remain audit-only until runtime evidence proves
  scaling behaviour.
- Consult `CONTEXT.md` and use `wayfinder`, `grilling`, `domain-modeling`, and
  `research` as directed by each ticket.

## Decisions so far

- [Define the Rule Claim taxonomy](issues/01-define-rule-claim-taxonomy.md): Established one-claim classes, bounded proof and enforcement ceilings, reviewed dispositions, complete contracts, and catalogue-based upstream governance.
- [Research defensible static-rule evaluation methods](issues/03-research-static-rule-evaluation-methods.md): Established an independent claim-centred oracle, stratified measurement with uncertainty, separate coverage and ambiguity, and explicit reviewer-cost evidence.
- [Research Semgrep Community Edition proof boundaries](issues/02-research-semgrep-ce-proof-boundaries.md): Bounded CE to local parsed structural and same-function taint claims, with explicit whole-program and mixed-template coverage limits.
- [Define the Ground-Truth Corpus protocol](issues/04-define-ground-truth-corpus-protocol.md): Established rolling immutable snapshots, source-backed blind labels, cluster sampling and holdouts, independent review, private-WIP limits, and refresh rules.
- [Audit the provisional benchmark cases](issues/05-audit-provisional-benchmark-cases.md): Found zero independently admissible cases unchanged; eleven need source-backed replacement, three remain useful unresolved boundaries, and three unsupported security assertions must leave acceptance evidence.
- [Define the Rule Quality Scorecard](issues/06-define-rule-quality-scorecard.md): Established non-compensating admission gates and evidence-based blocking, monitor, audit, and outside-portfolio outcomes without inventing a composite score or new infrastructure.
- [Define the Rule Lifecycle policy](issues/07-define-rule-lifecycle-policy.md): Established Noospheric stewardship, immutable upstream ownership, evidence-gated states, deterministic change actions, freshness triggers, suspension, and permanent retirement history.
- [Decide parsing-gap handling](issues/08-decide-parsing-gap-handling.md): Established an independent target inventory, non-clean partial parses, ratcheting coverage baselines, blocking-scope completeness, and audit-only mixed-template fallbacks.
- [Decide CI enforcement and rollout](issues/09-decide-ci-enforcement-and-rollout.md): Established mandatory full Karam scans, deterministic catalogue-based gating, progressive all-rule review, compatibility scans, bounded exceptions, private evidence, and reversible enforcement.
- [Define Rule Quality Standard governance](issues/10-define-rule-quality-standard-governance.md): Established canonical version-controlled governance, atomic change packets, independent approval, immutable evidence and history, targeted re-admission, and shared freshness triggers.
- [Define the existing-rule review order](issues/11-define-existing-rule-review-order.md): Established a latest-source finite review cut, five-claim pilot, dynamic risk and evidence queue, bounded batches, explicit entry and exit gates, and load-aware enforcement cadence.
- [Resolve Karam Semgrep input and CI authority](issues/13-resolve-karam-semgrep-input-authority.md): Established the governed catalogue as the sole blocking input, retained Karam-local and Registry rules as separate advisory lanes, split current engine pinning from post-pilot qualification, and kept private workflow integration behind an explicit milestone authorisation.

## Not yet specified

- None. The route to implementation is decision-complete.

## Out of scope

- Production-rule, CI, Frappe, ERPNext, or Karam Finance changes during this
  map.
- New TypeScript, Vue, Bash, Dockerfile, or GitHub Actions rule portfolios.
- Beads, Codex Desktop, or repository-agent setup.
- [Decide broad-rule remediation routes](issues/12-decide-broad-rule-remediation-routes.md): Rule-specific retain, narrow, split, taint, audit, or retirement choices require completed Evidence Packets and belong to Portfolio Review implementation rather than this foundation map.
