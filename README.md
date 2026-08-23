# Frappe Semgrep Rules Extended

Semgrep rules for Frappe applications, combining an organised mirror of
[Frappe's rules](https://github.com/frappe/semgrep-rules) with locally maintained
extensions.

## Rule ownership

```text
rules/
├── upstream/
│   └── frappe/       # Relocated mirror of frappe/semgrep-rules
├── backports/
│   └── frappe-press/ # Publishing-audit rules pending shared upstream adoption
└── custom/
    ├── correctness/  # Deterministic framework-adjacent language defects
    ├── performance/  # Database, queue and client-request scaling risks
    └── security/     # Permission bypasses at remote-call boundaries
```

Files under `rules/upstream/frappe/` retain Frappe's relative layout and should
only change through an upstream synchronisation. Repository-owned rules belong
under a purpose-based category in `rules/custom/`. Rules sourced from another
Frappe repository while awaiting adoption by `frappe/semgrep-rules` belong in
`rules/backports/` with their source revision recorded.

See [UPSTREAM.md](UPSTREAM.md) for the synchronisation procedure and
[rules/custom/README.md](rules/custom/README.md) for the custom-rule contract.

## Run the rules

Install Semgrep and scan an application with the combined ruleset:

```shell
semgrep scan --config ./rules /path/to/frappe-app
```

The ownership boundary also supports selective scans:

```shell
# Frappe-owned rules only
semgrep scan --config ./rules/upstream/frappe /path/to/frappe-app

# Repository-owned rules only
semgrep scan --config ./rules/custom /path/to/frappe-app

# Backported Frappe publishing-audit rules only
semgrep scan --config ./rules/backports /path/to/frappe-app

# One custom category
semgrep scan --config ./rules/custom/performance /path/to/frappe-app
```

Use `--severity=ERROR` when a scan should report only error-level findings.

## Test the rules

```shell
make test
```

Additional targets are available for focused verification:

```shell
make check-contract
make check-governance
make validate
make test-upstream
make test-backports
make test-custom
```

Every rule must have positive and negative test cases. Test targets remain next
to their rules and use the same basename so Semgrep can associate them. The
contract check also rejects duplicate IDs, incomplete ownership metadata and
any byte-level change to the recorded Frappe upstream mirror.

## Add a custom rule

1. Choose an existing purpose-based directory under `rules/custom/`, or create
   one when introducing the first rule in a new category.
2. Add the rule YAML and its same-basename test targets.
3. Give the rule a stable, repository-owned ID and provenance metadata.
4. Run `make test-custom` and `make test`.

Read Semgrep's [rule-writing overview](https://semgrep.dev/docs/writing-rules/overview/)
and [testing documentation](https://semgrep.dev/docs/writing-rules/testing-rules/)
before contributing a new rule.
