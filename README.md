# Frappe Semgrep Rules Extended

Official Frappe Semgrep rules, preserved unchanged, with additional checks for
Frappe correctness, security and performance.

- `rules/upstream/frappe/`: the official mirror.
- `rules/backports/frappe-press/`: rules with recorded source provenance.
- `rules/custom/`: repository-owned checks and positive/negative fixtures.

See [UPSTREAM.md](UPSTREAM.md) for synchronisation and
[custom rule guidance](rules/custom/README.md) for contributions.

## Scan an application

```sh
semgrep scan --config ./rules /path/to/frappe-app
```

Use `--config ./rules/custom` to run only custom rules. Matches need contextual
review: a database call in a loop does not establish a performance problem, and
a security hotspot does not establish exploitability. The rules are advisory;
fixture tests do not establish real-world precision or recall.

For scans that record the source, engine, rules and analysis errors:

```sh
make scan-all-apps APPS_ROOT=/path/to/bench/apps SCAN_OUTPUT=scan-results/all-apps
```

See [scan instructions](scan/README.md) for immutable commits, current worktrees
and output details.

For repeatable rule tuning, use the [evaluation CLI](scan/README.md#repeatable-rule-evaluation):
`baseline` retains all application inputs, `compare` evaluates candidate rules on
the same source, and `inspect` shows findings with source context. Parser errors,
exclusions and rules with no matches remain visible in the results.

## Test and improve rules

The reproducible scanner and CI use Semgrep CE **1.174.0**. Install it in an
isolated environment, or use an existing installation of that version:

```sh
python3 -m venv .venv
.venv/bin/pip install semgrep==1.174.0
make test SEMGREP="$(pwd)/.venv/bin/semgrep"
```

`make test` checks metadata, duplicate rule IDs, upstream integrity, scanner
behaviour, the 17 authored regression cases, and Semgrep validation and fixtures.
Individual targets are `check-contract`, `test-scanners`, `test-benchmark`,
`validate`, `test-upstream`, `test-backports` and `test-custom`.

For a rule change, add positive and safe negative cases, run the tests, then
inspect matches and missed cases in relevant application code. Record useful
limitations alongside the rule or fixture. No catalogue, approval ledger or
review-batch workflow is required.
