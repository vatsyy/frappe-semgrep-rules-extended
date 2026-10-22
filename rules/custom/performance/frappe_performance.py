import frappe


def comprehension_reads(names):
    # ruleid: frappe-n-plus-one-read-in-comprehension
    statuses = [frappe.db.get_value("ToDo", name, "status") for name in names]
    # ruleid: frappe-n-plus-one-read-in-comprehension
    docs = [frappe.get_doc("ToDo", name) for name in names]
    return statuses, docs


def comprehension_without_database_reads(names):
    # ok: frappe-n-plus-one-read-in-comprehension
    return [name.upper() for name in names]


def comprehension_constructing_documents(rows):
    # ok: frappe-n-plus-one-read-in-comprehension
    return [frappe.get_doc({"doctype": "ToDo", "description": row.description}) for row in rows]


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


def conditional_doctype_reads(rows):
    # ACF log cleanup checks each configured DocType before purging its logs.
    for row in rows:
        doctype = (getattr(row, "ref_doctype", None) or "").strip()
        if not doctype:
            continue
        # ruleid: frappe-n-plus-one-read-in-loop
        if not frappe.db.exists("DocType", doctype):
            continue
        print(doctype)


def conditional_migration_reads():
    # A bounded migration-style check is still a hotspot, not a proven defect.
    for doctype in ("API Request Log", "Driver Log"):
        # ruleid: frappe-n-plus-one-read-in-loop
        if frappe.db.exists("DocType", doctype):
            print(doctype)


def conditional_status_reads(names, enabled):
    for name in names:
        # ruleid: frappe-n-plus-one-read-in-loop
        if enabled and frappe.db.get_value("ToDo", name, "status") == "Open":
            print(name)
        # ruleid: frappe-n-plus-one-read-in-loop
        elif frappe.db.exists("ToDo", {"name": name, "allocated_to": "Administrator"}):
            print("allocated", name)


def conditional_count_in_while(names):
    while names:
        name = names.pop()
        # ruleid: frappe-n-plus-one-read-in-loop
        if frappe.db.count("ToDo", filters={"reference_name": name}) > 0:
            print(name)


def conditional_list_reads(names):
    for name in names:
        # ruleid: frappe-n-plus-one-read-in-loop
        if frappe.get_list("ToDo", filters={"reference_name": name}, limit=1):
            print(name)


def query_guard_outside_loop_is_ok(names):
    # ok: frappe-n-plus-one-read-in-loop
    if frappe.db.exists("DocType", "ToDo"):
        for name in names:
            print(name)


def iterable_query_with_in_memory_guard_is_ok():
    # ok: frappe-n-plus-one-read-in-loop
    for row in frappe.get_all("ToDo", fields=["name", "status"]):
        if row.status == "Open":
            print(row.name)


def prefetched_guard_in_loop_is_ok(names):
    # ok: frappe-n-plus-one-read-in-loop
    existing = set(frappe.get_all("ToDo", pluck="name"))
    for name in names:
        # ok: frappe-n-plus-one-read-in-loop
        if name in existing:
            print(name)


def unrelated_conditional_call_is_ok(names, records):
    for name in names:
        # ok: frappe-n-plus-one-read-in-loop
        if records.exists(name):
            print(name)


def conditional_document_construction_is_ok(rows):
    for row in rows:
        # ok: frappe-n-plus-one-read-in-loop
        if frappe.get_doc({"doctype": "ToDo", "description": row.description}):
            print(row.description)


def sql_reads_and_writes(names):
    for name in names:
        # ruleid: frappe-n-plus-one-read-in-loop
        frappe.db.sql("SELECT status FROM `tabToDo` WHERE name=%s", name)
        # ok: frappe-n-plus-one-read-in-loop
        frappe.db.sql("UPDATE `tabToDo` SET status='Closed' WHERE name=%s", name)


def query_producing_the_iterable_is_ok():
    # ok: frappe-n-plus-one-read-in-loop
    for row in frappe.get_all("ToDo", fields=["name"]):
        print(row.name)

    # ok: frappe-n-plus-one-read-in-loop
    for row in frappe.db.sql("SELECT name FROM `tabToDo`", as_dict=True):
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
