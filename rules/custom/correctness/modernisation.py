import frappe
import requests
from requests import get as http_get


def outbound_calls(url, options, timeout):
    # ruleid: frappe-requests-without-timeout
    requests.get(url)
    # ruleid: frappe-requests-without-timeout
    requests.post(url, json={"ready": True}, timeout=None)
    # ruleid: frappe-requests-without-timeout
    requests.request("PUT", url)
    # ruleid: frappe-requests-without-timeout
    http_get(url)
    # ok: frappe-requests-without-timeout
    requests.get(url, timeout=(5, 30))
    # ok: frappe-requests-without-timeout
    requests.get(url, timeout=timeout)
    # ok: frappe-requests-without-timeout
    requests.get(url, **options)
    # ok: frappe-requests-without-timeout
    requests.Session().get(url)
    # ruleid: frappe-requests-without-timeout
    requests.get(url, timeout=None, **options)


def increment(name):
    current = frappe.db.get_value("Counter", name, "value")
    # ruleid: frappe-read-modify-write
    frappe.db.set_value("Counter", name, "value", current + 1)


def decrement(name, amount):
    current = frappe.db.get_value("Counter", name, "value")
    current -= amount
    # ruleid: frappe-read-modify-write
    frappe.db.set_value("Counter", name, "value", current)


def subtract(name, amount):
    current = frappe.db.get_value("Counter", name, "value")
    # ruleid: frappe-read-modify-write
    frappe.db.set_value("Counter", name, "value", current - amount)


def add_in_place(name, amount):
    current = frappe.db.get_value("Counter", name, "value")
    current += amount
    # ruleid: frappe-read-modify-write
    frappe.db.set_value("Counter", name, "value", current)


def locked_increment(name):
    current = frappe.db.get_value("Counter", name, "value", for_update=True)
    # ok: frappe-read-modify-write
    frappe.db.set_value("Counter", name, "value", current + 1)


def different_record(name, other):
    current = frappe.db.get_value("Counter", name, "value")
    # ok: frappe-read-modify-write
    frappe.db.set_value("Counter", other, "value", current + 1)


def different_field(name):
    current = frappe.db.get_value("Counter", name, "value")
    # ok: frappe-read-modify-write
    frappe.db.set_value("Counter", name, "previous_value", current + 1)


def replace_with_independent_value(name):
    current = frappe.db.get_value("Counter", name, "value")
    # ok: frappe-read-modify-write
    frappe.db.set_value("Counter", name, "value", 1)


def intervening_operation(name):
    current = frappe.db.get_value("Counter", name, "value")
    acquire_lock_and_recheck(name)
    # ok: frappe-read-modify-write
    frappe.db.set_value("Counter", name, "value", current + 1)


def deferred_writer(name):
    current = frappe.db.get_value("Counter", name, "value")
    def later():
        # ok: frappe-read-modify-write
        frappe.db.set_value("Counter", name, "value", current + 1)
    return later


def write_then_enqueue(name):
    frappe.db.set_value("ToDo", name, "status", "Closed")
    # ruleid: frappe-enqueue-after-write
    frappe.enqueue("app.process", name=name)


def explicit_early_enqueue(name):
    frappe.db.set_value("ToDo", name, "status", "Closed")
    # ruleid: frappe-enqueue-after-write
    frappe.enqueue("app.process", name=name, enqueue_after_commit=False)


def deferred_enqueue(name):
    frappe.db.set_value("ToDo", name, "status", "Closed")
    # ok: frappe-enqueue-after-write
    frappe.enqueue("app.process", name=name, enqueue_after_commit=True)


def committed_enqueue(name):
    frappe.db.set_value("ToDo", name, "status", "Closed")
    frappe.db.commit()
    # ok: frappe-enqueue-after-write
    frappe.enqueue("app.process", name=name)


def synchronous_work(name):
    frappe.db.set_value("ToDo", name, "status", "Closed")
    # ok: frappe-enqueue-after-write
    frappe.enqueue("app.process", name=name, now=True)


def supplied_enqueue_options(name, options):
    frappe.db.set_value("ToDo", name, "status", "Closed")
    # ok: frappe-enqueue-after-write
    frappe.enqueue("app.process", name=name, **options)


def enqueue_document_after_write(name):
    frappe.db.set_value("ToDo", name, "status", "Closed")
    # ruleid: frappe-enqueue-after-write
    frappe.enqueue_doc("ToDo", name, "notify", enqueue_after_commit=False)


def read_then_enqueue(name):
    frappe.db.get_value("ToDo", name, "status")
    # ok: frappe-enqueue-after-write
    frappe.enqueue("app.process", name=name)


def deferred_enqueue_definition(name):
    frappe.db.set_value("ToDo", name, "status", "Closed")
    def later():
        # ok: frappe-enqueue-after-write
        frappe.enqueue("app.process", name=name)
    return later


def configured_enqueue(name, policy):
    frappe.db.set_value("ToDo", name, "status", "Closed")
    # ok: frappe-enqueue-after-write
    frappe.enqueue("app.process", name=name, enqueue_after_commit=policy)


def inline_enqueue(name):
    frappe.db.set_value("ToDo", name, "status", "Closed")
    # ok: frappe-enqueue-after-write
    frappe.enqueue("app.process", name=name, is_async=False)


class Controller:
    def on_update(self):
        frappe.db.set_value("ToDo", self.name, "status", "Closed")
        # ruleid: frappe-enqueue-after-write
        frappe.enqueue("app.process", name=self.name, enqueue_after_commit=False)

    def existing_upstream_coverage(self):
        frappe.db.set_value("ToDo", self.name, "status", "Closed")
        # ok: frappe-enqueue-after-write
        frappe.enqueue("app.process", name=self.name)
