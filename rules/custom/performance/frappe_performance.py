import frappe


def direct_reads(names):
    for name in names:
        # ruleid: frappe-n-plus-one-read-in-loop
        frappe.get_doc("ToDo", name)
        # ruleid: frappe-n-plus-one-read-in-loop
        frappe.db.get_value("ToDo", name, "status")


def direct_reads_in_while(names):
    while names:
        # ruleid: frappe-n-plus-one-read-in-loop
        frappe.db.get_single_value("System Settings", "country")
        names.pop()


def query_producing_the_iterable_is_ok():
    # ok: frappe-n-plus-one-read-in-loop
    for row in frappe.get_all("ToDo", fields=["name"]):
        print(row.name)


def constructing_a_new_document_is_ok(rows):
    for row in rows:
        # ok: frappe-n-plus-one-read-in-loop
        frappe.get_doc({"doctype": "ToDo", "description": row.description})


def precise_expansion():
    # ruleid: frappe-get-all-then-get-doc
    names = frappe.get_all("ToDo", pluck="name")
    for name in names:
        # ruleid: frappe-n-plus-one-read-in-loop
        frappe.get_doc("ToDo", name)


def bulk_names_without_document_expansion_is_ok():
    # ok: frappe-get-all-then-get-doc
    return frappe.get_all("ToDo", pluck="name")


def unbounded():
    # ruleid: frappe-unbounded-list-query
    return frappe.get_all("ToDo", limit_page_length=0)


def bounded_query_is_ok():
    # ok: frappe-unbounded-list-query
    return frappe.get_all("ToDo", limit_page_length=50)


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


def one_write_and_one_job_are_ok(name):
    # ok: frappe-database-write-in-loop
    frappe.db.set_value("ToDo", name, "status", "Closed")
    # ok: frappe-enqueue-in-loop
    frappe.enqueue("app.tasks.process", name=name)


def bulk_is_ok(names):
    # ok: frappe-n-plus-one-read-in-loop
    rows = frappe.get_all(
        "ToDo",
        filters={"name": ["in", names]},
        fields=["name", "status"],
    )
    return {row.name: row.status for row in rows}
