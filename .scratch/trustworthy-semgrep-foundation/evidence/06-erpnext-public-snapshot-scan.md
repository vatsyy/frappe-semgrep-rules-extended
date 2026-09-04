# Ticket 06 ERPNext public snapshot scan

Status: completed on 2026-08-25. The retained canonical output is
`scan-results/erpnext-11e0ba0a1c45-canonical/`.

## Immutable inputs

- Source: `https://github.com/frappe/erpnext.git`
- Commit: `11e0ba0a1c45f217e2e73e885f699102d06da325` (v16.32.3)
- Source tree: `2becff5417a8cecd388ffb07b244f932cad0ad03`
- Semgrep CE: `1.174.0`
- Rule-tree SHA-256:
  `b8eeeae2c0427a4a5890e815b39dd16a09d073c7f777bde044fa2be6865806ec`
- Catalogue SHA-256:
  `da1fc608dc6a702fe72b801e668d77546a6af2b2211e0cb690cd1d03a5cb4bbf`

The scan archived the exact commit from Git objects. ERPNext's unrelated dirty
`banking/yarn.lock` remained byte-identical at SHA-256
`29eeddc4f398ec5ff2b1cf9a2161b5284ee9fa6a44172fd87f1d6af4ca7ae844`.

## Result

Semgrep completed one full 61-rule execution with exit code `0`. It returned
2,792 advisory matches across 33 rule identities. These matches are unreviewed
raw evidence, not confirmed defects, precision evidence or Gate Evaluation.

Scan Health is `invalid` because Semgrep CE reported two `PartialParsing` gaps:

- `banking/src/types/Accounts/PaymentEntry.ts`
- `erpnext/templates/includes/rfq.js`

The canonical command therefore returned `2` after retaining complete outputs.
Ticket 07 owns target inventory and classification of these analysis gaps; they
were not hidden with ad hoc exclusions.

## Retained output hashes

- `catalogue.json`:
  `da1fc608dc6a702fe72b801e668d77546a6af2b2211e0cb690cd1d03a5cb4bbf`
- `provenance.json`:
  `8ecbe3337f28659f44ed40cf9ecac518a44808d4abb8b1b133eefdb36441110f`
- `findings.json`:
  `093e7de181df83b47e378980c7d664e0fc0f8b79b464f91786ba593823081a`
- `scan-health.json`:
  `d945e07c75b7c19ef6ca907da8c7efd7ced0c16fa533e946bc606a1ae00acb66`
- `semgrep.json`:
  `e06576887e9c845e3db0ced1230d45baa8236dc79e531c132f10c804e4396701`
- `summary.md`:
  `515f3c44be4219269a158c9d008b150883da0b132bb479f33db81fb4a0b99b37`

Two earlier diagnostic runs at `scan-results/erpnext-11e0ba0a1c45/` and
`scan-results/erpnext-11e0ba0a1c45-stable/` exposed machine-specific rewritten
rule IDs and then exercised the portable identifiers before atomic publication
was added. They are superseded and are not canonical evidence.
