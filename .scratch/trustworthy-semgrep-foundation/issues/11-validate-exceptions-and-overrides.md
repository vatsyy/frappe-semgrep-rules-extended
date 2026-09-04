# 11: Validate Rule Exceptions and emergency overrides

**What to build:** Add narrow, expiring human authorisations to the canonical
gate without allowing `nosemgrep`, broad suppressions or emergency workflow
needs to become hidden permanent policy.

**Blocked by:** 10: Evaluate the canonical gate.

**Status:** proposed — independent wave review and renewed Vatsal approval required.

- [ ] A Rule Exception requires exact rule and source, immutable evidence,
      rationale, owner, Vatsal approval and an expiry date or event.
- [ ] Relevant rule, source, corpus or milestone changes invalidate applicability;
      expiration and renewal append events rather than rewriting history.
- [ ] Bare, broad, permanent, automatically renewed and unapproved suppressions
      are rejected; existing `nosemgrep` grants no approval.
- [ ] Emergency Workflow Overrides are Vatsal-only, single-PR, expire after merge
      and require a canonical scan before the next non-emergency merge.
- [ ] Exception, override and ordinary suppression remain distinct in schemas,
      outputs and gate behaviour.
- [ ] Tests cover exact applicability, changes, expiry, renewal, invalid scope and
      missing approval at the public command boundary.
