import frappe


def load_accounts(rows: list[dict[str, str]]) -> list[object]:
    accounts = []
    for row in rows:
        accounts.append(frappe.db.get_value("Account", row["account"], "account_name"))
    return accounts
