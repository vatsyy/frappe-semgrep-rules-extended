# Regression cases

These 17 authored cases exercise the complete ruleset together. They complement
same-basename Semgrep fixtures beside each rule. They measure syntax behaviour,
not real-world precision, recall or application performance.

`manifest.json` maps each case to its exact expected rule IDs, an explanation
and its recorded provenance. Empty findings mean no rule should match. The
runner fails on missing or unexpected matches, missing cases and analysis errors.

```sh
make test-benchmark
```
