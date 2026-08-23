import frappe


def load_accounts(chunks: list[list[str]]) -> list[dict[str, object]]:
    accounts = []
    for names in chunks:
        accounts.extend(
            frappe.get_all("Account", filters={"name": ["in", names]}, fields=["name"])
        )
    return accounts
