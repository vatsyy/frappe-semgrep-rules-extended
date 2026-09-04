# 03: Enforce append-only history and schema migrations

**What to build:** Make governance history and schema evolution auditable so an
old decision cannot be deleted, reordered or silently reinterpreted by a new
validator.

**Blocked by:** 01: Validate catalogue and Rule Contract foundations; 02:
Validate evidence, holdout and review states.

**Status:** proposed — independent wave review and renewed Vatsal approval required.

- [ ] Admissions, suspensions, exceptions, standard impacts, holdout events,
      replacements and retirements form a validated append-only journal chain.
- [ ] Repository acceptance rejects mutation, deletion, reordering, broken
      predecessor links and reuse of a retired identity.
- [ ] A migration declares source and target schema versions, validates both,
      emits deterministic output and appends its decision instead of rewriting.
- [ ] Every migration emits an impact manifest naming affected rules, packets,
      evidence and generated consumers.
- [ ] Standard or schema changes suspend affected blockers until migrated and
      re-admitted while leaving demonstrably unaffected decisions valid.
- [ ] Valid and invalid migration fixtures exercise rollback and recovery without
      mutating the Frappe Upstream Mirror.
