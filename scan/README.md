# Canonical public snapshot scan

`scan-public-snapshot` archives an exact public Git commit into temporary
storage, executes the complete rule tree once and leaves the source worktree
untouched. Branches, tags passed as revisions and abbreviated SHAs are rejected.

Run it with explicit immutable inputs:

```shell
make scan-public-snapshot \
  SOURCE_REPO=../erpnext \
  SOURCE_REVISION=<40-character-commit-sha> \
  SOURCE_NAME=erpnext \
  SCAN_OUTPUT=scan-results/<identity>
```

The output directory is never overwritten. It contains the complete raw Semgrep
JSON, deterministic findings, immutable provenance, separate Scan Health,
Semgrep diagnostics and a concise summary. Findings remain advisory and do not
change the exit status; incomplete execution or any Semgrep analysis error
returns `2` after retaining the diagnostic outputs. Gate Evaluation belongs to
Ticket 10 and is not inferred from Semgrep severity.

Semgrep CE `1.174.0`, the complete rule-tree content hash, catalogue hash,
source commit and tree, exclusions and resource settings are recorded for every
run. `scan-results/` is local retained evidence and is intentionally ignored by
Git; CI consumers should upload the complete directory as an immutable
artefact.

For current migration or milestone WIP, use `SOURCE_MODE=worktree` and omit
`SOURCE_REVISION`. The scanner copies tracked, modified and non-ignored untracked
files into temporary storage, records a complete content hash and fails if the
worktree changes while that snapshot is being created. Agent metadata,
`.scratch/` and dependency directories are excluded from Analysis Targets.

Scan every Git application repository immediately beneath a Bench `apps/`
directory with current WIP included:

```shell
make scan-all-apps \
  APPS_ROOT=.. \
  SCAN_OUTPUT=scan-results/all-apps-<identity>
```

The rules repository is excluded because it is the scanner rather than an
application target. Per-application raw outputs remain separate; the aggregate
contains only identities, counts and Scan Health. One unhealthy application
does not prevent the remaining applications from being scanned.
