# Frappe security rules

These rules identify explicit framework permission bypasses at remote-call
boundaries. Findings require authorisation review; they are not vulnerability
verdicts without confirming the surrounding access checks and data flow.

The shell rule checks interpolation operands, including f-strings and positional
or keyword `.format` arguments. Quoted arguments and simple local assignments
used in string concatenation have regression coverage; mixed unquoted arguments
and unsafe reassignments must still warn. This does not prove that an entire
shell command is safe or model arbitrary quoting wrappers.

The file-path rule recognises a narrow allowlist guard: membership in a tuple
of simple string literals, with `frappe.throw(...)` as the sole rejected-branch
statement. It does not treat a guard inside `try`/`except` as sanitisation, since
the exception may be caught. Dynamic allowlists, logging without termination,
and replacement paths after validation remain findings. Other validation forms
may still require manual review.
