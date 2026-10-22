# Numeric bytes in decimal amount helpers

`frappe-decimal-amount-stringifies-bytes` is an advisory structural check for
`Decimal(str(value))` and `Decimal(str(value or 0))` inside helpers named
`decimal_amount`, where `value` is the first parameter. It recognises imported
and module-qualified `decimal.Decimal` calls.

## Evidence

Karam Accounts production Trial Balance failed on a SQL aggregate returned as
`b'0.0000'`. Stringification produced `"b'0.0000'"`, causing
`decimal.InvalidOperation: ConversionSyntax`. The General Ledger had the same
converter and query-cast pattern. Both converters reproduced the failure with
the captured byte input; local SQL returned ordinary strings instead.

The supported safe form decodes bytes with ASCII in an `isinstance(value, bytes)`
guard immediately before returning the converted amount. This preserves decimal
precision and retains errors for malformed input. Decoding an unrelated variable,
reassigning the input after decoding, or placing the guard in an optional branch
does not satisfy this exception.

## Boundaries

The rule does not establish that a database or caller returns bytes. Helpers with
contracts that exclude bytes can be intentional matches. Other function names,
interprocedural normalisation and alternative safe decoding forms are outside
the recognised pattern. The rule is scoped by helper name, not an app-specific
filesystem path, so the same report helper is checked in other apps. No automatic
fix is supplied. Review findings; do not replace malformed financial values with
zero or route exact amounts through floating-point conversion.

Fixtures include the original and corrected report converters, qualified calls,
unrelated decoding, reassignment, conditional decoding, and constant conversions.

Run from the repository root:

```sh
semgrep --test --strict --config rules/custom/correctness/decimal_numeric_bytes.yml rules/custom/correctness/decimal_numeric_bytes.py
python3 scripts/check_rule_contract.py
```
