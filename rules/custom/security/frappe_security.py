import csv
import shlex
from io import StringIO

import frappe
from frappe import _
from frappe.utils.csvutils import UnicodeWriter, escape_formula_injection


def direct_python_execution(expression):
    # ruleid: frappe-direct-python-eval-exec
    return eval(expression)


def safe_data_parsing(expression):
    # ok: frappe-direct-python-eval-exec
    return frappe.parse_json(expression)


def dynamic_template(template, context):
    # ruleid: frappe-dynamic-template-with-default-globals
    return frappe.render_template(template, context)


def restricted_dynamic_template(template, context):
    # ok: frappe-dynamic-template-with-default-globals
    return frappe.render_template(template, context, restrict_globals=True)


def fixed_template(context):
    # ok: frappe-dynamic-template-with-default-globals
    return frappe.render_template("templates/emails/status.html", context)


def enforce_permission():
    # ruleid: frappe-ignored-permission-result
    frappe.has_permission("Private Record", "read")


def combine_permissions():
    # ok: frappe-ignored-permission-result
    allowed = frappe.has_permission("Private Record", "select") or frappe.has_permission(
        "Private Record", "read"
    )
    return allowed


def permission_controls_keyword_action(primary_action):
    # ok: frappe-ignored-permission-result
    return dict(
        primary_action=primary_action if frappe.has_permission("System Health Report") else None
    )


@frappe.whitelist()
def print_to_caller_path(file_path):
    # ruleid: frappe-whitelisted-direct-file-path
    with open(file_path, "wb") as output:
        output.write(b"document")


@frappe.whitelist()
def read_allowed_license(license_type):
    allowed = {"mit": "/srv/licenses/mit.txt"}
    # ok: frappe-whitelisted-direct-file-path
    with open(allowed[license_type]) as source:
        return source.read()


def inspect_backup(sql_file_path):
    # ruleid: frappe-interpolated-execute-in-shell
    return frappe.utils.execute_in_shell(f"file {sql_file_path}")


def inspect_fixed_backup():
    # ok: frappe-interpolated-execute-in-shell
    return frappe.utils.execute_in_shell("file /srv/backups/current.sql")


def inspect_assigned_backup(sql_file_path):
    command = f"file {sql_file_path}"
    # ruleid: frappe-interpolated-execute-in-shell
    return frappe.utils.execute_in_shell(command)


def decrypt_assigned_backup(passphrase, file_path):
    template = "gpg --passphrase {passphrase} -d {file_path}"
    command = template.format(passphrase=passphrase, file_path=file_path)
    # ruleid: frappe-interpolated-execute-in-shell
    return frappe.utils.execute_in_shell(command)


def inspect_safe_argument_vector(sql_file_path):
    command = ["file", sql_file_path]
    # ok: frappe-interpolated-execute-in-shell
    return frappe.utils.execute_in_shell(command)


def restore_joined_pipeline(sql_file_path):
    command = ["cat", sql_file_path, "|", "mysql"]
    # ruleid: frappe-interpolated-execute-in-shell
    return frappe.utils.execute_in_shell(" ".join(command))


def inspect_shell_quoted_arguments(sql_file_path):
    command = shlex.join(["file", sql_file_path])
    # ok: frappe-interpolated-execute-in-shell
    return frappe.utils.execute_in_shell(command)


@frappe.whitelist()
def raw_sql_endpoint(company):
    # ruleid: frappe-whitelisted-raw-sql
    return frappe.db.sql(
        "SELECT name FROM `tabAccount` WHERE company=%s",
        company,
        as_dict=True,
    )


def internal_raw_sql(company):
    # ok: frappe-whitelisted-raw-sql
    return frappe.db.sql(
        "SELECT name FROM `tabAccount` WHERE company=%s",
        company,
        as_dict=True,
    )


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


@frappe.whitelist()
def role_gated_rows():
    frappe.only_for("System Manager")
    # ok: frappe-whitelisted-permission-bypass
    return frappe.get_all("Private Record", fields=["name", "secret"])


@frappe.whitelist()
def doctype_gated_rows():
    frappe.has_permission("Private Record", "read", throw=True)
    # ok: frappe-whitelisted-permission-bypass
    return frappe.get_all("Private Record", fields=["name", "secret"])


@frappe.whitelist()
def doctype_keyword_gated_delete(name):
    frappe.has_permission(doctype="Private Record", ptype="delete", throw=True)
    # ok: frappe-whitelisted-permission-bypass
    frappe.delete_doc("Private Record", name, ignore_permissions=True)


@frappe.whitelist()
def unrelated_doctype_guard():
    frappe.has_permission("Public Record", "read", throw=True)
    # ruleid: frappe-whitelisted-permission-bypass
    return frappe.get_all("Private Record", fields=["name", "secret"])


@frappe.whitelist()
def guard_after_bypass():
    # ruleid: frappe-whitelisted-permission-bypass
    rows = frappe.get_all("Private Record", fields=["name", "secret"])
    frappe.only_for("System Manager")
    return rows


@frappe.whitelist()
def guard_in_one_branch(include_secret):
    if include_secret:
        frappe.only_for("System Manager")
    # ruleid: frappe-whitelisted-permission-bypass
    return frappe.get_all("Private Record", fields=["name", "secret"])


@frappe.whitelist()
def document_gated_save(name):
    doc = frappe.get_doc("Private Record", name)
    doc.check_permission("write")
    doc.secret = "updated"
    # ok: frappe-whitelisted-permission-bypass
    doc.save(ignore_permissions=True)


@frappe.whitelist()
def document_keyword_gated_submit(name):
    doc = frappe.get_doc("Private Record", name)
    frappe.has_permission("Private Record", "submit", doc=doc, throw=True)
    # ok: frappe-whitelisted-permission-bypass
    doc.submit(ignore_permissions=True)


@frappe.whitelist()
def document_positional_gated_flag(name):
    doc = frappe.get_doc("Private Record", name)
    frappe.has_permission("Private Record", "write", doc, throw=True)
    # ok: frappe-whitelisted-permission-bypass
    doc.flags.ignore_permissions = True


@frappe.whitelist()
def unrelated_document_guard(parent_name, name):
    parent = frappe.get_doc("Public Record", parent_name)
    parent.check_permission("write")
    doc = frappe.get_doc("Private Record", name)
    # ruleid: frappe-whitelisted-permission-bypass
    doc.save(ignore_permissions=True)


@frappe.whitelist()
def unchecked_permission_result(name):
    doc = frappe.get_doc("Private Record", name)
    # ruleid: frappe-ignored-permission-result
    frappe.has_permission("Private Record", "write", doc)
    # ruleid: frappe-whitelisted-permission-bypass
    doc.save(ignore_permissions=True)


def run_as_administrator(callback):
    previous_user = frappe.session.user
    # ruleid: frappe-setuser-outside-tests
    frappe.set_user("Administrator")
    try:
        return callback()
    finally:
        # ruleid: frappe-setuser-outside-tests
        frappe.set_user(previous_user)


def current_user_name():
    # ok: frappe-setuser-outside-tests
    return frappe.session.user


def export_bank_lines(lines):
    buffer = StringIO()
    writer = csv.writer(buffer)
    # ok: frappe-csv-row-without-formula-escape
    writer.writerow(["Date", "Description", _("Amount")])
    for line in lines:
        # ruleid: frappe-csv-row-without-formula-escape
        writer.writerow([line.date, line.description, line.amount])
    return buffer.getvalue()


def export_rows(headers, rows):
    buffer = StringIO()
    writer = csv.writer(buffer)
    # ruleid: frappe-csv-row-without-formula-escape
    writer.writerow(headers)
    # ruleid: frappe-csv-row-without-formula-escape
    writer.writerows(rows)
    return buffer.getvalue()


def export_with_literal_header(rows):
    buffer = StringIO()
    writer = csv.writer(buffer)
    header = ["Account", "Debit", "Credit"]
    # ruleid: frappe-csv-row-without-formula-escape
    writer.writerow([rows[0].account, rows[0].description])
    # ok: frappe-csv-row-without-formula-escape
    writer.writerow(header)
    # ok: frappe-csv-row-without-formula-escape
    writer.writerows([escape_formula_injection(cell) for cell in row] for row in rows)
    return buffer.getvalue()


def export_with_computed_header(columns, rows):
    buffer = StringIO()
    writer = csv.writer(buffer)
    header = [column.label for column in columns]
    # ruleid: frappe-csv-row-without-formula-escape
    writer.writerow(header)
    return buffer.getvalue()


def export_escaped_beforehand(rows):
    escaped = [[escape_formula_injection(cell) for cell in row] for row in rows]
    buffer = StringIO()
    writer = csv.writer(buffer)
    # ok: frappe-csv-row-without-formula-escape
    writer.writerows(escaped)
    return buffer.getvalue()


def export_through_unicode_writer(rows):
    writer = UnicodeWriter()
    for row in rows:
        # ok: frappe-csv-row-without-formula-escape
        writer.writerow(row)
    return writer.getvalue()


def permission_result_boundaries(doc, should_throw):
    # ruleid: frappe-ignored-permission-result
    frappe.has_permission("ToDo", doc=doc, throw=False)
    # ruleid: frappe-ignored-permission-result
    frappe.has_permission("ToDo", doc=doc, throw=0)
    # ruleid: frappe-ignored-permission-result
    frappe.has_permission("ToDo", doc=doc, throw=None)
    # ok: frappe-ignored-permission-result
    frappe.has_permission("ToDo", doc=doc, throw=True)
    # ok: frappe-ignored-permission-result
    frappe.has_permission("ToDo", doc=doc, throw=should_throw)
    # ok: frappe-ignored-permission-result
    consume(frappe.has_permission("ToDo", doc=doc))
    # ok: frappe-ignored-permission-result
    permissions.append(frappe.has_permission("ToDo", doc=doc))
    # ok: frappe-ignored-permission-result
    while frappe.has_permission("ToDo", doc=doc):
        break


@frappe.whitelist()
def database_wrapper_permissions():
    # ruleid: frappe-whitelisted-permission-bypass
    frappe.db.get_all("ToDo")
    # ruleid: frappe-whitelisted-permission-bypass
    frappe.db.get_list("ToDo", ignore_permissions=True)
    # ok: frappe-whitelisted-permission-bypass
    frappe.db.get_list("ToDo")
    # ok: frappe-whitelisted-permission-bypass
    frappe.db.get_list("ToDo", ignore_permissions=False)


def internal_database_wrapper():
    # ok: frappe-whitelisted-permission-bypass
    return frappe.db.get_all("ToDo")


def interpolated_templates(user_template):
    # ruleid: frappe-dynamic-template-with-default-globals
    frappe.render_template(f"Header {user_template}", {})
    # ruleid: frappe-dynamic-template-with-default-globals
    frappe.render_template("Header {}".format(user_template), {})
    # ruleid: frappe-dynamic-template-with-default-globals
    frappe.render_template("Header %s" % user_template, {})
    # ruleid: frappe-dynamic-template-with-default-globals
    frappe.render_template("Header " + user_template, {})
    # ok: frappe-dynamic-template-with-default-globals
    frappe.render_template("Fixed content", {})
    # ok: frappe-dynamic-template-with-default-globals
    frappe.render_template(r"Fixed content", {})
    # ok: frappe-dynamic-template-with-default-globals
    frappe.render_template(f"Header {user_template}", {}, restrict_globals=True)
    # ok: frappe-dynamic-template-with-default-globals
    frappe.render_template("templates/{}.html".format(user_template), {}, is_path=True)


def permission_consumers_and_positional_throw(doc, should_throw):
    # ok: frappe-ignored-permission-result
    log(allowed=frappe.has_permission("ToDo", doc=doc))
    # ok: frappe-ignored-permission-result
    frappe.has_permission("ToDo", doc=doc) or deny()
    # ok: frappe-ignored-permission-result
    frappe.has_permission("ToDo", doc=doc) and perform_action()
    # ok: frappe-ignored-permission-result
    frappe.has_permission("ToDo", "read", doc, None, True)
    # ok: frappe-ignored-permission-result
    frappe.has_permission("ToDo", "read", doc, None, should_throw)
    # ruleid: frappe-ignored-permission-result
    frappe.has_permission("ToDo", "read", doc, None, False)
    # ruleid: frappe-ignored-permission-result
    frappe.has_permission("ToDo", "read", doc, None, 0)
    # ruleid: frappe-ignored-permission-result
    frappe.has_permission("ToDo", "read", doc, None, False, debug=True)
    # ruleid: frappe-ignored-permission-result
    frappe.has_permission("ToDo", doc=doc)


@frappe.whitelist()
def fixed_path_reassignment(path):
    path = "/srv/fixed.txt"
    # ok: frappe-whitelisted-direct-file-path
    return open(path).read()


@frappe.whitelist()
def copied_caller_path(path):
    target = path
    # ruleid: frappe-whitelisted-direct-file-path
    return open(target).read()


@frappe.whitelist()
def conditional_path_reassignment(path, use_fixed):
    if use_fixed:
        path = "/srv/fixed.txt"
    # ruleid: frappe-whitelisted-direct-file-path
    return open(path).read()


@frappe.whitelist()
def fixed_alias_after_reassignment(path):
    path = "/srv/fixed.txt"
    target = path
    # ok: frappe-whitelisted-direct-file-path
    return open(target).read()


def shell_string_operators(value):
    # ruleid: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo %s" % value)
    command = "echo " + value
    # ruleid: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell(command)
    # ruleid: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell(value + " --help")
    # ok: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo " + "fixed")
    # ok: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo " + shlex.quote(value))
    # ok: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo %s" % shlex.quote(value))


@frappe.whitelist()
def typed_caller_path(path: str):
    # ruleid: frappe-whitelisted-direct-file-path
    return open(path).read()


@frappe.whitelist()
def caller_path_list(paths):
    # ruleid: frappe-whitelisted-direct-file-path
    return open(paths[0]).read()


@frappe.whitelist()
def keyword_file_paths(path):
    # ruleid: frappe-whitelisted-direct-file-path
    open(file=path).read()
    path = "/srv/fixed.txt"
    # ok: frappe-whitelisted-direct-file-path
    open(file=path).read()


def keyword_shell_command(value):
    # ruleid: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell(cmd="echo %s" % value)
    # ok: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell(cmd="echo %s" % shlex.quote(value))


def shell_tuple_quoting(first, second):
    # ok: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo %s %s" % (shlex.quote(first), shlex.quote(second)))
    # ruleid: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo %s %s" % (shlex.quote(first), second))
    # ruleid: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo %s %s" % (first, second))
    # ok: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo %s %s" % ("fixed", shlex.quote(second)))


@frappe.whitelist()
def numeric_permission_bypass(doc):
    # ruleid: frappe-whitelisted-permission-bypass
    frappe.get_list("ToDo", ignore_permissions=1)
    # ruleid: frappe-whitelisted-permission-bypass
    frappe.db.get_list("ToDo", ignore_permissions=1)
    # ruleid: frappe-whitelisted-permission-bypass
    doc.save(ignore_permissions=1)
    # ruleid: frappe-whitelisted-permission-bypass
    doc.flags.ignore_permissions = 1
    # ok: frappe-whitelisted-permission-bypass
    frappe.get_list("ToDo", ignore_permissions=0)
    # ok: frappe-whitelisted-permission-bypass
    doc.save(ignore_permissions=False)


def yielded_permission():
    # ok: frappe-ignored-permission-result
    yield frappe.has_permission("ToDo")
    # ruleid: frappe-ignored-permission-result
    frappe.has_permission("ToDo")


def shell_quoted_interpolation(value, other):
    escaped = shlex.quote(value)
    # ok: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo " + escaped)
    # ok: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell(f"echo {shlex.quote(value)}")
    # ok: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo {}".format(shlex.quote(value)))
    # ruleid: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell(f"echo {shlex.quote(value)} {other}")
    # ruleid: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo {} {}".format(shlex.quote(value), other))
    escaped = other
    # ruleid: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo " + escaped)


def shell_quote_after_composition(value, other):
    command = shlex.quote(f"echo {value}")
    # ok: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo " + command)
    escaped = shlex.quote(value)
    mixed = escaped + " " + other
    # ruleid: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo " + mixed)
    if other:
        escaped = other
    # ruleid: frappe-interpolated-execute-in-shell
    frappe.utils.execute_in_shell("echo " + escaped)


@frappe.whitelist()
def fixed_path_allowlist(path):
    if path not in ("/srv/a.txt", "/srv/b.txt"):
        frappe.throw("Invalid path")
    # ok: frappe-whitelisted-direct-file-path
    return open(path).read()


@frappe.whitelist()
def nonterminating_path_allowlist(path):
    if path not in ("/srv/a.txt", "/srv/b.txt"):
        frappe.log_error("Invalid path")
    # ruleid: frappe-whitelisted-direct-file-path
    return open(path).read()


@frappe.whitelist()
def dynamic_path_allowlist(path, extra):
    if path not in ("/srv/a.txt", extra):
        frappe.throw("Invalid path")
    # ruleid: frappe-whitelisted-direct-file-path
    return open(path).read()


@frappe.whitelist()
def overwritten_path_allowlist(path, replacement):
    if path not in ("/srv/a.txt", "/srv/b.txt"):
        frappe.throw("Invalid path")
    path = replacement
    # ruleid: frappe-whitelisted-direct-file-path
    return open(path).read()


@frappe.whitelist()
def caught_path_allowlist(path):
    try:
        if path not in ("/srv/a.txt", "/srv/b.txt"):
            frappe.throw("Invalid path")
    except Exception:
        pass
    # ruleid: frappe-whitelisted-direct-file-path
    return open(path).read()


@frappe.whitelist()
def path_opened_before_rejection(path):
    if path not in ("/srv/a.txt", "/srv/b.txt"):
        # ruleid: frappe-whitelisted-direct-file-path
        open(path).read()
        frappe.throw("Invalid path")


@frappe.whitelist(methods=["POST"])
def role_gated_raw_read():
    frappe.only_for("System Manager")
    # ok: frappe-whitelisted-raw-sql
    return frappe.db.sql("select name from `tabGL Entry`")


@frappe.whitelist()
def raw_read_before_role_gate():
    # ruleid: frappe-whitelisted-raw-sql
    rows = frappe.db.sql("select name from `tabGL Entry`")
    frappe.only_for("System Manager")
    return rows


@frappe.whitelist()
def role_gate_in_unshared_branch(strict):
    if strict:
        frappe.only_for("System Manager")
    # ruleid: frappe-whitelisted-raw-sql
    return frappe.db.sql("select name from `tabGL Entry`")
