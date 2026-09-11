from __future__ import annotations

import base64
from io import BytesIO
import json
import sys
import urllib.error
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.protocol import display_backend as db  # noqa: E402
from qa_mcp.protocol.screenshot import PNG_MAGIC  # noqa: E402


@pytest.mark.parametrize("status", [True, -1, 600, 10 ** 300, "PRIVATE-STATUS", None])
def test_public_host_agent_error_omits_non_http_status(status) -> None:
    error = db.DisplayBackendError("foreground-denied", "PRIVATE-DETAIL", status=status)
    result = error.to_result("send_keys", remote_client=True)
    assert "status" not in result
    assert result["error"] == "foreground-denied"
    assert "PRIVATE" not in repr(result)
    assert len(json.dumps(result)) < 512


def test_remote_client_enabled_and_agent_configured() -> None:
    assert db.remote_client_enabled({"QA_MCP_REMOTE_CLIENT": "1"})
    assert db.remote_client_enabled({"QA_MCP_REMOTE_CLIENT": "true"})
    assert not db.remote_client_enabled({"QA_MCP_REMOTE_CLIENT": ""})
    assert db.remote_agent_configured({"QA_MCP_HOST_AGENT": "host.docker.internal:8001"})
    assert not db.remote_agent_configured({})


def test_get_display_backend_selects_remote() -> None:
    backend = db.get_display_backend({
        "QA_MCP_REMOTE_CLIENT": "1",
        "QA_MCP_HOST_AGENT": "host.docker.internal:8001",
        "QA_MCP_HOST_AGENT_TOKEN": "tok",
    })
    assert isinstance(backend, db.RemoteAgentBackend)
    assert backend.url == "http://host.docker.internal:8001"
    assert backend.token == "tok"


def test_remote_backend_marks_explicit_expected_version_as_pin() -> None:
    backend = db.RemoteAgentBackend.from_env({
        "QA_MCP_HOST_AGENT": "host.docker.internal:8001",
        "QA_MCP_HOST_AGENT_EXPECTED_VERSION": db.HOST_AGENT_VERSION,
    })

    assert backend.expected_version == db.HOST_AGENT_VERSION
    assert backend.version_pinned is True


def test_unavailable_remote_result_has_install_command() -> None:
    result = db.unavailable_remote_result("capture_screenshot", alt="read_form_descriptor")
    assert result["ok"] is False
    assert result["error"] == "display-backend-unavailable-remote-client"
    assert "install-windows-host-agent.ps1" in result["install_command"]
    assert "read_form_descriptor" in result["detail"]


def _capability_document(**updates):
    payload = {
        "api": db.HOST_BRIDGE_API,
        "api_major": db.HOST_BRIDGE_API_MAJOR,
        "version": db.HOST_AGENT_VERSION,
        "display_protocol": db.HOST_AGENT_DISPLAY_PROTOCOL,
        "sha256": "abc",
        "capabilities": sorted(db.HOST_BRIDGE_REQUIRED_CAPABILITIES),
    }
    payload.update(updates)
    return payload


def test_remote_handshake_accepts_standalone_contract(monkeypatch) -> None:
    backend = db.RemoteAgentBackend("host:8001")
    monkeypatch.setattr(backend, "_json", lambda method, path, token=True, payload=None: _capability_document())

    result = backend.handshake()

    assert result["api"] == db.HOST_BRIDGE_API
    assert result["api_major"] == db.HOST_BRIDGE_API_MAJOR
    assert result["version_relationship"] == "current"
    assert set(result["capabilities"]) == db.HOST_BRIDGE_REQUIRED_CAPABILITIES


def test_remote_handshake_version_pin_remains_exact(monkeypatch) -> None:
    backend = db.RemoteAgentBackend("host:8001", expected_version="pinned", version_pinned=True)
    monkeypatch.setattr(backend, "_json", lambda method, path, token=True, payload=None: _capability_document())

    with pytest.raises(db.DisplayBackendError) as exc:
        backend.handshake()

    assert exc.value.code == "host-agent-version-mismatch"


def test_remote_handshake_uses_authenticated_versioned_endpoint(monkeypatch) -> None:
    backend = db.RemoteAgentBackend("host:8001", token="tok")
    observed = {}

    def fake_json(method, path, token=True, payload=None):
        observed.update(method=method, path=path, token=token)
        return _capability_document()

    monkeypatch.setattr(backend, "_json", fake_json)
    backend.handshake()

    assert observed == {"method": "GET", "path": "/v1/capabilities", "token": True}


def test_remote_request_preserves_host_agent_json_error(monkeypatch) -> None:
    backend = db.RemoteAgentBackend("host:8001", token="tok")
    body = json.dumps({
        "ok": False,
        "status": 409,
        "error": "foreground-denied",
        "detail": "SetForegroundWindow denied",
    }).encode("utf-8")

    def fake_urlopen(req, timeout):
        raise urllib.error.HTTPError(
            req.full_url,
            409,
            "Conflict",
            hdrs=None,
            fp=BytesIO(body),
        )

    monkeypatch.setattr(db.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(db.DisplayBackendError) as exc:
        backend._json("POST", "/send_keys", payload={"keys": ["F5"]})

    assert exc.value.code == "foreground-denied"
    assert exc.value.status == 409
    assert "SetForegroundWindow denied" in exc.value.detail


@pytest.mark.parametrize(
    "code",
    [
        "desktop-session-locked",
        "desktop-session-disconnected",
        "desktop-session-noninteractive",
    ],
)
def test_remote_request_preserves_typed_desktop_session_error(monkeypatch, code) -> None:
    backend = db.RemoteAgentBackend("host:8001", token="tok")
    body = json.dumps({
        "ok": False,
        "status": 409,
        "error": code,
        "detail": "interactive desktop is unavailable",
    }).encode("utf-8")

    def fake_urlopen(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 409, "Conflict", hdrs=None, fp=BytesIO(body))

    monkeypatch.setattr(db.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(db.DisplayBackendError) as exc:
        backend._json("POST", "/send_keys", payload={"keys": ["F5"]})

    assert exc.value.code == code
    assert exc.value.status == 409
    assert exc.value.payload == json.loads(body)


def test_remote_visible_list_cells_posts_window_and_limit(monkeypatch) -> None:
    backend = db.RemoteAgentBackend("host:8001", expected_version="v1", target_window="class:V8TopLevelFrame")
    observed: dict[str, object] = {}
    monkeypatch.setattr(backend, "_ensure_ready", lambda: None)

    def fake_json(method, path, *, payload=None, token=True):
        observed.update(method=method, path=path, payload=payload, token=token)
        return {"ok": True, "target": {"class": "V8TopLevelFrameSDI"}, "cells": ["Российский рубль"]}

    monkeypatch.setattr(backend, "_json", fake_json)

    result = backend.visible_list_cells(limit=3)

    assert observed == {
        "method": "POST",
        "path": "/uia/visible_list_cells",
        "payload": {"window": "class:V8TopLevelFrame", "limit": 3},
        "token": True,
    }
    assert result["cells"] == ["Российский рубль"]
    assert result["backend"] == "remote-agent"


def test_remote_testclient_launch_posts_semantic_payload(monkeypatch) -> None:
    backend = db.RemoteAgentBackend("host:8001", expected_version="v1")
    observed: dict[str, object] = {}
    monkeypatch.setattr(backend, "_ensure_ready", lambda: None)

    def fake_json(method, path, *, payload=None, token=True, timeout=None):
        observed.update(method=method, path=path, payload=payload, token=token, timeout=timeout)
        return {"ok": True, "pid": 4321, "port": payload["port"], "response_id": "testclient-launch"}

    monkeypatch.setattr(backend, "_json", fake_json)

    result = backend.launch_test_client(
        infobase_path="C:/Bases/vanessa_client",
        user="Администратор",
        password="secret",
        platform_version="8.3.27.2130",
        use_hardware_licenses=True,
        port=15444,
        timeout_seconds=5,
    )

    assert observed == {
        "method": "POST",
        "path": "/testclient/launch",
        "payload": {
            "infobase_path": "C:/Bases/vanessa_client",
            "connection_string": "",
            "user": "Администратор",
            "password": "secret",
            "platform_version": "8.3.27.2130",
            "use_hardware_licenses": True,
            "port": 15444,
            "timeout_seconds": 5.0,
        },
        "token": True,
        # launch blocks on the host-agent readiness wait, so its HTTP timeout is
        # extended past the short default (5s wait + LAUNCH_HTTP_TIMEOUT_MARGIN).
        "timeout": 5.0 + db.LAUNCH_HTTP_TIMEOUT_MARGIN,
    }
    assert result["pid"] == 4321
    assert result["backend"] == "remote-agent"


def test_remote_testclient_stop_posts_lifecycle_handle(monkeypatch) -> None:
    backend = db.RemoteAgentBackend("host:8001")
    observed: dict[str, object] = {}
    handle = {"kind": "host-agent-testclient", "id": "launch-1", "pid": 4321, "port": 15444}
    monkeypatch.setattr(
        backend,
        "handshake",
        lambda: {"version": db.HOST_AGENT_VERSION, "version_relationship": "current"},
    )

    def fake_json(method, path, *, payload=None, token=True, timeout=None):
        observed.update(method=method, path=path, payload=payload, token=token, timeout=timeout)
        return {"ok": True, "pid": payload["pid"], "state": "stopped", "stopped": True}

    monkeypatch.setattr(backend, "_json", fake_json)

    result = backend.stop_test_client(pid=4321, port=15444, lifecycle_id="launch-1", lifecycle_handle=handle)

    assert observed == {
        "method": "POST",
        "path": "/testclient/stop",
        "payload": {"pid": 4321, "port": 15444, "lifecycle_id": "launch-1", "lifecycle_handle": handle},
        "token": True,
        "timeout": None,
    }
    assert result["pid"] == 4321
    assert result["state"] == "stopped"
    assert result["backend"] == "remote-agent"


def test_remote_testclient_stop_rejects_legacy_handshake_before_stop(monkeypatch) -> None:
    backend = db.RemoteAgentBackend("host:8001")
    calls = []
    handle = {"kind": "host-agent-testclient", "id": "launch-1", "pid": 4321, "port": 15444}

    def fake_json(method, path, *, payload=None, token=True, timeout=None):
        calls.append((method, path, payload))
        if path == "/v1/capabilities":
            return {"ok": True, "version": "0.1.9-testclient-owned-lifecycle"}
        raise AssertionError("legacy bridge must be rejected before stop")

    monkeypatch.setattr(backend, "_json", fake_json)

    with pytest.raises(db.DisplayBackendError) as exc:
        backend.stop_test_client(pid=4321, port=15444, lifecycle_id="launch-1", lifecycle_handle=handle)

    assert exc.value.code == "host-agent-capability-document-invalid"
    assert calls == [("GET", "/v1/capabilities", None)]


def test_remote_testclient_launch_uses_extended_http_timeout(monkeypatch) -> None:
    # Regression guard for the launch HTTP-timeout coherence gap surfaced by the
    # .205 E2E: /testclient/launch now blocks synchronously until the host-agent
    # classifies TestClient readiness, so the request timeout must cover the launch
    # wait, not the short default host_agent_timeout (which times out a real launch
    # on the client before the host-agent can answer).
    backend = db.RemoteAgentBackend("host:8001", token="tok", timeout=10.0)
    monkeypatch.setattr(backend, "_ensure_ready", lambda: None)
    captured: dict[str, object] = {}

    def fake_request(method, path, *, payload=None, token=True, accept="application/json", timeout=None):
        captured.update(path=path, timeout=timeout)
        body = json.dumps({"ok": True, "pid": 4321, "port": payload["port"], "readiness": "ready"}).encode("utf-8")
        return body, "application/json"

    monkeypatch.setattr(backend, "_request", fake_request)

    backend.launch_test_client(infobase_path="C:/Bases/x", user="Админ", port=15444, timeout_seconds=120)

    assert captured["path"] == "/testclient/launch"
    assert captured["timeout"] is not None
    assert captured["timeout"] >= 120.0
    assert captured["timeout"] > backend.timeout  # not the short 10s default


def test_remote_testclient_launch_urlopen_timeout_is_extended(monkeypatch) -> None:
    # Stronger F1 guard: exercise the REAL _request so a regression at the
    # urlopen(timeout=...) application line is caught. The _request-mocking test
    # above would still pass if _request reverted to self.timeout for urlopen;
    # this test drives launch through the real _request with a fake urlopen and
    # asserts the timeout that actually reaches urlopen is the extended one.
    backend = db.RemoteAgentBackend("host:8001", token="tok", timeout=10.0)
    monkeypatch.setattr(backend, "_ensure_ready", lambda: None)
    captured: dict[str, object] = {}

    class _FakeResponse:
        def __init__(self, body: bytes) -> None:
            self._body = body
            self.headers = {"Content-Type": "application/json"}

        def __enter__(self) -> "_FakeResponse":
            return self

        def __exit__(self, *exc: object) -> bool:
            return False

        def read(self) -> bytes:
            return self._body

    def fake_urlopen(req, timeout):  # noqa: ANN001 - test double mirrors urlopen
        captured["timeout"] = timeout
        body = json.dumps({"ok": True, "pid": 4321, "port": 15381, "readiness": "ready"}).encode("utf-8")
        return _FakeResponse(body)

    monkeypatch.setattr(db.urllib.request, "urlopen", fake_urlopen)

    backend.launch_test_client(infobase_path="C:/Bases/x", user="Админ", port=15381, timeout_seconds=120)

    # This is the value passed straight into urllib.request.urlopen(req, timeout=...).
    assert captured["timeout"] >= 120.0
    assert captured["timeout"] > backend.timeout  # a urlopen-line regression to self.timeout (10s) fails here


def test_remote_screenshot_accepts_json_base64(monkeypatch, tmp_path) -> None:
    png = PNG_MAGIC + b"fake"
    backend = db.RemoteAgentBackend("host:8001", expected_version="v1")
    monkeypatch.setattr(backend, "_ensure_ready", lambda: None)
    monkeypatch.setattr(
        backend,
        "_request",
        lambda *a, **kw: (
            json.dumps({"ok": True, "png_base64": base64.b64encode(png).decode("ascii")}).encode("utf-8"),
            "application/json",
        ),
    )

    result = backend.capture_screenshot("", tmp_path / "shot.png", window="1C")

    assert (tmp_path / "shot.png").read_bytes() == png
    assert result["size_bytes"] == len(png)
    assert result["backend"] == "remote-agent"


def test_mcp_remote_mode_without_agent_returns_guard(monkeypatch) -> None:
    from qa_mcp import mcp_server

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.delenv("QA_MCP_HOST_AGENT", raising=False)

    result = mcp_server.capture_screenshot(":89")

    assert result["ok"] is False
    assert result["error"] == "display-backend-unavailable-remote-client"
    assert result["tool"] == "capture_screenshot"


def test_mcp_remote_mode_with_agent_dispatches_backend(monkeypatch, tmp_path) -> None:
    from qa_mcp import mcp_server

    class FakeBackend:
        name = "fake-remote"

        def capture_screenshot(self, display, out_path, *, window=None):
            Path(out_path).write_bytes(PNG_MAGIC + b"fake")
            return {"path": str(out_path), "display": display, "window": window, "backend": self.name}

    monkeypatch.setattr(mcp_server, "REMOTE_CLIENT", True)
    monkeypatch.setenv("QA_MCP_HOST_AGENT", "host:8001")
    monkeypatch.setattr(mcp_server.client_display, "get_display_backend", lambda: FakeBackend())

    result = mcp_server.capture_screenshot(":89", out_path=str(tmp_path / "shot.png"))

    assert result["backend"] == "fake-remote"
    assert Path(result["path"]).exists()


def _capture_send_keys_payload(monkeypatch, backend) -> dict:
    captured: dict = {}
    monkeypatch.setattr(backend, "_ensure_ready", lambda: None)
    monkeypatch.setattr(
        backend, "_json",
        lambda method, path, token=True, payload=None: captured.update(payload=payload) or {"ok": True},
    )
    backend.send_keys(["F5"])
    return captured["payload"]


def test_remote_defaults_to_client_port_window_targeting(monkeypatch) -> None:
    backend = db.RemoteAgentBackend("host:8001", client_port=15383)
    payload = _capture_send_keys_payload(monkeypatch, backend)
    assert payload["window"] == ""
    assert payload["client_port"] == 15383


def test_remote_explicit_window_wins_and_client_port_still_sent(monkeypatch) -> None:
    backend = db.RemoteAgentBackend(
        "host:8001", target_window="Бухгалтерия предприятия, редакция 3.0", client_port=15383,
    )
    payload = _capture_send_keys_payload(monkeypatch, backend)
    assert payload["window"] == "Бухгалтерия предприятия, редакция 3.0"
    assert payload["client_port"] == 15383


def test_remote_no_client_port_omits_field(monkeypatch) -> None:
    backend = db.RemoteAgentBackend("host:8001")
    payload = _capture_send_keys_payload(monkeypatch, backend)
    assert payload["window"] == ""
    assert "client_port" not in payload


def test_remote_from_env_picks_up_client_port(monkeypatch) -> None:
    backend = db.RemoteAgentBackend.from_env({
        "QA_MCP_REMOTE_CLIENT": "1",
        "QA_MCP_HOST_AGENT": "host:8001",
        "QA_MCP_CLIENT_PORT": "15384",
    })
    assert backend.client_port == 15384


def test_remote_from_env_prefers_explicit_host_agent_client_port(monkeypatch) -> None:
    backend = db.RemoteAgentBackend.from_env({
        "QA_MCP_REMOTE_CLIENT": "1",
        "QA_MCP_HOST_AGENT": "host:8001",
        "QA_MCP_CLIENT_PORT": "15382",
        "QA_MCP_HOST_AGENT_CLIENT_PORT": "15381",
    })
    assert backend.client_port == 15381


def test_remote_lifecycle_target_is_sent_to_all_implicit_display_routes(monkeypatch, tmp_path) -> None:
    target = {
        "kind": "host-agent-testclient",
        "lifecycle_id": "launch-1",
        "pid": 4321,
        "port": 15383,
    }
    backend = db.RemoteAgentBackend("host:8001", client_port=15383, client_target=target)
    calls: list[tuple[str, dict]] = []
    handshake = {"capabilities": [db.HOST_AGENT_TESTCLIENT_WINDOW_TARGET_CAPABILITY]}
    monkeypatch.setattr(backend, "_ensure_ready", lambda: handshake)
    monkeypatch.setattr(
        backend,
        "_json",
        lambda method, path, token=True, payload=None, timeout=None: calls.append((path, payload))
        or {"ok": True, "windows": [], "cells": []},
    )
    monkeypatch.setattr(
        backend,
        "_request",
        lambda method, path, payload=None, token=True, accept="application/json", timeout=None: (
            calls.append((path, payload)) or (PNG_MAGIC + b"target", "image/png")
        ),
    )

    backend.send_keys(["F5"])
    backend.type_text("X")
    backend.click(10, 20)
    backend.list_windows("")
    backend.visible_list_cells(limit=2)
    backend.capture_screenshot("", tmp_path / "target.png")

    assert [path for path, _payload in calls] == [
        "/send_keys",
        "/type",
        "/click",
        "/window_list",
        "/uia/visible_list_cells",
        "/screenshot",
    ]
    for _path, payload in calls:
        assert payload["client_target"] == target
        assert payload["window"] == ""


def test_remote_explicit_window_retains_active_lifecycle_target(monkeypatch) -> None:
    target = {
        "kind": "host-agent-testclient",
        "lifecycle_id": "launch-1",
        "pid": 4321,
        "port": 15383,
    }
    backend = db.RemoteAgentBackend(
        "host:8001", client_port=15383, client_target=target, client_target_required=True
    )
    captured: dict = {}
    monkeypatch.setattr(
        backend,
        "_ensure_ready",
        lambda: {"capabilities": [db.HOST_AGENT_TESTCLIENT_WINDOW_TARGET_CAPABILITY]},
    )
    monkeypatch.setattr(
        backend,
        "_json",
        lambda method, path, token=True, payload=None, timeout=None: captured.update(payload=payload) or {"ok": True},
    )

    backend.send_keys(["F5"], window="class:V8TopLevelFrame")

    assert captured["payload"]["window"] == "class:V8TopLevelFrame"
    assert captured["payload"]["client_target"] == target


def test_remote_active_context_rejects_target_without_lifecycle_before_post(monkeypatch) -> None:
    backend = db.RemoteAgentBackend(
        "host:8001",
        client_port=15383,
        client_target={"kind": "host-agent-testclient", "pid": 4321, "port": 15383},
        client_target_required=True,
    )
    monkeypatch.setattr(
        backend,
        "_ensure_ready",
        lambda: {"capabilities": [db.HOST_AGENT_TESTCLIENT_WINDOW_TARGET_CAPABILITY]},
    )
    monkeypatch.setattr(
        backend,
        "_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("lifecycle-less display POST must not run")
        ),
    )

    with pytest.raises(db.DisplayBackendError) as exc:
        backend.send_keys(["F5"], window="class:V8TopLevelFrame")

    assert exc.value.code == "active-testclient-client-target-invalid"


def test_remote_implicit_client_target_requires_advertised_capability(monkeypatch) -> None:
    backend = db.RemoteAgentBackend(
        "host:8001",
        client_target={"kind": "host-agent-testclient", "pid": 4321, "port": 15383},
    )
    monkeypatch.setattr(backend, "_ensure_ready", lambda: {"version": "legacy", "capabilities": []})
    monkeypatch.setattr(
        backend,
        "_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("unsafe display POST must not run")),
    )

    with pytest.raises(db.DisplayBackendError) as exc:
        backend.send_keys(["F5"])

    assert exc.value.code == "host-agent-testclient-window-target-unsupported"


def test_remote_active_context_without_client_target_refuses_implicit_port_downgrade(monkeypatch) -> None:
    backend = db.RemoteAgentBackend(
        "host:8001",
        client_port=15444,
        client_target_required=True,
    )
    monkeypatch.setattr(
        backend,
        "_ensure_ready",
        lambda: {
            "version": "0.1.10-testclient-lifecycle-handle",
            "capabilities": [db.HOST_AGENT_TESTCLIENT_LIFECYCLE_STOP_CAPABILITY],
        },
    )
    monkeypatch.setattr(
        backend,
        "_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("implicit display POST must not downgrade to client_port")
        ),
    )

    with pytest.raises(db.DisplayBackendError) as exc:
        backend.send_keys(["F5"])

    assert exc.value.code == "active-testclient-client-target-missing"


def test_remote_active_context_with_invalid_client_target_refuses_before_post(monkeypatch) -> None:
    backend = db.RemoteAgentBackend(
        "host:8001",
        client_port=15444,
        client_target={"kind": "host-agent-testclient", "port": 15444},
        client_target_required=True,
    )
    monkeypatch.setattr(
        backend,
        "_ensure_ready",
        lambda: {"capabilities": [db.HOST_AGENT_TESTCLIENT_WINDOW_TARGET_CAPABILITY]},
    )
    monkeypatch.setattr(
        backend,
        "_json",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("invalid target display POST must not run")
        ),
    )

    with pytest.raises(db.DisplayBackendError) as exc:
        backend.send_keys(["F5"])

    assert exc.value.code == "active-testclient-client-target-invalid"
