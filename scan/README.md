# Scan and re-evaluate rules

## Repeatable rule evaluation

Use `scripts/evaluate_rules.py` to evaluate rule changes against real application
code. `baseline` saves source and rules before a change, `compare` scans edited
rules against that same source, and `inspect` displays findings with source
context. The CLI captures evidence; you decide whether a finding is useful.

### 1. Prepare the checkout

Have Python 3.11 or newer, Git and `uv` available on your `PATH`. The harness uses
the Python standard library; `uv tool run` supplies Semgrep CE **1.174.0** in an
isolated environment. Its first run may download Semgrep. Application services
do not need to be running.

```sh
cd /Users/vatsal/f-v16/v-16/apps/frappe-semgrep-rules-extended
uv tool run --from semgrep==1.174.0 semgrep --version
make test SEMGREP='uv tool run --from semgrep==1.174.0 semgrep'
```

The version command must print `1.174.0`. Record any existing test failures before
changing a rule. Run the remaining examples from this repository too.

### 2. Capture a baseline before editing rules

```sh
python3 scripts/evaluate_rules.py baseline --output scan-results/baseline
```

This selects every Git repository directly beneath the adjacent `apps/`
directory, excluding the rules repository. It scans the complete `rules/` tree:
upstream, backported and custom rules. App discovery is automatic; adding another
Git app makes it eligible for the next baseline.

To evaluate only the three original subjects, use a separate output directory:

```sh
python3 scripts/evaluate_rules.py baseline \
  --app karam_finance \
  --app onedrive_offsite_backup \
  --app africa_cement_factory \
  --output scan-results/selected-baseline
```

Use `--apps-root /path/to/bench/apps` for another Bench. Choose a **new output
directory for every run**; existing directories are never overwritten. The
remaining examples use `scan-results/baseline`.

The snapshot includes tracked files, working changes and non-ignored untracked
files. Root `.agents/`, `.codex/` and `.scratch/` directories, plus `node_modules/`
directories, are omitted. Files matching `*.min.js`, `*.min.css` and additional
`--exclude` patterns are excluded during scanning. App-local `.semgrepignore` files are
replaced only in the copies, so their patterns do not silently change coverage.
Git-ignored untracked files are not copied. Application worktrees are untouched.

Avoid concurrent source edits during capture. The harness checks content and Git
state, but copying a working tree is not an atomic snapshot. Once captured, later
comparisons use the retained bytes even if the live apps change.

### 3. Read results and choose one rule to investigate

Open `scan-results/baseline/summary.md`. It lists findings and analysis errors per
app, plus every rule's finding count, including zero. Copy an exact rule ID into
`inspect`:

```sh
python3 scripts/evaluate_rules.py inspect scan-results/baseline \
  --rule frappe-n-plus-one-read-in-loop --limit 10

python3 scripts/evaluate_rules.py inspect scan-results/baseline \
  --rule frappe-n-plus-one-read-in-loop \
  --app africa_cement_factory --limit 5 --context 8
```

`--limit` caps the total displayed findings; `--context` gives surrounding lines
on each side of the match's starting line. Defaults are 20 findings and 3 context
lines. Increase them or open the retained file to review the enclosing function.

Judge each example against the rule's stated purpose. A database read in a loop
can be a valid review hotspot without being a performance defect. Inspect guards,
caching and callers before making a stronger claim. Also search retained source
independently for missed cases, for example:

```sh
rg -n 'frappe\.(db\.(exists|get_value)|get_doc|get_all)\(' \
  scan-results/baseline/sources
```

That search is only a starting point; aliases and wrappers need separate review.

### 4. Add fixtures, then make the smallest justified change

Add positive and safe negative examples to the fixtures beside the custom rule's
YAML. Use `# ruleid: RULE_ID` immediately before an expected Python match and
`# ok: RULE_ID` before a safe case; JS fixtures use `//` comments. Follow the
[custom-rule conventions](../rules/custom/README.md).

Run focused tests **before changing detection** and confirm the new regression
fails against the original rule. For the performance rules:

```sh
uv tool run --from semgrep==1.174.0 semgrep \
  --test --strict --test-ignore-todo rules/custom/performance
```

Then edit the custom rule, preserve its ID when its intent is unchanged, and
rerun the focused command followed by the full suite:

```sh
make test SEMGREP='uv tool run --from semgrep==1.174.0 semgrep'
```

Edit the repository's `rules/custom/` files, not a saved run's `rules/` or
`sources/`. Keep `rules/upstream/frappe/` byte-for-byte unchanged and leave app
code alone. Document purpose, representative matches, safe cases and limitations
beside the rule. If source inspection does not justify a change, record that
conclusion instead of widening or narrowing detection to change the count.

### 5. Compare against the same application source

```sh
python3 scripts/evaluate_rules.py compare scan-results/baseline \
  --output scan-results/candidate
```

This reads current repository rules and the baseline's saved source. It does not
reread application worktrees. App selection, engine version, exclusions and
resource settings remain fixed. To evaluate another rule directory, add
`--rules /path/to/candidate-rules`.

Open `scan-results/candidate/summary.md`, then inspect all three kinds of change:

```sh
for kind in added removed changed; do
  python3 scripts/evaluate_rules.py inspect scan-results/candidate \
    --rule frappe-n-plus-one-read-in-loop --kind "$kind" --limit 20
done
```

Replace the rule ID with the one you edited. Omit `--kind` to inspect all current
findings. `--kind` filters require a comparison run, not an initial baseline.

| Result | What to review |
| --- | --- |
| Added | Newly covered behaviour or a new false positive. |
| Removed | An intended suppression, missed detection or removed rule. |
| Changed | Same match with different message, severity, metadata or fix. The CLI prints before and after. |
| Unchanged | The recorded match and claim stayed the same; correctness is still unverified. |
| Same paths = False | Investigate coverage changes before interpreting finding differences. |
| Analysis errors | Parsing or execution gaps remain, even when identical in both runs. |

Findings are paired by rule, location and captured metavariables. Separate
arguments at the same function location, and repeated matches, remain separate.
A location or metavariable change appears as an addition/removal. Disappearing
findings are not automatically fixes. Rule-level exclusion changes remain
visible in the saved rule trees.

### 6. Repeat the evaluation

For another edit on the same source, compare against the same baseline with a
fresh output name such as `scan-results/candidate-2`. A useful optional check is
to compare immediately after capturing a baseline, before editing rules; expect
no finding differences while retaining any analysis errors.

Capture a **new baseline** when you want updated application source, different
apps, exclusions or resource settings, or after updating the harness code.
Comparisons require the same harness implementation. Only evaluation-CLI runs
can be reused; older `scan-all-apps` outputs are not baseline inputs for this CLI.

Keep run folders in ignored `scan-results/`. They contain copies of application
source. Retain the complete folder while reviewing or reproducing results, and
remove old folders yourself when no longer needed. Do not edit retained inputs,
results or manifests: their checksums are verified before reuse. These are local
integrity checks, not authentication against deliberate changes to checksums.

### Output reference

Paths below are relative to a run's output directory.

| File or directory | Contents |
| --- | --- |
| `summary.md` | Per-app and per-rule counts, analysis status and comparison totals. |
| `manifest.json`, `manifest.sha256` | Source Git identities, content hashes, rule inventory, engine, harness and settings. |
| `sources/APP/`, `rules/` | Exact retained analysis inputs. |
| `applications/APP/command.json` | Exact scan arguments and working directory. |
| `applications/APP/semgrep.json` | Raw engine JSON. |
| `applications/APP/semgrep.stderr.txt` | Engine diagnostics. |
| `applications/APP/results.json` | Findings, execution/analysis health and scanned/skipped paths. |
| `comparison.json` | Added, removed and changed findings; before/after health and paths. Present for comparisons. |

### Exit codes and troubleshooting

| Symptom | Meaning and next step |
| --- | --- |
| `baseline` or `compare` exits 0 | Analysis completed without reported errors, regardless of finding count. |
| Exit 2 with a newly written manifest | Analysis is incomplete. Read the affected app's `results.json` and stderr; `inspect` can still display results. |
| Exit 2 without a manifest | Capture/execution failed before producing a reusable run. Read stderr and any saved diagnostics, then use a fresh output directory. |
| Output already exists | Choose a fresh directory; do not overwrite the baseline. |
| Unknown application or rule | Use the actual Git app directory name and an exact rule ID from `summary.md`. |
| Retained files or evaluation code changed | Preserve the diagnostics and capture a new baseline. |
| Engine version rejected | Use the default pinned command or an absolute executable path for CE 1.174.0 via `--semgrep-command`. |
| Timeout or resource failure | Adjust baseline resource options and recapture before comparing. |

Unchanged parser errors still make comparisons exit 2. `inspect` returns 0 when
inspection succeeds, including for runs marked incomplete and rules with no
matches. Run commands individually when reviewing failures; an `&&` chain stops
at a baseline's exit 2. Do not edit application code or hide parser errors to
make the scan return 0.

Baseline resource defaults are `--jobs 4`, `--timeout 30` (per rule per file),
`--process-timeout-seconds 1800` (per app) and `--max-memory-mib 0` (no configured
cap). Add exclusions with repeated `--exclude` options, quoting globs such as
`--exclude '*.generated.py'`. Comparisons inherit these settings. Run
`python3 scripts/evaluate_rules.py baseline --help`, or use `compare --help` and
`inspect --help`, for the available options.

More varied apps provide more examples, but counts and passing fixtures do not
establish precision or recall. Review safe cases and search for missed problems
as well as inspecting matches. Runtime checks are still needed for claims such
as query cost or exploitability.

## Canonical public snapshot scan

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
returns `2` after retaining the diagnostic outputs.

Semgrep CE `1.174.0`, the complete rule-tree content hash,
source commit and tree, exclusions and resource settings are recorded for every
run. `scan-results/` is local retained evidence and is intentionally ignored by
Git; CI consumers should upload the complete directory as an immutable
artefact.

For current migration or milestone WIP, use `SOURCE_MODE=worktree` and omit
`SOURCE_REVISION`. The scanner copies tracked, modified and non-ignored untracked
files into temporary storage, records a complete content hash and checks for Git status changes during copying. This does not detect every
concurrent edit; use commit mode when an immutable input is required. Agent metadata,
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

Use `SEMGREP=/absolute/path/to/semgrep` to select the pinned engine. The scanner
runs from temporary directories, so custom executable paths must be absolute.
