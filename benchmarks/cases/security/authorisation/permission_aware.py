import frappe


@frappe.whitelist()
def get_accounts(company: str) -> list[dict[str, object]]:
    return frappe.get_list("Account", filters={"company": company}, fields=["name"])
