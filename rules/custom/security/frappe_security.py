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
