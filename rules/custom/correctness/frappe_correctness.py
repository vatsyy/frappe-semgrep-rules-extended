def malformed_placeholders(values):
    # ruleid: frappe-malformed-sql-placeholder-list
    return ", ".join(["%s" * len(values)])


def valid_placeholders(values):
    # ok: frappe-malformed-sql-placeholder-list
    return ", ".join(["%s"] * len(values))


def submitted_ledger_rows(account):
    # ruleid: frappe-gl-entry-read-without-is-cancelled
    return frappe.get_all("GL Entry", filters={"account": account, "docstatus": 1}, pluck="name")


def submitted_ledger_rows_positional(account):
    # ruleid: frappe-gl-entry-read-without-is-cancelled
    return frappe.db.get_list("GL Entry", {"docstatus": 1, "account": account}, pluck="name")


def submitted_ledger_rows_from_variable(account_currency):
    filters = {"docstatus": 1, "account_currency": account_currency}
    # ruleid: frappe-gl-entry-read-without-is-cancelled
    return frappe.db.get_all("GL Entry", filters=filters, fields=["name", "account"])


def live_ledger_rows(account):
    # ok: frappe-gl-entry-read-without-is-cancelled
    return frappe.get_all(
        "GL Entry", filters={"account": account, "docstatus": 1, "is_cancelled": 0}, pluck="name"
    )


def live_ledger_rows_from_variable(account_currency):
    filters = {"docstatus": 1, "is_cancelled": 0, "account_currency": account_currency}
    # ok: frappe-gl-entry-read-without-is-cancelled
    return frappe.db.get_all("GL Entry", filters=filters, fields=["name", "account"])


def live_ledger_rows_with_late_flag(account):
    filters = {"docstatus": 1, "account": account}
    filters["is_cancelled"] = 0
    # ok: frappe-gl-entry-read-without-is-cancelled
    return frappe.get_all("GL Entry", filters=filters, pluck="name")


def ledger_rows_by_cancellation(account):
    # ok: frappe-gl-entry-read-without-is-cancelled
    return frappe.get_all("GL Entry", filters={"account": account, "is_cancelled": 0}, pluck="name")


def submitted_journal_entries(company):
    # ok: frappe-gl-entry-read-without-is-cancelled
    return frappe.get_all("Journal Entry", filters={"company": company, "docstatus": 1}, pluck="name")


def submitted_ledger_value(voucher_no):
    # ok: frappe-gl-entry-read-without-is-cancelled
    return frappe.db.get_value("GL Entry", {"voucher_no": voucher_no, "docstatus": 1}, "name")
