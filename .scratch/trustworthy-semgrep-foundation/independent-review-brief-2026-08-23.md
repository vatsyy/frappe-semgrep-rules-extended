# Independent review brief: corrected Semgrep foundation wave

This is an operational hand-off, not a source of truth. Review the corrected
foundation plan read-only and decide whether it is ready for Vatsal's explicit
implementation approval.

## Boundaries

- Do not edit files, ticket states, Git state, Frappe, ERPNext, Karam Finance or
  the rules implementation.
- Do not update or pull any local application.
- Preserve every tracked and untracked worktree change.
- Treat Karam WIP as private and read-only.
- Treat repository and linked artefacts as primary sources; authored Semgrep
  fixtures are not independent truth.
- Verify volatile facts against the live state only where they affect the
  readiness decision, and label historical observations rather than rewriting them.

## Read completely

1. `CONTEXT.md`.
2. `.scratch/semgrep-rule-foundation/map.md`, every linked decision including
   `issues/13-resolve-karam-semgrep-input-authority.md`, and the supporting
   research and audits in that foundation directory.
3. `.scratch/semgrep-rule-foundation/spec.md`.
4. `.scratch/trustworthy-semgrep-foundation/issues/README.md` and all 28 current
   ticket files.
5. `.scratch/trustworthy-semgrep-foundation/audits/second-pass-readiness-review-2026-08-23.md`.
6. The non-canonical pre-remediation snapshot only to verify that earlier
   findings were repaired without erasing their evidence.
7. Current repository contracts and read-only Frappe, ERPNext and Karam
   integration context, including applicable `AGENTS.md` instructions.

## Required checks

1. Confirm the approved Karam decision is internally consistent across the map,
   decision record, spec and Tickets 09, 25–27.
2. Confirm the spec still faithfully collapses every resolved Wayfinder decision
   and clearly identifies the new user-approved decision.
3. Rebuild the requirement-to-ticket matrix for all 55 implementation and 20
   testing decisions; identify anything missing, partial, duplicated or conflicting.
4. Verify every dependency edge. Distinguish genuine blockers from sequencing
   conveniences and confirm the `{01,04,05}` initial frontier.
5. Judge whether each ticket is bounded, independently demonstrable and suitable
   for one fresh implementation context or an explicit external human gate.
6. Scrutinise Tickets 01–03 for horizontal overreach and confirm the first real
   end-to-end proof is the public source-backed tracer across Tickets 14–15.
7. Confirm holdout commitment, freeze, reveal, replenishment, disagreement
   retention, packet states, author/reviewer separation and Vatsal approval are
   operational rather than prose-only.
8. Confirm current engine pinning is independent of post-pilot qualification and
   no authored fixture can qualify an engine upgrade.
9. Confirm Compatibility and advisory Karam evidence precede pilot activation,
   while weekly scheduling does not create an artificial pilot blocker.
10. Confirm provisional pilot members can be deferred and substituted without
    predetermined outcomes or hidden reviewer burden.
11. Assess reproducibility, schema migration, append-only history, immutable
    pre-merge inputs, parser coverage, exception expiry, rollback, privacy and
    Karam worktree safety.
12. Confirm the first wave ends after real Karam and public observation and that
    only the next bounded Review Batch proceeds to another `to-tickets` pass.

## Output

Choose exactly one verdict:

- Ready for Vatsal implementation approval
- Ready after minor corrections
- Not ready; planning defects remain

Then provide only substantive findings ordered P0–P3, a compact corrected
requirement-to-ticket matrix, dependency and slice review, any stale live-state
observations, the smallest required corrections, and a final go/no-go for
Vatsal's implementation approval.
