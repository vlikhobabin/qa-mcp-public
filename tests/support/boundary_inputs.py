"""Fresh inputs shared by validator and public operation-boundary tests."""

from urllib.parse import quote


def encoded(value: str, depth: int) -> str:
    for _ in range(depth):
        value = quote(value, safe="")
    return value


def nested_arrays(count: int) -> object:
    value: object = True
    for _ in range(count):
        value = [value]
    return value
