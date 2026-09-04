# 05: Pin the rules-CI engine

**What to build:** Make repository CI reproduce the verified local acceptance
environment with one exact current Semgrep CE version, without attempting the
later evidence-led upgrade decision.

**Blocked by:** None after corrected-wave approval.

**Status:** completed on 2026-08-25 — the five-test CI contract and full
repository acceptance suite pass with Semgrep CE `1.174.0`.

- [x] Rules CI installs exactly Semgrep CE `1.174.0`; no mutable engine label or
      unconstrained `pip install semgrep` remains.
- [x] The exact engine and complete rules-tree identity appear in CI provenance.
- [x] `make test` remains the single required rules check and exercises native
      tests, ownership, governance validators, benchmark guards and the
      byte-identical Upstream Mirror as those components become available.
- [x] CI distinguishes repository failure, engine failure and Analysis Coverage
      Failure in stable outputs.
- [x] No candidate engine is adopted and Karam's private `1.172.0` pin is not
      changed by this ticket.
- [x] The pin can be changed only by the post-pilot qualification ticket and an
      appended decision.
