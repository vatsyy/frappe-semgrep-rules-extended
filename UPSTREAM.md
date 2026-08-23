# Upstream synchronisation

Frappe's repository is the source of truth for every file under
`rules/upstream/frappe/`.

| Setting | Value |
| --- | --- |
| Upstream repository | `https://github.com/frappe/semgrep-rules.git` |
| Upstream branch | `develop` |
| Relocated rules | `rules/upstream/frappe/` |
| Last organised upstream commit | `b101a16e69df049b3fed1478bcc16223e957cca2` |

The relocation commit must not contain rule-content changes. Keeping relocation
separate gives Git the strongest possible rename evidence during later merges.

## Create the GitHub fork

Use GitHub's **Fork** action on `frappe/semgrep-rules`. Choose the intended
owner and give the fork its downstream name, such as
`frappe-semgrep-rules-extended`. Copying only the default branch is sufficient
for this repository.

This is preferable to an unrelated blank repository because GitHub retains the
visible fork relationship. Use a blank repository only when that relationship
is deliberately unwanted; if so, do not initialise it with a README, licence,
`.gitignore`, or first commit.

## Configure the remotes

After the fork exists, configure this local repository:

```shell
git remote rename origin upstream
git remote add origin <fork-repository-url>
git fetch origin
git branch --set-upstream-to=origin/develop develop
git remote -v
```

Do not run these commands until the downstream repository URL has been reviewed.

## Import an upstream update

Start from the downstream `develop` integration branch:

```shell
git fetch upstream
git switch develop
git pull --ff-only origin develop
git switch -c sync/frappe-YYYY-MM-DD

git log --oneline develop..upstream/develop
git diff --name-status develop...upstream/develop -- rules
git merge --no-ff upstream/develop
```

Git will normally apply upstream edits to the relocated files. Review the merge
for these exceptional cases:

- Move newly added upstream rule files into `rules/upstream/frappe/`.
- Apply upstream deletions and renames to their relocated counterparts.
- Resolve content conflicts without mixing in custom-rule changes.
- Keep repository-owned rules under `rules/custom/`.

Verify the result before merging the synchronisation branch:

```shell
make test
git diff --check
git status --short
```

`make test` includes an ownership check that compares every relocated upstream
file byte-for-byte with the recorded revision. CI therefore uses a full Git
history checkout so this invariant remains independently verifiable.

Record the imported upstream commit in this document as part of the reviewed
synchronisation change.

## Retire backports after upstream adoption

Rules under `rules/backports/` come from another identified Frappe repository
but are not yet part of `frappe/semgrep-rules`. During each synchronisation,
check whether upstream has adopted an equivalent rule ID. If it has, remove the
backport and its fixtures in the same change so the combined configuration does
not contain duplicate rule IDs.
