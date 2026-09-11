from __future__ import annotations

import json
from typing import Any

from qa_mcp import doctor
from qa_mcp import mcp_server
from qa_mcp.config import Settings


class FakeBackend:
    def __init__(
        self,
        *,
        health: dict[str, Any] | None = None,
        windows: list[dict[str, Any]] | None = None,
        version: dict[str, Any] | None = None,
    ) -> None:
        self._health = health or {
            "ok": True,
            "listener": "[::]:8001",
            "platform_catalog": {
                "configured": True,
                "executables": {
                    "1cv8": {"available": True, "version": "8.3.27.2130"},
                    "ibcmd": {"available": True, "version": "8.3.27.2130"},
                },
            },
            "bsl_agent": {"configured": False, "state": "disabled", "restart_count": 0},
        }
        self._windows = windows or [{"title": "1C:Enterprise", "class": "V8TopLevelFrameSDI"}]
        self._version = version or {"ok": True, "version": "0.1.0-testclient-launch", "sha256": "abc"}

    def handshake(self) -> dict[str, Any]:
        return dict(self._version)

    def health(self) -> dict[str, Any]:
        return dict(self._health)

    def list_windows(self, display: str, *, geometry: bool = True) -> list[dict[str, Any]]:
        return list(self._windows)


def _check(result: dict[str, Any], name: str) -> dict[str, Any]:
    return next(item for item in result["checks"] if item["name"] == name)


def _passing_probes(backend: FakeBackend | None = None) -> doctor.DoctorProbes:
    return doctor.DoctorProbes(
        backend_factory=lambda env=None: backend or FakeBackend(),
        port_is_listening=lambda host, port, timeout: True,
        testclient_smoke=lambda host, port, timeout: {
            "name": "testclient_smoke",
            "status": "pass",
            "ok": True,
            "data": {"host": host, "port": port, "initial_byte_count": 12},
        },
        com_connector_doctor=lambda **kwargs: {"ok": True, "transport": "com"},
        effective_user_probe=lambda: "Админ",
    )


def test_settings_reports_bearer_presence_without_value() -> None:
    settings = Settings.from_env({"QA_MCP_BEARER_TOKEN": "secret-token"})

    assert settings.bearer_token_present is True
    assert "secret-token" not in repr(settings)


def test_doctor_healthy_chain_is_green_and_secret_safe() -> None:
    result = doctor.run_doctor(
        env={
            "QA_MCP_BEARER_TOKEN": "secret-token",
            "QA_MCP_REMOTE_CLIENT": "1",
            "QA_MCP_HOST_AGENT": "host.docker.internal:8001",
            "QA_MCP_HOST_AGENT_TOKEN": "agent-secret",
            "QA_MCP_DOCTOR_COM_INFOBASE": r"C:\Bases\Finans",
            "QA_MCP_DOCTOR_COM_USER": "Админ",
        },
        host="host.docker.internal",
        port=15381,
        probes=_passing_probes(),
    )

    assert result["ok"] is True
    assert result["complete"] is True
    assert [item["status"] for item in result["checks"]] == ["pass"] * len(result["checks"])
    assert _check(result, "mcp_http_auth")["data"]["token_env_present"] is True
    assert _check(result, "container_host_agent_route")["data"]["listener"] == "[::]:8001"
    assert _check(result, "testclient_smoke")["data"]["initial_byte_count"] == 12
    payload = json.dumps(result, ensure_ascii=False)
    assert "secret-token" not in payload
    assert "agent-secret" not in payload


def test_doctor_reports_host_agent_protocol_relationship() -> None:
    backend = FakeBackend(version={
        "ok": True,
        "version": "0.1.99-future-build",
        "display_protocol": "ai1c.windows-host-display-http.v1",
        "version_relationship": "protocol-compatible",
    })

    result = doctor.run_doctor(
        env={
            "QA_MCP_BEARER_TOKEN": "secret-token",
            "QA_MCP_REMOTE_CLIENT": "1",
            "QA_MCP_HOST_AGENT": "host.docker.internal:8001",
            "QA_MCP_HOST_AGENT_TOKEN": "agent-secret",
            "QA_MCP_DOCTOR_COM_INFOBASE": r"C:\Bases\Finans",
        },
        probes=_passing_probes(backend),
    )

    check = _check(result, "host_agent_http")
    assert check["status"] == "pass"
    assert check["data"]["version"] == "0.1.99-future-build"
    assert check["data"]["display_protocol"] == "ai1c.windows-host-display-http.v1"
    assert check["data"]["version_relationship"] == "protocol-compatible"


def test_standalone_doctor_excludes_suite_platform_com_and_bsl_dependencies() -> None:
    com_called = False

    def com_probe(**_kwargs: Any) -> dict[str, Any]:
        nonlocal com_called
        com_called = True
        return {"ok": True}

    result = doctor.run_doctor(
        env={
            "QA_MCP_BEARER_TOKEN": "secret-token",
            "QA_MCP_REMOTE_CLIENT": "1",
            "QA_MCP_HOST_AGENT": "host.docker.internal:8001",
            "QA_MCP_HOST_AGENT_TOKEN": "agent-secret",
            "QA_MCP_DOCTOR_COM_INFOBASE": r"C:\Bases\Finans",
        },
        standalone=True,
        probes=doctor.DoctorProbes(
            backend_factory=lambda env=None: FakeBackend(),
            port_is_listening=lambda host, port, timeout: True,
            testclient_smoke=lambda host, port, timeout: {
                "name": "testclient_smoke", "status": "pass", "ok": True
            },
            com_connector_doctor=com_probe,
        ),
    )

    names = {item["name"] for item in result["checks"]}
    assert result["mode"] == "standalone"
    assert "mcp_http_auth" in names
    assert names.isdisjoint({"platform_discovery", "bsl_agent_supervision", "com_connector_doctor"})
    assert com_called is False


def test_doctor_platform_discovery_is_designer_dump_free() -> None:
    backend = FakeBackend(
        health={
            "ok": True,
            "listener": "[::]:8001",
            "platform_catalog": {
                "configured": True,
                "executables": {
                    "designer": {"available": True, "version": "8.3.27.2130"},
                    "ibcmd": {"available": True, "version": "8.3.27.2130"},
                },
            },
        },
    )

    result = doctor.run_doctor(
        env={
            "QA_MCP_BEARER_TOKEN": "secret-token",
            "QA_MCP_REMOTE_CLIENT": "1",
            "QA_MCP_HOST_AGENT": "host.docker.internal:8001",
            "QA_MCP_HOST_AGENT_TOKEN": "agent-secret",
            "QA_MCP_DOCTOR_COM_INFOBASE": r"C:\Bases\Finans",
            "QA_MCP_DOCTOR_COM_USER": "Админ",
        },
        probes=_passing_probes(backend),
    )

    platform = _check(result, "platform_discovery")
    assert platform["status"] == "pass"
    assert platform["data"]["diagnostic_strategy"] == "host-agent-health-only"
    assert platform["data"]["designer_metadata_dump"] is False
    assert "designer" in platform["data"]["available"]


def test_doctor_missing_bearer_env_is_legible() -> None:
    result = doctor.run_doctor(
        env={},
        require_bearer_token=True,
        probes=doctor.DoctorProbes(
            port_is_listening=lambda host, port, timeout: True,
            testclient_smoke=lambda host, port, timeout: {"name": "testclient_smoke", "status": "pass", "ok": True},
        ),
    )

    auth = _check(result, "mcp_http_auth")
    assert result["ok"] is False
    assert auth["status"] == "fail"
    assert auth["required"] is True
    assert auth["code"] == "bearer-token-env-missing"
    assert auth["data"] == {"token_env_present": False, "token_env": "QA_MCP_BEARER_TOKEN"}


def test_doctor_uses_process_environment_by_default(monkeypatch) -> None:
    monkeypatch.setenv("QA_MCP_BEARER_TOKEN", "secret-token")

    result = doctor.run_doctor(
        require_bearer_token=True,
        probes=doctor.DoctorProbes(
            port_is_listening=lambda host, port, timeout: True,
            testclient_smoke=lambda host, port, timeout: {"name": "testclient_smoke", "status": "pass", "ok": True},
        ),
    )

    auth = _check(result, "mcp_http_auth")
    assert auth["status"] == "pass"
    assert auth["data"] == {"token_env_present": True, "token_env": "QA_MCP_BEARER_TOKEN"}
    assert "secret-token" not in json.dumps(result)


def test_doctor_rejected_bearer_preserves_presence_hint() -> None:
    probes = doctor.DoctorProbes(
        port_is_listening=lambda host, port, timeout: True,
        testclient_smoke=lambda host, port, timeout: {"name": "testclient_smoke", "status": "pass", "ok": True},
        proxy_auth_probe=lambda settings: {"ok": False, "code": "proxy-auth-rejected", "detail": "unauthorized"},
    )

    result = doctor.run_doctor(env={"QA_MCP_BEARER_TOKEN": "secret-token"}, probes=probes)

    auth = _check(result, "mcp_http_auth")
    assert auth["status"] == "fail"
    assert auth["code"] == "proxy-auth-rejected"
    assert auth["data"]["token_env_present"] is True
    assert "secret-token" not in json.dumps(result)


def test_doctor_login_dialog_stuck_is_distinct() -> None:
    backend = FakeBackend(windows=[{"title": "Доступ к информационной базе", "class": "#32770"}])

    result = doctor.run_doctor(
        env={
            "QA_MCP_BEARER_TOKEN": "secret-token",
            "QA_MCP_REMOTE_CLIENT": "1",
            "QA_MCP_HOST_AGENT": "host.docker.internal:8001",
            "QA_MCP_HOST_AGENT_TOKEN": "agent-secret",
            "QA_MCP_DOCTOR_COM_USER": "Администратор",
        },
        probes=_passing_probes(backend),
    )

    login = _check(result, "login_dialog_state")
    user = _check(result, "effective_user")
    assert result["ok"] is False
    assert login["code"] == "login-dialog-stuck"
    assert user["code"] == "effective-user-mismatch"
    assert user["data"] == {"configured_user": "Администратор", "effective_user": "Админ"}


def test_doctor_cli_outputs_json_and_failed_exit(monkeypatch, capsys) -> None:
    monkeypatch.setattr(doctor, "run_doctor", lambda **kwargs: {"ok": False, "checks": [{"name": "x"}]})

    exit_code = doctor.main(["--no-require-bearer", "--timeout-sec", "0.1"])

    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload == {"ok": False, "checks": [{"name": "x"}]}


def test_mcp_doctor_wrapper_delegates(monkeypatch) -> None:
    observed: dict[str, Any] = {}

    def fake_run(**kwargs: Any) -> dict[str, Any]:
        observed.update(kwargs)
        return {"ok": True, "checks": []}

    monkeypatch.setattr(mcp_server, "run_qa_mcp_doctor", fake_run)

    result = mcp_server.qa_mcp_doctor(
        host="h",
        port=15444,
        require_bearer_token=False,
        com_infobase_path=r"C:\Bases\Finans",
        com_user="Админ",
        com_password="secret",
        com_query="ВЫБРАТЬ 1",
        timeout_sec=1.5,
    )

    assert result == {"ok": True, "checks": []}
    assert observed == {
        "host": "h",
        "port": 15444,
        "require_bearer_token": False,
        "com_infobase_path": r"C:\Bases\Finans",
        "com_user": "Админ",
        "com_password": "secret",
        "com_query": "ВЫБРАТЬ 1",
        "timeout_sec": 1.5,
        "standalone": True,
    }


def test_mcp_doctor_wrapper_omits_timeout_when_not_explicit(monkeypatch) -> None:
    observed: dict[str, Any] = {}

    def fake_run(**kwargs: Any) -> dict[str, Any]:
        observed.update(kwargs)
        return {"ok": True, "checks": []}

    monkeypatch.setattr(mcp_server, "run_qa_mcp_doctor", fake_run)

    result = mcp_server.qa_mcp_doctor()

    assert result == {"ok": True, "checks": []}
    assert observed["timeout_sec"] is None
    assert observed["require_bearer_token"] is False


def test_mcp_doctor_wrapper_requires_bearer_by_default_for_http(monkeypatch) -> None:
    observed: dict[str, Any] = {}
    monkeypatch.setattr(mcp_server, "_SETTINGS", Settings.from_env({"QA_MCP_TRANSPORT": "streamable-http"}))
    monkeypatch.setattr(
        mcp_server,
        "run_qa_mcp_doctor",
        lambda **kwargs: observed.update(kwargs) or {"ok": True, "checks": []},
    )

    mcp_server.qa_mcp_doctor()

    assert observed["require_bearer_token"] is True


def test_doctor_com_timeout_defaults_from_environment() -> None:
    observed: dict[str, Any] = {}

    def com_probe(**kwargs: Any) -> dict[str, Any]:
        observed.update(kwargs)
        return {"ok": True, "transport": "com"}

    result = doctor.run_doctor(
        env={
            "QA_MCP_BEARER_TOKEN": "secret-token",
            "QA_MCP_REMOTE_CLIENT": "1",
            "QA_MCP_HOST_AGENT": "host.docker.internal:8001",
            "QA_MCP_HOST_AGENT_TOKEN": "agent-secret",
            "QA_MCP_DOCTOR_COM_INFOBASE": r"C:\Bases\Finans",
            "QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS": "90",
        },
        host="host.docker.internal",
        port=15381,
        probes=doctor.DoctorProbes(
            backend_factory=lambda env=None: FakeBackend(),
            port_is_listening=lambda host, port, timeout: True,
            testclient_smoke=lambda host, port, timeout: {"name": "testclient_smoke", "status": "pass", "ok": True},
            com_connector_doctor=com_probe,
            effective_user_probe=lambda: None,
        ),
    )

    assert observed["timeout_sec"] == 90.0
    assert _check(result, "com_connector_doctor")["data"]["timeout_sec"] == 90.0


def test_doctor_explicit_timeout_overrides_environment() -> None:
    observed: dict[str, Any] = {}

    def com_probe(**kwargs: Any) -> dict[str, Any]:
        observed.update(kwargs)
        return {"ok": True, "transport": "com"}

    result = doctor.run_doctor(
        env={
            "QA_MCP_BEARER_TOKEN": "secret-token",
            "QA_MCP_REMOTE_CLIENT": "1",
            "QA_MCP_HOST_AGENT": "host.docker.internal:8001",
            "QA_MCP_HOST_AGENT_TOKEN": "agent-secret",
            "QA_MCP_DOCTOR_COM_INFOBASE": r"C:\Bases\Finans",
            "QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS": "90",
        },
        timeout_sec=1.5,
        probes=doctor.DoctorProbes(
            backend_factory=lambda env=None: FakeBackend(),
            port_is_listening=lambda host, port, timeout: True,
            testclient_smoke=lambda host, port, timeout: {"name": "testclient_smoke", "status": "pass", "ok": True},
            com_connector_doctor=com_probe,
            effective_user_probe=lambda: None,
        ),
    )

    assert observed["timeout_sec"] == 1.5
    assert _check(result, "com_connector_doctor")["data"]["timeout_sec"] == 1.5


def test_doctor_optional_effective_user_skip_is_partial_success() -> None:
    result = doctor.run_doctor(
        env={
            "QA_MCP_BEARER_TOKEN": "secret-token",
            "QA_MCP_REMOTE_CLIENT": "1",
            "QA_MCP_HOST_AGENT": "host.docker.internal:8001",
            "QA_MCP_HOST_AGENT_TOKEN": "agent-secret",
            "QA_MCP_DOCTOR_COM_INFOBASE": r"C:\Bases\Finans",
        },
        probes=doctor.DoctorProbes(
            backend_factory=lambda env=None: FakeBackend(),
            port_is_listening=lambda host, port, timeout: True,
            testclient_smoke=lambda host, port, timeout: {"name": "testclient_smoke", "status": "pass", "ok": True},
            com_connector_doctor=lambda **kwargs: {"ok": True, "transport": "com"},
            effective_user_probe=None,
        ),
    )

    user = _check(result, "effective_user")
    assert result["ok"] is True
    assert result["status"] == "partial"
    assert user["status"] == "skipped"
    assert user["required"] is False


def test_doctor_bsl_agent_supervision_disabled_is_healthy() -> None:
    backend = FakeBackend(health={
        "ok": True,
        "listener": "[::]:8001",
        "platform_catalog": {"configured": True, "executables": {"ibcmd": {"available": True}}},
        "bsl_agent": {"configured": False, "state": "disabled"},
    })
    result = doctor.run_doctor(
        env={"QA_MCP_BEARER_TOKEN": "secret", "QA_MCP_HOST_AGENT": "host:8001", "QA_MCP_HOST_AGENT_TOKEN": "agent-secret", "QA_MCP_DOCTOR_COM_INFOBASE": r"C:\Bases\Finans"},
        probes=_passing_probes(backend),
    )
    check = _check(result, "bsl_agent_supervision")
    assert check["status"] == "pass"
    assert check["data"] == {"configured": False, "state": "disabled"}


def test_doctor_bsl_agent_supervision_ready_reports_bounded_status() -> None:
    backend = FakeBackend(health={
        "ok": True,
        "listener": "[::]:8001",
        "platform_catalog": {"configured": True, "executables": {"ibcmd": {"available": True}}},
        "bsl_agent": {
            "configured": True,
            "state": "ready",
            "version": "bsl-agent-1",
            "protocol": "ai1c.bsl-agent-workstation-http.v1",
            "restart_count": 2,
        },
    })
    result = doctor.run_doctor(
        env={"QA_MCP_BEARER_TOKEN": "secret", "QA_MCP_HOST_AGENT": "host:8001", "QA_MCP_HOST_AGENT_TOKEN": "agent-secret", "QA_MCP_DOCTOR_COM_INFOBASE": r"C:\Bases\Finans"},
        probes=_passing_probes(backend),
    )
    check = _check(result, "bsl_agent_supervision")
    assert check["status"] == "pass"
    assert check["data"] == {
        "configured": True,
        "state": "ready",
        "version": "bsl-agent-1",
        "protocol": "ai1c.bsl-agent-workstation-http.v1",
        "restart_count": 2,
    }


def test_doctor_bsl_agent_supervision_configured_not_ready_fails() -> None:
    backend = FakeBackend(health={
        "ok": True,
        "listener": "[::]:8001",
        "platform_catalog": {"configured": True, "executables": {"ibcmd": {"available": True}}},
        "bsl_agent": {"configured": True, "state": "backoff", "restart_count": 3, "last_error": "process-exited"},
    })
    result = doctor.run_doctor(
        env={"QA_MCP_BEARER_TOKEN": "secret", "QA_MCP_HOST_AGENT": "host:8001", "QA_MCP_HOST_AGENT_TOKEN": "agent-secret", "QA_MCP_DOCTOR_COM_INFOBASE": r"C:\Bases\Finans"},
        probes=_passing_probes(backend),
    )
    check = _check(result, "bsl_agent_supervision")
    assert check["status"] == "fail"
    assert check["code"] == "bsl-agent-not-ready"
    assert "last_error" not in check["data"]
