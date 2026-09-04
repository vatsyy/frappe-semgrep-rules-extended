# 29: Prepare the host-boundary Review Batch

**What to build:** Complete one vertical authored review of
`frappe-security-file-traversal` and `frappe-subprocess-exec`: current-source
identity, match and suppression frame, source-backed cases, rule-independent
near-miss and missed-positive search, authored dispositions, supported rule and
fixture changes, compatibility impact, scan evidence and a frozen blind packet.

**Blocked by:** Approved Batch 01 adjudication at
`governance/review-batches/batch-01/adjudication-v1.json`.

**Status:** resolved — authored evidence and the blind packet were frozen on
2026-08-26; the full repository gate passes.

- [x] Assume Vatsal has already updated the local apps; record their exact current
      revisions, content hashes and worktree-status hashes without updating or
      modifying any application repository.
- [x] If current source or rule identities differ from the retained Batch 01 scan,
      refresh the read-only seven-app scan before constructing evidence. Otherwise
      record and reuse the matching immutable provenance.
- [x] Reconcile all 176 file-traversal findings and its one suppression, plus the
      complete census of all 16 subprocess findings, against the canonical scan.
- [x] Select 24–44 file-traversal contexts deterministically by application,
      filesystem operation, path construction and trust-boundary cluster. Together
      with the subprocess census, the blind packet contains 40–60 cases. Record the
      population, inclusion method and blocking-ineligible sampling ceiling.
- [x] Search independently for real safe near-misses and missed positives for both
      claims. A generic `open`, `Path` or subprocess call is not labelled traversal,
      injection or exploitability without the decisive source and boundary evidence.
- [x] Write authored evidence and dispositions before revealing any independent
      label. Narrow, split, replace or retire only where reviewed real code supports
      it; do not manufacture a successor merely to preserve a rule count.
- [x] Any Noospheric rule change includes native positive and negative fixtures and
      a current seven-app comparison. `rules/upstream/frappe/`, application sources
      and Karam WIP remain untouched.
- [x] Freeze a rule-ID-free blind input, opaque mapping commitment, result template
      and their hashes. Suppression annotations and authored judgements are removed
      from the blind context.
- [x] Record authoring minutes, selected case count, unresolved cases and unique
      semantic issues. Do not infer missing reviewer minutes from wall-clock time.
- [x] `make test`, the rule-tree contract and `git diff --check` pass before Ticket
      30 starts.
