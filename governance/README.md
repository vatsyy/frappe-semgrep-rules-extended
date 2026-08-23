# Rule governance

`catalogue.json` is the sole current-state source for governed Rule Claims. It
starts empty: existing rule files remain candidates until a later Portfolio
Review records their evidence-backed outcomes. Presence in `rules/` is not
acceptance.

The versioned contracts in `schemas/` define the catalogue, Rule Contract,
lifecycle and current-state vocabulary consumed by
`scripts/check_governance.py`. The validator enforces truthful enforcement
ceilings, lifecycle consistency and non-compensating admission gates. It also
prevents validation-only fixtures, urgency or sampled Baseline Triage from
creating a Blocking Rule.

Run the public repository seam:

```shell
make test
```

Invented examples may validate these contracts, but they cannot establish Rule
Confidence or admit a rule. Decision history, evidence packets and schema
migrations are added by the subsequent foundation tickets.
