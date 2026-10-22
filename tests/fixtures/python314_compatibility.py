from __future__ import annotations

import frappe
import requests


type Names = list[str]
type Result[T] = tuple[T, bool]


class Loader[T]:
    def __init__(self, fallback: T) -> None:
        self.fallback = fallback

    def fetch(self, url: str) -> T:
        # expect: frappe-requests-without-timeout
        requests.get(url)
        return self.fallback


def statuses[T: str](names: list[T]) -> list[str | None]:
    # expect: frappe-n-plus-one-read-in-comprehension
    return [frappe.db.get_value("ToDo", name, "status") for name in names]


def first_status[T: str](names: list[T]) -> str | None:
    for name in names:
        # expect: frappe-n-plus-one-read-in-loop
        return frappe.db.get_value("ToDo", name, "status")
    return None


@frappe.whitelist()
def raw_rows[T](company: T, annotation: MissingAtRuntime) -> list[dict]:
    # expect: frappe-whitelisted-raw-sql
    return frappe.db.sql(
        "SELECT name FROM `tabGL Entry` WHERE company=%s",
        company,
        as_dict=True,
    )


@frappe.whitelist()
def caller_path[T](path: str, fallback: T) -> bytes | T:
    if not path:
        return fallback
    # expect: frappe-whitelisted-direct-file-path
    return open(path, "rb").read()


def update_counter[T: int](name: str, amount: T) -> None:
    current = frappe.db.get_value("Counter", name, "value")
    # expect: frappe-read-modify-write
    frappe.db.set_value("Counter", name, "value", current + amount)


def exception_group_syntax(url: str) -> None:
    try:
        int("invalid")
    except ValueError, TypeError:
        # expect: frappe-requests-without-timeout
        requests.post(url)


def bounded_request(url: str) -> None:
    # safe: frappe-requests-without-timeout
    requests.get(url, timeout=(5, 30))

