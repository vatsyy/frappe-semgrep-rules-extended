# All-apps worktree scan

Status: executed on 2026-08-25. The retained canonical output is
`scan-results/all-apps-20260825-v2/`.

## Scope and result

The complete 61-rule tree scanned content-hashed snapshots of every Git code
repository immediately under `/Users/vatsal/f-v16/v-16/apps`, excluding only
the rules repository itself. Modified and non-ignored untracked files were
included, so Karam Finance represents its current v16 migration WIP rather than
its older committed state.

| Application | Findings | Scan Health | Analysis errors |
|---|---:|---|---:|
| ERPNext | 2,792 | invalid | 2 |
| Frappe | 1,881 | invalid | 7 |
| Frappe UI | 0 | invalid | 1 |
| Karam Finance | 11 | valid | 0 |
| OneDrive Offsite Backup | 0 | valid | 0 |
| Payments | 71 | invalid | 4 |
| Wiki | 101 | valid | 0 |

The 4,856 matches are unreviewed advisory evidence, not confirmed defects or
precision measurements. Zero findings likewise does not prove defect absence.

The independent Coverage Baseline inventories 8,496 eligible targets: 8,479
fully analysed, 14 partially analysed parser gaps and three reviewed explicit
exclusions. No target is silently unanalysed. A canonical ignore policy is
installed only inside each disposable snapshot and its original ignore-file
hash is recorded, making the denominator uniform without changing any app.

Karam's 11 current-WIP candidates comprise seven N+1 matches, two permission
bypass matches, one SQL-format match and one `override_doctype_class` match.
They require source review before any rule or application change.

## Scan Health gaps

Fourteen parser gaps remain visible:

- ERPNext: generated `PaymentEntry.ts` and Jinja-templated `rfq.js`;
- Frappe: `data.py`, `query.py`, vendor `fingerprintjs.js`, report boilerplate,
  two Jinja-templated includes and `website_script.js`;
- Frappe UI: `docs/scripts/anchor-links.ts`;
- Payments: four Jinja-templated checkout JavaScript files.

Ticket 07 must classify every eligible target and distinguish mixed-template,
generated/vendor and native-valid parser compatibility gaps. No generic-mode or
ad hoc exclusion was used to disguise these failures.

## Preservation and evidence

Every repository's post-scan Git-status SHA-256 equals the value captured when
its snapshot was created. The scan made no application change, including to
Karam Finance WIP, ERPNext's dirty `banking/yarn.lock`, or Wiki's modified
workspace JSON.

- `all-apps.json`:
  `e81a14fdd8db63af7a2dce7c3716dedbfdfd9212b78810a54fb7a96a399ef84b`
- `summary.md`:
  `c1e5ab1237d438bb1ae6a6fac7683264f361c3e8022f63115658ed1f3d27c91a`

Per-application provenance, complete findings, raw Semgrep JSON, Scan Health
and summaries are retained below `scan-results/all-apps-20260825-v2/applications/`.
