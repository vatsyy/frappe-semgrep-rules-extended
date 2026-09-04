# 09: Review `frappe-sql-format-injection`

**What to build:** Determine exactly what the upstream SQL-format rule proves,
measure its real safe and unsafe boundaries, and assign a disposition without
equating string formatting with proven injection.

**Blocked by:** 07: Record the Portfolio Review Cut and Review Queue.

**Status:** ready-for-agent

- [ ] The Rule Claim distinguishes the observed formatted SQL construct from
      unproved attacker control, exploitability, and allowlisted structural
      interpolation.
- [ ] Real source-backed positive, parameterised, static, and closed-branch
      structural cases are labelled independently and clustered correctly.
- [ ] Current Frappe, ERPNext, and Karam matches and suppressions receive source-
      contextual review without copying private Karam source into public
      evidence.
- [ ] Structural matching and same-function taint are assessed only against
      Semgrep CE's validated proof boundary; no implementation route is chosen
      before evidence supports it.
- [ ] Native tests, parser coverage, compatibility, reviewer cost, limitations,
      and exact defensible measurements are recorded.
- [ ] The scorecard produces a final disposition; any improved detector is a
      distinct Noospheric Rule and the upstream material remains unchanged.
