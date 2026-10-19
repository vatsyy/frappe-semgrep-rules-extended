# Frappe Semgrep Rules Extended

**The official Frappe Semgrep rules, unchanged—plus Frappe-aware rules refined
against real application code.**

This repository is an evidence-led extension of
[Frappe's official Semgrep rules](https://github.com/frappe/semgrep-rules). It
retains the upstream rules byte-for-byte while adding separately owned checks
for correctness, security and performance problems encountered in
production-style Frappe applications.

It is intended for teams that want broader coverage without turning every
suspicious syntax pattern into a failed build.

## Why this exists

Semgrep rules can be syntactically valid, thoroughly fixture-tested and still
produce poor results on real applications.

Frappe adds framework-specific semantics that generic Python and JavaScript
rules often miss:

- Whitelisted methods create remote-call trust boundaries.
- Frappe permission APIs do not all provide equivalent protection.
- Database calls inside loops may be expensive—or explicitly bounded and
  harmless.
- Raw SQL construction may be safe structural assembly or attacker-controlled
  interpolation.
- Template rendering depends on paths, globals and caller-controlled context.
- Async JavaScript callbacks may create completion races or be intentional
  background work.

This fork evaluates those distinctions explicitly.

## Why use this instead of only the standard rules?

You do not lose the standard rules. The repository contains an immutable mirror
of them and keeps every extension in a separate ownership namespace.

| Capability | Standard Frappe rules | This repository |
| --- | --- | --- |
| Official Frappe rules | Yes | Yes, unchanged |
| Independent upstream synchronisation | — | Yes |
| Additional Frappe-specific rules | Limited | Yes |
| Provenance-labelled Press backports | No | Yes |
| Positive and negative rule tests | Yes | Required |
| Real-application scan evidence | Not supplied as a portfolio contract | Recorded per rule review |
| Exact source, engine and ruleset identity | Limited | Recorded for canonical scans |
| Parser and Scan Health reporting | Limited | Separate from findings |
| Rule-by-rule enforcement decisions | No | Catalogue governed |
| Protection against noisy rules becoming blockers | No formal admission gate | Mandatory review gate |

Choose the official repository when you want only Frappe-maintained policy with
minimal machinery.

Choose this repository when you want the official rules **plus broader Frappe
coverage, reproducible scans and evidence showing what each reviewed rule
actually finds.**

## Current rule coverage

The current development portfolio contains **72 rules** across:

```text
rules/
├── upstream/frappe/        # Byte-identical Frappe upstream mirror
├── backports/frappe-press/ # Provenance-labelled rules awaiting adoption
└── custom/
    ├── correctness/
    ├── performance/
    └── security/
```

Custom coverage currently includes patterns such as:

- async callback completion races;
- N+1 reads in loops and comprehensions;
- malformed SQL placeholder lists;
- whitelisted methods performing raw SQL;
- direct Python `eval` and `exec`;
- dynamic template rendering with unrestricted globals;
- ignored permission-check results;
- subprocess execution and `shell=True`;
- Frappe controller override compatibility risks.

A custom rule is never represented as an upstream Frappe rule. See
[`UPSTREAM.md`](UPSTREAM.md) for the synchronisation procedure and
[`rules/custom/README.md`](rules/custom/README.md) for the custom-rule contract.

## Evidence from real Frappe applications

The rules have been exercised across seven applications in a live Bench
workspace, including Frappe, ERPNext and custom applications.

The recorded scan covered:

- **8,479 fully analysed targets**
- **14 partially analysed targets**
- **0 unanalysed targets**
- **3 intentionally excluded targets**

Parser gaps are retained as first-class Scan Health evidence. They are not
silently discarded or counted as clean files.

Real-code review has already demonstrated why this matters:

| Original rule population | Refined claim | Before | After |
| --- | --- | ---: | ---: |
| Broad code-injection/evaluation matching | Direct Python `eval` or `exec` | 53 | 5 |
| Broad template-injection matching | Dynamic templates with default globals | 75 | 40 |
| Any permission call in a suspicious position | Actually discarded permission result | 3 | 0 |

These reductions do not mean the removed findings were ignored. They mean
materially different behaviours were separated into correctly named claims
instead of being reported as the same defect.

The associated evidence is available under
[`governance/review-batches/`](governance/review-batches/).

## Findings are claims, not verdicts

A match may identify:

- a confirmed defect;
- a security or performance hotspot requiring contextual review;
- an intentional framework boundary;
- compatibility debt;
- a safe bounded operation;
- or a rule mismatch.

Consequently:

- Semgrep severity alone does not determine whether CI fails.
- `semgrep --error` is not used as a substitute for rule governance.
- High-volume or incompletely reviewed rules cannot become blockers.
- Performance findings require runtime evidence before performance impact is
  asserted.
- Security findings require authorisation or dataflow review before
  exploitability is asserted.

The current admission state is recorded in
[`governance/catalogue.json`](governance/catalogue.json).

## Run the rules

Install Semgrep and scan an application with the complete ruleset:

```shell
semgrep scan --config ./rules /path/to/frappe-app
```

The ownership boundary also supports selective scans:

```shell
# Frappe-owned rules only
semgrep scan --config ./rules/upstream/frappe /path/to/frappe-app

# Repository-owned rules only
semgrep scan --config ./rules/custom /path/to/frappe-app

# Provenance-labelled backports only
semgrep scan --config ./rules/backports /path/to/frappe-app
```

## Reproducible scans

Scan every application in a Bench while retaining current tracked and
non-ignored untracked work:

```shell
make scan-all-apps \
  APPS_ROOT=/path/to/bench/apps \
  SCAN_OUTPUT=scan-results/all-apps
```

Canonical scans record:

- Semgrep engine version;
- complete ruleset content hash;
- source commit or worktree content hash;
- catalogue identity;
- exclusions and resource settings;
- deterministic findings;
- parser and analysis failures;
- per-application Scan Health.

Worktree mode includes modified and non-ignored untracked application files
without modifying the source repository. This makes it suitable for milestone
and pre-PR scans of active migration work.

For immutable public source snapshots, see [`scan/README.md`](scan/README.md).

## Testing

```shell
make test
```

The complete verification seam includes:

- rule metadata and ownership contracts;
- upstream mirror integrity;
- governance-schema validation;
- benchmark-contract tests;
- scan and provenance contracts;
- comparison tests;
- pilot and review-batch evidence checks;
- Semgrep rule validation;
- positive and negative tests for upstream, backported and custom rules.

Focused targets include:

```shell
make check-contract
make check-governance
make validate
make test-upstream
make test-backports
make test-custom
```

The repository is currently qualified against **Semgrep CE 1.174.0**. Engine
upgrades require compatibility evidence rather than an unrecorded version
change.

## Trust model

Every governed rule must answer five questions:

1. What precise behaviour does it claim to detect?
2. What real source evidence supports that claim?
3. What are its known safe cases and blind spots?
4. Has someone other than the author reviewed the evidence?
5. What is the highest enforcement level justified by that evidence?

Until those conditions are met, a rule remains advisory regardless of how
serious its message sounds. The contracts and evidence model are documented in
[`governance/README.md`](governance/README.md).

## Project status

This repository is under active portfolio review.

The current rules and scanning infrastructure are usable for **advisory
analysis**. Not every inherited or newly authored rule has completed independent
review, and no incomplete review should be presented as proof of
production-blocking precision.

That limitation is deliberate: trust is earned rule by rule, not inferred from
a green test suite or a large rule count.
