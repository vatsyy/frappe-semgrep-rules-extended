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
