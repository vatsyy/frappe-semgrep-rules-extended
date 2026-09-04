# Provisional benchmark case audit

Audit date: 2026-08-22  
Scope: the 17 cases in `benchmarks/manifest.json`  
Method: the accepted Ground-Truth Corpus protocol

This audit changes no benchmark cases, rules, CI, Frappe, ERPNext, or Karam
Finance source. It is a first review, not corpus admission; the required blind
second review has not occurred.

## Evidence frame

- Frappe snapshot: `9523516cac25992bc2cd810e1015df8994c257f5`
- ERPNext snapshot: `21d187302045476f1ceb5d0d86219389ab1e75b8`
  (the unrelated `banking/yarn.lock` worktree change does not affect cited
  files)
- Karam Finance base: `c49398c9e2af3506ea1fe8a15d369afbab27b949`;
  active source remains mutable WIP and is exploratory only
- Active compatibility run: all 17 draft cases passed on Semgrep CE 1.174.0 in
  0.630 seconds, with a 0.012-second maximum per-rule match and 155.7 MiB
  measured memory

Rule scans were used only to locate candidates. Labels below come from source
review against the Rule Claim boundaries, never from whether Semgrep matched.

## Result

| Verdict | Cases | Meaning |
| --- | ---: | --- |
| Qualify unchanged | 0 | No case presently satisfies the admission protocol unchanged. |
| Source-backed replacement | 11 | A defensible public parent exists, or the real parent/fix must replace the current invented reduction. |
| Useful unresolved boundary | 3 | Preserve the investigation, but do not score or enforce it yet. |
| Remove from acceptance corpus | 3 | No admitted source establishes the asserted security fact; retain only as rule-local syntax regression if useful. |

Passing the runner therefore proves that the current patterns behave as
expected on their authored fixtures. It does not estimate precision, recall,
or blocking reliability.

## Case-by-case verdicts

| Case | Verdict | Evidence and required action |
| --- | --- | --- |
| `correctness.async-array-callback.broken-total` | Source-backed replacement | Replace the invented total calculation with a reduction of ERPNext `accounts/doctype/sales_invoice/sales_invoice.js:1109`-`1123`. `set_timesheet_data` appends child rows after awaited exchange-rate calls, while totals are triggered immediately after `forEach`; the lifecycle and row mutation are decisive. |
| `correctness.async-array-callback.awaited` | Source-backed replacement | The arithmetic `Promise.all` example is not a safe boundary for the Sales Invoice lifecycle and may change child-row ordering. Derive the negative from the actual correction or a real equivalent lifecycle; a sequential `for...of` is the likely reduction but cannot become truth before the source behaviour is resolved. |
| `performance.async-array-callback.fire-and-forget` | Source-backed replacement | Replace the invented `frappe.call` cache warmer with Frappe `public/js/frappe/views/reports/report_view.js:149`-`174`. Its async callback performs independent link-title DOM enrichment; it is a real non-blocking boundary for the correctness claim, while any request fan-out remains a separate performance hypothesis. |
| `security.shell.user-controlled` | Remove from acceptance corpus | The fixture is a rule-shaped function parameter, not an admitted request source or historical defect. A parameter named `user_value` does not independently establish attacker control. Keep it only as a syntax/taint regression until a real source-backed parent exists. |
| `security.shell.constant-policy` | Source-backed replacement | Use Frappe `commands/testing.py:488`-`494`, which executes a literal subshell to locate the Yarn binary. This supports a shell-use policy case, not command-injection proof; label it `policy-only` and cap it at monitor. |
| `security.shell.argument-list` | Source-backed replacement | Use Frappe `installer.py:819`-`821`, which invokes `tar` with an argument list. It is a real process-execution Review Hotspot and a shell-interpretation negative boundary, not an invented `git status` example. |
| `security.authorisation.permission-bypass` | Useful unresolved boundary | The structural fact—whitelisted code calling `get_all` or ignoring permissions—does not prove missing endpoint authorisation. ERPNext `accounts/custom/address.py:58`-`79` and an active Karam WIP candidate show why caller, role, record, and framework context must be reviewed. Remove the current blocking expectation; promote only after a stable source label and domain-owner review. |
| `security.authorisation.permission-aware` | Source-backed replacement | Use ERPNext `accounts/doctype/payment_entry/payment_entry.py:2736`-`2745`: it explicitly checks Payment Entry permission and uses `get_list` with `reference_doctype`. The current generic Account example omits the decisive permission context. |
| `security.sql.value-interpolation` | Remove from acceptance corpus | The fixture invents an untrusted parameter and directly interpolates it. No admitted parent establishes that provenance, and the upstream structural rule cannot prove it. Retain only as a rule-local regression until a real historical or current defect is independently confirmed. |
| `security.sql.parameterised` | Source-backed replacement | Replace the invented Account query with a real static query using the database parameter channel, for example ERPNext `setup/doctype/company/company.py:241`. The source anchor, values, and call context must be retained. |
| `security.sql.allowlisted-structure` | Source-backed replacement | Use ERPNext `accounts/deferred_revenue.py:270`-`303`, where selected debit/credit column names come from a closed branch and values remain parameterised. This is a real structural-interpolation negative for injection and a positive Review Hotspot for the broad upstream rule. |
| `security.filesystem.user-path` | Remove from acceptance corpus | A bare function parameter passed to `open` is not evidence of an HTTP-controlled path or traversal. Replace it only when a real source-to-open path is established; otherwise keep the pattern in native rule tests. |
| `security.filesystem.constant-path` | Source-backed replacement | Use Frappe `geo/country_info.py:24`-`27`, which opens a repository-owned JSON file relative to `__file__`. It is a real filesystem-access hotspot and a traversal-negative boundary. |
| `security.templates.user-template` | Useful unresolved boundary | Real Frappe code deliberately renders DocType-managed template text, for example `email/doctype/email_template/email_template.py:28`-`39`, after template validation. Whether any such path is exploitable depends on sandbox, trust, and caller boundaries; the current blocking label is unsupported. Replace it with source-backed audit cases and retain unresolved security questions explicitly. |
| `security.templates.static-template` | Source-backed replacement | Use ERPNext `stock/reorder_item.py:322`-`332`, which renders the repository-owned `templates/emails/reorder_item.html`. This is a real static-template boundary for the broad upstream audit rule. |
| `performance.n-plus-one.unbounded` | Source-backed replacement | Use ERPNext `accounts/deferred_revenue.py:84`-`94` or `115`-`123`, where invoice names drive one `get_doc` per invoice. This establishes the query/document-load-in-row-loop hypothesis; runtime query count and operational scale remain required before claiming a regression. |
| `performance.n-plus-one.chunked` | Useful unresolved boundary | The current random Account fixture does not preserve the active Karam batching semantics. Keep the underlying Karam candidate exploratory until its milestone commit; then reduce its real party-type/chunk behaviour and attach batch-size/query-count evidence before scoring it. |

## Cross-case contract failures

No case qualifies unchanged because the manifest currently:

- stores expected Semgrep findings but no independent Ground-Truth Label;
- gives prose provenance without an exact revision, source anchor, content
  hash, or source-backed parent;
- does not version the Rule Claim or record its Rule Scope and parser status;
- uses author-entered `confidence` rather than measured Rule Confidence;
- mixes enforcement tier with semantic truth;
- has no blind reviewer records, adjudication, Case Clusters, or sealed holdout;
- uses mutable `latest` as a compatibility label; and
- treats reductions authored from rule syntax as if they could measure the
  rule's precision.

## Disposition of the existing files

Do not wire the draft into CI as acceptance evidence. During later
implementation:

1. retain `benchmarks/run.py` and its version/performance machinery;
2. move or relabel pattern-mirroring cases as native syntax regression tests;
3. introduce a separate ground-truth ledger and finding-to-case mapping;
4. replace the eleven cases above with source-backed clusters;
5. keep the three unresolved families out of enforcement metrics; and
6. remove the three unsupported security assertions from the acceptance
   corpus unless genuine parents are found.
