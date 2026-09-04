# Gates: evidence-led five-rule Semgrep pilot

Scope: freeze the complete rule portfolio, adjudicate five pilot rules from real
source, implement only supported outcomes, and prove current all-app behaviour
without modifying application worktrees or the Frappe upstream mirror.

- [x] G0: this pilot ledger contains mechanically meaningful gates
  CHECK: node /Users/vatsal/.agents/skills/unlazy/scripts/gate-lint.mjs GATES.md
  EXPECT: LINT OK
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/vatsal/f-v16/v-16/apps/frappe-semgrep-rules-extended; path=f01c19962dbe/22 entries; EXPECT=matched; output-sha256=48630b7361dd44ee870917b12c3d19b9d7bdea738aaca16bb04d4cab83b772d2; output-bytes=8

- [x] G1: the Portfolio Review Cut freezes every rule and all seven source identities
  CHECK: python3 scripts/verify_pilot.py --check review-cut
  EXPECT: Portfolio Review Cut verification passed
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/vatsal/f-v16/v-16/apps/frappe-semgrep-rules-extended; path=f01c19962dbe/22 entries; EXPECT=matched; output-sha256=4d2861807594a4946094db96ed160b3ae6e166ef45ca9b61eada5ecfaaa07361; output-bytes=41

- [x] G2: all five pilot rules have complete bounded evidence packets
  CHECK: python3 scripts/verify_pilot.py --check evidence-packets
  EXPECT: pilot evidence verification passed
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/vatsal/f-v16/v-16/apps/frappe-semgrep-rules-extended; path=f01c19962dbe/22 entries; EXPECT=matched; output-sha256=8d19d56b02a844e68c6ce774127e6d4a25c17a59748847c57c20de7ec9f0ccaa; output-bytes=35

- [x] G3: every pilot rule has one evidence-supported authored portfolio recommendation
  CHECK: python3 scripts/verify_pilot.py --check decisions
  EXPECT: pilot decision verification passed
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/vatsal/f-v16/v-16/apps/frappe-semgrep-rules-extended; path=f01c19962dbe/22 entries; EXPECT=matched; output-sha256=9ec4d3845c63bf3f0a43d619c5a117e2bb7296b9290357a9e85139b3ba4da7c2; output-bytes=35

- [x] G4: source-derived positive and negative controls exercise every changed claim
  CHECK: python3 scripts/verify_pilot.py --check regression-controls
  EXPECT: pilot regression-control verification passed
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/vatsal/f-v16/v-16/apps/frappe-semgrep-rules-extended; path=f01c19962dbe/22 entries; EXPECT=matched; output-sha256=c07e00cf2e79192338ea90fd8f6b90e110aa88781f093e9cef50ad280246639d; output-bytes=80

- [x] G5: a current complete scan covers all seven application worktrees
  CHECK: python3 scripts/verify_pilot.py --check all-app-scan
  EXPECT: current all-app scan verification passed
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/vatsal/f-v16/v-16/apps/frappe-semgrep-rules-extended; path=f01c19962dbe/22 entries; EXPECT=matched; output-sha256=b0c218720170dec6a3ad0f57dd9c17bd4c1330f4152db1244d78fa2f54da7d34; output-bytes=41

- [x] G6: before-and-after evidence measures finding and coverage drift per pilot rule
  CHECK: python3 scripts/verify_pilot.py --check comparison
  EXPECT: pilot comparison verification passed
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/vatsal/f-v16/v-16/apps/frappe-semgrep-rules-extended; path=f01c19962dbe/22 entries; EXPECT=matched; output-sha256=ded72fc69551850f9b4b85a32883b01d4304ae112544f0fec983d97bc852b7b8; output-bytes=37

- [x] G7: every application worktree and the Frappe upstream mirror remain unchanged
  CHECK: python3 scripts/verify_pilot.py --check preservation
  EXPECT: source and mirror preservation verification passed
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/vatsal/f-v16/v-16/apps/frappe-semgrep-rules-extended; path=f01c19962dbe/22 entries; EXPECT=matched; output-sha256=d7b11e711f1c200b27b417ea5473a7c4f6f1b5bd27081a2c52ab526641064e01; output-bytes=51

- [x] G8: the complete repository acceptance seam remains green
  CHECK: make test && printf '\npilot repository acceptance passed\n'
  EXPECT: pilot repository acceptance passed
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/vatsal/f-v16/v-16/apps/frappe-semgrep-rules-extended; path=f01c19962dbe/22 entries; EXPECT=matched; output-sha256=af8b423998c372f10656617502c9488565b23ec4ac6d6b8458fd1a6d29414726; output-bytes=2132

- [x] G9: a distinct reviewer blindly labels all cases and recommends all five outcomes
  CHECK: python3 scripts/verify_pilot.py --check independent-review
  EXPECT: independent blind review verification passed
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/vatsal/f-v16/v-16/apps/frappe-semgrep-rules-extended; path=f01c19962dbe/22 entries; EXPECT=matched; output-sha256=f4299c4dfc8acca36fa5a907928300b9ae5f8da9562321593f3d73a9fda48e7e; output-bytes=45

- [x] G10: Vatsal approves or amends the independently reviewed five-rule decisions
  CHECK: python3 scripts/verify_pilot.py --check approval
  EXPECT: Vatsal pilot approval verification passed
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/vatsal/f-v16/v-16/apps/frappe-semgrep-rules-extended; path=f01c19962dbe/22 entries; EXPECT=matched; output-sha256=db59070c58e03eb32a30da78eb62a4c00e75cb79ba463d6da577b4ee78fc338b; output-bytes=42
