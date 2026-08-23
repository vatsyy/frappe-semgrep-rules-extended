import frappe


@frappe.whitelist()
def get_accounts(company: str) -> list[dict[str, object]]:
    return frappe.get_all("Account", filters={"company": company}, fields=["name"])
