def malformed_placeholders(values):
    # ruleid: frappe-malformed-sql-placeholder-list
    return ", ".join(["%s" * len(values)])


def valid_placeholders(values):
    # ok: frappe-malformed-sql-placeholder-list
    return ", ".join(["%s"] * len(values))
