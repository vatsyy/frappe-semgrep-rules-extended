# Karam rule-review outcome

The current v16 migration worktree was scanned read-only before and after the
review-supported local rule change. Its source content identity remained
`7a92fde4798c6832f741efbffe59aff821f1a57afee5449976036c9b786b8128`.

- Initial candidates: 11; source-reviewed: 11/11.
- Current candidates after rule refinement: 8.
- Current composition: four N+1 advisories, two confirmed authorisation risks,
  one safe SQL-format review prompt and one intentional upstream policy finding.
- No new rule was created.

The N+1 rule now excludes clear literal SQL writes and a query that merely
produces the loop iterable. Four old identities disappeared and one enclosing,
bounded schema-read advisory was exposed and separately reviewed: a net
reduction of three candidates. Karam Finance itself was not modified.
