# Resolve Karam Semgrep input and CI authority

Type: decision
Status: resolved
Approved by: Vatsal
Approved on: 2026-08-23
Triggered by: [second-pass readiness review](../../trustworthy-semgrep-foundation/audits/second-pass-readiness-review-2026-08-23.md)

## Context and decision

Karam's committed linter and private replacement-CI WIP use different engines,
rule revisions and failure behaviour. The replacement workflow is the intended
future integration target, but it still combines a pinned rules-repository
revision with a mutable Registry pack and an app-local rule outside the governed
catalogue. Treating that mixture as one authoritative scan would make
reproduction and catalogue-based gating false.

The governed rules-repository catalogue is therefore the sole blocking input.
The Karam-local rule and Registry pack remain separate advisory lanes until each
is explicitly imported through governance and identified by immutable content.
No mutable Registry alias may participate in Gate Evaluation. Private untracked
`quality.yml` remains read-only until Vatsal separately names and authorises the
integration file and milestone.

Rules-repository CI pins Semgrep CE 1.174.0, the engine used for the verified
live scan. Karam remains on 1.172.0 until post-pilot qualification exercises
real Evidence Packets, canonical public scans and both Karam scan modes. Every
pre-merge rules input uses an immutable pull-request commit SHA or a content hash
covering the complete rule tree.

## Consequences

- Auxiliary Karam findings remain visible but cannot fail the workflow or count
  as admission evidence merely because their current configuration runs them.
- Ticketed integration cannot silently drop the local or Registry lanes, promote
  them, or edit private Karam WIP before the explicit milestone gate.
- Engine pinning can proceed immediately; engine alignment and upgrades wait for
  real post-pilot evidence.
- Importing an auxiliary rule later requires ownership, provenance, contract,
  tests, evidence and a normal catalogue decision.
