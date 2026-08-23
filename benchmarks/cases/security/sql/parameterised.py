import frappe


def get_account(account_name: str) -> list[tuple[object, ...]]:
    return frappe.db.sql(
        "SELECT name FROM `tabAccount` WHERE name = %s",
        (account_name,),
    )
