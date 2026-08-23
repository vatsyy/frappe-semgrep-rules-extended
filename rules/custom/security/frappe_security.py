import frappe


@frappe.whitelist()
def list_private_rows():
    # ruleid: frappe-whitelisted-permission-bypass
    return frappe.get_all("Private Record", fields=["name", "secret"])


@frappe.whitelist()
def update_private_row(name):
    doc = frappe.get_doc("Private Record", name)
    doc.secret = "updated"
    # ruleid: frappe-whitelisted-permission-bypass
    doc.save(ignore_permissions=True)


@frappe.whitelist()
async def delete_private_row(name):
    # ruleid: frappe-whitelisted-permission-bypass
    frappe.delete_doc("Private Record", name, ignore_permissions=True)


def internal_rebuild():
    # ok: frappe-whitelisted-permission-bypass
    return frappe.get_all("Private Record", pluck="name")


@frappe.whitelist()
def permission_aware_list():
    # ok: frappe-whitelisted-permission-bypass
    return frappe.get_list("Private Record", fields=["name"])


@frappe.whitelist()
def normal_save(name):
    doc = frappe.get_doc("Private Record", name)
    # ok: frappe-whitelisted-permission-bypass
    doc.save()
