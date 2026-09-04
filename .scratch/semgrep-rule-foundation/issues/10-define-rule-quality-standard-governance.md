# Define Rule Quality Standard governance

Type: grilling
Status: resolved
Assignee: Noema
Blocked by: 07, 09

## Question

What artefact structure, ownership, review triggers, compatibility process, and
update workflow should keep the Rule Portfolio Catalogue, Ground-Truth Corpus,
Rule Quality Scorecard, and implementation route coherent over time?

## Answer

### Canonical artefacts

Governance remains a lightweight, version-controlled part of this repository.
The Rule Portfolio Catalogue, Rule Contracts, Evidence Packets, schema, and
decision history are reviewable repository files with links to immutable
external evidence. They do not require a database, governance application, or
encrypted snapshot system.

The catalogue contains exactly one authoritative entry for each Rule Claim.
Semgrep rule YAML, generated reports, CI configuration, and dashboards consume
that entry; none is a competing governance source. Generated views are
disposable and must be reproducible from the authoritative files.

The catalogue has an explicit schema version. A schema change requires a
reviewed migration and may not silently reinterpret existing fields or
decisions.

### Atomic changes and validation

Every governed change is one Governance Change Packet containing all affected
rule implementations, Rule Contracts, native tests, Evidence Packets,
catalogue decisions, and compatibility impacts. A rule-only change with
governance deferred to a later change is incomplete.

Before atomic merge, the packet must pass schema validation, native Semgrep
tests, affected Ground-Truth Corpus evaluation, and the compatibility and Scan
Health checks already defined by the Rule Quality Scorecard and CI enforcement
policy. Automation validates consistency but never substitutes for the
required independent review or approval.

### Stewardship and approval

Noospheric owns the Rule Quality Standard and governed artefacts. Vatsal
approves every change to the standard and every blocking admission,
re-admission, suspension reversal, or enforcement change. Monitor and audit
decisions require independent Noospheric review. No author may act as the
independent reviewer of the same Governance Change Packet.

Noema maintains the operational artefacts and may author or independently
review work Noema did not author. If Vatsal authors a packet, Noema may provide
the independent review; if Noema authors it, Vatsal or another authorised
Noospheric reviewer must review it. Vatsal remains the accountable human
approver wherever the standard or blocking behaviour changes.

### Evidence retention and history

Public evidence uses immutable commit identifiers, content hashes, source
anchors, and durable links. Private Karam Finance source, snippets, raw
findings, and reports remain access-controlled. Public catalogue entries refer
to them through opaque evidence identifiers and provenance without copying
private content into this repository.

Each catalogue entry exposes its current state while an append-only decision
history retains admissions, re-admissions, suspensions, exceptions,
replacements, and retirements with their dates and evidence. Corrections add a
superseding decision; they do not rewrite the earlier decision or its evidence.

### Standard evolution and freshness

A changed Rule Quality Standard governs new decisions immediately. Every
change includes an impact analysis identifying existing Accepted Rules whose
admission relied on the changed requirement. Only affected rules require
re-admission; unaffected rules are not ceremonially re-reviewed. An affected
Blocking Rule that no longer satisfies a required gate is suspended from
blocking until re-admitted.

Governance freshness reuses the established lifecycle and Corpus Refresh
triggers: material rule or policy changes, relevant Frappe or ERPNext changes,
new corpus snapshots, Semgrep engine or parser changes, new false positives or
missed positives, upstream replacements, milestone scans, compatibility scans,
and relevant security events. No separate governance-review calendar is
introduced.
