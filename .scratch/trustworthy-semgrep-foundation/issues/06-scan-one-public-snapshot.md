# 06: Scan one public application snapshot canonically

**What to build:** Deliver one public, reproducible vertical scan that executes
the complete governed portfolio once against an immutable Frappe or ERPNext
snapshot and emits the stable raw contracts needed by later coverage and gate
slices.

**Blocked by:** 01: Validate catalogue and Rule Contract foundations; 05: Pin the
rules-CI engine.

**Status:** completed on 2026-08-25 — the immutable ERPNext v16.32.3 scan and
retained evidence are recorded in
[`evidence/06-erpnext-public-snapshot-scan.md`](../evidence/06-erpnext-public-snapshot-scan.md).

- [x] One public command resolves exact engine, complete rule-tree identity,
      catalogue, source revision, exclusions and resource settings.
- [x] A pre-merge rule tree requires an immutable PR commit SHA or content hash
      covering every input; branches, aliases and partial pins are rejected.
- [x] The portfolio executes once and structured Semgrep output is retained as
      input to deterministic post-processing.
- [x] Stable outputs include provenance, complete findings, execution health and
      a concise human summary without using Semgrep severity as policy.
- [x] Invalid, incomplete or irreproducible execution fails clearly while valid
      advisory findings do not.
- [x] Integration tests use a real public source-backed snapshot and leave the
      application worktree unchanged.
