from __future__ import annotations

import json
from typing import Any

from qa_mcp import mcp_server
from qa_mcp.com_host import COMHostAgentClient, assert_com_count, query_com, unsafe_query_reason


def _client(response: dict[str, Any], seen: list[dict[str, Any]] | None = None) -> COMHostAgentClient:
    def fetch(url: str, headers: dict[str, str], data: bytes | None, timeout: float, method: str) -> dict[str, Any]:
        assert url == "http://host.docker.internal:8001/com/execute"
        assert method == "POST"
        assert headers["X-QA-MCP-Agent-Token"] == "tok"
        payload = json.loads((data or b"{}").decode("utf-8"))
        if seen is not None:
            seen.append(payload)
        return response

    return COMHostAgentClient("host.docker.internal:8001", "tok", fetcher=fetch)


def test_query_com_builds_worker_request_and_returns_rows() -> None:
    seen: list[dict[str, Any]] = []
    client = _client(
        {
            "ok": True,
            "requestId": "r1",
            "result": {
                "columns": ["Qty"],
                "rows": [{"Qty": 1}],
                "provider_kind": "com",
                "platform": "windows",
                "bitness": "x64",
            },
        },
        seen,
    )

    result = query_com(
        infobase_path=r"C:\Bases\Finans",
        user="Администратор",
        password="secret",
        query="ВЫБРАТЬ КОЛИЧЕСТВО(*) КАК Qty ИЗ Справочник.Валюты",
        client=client,
    )

    assert result["ok"] is True
    assert result["transport"] == "com"
    assert result["rows"] == [{"Qty": 1}]
    assert result["row_count"] == 1
    assert result["provider_kind"] == "com"
    assert seen[0]["operation"] == "execute_query"
    assert seen[0]["connection"]["infobasePath"] == r"C:\Bases\Finans"
    assert seen[0]["connection"]["username"] == "Администратор"
    assert seen[0]["connection"]["password"] == "secret"
    assert seen[0]["payload"]["limits"]["maxRows"] == 100


def test_assert_com_count_compares_first_numeric_value() -> None:
    client = _client({"ok": True, "result": {"rows": [{"Qty": "3"}]}})

    result = assert_com_count(
        infobase_path=r"C:\Bases\Finans",
        query="ВЫБРАТЬ 3 КАК Qty",
        expected=2,
        op="gt",
        count_field="Qty",
        client=client,
    )

    assert result["ok"] is True
    assert result["count"] == 3
    assert result["expected"] == 2
    assert result["op"] == "gt"


def test_query_com_rejects_write_shaped_query_before_transport() -> None:
    calls: list[dict[str, Any]] = []
    client = _client({"ok": True, "result": {"rows": []}}, calls)

    result = query_com(
        infobase_path=r"C:\Bases\Finans",
        query="УДАЛИТЬ ИЗ Справочник.Валюты",
        client=client,
    )

    assert result["ok"] is False
    assert result["error"] == "com-query-not-read-only"
    assert calls == []
    assert unsafe_query_reason("delete from Catalog") is not None


def test_query_com_missing_host_agent_config_is_actionable(monkeypatch) -> None:
    monkeypatch.delenv("QA_MCP_HOST_AGENT", raising=False)
    monkeypatch.delenv("QA_MCP_HOST_AGENT_TOKEN", raising=False)

    result = mcp_server.query_com(
        infobase_path=r"C:\Bases\Finans",
        query="ВЫБРАТЬ 1 КАК Qty",
    )

    assert result["ok"] is False
    assert result["error"] == "host-agent-not-configured"
    assert "install_command" in result
    assert "ai-com-worker.exe" in result["feature_requires"]


def test_com_connector_doctor_wrapper_returns_type_lib_guidance(monkeypatch) -> None:
    def fake_doctor(**kwargs: Any) -> dict[str, Any]:
        assert kwargs["infobase_path"] == r"C:\Bases\Finans"
        return {
            "ok": False,
            "error": "typelib-missing",
            "repair_command": r'C:\Windows\System32\regsvr32.exe "C:\Program Files\1cv8\8.3.27.2130\bin\comcntr.dll"',
        }

    monkeypatch.setattr("qa_mcp.com_host.com_connector_doctor", fake_doctor)

    result = mcp_server.com_connector_doctor(infobase_path=r"C:\Bases\Finans")

    assert result["ok"] is False
    assert result["error"] == "typelib-missing"
    assert r"C:\Windows\System32\regsvr32.exe" in result["repair_command"]
