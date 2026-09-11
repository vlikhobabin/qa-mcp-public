"""Secret-safe end-to-end diagnostics for qa-mcp model-B setup."""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from . import com_host
from .config import Settings
from .core.runtime_target import (
    RuntimeTargetBindingError,
    RuntimeTargetResolution,
    resolve_runtime_target,
    runtime_target_readiness,
)
from .protocol import lifecycle as client_lifecycle
from .protocol import display_backend as client_display
from .protocol.session import TestClientSession

Check = dict[str, Any]
Env = Mapping[str, str]
ProxyAuthProbe = Callable[[Settings], Check]
EffectiveUserProbe = Callable[[], str | None]
PortProbe = Callable[[str, int, float], bool]
SmokeProbe = Callable[[str, int, float], Check]
BackendFactory = Callable[[Env | None], client_display.RemoteAgentBackend]
ComDoctorProbe = Callable[..., dict[str, Any]]


LOGIN_DIALOG_MARKERS = (
    "доступ к информационной базе",
    "аутентификация",
    "authentication",
    "information base access",
    "access to infobase",
    "пользователь",
    "пароль",
)


@dataclass(frozen=True)
class DoctorProbes:
    backend_factory: BackendFactory = client_display.RemoteAgentBackend.from_env
    port_is_listening: PortProbe = client_lifecycle.port_is_listening
    testclient_smoke: SmokeProbe | None = None
    com_connector_doctor: ComDoctorProbe = com_host.com_connector_doctor
    proxy_auth_probe: ProxyAuthProbe | None = None
    effective_user_probe: EffectiveUserProbe | None = None


def _check(
    name: str,
    status: str,
    *,
    code: str = "",
    hint: str = "",
    data: dict[str, Any] | None = None,
    required: bool = True,
) -> Check:
    result: Check = {"name": name, "status": status, "ok": status == "pass", "required": bool(required)}
    if status == "skipped":
        result["ok"] = None
    if code:
        result["code"] = code
    if hint:
        result["hint"] = hint
    if data:
        result["data"] = data
    return result


def _failure(name: str, code: str, hint: str, *, data: dict[str, Any] | None = None, required: bool = True) -> Check:
    return _check(name, "fail", code=code, hint=hint, data=data, required=required)


def _skip(name: str, code: str, hint: str, *, data: dict[str, Any] | None = None, required: bool = False) -> Check:
    return _check(name, "skipped", code=code, hint=hint, data=data, required=required)


def _pass(name: str, *, code: str = "", data: dict[str, Any] | None = None, required: bool = True) -> Check:
    return _check(name, "pass", code=code, data=data, required=required)


def _proxy_auth_check(settings: Settings, *, require_bearer_token: bool, probe: ProxyAuthProbe | None) -> Check:
    token_env_present = bool(settings.bearer_token_present)
    data = {"token_env_present": token_env_present, "token_env": "QA_MCP_BEARER_TOKEN"}
    if not require_bearer_token:
        return _skip(
            "mcp_http_auth",
            "proxy-auth-not-required",
            "Bearer auth check was disabled.",
            data=data,
        )
    if not token_env_present:
        return _failure(
            "mcp_http_auth",
            "bearer-token-env-missing",
            "Set QA_MCP_BEARER_TOKEN in the active qa-mcp/MCP process environment.",
            data=data,
        )
    if probe is None:
        return _pass("mcp_http_auth", code="bearer-token-env-present", data=data)
    try:
        result = probe(settings)
    except Exception as exc:  # noqa: BLE001 - diagnostics must stay structured.
        return _failure("mcp_http_auth", "http-auth-probe-failed", str(exc), data=data)
    if result.get("status") == "pass" or result.get("ok") is True:
        return _pass("mcp_http_auth", code=str(result.get("code") or "http-auth-ok"), data=data)
    return _failure(
        "mcp_http_auth",
        str(result.get("code") or result.get("error") or "proxy-auth-rejected"),
        str(result.get("hint") or result.get("detail") or "MCP proxy rejected the bearer credential."),
        data=data,
    )


def _safe_host_agent_data(settings: Settings) -> dict[str, Any]:
    return {
        "configured": bool(settings.host_agent),
        "address": settings.host_agent or None,
        "token_env_present": bool(settings.host_agent_token),
        "token_env": "QA_MCP_HOST_AGENT_TOKEN",
    }


def _host_agent_checks(
    settings: Settings,
    *,
    env: Mapping[str, str] | None,
    probes: DoctorProbes,
) -> tuple[Check, Check, Check, client_display.RemoteAgentBackend | None, dict[str, Any] | None]:
    data = _safe_host_agent_data(settings)
    if not settings.host_agent:
        check = _failure(
            "host_agent_http",
            "host-agent-not-configured",
            "Set QA_MCP_HOST_AGENT and QA_MCP_HOST_AGENT_TOKEN for model-B host-agent diagnostics.",
            data=data,
        ) if settings.remote_client else _skip(
            "host_agent_http",
            "host-agent-not-configured",
            "QA_MCP_HOST_AGENT is not configured on this contour.",
            data=data,
        )
        return (
            check,
            _skip("container_host_agent_route", "host-agent-check-not-run", "Host-agent HTTP check did not pass."),
            _skip("platform_discovery", "host-agent-check-not-run", "Host-agent HTTP check did not pass."),
            None,
            None,
        )

    backend = probes.backend_factory(env)
    try:
        version = backend.handshake()
        host_agent = _pass(
            "host_agent_http",
            data={
                **data,
                "version": version.get("version"),
                "display_protocol": version.get("display_protocol"),
                "version_relationship": version.get("version_relationship"),
            },
        )
    except client_display.DisplayBackendError as exc:
        return (
            _failure("host_agent_http", exc.code, exc.detail, data=data),
            _skip("container_host_agent_route", "host-agent-check-not-run", "Host-agent HTTP check did not pass."),
            _skip("platform_discovery", "host-agent-check-not-run", "Host-agent HTTP check did not pass."),
            backend,
            None,
        )

    try:
        health = backend.health()
        route = _pass(
            "container_host_agent_route",
            data={
                "address": settings.host_agent,
                "remote_client": settings.remote_client,
                "http_ok": bool(health.get("ok", True)),
                "listener": health.get("listener"),
            },
        )
    except client_display.DisplayBackendError as exc:
        return (
            host_agent,
            _failure("container_host_agent_route", exc.code, exc.detail, data={"address": settings.host_agent}),
            _skip("platform_discovery", "host-agent-health-not-available", "Host-agent health was not available."),
            backend,
            None,
        )

    platform = _platform_check(health)
    return host_agent, route, platform, backend, health


def _platform_check(health: dict[str, Any]) -> Check:
    diagnostics_policy = {
        "diagnostic_strategy": "host-agent-health-only",
        "designer_metadata_dump": False,
    }
    catalog = health.get("platform_catalog")
    if not isinstance(catalog, dict):
        return _skip(
            "platform_discovery",
            "platform-catalog-not-reported",
            "Host-agent health did not report platform_catalog.",
            data=diagnostics_policy,
        )
    if catalog.get("error"):
        return _failure(
            "platform_discovery",
            str(catalog.get("error")),
            "Configure the host-agent platform catalog so 1C executables can be discovered.",
            data={**diagnostics_policy, "configured": bool(catalog.get("configured"))},
        )
    executables = catalog.get("executables") if isinstance(catalog.get("executables"), dict) else {}
    available = sorted(name for name, info in executables.items() if isinstance(info, dict) and info.get("available"))
    if not available:
        return _failure(
            "platform_discovery",
            "platform-executable-not-found",
            "No allowlisted 1C platform executable was available in host-agent health.",
            data={**diagnostics_policy, "configured": bool(catalog.get("configured"))},
        )
    return _pass(
        "platform_discovery",
        data={**diagnostics_policy, "configured": bool(catalog.get("configured")), "available": available},
    )


def _bsl_agent_check(health: dict[str, Any] | None) -> Check:
    if health is None:
        return _skip(
            "bsl_agent_supervision",
            "host-agent-health-not-available",
            "Host-agent health was not available for workstation bsl-agent supervision.",
        )
    helper = health.get("bsl_agent")
    if not isinstance(helper, dict):
        return _skip(
            "bsl_agent_supervision",
            "bsl-agent-status-not-reported",
            "This compatible host-agent predates workstation bsl-agent supervision status.",
        )
    data = {
        key: helper[key]
        for key in ("configured", "state", "version", "protocol", "restart_count")
        if key in helper
    }
    if helper.get("configured") is not True:
        data.setdefault("configured", False)
        data.setdefault("state", "disabled")
        return _pass("bsl_agent_supervision", data=data)
    if helper.get("state") == "ready":
        return _pass("bsl_agent_supervision", data=data)
    return _failure(
        "bsl_agent_supervision",
        "bsl-agent-not-ready",
        "The configured workstation bsl-agent is not ready; inspect host-agent health and local ignored logs.",
        data=data,
    )


def _default_testclient_smoke(host: str, port: int, timeout_sec: float) -> Check:
    try:
        with TestClientSession(
            host=host,
            port=port,
            connect_timeout_sec=timeout_sec,
            read_timeout_sec=min(timeout_sec, 2.0),
            idle_timeout_sec=0.05,
        ) as session:
            try:
                initial = session.read_initial()
            except socket.timeout:
                initial = b""
    except OSError as exc:
        return _failure(
            "testclient_smoke",
            "testclient-smoke-connect-failed",
            str(exc),
            data={"host": host, "port": int(port)},
        )
    return _pass("testclient_smoke", data={"host": host, "port": int(port), "initial_byte_count": len(initial)})


def _testclient_checks(
    settings: Settings,
    *,
    host: str,
    port: int,
    timeout_sec: float,
    probes: DoctorProbes,
) -> tuple[Check, Check]:
    try:
        listening = probes.port_is_listening(host, int(port), timeout_sec)
    except Exception as exc:  # noqa: BLE001
        listening = False
        tport = _failure("testclient_tport", "tport-probe-failed", str(exc), data={"host": host, "port": int(port)})
    else:
        tport = _pass("testclient_tport", data={"host": host, "port": int(port)}) if listening else _failure(
            "testclient_tport",
            "testclient-tport-unreachable",
            "Start or attach a 1C /TESTCLIENT endpoint and verify QA_MCP_CLIENT_HOST/QA_MCP_CLIENT_PORT.",
            data={"host": host, "port": int(port), "remote_client": settings.remote_client},
        )
    if not listening:
        return tport, _skip("testclient_smoke", "tport-not-listening", "TestClient TPort is not reachable.")
    smoke = (probes.testclient_smoke or _default_testclient_smoke)(host, int(port), timeout_sec)
    return tport, smoke


def _window_texts_from_backend(backend: client_display.RemoteAgentBackend | None) -> list[str]:
    if backend is None:
        return []
    try:
        windows = backend.list_windows("", geometry=True)
    except client_display.DisplayBackendError:
        return []
    texts: list[str] = []
    for item in windows:
        if isinstance(item, dict):
            texts.extend(str(item.get(key) or "") for key in ("title", "caption", "class"))
    return [text for text in texts if text]


def login_dialog_state(texts: list[str]) -> dict[str, Any]:
    lowered = [text.lower() for text in texts if text]
    for original, value in zip(texts, lowered, strict=False):
        if any(marker in value for marker in LOGIN_DIALOG_MARKERS):
            return {"state": "login-dialog-stuck", "matched": original}
    if texts:
        return {"state": "not-detected", "sample_count": len(texts)}
    return {"state": "unknown", "sample_count": 0}


def _login_dialog_check(backend: client_display.RemoteAgentBackend | None) -> Check:
    state = login_dialog_state(_window_texts_from_backend(backend))
    if state["state"] == "login-dialog-stuck":
        return _failure(
            "login_dialog_state",
            "login-dialog-stuck",
            "The TestClient appears to be stopped at the 1C login/access dialog; verify the launch user.",
            data=state,
        )
    if state["state"] == "unknown":
        return _skip(
            "login_dialog_state",
            "login-dialog-evidence-unavailable",
            "No host-agent or TestClient window evidence was available for login-dialog detection.",
            data=state,
        )
    return _pass("login_dialog_state", data=state)


def _effective_user_check(configured_user: str, probe: EffectiveUserProbe | None) -> Check:
    if probe is None:
        return _skip(
            "effective_user",
            "effective-user-not-queryable",
            "No effective-user probe is available on this contour.",
            data={"configured_user": configured_user or None},
        )
    try:
        effective = probe()
    except Exception as exc:  # noqa: BLE001
        return _failure("effective_user", "effective-user-probe-failed", str(exc), data={"configured_user": configured_user or None})
    data = {"configured_user": configured_user or None, "effective_user": effective or None}
    if not effective:
        return _skip("effective_user", "effective-user-not-queryable", "The probe returned no effective user.", data=data)
    if configured_user and effective != configured_user:
        return _failure(
            "effective_user",
            "effective-user-mismatch",
            "Configured launch user differs from the effective infobase user.",
            data=data,
        )
    return _pass("effective_user", data=data)


def _com_check(settings: Settings, *, probes: DoctorProbes, timeout_sec: float) -> Check:
    if not settings.doctor_com_infobase_path:
        return _skip(
            "com_connector_doctor",
            "com-infobase-not-configured",
            "Set QA_MCP_DOCTOR_COM_INFOBASE or pass --com-infobase-path to run the COMConnector doctor.",
            data={"infobase_path_present": False},
        )
    data = {
        "infobase_path_present": True,
        "user": settings.doctor_com_user or None,
        "query_present": bool(settings.doctor_com_query),
        "timeout_sec": float(timeout_sec),
    }
    try:
        result = probes.com_connector_doctor(
            infobase_path=settings.doctor_com_infobase_path,
            user=settings.doctor_com_user,
            password=settings.doctor_com_password,
            query=settings.doctor_com_query,
            timeout_sec=timeout_sec,
        )
    except Exception as exc:  # noqa: BLE001 - diagnostics must stay structured.
        return _failure("com_connector_doctor", "com-doctor-probe-failed", str(exc), data=data)
    if result.get("ok") is True:
        return _pass("com_connector_doctor", data={**data, "transport": result.get("transport")})
    return _failure(
        "com_connector_doctor",
        str(result.get("error") or "com-doctor-failed"),
        str(result.get("detail") or "COMConnector doctor did not pass."),
        data=data,
    )


def _with_overrides(env: Mapping[str, str] | None, overrides: Mapping[str, str]) -> dict[str, str]:
    merged = dict(os.environ if env is None else env)
    for key, value in overrides.items():
        if value:
            merged[key] = value
    return merged


def run_doctor(
    *,
    env: Mapping[str, str] | None = None,
    host: str | None = None,
    port: int | None = None,
    require_bearer_token: bool = True,
    com_infobase_path: str = "",
    com_user: str = "",
    com_password: str = "",
    com_query: str = "",
    timeout_sec: float | None = None,
    probes: DoctorProbes | None = None,
    standalone: bool = False,
    runtime_target: RuntimeTargetResolution | None = None,
    resolve_configured_target: bool = True,
) -> dict[str, Any]:
    """Run the end-to-end diagnostic chain and return a JSON-serializable result."""
    env_map = _with_overrides(env, {
        "QA_MCP_DOCTOR_COM_INFOBASE": com_infobase_path,
        "QA_MCP_DOCTOR_COM_USER": com_user,
        "QA_MCP_DOCTOR_COM_PASSWORD": com_password,
        "QA_MCP_DOCTOR_COM_QUERY": com_query,
    })
    try:
        resolution = (
            resolve_runtime_target(env_map)
            if resolve_configured_target
            else runtime_target
        )
        target_readiness = runtime_target_readiness(resolution)
    except RuntimeTargetBindingError as error:
        check = _failure(
            "runtime_target_binding",
            error.code,
            "Resolve the declared provider-local target binding before runtime probes.",
            data={"state": "invalid", "field": error.field},
        )
        return {
            "ok": False,
            "complete": False,
            "status": "fail",
            "checks": [check],
            "failed": 1,
            "skipped": 0,
            "mode": "standalone" if standalone else "extended",
            "target": {"bound": True, "state": "invalid"},
        }
    settings = Settings.from_env(env_map)
    probes = probes or DoctorProbes()
    target_host = host or settings.client_host
    target_port = int(port or settings.client_port)
    effective_timeout_sec = float(timeout_sec) if timeout_sec is not None else float(settings.doctor_com_timeout_sec)

    target_check = _pass(
        "runtime_target_binding",
        code=(
            "runtime-target-ready"
            if target_readiness["active"]
            else "runtime-target-unbound"
        ),
        data={
            key: target_readiness[key]
            for key in ("state", "target", "evidence", "observation")
            if key in target_readiness
        },
    )
    checks: list[Check] = [
        target_check,
        _proxy_auth_check(
            settings,
            require_bearer_token=require_bearer_token,
            probe=probes.proxy_auth_probe,
        ),
    ]
    host_agent, route, platform, backend, _health = _host_agent_checks(settings, env=env_map, probes=probes)
    checks.extend([host_agent, route])
    tport, smoke = _testclient_checks(
        settings,
        host=target_host,
        port=target_port,
        timeout_sec=effective_timeout_sec,
        probes=probes,
    )
    checks.extend([tport, smoke, _login_dialog_check(backend)])
    if not standalone:
        checks.extend([
            platform,
            _bsl_agent_check(_health),
            _effective_user_check(settings.doctor_com_user, probes.effective_user_probe),
            _com_check(settings, probes=probes, timeout_sec=effective_timeout_sec),
        ])

    failed = [check for check in checks if check["status"] == "fail" and check.get("required", True)]
    skipped = [check for check in checks if check["status"] == "skipped"]
    return {
        "ok": not failed,
        "complete": not failed and not skipped,
        "status": "pass" if not failed and not skipped else ("fail" if failed else "partial"),
        "checks": checks,
        "failed": len(failed),
        "skipped": len(skipped),
        "mode": "standalone" if standalone else "extended",
        "target": (
            target_readiness["target"]
            if target_readiness["active"]
            else {"host": target_host, "port": target_port, "remote_client": settings.remote_client}
        ),
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run qa-mcp end-to-end diagnostics.")
    parser.add_argument("--host", default=None, help="TestClient host override.")
    parser.add_argument("--port", type=int, default=None, help="TestClient TPort override.")
    parser.add_argument(
        "--timeout-sec",
        type=float,
        default=None,
        help="Per-link timeout override; defaults to QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS or 3 seconds.",
    )
    parser.add_argument("--require-bearer", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--com-infobase-path", default="", help="Optional COM doctor file infobase path.")
    parser.add_argument("--com-user", default="", help="Optional COM doctor user.")
    parser.add_argument("--com-password", default="", help="Optional COM doctor password; never echoed.")
    parser.add_argument("--com-query", default="", help="Optional read-only COM doctor smoke query.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    result = run_doctor(
        host=args.host,
        port=args.port,
        require_bearer_token=args.require_bearer,
        com_infobase_path=args.com_infobase_path,
        com_user=args.com_user,
        com_password=args.com_password,
        com_query=args.com_query,
        timeout_sec=args.timeout_sec,
        standalone=True,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
