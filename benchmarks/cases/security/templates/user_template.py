import frappe


def render_user_template(template_source: str, context: dict[str, object]) -> str:
    return frappe.render_template(template_source, context)
