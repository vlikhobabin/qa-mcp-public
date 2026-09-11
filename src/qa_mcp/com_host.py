"""Host-agent COM bridge helpers for read-only file-infobase queries."""

from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Callable

from .config import Settings
from .protocol.display_backend import host_agent_install_command

Fetch = Callable[[str, "dict[str, str]", bytes | None, float, str], "dict[str, Any]"]

DEFAULT_COM_PROG_ID = "V83.COMConnector"
DEFAULT_CONNECTION_ID = "qa-mcp-com"
DEFAULT_MAX_ROWS = 100
DEFAULT_TIMEOUT_SEC = 30.0
COUNT_OPS: dict[str, Callable[[Decimal, Decimal], bool]] = {
    "eq": lambda actual, expected: actual == expected,
    "ne": lambda actual, expected: actual != expected,
    "gt": lambda actual, expected: actual > expected,
    "lt": lambda actual, expected: actual < expected,
    "ge": lambda actual, expected: actual >= expected,
    "le": lambda actual, expected: actual <= expected,
}

_UNSAFE_QUERY_RE = re.compile(
    r"(?iu)(?:^|[^\w])("
    r"insert|update|delete|create|drop|alter|merge|execute|exec|"
    r"записать|провести|удалить|изменить|создать|выполнить|"
    r"запуститьприложение|начатьзапись|открытьфайл|файловыйпоток"
    r")(?:[^\w]|$)"
)


class COMHostAgentError(RuntimeError):
    """Structured COM bridge failure suitable for MCP result payloads."""

    def __init__(self, code: str, detail: str, *, status: int | None = None) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.status = status

    def to_result(self, tool: str) -> dict[str, Any]:
        result: dict[str, Any] = {
            "ok": False,
            "error": self.code,
            "tool": tool,
            "detail": self.detail,
            "transport": "com",
        }
        if self.status is not None:
            result["status"] = self.status
        return result


@dataclass(frozen=True)
class COMHostAgentClient:
    """Minimal authenticated client for host-agent COM endpoints."""

    address: str
    token: str
    timeout: float = DEFAULT_TIMEOUT_SEC
    fetcher: Fetch | None = None

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "COMHostAgentClient":
        settings = Settings.from_env(env)
        return cls(
            address=settings.host_agent,
            token=settings.host_agent_token,
            timeout=settings.host_agent_timeout or DEFAULT_TIMEOUT_SEC,
        )

    @property
    def base_url(self) -> str:
        if not self.address:
            raise COMHostAgentError(
                "host-agent-not-configured",
                "QA_MCP_HOST_AGENT is not set; host-side COM queries require the Windows host-agent.",
            )
        address = self.address if "://" in self.address else f"http://{self.address}"
        return address.rstrip("/")

    def _headers(self) -> dict[str, str]:
        if not self.token:
            raise COMHostAgentError(
                "host-agent-token-not-configured",
                "QA_MCP_HOST_AGENT_TOKEN is not set; host-side COM queries require host-agent authentication.",
            )
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-QA-MCP-Agent-Token": self.token,
        }

    def post_json(self, path: str, payload: dict[str, Any], *, timeout: float | None = None) -> dict[str, Any]:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        url = f"{self.base_url}{path}"
        headers = self._headers()
        request_timeout = float(timeout or self.timeout or DEFAULT_TIMEOUT_SEC)
        fetcher = self.fetcher or _http_fetch_json
        return fetcher(url, headers, data, request_timeout, "POST")

    def execute_query(
        self,
        *,
        infobase_path: str,
        user: str = "",
        password: str = "",
        query: str,
        timeout_sec: float = DEFAULT_TIMEOUT_SEC,
        max_rows: int = DEFAULT_MAX_ROWS,
        prog_id: str = DEFAULT_COM_PROG_ID,
    ) -> dict[str, Any]:
        _raise_if_query_not_read_only(query)
        request_id = f"qa-mcp-com-{int(time.time() * 1000)}"
        worker_request = {
            "requestId": request_id,
            "operation": "execute_query",
            "timeout_seconds": float(timeout_sec or self.timeout or DEFAULT_TIMEOUT_SEC),
            "connection": {
                "connectionId": DEFAULT_CONNECTION_ID,
                "infobasePath": infobase_path,
                "username": user,
                "password": password,
                "progId": prog_id or DEFAULT_COM_PROG_ID,
            },
            "payload": {
                "query": {
                    "text": query,
                    "hash": hashlib.sha256(query.encode("utf-8")).hexdigest(),
                },
                "parameters": [],
                "limits": {"maxRows": int(max_rows or DEFAULT_MAX_ROWS)},
            },
        }
        return self.post_json("/com/execute", worker_request, timeout=timeout_sec)

    def doctor(
        self,
        *,
        infobase_path: str,
        user: str = "",
        password: str = "",
        query: str = "",
        timeout_sec: float = DEFAULT_TIMEOUT_SEC,
        prog_id: str = DEFAULT_COM_PROG_ID,
    ) -> dict[str, Any]:
        if query:
            _raise_if_query_not_read_only(query)
        return self.post_json(
            "/com/doctor",
            {
                "infobase_path": infobase_path,
                "user": user,
                "password": password,
                "query": query,
                "timeout_seconds": float(timeout_sec or self.timeout or DEFAULT_TIMEOUT_SEC),
                "prog_id": prog_id or DEFAULT_COM_PROG_ID,
            },
            timeout=timeout_sec,
        )


def query_com(
    *,
    infobase_path: str,
    query: str,
    user: str = "",
    password: str = "",
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    max_rows: int = DEFAULT_MAX_ROWS,
    prog_id: str = DEFAULT_COM_PROG_ID,
    client: COMHostAgentClient | None = None,
) -> dict[str, Any]:
    """Execute a read-only 1C query through host-agent COM and normalize rows."""
    if not infobase_path.strip():
        return {"ok": False, "error": "infobase-path-required", "transport": "com"}
    if not query.strip():
        return {"ok": False, "error": "query-required", "transport": "com"}
    client = client or COMHostAgentClient.from_env()
    try:
        response = client.execute_query(
            infobase_path=infobase_path,
            user=user,
            password=password,
            query=query,
            timeout_sec=timeout_sec,
            max_rows=max_rows,
            prog_id=prog_id,
        )
    except COMHostAgentError as exc:
        result = exc.to_result("query_com")
        if exc.code == "host-agent-not-configured":
            result["install_command"] = host_agent_install_command()
            result["feature_requires"] = ["Windows host-agent", "ai-com-worker.exe"]
        return result

    result = response.get("result") if isinstance(response, dict) else None
    rows = result.get("rows") if isinstance(result, dict) else None
    normalized = {
        "ok": bool(response.get("ok")) if isinstance(response, dict) else False,
        "transport": "com",
        "rows": rows if isinstance(rows, list) else [],
        "row_count": len(rows) if isinstance(rows, list) else 0,
        "platform": result.get("platform") if isinstance(result, dict) else None,
        "bitness": result.get("bitness") if isinstance(result, dict) else None,
        "worker_response": response,
    }
    if isinstance(result, dict):
        for key in ("columns", "platform", "bitness", "provider_kind", "metadata_snapshot_provenance"):
            if key in result:
                normalized[key] = result[key]
    if not normalized["ok"]:
        error = response.get("error") if isinstance(response, dict) else None
        normalized["error"] = error.get("code") if isinstance(error, dict) else "com-query-failed"
        normalized["detail"] = error.get("message") if isinstance(error, dict) else "COM worker query failed"
    return normalized


def assert_com_count(
    *,
    infobase_path: str,
    query: str,
    expected: int,
    op: str = "eq",
    count_field: str = "",
    user: str = "",
    password: str = "",
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    prog_id: str = DEFAULT_COM_PROG_ID,
    client: COMHostAgentClient | None = None,
) -> dict[str, Any]:
    """Execute a COM read query and compare its first numeric value."""
    if op not in COUNT_OPS:
        return {"ok": False, "error": "unknown-count-op", "op": op, "transport": "com"}
    query_result = query_com(
        infobase_path=infobase_path,
        query=query,
        user=user,
        password=password,
        timeout_sec=timeout_sec,
        max_rows=1,
        prog_id=prog_id,
        client=client,
    )
    base: dict[str, Any] = {
        "transport": "com",
        "op": op,
        "expected": int(expected),
        "query_result": query_result,
    }
    if not query_result.get("ok"):
        return {**base, "ok": False, "error": query_result.get("error", "com-query-failed")}
    try:
        count = _extract_count(query_result.get("rows"), count_field=count_field)
    except ValueError as exc:
        return {**base, "ok": False, "error": "count-not-numeric", "detail": str(exc)}
    actual = Decimal(count)
    expected_value = Decimal(int(expected))
    return {**base, "ok": COUNT_OPS[op](actual, expected_value), "count": int(actual)}


def com_connector_doctor(
    *,
    infobase_path: str,
    user: str = "",
    password: str = "",
    query: str = "",
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    prog_id: str = DEFAULT_COM_PROG_ID,
    client: COMHostAgentClient | None = None,
) -> dict[str, Any]:
    """Run host-agent COMConnector registration and optional read-smoke diagnostics."""
    if not infobase_path.strip():
        return {"ok": False, "error": "infobase-path-required", "transport": "com"}
    client = client or COMHostAgentClient.from_env()
    try:
        result = client.doctor(
            infobase_path=infobase_path,
            user=user,
            password=password,
            query=query,
            timeout_sec=timeout_sec,
            prog_id=prog_id,
        )
    except COMHostAgentError as exc:
        payload = exc.to_result("com_connector_doctor")
        if exc.code == "host-agent-not-configured":
            payload["install_command"] = host_agent_install_command()
        return payload
    if isinstance(result, dict):
        return {**result, "transport": "com"}
    return {"ok": False, "error": "host-agent-invalid-json", "transport": "com"}


def unsafe_query_reason(query: str) -> str | None:
    """Return a policy reason when query text is obviously not read-only."""
    text = query.strip()
    if not text:
        return "query is empty"
    match = _UNSAFE_QUERY_RE.search(text)
    if match:
        return f"query contains side-effecting token {match.group(1)!r}"
    return None


def _raise_if_query_not_read_only(query: str) -> None:
    reason = unsafe_query_reason(query)
    if reason is not None:
        raise COMHostAgentError("com-query-not-read-only", reason)


def _extract_count(rows: Any, *, count_field: str = "") -> Decimal:
    if not isinstance(rows, list) or not rows:
        raise ValueError("COM count query returned no rows")
    first = rows[0]
    if not isinstance(first, dict) or not first:
        raise ValueError("COM count query first row is not an object")
    value: Any
    if count_field:
        if count_field not in first:
            raise ValueError(f"count field {count_field!r} is missing")
        value = first[count_field]
    else:
        value = next(iter(first.values()))
    try:
        return Decimal(str(value).strip().replace(" ", "").replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError(f"count value {value!r} is not numeric") from exc


def _http_fetch_json(url: str, headers: dict[str, str], data: bytes | None, timeout: float, method: str) -> dict[str, Any]:
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - lab-local host-agent URL.
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict) and payload.get("ok") is False:
            raise COMHostAgentError(
                str(payload.get("error") or "host-agent-http-error"),
                str(payload.get("detail") or body),
                status=exc.code,
            ) from exc
        raise COMHostAgentError("host-agent-http-error", body or f"HTTP {exc.code}", status=exc.code) from exc
    except urllib.error.URLError as exc:
        raise COMHostAgentError("host-agent-unreachable", str(exc.reason)) from exc
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise COMHostAgentError("host-agent-invalid-json", "host-agent returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise COMHostAgentError("host-agent-invalid-json", "host-agent JSON response is not an object")
    return payload
