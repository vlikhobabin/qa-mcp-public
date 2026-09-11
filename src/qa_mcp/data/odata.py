"""Card 105 (E-XV) — thin READ-ONLY 1C OData client + data-layer assertion.

qa-mcp asserts what a UI action did AGAINST the data layer (standard 1C OData), in one scenario — beyond Vanessa
(UI-only). The HTTP fetch is injectable (`fetcher=`) so the query-building + assertion logic is fully
unit-testable offline with no network. The real fetch hits the lab's standard OData (published via Apache, e.g.
`http://127.0.0.1:8316/<pub>/odata/standard.odata`, basic auth `Администратор:`) — read-only.

Config (params override env): base URL `QA_MCP_ODATA_URL`, user `QA_MCP_ODATA_USER`, password
`QA_MCP_ODATA_PASSWORD`.

DEPRECATED for a test-client-held base (card 125 #1): a file/server infobase opened by a «Клиент тестирования» is
held under an EXCLUSIVE lock, so this out-of-process OData reader cannot open it — an OData read-back of what the
running test client just did is impossible on the same base. Verify UI writes through the SAME test client's
protocol value-read instead (`write_form_fields_by_label`'s value-read `committed`, `read_record`,
`read_form_descriptor`, `read_table_cell`). This client stays valid only against a SEPARATELY published,
non-exclusive OData endpoint (a different base, or a server infobase not held for testing); it is retained (not
removed) pending the scenario/autofill/regression/gherkin cleanup.
"""
from __future__ import annotations

import base64
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from typing import Any, Callable

from ..config import (
    ODATA_DEFAULT_PASSWORD,
    ODATA_DEFAULT_URL,
    ODATA_DEFAULT_USER,
    ODATA_PASSWORD_ENV,
    ODATA_URL_ENV,
    ODATA_USER_ENV,
    Settings,
)

Fetcher = Callable[[str, "dict[str, str]"], "dict[str, Any]"]

URL_ENV = ODATA_URL_ENV
USER_ENV = ODATA_USER_ENV
PASSWORD_ENV = ODATA_PASSWORD_ENV

_GUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def _http_fetch(url: str, headers: dict[str, str]) -> dict[str, Any]:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 — lab-local OData URL
        return json.loads(resp.read().decode("utf-8"))


class ODataClient:
    """Minimal read-only 1C standard-OData client. Pass ``fetcher`` to unit-test offline."""

    def __init__(
        self,
        base_url: str | None = None,
        user: str | None = None,
        password: str | None = None,
        *,
        fetcher: Fetcher | None = None,
    ) -> None:
        settings = Settings.from_env()
        self.base_url = (
            base_url if base_url is not None else settings.odata_url or ODATA_DEFAULT_URL
        ).rstrip("/")
        self.user = user if user is not None else settings.odata_user or ODATA_DEFAULT_USER
        self.password = password if password is not None else settings.odata_password or ODATA_DEFAULT_PASSWORD
        self.fetcher = fetcher or _http_fetch

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.user or self.password:
            token = base64.b64encode(f"{self.user}:{self.password}".encode()).decode()
            headers["Authorization"] = f"Basic {token}"
        return headers

    def build_url(
        self,
        entity_set: str,
        *,
        key: str | None = None,
        select: list[str] | str | None = None,
        filter: str | None = None,
        top: int | None = None,
    ) -> str:
        if not self.base_url:
            raise ValueError(f"OData base_url not configured (set {URL_ENV} or pass base_url=)")
        # The entity-set name (and a string key) are almost always Cyrillic on a real 1C config
        # (Catalog_Банки, Document_Заказ, …); percent-encode them so the request line is ASCII-safe —
        # an unencoded Cyrillic path raises UnicodeEncodeError in urllib before the request is sent.
        path = f"{self.base_url}/{urllib.parse.quote(entity_set)}"
        if key is not None:
            path += f"(guid'{key}')" if _GUID_RE.match(key) else f"('{urllib.parse.quote(key)}')"
        params: list[tuple[str, str]] = []
        if select:
            params.append(("$select", ",".join(select) if isinstance(select, (list, tuple)) else select))
        if filter:
            params.append(("$filter", filter))
        if top is not None:
            params.append(("$top", str(top)))
        params.append(("$format", "json"))
        # 1C OData's $filter parser treats '+' literally (NOT as a space) — a quote_plus-encoded space
        # yields «Operation not allowed in clause "ГДЕ"». Encode spaces as %20 via quote (not quote_plus).
        return path + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

    def query(
        self,
        entity_set: str,
        *,
        key: str | None = None,
        select: list[str] | str | None = None,
        filter: str | None = None,
        top: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return matching records as a list of dicts. A by-key fetch returns the single entity wrapped in a
        list; a collection fetch returns its ``value`` array."""
        url = self.build_url(entity_set, key=key, select=select, filter=filter, top=top)
        data = self.fetcher(url, self._headers())
        if isinstance(data, dict) and "value" in data:
            return list(data["value"])
        return [data] if isinstance(data, dict) else list(data)

    def count_records(self, entity_set: str, *, filter: str | None = None,
                      select: list[str] | None = None) -> int:
        """Count matching records. Fetches a minimal projection (``Ref_Key`` by default — ref-bearing entity
        sets: catalogs/documents) and returns its length. 1C standard OData's ``$count`` support is
        version-dependent, so this stays portable by counting a thin payload (fine for a test infobase)."""
        return len(self.query(entity_set, filter=filter, select=select if select is not None else ["Ref_Key"]))


def _parse_decimal(value: Any) -> Decimal:
    text = "" if value is None else str(value)
    normalized = text.strip().replace(" ", "").replace(",", ".")
    try:
        return Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError(f"value {value!r} is not numeric") from exc


def match_value(actual: Any, expected: str, mode: str = "equals") -> bool:
    """Compare a fetched value to an expected string.

    Modes: equals (str-equal), contains (substring), regex (re.search), numeric (Decimal value).
    """
    actual_s = "" if actual is None else str(actual)
    if mode == "equals":
        return actual_s == expected
    if mode == "contains":
        return expected in actual_s
    if mode == "regex":
        return re.search(expected, actual_s) is not None
    if mode == "numeric":
        return _parse_decimal(actual) == _parse_decimal(expected)
    raise ValueError(f"unknown match mode {mode!r} (use equals/contains/regex/numeric)")


def assert_data_value(
    client: ODataClient,
    entity_set: str,
    field: str,
    expected: str,
    *,
    key: str | None = None,
    filter: str | None = None,
    match: str = "equals",
    select: list[str] | None = None,
) -> dict[str, Any]:
    """Read a record via OData and assert one field. Returns a result dict with ``ok`` + ``actual``/``expected``
    (read-only; no mutation)."""
    sel = select if select is not None else [field]
    records = client.query(entity_set, key=key, filter=filter, select=sel)
    base = {"entity_set": entity_set, "field": field, "expected": expected, "match": match,
            "filter": filter, "key": key, "record_count": len(records)}
    if not records:
        return {**base, "ok": False, "actual": None, "reason": "no matching record"}
    actual = records[0].get(field)
    return {**base, "ok": match_value(actual, expected, match), "actual": actual}


# --- card 111 item 7 (E-XV): deeper data-layer — count assertions + a role/security matrix ----------------

_COUNT_OPS: dict[str, Callable[[int, int], bool]] = {
    "eq": lambda a, b: a == b, "ne": lambda a, b: a != b,
    "gt": lambda a, b: a > b, "lt": lambda a, b: a < b,
    "ge": lambda a, b: a >= b, "le": lambda a, b: a <= b,
}


def assert_data_count_value(
    client: ODataClient,
    entity_set: str,
    expected: int,
    *,
    op: str = "eq",
    filter: str | None = None,
) -> dict[str, Any]:
    """Assert the NUMBER of records matching ``filter`` against ``expected`` with ``op`` (eq/ne/gt/lt/ge/le).
    A richer data-layer check than a single-field read — e.g. "a posting created exactly N register rows", or
    "no orphan record remains" (op=eq, expected=0). Read-only."""
    if op not in _COUNT_OPS:
        raise ValueError(f"unknown count op {op!r} (use {'/'.join(_COUNT_OPS)})")
    count = client.count_records(entity_set, filter=filter)
    return {"entity_set": entity_set, "filter": filter, "op": op, "expected": int(expected),
            "count": count, "ok": _COUNT_OPS[op](count, int(expected))}


def role_data_matrix(
    entity_set: str,
    roles: list[dict[str, Any]],
    *,
    base_url: str | None = None,
    filter: str | None = None,
    fetcher: Fetcher | None = None,
) -> dict[str, Any]:
    """Run the SAME data-layer read under several credentials (roles) and report per-role access + count —
    data-layer security verification Vanessa (UI-only) cannot do. Each ``role`` = ``{label, user, password}``
    plus an optional expectation: ``expect_access`` ∈ {"read","denied"} and/or ``min_count`` (int).

    Per-role outcome: ``access`` ∈ {"read","denied","error"} (401/403 → denied), ``count`` (when read), ``http``.
    A role with no expectation is informational (``ok=True``). Overall ``ok`` = every role met its expectation.
    NOTE: a genuine ROLE-DIFFERENCE matrix needs restricted infobase users provisioned out-of-band (admin-mcp/
    edt-mcp) — outside qa-mcp's read-only scope; this primitive evaluates whatever credentials it is given."""
    results: list[dict[str, Any]] = []
    overall_ok = True
    for role in roles:
        label = role.get("label") or role.get("user") or "?"
        client = ODataClient(base_url, role.get("user"), role.get("password"), fetcher=fetcher)
        outcome: dict[str, Any] = {"label": label, "user": role.get("user")}
        try:
            count = client.count_records(entity_set, filter=filter)
            outcome.update(access="read", count=count, http=200)
        except urllib.error.HTTPError as exc:
            outcome.update(access="denied" if exc.code in (401, 403) else "error", count=None, http=exc.code)
        except Exception as exc:  # noqa: BLE001 — a per-role failure is recorded, not raised
            outcome.update(access="error", count=None, error=f"{type(exc).__name__}: {exc}")

        ok = True
        exp_access = role.get("expect_access")
        if exp_access is not None:
            ok = ok and outcome["access"] == exp_access
        if role.get("min_count") is not None:
            ok = ok and outcome["access"] == "read" and (outcome["count"] or 0) >= int(role["min_count"])
        outcome["ok"] = ok
        overall_ok = overall_ok and ok
        results.append(outcome)
    return {"ok": overall_ok, "entity_set": entity_set, "filter": filter, "roles": results}
