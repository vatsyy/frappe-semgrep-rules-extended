# 07: Inventory Analysis Targets and Scan Health

**What to build:** Extend the canonical public scan with an independent target
denominator, explicit parser coverage and a ratcheting Coverage Baseline so
unanalysed code is never reported as clean.

**Blocked by:** 06: Scan one public application snapshot canonically.

**Status:** resolved — the 2026-08-25 all-apps worktree scan retained 14 parser
gaps across seven repositories; the versioned baseline classifies all 8,496
eligible targets with stable identities and zero silent gaps.

- [x] Every eligible target is classified independently of Semgrep's path count.
- [x] Parser failures and incomplete execution are Scan Health, never clean negatives.
- [x] The Coverage Baseline records stable target identities and gap state.
- [x] Mixed templates, generated/vendor sources and native-valid gaps have explicit treatments.
- [x] New or changed gaps fail baseline verification; inherited gaps remain visible.
- [x] Historical eight-gap evidence is preserved; current source/engine drift is recorded as 14 gaps.
