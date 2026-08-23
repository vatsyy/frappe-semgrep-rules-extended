import frappe


def get_account(account_name: str) -> list[tuple[object, ...]]:
    return frappe.db.sql(f"SELECT name FROM `tabAccount` WHERE name = '{account_name}'")
