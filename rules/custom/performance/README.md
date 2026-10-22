# Frappe performance rules

These rules identify database, queue and client-request patterns whose cost can
grow with the size of an iteration. They are warnings and review leads, not
proof that a path has an N+1 query or request defect.

Keep this directory separate from the relocated Frappe rules under
`rules/upstream/frappe/`. Validate changes from the repository root:

```bash
semgrep --validate --config rules/custom/performance/frappe_performance.yml
semgrep --test --strict --config rules/custom/performance/frappe_performance.yml \
  rules/custom/performance/frappe_performance.py
semgrep --test --strict --config rules/custom/performance/frappe_performance.yml \
  rules/custom/performance/frappe_performance.js
```

Before promoting a rule to `ERROR`, review its baseline across Frappe apps and
add a runtime query-count or request-count test for every intentional exception.
The N+1 rule deliberately excludes the query that produces a loop iterable and
the dictionary form of `frappe.get_doc`, which constructs a new document
without reading one from the database.

## Reads in loop conditions

`frappe-n-plus-one-read-in-loop` also matches `if`/`elif` predicates in
`for`/`while` bodies for its existing named read APIs, including `db.exists`,
`db.get_value`, `db.count` and list queries. Negation, comparisons and boolean
guards can still contain repeated reads. The fixtures mirror ACF's
`clear_expired_logs` and `_ensure_custom_fields_from_dir`, which check
`frappe.db.exists("DocType", doctype)` before processing each configured DocType.

Safe negatives include a query before a loop, a query producing the iterable,
membership checks against prefetched names, unrelated `exists` methods and
in-memory document construction. The predicate uses Semgrep's
[deep expression operator](https://semgrep.dev/docs/writing-rules/pattern-syntax/#deep-expression-operator).

These are structural review hotspots. Guards can skip reads; caching, fixed
configuration and chunked bulk lookups can make matches intentional. The rule
does not establish reachability, query counts, data volume or a performance
defect. This extension does not add coverage for `while` headers, helper calls,
aliases or reads across function boundaries. SQL/document-read patterns and
test/patch exclusions remain as before; comprehension reads have a separate rule.
