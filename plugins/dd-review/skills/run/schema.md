# Finding schema (every reviewer returns exactly this)

```json
{
  "role": "correctness",
  "reviewed_range": "<BASE_SHA>..<HEAD_SHA>",
  "summary": "2 findings (1 blocking)",
  "nothing_to_report": false,
  "findings": [
    {
      "id": "COR-1",
      "severity": "blocking | should_fix | nit",
      "origin": "introduced | pre_existing",
      "class": "short_snake_case_bug_class",
      "file": "src/billing/invoice.ts",
      "lines": "88-97",
      "claim": "Discount applied twice when coupon and plan discount coexist",
      "trigger": "Plan with 10% discount + coupon SAVE10 -> total reduced 20% then 10% again",
      "evidence": "invoice.ts:91 applies plan discount; applyCoupon() at :96 re-reads discounted subtotal",
      "spec_ref": "SPEC.md 3.2 'discounts do not stack' (or null)",
      "suggested_fix": "one-sentence minimal fix, no code rewrite",
      "confidence": 75
    }
  ]
}
```

Severity guide:
- blocking: wrong behaviour on a realistic path, spec requirement missing, security hole, data loss,
  broken contract, test tampering.
- should_fix: real defect on an edge path, missing test for a spec'd edge case, scope extra with risk.
- nit: everything else that still passed the bar. Nits are reported, never sent to the fixer.

ID prefixes: SPEC, COR, TEST, SEC, CON (contract), CONV, SIMP, PERF, ARCH, E2E, INT (test integrity).
