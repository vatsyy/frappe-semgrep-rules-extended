import frappe


def render_receipt(context: dict[str, object]) -> str:
    return frappe.render_template("templates/includes/receipt.html", context)
