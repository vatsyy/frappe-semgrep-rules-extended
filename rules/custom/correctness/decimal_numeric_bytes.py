from decimal import Decimal
import decimal
from typing import Any


def decimal_amount(value: Any) -> Decimal:
    # ruleid: frappe-decimal-amount-stringifies-bytes
    return Decimal(str(value or 0))


def decimal_amount(value):
    # ruleid: frappe-decimal-amount-stringifies-bytes
    return decimal.Decimal(str(value))


def decimal_amount(value: Any) -> Decimal:
    if isinstance(value, bytes):
        value = value.decode("ascii")
    # ok: frappe-decimal-amount-stringifies-bytes
    return Decimal(str(value or 0))


def decimal_amount(value):
    if isinstance(value, bytes):
        value = value.decode("ascii")
    # ok: frappe-decimal-amount-stringifies-bytes
    return decimal.Decimal(str(value))


def decimal_amount(value, other):
    if isinstance(other, bytes):
        other = other.decode("ascii")
    # ruleid: frappe-decimal-amount-stringifies-bytes
    return Decimal(str(value or 0))


def decimal_amount(value, replacement):
    if isinstance(value, bytes):
        value = value.decode("ascii")
    value = replacement
    # ruleid: frappe-decimal-amount-stringifies-bytes
    return Decimal(str(value or 0))


def decimal_amount(value, enabled):
    if enabled:
        if isinstance(value, bytes):
            value = value.decode("ascii")
    # ruleid: frappe-decimal-amount-stringifies-bytes
    return Decimal(str(value or 0))


def decimal_amount(value):
    # ok: frappe-decimal-amount-stringifies-bytes
    return Decimal("0.0000")


def decimal_amount(value):
    # ok: frappe-decimal-amount-stringifies-bytes
    return Decimal(str(123))


def unrelated_converter(value):
    # ok: frappe-decimal-amount-stringifies-bytes
    return Decimal(str(value))
