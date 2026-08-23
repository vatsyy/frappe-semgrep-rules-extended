import frappe


def get_recent_accounts(descending: bool) -> list[tuple[object, ...]]:
    direction = "DESC" if descending else "ASC"
    return frappe.db.sql(f"SELECT name FROM `tabAccount` ORDER BY modified {direction}")
