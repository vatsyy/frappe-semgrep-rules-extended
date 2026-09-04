import shlex

import frappe


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
