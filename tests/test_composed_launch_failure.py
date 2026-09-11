"""Failed launch keeps safe cleanup identity through the real MCP/HTTP path."""
from __future__ import annotations

import asyncio
from io import BytesIO
import json
import urllib.error

import pytest

from qa_mcp import mcp_server
from qa_mcp.config import Settings
from qa_mcp.protocol import display_backend


@pytest.mark.parametrize("transport", ["http-error", "json-error"])
@pytest.mark.parametrize("invalid", [
    None, "unowned", "reused", "owner", "pid", "port", "handle-pid", "handle-port",
    "handle-id", "kind", "identity", "token", "oversized", "handle-type",
])
def test_failed_launch_preserves_only_valid_cleanup_identity(monkeypatch, transport, invalid):
    token = "SYNTHETIC-LAUNCH-TOKEN"
    private = "PRIVATE-LAUNCH-DIAGNOSTIC"
    identity = "owned-launch_1"
    handle = {"kind": "host-agent-testclient", "id": identity, "pid": 4321, "port": 15444}
    payload = {
        "ok": False, "error": "testclient-not-listening", "detail": private,
        "pid": 4321, "port": 15444, "owns_process": True,
        "lifecycle_owner": "host-agent", "lifecycle_id": identity,
        "lifecycle_handle": {**handle, "private": private, "token": token},
        "token": token,
    }
    if invalid == "unowned": payload["owns_process"] = False
    if invalid == "reused": payload["reused_existing"] = True
    if invalid == "owner": payload["lifecycle_owner"] = private
    if invalid == "pid": payload["pid"] = True
    if invalid == "port": payload["port"] = 15445
    if invalid == "handle-pid": payload["lifecycle_handle"]["pid"] = 5678
    if invalid == "handle-port": payload["lifecycle_handle"]["port"] = 15445
    if invalid == "handle-id": payload["lifecycle_handle"]["id"] = "other"
    if invalid == "kind": payload["lifecycle_handle"]["kind"] = "foreign"
    if invalid in {"identity", "token", "oversized"}:
        value = {"identity": "bad identity", "token": token, "oversized": "x" * 129}[invalid]
        payload["lifecycle_id"] = value
        payload["lifecycle_handle"]["id"] = value
    if invalid == "handle-type": payload["lifecycle_handle"] = private
    calls = []

    class Response(BytesIO):
        headers = {"Content-Type": "application/json"}

    def urlopen(request, timeout):
        calls.append(request.full_url)
        assert request.get_header("X-qa-mcp-agent-token") == token
        if request.full_url.endswith("/v1/capabilities"):
            return Response(json.dumps({
                "api": display_backend.HOST_BRIDGE_API,
                "api_major": display_backend.HOST_BRIDGE_API_MAJOR,
                "version": display_backend.HOST_AGENT_VERSION,
                "display_protocol": display_backend.HOST_AGENT_DISPLAY_PROTOCOL,
                "capabilities": sorted(display_backend.HOST_BRIDGE_REQUIRED_CAPABILITIES),
            }).encode())
        if request.full_url.endswith("/testclient/stop"):
            sent = json.loads(request.data)
            assert sent["pid"] == 4321 and sent["lifecycle_id"] == identity
            assert sent["lifecycle_handle"] == handle
            return Response(json.dumps({"ok": True, "stopped": True, "state": "stopped"}).encode())
        assert request.full_url.endswith("/testclient/launch")
        assert json.loads(request.data)["port"] == 15444
        body = json.dumps(payload).encode()
        if transport == "http-error":
            raise urllib.error.HTTPError(request.full_url, 504, "failure", None, BytesIO(body))
        return Response(body)

    monkeypatch.setenv("QA_MCP_REMOTE_CLIENT", "0")
    monkeypatch.setenv("QA_MCP_HOST_AGENT", "foreign.invalid:8999")
    monkeypatch.setattr(display_backend.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(mcp_server.client_lifecycle, "load_env_file", lambda _: {
        "INFOBASE_PATH": "/synthetic", "TEST_CLIENT_USER": "fixture",
    })
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", lambda *a, **kw: pytest.fail("unexpected probe"))
    server = mcp_server.create_mcp_server(settings=Settings(
        manager_templates="synthetic-manager.json", value_read_templates="synthetic-values.json",
        remote_client=True, host_agent="application.invalid:8123", host_agent_token=token,
    ))
    result = asyncio.run(server.call_tool("launch_test_client", {"port": 15444})).structured_content
    assert result["ok"] is False
    assert result["error"] == "testclient-not-listening"
    assert result["detail"] == "host agent request failed"
    assert "host_agent" not in result and "active_attachment" not in result
    assert token not in json.dumps(result) and private not in json.dumps(result)
    if invalid is None:
        assert result["lifecycle_handle"] == handle
        assert result["pid"] == 4321 and result["owns_process"] is True
        assert result["lifecycle_id"] == identity and result["lifecycle_owner"] == "host-agent"
    else:
        assert "lifecycle_handle" not in result and "pid" not in result
        assert result.get("owns_process") is not True
    assert calls == ["http://application.invalid:8123/v1/capabilities", "http://application.invalid:8123/testclient/launch"]
    if invalid is None:
        stopped = asyncio.run(server.call_tool("stop_test_client", {
            "pid": result["pid"], "port": result["port"],
            "lifecycle_id": result["lifecycle_id"], "lifecycle_handle": result["lifecycle_handle"],
        })).structured_content
        assert stopped["stopped"] is True
        assert calls[-2:] == ["http://application.invalid:8123/v1/capabilities", "http://application.invalid:8123/testclient/stop"]
