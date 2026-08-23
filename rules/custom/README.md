# Custom rules

This directory contains rules maintained by this repository. It is separate
from the relocated Frappe rules under `rules/upstream/frappe/` so provenance is
visible in both the filesystem and review history.

Organise rules by the problem they detect. Add a category only with its first
rule; do not retain empty category directories.

Each ruleset must:

- keep its YAML and same-basename test targets together;
- use stable, repository-owned rule IDs;
- include `metadata.origin: custom`;
- declare an appropriate `metadata.category`, `metadata.technology`, and
  `metadata.confidence`;
- contain positive and negative fixtures; and
- pass both `make test-custom` and `make test`.

`make check-contract` enforces these ownership and fixture requirements. It
also proves that `rules/upstream/frappe/` remains identical to the revision
recorded in `UPSTREAM.md`.

Do not edit or duplicate Frappe-owned rules here. If a Frappe rule needs a
general improvement, contribute it upstream; if local policy must intentionally
differ, create a separately named custom rule and document the distinction.
