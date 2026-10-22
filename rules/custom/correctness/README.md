# Frappe correctness rules

These rules detect framework-adjacent language mistakes and flag concrete
reliability risks for review. Keep `ERROR` findings limited to patterns whose
semantics are wrong regardless of data volume.

## Modernisation checks

`modernisation.yml` adds four advisory rules, with no automatic fixes:

| Rule | Coverage and intended response |
| --- | --- |
| `frappe-synchronous-browser-request` | Explicit `async: false` in `frappe.call`, `$.ajax` and `jQuery.ajax`. Move to asynchronous completion and error handling; removing the flag alone can break dependent code. |
| `frappe-requests-without-timeout` | Direct Requests HTTP methods with no timeout or `timeout=None`. Set appropriate connect/read timeouts. Calls forwarding unknown `**kwargs` are excluded unless `None` is explicit; custom sessions and wrappers are outside scope. |
| `frappe-read-modify-write` | Adjacent three-argument `frappe.db.get_value` and `frappe.db.set_value` calls that add or subtract from the same record and field, including an intervening `+=` or `-=`. Review atomic updates or transaction locking while preserving document hooks. Reads using `for_update` are outside this narrow pattern. |
| `frappe-enqueue-after-write` | Adjacent explicit database write/delete and `frappe.enqueue`/`enqueue_doc` calls inside a function. Review whether the job depends on the write, and defer until commit if it does. Covers omitted commit policy in ordinary functions and explicit `False` in functions or controllers. The upstream rule retains controller coverage for omitted policy. |

The transaction checks intentionally do not follow intervening operations,
helper calls or arbitrary document methods. Their absence does not establish
concurrency safety. Locks acquired elsewhere and jobs unrelated to the preceding
write can make a finding intentional. Immediate execution, unknown forwarded
enqueue options and explicit commit policies other than `False` are excluded.
Deferring enqueue until commit does not guarantee delivery if enqueue itself
fails after the database commits.

Run `make test SEMGREP='uv tool run --from semgrep==1.174.0 semgrep'` from the
repository root. Same-basename Python and JavaScript fixtures exercise both
reported patterns and their safe or deliberately unsupported neighbours.

## Python 3.14 compatibility

`tests/test_python314_compatibility.py` scans a dedicated fixture through the
complete custom rule tree. It requires clean parsing and retained findings for
PEP 695 type aliases and generics, deferred forward-reference annotations, and
exception clauses without brackets. It also verifies a bounded Requests call
remains unreported.

Template strings have a separate expected-failure fixture because Semgrep CE
1.174.0 partially parses the `t"..."` prefix when the Requests timeout rule is
active in the same module. The compatibility test makes that interaction
visible without claiming complete rule coverage. Remove the expected-failure
marker only after a qualified engine parses the fixture without Scan Health
warnings; an unexpected pass deliberately fails the suite and prompts review.
