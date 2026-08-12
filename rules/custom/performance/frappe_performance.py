import frappe


def direct_reads(names):
    for name in names:
        # ruleid: frappe-n-plus-one-read-in-loop
        frappe.get_doc("ToDo", name)
        # ruleid: frappe-n-plus-one-read-in-loop
        frappe.db.get_value("ToDo", name, "status")


def precise_expansion():
    # ruleid: frappe-get-all-then-get-doc
    names = frappe.get_all("ToDo", pluck="name")
    for name in names:
        # ruleid: frappe-n-plus-one-read-in-loop
        frappe.get_doc("ToDo", name)


def unbounded():
    # ruleid: frappe-unbounded-list-query
    return frappe.get_all("ToDo", limit_page_length=0)


def materialises_only_to_count():
    # ruleid: frappe-materialises-list-only-to-count
    return len(frappe.get_all("ToDo"))


def permission_aware_materialises_only_to_count():
    # ruleid: frappe-materialises-list-only-to-count
    return len(frappe.get_list("ToDo"))


def bounded_materialisation_is_ok():
    # ok: frappe-materialises-list-only-to-count
    return len(frappe.get_all("ToDo", limit=2))


def writes_and_jobs(names):
    for name in names:
        # ruleid: frappe-database-write-in-loop
        frappe.db.set_value("ToDo", name, "status", "Closed")
        # ruleid: frappe-enqueue-in-loop
        frappe.enqueue("app.tasks.process", name=name)


def bulk_is_ok(names):
    # ok: frappe-n-plus-one-read-in-loop
    rows = frappe.get_all(
        "ToDo",
        filters={"name": ["in", names]},
        fields=["name", "status"],
    )
    return {row.name: row.status for row in rows}
