# Compatibility benchmark

This runner checks authored fixtures for rule syntax, engine compatibility and
performance regressions. It is not a Ground-Truth Corpus, does not measure Rule
Confidence, precision or recall, and cannot admit a rule or justify blocking.

Each case in `manifest.json` records:

- its compatibility-fixture role and exact observed engine versions;
- provenance and the reason for its authored expectation;
- the findings that should and should not be produced;
- its audited disposition; and
- an explicit `admission_eligible: false` boundary.

The case audit found that none of the 17 fixtures qualifies unchanged as
acceptance evidence:

- eleven require source-backed replacements;
- three remain unresolved boundaries; and
- three remain syntax regressions only because their asserted security facts
  are unsupported.

Source-backed replacements enter the separate governance and evidence workflow
with immutable provenance, blind review and holdout handling. They are never
silently promoted from this manifest.

Run the benchmark with the active Semgrep installation:

```shell
python3 benchmarks/run.py
```

To exercise another installation, provide its command:

```shell
python3 benchmarks/run.py --semgrep-command /path/to/semgrep
python3 benchmarks/run.py --semgrep-command "uvx --from semgrep==1.172.0 semgrep"
```

The runner rejects admission language, mutable engine labels, unlisted or
missing findings, parse errors, duplicate paths and unregistered fixtures. It
retains whole-scan, per-rule matching, memory and process timeout guards.
Production rules remain under `rules/`; fixtures must not enter the immutable
`rules/upstream/frappe/` mirror.
