import requests


def structured_template(name: str):
    requests.get("https://example.invalid", timeout=5)
    return t"Hello {name}"
