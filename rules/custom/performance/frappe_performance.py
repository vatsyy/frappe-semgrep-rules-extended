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


def comprehension_expression_boundaries(names):
    # ruleid: frappe-n-plus-one-read-in-comprehension
    filtered = [frappe.db.get_value("ToDo", name, "status") for name in names if name]
    # ruleid: frappe-n-plus-one-read-in-comprehension
    predicate = [name for name in names if frappe.db.exists("ToDo", name)]
    # ruleid: frappe-n-plus-one-read-in-comprehension
    wrapped = [str(frappe.db.get_value("ToDo", name, "status")) for name in names]
    # ruleid: frappe-n-plus-one-read-in-comprehension
    statuses = {str(frappe.db.get_value("ToDo", name, "status")) for name in names if name}
    # ruleid: frappe-n-plus-one-read-in-comprehension
    pending = (name for name in names if frappe.db.exists("ToDo", name))
    # ruleid: frappe-n-plus-one-read-in-comprehension
    mapped = {name: str(frappe.db.get_value("ToDo", name, "status")) for name in names if name}
    # ruleid: frappe-n-plus-one-read-in-comprehension
    keys = {frappe.db.get_value("ToDo", name, "status"): name for name in names}
    # ruleid: frappe-n-plus-one-read-in-comprehension
    docs = [frappe.get_doc("ToDo", name) for name in names if name]
    # ok: frappe-n-plus-one-read-in-comprehension
    once = [name for name in frappe.get_all("ToDo", pluck="name") if name]
    # ok: frappe-n-plus-one-read-in-comprehension
    constructed = [frappe.get_doc({"doctype": "ToDo", "description": name}) for name in names if name]
    # ok: frappe-n-plus-one-read-in-comprehension
    cached = {name: str(name) for name in names if name}


def parenthesised_comprehension_receivers(items):
    # Regression from Letter Reconciliation: inspecting this expression must
    # not produce a Semgrep String.sub / Bytes.sub analysis error.
    # ok: frappe-n-plus-one-read-in-comprehension
    accounts = {(item.get("account") or "").strip() for item in items if item.get("account")}
    # ruleid: frappe-n-plus-one-read-in-comprehension
    descriptions = {(frappe.db.get_value("ToDo", name, "description") or "").strip() for name in items}


def bulk_query_with_comprehension_filter(rows):
    # ok: frappe-n-plus-one-read-in-comprehension
    return frappe.get_all("ToDo", filters={"name": ["in", [row["name"] for row in rows]]})


def count_zero_limits(limit):
    # ruleid: frappe-materialises-list-only-to-count
    len(frappe.get_all("ToDo", limit=0))
    # ruleid: frappe-unbounded-list-query, frappe-materialises-list-only-to-count
    len(frappe.get_all("ToDo", limit_page_length=0))
    # ruleid: frappe-materialises-list-only-to-count
    len(frappe.db.get_all("ToDo", limit=0))
    # ruleid: frappe-unbounded-list-query, frappe-materialises-list-only-to-count
    len(frappe.db.get_list("ToDo", limit_page_length=0))
    # ok: frappe-materialises-list-only-to-count
    len(frappe.get_all("ToDo", limit=10))
    # ok: frappe-materialises-list-only-to-count
    len(frappe.get_all("ToDo", limit=limit))
    # ok: frappe-materialises-list-only-to-count
    len(frappe.get_all("ToDo", limit=0, limit_page_length=10))


def two_generator_reads(groups):
    # ruleid: frappe-n-plus-one-read-in-comprehension
    values = [frappe.db.get_value("ToDo", name, "status") for group in groups for name in group]
    # ruleid: frappe-n-plus-one-read-in-comprehension
    filtered = {frappe.db.get_value("ToDo", name, "status") for group in groups for name in group if name}
    # ruleid: frappe-n-plus-one-read-in-comprehension
    existing = (name for group in groups for name in group if frappe.db.exists("ToDo", name))
    # ruleid: frappe-n-plus-one-read-in-comprehension
    docs = {name: frappe.get_doc("ToDo", name) for group in groups for name in group}
    # ok: frappe-n-plus-one-read-in-comprehension
    plain = [str(name) for group in groups for name in group]
    # ok: frappe-n-plus-one-read-in-comprehension
    outer_query = [name for group in frappe.get_all("ToDo", fields=["name"]) for name in group]
    # ok: frappe-n-plus-one-read-in-comprehension
    bulk_query = frappe.get_all("ToDo", filters={"name": ["in", [name for group in groups for name in group]]})


def effective_query_limits(limit):
    # ok: frappe-unbounded-list-query
    frappe.get_all("ToDo", limit_page_length=0, limit=10)
    # ok: frappe-unbounded-list-query
    frappe.db.get_list("ToDo", limit_page_length=0, page_length=10)
    # ok: frappe-unbounded-list-query
    frappe.get_all("ToDo", limit_page_length=0, limit=limit)
    # ruleid: frappe-unbounded-list-query
    frappe.get_all("ToDo", limit_page_length=0, limit=0)
    # ruleid: frappe-unbounded-list-query
    frappe.get_all("ToDo", limit_page_length=0, page_length=0)
    # ruleid: frappe-unbounded-list-query
    frappe.get_all("ToDo", limit_page_length=0, limit=0, page_length=10)


def deferred_reads(names, callbacks):
    for name in names:
        def fetch_later():
            # ok: frappe-n-plus-one-read-in-loop
            return frappe.db.get_value("ToDo", name, "status")
        callbacks.append(fetch_later)
        # ruleid: frappe-n-plus-one-read-in-loop
        value = frappe.db.get_value("ToDo", name, "status")


def deferred_and_conditional_reads(names, callbacks, enabled):
    for name in names:
        # ok: frappe-n-plus-one-read-in-loop
        callbacks.append(lambda: frappe.db.get_value("ToDo", name, "status"))
        async def async_fetch_later():
            # ok: frappe-n-plus-one-read-in-loop
            return frappe.db.sql("SELECT status FROM `tabToDo` WHERE name=%s", name)
        callbacks.append(async_fetch_later)
        if enabled:
            try:
                # ruleid: frappe-n-plus-one-read-in-loop
                frappe.db.get_value("ToDo", name, "status")
            except Exception:
                pass


def iterable_and_body_same_api():
    # ok: frappe-n-plus-one-read-in-loop
    for row in frappe.get_all("ToDo", fields=["name"]):
        # ruleid: frappe-n-plus-one-read-in-loop
        frappe.get_all("ToDo", filters={"reference_name": row.name})
