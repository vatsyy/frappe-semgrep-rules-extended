# Independent pilot review

Vatsal is the approval owner. The independent reviewer must be a distinct actor
authorised by Vatsal and must not inspect rule YAML, authored evidence packets,
`decisions-v1.json` or the allocation before freezing labels.

The reviewer receives only
`.scratch/trustworthy-semgrep-foundation/pilot/blind-review-input-v1.json` and
writes the supplied `blind-review-result-v1.json` template. Every one of the 99
cases needs a source-backed label and basis, followed by one recommendation for
each opaque claim A–E. After labels freeze, the allocation may be revealed and
the authored recommendations may be compared. Vatsal then approves or amends
the five final outcomes. No incomplete census can become blocking.
