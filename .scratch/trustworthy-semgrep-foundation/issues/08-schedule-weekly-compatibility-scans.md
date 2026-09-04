# 08: Schedule weekly Compatibility Scans

**What to build:** Give the rules repository an owned recurring execution of the
canonical read-only scan against immutable stable Frappe and ERPNext snapshots,
without modifying or gating either upstream project.

**Blocked by:** 07: Inventory Analysis Targets and Scan Health.

**Status:** proposed — independent wave review and renewed Vatsal approval required.

- [ ] A rules-repository workflow runs weekly and can also be invoked manually
      with exact source, engine, rule and catalogue identities.
- [ ] The schedule records latest success, missed or failed runs, next due time
      and immutable output provenance.
- [ ] Frappe and ERPNext are checked out read-only at declared revisions; the
      workflow never updates a user's local applications or gates upstream CI.
- [ ] Findings, target coverage, Scan Health, runtime and memory remain stable
      structured evidence suitable for Corpus Refresh and trend comparison.
- [ ] Failure to run is visible and cannot be represented as a clean scan.
- [ ] The solution reuses repository automation and artefacts; it adds no service,
      dashboard or second source of truth.
