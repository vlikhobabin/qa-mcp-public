"""Native qa-mcp MCP server (card 74 Phase 5).

Exposes the native scenario runner over MCP — `transpile`, `run_scenario`, `run_step` — so 1C test
scenarios run through the in-repo Python TestManager (synthesized capture-free bootstrap) with NO
Vanessa Automation manager in the loop. This is the MCP surface that replaces vanessa-mcp's
run/step tools. Launch: `python -m qa_mcp.mcp_server` (stdio).
"""

from __future__ import annotations

import asyncio
import functools
import hashlib
import hmac
import inspect
import json
import os
import re
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping, get_type_hints

from fastmcp import FastMCP

from .config import Settings, active_application_settings, env_flag
from .core.boundary import _current_evidence_scope
from .core import (
    ApplicationContext,
    ArtifactReference,
    LocalQAExecutor,
    NATIVE_SESSION_OPERATION_NAMES,
    OperationKind,
    OperationRequest,
    OperationResult,
    OperationVerdict,
    QAExecutor,
    RuntimeTargetBindingError,
    RuntimeTargetResolution,
    SessionIdentity,
    TargetIdentity,
    WindowsHostQAExecutor,
    bind_application_context,
    blocked_bound_route,
    current_application_context,
    execute_mcp_operation,
    is_explicitly_unbound_context,
    resolve_runtime_target,
    set_default_application_context,
    validate_runtime_target_resolution,
)
from .doctor import run_doctor as run_qa_mcp_doctor
from .protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir
from .protocol import foreground as protocol_foreground
from .protocol import introspection as protocol_introspection
from .protocol import lifecycle as client_lifecycle
from .protocol import display_backend as client_display
from .protocol import transport as client_transport
from .protocol import screenshot as client_screenshot
from .protocol import windows as window_list
from .protocol.bootstrap_synth import synthesize_bootstrap
from .protocol.handshake import (
    is_manager_handshake_drift_error,
    manager_handshake_drift_diagnostic,
)
from .protocol.native_write import (
    NativeWriteSession,
    ProtocolSendTimeout,
    WriteRetargetError,
    activate_window as native_activate_window,
    answer_dialog as native_answer_dialog,
    choose_from_list as native_choose_from_list,
    click_command as native_click_command,
    close_window as native_close_window,
    derive_activate_window,
    derive_answer_dialog,
    derive_close_window,
    derive_open_card,
    derive_advanced_search,
    derive_read_spreadsheet_cell,
    derive_read_user_messages,
    derive_search_list,
    derive_set_reference_field,
    advanced_search as native_advanced_search,
    open_card as native_open_card,
    read_spreadsheet_cell as native_read_spreadsheet_cell,
    search_list as native_search_list,
    set_list_view as native_set_list_view,
    read_user_messages as native_read_user_messages,
    set_reference_field as native_set_reference_field,
    derive_checkbox_toggle,
    derive_choice_set,
    derive_choose_from_list,
    derive_command_click,
    derive_table_command,
    derive_open_list,
    derive_page_switch,
    derive_table_cell_write,
    derive_write_template,
    open_list as native_open_list,
    select_table_row as native_select_table_row,
    set_choice as native_set_choice,
    set_table_cell as native_set_table_cell,
    switch_page as native_switch_page,
    toggle_checkbox as native_toggle_checkbox,
)
from .protocol.native_xtest import send_keys as native_send_keys
from .protocol.native_xtest import write_form_value_xtest as native_write_form_value_xtest
from .protocol.session import timestamp_name
from .telemetry_bridge import emit_bridge_observation as _emit_qa_bridge_observation
from .versioning import platform_version_from_root
from .scenario import (
    Scenario,
    ScenarioResult,
    ScenarioRunner,
    StepResult,
    normalize_form_date as _normalize_form_date,
    run_write_scenario,
    search_steps,
    transpile_feature,
)

mcp = FastMCP("qa-native-manager")

# The compatibility server above retains the complete historical surface.
# New applications are composed from this explicit catalog and named profiles.
_TOOL_CATALOG: dict[str, Callable[..., Any]] = {}
_RESEARCH_ONLY_TOOL_NAMES = frozenset({
    "autofill_required_fields",
    "echo_jsonrpc_arguments",
    "generate_smoke_suite",
    "measure_scenario",
})


def qa_tool() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register a compatibility tool and retain its public factory callable."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if fn.__name__ in _TOOL_CATALOG:
            raise ValueError(f"duplicate qa-mcp tool registration: {fn.__name__}")
        _TOOL_CATALOG[fn.__name__] = fn
        return mcp.tool()(fn)

    return decorator

# Frame templates the engine renders. Defaults are resolved by Settings from the active bundled platform family.
# Override with QA_MCP_MANAGER_TEMPLATES / QA_MCP_VALUE_READ_TEMPLATES to point at a custom capture.
_SETTINGS = Settings.from_env()
_DEFAULT_APPLICATION_CONTEXT = ApplicationContext(
    settings=_SETTINGS,
    executor=LocalQAExecutor(),
)
set_default_application_context(_DEFAULT_APPLICATION_CONTEXT)
DEFAULT_TEMPLATES = _SETTINGS.manager_templates
# Card 79 value-read templates (open 11-17 + value-read frames 218-221) — needed to read a field's LIVE value
# (assert_form_value / wait_for_form_value). DEFAULT_TEMPLATES (frames 8-106) lacks the 218-221 value-read frames.
VALUE_READ_TEMPLATES = _SETTINGS.value_read_templates

# --- Model B — thin cross-machine remote-client mode (card 119) --------------------------------------------
# When qa-mcp runs in the THIN container and the TestClient runs on the USER'S host (e.g. a licensed Windows
# 1C), the agent points the PROTOCOL tools at the pre-launched client. The host/port DEFAULTS come from the env
# so the agent can omit them: the thin image sets QA_MCP_CLIENT_HOST=host.docker.internal — Docker Desktop
# forwards that to the client as a LOOPBACK-ORIGIN peer, the only address a Windows-built client accepts at the
# bootstrap (a raw LAN IP to a different box is rejected — card 119 finding). REMOTE_CLIENT additionally turns
# the LOCAL-only tools — X11/display (XTEST writes, screenshots, OS window list) and the local-boot lifecycle —
# into a clear "not served here" result instead of an opaque X11/xdotool crash, because the Windows render is
# GDI and lives on the host, not in this container's X server. The display subset is recovered by the host-side
# input/screenshot agent (card 119 agenda #2). Model A (no env) keeps 127.0.0.1 / local boot — unchanged.
DEFAULT_CLIENT_HOST = _SETTINGS.client_host
DEFAULT_CLIENT_PORT = _SETTINGS.client_port
REMOTE_CLIENT = _SETTINGS.remote_client


def _remote_client_enabled() -> bool:
    """Use explicit per-app settings while preserving legacy direct-call tests."""

    application = current_application_context()
    if application is _DEFAULT_APPLICATION_CONTEXT:
        return REMOTE_CLIENT
    return application.settings.remote_client


def _runtime_client_host() -> str:
    application = current_application_context()
    return DEFAULT_CLIENT_HOST if application is _DEFAULT_APPLICATION_CONTEXT else application.settings.client_host


def _runtime_client_port() -> int:
    application = current_application_context()
    return DEFAULT_CLIENT_PORT if application is _DEFAULT_APPLICATION_CONTEXT else application.settings.client_port

def _composed_host_agent_settings() -> Settings | None:
    """Return explicit factory settings, leaving direct legacy calls env-backed."""

    application = current_application_context()
    return None if application is _DEFAULT_APPLICATION_CONTEXT else application.settings


def _display_remote_client_enabled() -> bool:
    """Match display construction: scoped Settings, or the legacy env adapter."""

    settings = _composed_host_agent_settings()
    return client_display.remote_client_enabled() if settings is None else settings.remote_client


def _remote_agent_configured() -> bool:
    settings = _composed_host_agent_settings()
    return (
        client_display.remote_agent_configured()
        if settings is None
        else client_display.remote_agent_configured(settings=settings)
    )


def _remote_agent_backend() -> client_display.RemoteAgentBackend:
    settings = _composed_host_agent_settings()
    return (
        client_display.RemoteAgentBackend.from_env()
        if settings is None
        else client_display.RemoteAgentBackend.from_settings(settings)
    )


def _host_agent_install_command() -> str:
    settings = _composed_host_agent_settings()
    return (
        client_display.host_agent_install_command()
        if settings is None
        else client_display.host_agent_install_command(settings=settings)
    )


# Card 125 Change 5 — dynamic-list read currency. A 1C dynamic list is async / eventually-consistent: a
# just-created record is NOT in the list's query result until the query re-runs (the interactive fix is F5 / the
# «Обновить» command). Dynlist reads therefore force a refresh and poll-until-stable so a reported 0-row result
# only ever denotes a genuinely empty list — never a not-yet-loaded / stale dynamic list. Bounded + tunable
# (also via env) so tests drive the loop without real sleeps.
LIST_POLL_ATTEMPTS = _SETTINGS.list_poll_attempts
LIST_POLL_SETTLE_SEC = _SETTINGS.list_poll_settle_sec


@dataclass(frozen=True)
class _AttachedTestClientContext:
    host: str
    port: int
    attached_at: float
    status: Mapping[str, Any]
    target: TargetIdentity | None = None
    session: SessionIdentity | None = None
    binding_generation: int = 0
    ownership_class: str = "unbound"
    lifecycle_id: str = ""
    display: str | None = None
    cleanup: Mapping[str, Any] | None = None

    def as_dict(self, *, listening: bool | None = None) -> dict[str, Any]:
        payload = {
            "host": self.host,
            "port": self.port,
            "attached": True,
            "owns_process": bool(self.status.get("owns_process")),
            "attached_at": self.attached_at,
        }
        for key in ("pid", "lifecycle_owner", "lifecycle_id", "lifecycle_handle", "client_target"):
            if key in self.status:
                payload[key] = self.status[key]
        if listening is not None:
            payload["listening"] = listening
        return payload


def _extract_status_endpoint(status: dict[str, Any]) -> tuple[str, int]:
    connection = status.get("connection") if isinstance(status.get("connection"), dict) else {}
    host = status.get("host") or connection.get("host") or _runtime_client_host()
    port = status.get("port") or connection.get("port") or _runtime_client_port()
    return str(host), int(port)


def _remember_attached_testclient(status: dict[str, Any]) -> dict[str, Any]:
    host, port = _extract_status_endpoint(status)
    ctx = _AttachedTestClientContext(host=host, port=port, attached_at=time.time(), status=dict(status))
    current_application_context().attachment = ctx
    enriched = dict(status)
    enriched["active_attachment"] = ctx.as_dict(listening=status.get("listening"))
    return enriched


def _bound_lifecycle_result(
    name: str, *, value: dict[str, Any] | None = None, code: str = "", message: str = ""
) -> dict[str, Any]:
    request = OperationRequest(OperationKind.LIFECYCLE, name)
    result = (
        OperationResult.success(request, value=value)
        if not code else OperationResult.blocked(request, code=code, message=message)
    )
    payload = result.to_dict()
    if value is not None:
        payload.pop("value", None)
        payload.update(value)
    return payload


def _bound_lifecycle_block(name: str, code: str) -> dict[str, Any]:
    messages = {
        "runtime-target-override-forbidden": "caller target overrides are forbidden",
        "runtime-target-unavailable": "the declared provider target is unavailable",
        "runtime-target-observation-missing": "the required target observation is missing",
        "runtime-target-mismatch": "the observed lifecycle identity does not match the declared target",
        "runtime-target-session-required": "a target-bound TestClient session is required",
        "runtime-target-cleanup-not-owned": "cleanup identity is stale or foreign",
    }
    return _bound_lifecycle_result(name, code=code, message=messages.get(code, "lifecycle admission blocked"))


def _provider_testclient_target() -> client_lifecycle.TestClientTarget:
    application = current_application_context()
    resolution = validate_runtime_target_resolution(application.runtime_target)
    config = resolution._physical_config
    platform_root = config.platform_root
    if not platform_root:
        raise ValueError("platform")
    kind = config.test_client_kind.lower()
    kind = "thin" if kind.startswith("thin") else "thick"
    infobase = config.infobase_path or None
    connection = config.connection_string or None
    if resolution.binding.target_kind == "file" and not infobase:
        raise ValueError("infobase")
    if resolution.binding.target_kind == "client-server" and not connection:
        raise ValueError("connection")
    target = client_lifecycle.TestClientTarget(
        infobase_path=infobase if resolution.binding.target_kind == "file" else None,
        connection_string=connection if resolution.binding.target_kind == "client-server" else None,
        platform_root=platform_root,
        kind=kind,
        user=config.test_client_user,
        password=config.test_client_password,
        host=application.settings.client_host,
        port=application.settings.host_agent_client_port or application.settings.client_port,
    )
    if not application.settings.remote_client:
        if resolution.binding.target_kind == "file" and not Path(infobase or "").is_dir():
            raise ValueError("infobase")
        if not Path(target.resolved_client_bin()).is_file():
            raise ValueError("platform")
    return target


def _bound_public_identity(attachment: _AttachedTestClientContext) -> dict[str, Any]:
    return {
        "target": _bound_logical_target_identity(),
        "session": {
            "session_id": attachment.session.session_id if attachment.session else "",
            "sequence": attachment.session.sequence if attachment.session else 0,
        },
        "ownership_class": attachment.ownership_class,
        "lifecycle_id": attachment.lifecycle_id,
        "attached": True,
    }


def _bound_logical_target_identity() -> dict[str, Any]:
    """Return the public, provider-neutral projection for bound diagnostics."""

    binding = validate_runtime_target_resolution(
        current_application_context().runtime_target
    ).binding
    return {
        "logical_id": binding.target.logical_id,
        "kind": binding.declared_target_kind,
        "fingerprint": binding.target.fingerprint,
        "binding_ref": binding.binding_ref,
        "binding_generation": binding.binding_generation,
    }


def _remember_bound_testclient(
    status: Mapping[str, Any], *, operation: str, ownership_class: str, lifecycle_id: str
) -> dict[str, Any]:
    application = current_application_context()
    resolution = validate_runtime_target_resolution(application.runtime_target)
    host = str(status["host"])
    port = int(status["port"])
    session = SessionIdentity(
        session_id=str(uuid.uuid4()),
        target=resolution.binding.target,
        sequence=resolution.binding.binding_generation,
    )
    sanitized_values = {
        key: status[key] for key in ("pid", "alive", "listening", "owns_process") if key in status
    }
    if type(status.get("client_target")) is dict:
        sanitized_values["client_target"] = dict(status["client_target"])
    sanitized = MappingProxyType(sanitized_values)
    raw_handle = status.get("lifecycle_handle")
    handle = MappingProxyType(dict(raw_handle)) if type(raw_handle) is dict else None
    cleanup = MappingProxyType({
        "pid": status.get("pid"),
        "xvfb_pid": status.get("xvfb_pid"),
        "manage_apache": status.get("apache_stopped") is True,
        "lifecycle_id": lifecycle_id,
        "lifecycle_handle": handle,
        "port": status.get("native_port", status.get("port")),
    })
    attachment = _AttachedTestClientContext(
        host=host, port=port, attached_at=time.time(), status=sanitized,
        target=resolution.binding.target, session=session,
        binding_generation=resolution.binding.binding_generation,
        ownership_class=ownership_class, lifecycle_id=lifecycle_id,
        display=(
            status.get("display") if type(status.get("display")) is str
            else ("" if application.settings.remote_client else None)
        ),
        cleanup=cleanup,
    )
    application.session = session
    application.attachment = attachment
    return _bound_lifecycle_result(operation, value=_bound_public_identity(attachment))


def _strict_owned_remote_identity(payload: Mapping[str, Any], declared_port: int) -> tuple[int, int, str] | None:
    client = payload.get("client_target")
    handle = payload.get("lifecycle_handle")
    if type(client) is not dict or type(handle) is not dict:
        return None
    top = (payload.get("pid"), payload.get("port"), payload.get("lifecycle_id"))
    client_values = (client.get("pid"), client.get("port"), client.get("lifecycle_id"))
    handle_values = (handle.get("pid"), handle.get("port"), handle.get("id"))
    pid, port, lifecycle_id = top
    projections = (top, client_values, handle_values)
    exactly_typed = all(
        type(raw_pid) is int and raw_pid > 0
        and type(raw_port) is int and 0 < raw_port <= 65535
        and type(raw_id) is str and bool(raw_id) and raw_id == raw_id.strip()
        for raw_pid, raw_port, raw_id in projections
    )
    if (
        not exactly_typed or port != declared_port
        or top != client_values or top != handle_values
        or payload.get("owns_process") is not True or payload.get("reused_existing") is True
    ):
        return None
    return pid, port, lifecycle_id


def _clear_attached_testclient_context() -> None:
    """Test helper and explicit reset hook for process-lifetime attach state."""
    current_application_context().attachment = None


def _clear_bound_testclient_context() -> None:
    application = current_application_context()
    application.attachment = None
    application.session = None


def _active_attached_testclient_status() -> dict[str, Any] | None:
    attachment = current_application_context().attachment
    if not isinstance(attachment, _AttachedTestClientContext):
        return None
    ctx = attachment
    return ctx.as_dict(listening=_attached_endpoint_is_listening(ctx))


def _display_backend() -> client_display.LocalXTestBackend | client_display.RemoteAgentBackend:
    application = current_application_context()
    backend = (
        client_display.get_display_backend()
        if application is _DEFAULT_APPLICATION_CONTEXT
        else client_display.get_display_backend(settings=application.settings)
    )
    attachment = application.attachment
    if isinstance(backend, client_display.RemoteAgentBackend) and isinstance(
        attachment, _AttachedTestClientContext
    ):
        target = attachment.status.get("client_target")
        backend.client_target_required = True
        backend.client_target = dict(target) if isinstance(target, dict) else None
    return backend


def _attached_endpoint_is_listening(ctx: _AttachedTestClientContext) -> bool:
    """Verify a remembered endpoint without consuming a relay target session."""

    relay = client_transport.relay_configuration()
    host_agent = ctx.status.get("host_agent")
    if (
        _remote_client_enabled()
        and relay is not None
        and (ctx.host, ctx.port) == relay[0]
        and isinstance(host_agent, dict)
        and host_agent.get("ok") is True
        and host_agent.get("alive") is True
        and host_agent.get("listening") is True
    ):
        return client_transport.relay_listener_reachable((ctx.host, ctx.port), timeout=0.5)
    return client_lifecycle.port_is_listening(ctx.host, ctx.port)


def _resolve_testclient_endpoint(
    host: str,
    port: int,
    *,
    phase: str,
) -> tuple[str, int, dict[str, Any] | None]:
    """Resolve MCP default host/port through the current attached endpoint, if any.

    Non-default host/port values remain explicit overrides. The existing public signatures keep their historical
    defaults, so a caller that omits host/port automatically uses the active attached endpoint after attach.
    """
    application = current_application_context()
    ctx = application.attachment
    default_endpoints = {
        (DEFAULT_CLIENT_HOST, DEFAULT_CLIENT_PORT),
        (application.settings.client_host, application.settings.client_port),
    }
    if not isinstance(ctx, _AttachedTestClientContext) or (host, int(port)) not in default_endpoints:
        return host, int(port), None
    if not _attached_endpoint_is_listening(ctx):
        raise ConnectionError(f"attached TestClient endpoint {ctx.host}:{ctx.port} is not listening during {phase}")
    return ctx.host, ctx.port, ctx.as_dict(listening=True)


def _attach_tool_error(tool: str, phase: str, exc: Exception, *, host: str, port: int) -> dict[str, Any]:
    detail = str(exc)
    stale = "attached TestClient endpoint" in detail and "not listening" in detail
    action_hint = (
        "Restart the qa-mcp-testclient scheduled task or run attach_test_client after the TestClient is listening."
        if stale else
        "Run attach_test_client after starting a listening TestClient endpoint, or pass explicit host/port."
    )
    return {
        "ok": False,
        "error": "stale-attached-testclient" if stale else "attached-testclient-unavailable",
        "tool": tool,
        "phase": phase,
        "host": host,
        "port": int(port),
        "detail": detail,
        "action_hint": action_hint,
        "attached_endpoint": _active_attached_testclient_status(),
    }


def _is_missing_current_form_guid_error(exc: Exception) -> bool:
    detail = str(exc)
    return (
        "managed_form_guid_ascii template field requires a live ManagedForm GUID" in detail
        or "managed_form_guid_utf16le template field requires a live ManagedForm GUID" in detail
    )


def _open_link_required_error(tool: str, phase: str, *, host: str, port: int) -> dict[str, Any]:
    return {
        "ok": False,
        "error": "open-link-required",
        "tool": tool,
        "phase": phase,
        "host": host,
        "port": int(port),
        "detail": "cannot infer current ManagedForm GUID; pass open_link",
        "action_hint": "Pass open_link such as e1cib/list/<metadata> or e1cib/data/<metadata>?ref=<ref>.",
    }


def _structured_tool_error(
    tool: str,
    phase: str,
    exc: Exception,
    *,
    error: str,
    host: str | None = None,
    port: int | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "ok": False,
        "error": error,
        "tool": tool,
        "phase": phase,
        "detail": str(exc),
    }
    if host is not None:
        result["host"] = host
    if port is not None:
        result["port"] = int(port)
    attached = _active_attached_testclient_status()
    if attached is not None:
        result["attached_endpoint"] = attached
    return result


def _execute_composed_operation(
    kind: OperationKind,
    name: str,
    arguments: Mapping[str, Any],
    local_call: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    """Route composed applications through their executor; preserve direct-call compatibility."""

    application = current_application_context()
    if application is _DEFAULT_APPLICATION_CONTEXT:
        return local_call()
    result = execute_mcp_operation(application, OperationRequest(kind, name, arguments))
    if application.runtime_target is not None and name in application.operation_schemas:
        return result.to_dict()
    if result.verdict is OperationVerdict.SUCCESS and isinstance(result.value, dict):
        return result.value
    return result.to_dict()


def _remote_local_boot_result(tool: str) -> dict[str, Any]:
    return {
        "ok": False,
        "error": "local-boot-disabled-remote-client",
        "mode": "remote-client",
        "tool": tool,
        "detail": (
            "model-B remote-client mode does not boot a local TestClient — the client runs "
            "on your host (e.g. Windows `1cv8 ENTERPRISE /TESTCLIENT -TPort <p>`). Point "
            "the protocol tools at it with host=$QA_MCP_CLIENT_HOST (default "
            "host.docker.internal) and port=<your TPort>."
        ),
    }


def _redact_connection_string(value: str, password: str = "") -> str:
    redacted = value
    if password:
        redacted = redacted.replace(password, "<redacted-password>")
    redacted = re.sub(r"(?i)(password|pwd)=([^;\s]+)", r"\1=<redacted-password>", redacted)
    return redacted


def _remote_testclient_host_command(target: client_lifecycle.TestClientTarget) -> str:
    args = [
        target.resolved_client_bin(),
        "ENTERPRISE",
        "/IBConnectionString",
        _redact_connection_string(target.connection_string_value(), target.password),
    ]
    if target.user:
        args.append(f"/N{target.user}")
    if target.password:
        args.append("/P<redacted-password>")
    args += ["/TESTCLIENT", "-TPort", str(target.port), "/DisableStartupDialogs", "/DisableStartupMessages"]
    return subprocess.list2cmdline(args)


def _wait_for_remote_testclient(host: str, port: int, wait_sec: float) -> bool:
    relay = client_transport.relay_configuration()

    def listening() -> bool:
        if relay is not None and (host, port) == relay[0]:
            return client_transport.relay_listener_reachable((host, port), timeout=0.5)
        return client_lifecycle.port_is_listening(host, port)

    deadline = time.monotonic() + max(0.0, wait_sec)
    while time.monotonic() < deadline:
        if listening():
            return True
        time.sleep(0.5)
    return listening()


def _remote_protocol_endpoint(target: client_lifecycle.TestClientTarget) -> tuple[str, int]:
    relay = client_transport.relay_configuration()
    return relay[0] if relay is not None else (target.host, target.port)


def _remote_testclient_launch_failure(
    *,
    target: client_lifecycle.TestClientTarget,
    tool: str,
    error: str,
    detail: str,
    host_agent_result: dict[str, Any] | None = None,
    install_command: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "ok": False,
        "error": error,
        "mode": "remote-client",
        "tool": tool,
        "detail": detail,
        "host": target.host,
        "port": target.port,
        "connection": target.redacted_summary(),
        "host_command": _remote_testclient_host_command(target),
    }
    if install_command:
        result["install_command"] = install_command
    if host_agent_result is not None:
        result.update(_remote_launch_cleanup_fields(host_agent_result, target=target))
    return result


def _remote_launch_cleanup_fields(
    payload: dict[str, Any], *, target: client_lifecycle.TestClientTarget,
) -> dict[str, Any]:
    """Retain a validated cleanup identity, never an arbitrary error body."""
    handle = payload.get("lifecycle_handle")
    if handle is not None and not isinstance(handle, dict):
        return {}
    handle = handle or {}
    identity = payload.get("lifecycle_id", handle.get("id"))
    pid = payload.get("pid")
    port = payload.get("port", target.port)
    settings = _composed_host_agent_settings()
    settings = Settings.from_env() if settings is None else settings
    if (
        payload.get("owns_process") is not True
        or payload.get("reused_existing") is True
        or payload.get("lifecycle_owner", "host-agent") != "host-agent"
        or type(pid) is not int or pid <= 0
        or type(port) is not int or port != target.port
        or not isinstance(identity, str)
        or re.fullmatch(r"[A-Za-z0-9_-]{1,128}", identity) is None
        or any(secret and secret in identity for secret in (settings.host_agent_token, target.password))
        or handle.get("kind", "host-agent-testclient") != "host-agent-testclient"
        or handle.get("id", identity) != identity
        or type(handle.get("pid", pid)) is not int or handle.get("pid", pid) != pid
        or type(handle.get("port", port)) is not int or handle.get("port", port) != port
    ):
        return {}
    return {
        "pid": pid, "owns_process": True, "lifecycle_owner": "host-agent",
        "lifecycle_id": identity,
        "lifecycle_handle": {"kind": "host-agent-testclient", "id": identity, "pid": pid, "port": port},
    }


def _remote_host_agent_lifecycle_fields(host_agent_result: dict[str, Any], *, default_port: int) -> dict[str, Any]:
    lifecycle_id = _remote_lifecycle_id(host_agent_result.get("lifecycle_handle"))
    if not lifecycle_id:
        lifecycle_id = str(host_agent_result.get("lifecycle_id") or "").strip()
    owns_process = (
        host_agent_result.get("owns_process") is True
        and host_agent_result.get("pid") is not None
        and host_agent_result.get("reused_existing") is not True
        and bool(lifecycle_id)
    )
    if not owns_process:
        return {"owns_process": False}
    fields: dict[str, Any] = {
        "owns_process": True,
        "lifecycle_owner": str(host_agent_result.get("lifecycle_owner") or "host-agent"),
        "lifecycle_id": lifecycle_id,
    }
    handle = host_agent_result.get("lifecycle_handle")
    if isinstance(handle, dict):
        normalized_handle = dict(handle)
        normalized_handle.setdefault("kind", "host-agent-testclient")
        normalized_handle.setdefault("id", lifecycle_id)
        normalized_handle.setdefault("pid", host_agent_result.get("pid"))
        normalized_handle.setdefault("port", int(host_agent_result.get("port") or default_port))
        fields["lifecycle_handle"] = normalized_handle
    else:
        fields["lifecycle_handle"] = {
            "kind": "host-agent-testclient",
            "id": lifecycle_id,
            "pid": host_agent_result.get("pid"),
            "port": int(host_agent_result.get("port") or default_port),
        }
    return fields


def _remote_lifecycle_id(lifecycle_handle: Any) -> str:
    if not isinstance(lifecycle_handle, dict):
        return ""
    return str(lifecycle_handle.get("id") or "").strip()


def _remote_client_target(payload: dict[str, Any], *, default_port: int) -> dict[str, Any] | None:
    supplied = payload.get("client_target")
    if isinstance(supplied, dict):
        pid = supplied.get("pid")
        port = supplied.get("port") or default_port
        if isinstance(pid, int) and pid > 0 and isinstance(port, int) and port > 0:
            target = {
                "kind": str(supplied.get("kind") or "host-agent-testclient"),
                "pid": pid,
                "port": port,
            }
            lifecycle_id = str(supplied.get("lifecycle_id") or supplied.get("id") or "").strip()
            if lifecycle_id:
                target["lifecycle_id"] = lifecycle_id
            return target

    pid = payload.get("pid")
    if not isinstance(pid, int) or pid <= 0:
        return None
    port = payload.get("port") or default_port
    if not isinstance(port, int) or port <= 0:
        return None
    target = {"kind": "host-agent-testclient", "pid": pid, "port": port}
    lifecycle_id = _remote_lifecycle_id(payload.get("lifecycle_handle")) or str(
        payload.get("lifecycle_id") or ""
    ).strip()
    if lifecycle_id:
        target["lifecycle_id"] = lifecycle_id
    return target


def _host_agent_owned_readiness_is_authoritative(host_agent_result: dict[str, Any], *, default_port: int) -> bool:
    """Whether host-side readiness should replace a thin-side TCP probe.

    A local TCP probe through SSH or another direct port forward can consume the
    Windows TestClient's single manager socket before the protocol tool gets to
    use it. The host-agent's launch check is host-side and lifecycle-bound, so a
    ready owned launch is sufficient without opening the forwarded socket.
    """

    return (
        host_agent_result.get("listening") is True
        and host_agent_result.get("alive") is not False
        and _remote_host_agent_lifecycle_fields(
            host_agent_result, default_port=default_port
        )["owns_process"] is True
    )


def _descriptor_result_is_empty(result: dict[str, Any]) -> bool:
    return (
        result.get("opened") is None
        and not result.get("fields")
        and not result.get("elements")
        and int(result.get("field_count") or 0) == 0
        and int(result.get("element_count") or 0) == 0
    )


def _resolved_annotations(fn):
    """Resolve postponed annotations before FastMCP inspects a tool function."""

    fn.__annotations__ = get_type_hints(fn, include_extras=True)
    return fn


def _local_only_tool(*, alt: str | None = None, local_boot: bool = False):
    """Mark an MCP tool as LOCAL-display/local-boot only — in REMOTE_CLIENT mode it returns a structured
    "not served here" result (pointing at the protocol alternative / the host agent) instead of running.

    Wraps with functools.wraps so FastMCP still introspects the real signature for the tool schema. Applied
    UNDER @mcp.tool() so the registered tool is the guarded wrapper:  @mcp.tool() / @_local_only_tool(...) / def.
    """
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
            if _remote_client_enabled():
                if local_boot:
                    return _remote_local_boot_result(fn.__name__)
                application = current_application_context()
                settings = application.settings
                configured = (
                    client_display.remote_agent_configured()
                    if application is _DEFAULT_APPLICATION_CONTEXT
                    else client_display.remote_agent_configured(settings=settings)
                )
                if configured:
                    return fn(*args, **kwargs)
                return client_display.unavailable_remote_result(
                    fn.__name__,
                    alt=alt,
                    settings=None if application is _DEFAULT_APPLICATION_CONTEXT else settings,
                )
            return fn(*args, **kwargs)
        # Normalize now while preserving the public wrapped signature so
        # FastMCP sees concrete types on the closure.
        wrapper.__annotations__ = get_type_hints(fn, include_extras=True)
        return wrapper
    return deco


def testclient_tool(
    *,
    phase: str,
    local_boot: bool = False,
    before_endpoint: Callable[
        [dict[str, Any]],
        dict[str, Any] | Callable[[str, int], dict[str, Any]] | None,
    ] | None = None,
):
    """Resolve attach-aware endpoint defaults and return structured wrapper errors for protocol tools."""

    def deco(fn):
        signature = inspect.signature(fn)

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
            if _remote_client_enabled() and local_boot:
                return _remote_local_boot_result(fn.__name__)
            try:
                bound = signature.bind_partial(*args, **kwargs)
                bound.apply_defaults()
                host = str(bound.arguments.get("host", DEFAULT_CLIENT_HOST))
                port = int(bound.arguments.get("port", DEFAULT_CLIENT_PORT))
            except (TypeError, ValueError) as exc:
                return _structured_tool_error(fn.__name__, phase, exc, error="invalid-arguments")
            prepared_call: Callable[[str, int], dict[str, Any]] | None = None
            if before_endpoint is not None:
                prepared = before_endpoint(dict(bound.arguments))
                if isinstance(prepared, dict):
                    return prepared
                prepared_call = prepared
            try:
                host, port, attachment = _resolve_testclient_endpoint(host, port, phase=phase)
            except ConnectionError as exc:
                return _attach_tool_error(fn.__name__, "attach", exc, host=host, port=port)
            bound.arguments["host"] = host
            bound.arguments["port"] = port
            try:
                result = prepared_call(host, port) if prepared_call is not None else fn(**bound.arguments)
            except (WriteRetargetError, ProtocolSendTimeout):
                raise
            except FileNotFoundError as exc:
                return _structured_tool_error(
                    fn.__name__, phase, exc, error="capture-not-found", host=host, port=port
                )
            except ValueError as exc:
                if _is_missing_current_form_guid_error(exc) and not bound.arguments.get("open_link"):
                    return _open_link_required_error(fn.__name__, phase, host=host, port=port)
                if is_manager_handshake_drift_error(exc):
                    return {
                        "tool": fn.__name__,
                        "phase": phase,
                        "host": host,
                        "port": port,
                        **manager_handshake_drift_diagnostic(exc),
                    }
                return _structured_tool_error(
                    fn.__name__, phase, exc, error="invalid-arguments", host=host, port=port
                )
            except TypeError as exc:
                return _structured_tool_error(
                    fn.__name__, phase, exc, error="invalid-arguments", host=host, port=port
                )
            if attachment is not None and isinstance(result, dict):
                result = dict(result)
                if fn.__name__ == "read_form_descriptor" and _descriptor_result_is_empty(result):
                    result.update({
                        "ok": False,
                        "error": "attached-descriptor-empty",
                        "phase": "descriptor",
                        "diagnostic": (
                            "attached endpoint was reachable and the descriptor call returned no opened form, "
                            "fields or elements"
                        ),
                    })
                if result.get("attached_endpoint") is None:
                    result["attached_endpoint"] = attachment
            return result

        # See _local_only_tool: keep FastMCP from reconstructing a compiled
        # decorator closure after resolving postponed annotations.
        wrapper.__annotations__ = get_type_hints(fn, include_extras=True)
        wrapper._qa_mcp_testclient_tool = True
        return wrapper

    return deco


def _display_backend_error(tool: str, exc: client_display.DisplayBackendError) -> dict[str, Any]:
    return _display_backend_error_result(tool, exc)


def scenario_from_input(scenario_json: str | dict | None, feature_text: str | None) -> tuple[Scenario, list[str]]:
    """Build a Scenario from either a .feature (Gherkin) text or a scenario JSON (pure/testable)."""
    if feature_text:
        results = transpile_feature(feature_text)
        if not results:
            raise ValueError("no scenarios found in feature_text")
        return results[0].scenario, results[0].unmapped
    if scenario_json is not None:
        data = json.loads(scenario_json) if isinstance(scenario_json, str) else scenario_json
        return Scenario.from_dict(data), []
    raise ValueError("provide either feature_text or scenario_json")


_SAVE_COMMANDS = frozenset({"записать", "save", "write", "ctrl+s", "записать и закрыть"})


def _normalize_table_date_parts(value: str) -> tuple[str, int, int, int]:
    """Validate a table date-cell value and return normalized text plus day/month/year parts."""
    normalized = _normalize_form_date(value)
    d, m, y = (int(part) for part in normalized.split("."))
    return normalized, d, m, y


def _looks_like_form_date(value: str) -> bool:
    try:
        _normalize_form_date(value)
    except ValueError:
        return False
    return True


def _open_link_visible_label(open_link: str, field: str, field_mode: str) -> str:
    # Card 125: the owner/reference label is resolved from the live form, so
    # the requested on-screen field name is used directly.
    return field


_LABEL_LOCATE_RETRY_FOREGROUND_METHODS = {"create_listreplay", "listreplay"}


def _should_retry_label_locate(foreground_method: str | None, attempt: int, located: object | None) -> bool:
    return located is None and attempt == 0 and foreground_method in _LABEL_LOCATE_RETRY_FOREGROUND_METHODS


def _json_object_option(value: Any, *, option: str) -> tuple[dict[str, Any] | None, str | None]:
    if value is None:
        return None, None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None, None
        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            return None, f"{option} is not valid JSON: {exc.msg}"
    if not isinstance(value, dict):
        return None, f"{option} must be a JSON object"
    return value, None


_MOJIBAKE_QMARK_RE = re.compile(r"\?{4,}")


def _jsonrpc_value_warnings(value: Any, *, path: str) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    if isinstance(value, str):
        if "\ufffd" in value:
            warnings.append({
                "path": path,
                "code": "unicode-replacement-character",
                "detail": "value contains U+FFFD replacement characters; request text may have been decoded incorrectly",
                "value": value,
            })
        if _MOJIBAKE_QMARK_RE.search(value):
            warnings.append({
                "path": path,
                "code": "question-mark-mojibake",
                "detail": "value contains a long run of question marks; Cyrillic text may have been replaced before qa-mcp received it",
                "value": value,
            })
        return warnings
    if isinstance(value, dict):
        for key, item in value.items():
            warnings.extend(_jsonrpc_value_warnings(item, path=f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            warnings.extend(_jsonrpc_value_warnings(item, path=f"{path}[{index}]"))
    return warnings


def _evidence_ok(evidence: dict[str, Any]) -> bool:
    if "ok" in evidence:
        return bool(evidence.get("ok"))
    status = str(evidence.get("status") or "").strip().lower()
    return status in {"ok", "passed", "verified", "provided", "cleaned", "restored"}


def _contract_assertion_summaries(assertions: list[Any]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    field_aliases = {
        "description": "Наименование",
        "наименование": "Наименование",
        "main": "Основной",
        "основной": "Основной",
    }
    for index, raw in enumerate(assertions, start=1):
        if not isinstance(raw, dict):
            continue
        field = str(raw.get("field") or raw.get("field_ru") or "").strip()
        normalized_field = field_aliases.get(field.lower())
        if normalized_field is None:
            continue
        label = str(raw.get("contract") or raw.get("label") or raw.get("name") or "").strip()
        key = label or f"contract-{index}"
        lower_key = key.lower().replace("_", "-")
        if lower_key in {"first", "first-contract", "contract-1"}:
            key = "first-contract"
        elif lower_key in {"second", "second-contract", "contract-2"}:
            key = "second-contract"
        summary = grouped.setdefault(key, {"contract": key, "assertions": {}})
        summary["assertions"][normalized_field] = {
            "expected": raw.get("expected"),
            "actual": raw.get("actual"),
            "ok": bool(raw.get("ok")),
        }
    return list(grouped.values())


def _build_persistence_verification(
    *,
    save_requested: bool,
    saved: bool,
    evidence: dict[str, Any] | None,
    evidence_error: str | None,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "requested": bool(save_requested),
        "save_sent": bool(saved),
    }
    if not save_requested:
        return {**base, "status": "not_requested", "ok": True}
    if not saved:
        return {
            **base,
            "status": "not_saved",
            "ok": False,
            "reason": "save was requested but Ctrl+S was not sent or accepted",
        }
    if evidence_error:
        return {**base, "status": "verification_error", "ok": False, "reason": evidence_error}
    if evidence is None:
        return {
            **base,
            "status": "provider_gap",
            "ok": False,
            "reason": "saved open-link create requires retained read-back, list-read or data assertion evidence",
            "expected_evidence": "data_assertion",
        }
    assertions = evidence.get("assertions") if isinstance(evidence.get("assertions"), list) else []
    ok = _evidence_ok(evidence) and all(
        bool(item.get("ok")) for item in assertions if isinstance(item, dict) and "ok" in item
    )
    status = str(evidence.get("status") or ("verified" if ok else "assertion_failed"))
    summary = {
        **base,
        "status": status,
        "ok": ok,
        "route": evidence.get("route") or evidence.get("provider"),
        "artifact_path": evidence.get("artifact_path"),
        "identifying_fields": evidence.get("identifying_fields"),
        "created_records": evidence.get("created_records") or evidence.get("records"),
        "assertions": assertions,
        "contract_assertions": _contract_assertion_summaries(assertions),
    }
    if not ok and evidence.get("reason"):
        summary["reason"] = evidence.get("reason")
    return summary


def _build_cleanup_verification(
    *,
    required: bool,
    evidence: dict[str, Any] | None,
    evidence_error: str | None,
) -> dict[str, Any]:
    base = {"required": bool(required)}
    if evidence_error:
        return {**base, "status": "verification_error", "ok": False, "reason": evidence_error}
    if evidence is None:
        if required:
            return {
                **base,
                "status": "missing",
                "ok": False,
                "reason": "saved mutation proof requires cleanup evidence",
            }
        return {**base, "status": "not_required", "ok": True}
    unresolved = evidence.get("unresolved_leftovers") or evidence.get("leftovers") or []
    if isinstance(unresolved, int):
        unresolved_count = unresolved
    elif isinstance(unresolved, list):
        unresolved_count = len(unresolved)
    else:
        unresolved_count = 1 if unresolved else 0
    ok = _evidence_ok(evidence) and unresolved_count == 0
    status = str(evidence.get("status") or ("cleaned" if ok else "unresolved_leftovers"))
    summary = {
        **base,
        "status": status,
        "ok": ok,
        "route": evidence.get("route") or evidence.get("cleanup_route"),
        "artifact_path": evidence.get("artifact_path"),
        "created_objects": evidence.get("created_objects") or evidence.get("created_records"),
        "final_state": evidence.get("final_state"),
        "unresolved_leftovers": unresolved,
    }
    if not ok:
        summary["reason"] = evidence.get("reason") or (
            "cleanup left unresolved records" if unresolved_count else "cleanup evidence did not report ok=true"
        )
    return summary


def _write_open_link_fields_by_label(
    *,
    open_link: str,
    labels: list[str],
    values: list[str],
    host: str,
    port: int,
    display: str,
    input_offset: int,
    save: bool,
    field_modes: list[str] | None = None,
    settle_sec: float = 1.2,
) -> dict[str, Any]:
    """Shared open-link write route backed by the existing foreground label writer.

    This is intentionally a bounded bridge: the pure protocol write template remains
    fixture-backed, while the already shipped foreground writer can target arbitrary
    forms by nav-link and type into fields located by label.
    """
    if not open_link:
        return {"ok": False, "error": "missing-open-link", "reason": "open_link is required"}
    if len(labels) != len(values):
        return {
            "ok": False,
            "error": "label-value-count-mismatch",
            "labels": labels,
            "values": values,
        }
    if field_modes is not None and len(field_modes) != len(labels):
        return {
            "ok": False,
            "error": "label-mode-count-mismatch",
            "labels": labels,
            "field_modes": field_modes,
        }
    try:
        host, port, attachment = _resolve_testclient_endpoint(host, port, phase="write_open_link")
    except ConnectionError as exc:
        return _attach_tool_error("write_open_link_fields", "attach", exc, host=host, port=port)
    try:
        raw = write_form_fields_by_label(
            open_link=open_link,
            labels=labels,
            values=values,
            display=display,
            host=host,
            port=port,
            input_offset=input_offset,
            save=save,
            field_modes=field_modes,
            settle_sec=settle_sec,
        )
    except Exception as exc:  # noqa: BLE001 - tool result must fail closed, not tear down the MCP session
        raw = {
            "ok": False,
            "error": "open-link-write-failed",
            "open_link": open_link,
            "detail": f"{type(exc).__name__}: {exc}",
        }
    if attachment is not None:
        raw["attached_endpoint"] = attachment
    return raw


def _open_link_field_write_result(
    *,
    value: str,
    field: str,
    open_link: str,
    host: str,
    port: int,
    display: str,
    input_offset: int,
    save: bool,
    surface: str = "form_field",
    field_mode: str = "text",
) -> dict[str, Any]:
    raw = _write_open_link_fields_by_label(
        open_link=open_link,
        labels=[field],
        values=[value],
        host=host,
        port=port,
        display=display,
        input_offset=input_offset,
        save=save,
        field_modes=[field_mode],
    )
    targeted = bool(raw.get("foregrounded")) and bool(raw.get("all_targeted"))
    # card 125 #4 — honest committed from the protocol value-read of the open form (no more committed==targeted).
    first = (raw.get("results") or [{}])[0] if isinstance(raw.get("results"), list) else {}
    readback = raw.get("readback") or {}
    verified = bool(readback.get("verified"))
    committed = bool(first.get("committed")) if verified else False
    result = {
        "open_link": open_link,
        "opened": raw.get("foregrounded"),
        "field": field,
        "requested_value": value,
        "readback_value": first.get("readback_value"),
        "committed": committed,
        "accepted": targeted,
        "surface": surface,
        "write_mode": "open_link_label_xtest",
        "verification": "value_readback" if verified else "screen_targeted",
        "raw": raw,
    }
    if not targeted:
        result["ok"] = False
        result["error"] = raw.get("error") or "open-link-field-not-targeted"
        result["reason"] = raw.get("reason") or raw.get("detail") or "field label was not targeted on screen"
    if raw.get("attached_endpoint") is not None:
        result["attached_endpoint"] = raw["attached_endpoint"]
    return result


def _run_open_link_write_scenario(
    scenario: Scenario,
    *,
    host: str,
    port: int,
    open_link: str | None,
    display: str,
    input_offset: int,
    save: bool,
    persistence_verification_json: Any = None,
    cleanup_evidence_json: Any = None,
    require_cleanup: bool = False,
) -> dict[str, Any]:
    nav_link = open_link
    labels: list[str] = []
    values: list[str] = []
    field_modes: list[str] = []
    input_steps: list[tuple[int, Any, str, str, str, str, str]] = []
    steps: list[StepResult] = []
    raw: dict[str, Any] = {}
    save_requested = save
    unsupported: list[StepResult] = []
    persistence_evidence, persistence_error = _json_object_option(
        persistence_verification_json, option="persistence_verification_json")
    cleanup_evidence, cleanup_error = _json_object_option(cleanup_evidence_json, option="cleanup_evidence_json")

    for idx, step in enumerate(scenario.steps):
        if step.kind in {"open_create_form", "open_main_form", "open_list"}:
            step_link = (step.params.get("open_link") or "").strip() or _nav_link_for_step(step)
            nav_link = nav_link or step_link
            ok = bool(step_link or nav_link)
            steps.append(StepResult(
                name=step.name,
                kind=step.kind,
                status="ok" if ok else "error",
                preview=json.dumps({"open_link": step_link or nav_link}, ensure_ascii=False),
                assertion=ok,
                error=None if ok else f"cannot derive open_link for {step.kind}",
            ))
            continue
        if step.kind == "input_text":
            field = step.marker or ""
            value = str(step.params.get("new_value") or step.params.get("value") or "")
            requested_mode = str(step.params.get("field_mode") or step.params.get("value_type") or "").strip().lower()
            if requested_mode in {"reference", "ref", "ссылка"}:
                field_mode = "reference"
            elif requested_mode in {"choice", "enum", "перечисление"}:
                field_mode = "choice"
            else:
                field_mode = "text"
            surface = "form_field_reference" if field_mode == "reference" else (
                "form_field_choice" if field_mode == "choice" else
                "form_field_date" if step.params.get("value_type") == "date" or _looks_like_form_date(value)
                else "form_field"
            )
            if surface == "form_field_date":
                try:
                    value = _normalize_form_date(value)
                except ValueError as exc:
                    err = StepResult(name=step.name, kind=step.kind, status="error", error=str(exc))
                    steps.append(err)
                    unsupported.append(err)
                    continue
            if not field:
                err = StepResult(name=step.name, kind=step.kind, status="error", error="input_text step has no field marker")
                steps.append(err)
                unsupported.append(err)
                continue
            target_label = _open_link_visible_label(nav_link or open_link or "", field, field_mode)
            labels.append(target_label)
            values.append(value)
            field_modes.append(field_mode)
            input_steps.append((idx, step, field, target_label, value, surface, field_mode))
            continue
        if step.kind in {"click_button", "form_command"}:
            command = (step.marker or step.params.get("button") or "").strip()
            if command.lower() in _SAVE_COMMANDS:
                save_requested = True
                steps.append(StepResult(
                    name=step.name,
                    kind=step.kind,
                    status="ok",
                    preview=f"save command requested: {command or 'Ctrl+S'}",
                    assertion=True,
                ))
            else:
                err = StepResult(
                    name=step.name,
                    kind=step.kind,
                    status="error",
                    error=f"command {command!r} is not supported in open-link write mode",
                )
                steps.append(err)
                unsupported.append(err)
            continue
        if step.kind in {"assert_data", "assert_data_count"}:
            err = StepResult(
                name=step.name,
                kind=step.kind,
                status="error",
                error=f"{step.kind!r} persistence verification is not executed inside open-link write mode",
            )
            steps.append(err)
            unsupported.append(err)
            continue
        err = StepResult(
            name=step.name,
            kind=step.kind,
            status="error",
            error=f"{step.kind!r} not supported in open-link write mode",
        )
        steps.append(err)
        unsupported.append(err)

    if nav_link is None:
        err = StepResult(name="open_link", kind="open_link", status="error", error="no open_link supplied or derived")
        steps.append(err)
        unsupported.append(err)
    elif labels:
        raw = _write_open_link_fields_by_label(
            open_link=nav_link,
            labels=labels,
            values=values,
            host=host,
            port=port,
            display=display,
            input_offset=input_offset,
            save=save_requested,
            field_modes=field_modes,
        )
        raw_results = raw.get("results") if isinstance(raw.get("results"), list) else []
        for pos, (_idx, step, field, target_label, value, surface, field_mode) in enumerate(input_steps):
            item = raw_results[pos] if pos < len(raw_results) and isinstance(raw_results[pos], dict) else {}
            selected_ok = bool(item.get("selected")) if field_mode == "reference" else True
            ok = bool(raw.get("foregrounded")) and bool(item.get("targeted")) and selected_ok
            preview = json.dumps({
                "open_link": nav_link,
                "field": field,
                "target_label": target_label,
                "value": value,
                "surface": surface,
                "field_mode": field_mode,
                "targeted": item.get("targeted"),
                "selected": item.get("selected") if field_mode == "reference" else None,
                "click_xy": item.get("click_xy"),
                "save_requested": save_requested,
            }, ensure_ascii=False)
            steps.append(StepResult(
                name=step.name,
                kind=step.kind,
                status="ok" if ok else "error",
                preview=preview[:500],
                assertion=ok,
                error=None if ok else item.get("reason") or raw.get("reason") or raw.get("error") or "field not targeted",
                attachments=[p for p in [item.get("selection_screenshot"), raw.get("screenshot")] if p],
            ))
        if save_requested:
            ok = bool(raw.get("saved"))
            steps.append(StepResult(
                name="save",
                kind="click_button",
                status="ok" if ok else "error",
                preview=(f"Ctrl+S sent={raw.get('saved')} all_targeted={raw.get('all_targeted')} "
                         f"all_selected={raw.get('all_selected')}"),
                assertion=ok,
                error=None if ok else raw.get("save_blocked_reason") or raw.get("error")
                or "save not attempted because field targeting/selection failed",
            ))
    else:
        steps.append(StepResult(name="write_fields", kind="input_text", status="error", error="no input_text steps to write"))

    persistence = _build_persistence_verification(
        save_requested=save_requested,
        saved=bool(raw.get("saved")),
        evidence=persistence_evidence,
        evidence_error=persistence_error,
    )
    cleanup_required = bool(require_cleanup or (save_requested and raw.get("saved")))
    cleanup = _build_cleanup_verification(
        required=cleanup_required,
        evidence=cleanup_evidence,
        evidence_error=cleanup_error,
    )
    if save_requested or persistence_evidence is not None or persistence_error:
        _emit_qa_bridge_observation(
            subject="persistence_verification",
            status="ok" if persistence.get("ok") else "failed",
            retained_evidence_path=persistence.get("artifact_path")
            if isinstance(persistence.get("artifact_path"), str) else None,
            evidence_summary=str(persistence.get("status") or ""),
            error_class=None if persistence.get("ok") else "PersistenceVerificationFailed",
            error_summary=None if persistence.get("ok") else persistence.get("reason") or persistence.get("status"),
            tool_name="qa.testclient.bridge.persistence_verification",
        )
        steps.append(StepResult(
            name="persistence verification",
            kind="assert_data",
            status="ok" if persistence.get("ok") else "assert_failed",
            preview=json.dumps(persistence, ensure_ascii=False, default=str)[:500],
            assertion=bool(persistence.get("ok")),
            error=None if persistence.get("ok") else persistence.get("reason") or persistence.get("status"),
            attachments=[p for p in [persistence.get("artifact_path")] if isinstance(p, str) and p],
        ))
    if cleanup_required or cleanup_evidence is not None or cleanup_error:
        _emit_qa_bridge_observation(
            subject="cleanup_verification",
            status="ok" if cleanup.get("ok") else "failed",
            retained_evidence_path=cleanup.get("artifact_path")
            if isinstance(cleanup.get("artifact_path"), str) else None,
            evidence_summary=str(cleanup.get("status") or ""),
            error_class=None if cleanup.get("ok") else "CleanupVerificationFailed",
            error_summary=None if cleanup.get("ok") else cleanup.get("reason") or cleanup.get("status"),
            tool_name="qa.testclient.bridge.cleanup_verification",
        )
        steps.append(StepResult(
            name="cleanup verification",
            kind="assert_data_count",
            status="ok" if cleanup.get("ok") else "assert_failed",
            preview=json.dumps(cleanup, ensure_ascii=False, default=str)[:500],
            assertion=bool(cleanup.get("ok")),
            error=None if cleanup.get("ok") else cleanup.get("reason") or cleanup.get("status"),
            attachments=[p for p in [cleanup.get("artifact_path")] if isinstance(p, str) and p],
        ))

    result = ScenarioResult(
        name=scenario.name,
        status="passed" if steps and not unsupported and all(s.status == "ok" for s in steps) else "failed",
        steps=steps,
        started_at=time.time(),
    ).to_dict()
    result["open_link"] = nav_link
    result["write_mode"] = "open_link_label_xtest"
    result["save_requested"] = save_requested
    result["persistence_verification"] = persistence
    result["cleanup_verification"] = cleanup
    return result


def _repo_root() -> Path:
    # Base for runtime OUTPUT (lifecycle logs, screenshots) and the dev capture/env fallback. In the repo
    # this is the checkout root; in a wheel/Docker install it would point into site-packages, so honor
    # QA_MCP_HOME (the container sets it to a writable, mountable workdir, e.g. /work).
    # A factory-bound call must not reconstruct Settings from the process: an
    # explicitly empty home is authoritative and selects the static fallback.
    active_settings = active_application_settings()
    if active_settings is not None:
        home = active_settings.home
    else:
        home = Settings.from_env().home
    if home:
        return Path(home)
    return Path(__file__).resolve().parents[2]


def _lifecycle_output_dir() -> Path:
    """Return the root which owns composed lifecycle output and its marker."""

    return client_lifecycle.ownership_root() / timestamp_name()


# Card 98 #2 — test-results aggregation. A scenario run's outcome is appended here so `get_test_results`
# (and the run-session summary in `get_state`) can report across this MCP-server session, the capture-free
# equivalent of vanessa-mcp's `get_test_results`. Process-lifetime, in-memory (reset with get_test_results(clear=True)).
_RESULTS_LOG: list[dict[str, Any]] = _DEFAULT_APPLICATION_CONTEXT.results_log


def _results_log() -> list[dict[str, Any]]:
    """Return the scenario-result log owned by the active application."""

    return current_application_context().results_log


def _record_result(report: dict[str, Any]) -> dict[str, Any]:
    """Append a scenario run's outcome (a compact summary: name, status, per-step kind/status) to
    the active application's result log. Returns ``report`` unchanged (call-through)."""
    steps = report.get("steps") or []
    _results_log().append({
        "scenario": report.get("scenario"),
        "status": report.get("status"),
        "step_count": len(steps),
        "duration_sec": report.get("duration_sec"),
        "started_at": report.get("started_at"),
        # card 104: keep error/timing/attachments so write_test_report can emit useful JUnit/Allure
        "steps": [{"kind": s.get("kind"), "name": s.get("name"), "status": s.get("status"),
                   "error": s.get("error"), "duration_sec": s.get("duration_sec"),
                   "attachments": s.get("attachments")} for s in steps],
    })
    first_attachment = next(
        (
            path
            for step in steps
            if isinstance(step, dict)
            for path in (step.get("attachments") or [])
            if isinstance(path, str) and path
        ),
        None,
    )
    first_error = next(
        (
            step.get("error")
            for step in steps
            if isinstance(step, dict) and step.get("error")
        ),
        None,
    )
    _emit_qa_bridge_observation(
        subject="scenario_outcome",
        status=report.get("status"),
        duration_ms=int(round(float(report.get("duration_sec") or 0) * 1000)),
        retained_evidence_path=first_attachment,
        error_class="ScenarioFailure" if report.get("status") != "passed" else None,
        error_summary=first_error,
        tool_name="qa.testclient.bridge.scenario_outcome",
        extra={"step_count": len(steps)},
    )
    return report


def _build_action_resolver(action_capture: str, *, captured_input_value: str | None = None,
                           marker_ordinals: "dict[str, int] | None" = None) -> Any:
    """Card 103 Wave 3: build an `action_resolver(step, handle)` from a captured action corpus so action
    steps EXECUTE through `run_single_session` (the production bridge — previously only protocol-research
    tools wired this). Loads the capture's manager frames + the captured ManagedForm/SecondaryFrame GUIDs
    (extracted from the client responses) and delegates to `build_single_session_action_resolver`."""
    from .protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT
    from .protocol.native_write import _read_chunks
    from .protocol.session import extract_managed_form_guid, extract_secondary_frame_guid
    from .scenario.replay import build_single_session_action_resolver

    cap = resolve_capture_dir(action_capture, _repo_root())
    manager_chunks = [{"payload": payload} for payload in _read_chunks(cap, MANAGER_TO_CLIENT)]
    captured_mfg: str | None = None
    captured_sfg: str | None = None
    for payload in _read_chunks(cap, CLIENT_TO_MANAGER):
        captured_mfg = extract_managed_form_guid(payload) or captured_mfg
        captured_sfg = extract_secondary_frame_guid(payload) or captured_sfg
    return build_single_session_action_resolver(
        manager_chunks, captured_mfg, captured_input_value=captured_input_value,
        marker_ordinals=marker_ordinals, captured_secondary_frame_guid=captured_sfg)


def _run(scenario: Scenario, host: str, port: int, capture_dir: str, manager_templates: str, single_session: bool,
         scenario_registry: "dict[str, Scenario] | None" = None, action_resolver: Any = None) -> dict[str, Any]:
    try:
        host, port, attachment = _resolve_testclient_endpoint(host, port, phase="scenario")
    except ConnectionError as exc:
        return _attach_tool_error("run_scenario", "attach", exc, host=host, port=port)
    repo_root = _repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir(capture_dir, repo_root))
    templates = ProtocolTemplates.load((repo_root / manager_templates).resolve() if not Path(manager_templates).is_absolute() else Path(manager_templates))
    synthesized = synthesize_bootstrap()
    output_dir = repo_root / "runtime" / "protocol-research" / "native-mcp" / timestamp_name()

    def session_factory() -> TestClientSession:
        return TestClientSession(host=host, port=port)

    # Card 103 Wave 3: pass the feature's scenario registry so a `run_subscenario` («я выполняю сценарий 'X'»)
    # step resolves its callee by name; the action_resolver (when an action_capture is given) lets capture-backed
    # action steps EXECUTE on the bootstrapped handle; the navigate_resolver lets open_main_form/open_list steps
    # open a form LIVE by nav-link (no capture); `assert_data` builds its read-only OData client lazily from env.
    runner = ScenarioRunner(session_factory, bootstrap, templates, output_dir=output_dir,
                            synthesized=synthesized, scenario_registry=scenario_registry,
                            action_resolver=action_resolver, navigate_resolver=_build_navigate_resolver(),
                            operation_context=current_application_context())
    result = runner.run_single_session(scenario) if single_session else runner.run(scenario)
    report = result.to_dict()
    if attachment is not None:
        report["attached_endpoint"] = attachment
    return _record_result(report)


@qa_tool()
@_resolved_annotations
def transpile(feature_text: str) -> dict[str, Any]:
    """Transpile a .feature (Gherkin, ru/en) into the native Scenario model without executing it.
    Returns the scenario steps and any unmapped (unsupported) step lines."""
    scenario, unmapped = scenario_from_input(None, feature_text)
    return {
        "scenario": scenario.name,
        "steps": [{"kind": s.kind, "name": s.name, "marker": s.marker, "params": s.params, "expect_contains": s.expect_contains} for s in scenario.steps],
        "unmapped": unmapped,
    }


@qa_tool()
@_resolved_annotations
def search_for_steps(keywords: str = "") -> dict[str, Any]:
    """Discover the supported Gherkin step vocabulary. Returns the qa-mcp step library: each recognized step's
    canonical phrasing, a concrete example, its native Step kind, category (read | action | navigation) and a
    description, optionally filtered by ``keywords`` (each whitespace-separated token must appear, case-insensitive;
    empty returns all). The library is derived from the transpiler's STEP_PATTERNS, so it exactly matches what
    ``transpile`` / ``run_scenario`` execute. Use it to author features for qa-mcp; ``transpile`` then flags any
    unmapped lines. Returns {count, total, steps:[{phrase, example, kind, category, description}]}."""
    steps = search_steps(keywords)
    return {"count": len(steps), "total": len(search_steps("")), "keywords": keywords, "steps": steps}


@qa_tool()
@_resolved_annotations
def echo_jsonrpc_arguments(
    open_link: str = "",
    text: str = "",
    arguments_json: Any = None,
) -> dict[str, Any]:
    """Echo parsed JSON-RPC arguments exactly as qa-mcp received them.

    Use this when troubleshooting manual HTTP/MCP requests from Windows PowerShell. It returns the received
    ``open_link`` and optional ``text`` unchanged, parses ``arguments_json`` when it is a JSON object string, and
    adds warnings for common mojibake symptoms such as replacement characters or long question-mark runs.
    """
    arguments, arguments_error = _json_object_option(arguments_json, option="arguments_json")
    received: dict[str, Any] = {
        "open_link": open_link,
        "text": text,
    }
    if arguments is not None:
        received["arguments"] = arguments
    result: dict[str, Any] = {
        "ok": arguments_error is None,
        "received": received,
        "suspect_mojibake": False,
        "warnings": _jsonrpc_value_warnings(received, path="received"),
    }
    result["suspect_mojibake"] = bool(result["warnings"])
    if arguments_error:
        result["error"] = "invalid-arguments-json"
        result["detail"] = arguments_error
    return result


@qa_tool()
@testclient_tool(phase="scenario")
def run_scenario(
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture_dir: str = "tm-v1-ro-batchQ3",
    manager_templates: str = DEFAULT_TEMPLATES,
    scenario_json: str | None = None,
    feature_text: str | None = None,
    single_session: bool = True,
    action_capture: str | None = None,
    action_input_value: str | None = None,
    action_ordinals: str | None = None,
) -> dict[str, Any]:
    """Run a scenario (from feature_text or scenario_json) through the native Python TestManager against a running
    1C /TESTCLIENT at host:port. When ``feature_text`` carries several scenarios, the first runs and the rest
    register as callees for any `run_subscenario` («я выполняю сценарий 'X'») step.

    OPEN steps (``open_main_form`` / ``open_list``) EXECUTE LIVE with no capture: the form is opened by its e1cib
    nav-link via the splice_navigate sequence on the bootstrapped session (config-agnostic, fixture-free — the same
    mechanism read_form_descriptor uses). The step passes when the form actually opens (window-resolved), so «Я
    открываю основную форму справочника 'Валюты'» drives a real client open + state change. Other ACTION steps
    (click/select/input/close/…) re-target a CAPTURED command frame, so to EXECUTE those pass ``action_capture`` —
    the capture dir holding those command frames; each action step's frame is located by its marker and replayed
    GUID-rebound to the live session. ``action_input_value`` is the value baked into the capture's input frame (so a
    `.feature` input_text retargets correctly), and ``action_ordinals`` ("marker=ordinal,marker=ordinal") pins a
    frame when a marker is not unique. Without ``action_capture`` only read/assert/data/skip/subscenario/open steps
    run; other action steps report unsupported. Returns the ScenarioResult."""
    scenario, unmapped = scenario_from_input(scenario_json, feature_text)
    # Build the callee registry from EVERY scenario in the feature so nested calls resolve by name.
    registry = {r.scenario.name: r.scenario for r in transpile_feature(feature_text)} if feature_text else None
    action_resolver = None
    if action_capture:
        marker_ordinals: dict[str, int] | None = None
        if action_ordinals:
            marker_ordinals = {}
            for pair in action_ordinals.split(","):
                marker, _, ordinal = pair.partition("=")
                if ordinal.strip():
                    marker_ordinals[marker.strip()] = int(ordinal)
        action_resolver = _build_action_resolver(
            action_capture, captured_input_value=action_input_value, marker_ordinals=marker_ordinals)
    report = _run(scenario, host, port, capture_dir, manager_templates, single_session,
                  scenario_registry=registry, action_resolver=action_resolver)
    report["unmapped"] = unmapped
    return report


@qa_tool()
@testclient_tool(phase="scenario")
def run_step(
    kind: str,
    marker: str | None = None,
    expect_contains: str | None = None,
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture_dir: str = "tm-v1-ro-batchQ3",
    manager_templates: str = DEFAULT_TEMPLATES,
) -> dict[str, Any]:
    """Run a single read step (read_active_window / read_form_summary / read_element) natively."""
    scenario = Scenario.from_dict({"name": f"step-{kind}", "steps": [{"kind": kind, "name": kind, "marker": marker, "expect_contains": expect_contains}]})
    return _run(scenario, host, port, capture_dir, manager_templates, single_session=True)


@qa_tool()
@testclient_tool(phase="write")
def write_form_value(
    value: str,
    field: str = "PF_EDIT_STRING",
    base_field: str = "PF_EDIT_STRING",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "commit-conn",
    captured_value: str = "QAGENUINE2026",
    default_value: str = "PF_EDIT_STRING_VALUE",
    commit_partner: str | None = None,
    commit_partner_value: str | None = None,
    open_link: str | None = None,
    display: str = ":89",
    input_offset: int = 170,
    save: bool = False,
) -> dict[str, Any]:
    """Write an arbitrary VALUE into a form field and COMMIT it natively.

    Replays the genuine INPUT capture ``capture`` for ``base_field`` (auto-derived template) to establish an
    input-authorized session, retargets the captured value to ``value`` (variable-length, fixed-width aware), and
    verifies by read-back. When ``field`` differs from ``base_field``, the element-address path leaf is re-targeted
    to ``field`` (same enclosing group). ``commit_partner`` (+ ``commit_partner_value``): for a field whose genuine
    input had no trailing focus-change (e.g. base_field="PF_EDIT_NUMBER", captured_value="777,77"), pass another
    field with a genuine input (e.g. commit_partner="PF_EDIT_STRING", commit_partner_value="QAGENUINE2026"); its
    ACTIVATE is appended as the synthesized focus-change so the value COMMITS. Returns committed/readback_value/field.

    ``open_link`` switches to the config-agnostic foreground write route: the target form is opened by nav-link
    and the on-screen field label is targeted with XTEST text input. That route is explicit in the result as
    ``write_mode="open_link_label_xtest"`` and retains a screenshot path."""
    if open_link:
        return _open_link_field_write_result(
            value=value,
            field=field,
            open_link=open_link,
            host=host,
            port=port,
            display=display,
            input_offset=input_offset,
            save=save,
        )
    template = derive_write_template(
        resolve_capture_dir(capture, _repo_root()), base_field, captured_value, default_value,
        commit_partner_field=commit_partner, commit_partner_value=commit_partner_value,
    )
    try:
        host, port, _attachment = _resolve_testclient_endpoint(host, port, phase="write")
    except ConnectionError as exc:
        return _attach_tool_error("write_form_value", "attach", exc, host=host, port=port)
    with NativeWriteSession(template, host=host, port=port) as sess:
        return sess.write(value, field=field)


@qa_tool()
@testclient_tool(phase="write_date")
def write_form_date(
    date: str,
    field: str,
    open_link: str | None = None,
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    display: str = ":89",
    input_offset: int = 170,
    save: bool = False,
    capture: str = "commit-conn",
    base_field: str = "PF_EDIT_STRING",
    captured_value: str = "QAGENUINE2026",
    default_value: str = "PF_EDIT_STRING_VALUE",
) -> dict[str, Any]:
    """Set a FORM-LEVEL managed-form date EditField (`DD.MM.YYYY`), distinct from grid date-cell writing.

    With ``open_link`` this uses the config-agnostic foreground label writer against the target form. Without
    ``open_link`` it falls back to the capture-backed field writer with date-prefix readback acceptance.
    """
    try:
        normalized = _normalize_form_date(date)
    except ValueError as exc:
        return {"ok": False, "error": "invalid-date", "field": field, "requested_date": date, "detail": str(exc)}
    if open_link:
        return _open_link_field_write_result(
            value=normalized,
            field=field,
            open_link=open_link,
            host=host,
            port=port,
            display=display,
            input_offset=input_offset,
            save=save,
            surface="form_field_date",
            field_mode="date",
        )
    result = write_form_value(
        normalized,
        field=field,
        base_field=base_field,
        host=host,
        port=port,
        capture=capture,
        captured_value=captured_value,
        default_value=default_value,
    )
    readback = str(result.get("readback_value") or "")
    result.update({
        "surface": "form_field_date",
        "requested_date": normalized,
        "date_prefix_match": readback.startswith(normalized) if readback else False,
    })
    if readback and readback.startswith(normalized):
        result["committed"] = True
    return result


@qa_tool()
@_local_only_tool(alt="write_form_value / set_table_cell / set_reference_field (protocol writes)")
@testclient_tool(phase="write_xtest")
def write_form_value_xtest(
    value: str,
    field: str = "Наименование",
    capture: str = "demo-write",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    display: str = ":89",
    setup_stop: int = 17,
    read_start: int = 25,
    read_frame: int = 28,
    blur: bool = True,
    save: bool = False,
) -> dict[str, Any]:
    """Write a value into a form field via the protocol+XTEST HYBRID — for OBJECT-attribute fields (Объект.* on
    catalog/document forms) that the pure protocol replay cannot commit.

    The pure ``write_form_value`` only sets a field's edit-text; an object attribute commits only on a genuine user
    edit + blur, which a programmatic SetEditText does not trigger (and 1C exposes no AT-SPI elements). The 1C window
    IS OS-accessible, so this replays the capture's open+focus prefix (protocol, addresses ``field`` by name), then
    injects ``value`` via ``xdotool type`` (Unicode/Cyrillic-aware) into the focused client window on ``display``,
    blurs (Tab -> commit), optionally saves (``save=True`` -> Ctrl+S -> DB), and reads the value back by replaying
    the capture's read sequence. PREREQ: launch the client with ``launch_test_client(display=":89", port=…)`` (and a
    window manager so the form lays out — matchbox); ``display`` must be that Xvfb. Defaults match the demo capture
    (Справочник.Валюты.Наименование). Returns {field, value, committed, value_in_readback, readback_value,
    diverged_at, blurred, saved, display}."""
    backend = _display_backend()
    try:
        host, port, _attachment = _resolve_testclient_endpoint(host, port, phase="write_xtest")
        return native_write_form_value_xtest(
            capture, value, field, host=host, port=port, display=display,
            setup_stop=setup_stop, read_start=read_start, read_frame=read_frame,
            blur=blur, save=save, repo_root=_repo_root(), display_backend=backend,
        )
    except ConnectionError as exc:
        return _attach_tool_error("write_form_value_xtest", "attach", exc, host=host, port=port)
    except client_display.DisplayBackendError as exc:
        return _display_backend_error("write_form_value_xtest", exc)


@qa_tool()
@_local_only_tool(alt="answer_dialog / click_command / the protocol write tools")
def send_keys(
    keys: list[str],
    display: str = ":89",
    settle_sec: float = 0.15,
) -> dict[str, Any]:
    """Send raw OS keystrokes (Enter / Esc / Tab / arrows / shortcuts) to the focused 1C client window. 1C keyboard
    input is OS-LEVEL (the key is in NO manager->client protocol frame), so raw keys are delivered via XTEST
    (xdotool) into the client window. Same primitive as ``write_form_value_xtest``'s DB-verified Tab/Ctrl+S.

    ``keys`` is a sequence of xdotool key specs sent in order (``["Down", "Down", "Return"]``, ``["Escape"]``,
    ``["ctrl+s"]``, ``["Tab"]``…). Keys go to the FOCUSED window (the launched client is the lone app window), so
    PREREQ: launch the client with ``launch_test_client(display=":89", port=…)`` + a window manager (matchbox);
    ``display`` must be that Xvfb. Most keyboard INTENTS already have a protocol tool — confirm/cancel dialogs
    (`answer_dialog`), field commit (Tab / focus-change), row navigation (`select_table_row` / `read_list_grid`),
    save (`click_command` «Записать») — use those first; ``send_keys`` is the raw-key escape hatch for controls that
    need genuine OS keys. Returns {keys, display, sent}."""
    arguments = {"keys": keys, "display": display, "settle_sec": settle_sec}
    return _execute_composed_operation(
        OperationKind.WRITE,
        "send_keys",
        arguments,
        lambda: _send_keys_impl(**arguments),
    )


def _send_keys_impl(keys: list[str], display: str, settle_sec: float) -> dict[str, Any]:
    try:
        return _display_backend().send_keys(keys, display=display, settle_sec=settle_sec)
    except client_display.DisplayBackendError as exc:
        return _display_backend_error("send_keys", exc)


@qa_tool()
@testclient_tool(phase="write")
def write_form_values(
    values: list[str],
    field: str = "PF_EDIT_STRING",
    base_field: str = "PF_EDIT_STRING",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "commit-conn",
    captured_value: str = "QAGENUINE2026",
    default_value: str = "PF_EDIT_STRING_VALUE",
    open_link: str | None = None,
    display: str = ":89",
    input_offset: int = 170,
    save: bool = False,
) -> dict[str, Any]:
    """Batch value-write: open the form ONCE and COMMIT several values in sequence on one connection
    (NativeWriteSession multi-write). Same as write_form_value (incl. capture-free ``field`` addressing via
    ``base_field``) but for ``values`` in order."""
    if open_link:
        raw = _write_open_link_fields_by_label(
            open_link=open_link,
            labels=[field for _ in values],
            values=[str(v) for v in values],
            host=host,
            port=port,
            display=display,
            input_offset=input_offset,
            save=save,
        )
        # card 125 #4 — committed reflects the protocol value-read of the open form, not just on-screen targeting.
        verified = bool((raw.get("readback") or {}).get("verified"))
        writes = []
        for value, item in zip(values, raw.get("results") or []):
            item = item if isinstance(item, dict) else {}
            targeted = bool(item.get("targeted"))
            committed = bool(item.get("committed")) if verified else False
            writes.append({
                "field": field,
                "requested_value": value,
                "readback_value": item.get("readback_value"),
                "committed": committed,
                "accepted": targeted,
                "surface": "form_field",
                "write_mode": "open_link_label_xtest",
            })
        return {
            "field": field,
            "open_link": open_link,
            "opened": raw.get("foregrounded"),
            "writes": writes,
            "all_committed": bool(raw.get("foregrounded")) and bool(raw.get("all_committed")),
            "raw": raw,
        }
    template = derive_write_template(
        resolve_capture_dir(capture, _repo_root()), base_field, captured_value, default_value
    )
    try:
        host, port, _attachment = _resolve_testclient_endpoint(host, port, phase="write")
    except ConnectionError as exc:
        return _attach_tool_error("write_form_values", "attach", exc, host=host, port=port)
    results = []
    with NativeWriteSession(template, host=host, port=port) as sess:
        for v in values:
            results.append(sess.write(v, field=field))
    return {"field": field, "writes": results, "all_committed": all(r["committed"] for r in results)}


@qa_tool()
@testclient_tool(phase="write_scenario")
def run_write_scenario_tool(
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "commit-conn",
    base_field: str = "PF_EDIT_STRING",
    captured_value: str = "QAGENUINE2026",
    default_value: str = "PF_EDIT_STRING_VALUE",
    scenario_json: str | None = None,
    feature_text: str | None = None,
    open_link: str | None = None,
    display: str = ":89",
    input_offset: int = 170,
    save: bool = False,
    persistence_verification_json: str = "",
    cleanup_evidence_json: str = "",
    require_cleanup: bool = False,
) -> dict[str, Any]:
    """Run a WRITE scenario (Gherkin «в поле с именем 'F' я ввожу текст 'V'» / scenario_json) natively: each
    ``input_text`` step is routed through the COMMIT-capable NativeWriteSession, so the value actually commits —
    verified by read-back. Steps may target DIFFERENT fields (step.marker) on one session via capture-free element
    addressing off the ``base_field`` capture (same enclosing group); non-write steps are reported unsupported.
    Returns the ScenarioResult (per-step committed/read-back preview)."""
    scenario, unmapped = scenario_from_input(scenario_json, feature_text)
    try:
        host, port, attachment = _resolve_testclient_endpoint(host, port, phase="write_scenario")
    except ConnectionError as exc:
        return _attach_tool_error("run_write_scenario", "attach", exc, host=host, port=port)
    if open_link or any(s.kind in {"open_create_form", "open_main_form", "open_list"} for s in scenario.steps):
        report = _record_result(_run_open_link_write_scenario(
            scenario,
            host=host,
            port=port,
            open_link=open_link,
            display=display,
            input_offset=input_offset,
            save=save,
            persistence_verification_json=persistence_verification_json,
            cleanup_evidence_json=cleanup_evidence_json,
            require_cleanup=require_cleanup,
        ))
        if attachment is not None:
            report["attached_endpoint"] = attachment
        report["unmapped"] = unmapped
        return report
    result = run_write_scenario(
        scenario, host=host, port=port, capture=capture, base_field=base_field,
        captured_value=captured_value, default_value=default_value,
    )
    report = _record_result(result.to_dict())
    if attachment is not None:
        report["attached_endpoint"] = attachment
    report["unmapped"] = unmapped
    return report


@qa_tool()
@_resolved_annotations
def launch_test_client(
    infobase_path: str | None = None,
    port: int = DEFAULT_CLIENT_PORT,
    user: str | None = None,
    kind: str | None = None,
    headless: bool = True,
    manage_apache: bool = False,
    display: str | None = None,
    env_file: str = client_lifecycle.DEFAULT_ENV_FILE,
    wait_sec: float = 90.0,
    use_hardware_licenses: bool | None = None,
) -> dict[str, Any]:
    """Launch a 1C `/TESTCLIENT` and wait for its TPort to listen.

    Loads the local `.ai1c/*.env` profile (INFOBASE_PATH / PLATFORM_ROOT / TEST_CLIENT_USER/KIND/PASSWORD),
    overridden by any args given. Boots `1cv8 ENTERPRISE /IBConnectionString File="…"; /N<user> /TESTCLIENT -TPort
    <port>`. The client OUTLIVES this call — connect with run_scenario/write_form_value(port=…), then tear down with
    stop_test_client(pid, xvfb_pid). Set manage_apache=true for an Apache-served infobase (stops apache2 for the
    boot, restart on stop_test_client).

    Display (for screenshots): pass ``display=":101"`` (or ``"auto"``) to OWN an Xvfb on that display and run the
    client with DISPLAY=:N — then capture_screenshot(display) works. Default (None) uses `xvfb-run -a` (no
    screenshots). Returns {pid, alive, listening, display, xvfb_pid, connection (password-redacted), out_dir,
    launch_environment}. The password is never echoed back. For an explicitly authorized Windows
    hardware/network-license contour, set ``use_hardware_licenses=true``; when omitted, ignored runtime state may
    opt in with ``QA_MCP_TESTCLIENT_USE_HW_LICENSES=1``."""
    application = current_application_context()
    if application.runtime_target is not None:
        if (
            infobase_path is not None or user is not None or kind is not None
            or env_file != client_lifecycle.DEFAULT_ENV_FILE
            or type(port) is not int or port != application.settings.client_port
        ):
            return _bound_lifecycle_block("launch_test_client", "runtime-target-override-forbidden")
        try:
            target = _provider_testclient_target()
        except (OSError, RuntimeError, ValueError):
            return _bound_lifecycle_block("launch_test_client", "runtime-target-unavailable")
        target.headless, target.manage_apache, target.display = headless, manage_apache, display
        if application.settings.remote_client:
            if not _remote_agent_configured():
                return _bound_lifecycle_block("launch_test_client", "runtime-target-unavailable")
            backend = _remote_agent_backend()
            try:
                observed = backend.launch_test_client(
                    infobase_path=target.infobase_path, connection_string=target.connection_string,
                    user=target.user, password=target.password,
                    platform_version=platform_version_from_root(target.platform_root) or "",
                    use_hardware_licenses=bool(use_hardware_licenses), port=target.port,
                    timeout_seconds=min(max(wait_sec, 1.0), 120.0),
                )
            except client_display.DisplayBackendError:
                return _bound_lifecycle_block("launch_test_client", "runtime-target-unavailable")
            identity = _strict_owned_remote_identity(observed, target.port)
            if (
                identity is None or observed.get("ok") is not True
                or observed.get("listening") is not True or observed.get("alive") is False
            ):
                return _bound_lifecycle_block("launch_test_client", "runtime-target-mismatch")
            pid, _observed_port, lifecycle_id = identity
            protocol_host, protocol_port = _remote_protocol_endpoint(target)
            status = {"pid": pid, "alive": observed.get("alive"), "listening": True,
                      "owns_process": True, "host": protocol_host, "port": protocol_port,
                      "native_port": _observed_port,
                      "lifecycle_handle": dict(observed["lifecycle_handle"]),
                      "client_target": dict(observed["client_target"])}
            return _remember_bound_testclient(
                status, operation="launch_test_client", ownership_class="owned", lifecycle_id=lifecycle_id
            )
        out_dir = _lifecycle_output_dir()
        try:
            status = client_lifecycle.launch_test_client(target, wait_sec=wait_sec, out_dir=out_dir).status()
        except (OSError, RuntimeError, TimeoutError, ValueError):
            return _bound_lifecycle_block("launch_test_client", "runtime-target-unavailable")
        status = {**status, "host": target.host, "port": target.port}
        return _remember_bound_testclient(
            status, operation="launch_test_client", ownership_class="owned",
            lifecycle_id=f"local-{status.get('pid')}-{uuid.uuid4()}",
        )
    repo_root = _repo_root()
    runtime_settings = current_application_context().settings
    env_path = env_file if Path(env_file).is_absolute() else str(repo_root / env_file)
    env = client_lifecycle.load_env_file(env_path)
    target = client_lifecycle.TestClientTarget.from_env(
        env,
        infobase_path=infobase_path,
        port=port,
        host=_runtime_client_host() if _remote_client_enabled() else None,
        user=user,
        kind=kind,
        headless=headless,
        manage_apache=manage_apache,
        display=display,
    )
    if _remote_client_enabled():
        if not _remote_agent_configured():
            return _remote_testclient_launch_failure(
                target=target,
                tool="launch_test_client",
                error="host-agent-not-configured",
                detail="QA_MCP_HOST_AGENT is not set; run the returned host command manually or configure the Windows host-agent.",
                install_command=_host_agent_install_command(),
            )
        backend = _remote_agent_backend()
        resolved_use_hardware_licenses = (
            use_hardware_licenses
            if use_hardware_licenses is not None
            else os.environ.get("QA_MCP_TESTCLIENT_USE_HW_LICENSES", "").strip().lower()
            in {"1", "true", "yes", "on"}
        )
        try:
            host_agent_result = backend.launch_test_client(
                infobase_path=target.infobase_path,
                connection_string=target.connection_string,
                user=target.user,
                password=target.password,
                platform_version=runtime_settings.platform_version or platform_version_from_root(target.platform_root) or "",
                use_hardware_licenses=resolved_use_hardware_licenses,
                port=target.port,
                timeout_seconds=min(max(wait_sec, 1.0), 120.0),
            )
        except client_display.DisplayBackendError as exc:
            public_error = exc.to_result(
                "launch_test_client", remote_client=runtime_settings.remote_client,
            )
            return _remote_testclient_launch_failure(
                target=target,
                tool="launch_test_client",
                error=str(public_error["error"]),
                detail=str(public_error["detail"]),
                host_agent_result=exc.payload,
                install_command=exc.install_command,
            )
        if not host_agent_result.get("ok", True) or host_agent_result.get("listening") is False or host_agent_result.get("alive") is False:
            public_error = client_display.DisplayBackendError(
                str(host_agent_result.get("error") or "host-agent-error"), "",
            ).to_result("launch_test_client", remote_client=runtime_settings.remote_client)
            return _remote_testclient_launch_failure(
                target=target,
                tool="launch_test_client",
                error=str(public_error["error"]),
                detail=str(public_error["detail"]),
                host_agent_result=host_agent_result,
            )
        protocol_host, protocol_port = _remote_protocol_endpoint(target)
        readiness_from_host_agent = _host_agent_owned_readiness_is_authoritative(
            host_agent_result, default_port=target.port
        )
        listening = (
            True
            if readiness_from_host_agent
            else _wait_for_remote_testclient(protocol_host, protocol_port, wait_sec)
        )
        if not listening:
            failure = _remote_testclient_launch_failure(
                target=target,
                tool="launch_test_client",
                error="remote-testclient-relay-not-ready" if (protocol_host, protocol_port) != (target.host, target.port) else "remote-testclient-port-not-listening",
                detail=(
                    f"Host-agent launch returned but routed TestClient endpoint {protocol_host}:{protocol_port} "
                    "is not reachable from the container."
                ),
                host_agent_result=host_agent_result,
            )
            failure["host"] = protocol_host
            failure["port"] = protocol_port
            failure["connection"] = {**target.redacted_summary(), "host": protocol_host, "port": protocol_port}
            return failure
        connection = {**target.redacted_summary(), "host": protocol_host, "port": protocol_port}
        lifecycle_fields = _remote_host_agent_lifecycle_fields(host_agent_result, default_port=target.port)
        client_target = _remote_client_target(host_agent_result, default_port=target.port)
        status = {
            "pid": host_agent_result.get("pid"),
            "alive": None,
            "listening": True,
            "host": protocol_host,
            "port": protocol_port,
            "display": None,
            "xvfb_pid": None,
            "owns_process": lifecycle_fields["owns_process"],
            "attached": True,
            "connection": connection,
            "host_agent": host_agent_result,
            "host_command": _remote_testclient_host_command(target),
        }
        if readiness_from_host_agent:
            status["remote_reachability"] = {
                "method": "host_agent_lifecycle_ready",
                "probe_skipped": True,
                "detail": "host-agent owned launch reported a listening TestClient; local TCP probe skipped",
            }
        if client_target is not None:
            status["client_target"] = client_target
        if status["owns_process"]:
            status["lifecycle_owner"] = lifecycle_fields["lifecycle_owner"]
            status["lifecycle_id"] = lifecycle_fields["lifecycle_id"]
            status["lifecycle_handle"] = lifecycle_fields["lifecycle_handle"]
        return _remember_attached_testclient(status)
    out_dir = _lifecycle_output_dir()
    proc = client_lifecycle.ensure_test_client(
        env_file=env_path, out_dir=out_dir, wait_sec=wait_sec,
        infobase_path=infobase_path, port=port, user=user, kind=kind,
        headless=headless, manage_apache=manage_apache, display=display,
    )
    return proc.status()


@qa_tool()
@_resolved_annotations
def attach_test_client(
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    connect_timeout_sec: float = 0.5,
) -> dict[str, Any]:
    """Attach to an already-listening `/TESTCLIENT` endpoint without owning its process.

    This is for clients started out-of-band, for example with a custom environment or by a host-side launcher.
    The returned handle status records ``attached=true`` and ``owns_process=false``. The MCP server also records
    the endpoint as the active attached context for replay-backed tools that are called with default host/port."""
    application = current_application_context()
    if application.runtime_target is not None:
        configured = (application.settings.client_host, application.settings.client_port)
        if type(port) is not int or (host, port) != configured:
            return _bound_lifecycle_block("attach_test_client", "runtime-target-override-forbidden")
        # A profile records the declared target, but does not observe which
        # infobase the already-running non-owned process actually opened.  Do
        # not promote endpoint reachability, a host-agent PID/port projection,
        # or a prior owned handle into that missing provenance.
        return _bound_lifecycle_block("attach_test_client", "runtime-target-observation-missing")
    current = application.attachment
    if (
        isinstance(current, _AttachedTestClientContext)
        and (host, int(port)) == (current.host, current.port)
        and _attached_endpoint_is_listening(current)
    ):
        status = dict(current.status)
        status.update({"attached": True, "owns_process": False, "listening": True})
        return _remember_attached_testclient(status)
    status = client_lifecycle.attach_test_client(
        host=host,
        port=port,
        connect_timeout_sec=connect_timeout_sec,
    ).status()
    if _remote_client_enabled() and _remote_agent_configured():
        backend = _remote_agent_backend()
        target_port = int(application.settings.host_agent_client_port or port)
        try:
            host_status = backend.test_client_status(port=target_port)
            client_target = _remote_client_target(host_status, default_port=target_port)
            if client_target is not None:
                status["client_target"] = client_target
            status["host_agent"] = host_status
        except client_display.DisplayBackendError as exc:
            status["client_target_error"] = exc.to_result(
                "attach_test_client.client_target", remote_client=application.settings.remote_client,
            )
    return _remember_attached_testclient(status)


@qa_tool()
@_resolved_annotations
def test_client_status(pid: int | None = None, host: str = DEFAULT_CLIENT_HOST, port: int = DEFAULT_CLIENT_PORT) -> dict[str, Any]:
    """Report a launched TestClient's health: whether ``pid`` is alive (if given) and whether its TPort at
    host:port is listening (connectable). Use after launch_test_client / before driving a scenario."""
    application = current_application_context()
    if application.runtime_target is not None:
        configured = (application.settings.client_host, application.settings.client_port)
        if pid is not None or type(port) is not int or (host, port) != configured:
            return _bound_lifecycle_block("test_client_status", "runtime-target-override-forbidden")
        attachment = application.attachment
        if attachment is None and application.session is None:
            return _bound_lifecycle_block("test_client_status", "runtime-target-session-required")
        resolution = validate_runtime_target_resolution(application.runtime_target)
        if (
            type(attachment) is not _AttachedTestClientContext
            or attachment.target is not resolution.binding.target
            or attachment.session is not application.session
            or attachment.binding_generation != resolution.binding.binding_generation
            or (attachment.host, attachment.port) != configured
        ):
            return _bound_lifecycle_block("test_client_status", "runtime-target-mismatch")
        status = _test_client_status_impl(None, attachment.host, attachment.port)
        value = {**_bound_public_identity(attachment), "alive": status["alive"],
                 "listening": status["listening"]}
        return _bound_lifecycle_result("test_client_status", value=value)
    arguments = {"pid": pid, "host": host, "port": port}
    return _execute_composed_operation(
        OperationKind.LIFECYCLE,
        "test_client_status",
        arguments,
        lambda: _test_client_status_impl(**arguments),
    )


def _test_client_status_impl(pid: int | None, host: str, port: int) -> dict[str, Any]:
    return {
        "pid": pid,
        "alive": client_lifecycle.pid_is_alive(pid) if pid is not None else None,
        "listening": client_lifecycle.port_is_listening(host, port),
        "host": host,
        "port": port,
    }


@qa_tool()
@_resolved_annotations
def qa_mcp_doctor(
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    require_bearer_token: bool | None = None,
    com_infobase_path: str = "",
    com_user: str = "",
    com_password: str = "",
    com_query: str = "",
    timeout_sec: float | None = None,
) -> dict[str, Any]:
    """Run the secret-safe end-to-end qa-mcp setup doctor.

    The doctor returns one ordered pass/fail/skipped chain for project-owned bearer-token
    env presence, host-agent HTTP reachability, container-to-host route,
    TestClient TPort reachability, an open-link-free TestClient smoke and
    login/access-dialog state. Platform, COM and private-suite diagnostics are
    intentionally outside the standalone route. When
    ``require_bearer_token`` is omitted, bearer auth is required for HTTP
    transports and skipped for stdio."""
    resolved_require_bearer = (
        _SETTINGS.http_transport != "stdio"
        if require_bearer_token is None
        else require_bearer_token
    )
    doctor_kwargs: dict[str, Any] = {}
    application = current_application_context()
    if application is not _DEFAULT_APPLICATION_CONTEXT:
        doctor_kwargs.update(
            runtime_target=application.runtime_target,
            resolve_configured_target=False,
        )
    return run_qa_mcp_doctor(
        host=host,
        port=port,
        require_bearer_token=resolved_require_bearer,
        com_infobase_path=com_infobase_path,
        com_user=com_user,
        com_password=com_password,
        com_query=com_query,
        timeout_sec=timeout_sec,
        standalone=True,
        **doctor_kwargs,
    )


@qa_tool()
@_resolved_annotations
def stop_test_client(
    pid: int,
    xvfb_pid: int | None = None,
    manage_apache: bool = False,
    lifecycle_id: str = "",
    lifecycle_handle: dict[str, Any] | None = None,
    port: int | None = None,
) -> dict[str, Any]:
    """Tear down a TestClient launched by launch_test_client.

    Local mode stops by PID/process group. Remote-client mode requires the
    host-agent lifecycle handle returned by launch_test_client, so stale or
    recycled PIDs cannot target a newer process."""
    if current_application_context().runtime_target is not None:
        return _bound_lifecycle_block("stop_test_client", "runtime-target-override-forbidden")
    return _stop_test_client_impl(
        pid=pid, xvfb_pid=xvfb_pid, manage_apache=manage_apache,
        lifecycle_id=lifecycle_id, lifecycle_handle=lifecycle_handle, port=port,
    )


def _stop_test_client_impl(
    *, pid: int, xvfb_pid: int | None = None, manage_apache: bool = False,
    lifecycle_id: str = "", lifecycle_handle: Mapping[str, Any] | None = None,
    port: int | None = None,
) -> dict[str, Any]:
    if _remote_client_enabled():
        if not _remote_agent_configured():
            return {
                "ok": False,
                "error": "host-agent-not-configured",
                "mode": "remote-client",
                "tool": "stop_test_client",
                "pid": int(pid),
                "detail": (
                    "QA_MCP_HOST_AGENT is not set; remote-client cleanup must be routed "
                    "through the Windows host-agent that launched the TestClient."
                ),
                "install_command": _host_agent_install_command(),
            }
        provided_lifecycle_id = str(lifecycle_id or "").strip()
        normalized_handle = dict(lifecycle_handle) if isinstance(lifecycle_handle, Mapping) else None
        handle_lifecycle_id = _remote_lifecycle_id(normalized_handle)
        if provided_lifecycle_id and handle_lifecycle_id and provided_lifecycle_id != handle_lifecycle_id:
            return {
                "ok": True,
                "mode": "remote-client",
                "tool": "stop_test_client",
                "pid": int(pid),
                "port": int(port) if port is not None else None,
                "state": "not_owned",
                "stopped": False,
                "refused": True,
                "reason": "lifecycle_handle_mismatch",
                "lifecycle_owner": "host-agent",
                "detail": "Remote TestClient cleanup lifecycle_id must match lifecycle_handle.id.",
            }
        resolved_lifecycle_id = provided_lifecycle_id or handle_lifecycle_id
        if not resolved_lifecycle_id:
            return {
                "ok": True,
                "mode": "remote-client",
                "tool": "stop_test_client",
                "pid": int(pid),
                "port": int(port) if port is not None else None,
                "state": "not_owned",
                "stopped": False,
                "refused": True,
                "reason": "missing_lifecycle_handle",
                "lifecycle_owner": "host-agent",
                "detail": "Remote TestClient cleanup requires lifecycle_handle.id from launch_test_client.",
            }
        backend = _remote_agent_backend()
        try:
            host_agent_result = backend.stop_test_client(
                pid=int(pid),
                port=port,
                lifecycle_id=resolved_lifecycle_id,
                lifecycle_handle=normalized_handle,
            )
        except client_display.DisplayBackendError as exc:
            return {
                **exc.to_result("stop_test_client", remote_client=True),
                "pid": int(pid),
            }
        result = dict(host_agent_result)
        result.setdefault("ok", True)
        result["mode"] = "remote-client"
        result["tool"] = "stop_test_client"
        if result.get("state") in {"stopped", "already_stopped"} and result.get("refused") is not True:
            current = current_application_context().attachment
            current_lifecycle_id = (
                str(current.status.get("lifecycle_id") or "").strip()
                if isinstance(current, _AttachedTestClientContext)
                else ""
            )
            if isinstance(current, _AttachedTestClientContext) and not current_lifecycle_id:
                current_lifecycle_id = _remote_lifecycle_id(current.status.get("lifecycle_handle"))
            if (
                isinstance(current, _AttachedTestClientContext)
                and current.status.get("pid") == pid
                and current_lifecycle_id == resolved_lifecycle_id
            ):
                _clear_attached_testclient_context()
        return result
    return client_lifecycle.stop_by_pid(pid, xvfb_pid=xvfb_pid, restore_apache=manage_apache)


def _project_bound_cleanup() -> dict[str, Any]:
    """Detach or stop only the exact lifecycle admitted by this application."""

    application = current_application_context()
    attachment = application.attachment
    if application.runtime_target is None or type(attachment) is not _AttachedTestClientContext:
        return _bound_lifecycle_block("stop_test_client", "runtime-target-session-required")
    binding = validate_runtime_target_resolution(application.runtime_target).binding
    if (
        attachment.target is not binding.target
        or attachment.session is not application.session
        or attachment.binding_generation != binding.binding_generation
    ):
        return _bound_lifecycle_block("stop_test_client", "runtime-target-cleanup-not-owned")
    identity = _bound_public_identity(attachment)
    if attachment.ownership_class == "attached" and attachment.status.get("owns_process") is False:
        _clear_bound_testclient_context()
        return _bound_lifecycle_result("stop_test_client", value={
            **identity, "ok": True, "state": "detached", "stopped": False,
            "refused": False, "reason": "attached_process_not_owned",
        })
    cleanup = attachment.cleanup
    if attachment.ownership_class != "owned" or not isinstance(cleanup, Mapping):
        return _bound_lifecycle_block("stop_test_client", "runtime-target-cleanup-not-owned")
    pid, lifecycle_id, port = cleanup.get("pid"), cleanup.get("lifecycle_id"), cleanup.get("port")
    if (
        type(pid) is not int or pid <= 0
        or type(lifecycle_id) is not str or lifecycle_id != attachment.lifecycle_id
        or type(port) is not int or not 0 < port <= 65535
    ):
        return _bound_lifecycle_block("stop_test_client", "runtime-target-cleanup-not-owned")
    handle = cleanup.get("lifecycle_handle")
    if application.settings.remote_client:
        if not isinstance(handle, Mapping) or (
            type(handle.get("pid")) is not int or handle.get("pid") != pid
            or type(handle.get("port")) is not int or handle.get("port") != port
            or type(handle.get("id")) is not str or handle.get("id") != lifecycle_id
        ):
            return _bound_lifecycle_block("stop_test_client", "runtime-target-cleanup-not-owned")
    elif handle is not None:
        return _bound_lifecycle_block("stop_test_client", "runtime-target-cleanup-not-owned")
    result = _stop_test_client_impl(
        pid=pid,
        xvfb_pid=cleanup.get("xvfb_pid") if type(cleanup.get("xvfb_pid")) is int else None,
        manage_apache=cleanup.get("manage_apache") is True,
        lifecycle_id=lifecycle_id,
        lifecycle_handle=handle,
        port=port if application.settings.remote_client else None,
    )
    completed = result.get("refused") is not True and (
        result.get("stopped") is True or result.get("state") in {"stopped", "already_stopped"}
    )
    if completed:
        _clear_bound_testclient_context()
    public_result = {
        key: result[key] for key in ("ok", "state", "stopped", "refused", "reason")
        if key in result
    }
    return _bound_lifecycle_result("stop_test_client", value={**identity, **public_result})


def _aggregate_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate scenario-result summaries: scenario/pass/fail counts, total steps, per-step-status counts."""
    status_counts: dict[str, int] = {}
    step_status: dict[str, int] = {}
    for r in results:
        status_counts[r.get("status")] = status_counts.get(r.get("status"), 0) + 1
        for s in r.get("steps", []):
            step_status[s.get("status")] = step_status.get(s.get("status"), 0) + 1
    return {
        "scenarios": len(results),
        "passed": status_counts.get("passed", 0),
        "failed": status_counts.get("failed", 0),
        "total_steps": sum(r.get("step_count", 0) for r in results),
        "step_status_counts": step_status,
    }


@qa_tool()
@_resolved_annotations
def get_test_results(clear: bool = False) -> dict[str, Any]:
    """Aggregate the scenarios run in THIS MCP-server session natively. Every ``run_scenario`` / ``run_step`` /
    ``run_write_scenario_tool`` call records its outcome; this returns the roll-up: {scenarios, passed, failed,
    total_steps, step_status_counts {ok|assert_failed|error: n}, results:[{scenario, status, step_count,
    steps:[{kind, name, status}]}]}. The log is process-lifetime, in-memory; pass ``clear=true`` to report the
    current roll-up AND reset it (adds ``cleared`` = how many were dropped). Use it after a batch of scenarios to get
    a single pass/fail report instead of eyeballing each ScenarioResult."""
    log = _results_log()
    results = list(log)
    agg = _aggregate_results(results)
    agg["results"] = results
    if clear:
        agg["cleared"] = len(log)
        log.clear()
    return agg


@qa_tool()
@_resolved_annotations
def write_test_report(
    out_dir: str,
    formats: list[str] | None = None,
    suite_name: str = "qa-mcp",
    clear: bool = False,
) -> dict[str, Any]:
    """Write machine-readable test reports for the scenarios run THIS MCP-server session so qa-mcp slots into an
    existing CI pipeline. ``formats`` (default both): ``"junit"`` -> ``<out_dir>/junit.xml`` (CI test-result
    panels); ``"allure"`` -> ``<out_dir>/allure-results/*.json`` (renderable by the Allure CLI, with per-step
    status/timing and any screenshot attachments). Uses the same session log as ``get_test_results``; pass
    ``clear=true`` to reset it after writing. Returns the output paths + scenario count."""
    from .scenario.reporting import junit_xml, write_allure_results

    fmts = formats if formats is not None else ["junit", "allure"]
    log = _results_log()
    results = list(log)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: dict[str, Any] = {}
    if "junit" in fmts:
        path = out / "junit.xml"
        path.write_text(junit_xml(results, suite_name=suite_name), encoding="utf-8")
        written["junit"] = str(path)
    if "allure" in fmts:
        allure_dir = out / "allure-results"
        paths = write_allure_results(results, allure_dir, suite_name=suite_name)
        written["allure"] = {"dir": str(allure_dir), "files": len(paths)}
    if clear:
        log.clear()
    result = {"out_dir": str(out), "scenarios": len(results), "written": written}
    _emit_qa_bridge_observation(
        subject="test_report",
        status="ok",
        retained_evidence_path=str(out),
        tool_name="qa.testclient.bridge.test_report",
        extra={"scenario_count": len(results), "written_formats": sorted(written), "format_count": len(written)},
    )
    return result


# Card 125 #1 — the OData data-layer tools are DEPRECATED for a test-client-held infobase. A file/server base
# opened by a «Клиент тестирования» is held under an EXCLUSIVE lock, so an out-of-process OData/COM reader cannot
# open it — an OData read-back of what the running client just did is impossible on the same base. Verify UI writes
# through the SAME test client's protocol value-read instead (write_form_fields_by_label's value-read `committed`,
# read_record / read_form_descriptor / read_table_cell). These tools stay usable ONLY against a SEPARATELY published,
# non-exclusive OData endpoint (a different base, or a server infobase not held for testing); they remain here (not
# removed) pending the scenario/autofill/regression/gherkin cleanup. They report `deprecated: true` + guidance.
_ODATA_TEST_CLIENT_DEPRECATION = (
    "DEPRECATED for a test-client-held base: a file/server infobase opened by a «Клиент тестирования» is exclusively "
    "locked, so OData/COM cannot read it — verify UI writes via the same test client's protocol value-read "
    "(write_form_fields_by_label `committed`, read_record, read_form_descriptor, read_table_cell) instead. Use OData "
    "only against a separately published, non-exclusive endpoint."
)


def _mark_odata_deprecated(result: dict[str, Any]) -> dict[str, Any]:
    """Annotate an OData tool result with the test-client-held-base deprecation (card 125 #1), additively (the
    underlying `ok`/values are untouched) so a caller sees the guidance without a behaviour change."""
    return {**result, "deprecated": True, "deprecation": _ODATA_TEST_CLIENT_DEPRECATION}


@qa_tool()
@_resolved_annotations
def assert_data(
    entity_set: str,
    field: str,
    expected: str,
    filter: str = "",
    key: str = "",
    match: str = "equals",
    base_url: str = "",
    user: str = "",
    password: str = "",
    select: str = "",
) -> dict[str, Any]:
    """DEPRECATED for a test-client-held base — see below. Assert a value in the DATA LAYER via
    read-only 1C OData. Locate a record in ``entity_set`` (e.g. 'Catalog_Товары') by an OData ``filter`` (e.g.
    "Description eq 'Обувь'") or a ``key`` (Ref_Key guid / code), then assert ``field`` against ``expected`` with
    ``match`` = equals|contains|regex. Connection from params or env (QA_MCP_ODATA_URL/USER/PASSWORD). Returns {ok,
    actual, expected, record_count, deprecated, deprecation, …}.

    DEPRECATION: an infobase opened by a «Клиент тестирования» is EXCLUSIVELY LOCKED, so OData cannot read it — an
    OData read-back of what the running test client just did is impossible on that base. Verify UI writes through the
    SAME client's protocol value-read (``write_form_fields_by_label`` returns a value-read ``committed``;
    ``read_record`` / ``read_form_descriptor`` read committed values). This tool is valid ONLY against a SEPARATELY
    published, non-exclusive OData endpoint."""
    from .data import ODataClient, assert_data_value

    client = ODataClient(base_url or None, user or None, password or None)
    sel = [s.strip() for s in select.split(",") if s.strip()] or None
    return _mark_odata_deprecated(assert_data_value(
        client, entity_set, field, expected,
        key=key or None, filter=filter or None, match=match, select=sel))


@qa_tool()
@_resolved_annotations
def assert_data_count(
    entity_set: str,
    expected: int,
    op: str = "eq",
    filter: str = "",
    base_url: str = "",
    user: str = "",
    password: str = "",
) -> dict[str, Any]:
    """DEPRECATED for a test-client-held base — a «Клиент тестирования» holds the infobase under an
    EXCLUSIVE lock, so OData cannot read it; verify via the same client's protocol value-read (``read_record`` /
    ``read_form_descriptor``) instead. Assert the NUMBER of records matching a filter in the DATA LAYER. ``op`` =
    eq|ne|gt|lt|ge|le; e.g. assert a posting created exactly N register rows, or that no orphan remains (op='eq',
    expected=0). Read-only OData; valid only against a separately published, non-exclusive endpoint. Returns {ok,
    count, expected, op, deprecated, deprecation, ...}."""
    from .data import ODataClient, assert_data_count_value
    client = ODataClient(base_url or None, user or None, password or None)
    return _mark_odata_deprecated(
        assert_data_count_value(client, entity_set, int(expected), op=op, filter=filter or None))


@qa_tool()
@_resolved_annotations
def query_com(
    infobase_path: str,
    query: str,
    user: str = "",
    password: str = "",
    timeout_sec: float = 30.0,
    max_rows: int = 100,
    prog_id: str = "V83.COMConnector",
) -> dict[str, Any]:
    """Run a read-only 1C query through the Windows host-agent COM bridge.

    This is the file-infobase data path for model-B installs without OData:
    qa-mcp sends an authenticated host-agent `/com/execute` WorkerRequest to the
    bundled `ai-com-worker.exe` on the Windows host. Obvious write-shaped query
    text is rejected locally before host transport. Configure
    `QA_MCP_HOST_AGENT` and `QA_MCP_HOST_AGENT_TOKEN`; the host install must have
    `ai-com-worker.exe` available for `/com/execute`.
    """
    from .com_host import query_com as _query_com

    return _query_com(
        infobase_path=infobase_path,
        query=query,
        user=user,
        password=password,
        timeout_sec=float(timeout_sec),
        max_rows=int(max_rows),
        prog_id=prog_id,
    )


@qa_tool()
@_resolved_annotations
def assert_com_count(
    infobase_path: str,
    query: str,
    expected: int,
    op: str = "eq",
    count_field: str = "",
    user: str = "",
    password: str = "",
    timeout_sec: float = 30.0,
    prog_id: str = "V83.COMConnector",
) -> dict[str, Any]:
    """Assert a numeric result from a read-only host-side COM query.

    Use for file infobases where OData is not published. `query` should return a
    single row whose first value, or `count_field` when supplied, is numeric.
    `op` is one of eq/ne/gt/lt/ge/le.
    """
    from .com_host import assert_com_count as _assert_com_count

    return _assert_com_count(
        infobase_path=infobase_path,
        query=query,
        expected=int(expected),
        op=op,
        count_field=count_field,
        user=user,
        password=password,
        timeout_sec=float(timeout_sec),
        prog_id=prog_id,
    )


@qa_tool()
@_resolved_annotations
def com_connector_doctor(
    infobase_path: str,
    user: str = "",
    password: str = "",
    query: str = "",
    timeout_sec: float = 30.0,
    prog_id: str = "V83.COMConnector",
) -> dict[str, Any]:
    """Diagnose Windows `V83.COMConnector` registration and optional read smoke.

    Calls the authenticated host-agent COMConnector doctor on the Windows host.
    The doctor checks 64-bit registration state, TypeLib presence, COM
    creation, file-infobase connection, and an optional read-only query. If the
    TypeLib is missing, the result includes the elevated
    `C:\\Windows\\System32\\regsvr32.exe` remediation command.
    """
    from .com_host import com_connector_doctor as _com_connector_doctor

    return _com_connector_doctor(
        infobase_path=infobase_path,
        user=user,
        password=password,
        query=query,
        timeout_sec=float(timeout_sec),
        prog_id=prog_id,
    )


@qa_tool()
@_resolved_annotations
def role_data_matrix(
    entity_set: str,
    roles: list[dict[str, Any]],
    filter: str = "",
    base_url: str = "",
) -> dict[str, Any]:
    """DEPRECATED for a test-client-held base — a «Клиент тестирования» holds the infobase under an
    EXCLUSIVE lock, so OData cannot read it; this matrix is valid only against a SEPARATELY published, non-exclusive
    endpoint. Run the SAME data-layer read under several credentials/ROLES and report per-role access + count. Each
    role = {label, user, password} + optional expectation {expect_access: "read"|"denied", min_count: N}. Returns
    {ok, roles: [{label, access ('read'|'denied'|'error'), count, http, ok}], deprecated, deprecation}. NOTE: a
    genuine role-DIFFERENCE matrix needs restricted infobase users provisioned out-of-band (admin-mcp) — outside
    qa-mcp's read-only scope."""
    from .data import role_data_matrix as _matrix
    return _mark_odata_deprecated(_matrix(entity_set, roles, base_url=base_url or None, filter=filter or None))


@qa_tool()
@_resolved_annotations
def generate_smoke_suite(
    objects: list[dict[str, str]],
    feature_name: str = "smoke — формы открываются",
    out_path: str = "",
) -> dict[str, Any]:
    """Generate a runnable SMOKE suite from a metadata listing — auto-author "does every form still open + render?"
    tests. ``objects`` is a list of {kind, name} (kind ru/en: Справочник/Документ/Обработка/Отчёт), e.g. from
    meta-mcp ``metadata_list``. Returns the generated `.feature` text (canonical steps — transpiles 100%, runnable
    via `run_scenario`), the per-object ``open_links`` (for `read_form_descriptor(open_link=…)`), and counts.
    Optional ``out_path`` writes the feature. Drive it: meta-mcp ``metadata_list`` -> this tool -> ``run_scenario`` /
    per-link ``read_form_descriptor``."""
    from .scenario import generate_smoke_feature, generate_smoke_scenarios

    feature = generate_smoke_feature(objects, feature_name=feature_name)
    scenarios = generate_smoke_scenarios(objects)
    if out_path:
        Path(out_path).write_text(feature, encoding="utf-8")
    return {
        "count": len(scenarios),
        "skipped": len(objects) - len(scenarios),
        "feature": feature,
        "open_links": [{"kind": s["kind"], "name": s["name"], "open_link": s["open_link"]} for s in scenarios],
        "out_path": out_path or None,
    }


_CREATE_FILL_KIND_PHRASE = {"справочник": "элемент справочника", "catalog": "элемент справочника",
                            "документ": "документ", "document": "документ"}


@qa_tool()
@_resolved_annotations
def autofill_required_fields(mdo_xml: str, kind: str, name: str, out_path: str = "",
                            resolve_references: bool = True, odata_url: str = "", odata_user: str = "",
                            odata_password: str = "", enum_src_root: str = "") -> dict[str, Any]:
    """Metadata-driven required-field AUTOFILL for create-form smoke. Given an object's EDT ``.mdo`` XML and its
    ``kind`` (Справочник/Документ, ru/en) + ``name``, find the MANDATORY attributes (``fillChecking=ShowError`` —
    «ЗаполнениеПроверки = ВыдаватьОшибку»; standard Owner/Parent gated on owners/hierarchy), synthesize a smoke
    value per PRIMITIVE type (String/Number/Date/Boolean), and emit a runnable create-and-fill `.feature` («я создаю
    новый <kind> 'X'» + «в поле 'F' я ввожу текст 'V'» per fillable field).

    REFERENCE-typed required fields (CatalogRef./DocumentRef.) are resolved to an EXISTING value from the data layer
    (read-only OData) when ``resolve_references`` (default), so the plan covers DOCUMENTS, not just primitive
    catalogs — each such field gets ``source="odata-ref"``. OData config falls back to env
    (``QA_MCP_ODATA_URL``/``USER``/``PASSWORD``). EnumRef fields resolve to the first enum value (``source="enum"``)
    when ``enum_src_root`` points at the EDT src root (reads ``<root>/Enums/<Имя>/<Имя>.mdo``). Returns {object,
    create_link, required, fillable, unfillable, feature}. Optional ``out_path`` writes the feature."""
    from .scenario import build_autofill_plan, create_fill_feature

    client = None
    if resolve_references:
        from .data import ODataClient
        client = ODataClient(odata_url or None, odata_user or None, odata_password or None)
    enum_provider = None
    if enum_src_root:  # read <root>/Enums/<EnumName>/<EnumName>.mdo to resolve required EnumRef fields
        def enum_provider(enum_name: str, _root: str = enum_src_root) -> str | None:
            p = Path(_root) / "Enums" / enum_name / f"{enum_name}.mdo"
            return p.read_text(encoding="utf-8") if p.exists() else None
    plan = build_autofill_plan(mdo_xml, kind, name, odata_client=client, enum_mdo_provider=enum_provider)
    kind_phrase = _CREATE_FILL_KIND_PHRASE.get(kind.strip().lower(), "элемент справочника")
    feature = create_fill_feature(kind_phrase, name, plan["fillable"])
    if out_path:
        Path(out_path).write_text(feature, encoding="utf-8")
    return {**plan, "feature": feature, "out_path": out_path or None}


@qa_tool()
@_resolved_annotations
def infobase_info(
    env_file: str = client_lifecycle.DEFAULT_ENV_FILE,
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    infobase_path: str | None = None,
) -> dict[str, Any]:
    """Report the configured TestClient infobase / connection metadata natively. Reads the local ``.ai1c/*.env``
    profile (INFOBASE_PATH / PLATFORM_ROOT / TEST_CLIENT_KIND / TEST_CLIENT_USER) into a target descriptor — the
    **password is never echoed** (only ``password_set``) — and reports whether the TPort at host:port is live.
    Override the profile with ``infobase_path`` / ``env_file``. Returns {env_file, env_present, infobase {host, port,
    kind, user, target, headless, display, password_set}, platform_root, client_bin, listening}. Richer config
    name/version metadata (from the handshake) is a decode follow-up."""
    application = current_application_context()
    if application.runtime_target is not None:
        return {
            "target": _bound_logical_target_identity(),
            "listening": client_lifecycle.port_is_listening(host, port),
        }
    repo_root = _repo_root()
    env_path = env_file if Path(env_file).is_absolute() else str(repo_root / env_file)
    env = client_lifecycle.load_env_file(env_path)
    target = client_lifecycle.TestClientTarget.from_env(env, host=host, port=port, infobase_path=infobase_path)
    return {
        "env_file": env_path,
        "env_present": bool(env),
        "infobase": target.redacted_summary(),
        "platform_root": target.platform_root,
        "client_bin": target.resolved_client_bin(),
        "listening": client_lifecycle.port_is_listening(host, port),
    }


@qa_tool()
@_resolved_annotations
def get_state(
    pid: int | None = None,
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    env_file: str = client_lifecycle.DEFAULT_ENV_FILE,
) -> dict[str, Any]:
    """Snapshot the native QA engine's session/run state. Aggregates three views: ``connection`` (the TestClient
    TPort liveness, + ``pid`` aliveness if given), ``run_session`` (the scenarios run this server session — counts +
    the last scenario/status, from the same log as ``get_test_results``), and ``infobase`` (the configured target
    identity, password-redacted, from the ``.ai1c`` profile). Returns {engine {default_capture, value_read_templates},
    connection {pid, alive, host, port, listening}, run_session {…aggregate…, last_scenario, last_status}, infobase
    {…redacted…}}."""
    application = current_application_context()
    if application.runtime_target is not None:
        bound_target = _bound_logical_target_identity()
    else:
        repo_root = _repo_root()
        env_path = env_file if Path(env_file).is_absolute() else str(repo_root / env_file)
        env = client_lifecycle.load_env_file(env_path)
        target = client_lifecycle.TestClientTarget.from_env(env, host=host, port=port)
    log = _results_log()
    run_session = _aggregate_results(log)
    last = log[-1] if log else None
    run_session["last_scenario"] = last["scenario"] if last else None
    run_session["last_status"] = last["status"] if last else None
    result = {
        "engine": {"default_capture": "tm-v1-ro-batchQ3", "value_read_templates": VALUE_READ_TEMPLATES},
        "connection": {
            "pid": pid,
            "alive": client_lifecycle.pid_is_alive(pid) if pid is not None else None,
            "host": host,
            "port": port,
            "listening": client_lifecycle.port_is_listening(host, port),
        },
        "run_session": run_session,
    }
    if application.runtime_target is not None:
        result["target"] = bound_target
    else:
        result["infobase"] = target.redacted_summary()
    return result


@qa_tool()
@_local_only_tool(alt="get_window_list_testclient (the protocol-level 1C window list)")
def get_window_list(display: str, geometry: bool = True) -> dict[str, Any]:
    """Enumerate the visible OS windows on the TestClient's X display natively. Lists the window-manager's top-level
    windows on ``display`` (the one from ``launch_test_client(display=…)`` status, e.g. ":101") via xdotool — id +
    title (+ ``geometry`` {x, y, width, height} unless ``geometry=false``). Use to see what the client has open
    (main window, an opened list/card, a modal dialog) at the OS level; address an individual window programmatically
    with ``activate_window`` / ``close_window``. Requires xdotool + a launched display. Returns {display, count,
    windows:[{id, title, geometry?}]}. (The protocol-level "windows known to the test client" list is
    ``get_window_list_testclient``.)"""
    arguments = {"display": display, "geometry": geometry}
    return _execute_composed_operation(
        OperationKind.READ, "get_window_list", arguments,
        lambda: _get_window_list_impl(**arguments),
    )


def _get_window_list_impl(display: str, geometry: bool) -> dict[str, Any]:
    try:
        windows = _display_backend().list_windows(display, geometry=geometry)
    except client_display.DisplayBackendError as exc:
        return _display_backend_error("get_window_list", exc)
    return {"display": display, "count": len(windows), "windows": windows,
            "backend": _display_backend().name}


def _get_window_list_handler(request: OperationRequest) -> OperationResult | dict[str, Any]:
    """Adapt the documented legacy window-list failure DTO at its producer.

    ``_get_window_list_impl`` remains directly callable for compatibility and
    therefore retains its historic error dictionary.  The registered primitive
    has an unambiguous producer identity, so it can preserve the operation
    verdict without teaching the generic executor to infer verdicts from
    arbitrary dictionary keys.
    """

    value = _get_window_list_impl(**dict(request.arguments))
    if (
        type(value) is dict
        and value.get("ok") is False
        and value.get("tool") == "get_window_list"
        and type(value.get("error")) is str
        and type(value.get("detail")) is str
    ):
        return OperationResult.failure(
            request,
            code=value["error"],
            message=value["detail"],
        )
    return value


@qa_tool()
@_local_only_tool()
def capture_screenshot(
    display: str,
    window: str | None = None,
    out_path: str | None = None,
) -> dict[str, Any]:
    """Capture an OS-level PNG screenshot of the TestClient's X display (Linux).

    ``display`` is the one from launch_test_client(display=…) status (e.g. ":101"). Optional ``window`` is a title
    substring (xdotool) to capture a single window instead of the whole display; if no window matches, falls back to
    the full display (matched_window_id=null). Captures with scrot (fallback ImageMagick import). Returns {path,
    display, window, matched_window_id, size_bytes, tool}; read the PNG at `path`."""
    arguments = {"display": display, "window": window, "out_path": out_path}
    return _execute_composed_operation(
        OperationKind.DISPLAY,
        "capture_screenshot",
        arguments,
        lambda: _capture_screenshot_impl(**arguments),
    )


def _capture_screenshot_impl(
    display: str,
    window: str | None,
    out_path: str | None,
) -> dict[str, Any]:
    repo_root = _repo_root()
    if out_path is None:
        out = repo_root / "runtime" / "protocol-research" / "screenshots" / f"{timestamp_name()}.png"
    else:
        out = Path(out_path) if Path(out_path).is_absolute() else repo_root / out_path
    try:
        result = _display_backend().capture_screenshot(display, out, window=window)
    except client_display.DisplayBackendError as exc:
        return _display_backend_error("capture_screenshot", exc)
    _emit_qa_bridge_observation(
        subject="screenshot",
        status="ok" if result.get("path") else "warn",
        retained_evidence_path=result.get("path"),
        sensitivity_class="screenshot" if result.get("path") else "internal",
        tool_name="qa.testclient.bridge.screenshot",
        extra={
            "display": result.get("display"),
            "window": result.get("window"),
            "matched_window_id": result.get("matched_window_id"),
            "size_bytes": result.get("size_bytes"),
        },
    )
    return result


@qa_tool()
@_local_only_tool()
def open_external_processor(
    path: str,
    display: str,
    expect_caption: str = "",
    main_menu_x: int = 1163,
    main_menu_y: int = 14,
    settle_sec: float = 2.0,
) -> dict[str, Any]:
    """Open an EXTERNAL data processor/report (``.epf``/``.erf``) in the running client the 1C-NATIVE way. NO
    external input component, NO config object: drives «Главное меню (≡, top-right) -> Файл -> Открыть» (located
    on-screen via ``locate_text``) -> the GTK file chooser -> Ctrl+L -> types ``path`` Unicode-safe
    (``xtest_type_unicode`` — plain typing drops Cyrillic) -> Enter. The Gherkin step «Я открываю внешнюю обработку
    или отчет '<path>' (Расширение)» maps to this. PREREQ (as for ``write_form_value_xtest``): the client was
    launched with an Xvfb ``display`` + a window manager (matchbox). Pass ``expect_caption`` (e.g. a substring of the
    processor's window title) to verify the form opened. Returns {path, opened, caption_found, dialog_closed,
    screenshot, located}."""
    from .protocol.native_xtest import locate_text

    backend = _display_backend()
    shotdir = _repo_root() / "runtime" / "protocol-research" / "screenshots" / timestamp_name()
    shotdir.mkdir(parents=True, exist_ok=True)

    def cap(name: str) -> Path:
        p = shotdir / name
        backend.capture_screenshot(display, p)
        return p

    located: dict[str, Any] = {}
    try:
        backend.click(main_menu_x, main_menu_y, display=display)  # «Главное меню»
    except client_display.DisplayBackendError as exc:
        return _display_backend_error("open_external_processor", exc)
    time.sleep(1.2)
    try:
        fx = locate_text(cap("01-mainmenu.png"), "Файл")
    except client_display.DisplayBackendError as exc:
        return _display_backend_error("open_external_processor", exc)
    located["Файл"] = fx
    if not fx:
        return {"path": path, "opened": False, "reason": "«Файл» not located in the main menu",
                "screenshot": str(shotdir / "01-mainmenu.png"), "located": located}
    backend.click(*fx, display=display)
    time.sleep(1.0)
    ox = locate_text(cap("02-file-submenu.png"), "Открыть")
    located["Открыть"] = ox
    if not ox:
        return {"path": path, "opened": False, "reason": "«Открыть» not located in the Файл submenu",
                "screenshot": str(shotdir / "02-file-submenu.png"), "located": located}
    backend.click(*ox, display=display)
    time.sleep(settle_sec)
    # GTK file chooser: Ctrl+L (location entry) -> type the path (Unicode-safe) -> Enter
    backend.send_keys(["ctrl+l"], display=display)
    time.sleep(0.6)
    backend.type_text(path, display=display, unicode=True)
    time.sleep(0.6)
    backend.send_keys(["Return"], display=display)
    time.sleep(settle_sec + 1.0)
    final = cap("03-after-open.png")
    dialog_closed = locate_text(str(final), "Открыть файл") is None  # the GTK chooser title is gone => accepted
    caption_found = (locate_text(str(final), expect_caption) is not None) if expect_caption else None
    opened = caption_found if expect_caption else dialog_closed
    return {"path": path, "opened": bool(opened), "caption_found": caption_found,
            "expect_caption": expect_caption or None, "dialog_closed": dialog_closed,
            "screenshot": str(final), "located": located}


@qa_tool()
@_local_only_tool(alt="write_form_value / set_table_cell addressed by field name")
@testclient_tool(phase="write_open_link")
def write_form_fields_by_label(
    open_link: str,
    labels: list[str],
    values: list[str],
    display: str,
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    input_offset: int = 170,
    date_input_offset: int = 90,
    input_column_gap: int = 24,
    save: bool = False,
    field_modes: list[str] | None = None,
    settle_sec: float = 1.2,
    readback: bool = True,
    readback_caption: str = "",
) -> dict[str, Any]:
    """Write values into form fields located by their on-screen LABEL — CONFIG-AGNOSTIC, no per-field capture
    (generalizes ``write_form_value_xtest`` beyond a single fixed field). Foregrounds the form by ``open_link`` (e.g.
    ``e1cib/data/Справочник.Валюты`` create form), then TWO-PASS: pass 1 `locate_text`'s every label and records its
    right edge; pass 2 clicks each field into the SHARED input column (rightmost label edge + ``input_column_gap``) —
    so a short reference label like «Владелец» hits the same right-aligned column as the longest label instead of
    under-reaching into a neighbour — types the value Unicode-safe (``xtest_type_unicode`` — Cyrillic-safe) -> Tab.
    (A ``field_mode="date"`` field clicks its own input mask at ``date_input_offset`` and types digit keys, never the
    calendar button; with 0/1 located labels the column falls back to the legacy label-center + ``input_offset``.)
    Pairs with ``autofill_required_fields`` (feed its resolved {label->value} plan). ``save`` -> Ctrl+S (creates a
    record).

    HONEST verification: after typing, the open form is value-READ on a fresh manager connection (``readback``,
    default on) and each item's ``committed`` is set True ONLY when the requested value is actually read back from
    the form model (the «стал равен» value-read) — a field targeted on screen but not read back is
    ``committed=False`` (no false positives). OData cannot verify here: a test-client-held file/server base is
    exclusively locked, so the protocol value-read of the SAME client is the verification, not ``assert_data``.

    PREREQ: client launched with an Xvfb ``display`` + matchbox. ``all_targeted`` = every label located + typed;
    ``all_committed`` = every targeted value read back. Returns {open_link, foregrounded, results:[{label, value,
    click_xy, targeted, committed, readback_value, geometry}], all_targeted, all_committed, readback:{opened,
    field_count, verified, fields}, screenshot}."""
    from .protocol.native_xtest import input_column_x, locate_text

    backend = _display_backend()
    shotdir = _repo_root() / "runtime" / "protocol-research" / "screenshots" / timestamp_name()
    shotdir.mkdir(parents=True, exist_ok=True)
    # Start the foreground from a CLEAN working area. The card-101 replay opens the form correctly only when no
    # other forms are stacked: with pre-existing tabs (e.g. the live-regression write check runs after the read
    # checks, which leave catalog forms open) the GUID rebinder mis-binds the window GUIDs and the replay surfaces
    # a stale tab instead of the target form. Escape closes the active form (a list/object form just closes; the
    # start page can't be closed), so a bounded Escape sweep collapses any accumulated tabs to the start page —
    # config-agnostic and idempotent on an already-clean client. Best-effort: never block the write.
    if display:
        for _ in range(8):
            try:
                backend.send_keys(["Escape"], display=display)
                time.sleep(0.45)
            except Exception:  # noqa: BLE001
                break
    normalized_open_link = _normalize_data_ref_link(open_link)
    foreground_resource: Any | None
    foreground_meta: dict[str, Any]
    if _is_bare_create_data_link(normalized_open_link):
        foreground_resource, foreground_meta = _open_bare_create_form_for_write(
            normalized_open_link, host=host, port=port)
    else:
        foreground_resource = _foreground_form_by_link(normalized_open_link, host=host, port=port)
        foreground_meta = {
            "foreground_method": "listreplay",
            "normalized_open_link": normalized_open_link,
        }
    results: list[dict[str, Any]] = []
    final = shotdir / "final.png"
    modes = field_modes or ["text" for _ in labels]
    saved = False
    if len(modes) != len(labels):
        return {"open_link": open_link, "foregrounded": False, "results": [], "all_targeted": False,
                "error": "label-mode-count-mismatch", "labels": labels, "field_modes": field_modes or []}
    try:
        if foreground_resource is None:
            return {"open_link": open_link, "foregrounded": False, "results": [], "all_targeted": False,
                    "reason": foreground_meta.get("reason") or "form did not foreground", **foreground_meta}
        time.sleep(settle_sec)
        # card 125 #2 — TWO-PASS geometry. Managed-form inputs are right-aligned to the LONGEST label on the
        # form, so a short reference label like «Владелец» (or «Код») whose own center + input_offset under-reaches
        # the input column lands in a NEIGHBOUR field. Pass 1 locates every label and records its right edge; pass 2
        # clicks every field into the SHARED input column derived from the rightmost located label edge, so short
        # and long labels alike hit the same column.
        located: list[dict[str, Any]] = []
        for idx, (label, value, field_mode) in enumerate(zip(labels, values, modes)):
            activation_retry: str | None = None
            lx = None
            locate_diag: dict[str, Any] = {}
            shot = shotdir / f"locate-{idx:02d}.png"
            for attempt in range(2):
                try:
                    backend.capture_screenshot(display, shot)
                except client_display.DisplayBackendError as exc:
                    return _display_backend_error("write_form_fields_by_label", exc)
                # 1C labels render with a trailing colon; match «Label:» first so a short label doesn't match inside a
                # longer one («Наименование» ⊂ «Наименование основной валюты»). Fall back to the bare label.
                # card 125: capture which localization path/point size located the label (primary vs short-label
                # fallback) so a short reference label like «Владелец» reports the knob it needed, plus the matched
                # box (diag["box"]["right"]) that pass 2 needs for the input column.
                locate_diag = {}
                lx = (locate_text(str(shot), f"{label}:", diag=locate_diag)
                      or locate_text(str(shot), label, diag=locate_diag))
                if not _should_retry_label_locate(foreground_meta.get("foreground_method"), attempt, lx):
                    break
                activate = getattr(foreground_resource, "activate", None)
                if activate is not None:
                    activation_retry = "protocol_window_command"
                    foreground_meta["activation_result"] = activate()
                else:
                    activation_retry = "ctrl+tab"
                    backend.send_keys(["ctrl+tab"], display=display)
                time.sleep(settle_sec)
                shot = shotdir / f"locate-{idx:02d}-retry.png"
            located.append({"label": label, "value": value, "field_mode": field_mode, "lx": lx,
                            "locate_diag": locate_diag, "activation_retry": activation_retry})
        # Derive the shared input column from the RIGHTMOST located label edge (non-date fields only — a date field
        # clicks its own input mask, never the column). With 0/1 usable edges the column is unreliable, so
        # input_column_x falls back to the legacy per-field label-center + input_offset.
        right_edges = [
            (entry["locate_diag"].get("box") or {}).get("right")
            for entry in located
            if entry["lx"] is not None and entry["field_mode"] != "date"
        ]
        usable_edges = [e for e in right_edges if e is not None]
        input_col_x = (input_column_x(usable_edges, gap=input_column_gap, fallback_offset=input_offset)
                       if len(usable_edges) >= 2 else None)
        for idx, entry in enumerate(located):
            label, value, field_mode = entry["label"], entry["value"], entry["field_mode"]
            lx, locate_diag, activation_retry = entry["lx"], entry["locate_diag"], entry["activation_retry"]
            if not lx:
                results.append({"label": label, "value": value, "click_xy": None, "targeted": False,
                                "field_mode": field_mode, "reason": "label not located",
                                "activation_retry": activation_retry})
                continue
            # card 125: a managed-form date field carries a calendar-dropdown button at the right edge of its input;
            # the default input_offset(170) from the label center lands ON that button (opens the picker, leaves the
            # field empty). For field_mode="date" click into the input MASK with a smaller offset and type the date
            # as digit keys (the proven inline path — «30.06.2026» -> keys 3,0,0,6,2,0,2,6 fill the mask and commit),
            # never touching the calendar button. Non-date fields click the shared two-pass input column (or, when
            # the column is unavailable, fall back to the legacy label-center + input_offset).
            if field_mode == "date":
                click_x, geometry = lx[0] + date_input_offset, "date_mask"
            elif input_col_x is not None:
                click_x, geometry = input_col_x, "input_column"
            else:
                click_x, geometry = lx[0] + input_offset, "label_offset"
            click_xy = (click_x, lx[1])
            backend.click(*click_xy, display=display)
            time.sleep(0.4)
            if field_mode in {"reference", "choice", "date"}:
                backend.send_keys(["ctrl+a"], display=display)
                time.sleep(0.2)
            if field_mode == "date":
                backend.send_keys([ch for ch in value if ch.isdigit()], display=display)
            else:
                backend.type_text(value, display=display, unicode=True)
            time.sleep(0.4)
            backend.send_keys(["Tab"], display=display)
            time.sleep(0.8 if field_mode == "reference" else 0.3)
            item = {"label": label, "value": value, "click_xy": list(click_xy),
                    "targeted": True, "field_mode": field_mode, "geometry": geometry, "locate": locate_diag}
            if field_mode == "reference":
                verify_shot = shotdir / f"select-{idx:02d}.png"
                try:
                    backend.capture_screenshot(display, verify_shot)
                except client_display.DisplayBackendError as exc:
                    return _display_backend_error("write_form_fields_by_label", exc)
                selected = locate_text(str(verify_shot), value) is not None
                item.update({"selected": selected, "selection_screenshot": str(verify_shot)})
                if not selected:
                    item["reason"] = "requested reference value not visible after input"
            if activation_retry is not None:
                item["activation_retry"] = activation_retry
            results.append(item)
        all_targeted_now = bool(results) and all(bool(item.get("targeted")) for item in results)
        all_selected_now = bool(results) and all(
            bool(item.get("selected")) if item.get("field_mode") == "reference" else True
            for item in results
        )
        if save and all_targeted_now and all_selected_now:
            backend.send_keys(["ctrl+s"], display=display)
            time.sleep(settle_sec + 1.0)
            saved = True
        backend.capture_screenshot(display, final)
    finally:
        close = getattr(foreground_resource, "close", None)
        if close is not None:
            try:
                close()
            except OSError:
                pass
    all_targeted = bool(results) and all(bool(r.get("targeted")) for r in results)
    all_selected = bool(results) and all(
        bool(r.get("selected")) if r.get("field_mode") == "reference" else True
        for r in results
    )
    # card 125 #4 — HONEST verification. The socket that foregrounded the form is now closed but the form stays
    # open as a tab; on a fresh manager connection value-READ the open form and confirm each requested value was
    # actually committed to the form model (the Vanessa «стал равен» equivalent). OData cannot do this on a
    # test-client-held base (exclusive lock), so a targeted-on-screen field is no longer reported committed until
    # the value is read back. Best-effort: a read-back that cannot resolve the form leaves committed unverified.
    readback_meta: dict[str, Any] = {}
    # ``verified`` = the value-read actually retrieved values (field_count > 0). A form that RESOLVES but yields no
    # values (the cold-client boundary never materialised after the retries) is INCONCLUSIVE, not authoritative — so
    # verification is applied and claimed only when values were read; otherwise committed is left unverified.
    readback_verified = False
    if readback and any(r.get("targeted") for r in results):
        readback_meta = _read_open_form_field_values(host=host, port=port, caption_match=readback_caption)
        readback_verified = readback_meta.get("field_count", 0) > 0
        if readback_verified:
            _apply_readback_verification(results, readback_meta.get("fields", {}))
    committed_items = [r for r in results if r.get("targeted")]
    all_committed = readback_verified and bool(committed_items) and all(
        bool(r.get("committed")) for r in committed_items)
    out = {"open_link": open_link, "foregrounded": True, "results": results,
           "all_targeted": all_targeted, "all_selected": all_selected,
           "all_committed": all_committed,
           "readback": {"opened": readback_meta.get("opened"),
                        "field_count": readback_meta.get("field_count", 0),
                        "verified": readback_verified,
                        "read_attempts": readback_meta.get("read_attempts"),
                        "fields": readback_meta.get("fields", {}),
                        **({"error": readback_meta["error"]} if readback_meta.get("error") else {})},
           "save_requested": save, "saved": saved, "screenshot": str(final), **foreground_meta}
    if save and not saved:
        out["save_blocked_reason"] = "not all fields were targeted and selected"
    return out


@qa_tool()
@testclient_tool(phase="page_switch")
def switch_page(
    target_page: str,
    base_page: str = "PF_PAGE_B",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "multiaction-clean",
) -> dict[str, Any]:
    """Switch the active tab page (закладку) natively. Opens the form (replays the genuine setup from ``capture``,
    which switched to ``base_page``) and sends the genuine page-switch command re-targeted to ``target_page`` (the
    page-Group leaf). Returns {base_page, target_page, accepted}. (A page-switch has no value read-back — use
    capture_screenshot to confirm visually.)"""
    template = derive_page_switch(resolve_capture_dir(capture, _repo_root()), base_page)
    return native_switch_page(template, target_page, host=host, port=port)


@qa_tool()
@testclient_tool(phase="checkbox_toggle")
def toggle_checkbox(
    target_field: str,
    base_field: str = "PF_CHECKBOX_FALSE",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "genuine-card90-20260617/traffic-selfcontained",
) -> dict[str, Any]:
    """Toggle a Boolean checkbox (флаг) natively. A checkbox commits with NO value buffer: the wire only ACTIVATES
    the EditField (the value-free `e0 4b 55` toggle, identical for set & clear) and the server flips the Boolean +
    fires ПриИзменении — the EditField twin of switch_page. Opens the form (replays the genuine setup from
    ``capture``, which toggled ``base_field``) and sends the genuine toggle re-targeted to ``target_field`` (the
    EditField leaf). Returns {base_field, target_field, accepted}. (A toggle has no ASCII value read-back — the
    Boolean reads as Да/Нет; confirm via a side-effect field or capture_screenshot.)"""
    template = derive_checkbox_toggle(resolve_capture_dir(capture, _repo_root()), base_field)
    return native_toggle_checkbox(template, target_field, host=host, port=port)


@qa_tool()
@testclient_tool(phase="choice_set")
def set_choice(
    variant: str,
    base_field: str = "PF_CHOICE_MODE",
    target_field: str | None = None,
    captured_variant: str = "PF_CHOICE_A",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "genuine-card90-choice-20260617/traffic-selfcontained",
) -> dict[str, Any]:
    """Set a radio (Переключатель) to ``variant`` natively. A choice ACTIVATES the EditField and carries the
    selected variant as a length-prefixed string (`…EditField[NAME] … e0 4b 53 <0x9a><len><variant>`); ``variant``
    is the value NAME (e.g. PF_CHOICE_C). Opens the form (replays the genuine setup from ``capture``, which set
    ``base_field`` to ``captured_variant``) and sends the genuine choose block re-targeted: the EditField leaf to
    ``target_field`` (defaults to ``base_field``) + the variant string to ``variant`` (same-length swap). Returns
    {base_field, target_field, variant, accepted}."""
    template = derive_choice_set(resolve_capture_dir(capture, _repo_root()), base_field, captured_variant)
    return native_set_choice(template, variant, target_field=target_field, host=host, port=port)


@qa_tool()
@testclient_tool(phase="table_cell_write")
def set_table_cell(
    value: str,
    column: str = "PF_TABLE_TEXT",
    table: str = "PF_TABLE_ITEMS",
    base_column: str = "PF_TABLE_TEXT",
    base_table: str = "PF_TABLE_ITEMS",
    captured_value: str = "CELLAA",
    commit_partner_field: str = "PF_EDIT_STRING",
    commit_partner_value: str = "C90CMT",
    row_match: str | None = None,
    captured_row_match: str = "PF_ROW_002_TEXT",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "genuine-card90-table-20260617/traffic-selfcontained",
) -> dict[str, Any]:
    """Write ``value`` into a table cell on the ACTIVE row natively. A table-cell SET is byte-identical to a plain
    string-field SET; only the element path differs — the column is the `EditField` leaf inside a `Table[<table>]`
    segment, with NO row index (the edit hits the active/selected row). Opens the form (replays the genuine setup
    from ``capture``, which added a row and edited ``base_column`` to ``captured_value``), then re-targets the cell
    SET to ``table``/``column`` + the value and commits via the synthesized focus-change (``commit_partner_field`` —
    same machinery as the number field). The fixture's editable table is ``PF_TABLE_ITEMS`` (PF_TABLE_TEXT string,
    PF_TABLE_NUMBER number; PF_TABLE_MARKER read-only). The NUMBER cell uses the SAME value buffer as the string
    cell — the genuine PF_TABLE_NUMBER SET is byte-identical (`e0 41 81 81 ba <len> <ascii>`, value as text), so
    ``set_table_cell(value, column="PF_TABLE_NUMBER")`` just works (readback "999"). A grid DATE cell is NOT drivable
    this way: the date control rejects text input («Неподходящий тип элемента управления»); use
    ``set_table_date_cell``. Returns {requested_value, readback_value, committed, column, table}. The cell read-back
    IS reliable: the SET response echoes the committed value via the column EditField + value-SET tag — so
    ``readback_value``/``committed`` reflect the actual write (no screenshot needed).

    ROW ADDRESSING: by default the write hits the captured active row. To write into a SPECIFIC row, use a
    ``capture`` whose setup selected a row (with ``base_column=PF_TABLE_TEXT``, ``captured_value=R2WROT``,
    ``commit_partner_value=C90RC``) and pass ``row_match`` = the target row's ``base_column`` value — the genuine
    row-select's search value (``captured_row_match``, default ``PF_ROW_002_TEXT``) is re-targeted in the setup so
    the row whose column equals ``row_match`` becomes active (row_match=PF_ROW_003_TEXT writes into row 3)."""
    template = derive_table_cell_write(
        resolve_capture_dir(capture, _repo_root()), base_column, captured_value,
        commit_partner_field=commit_partner_field, commit_partner_value=commit_partner_value,
    )
    return native_set_table_cell(
        template, value, target_column=column, target_table=table, base_table=base_table,
        row_match=row_match, captured_row_match=captured_row_match, host=host, port=port,
    )


def _drive_calendar_pick(
    *, display: str, button: tuple[int, int], d: int, m: int, y: int, from_year: int | None,
    settle_sec: float, out_dir: Path, column: str, table: str, requested_date: str,
    activation_screenshot: str, verify_in_row_band: bool = False, backend: Any | None = None,
) -> dict[str, Any]:
    """Card 99/100 — drive the open date-cell calendar by mouse from the localized dropdown ``button`` (center):
    open the dropdown, navigate the YEAR forward if the target differs from the cell's current year (the ‹/› arrows
    step the MONTH, so the year uses the «<year> ▼» dropdown — current at row 0, current+k below, chained in steps
    of CALENDAR_YEAR_MAX_STEP), then click the month + day and commit (Return). The popup month-list / day-grid
    origins are FIXED deltas from the button, so they travel with it. Shared by the fixture-capture path
    (``_set_table_date_cell``) and the config-agnostic open_link path (``_set_table_date_cell_open_link``). Returns
    the result dict; the proof is the screenshot (a mouse-set cell has no protocol SET echo). ``verify_in_row_band``
    confirms the calendar closed by re-locating the button ONLY in the cell's row band — required on real forms that
    have OTHER date fields (e.g. the document header «Дата») whose calendar glyph would else false-positive."""
    from datetime import date as _date

    from .protocol.native_xtest import (
        CALENDAR_DAY_DELTA, CALENDAR_MONTH_DELTA, CALENDAR_YEAR_MAX_STEP, calendar_day_cell, calendar_month_cell,
        calendar_year_row, locate_calendar_button,
    )

    display_backend = backend or client_display.LocalXTestBackend()
    bx, by = button
    month_origin = (bx + CALENDAR_MONTH_DELTA[0], by + CALENDAR_MONTH_DELTA[1])
    day_origin = (bx + CALENDAR_DAY_DELTA[0], by + CALENDAR_DAY_DELTA[1])
    current_year = from_year if from_year is not None else _date.today().year
    year_offset = y - current_year
    year_nav = {"current_year": current_year, "target_year": y, "offset": year_offset, "applied": False}
    if year_offset < 0:                            # forward-only dropdown — do NOT set the wrong year
        return {"column": column, "table": table, "requested_date": requested_date, "localized": True,
                "button_xy": [bx, by], "status": "blocked", "year_nav": year_nav,
                "reason": f"target year {y} is before the cell's current year {current_year}; backward year "
                          "navigation is not yet supported (the year dropdown lists forward only) — pass "
                          "from_year, or target a year >= the current one", "screenshot": activation_screenshot}
    display_backend.click(bx, by, display=display)                   # open the calendar dropdown
    time.sleep(settle_sec)
    remaining = year_offset                         # forward: chain dropdown opens, up to MAX_STEP per open
    while remaining > 0:
        step = min(remaining, CALENDAR_YEAR_MAX_STEP)
        display_backend.click(*calendar_year_row((bx, by), 0), display=display)     # open the year dropdown
        time.sleep(settle_sec)
        display_backend.click(*calendar_year_row((bx, by), step), display=display)  # click row = current+step
        time.sleep(settle_sec)
        remaining -= step
        year_nav["applied"] = True
    mx, my = calendar_month_cell(m, origin=month_origin)
    display_backend.click(mx, my, display=display)
    time.sleep(settle_sec)
    dx, dy = calendar_day_cell(y, m, d, origin=day_origin)
    display_backend.click(dx, dy, display=display)
    time.sleep(settle_sec)
    display_backend.send_keys(["Return"], display=display)                   # commit the cell edit into the active row
    time.sleep(settle_sec)
    picked = str(out_dir / "02_picked.png")
    display_backend.capture_screenshot(display, picked)
    # Confirm the calendar dropdown is gone (the pick committed and closed it). On a real document form (open_link)
    # the doc-header «Дата» field carries a permanent calendar glyph, so verify ONLY in the cell's row band.
    if verify_in_row_band:
        import subprocess as _sp
        band = str(out_dir / "02b_picked_rowband.png")
        _sp.run(["convert", picked, "-crop", f"1280x44+0+{max(0, by - 22)}", "+repage", band], check=False)
        still_open = locate_calendar_button(band) is not None
    else:
        still_open = locate_calendar_button(picked) is not None
    return {"column": column, "table": table, "requested_date": requested_date, "localized": True,
            "button_xy": [bx, by], "month_origin": list(month_origin), "day_origin": list(day_origin),
            "year_nav": year_nav, "status": "set" if not still_open else "set_calendar_open",
            "verified_by": "screenshot", "screenshot": picked, "activation_screenshot": activation_screenshot}


def _set_table_date_cell(
    *, date: str, column: str, table: str, base_column: str, captured_value: str,
    commit_partner_field: str, commit_partner_value: str, host: str, port: int, display: str,
    capture: str, manage_wm: bool, settle_sec: float, from_year: int | None = None,
    backend: Any | None = None, date_parts: tuple[int, int, int] | None = None,
) -> dict[str, Any]:
    """Card 99 #2 — set a grid DATE cell with ON-SCREEN-LOCALIZED coordinates (no hardcoded pixels). Activates
    the date cell over the protocol (the shipped table-cell write_block, activate+SET WITHOUT commit, so the
    inline date editor + calendar dropdown button appear), screenshots, locates the calendar button by
    template-match, then drives the calendar by mouse (click button -> month -> day -> Return) using the popup
    geometry DERIVED from the localized button (fixed deltas), and reads the cell back."""
    import os
    import subprocess

    from .protocol.native_mutation import _read_available
    from .protocol.native_write import build_write_frame
    from .protocol.native_xtest import locate_calendar_button

    display_backend = backend or client_display.LocalXTestBackend()
    d, m, y = date_parts if date_parts is not None else _normalize_table_date_parts(date)[1:]
    template = derive_table_cell_write(
        resolve_capture_dir(capture, _repo_root()), base_column, captured_value,
        commit_partner_field=commit_partner_field, commit_partner_value=commit_partner_value,
    )
    out_dir = _repo_root() / "runtime" / "protocol-research" / "native-mcp" / timestamp_name()
    out_dir.mkdir(parents=True, exist_ok=True)
    wm = None
    if manage_wm:
        try:
            wm = subprocess.Popen(["matchbox-window-manager", "-use_titlebar", "no"],
                                  env={**os.environ, "DISPLAY": display},
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1.0)
        except FileNotFoundError:
            wm = None
    try:
        with NativeWriteSession(template, host=host, port=port) as s:
            lo, hi = s.t.write_block                       # ACTIVATE the date cell (write_block, no commit)
            for i in range(lo, hi + 1):
                wire = build_write_frame(s._rebinder.apply(s._mgr[i]), s.t.captured_value, captured_value,
                                         base_field=s.t.field, target_field=column, seq=s._seq)
                s._seq += 1
                s._sock.sendall(wire)
                s._rebinder.observe_response(_read_available(s._sock, s.rt, s.it))
            time.sleep(settle_sec)
            shot = str(out_dir / "01_activated.png")
            display_backend.capture_screenshot(display, shot)
            button = locate_calendar_button(shot)          # LOCALIZE — no hardcoded coords
            if button is None:
                return {"column": column, "table": table, "requested_date": date, "localized": False,
                        "committed": False, "status": "blocked",
                        "reason": "calendar dropdown button not located (cell not activated, off-screen, "
                                  "or theme/resolution mismatch) — no fallback to guessed coordinates",
                        "screenshot": shot}
            return _drive_calendar_pick(
                display=display, button=button, d=d, m=m, y=y, from_year=from_year, settle_sec=settle_sec,
                out_dir=out_dir, column=column, table=table, requested_date=date, activation_screenshot=shot,
                backend=display_backend,
            )
    finally:
        if wm is not None:
            wm.terminate()


def _foreground_form_by_link(
    open_link: str, *, host: str, port: int, read_timeout_sec: float = 6.0,
    idle_timeout_sec: float = 1.5, connect_timeout_sec: float = 10.0, max_total_sec: float = 30.0,
    allow_partial: bool = False,
) -> Any:
    return protocol_foreground.foreground_form_by_link(
        open_link,
        host=host,
        port=port,
        read_timeout_sec=read_timeout_sec,
        idle_timeout_sec=idle_timeout_sec,
        connect_timeout_sec=connect_timeout_sec,
        max_total_sec=max_total_sec,
        allow_partial=allow_partial,
        repo_root=_repo_root(),
    )


def _set_table_date_cell_open_link(
    *, date: str, open_link: str, column: str, table: str, column_title: str | None,
    cell_xy: tuple[int, int] | None, row_offset: int, host: str, port: int, display: str,
    manage_wm: bool, settle_sec: float, from_year: int | None, prime: bool, foreground: str = "listreplay",
    backend: Any | None = None, date_parts: tuple[int, int, int] | None = None,
) -> dict[str, Any]:
    """Card 100/101 — set a tabular DATE cell on ANY navigated document form, CONFIG-AGNOSTIC (no per-form capture).
    FOREGROUND the form (Blocker 1), then activate the date cell ON SCREEN — double-click the cell located from its
    column header ``column_title`` (subimage-search; the descriptor has no pixel bounds) or the explicit ``cell_xy``
    (Blocker 3) — and reuse the form-agnostic calendar localization + month/day/year pick (``_drive_calendar_pick``).
    Returns the pick result + ``opened`` / ``cell_xy``.

    ``foreground`` selects the foreground method (card 101):
    - ``"listreplay"`` (DEFAULT, fixture-FREE, config-agnostic): replay the genuine cold catalog-list-open sequence
      retargeted to ``open_link`` (``_foreground_form_by_link``) — opens the target as the active tab with NO
      fixture, holding the manager socket open during the on-screen pick. Live-verified: Документ.Заказ Товары.Дата
      → 15.08.2026 and cross-year 10.03.2028, no fixture tab.
    - ``"fixture"`` (legacy fallback): prime tabbed mode with the bundled fixture render-push frames
      (``_VALUE_READ_OPEN_FRAMES``) then ``splice_navigate`` — needs the vanessa_client fixture."""
    import os
    import subprocess

    from .protocol.native_xtest import (
        locate_calendar_button, locate_text, table_cell_from_header,
    )

    display_backend = backend or client_display.LocalXTestBackend()
    d, m, y = date_parts if date_parts is not None else _normalize_table_date_parts(date)[1:]
    if cell_xy is None and not column_title:
        raise ValueError("the open_link path needs either cell_xy=(x, y) or column_title=<the date column's "
                         "on-screen header text> to locate the cell")

    out_dir = _repo_root() / "runtime" / "protocol-research" / "native-mcp" / timestamp_name()
    out_dir.mkdir(parents=True, exist_ok=True)

    def _pick_after_foreground(opened: str) -> dict[str, Any]:
        """Shared: screenshot the FOREGROUND form, localize + activate the date cell, drive the calendar pick."""
        form_shot = str(out_dir / "00_form.png")
        display_backend.capture_screenshot(display, form_shot)
        cxy = cell_xy
        if cxy is None:
            header = locate_text(form_shot, column_title or "")
            if header is None:
                return {"column": column, "table": table, "requested_date": date, "opened": opened,
                        "localized": False, "status": "blocked",
                        "reason": f"date column header {column_title!r} not localized on screen (title/font/theme "
                                  "mismatch) — pass cell_x / cell_y", "screenshot": form_shot}
            cxy = table_cell_from_header(header, row_offset=row_offset)
        cx, cy = int(cxy[0]), int(cxy[1])
        display_backend.double_click(cx, cy, display=display)             # ACTIVATE the date cell editor
        time.sleep(settle_sec)
        act = str(out_dir / "01_activated.png")
        display_backend.capture_screenshot(display, act)
        # LOCALIZE the calendar button in the cell's ROW BAND (the doc-header «Дата» glyph would else win).
        band_y0 = max(0, cy - 22)
        band = str(out_dir / "01b_rowband.png")
        subprocess.run(["convert", act, "-crop", f"1280x44+0+{band_y0}", "+repage", band], check=False)
        rel = locate_calendar_button(band)
        button = (rel[0], rel[1] + band_y0) if rel else None
        if button is None:
            return {"column": column, "table": table, "requested_date": date, "opened": opened,
                    "cell_xy": [cx, cy], "localized": False, "status": "blocked",
                    "reason": "calendar dropdown button not located in the cell row band (cell not activated, "
                              "off-screen, or theme mismatch) — check cell_x / cell_y and 01_activated.png",
                    "screenshot": act}
        result = _drive_calendar_pick(
            display=display, button=button, d=d, m=m, y=y, from_year=from_year, settle_sec=settle_sec,
            out_dir=out_dir, column=column, table=table, requested_date=date, activation_screenshot=act,
            verify_in_row_band=True, backend=display_backend,
        )
        result.update({"opened": opened, "cell_xy": [cx, cy], "foreground": foreground})
        return result

    wm = None
    if manage_wm:
        try:
            wm = subprocess.Popen(["matchbox-window-manager", "-use_titlebar", "no"],
                                  env={**os.environ, "DISPLAY": display},
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1.0)
        except FileNotFoundError:
            wm = None
    try:
        if foreground == "fixture":                         # legacy: fixture render-push primer + splice_navigate
            repo_root = _repo_root()
            bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo_root))
            templates = ProtocolTemplates.load((repo_root / VALUE_READ_TEMPLATES).resolve())
            synthesized = synthesize_bootstrap()
            with TestClientSession(host=host, port=port) as session:
                handle = session.open_and_bootstrap(bootstrap=bootstrap, templates=templates,
                                                    output_dir=out_dir, synthesized=synthesized)
                time.sleep(1.0)
                if prime:
                    handle.run_segment(_VALUE_READ_OPEN_FRAMES, query_id="form-element-details")
                    time.sleep(1.5)
                resolved = _open_form_by_link(handle, open_link)
                if resolved is None:
                    return {"column": column, "table": table, "requested_date": date, "opened": None,
                            "status": "blocked", "reason": f"form did not open/resolve for {open_link!r}"}
                time.sleep(2.0)
                return _pick_after_foreground(resolved[0])
        # DEFAULT: fixture-free foreground (card 101) — hold the manager socket open during the on-screen pick.
        sock = _foreground_form_by_link(open_link, host=host, port=port)
        if sock is None:
            return {"column": column, "table": table, "requested_date": date, "opened": None, "status": "blocked",
                    "reason": f"fixture-free foreground replay diverged for {open_link!r}"}
        try:
            time.sleep(2.0)
            return _pick_after_foreground(open_link)
        finally:
            sock.close()
    finally:
        if wm is not None:
            wm.terminate()


@qa_tool()
@_local_only_tool(alt="set_table_cell (protocol cell write)")
@testclient_tool(phase="table_date_cell")
def set_table_date_cell(
    date: str,
    column: str = "PF_TABLE_DATE",
    table: str = "PF_TABLE_ITEMS",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    display: str = ":89",
    base_column: str = "PF_TABLE_TEXT",
    captured_value: str = "CELLAA",
    commit_partner_field: str = "PF_EDIT_STRING",
    commit_partner_value: str = "C90CMT",
    capture: str = "genuine-card90-table-20260617/traffic-selfcontained",
    manage_wm: bool = True,
    settle_sec: float = 1.0,
    from_year: int | None = None,
    open_link: str | None = None,
    column_title: str | None = None,
    cell_x: int | None = None,
    cell_y: int | None = None,
    row_offset: int = 28,
    prime: bool = True,
    foreground: str = "listreplay",
) -> dict[str, Any]:
    """Set a grid DATE cell to ``date`` (``DD.MM.YYYY``) on the ACTIVE row natively, with the cell located ON SCREEN
    (no hardcoded coordinates). A 1C date grid cell rejects text/keystroke SET (masked editor); it is settable only
    by MOUSE through the calendar picker. This tool: (1) protocol-activates the cell (the shipped table-cell
    ``write_block`` — activate+SET, no commit — so the inline date editor and its calendar dropdown button appear),
    (2) screenshots and LOCATES the calendar button by template-matching the shipped glyph (ImageMagick
    ``compare -subimage-search`` via ``locate_calendar_button``), (3) drives the calendar by mouse — click the
    dropdown, then the month, then the day — using the popup month-list / day-grid origins DERIVED from the localized
    button center (fixed deltas, ``calendar_month_cell`` / ``calendar_day_cell`` geometry), then commits (Return).
    Returns {column, requested_date, localized, button_xy, month_origin, day_origin, status, verified_by, screenshot,
    activation_screenshot}. When the button cannot be located it returns ``status="blocked"`` and does NOT click
    guessed coordinates; ``status="set"`` when the pick committed (the calendar closed) and ``"set_calendar_open"``
    if the calendar is still visible after the pick.

    YEAR is navigated when the target year differs from the cell's CURRENT year (the calendar opens on it): the ‹/›
    arrows step the month, so the year uses the «<year> ▼» dropdown (current at the top, current+k below; clicked by
    row, chained in steps of 3 for larger forward offsets). The current year = ``from_year`` if given, else today
    (correct for an EMPTY cell, which opens on today) — pass ``from_year`` for a populated cell whose year differs
    from today. Backward years (target < current) are not yet supported (the dropdown lists forward only) and return
    ``status="blocked"``.

    VERIFICATION is the SCREENSHOT: a mouse-set date cell has no protocol SET echo (the value enters via the
    calendar, not a wire SET) and the in-form value is not protocol-readable without a save, so the active cell
    showing the picked date in ``screenshot`` is the proof.

    REQUIRES an X display with the client laid out by a window manager (matchbox; started here when ``manage_wm``) so
    the cell/calendar geometry is stable, plus ``xdotool`` (XTEST mouse) and ImageMagick.

    CONFIG-AGNOSTIC path — pass ``open_link`` (a document's ``e1cib/data/Документ.X?ref=…`` ref) to set the date on
    ANY real document form's tabular date cell with NO per-form capture (no ``capture`` / write_block). The engine
    brings the form FOREGROUND, activates the cell ON SCREEN by double-clicking it — located from the date column's
    on-screen header ``column_title`` (e.g. "Дата", subimage-search; the form descriptor has no pixel bounds) or the
    explicit ``cell_x``/``cell_y`` — and reuses the same calendar pick. ``row_offset`` (≈ one grid row, 28 px) steps
    from the header to the first data row; ``column`` is the date column NAME (for the result).

    ``foreground`` selects how the form is brought to the active tab: ``"listreplay"`` (DEFAULT, fixture-FREE,
    config-agnostic) replays a genuine cold catalog-list-open sequence retargeted to ``open_link`` (no bundled
    fixture — works on any config); ``"fixture"`` is the legacy primer (the bundled fixture render-push frames +
    ``prime``). ``prime`` only applies to ``foreground="fixture"``."""
    try:
        normalized_date, d, m, y = _normalize_table_date_parts(date)
    except ValueError as exc:
        return {"column": column, "table": table, "requested_date": date, "localized": False,
                "committed": False, "status": "blocked", "reason": "invalid_date", "detail": str(exc)}
    backend = _display_backend()
    if open_link is not None:
        try:
            return _set_table_date_cell_open_link(
                date=normalized_date, open_link=open_link, column=column, table=table, column_title=column_title,
                cell_xy=(cell_x, cell_y) if cell_x is not None and cell_y is not None else None,
                row_offset=row_offset, host=host, port=port, display=display, manage_wm=manage_wm,
                settle_sec=settle_sec, from_year=from_year, prime=prime, foreground=foreground,
                backend=backend, date_parts=(d, m, y),
            )
        except client_display.DisplayBackendError as exc:
            return _display_backend_error("set_table_date_cell", exc)
    try:
        return _set_table_date_cell(
            date=normalized_date, column=column, table=table, base_column=base_column, captured_value=captured_value,
            commit_partner_field=commit_partner_field, commit_partner_value=commit_partner_value,
            host=host, port=port, display=display, capture=capture, manage_wm=manage_wm, settle_sec=settle_sec,
            from_year=from_year, backend=backend, date_parts=(d, m, y),
        )
    except client_display.DisplayBackendError as exc:
        return _display_backend_error("set_table_date_cell", exc)


@qa_tool()
@testclient_tool(phase="table_row_select")
def select_table_row(
    row_match: str,
    captured_row_match: str = "PF_ROW_002_TEXT",
    base_column: str = "PF_TABLE_TEXT",
    captured_value: str = "R2WROT",
    commit_partner_field: str = "PF_EDIT_STRING",
    commit_partner_value: str = "C90RC",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "genuine-card90-row2write-20260617/traffic-selfcontained",
) -> dict[str, Any]:
    """Position the active row of a table to the row whose column equals ``row_match`` natively. A native row-select
    is "find the row where <column> = <value>" (both length-prefixed strings in the genuine command); re-targeting
    the VALUE (fixed-width) selects a different row. Replays the ``capture`` setup (which selected a row by
    ``captured_row_match``) with the search value re-pointed to ``row_match`` so that row becomes ACTIVE. Returns
    {row_match, accepted}. Verify via `assert_form_value('PF_SELECTED_ROW_MARKER')` -> `PF_ROW_IDX_<n>:<marker>`
    (fixture OnActivateRow handler), or chain `set_table_cell(row_match=…)` to WRITE into the selected row."""
    template = derive_table_cell_write(
        resolve_capture_dir(capture, _repo_root()), base_column, captured_value,
        commit_partner_field=commit_partner_field, commit_partner_value=commit_partner_value,
    )
    return native_select_table_row(template, row_match, captured_row_match=captured_row_match, host=host, port=port)


def _open_list_navigation_asset_error(
    exc: protocol_introspection.NavigationAssetError,
    *,
    navigation_templates: str | None,
) -> dict[str, Any]:
    return {
        "ok": False,
        "error": "open-list-navigation-unavailable",
        "tool": "open_list",
        "phase": "open_list",
        "capability": "template-backed-open-list",
        "asset_class": exc.asset_class,
        "asset_selector": "explicit" if navigation_templates else "bundled-default",
        "reason": exc.reason_code,
        "protocol_write_attempted": False,
    }


def _open_list_from_prepared_navigation_assets(
    *,
    assets: protocol_introspection.NavigationAssets,
    catalog: str | None,
    base_link: str,
    host: str,
    port: int,
) -> dict[str, Any]:
    target_catalog = (catalog or "").strip()
    target_link = f"e1cib/list/{target_catalog}" if target_catalog else base_link
    opened = protocol_introspection.open_list_from_navigation_assets(
        assets,
        target_link,
        host=host,
        port=port,
        repo_root=_repo_root(),
    )
    if opened is None:
        return {
            "ok": False,
            "base_link": base_link,
            "target_link": target_link,
            "accepted": False,
            "opened": None,
            "navigation_method": "template-backed",
            "reason": "list-form-not-resolved",
        }
    caption, _secondary_frame, _managed_form = opened
    return {
        "ok": True,
        "base_link": base_link,
        "target_link": target_link,
        "accepted": True,
        "opened": caption,
        "navigation_method": "template-backed",
    }


def _prepare_open_list_before_endpoint(
    arguments: dict[str, Any],
) -> dict[str, Any] | Callable[[str, int], dict[str, Any]] | None:
    capture = arguments.get("capture")
    capture_selector = str(capture).strip() if capture is not None else ""
    if capture_selector:
        return None

    navigation_templates = arguments.get("navigation_templates")
    template_selector = navigation_templates or VALUE_READ_TEMPLATES
    try:
        assets = protocol_introspection.prepare_open_list_navigation_assets(
            manager_templates=template_selector,
            repo_root=_repo_root(),
        )
    except protocol_introspection.NavigationAssetError as exc:
        return _open_list_navigation_asset_error(exc, navigation_templates=navigation_templates)

    catalog = arguments.get("catalog")
    base_link = str(arguments.get("base_link") or "")

    def prepared_call(host: str, port: int) -> dict[str, Any]:
        return _open_list_from_prepared_navigation_assets(
            assets=assets,
            catalog=catalog,
            base_link=base_link,
            host=host,
            port=port,
        )

    return prepared_call


def _open_list_from_navigation_templates(
    *,
    catalog: str | None,
    base_link: str,
    host: str,
    port: int,
    navigation_templates: str | None,
) -> dict[str, Any]:
    prepared = _prepare_open_list_before_endpoint({
        "catalog": catalog,
        "base_link": base_link,
        "capture": None,
        "navigation_templates": navigation_templates,
    })
    if isinstance(prepared, dict):
        return prepared
    if prepared is None:
        raise RuntimeError("template-backed open_list did not prepare a navigation call")
    return prepared(host, port)


@qa_tool()
@testclient_tool(phase="open_list", before_endpoint=_prepare_open_list_before_endpoint)
def open_list(
    catalog: str | None = None,
    base_link: str = "e1cib/list/Справочник.Товары",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str | None = None,
    navigation_templates: str | None = None,
) -> dict[str, Any]:
    """Open a catalog/list window natively through ``e1cib/list/<path>``.

    Omitting ``capture`` (or passing a blank value) uses the released, version-selected bundled bootstrap and
    value-read navigation templates. All assets are loaded and structurally checked before a TestClient session
    opens; missing assets return ``open-list-navigation-unavailable`` with ``protocol_write_attempted=false``.

    A non-blank ``capture`` preserves the explicit capture-replay compatibility path. ``navigation_templates``
    optionally selects a controlled value-read template JSON for the default template-backed path. Returns the
    requested ``base_link``/``target_link``, the navigation method, and whether the target form resolved. A
    list-open has no business-data mutation or value read-back."""
    capture_selector = str(capture).strip() if capture is not None else ""
    if not capture_selector:
        return _open_list_from_navigation_templates(
            catalog=catalog,
            base_link=base_link,
            host=host,
            port=port,
            navigation_templates=navigation_templates,
        )
    template = derive_open_list(resolve_capture_dir(capture_selector, _repo_root()), base_link)
    return native_open_list(template, catalog, host=host, port=port)


@qa_tool()
@testclient_tool(phase="search_list")
def search_list(
    value: str,
    search_field: str = "ДенамическийСписокИерархияСтрокаПоиска",
    captured_value: str = "Молоко",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "search",
    refresh: bool = True,
) -> dict[str, Any]:
    """Filter a dynamic list by a SEARCH STRING natively. Types ``value`` into a dynamic list's search-string
    addition (``search_field``); the list filters incrementally (searchOnInput). A dynlist search rides the SAME
    UTF-16 value-SET buffer as a reference-name input (``e0 41 81 81 b7 <char-count><utf-16le><space pad>``)
    addressed at the SearchStringAddition element, so it composes from the same full-replay machinery as
    ``set_reference_field``: open the form (replay the genuine setup from ``capture``, which typed ``captured_value``
    into the search box) -> activate the dynlist -> SET the search string, re-targeting the UTF-16 string to
    ``value`` (fixed-width, bounded by the captured length). A list-filter has no clean value read-back — confirm
    with capture_screenshot (the visible rows narrow); ``echoed`` reports the search value echoed in the client
    responses. CURRENCY: ``refresh=True`` (default) forces an «Обновить»/F5 requery first so the search
    runs against a current list (a just-created record is filterable); ``refresh=False`` opts out. A search reports
    no row count, so this is refresh-only (no poll-until-stable); ``list_refresh`` records the refresh method.
    Returns {search_field, value, echoed, list_refresh}."""
    template = derive_search_list(resolve_capture_dir(capture, _repo_root()), search_field, captured_value)
    if refresh:
        method, note = _force_list_refresh()
    else:
        method, note = "none", "no refresh applied (refresh opt-out)"
    result = native_search_list(template, value, host=host, port=port)
    result["list_refresh"] = {"refresh": bool(refresh), "method": method}
    note_text, refresh_error = _normalize_display_note(note)
    if note_text:
        result["list_refresh"]["note"] = note_text
    if refresh_error:
        result["list_refresh"]["error"] = refresh_error
    return result


@qa_tool()
@testclient_tool(phase="set_list_view")
def set_list_view(
    mode: str,
    dynlist: str = "ДенамическийСписокИерархия",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "viewmode",
) -> dict[str, Any]:
    """Switch a dynamic list's VIEW MODE / grouping natively — the «Режим просмотра» toggle. ``mode`` is Список
    (flat) / Дерево (tree) / Иерархический (hierarchy) — also list/tree/hierarchical. The «Режим просмотра» entries
    are standard FORM BUTTONS (`<dynlist>Список` / `…Дерево` / `…ИерархическийСписок`); clicking one is the
    `…Button[<name>] 88 82 81 20 20 20` command family (the same invoke as the row ops / close-window) with the
    Button leaf encoded UTF-16LE (Cyrillic name — so this also exercises the UTF-16-aware command-click path that
    generalizes `click_command` to real configs). Replays the genuine click from ``capture`` (which clicked Список +
    ИерархическийСписок), re-targeting the Button leaf (Дерево = same-char-length UTF-16 retarget of Список; Список /
    Иерархический = verbatim). No value read-back — the list REPRESENTATION changes (verify with capture_screenshot).
    Returns {mode, button, accepted}."""
    return native_set_list_view(resolve_capture_dir(capture, _repo_root()), mode, dynlist, host=host, port=port)


@qa_tool()
@testclient_tool(phase="advanced_search")
def advanced_search(
    value: str,
    search_command: str = "ДенамическийСписокИерархияНайти",
    captured_value: str = "Молоко",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "advsearch",
) -> dict[str, Any]:
    """Filter a dynamic list via the «Расширенный поиск» (advanced-search) DIALOG natively. The reusable "drive a
    MODAL dialog" pattern: replay the genuine flow — open the form -> click «Расширенный поиск» (opens the standard
    `UniversalListFindExtForm` in a NEW window) -> SET its `Pattern` field -> click `Find` — with GUID rebinder
    rebinding the dialog window (the answer_dialog / open_card machinery) and the Pattern re-targeted to ``value``
    (UTF-16 buffer, fixed-width, bounded by the captured length). Searches the dialog's default field (the capture
    left FieldSelector at «Код»; targeting another field is a refinement). No clean value read-back — the list
    narrows (verify with capture_screenshot). Returns {search_command, value, echoed}."""
    template = derive_advanced_search(resolve_capture_dir(capture, _repo_root()), search_command, captured_value)
    return native_advanced_search(template, value, host=host, port=port)


@qa_tool()
@testclient_tool(phase="run_report")
def run_report(
    command: str = "PF_RUN_REPORT",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "report",
) -> dict[str, Any]:
    """Run a report / fill a ТабличныйДокумент natively. A report-run is a standard FORM-COMMAND click (the
    `click_command` family, `…Button[<command>] 88 82 81 20 20 20`); clicking PF_RUN_REPORT fills the form's
    spreadsheet attribute ON THE SERVER (cells PF_RPT_R1C1…R2C2) and sets PF_LAST_ACTION="PF_RUN_REPORT". Replays
    the genuine setup from ``capture`` + the command click. NOTE: the SPREADSHEET CELL CONTENT rides the wire as a
    1C-packed BINARY ТабличныйДокумент (.mxl) blob — NOT plain strings, NOT zlib/deflate. So reading individual cells
    capture-free is a deep .mxl-format decode (deferred — the in-client testing API's domain, e.g. «табличный
    документ … равен»); verify the produced spreadsheet with capture_screenshot (the cells render) or by reading the
    PF_LAST_ACTION marker. Returns {command, accepted}."""
    template = derive_command_click(resolve_capture_dir(capture, _repo_root()), command)
    return native_click_command(template, None, host=host, port=port)


@qa_tool()
@testclient_tool(phase="spreadsheet_read")
def read_spreadsheet_cell(
    address: str = "R1C1",
    field: str = "PF_REPORT",
    captured_address: str = "R1C1",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "cellread",
) -> dict[str, Any]:
    """Read a spreadsheet (ТабличныйДокумент) CELL by address natively. Reading a cell is an IN-CLIENT method on the
    live object, NOT a binary .mxl wire-decode: the manager NEVER receives the cell text in the binary form-render
    (only a 20-byte handle); a TARGETED read («перейти к ячейке <addr>») makes the client evaluate the cell and
    return its value as a small PLAIN string. Replays the genuine flow (open form -> run the report -> navigate to
    the cell) re-targeting the ``address`` (R1C1 notation, ANY length — the navigate frame resizes) and parses the
    value from the client response with the value-read path (the cell value rides the SAME `0x9a<len><utf-8>` shape).
    Live-verified across address lengths (R1C1->PF_RPT_R1C1, R1C12->PF_RPT_R1C12, R12C12->PF_RPT_R12C12). Returns
    {field, address, value}."""
    template = derive_read_spreadsheet_cell(resolve_capture_dir(capture, _repo_root()), field, captured_address)
    return native_read_spreadsheet_cell(template, address, host=host, port=port)


@qa_tool()
@testclient_tool(phase="choose_from_list")
def choose_from_list(
    value: str,
    base_command: str = "PF_SHOW_CHOICE_LIST",
    captured_value: str = "PF_CHOICE_B",
    message_prefix: str = "PF_CHOICE=",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "genuine-card96-choicelist-20260618/traffic",
) -> dict[str, Any]:
    """Pick a value from a ПоказатьВыборИзСписка modal natively. The flow: open the form, click the command that
    raises the choice list (``base_command``), then PICK ``value`` (a list-item VALUE NAME, e.g. PF_CHOICE_A/B/C).
    The pick is the choose tag ``e0 4b 53`` + the length-prefixed value at the ManagedForm path — the same
    ``e0 4b 53`` family as a radio ``set_choice``, but addressed at the FORM (the popup reuses the window, so NO new
    SecondaryFrame to bind); only the value is re-targeted (``captured_value`` -> ``value``). Opens the form by
    replaying the genuine setup from ``capture`` (which clicked ``base_command`` and picked ``captured_value``). The
    result is a user message ``Сообщить(<message_prefix> + value)``, so commit is verified by scanning the responses
    for that ASCII marker. Returns {captured_value, value, accepted, committed, message}."""
    template = derive_choose_from_list(resolve_capture_dir(capture, _repo_root()), base_command, captured_value)
    return native_choose_from_list(template, value, message_prefix=message_prefix, host=host, port=port)


@qa_tool()
@testclient_tool(phase="answer_dialog")
def answer_dialog(
    raise_command: str = "PF_V4_WARNING",
    result_marker: str = "PF_V4_WARNING_ACK",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "genuine-card96-dialog-warn-20260618/traffic",
) -> dict[str, Any]:
    """Answer a 1C modal dialog (ПоказатьВопрос / ПоказатьПредупреждение) natively. Unlike a popup choice list
    (which reuses the form window), a real dialog opens a NEW top-level window — a fresh `SecondaryFrame` GUID per
    open. The genuine answer is a WINDOW-LEVEL command on that dialog frame (`…SecondaryFrame[<dlg>] 88 82 81` = the
    window's default action = ОК/Да), NOT a `Button` activate. This faithfully replays the genuine dialog session
    from ``capture`` (open form -> click ``raise_command`` -> the dialog opens -> the window-level answer);
    `GUID rebinder` learns the LIVE dialog GUID from the live open response and rebinds the captured one in the close
    command (the same first-appearance rebinding as the form window). Commit is confirmed by ``result_marker`` (the
    fixture's answer field, e.g. PF_V4_WARNING_ACK) appearing in the post-answer read-back. Returns {raise_command,
    result_marker, dialog_sf, committed}. NOTE: the WARNING (ОК) path is the default — the QUESTION (Да/Нет) answer
    is the same window-level mechanism with the appropriate raise_command/marker once captured."""
    template = derive_answer_dialog(resolve_capture_dir(capture, _repo_root()), raise_command, result_marker)
    return native_answer_dialog(template, host=host, port=port)


@qa_tool()
@testclient_tool(phase="reference_field")
def set_reference_field(
    value: str = "Корнет ЗАО",
    field: str = "Контрагент",
    captured_value: str = "Корнет ЗАО",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "genuine-card96-ref-20260618/traffic",
) -> dict[str, Any]:
    """Set a CatalogRef field to ``value`` (a catalog element NAME, e.g. "Пантера АО") natively. A reference
    InputField resolves a TYPED name to a ref (выбор по строке) on focus-change; the typed name rides the wire as
    `e0 41 81 81 b7 <char-count><utf-16le name><space pad>` (the value-SET family with a UTF-16 choice value). This
    faithfully replays the genuine reference-input session from ``capture`` (open form -> type ``captured_value``
    into ``field`` -> focus-change commit -> read-back), re-targeting the UTF-16 name to ``value``. Commit is
    confirmed by the resolved presentation reading back. Returns {field, value, committed}. CONSTRAINT: ``value``
    must currently be the SAME character length as ``captured_value`` (the field's edit buffer is length-fixed — same
    fixed-width limit as the string write; a variable-length ref name does not commit yet). Re-capture with a
    same-length name for other lengths."""
    template = derive_set_reference_field(resolve_capture_dir(capture, _repo_root()), field, captured_value)
    return native_set_reference_field(template, value, host=host, port=port)


@qa_tool()
@testclient_tool(phase="open_card")
def open_card(
    result_marker: str = "ФормаГруппы",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "genuine-card96-opencard-20260618/traffic",
) -> dict[str, Any]:
    """Open a record CARD by drilling into a catalog list row natively. Drilling into a list item opens the record's
    form in a NEW top-level window (a fresh SecondaryFrame, like a dialog). This faithfully replays the genuine
    navigation from ``capture`` (open the fixture form -> open the catalog list via a nav link -> «Изменить» the
    active row -> the card form opens). Each new window's per-open SecondaryFrame GUID is rebound by `GUID rebinder`
    automatically (first-appearance, like the dialog window — the same new-window machinery as answer_dialog).
    Opening is confirmed by ``result_marker`` (a card-specific UTF-16 string, e.g. the card form id "ФормаГруппы")
    reading back. Returns {result_marker, opened}. Opens the captured active row's card; to open a SPECIFIC row,
    precede with a row-select (compose with select_table_row)."""
    template = derive_open_card(resolve_capture_dir(capture, _repo_root()), result_marker)
    return native_open_card(template, host=host, port=port)


@qa_tool()
@testclient_tool(phase="close_window")
def close_window(
    window_ref: str = "e1cib/data/Справочник.Контрагенты",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "genuine-card96-windows3-20260618/traffic",
) -> dict[str, Any]:
    """Close a top-level window natively. close (and activate) are window-level commands:
    `…SecondaryFrame[<window>] 88 82 81` — the SAME family as the dialog close in answer_dialog, applied to any
    top-level window. This faithfully replays the genuine navigation from ``capture`` (open form -> open the catalog
    list -> drill a row -> the record card opens in a new window) then the window-level close on the active card;
    `GUID rebinder` rebinds the list/card window GUIDs as they appear (first-appearance, same machinery as open_card /
    answer_dialog), and the replay is truncated just before any subsequent close so ONLY the target window
    (``window_ref``, default the card's record data ref) is closed. Confirmed by the closed window's (live, rebound)
    SecondaryFrame being reported by the client BEFORE the close but gone AFTER it (``closed``), and the window
    behind it becoming active (``active_window_after``). Returns {window_ref, window_sf, live_window_sf, accepted,
    closed, active_window_after}. NOTE: replays the captured open-card->close flow, so it closes that card window; to
    close a different window, capture that flow (the window-level close mechanism is identical)."""
    template = derive_close_window(resolve_capture_dir(capture, _repo_root()), window_ref)
    return native_close_window(template, host=host, port=port)


@qa_tool()
@testclient_tool(phase="activate_window")
def activate_window(
    window_ref: str = "e1cib/app/Обработка.ФикстураПротоколаTestClient",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "genuine-card96-activate-20260618/traffic",
) -> dict[str, Any]:
    """Bring a buried top-level window to the front natively. activate and close are the SAME window-level command
    `…SecondaryFrame[<window>] 88 82 81`; the effect is contextual on z-order — applied to a BACKGROUND window it
    activates (brings forward), applied to the active window it closes it (see close_window). This faithfully replays
    the genuine navigation from ``capture`` (open the fixture form -> open the catalog list -> drill a row, so other
    windows cover the target) then the window-level command that raises the buried target (``window_ref``, default
    the fixture form's app ref); `GUID rebinder` rebinds the window GUIDs as they appear (first-appearance, same
    machinery as open_card / close_window). Confirmed by the target becoming the ACTIVE (last-reported) window — its
    (live, rebound) SecondaryFrame is the one in the final window-bearing client response (``activated``), the
    inverse of close_window. Returns {window_ref, window_sf, live_window_sf, accepted, activated,
    target_in_activate_resp}."""
    template = derive_activate_window(resolve_capture_dir(capture, _repo_root()), window_ref)
    return native_activate_window(template, host=host, port=port)


@qa_tool()
@testclient_tool(phase="read_user_messages")
def read_user_messages(
    expected: str = "",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "genuine-card96-choicelist-20260618/traffic",
) -> dict[str, Any]:
    """Read the user messages (`Сообщить` text / the "messages to user" panel) a form emits. This is the
    capture-free ASSERTION read for «нет сообщений пользователю» and for reading `Сообщить` output. The client
    reports the message panel in its responses as the envelope `cb 53 9a <byte-len> <UTF-8>`; this faithfully
    replays the genuine flow from ``capture`` (whatever raises the message — e.g. the choose-from-list /
    choose-from-menu callbacks) and decodes every message. Returns {messages, count, expected_found}. Pass
    ``expected`` to assert a specific message is present. NOTE: byte-length-prefixed UTF-8 — proven on ASCII and on a
    synthetic multibyte string; a real Cyrillic `Сообщить` should decode the same."""
    template = derive_read_user_messages(resolve_capture_dir(capture, _repo_root()), expected or None)
    return native_read_user_messages(template, host=host, port=port)


@qa_tool()
@testclient_tool(phase="choose_from_menu")
def choose_from_menu(
    value: str,
    base_command: str = "PF_SHOW_CHOICE_MENU",
    captured_value: str = "PF_MENU_1",
    message_prefix: str = "PF_MENU=",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "genuine-card96-menu-20260618/traffic",
) -> dict[str, Any]:
    """Pick an item from a ПоказатьВыборИзМеню popup menu natively. The popup menu is the wire TWIN of the choice
    list (``choose_from_list``): clicking ``base_command`` raises it, and the pick is the SAME ``e0 4b 53`` choose
    tag + the length-prefixed item VALUE NAME at the ManagedForm path (the popup reuses the form window — no new
    SecondaryFrame). Only the value is re-targeted (``captured_value`` -> ``value``, e.g. PF_MENU_1 -> PF_MENU_2).
    Opens the form by replaying the genuine setup from ``capture`` (which clicked ``base_command`` and picked
    ``captured_value``). The result is a user message ``Сообщить("PF_MENU=" + value)``, confirmed on the wire.
    Returns {captured_value, value, accepted, committed, message}."""
    template = derive_choose_from_list(resolve_capture_dir(capture, _repo_root()), base_command, captured_value)
    return native_choose_from_list(template, value, message_prefix=message_prefix, host=host, port=port)


@qa_tool()
@testclient_tool(phase="click_command")
def click_command(
    target_button: str | None = None,
    base_button: str = "PF_ADD_ROW",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "genuine-card90-addrow-20260617/traffic-selfcontained",
) -> dict[str, Any]:
    """Click a form-command BUTTON natively. A command click activates the `…Group[<bar>].Button[NAME]` element
    (`88 81 81 e1` command-execute) — the Button twin of switch_page / toggle_checkbox. Opens the form (replays the
    genuine setup from ``capture``, which clicked ``base_button``) and sends the genuine click re-targeted to
    ``target_button`` (the `Button` leaf; defaults to ``base_button``). A click has no value read-back — verify via a
    side-effect field (PF_LAST_ACTION) or capture_screenshot. Returns {base_button, target_button, accepted}."""
    template = derive_command_click(resolve_capture_dir(capture, _repo_root()), base_button)
    return native_click_command(template, target_button, host=host, port=port)


@qa_tool()
@testclient_tool(phase="add_table_row")
def add_table_row(
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = "genuine-card90-addrow-20260617/traffic-selfcontained",
) -> dict[str, Any]:
    """Add a persistent row to the fixture table natively. The standard «add row» discards an uncommitted empty row,
    so the fixture exposes a `PF_ADD_ROW` command that server-side appends a MARKED row (`PF_ROW_ADDED_<n>` /
    `PF_ADDED_TEXT`), activates it, and sets PF_LAST_ACTION. This clicks `PF_ADD_ROW` capture-free (=
    `click_command('PF_ADD_ROW')`). Verify via assert_form_value('PF_LAST_ACTION')=='PF_ADD_ROW' /
    'PF_SELECTED_ROW_MARKER' or capture_screenshot. Returns {base_button, target_button, accepted}."""
    template = derive_command_click(resolve_capture_dir(capture, _repo_root()), "PF_ADD_ROW")
    return native_click_command(template, None, host=host, port=port)


# --- Card 97 #1: table row operations (delete / move up-down / copy) ---------------------------------------
# The fixture exposes custom commands PF_DELETE_ROW / PF_MOVE_ROW_UP / PF_MOVE_ROW_DOWN / PF_COPY_ROW that act
# on the ACTIVE row of PF_TABLE_ITEMS (ДанныеФормыКоллекция.Удалить/Сдвинуть/Вставить) and refresh the
# PF_TABLE_SNAPSHOT read-back marker (`PF_TABLE[<count>]=<marker>|<marker>…`). All four are the same
# `…Group[PF_COMMAND_BAR_MAIN].Button[NAME]` command invoke, so they replay from ONE genuine capture: the
# combined connect+open+clicks capture's FIRST click (PF_COPY_ROW) carries the form-open SETUP, and
# click_command retargets the Button leaf to the wanted command. Live-proven 2026-06-19 (DB-free, form-state):
# COPY -> PF_TABLE[4]=…|PF_ROW_001_COPY|…  ·  DELETE -> PF_TABLE[2]  ·  MOVE_DOWN -> [002|001|003].
_ROWOPS_CAPTURE = "genuine-card97-rowops-combined-20260619/traffic-selfcontained"
_ROWOPS_BASE_BUTTON = "PF_COPY_ROW"


@qa_tool()
@testclient_tool(phase="delete_table_row")
def delete_table_row(
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = _ROWOPS_CAPTURE,
) -> dict[str, Any]:
    """Delete the ACTIVE table row natively. Clicks the fixture's `PF_DELETE_ROW` command
    (`ДанныеФормыКоллекция.Удалить` on the active row of `PF_TABLE_ITEMS`), capture-free, by replaying the genuine
    `PF_COPY_ROW` click (its form-open setup) retargeted to the `PF_DELETE_ROW` `Button` leaf. Example: baseline
    [PF_ROW_001|PF_ROW_002|PF_ROW_003], active row 1 ->
    `PF_TABLE_SNAPSHOT`=`PF_TABLE[2]=PF_ROW_002|PF_ROW_003`. The deletion is session-local form state (reset on a
    fresh form-open), so verify in the SAME session via assert_form_value('PF_TABLE_SNAPSHOT') /
    ('PF_LAST_ACTION'=='PF_DELETE_ROW') or capture_screenshot. Select the target row first with select_table_row.
    Returns {base_button, target_button, accepted}."""
    template = derive_command_click(resolve_capture_dir(capture, _repo_root()), _ROWOPS_BASE_BUTTON)
    return native_click_command(template, "PF_DELETE_ROW", host=host, port=port)


@qa_tool()
@testclient_tool(phase="move_table_row")
def move_table_row(
    direction: str = "up",
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = _ROWOPS_CAPTURE,
) -> dict[str, Any]:
    """Move the ACTIVE table row up or down natively. ``direction`` in {"up","down"} clicks the fixture's
    `PF_MOVE_ROW_UP` / `PF_MOVE_ROW_DOWN` command (`ДанныеФормыКоллекция.Сдвинуть(±1)` on the active row, no-op at
    the table boundary), capture-free, by replaying the genuine `PF_COPY_ROW` click retargeted to the move `Button`
    leaf. Example: baseline active row 1 + "down" ->
    `PF_TABLE_SNAPSHOT`=`PF_TABLE[3]=PF_ROW_002|PF_ROW_001|PF_ROW_003`. Session-local form state — verify in the SAME
    session via assert_form_value('PF_TABLE_SNAPSHOT') / ('PF_LAST_ACTION'). Select the target row first with
    select_table_row. Returns {base_button, target_button, accepted}."""
    button = {"up": "PF_MOVE_ROW_UP", "down": "PF_MOVE_ROW_DOWN"}.get(direction.strip().lower())
    if button is None:
        raise ValueError(f"direction must be 'up' or 'down', got {direction!r}")
    template = derive_command_click(resolve_capture_dir(capture, _repo_root()), _ROWOPS_BASE_BUTTON)
    return native_click_command(template, button, host=host, port=port)


@qa_tool()
@testclient_tool(phase="copy_table_row")
def copy_table_row(
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = _ROWOPS_CAPTURE,
) -> dict[str, Any]:
    """Copy the ACTIVE table row natively. Clicks the fixture's `PF_COPY_ROW` command
    (`ДанныеФормыКоллекция.Вставить` a copy of the active row right below it, marker suffixed `_COPY`, made active),
    capture-free, by replaying the genuine `PF_COPY_ROW` click (the identity case — no Button-leaf retarget).
    Example: baseline active row 1 ->
    `PF_TABLE_SNAPSHOT`=`PF_TABLE[4]=PF_ROW_001|PF_ROW_001_COPY|PF_ROW_002|PF_ROW_003`. Session-local form state —
    verify in the SAME session via assert_form_value('PF_TABLE_SNAPSHOT') / ('PF_LAST_ACTION'=='PF_COPY_ROW'). Select
    the target row first with select_table_row. Returns {base_button, target_button, accepted}."""
    template = derive_command_click(resolve_capture_dir(capture, _repo_root()), _ROWOPS_BASE_BUTTON)
    return native_click_command(template, "PF_COPY_ROW", host=host, port=port)


_MULTISELECT_CAPTURE = "genuine-card97-multiselect-capture-20260619/traffic-selfcontained"


@qa_tool()
@testclient_tool(phase="select_all_table_rows")
def select_all_table_rows(
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture: str = _MULTISELECT_CAPTURE,
) -> dict[str, Any]:
    """Select ALL rows of the table natively (multi-select). Multi-row select IS protocol-drivable: the genuine
    «выделяю все строки» step is a TABLE-level command invoke addressed at the `…Table[PF_TABLE_ITEMS]` element (tail
    `88 82 81 20 20 20`, the same command family as the row-op buttons / window commands — NOT OS input), so it
    replays from a connect+open+select-all capture and fires (accepted). CAVEAT — read-back boundary: the
    multi-selection (`Элементы.PF_TABLE_ITEMS.ВыделенныеСтроки`) is TRANSIENT table-focus UI state. Any SEPARATE
    focus-changing protocol command (e.g. clicking PF_REFRESH_SELECTION to read it) collapses it back to the active
    row — confirmed identically in genuine AND replay (both read `PF_SEL[1]=<active>`), i.e. standard 1C focus
    behaviour, not a replay defect. So a live multi-selection is NOT capture-free-readable across commands; the
    non-collapsing read is the in-session testing API (`ТестируемаяТаблицаФормы.ПолучитьВыделенныеСтроки`), and
    composing select-then-act must capture the whole flow in ONE session. Returns {base_button, target_button,
    accepted}. (Arbitrary multi-select via Ctrl-toggle / deselect-all are the same Table-command family — capture on
    demand.)"""
    template = derive_table_command(resolve_capture_dir(capture, _repo_root()), "PF_TABLE_ITEMS")
    return native_click_command(template, None, host=host, port=port)


# --- Card 97 #5: waits + assertions (first-class assert + WaitForCondition) --------------------------------
def _parse_1c_number(text: str | None) -> Decimal | None:
    """Parse a 1C-formatted localized number to a Decimal, or None if not numeric. Handles the comma decimal
    separator (RU locale, e.g. "120,50"), space / NBSP / narrow-NBSP thousands separators ("1 234,50") and a
    leading sign. Card 97 #3: a value-read returns a number as its formatted display text, so a robust numeric
    assert must normalize that text rather than string-compare it."""
    if text is None:
        return None
    # drop all whitespace (plain space / NBSP / narrow-NBSP thousands separators) then RU comma -> dot
    t = re.sub(r"\s", "", text.strip()).replace(",", ".")
    if t in ("", "+", "-", "."):
        return None
    try:
        return Decimal(t)
    except InvalidOperation:
        return None


def _match_value(actual: str | None, expected: str, mode: str) -> bool:
    """Compare a read-back field value against ``expected`` under ``mode`` (equals | contains | regex | numeric).
    ``numeric`` parses both sides as 1C-formatted numbers and compares by value, so "120,50" == "120.5" == "120.50"
    (format/locale robust — card 97 #3)."""
    if actual is None:
        return False
    if mode == "equals":
        return actual == expected
    if mode == "contains":
        return expected in actual
    if mode == "regex":
        return re.search(expected, actual) is not None
    if mode == "numeric":
        a, e = _parse_1c_number(actual), _parse_1c_number(expected)
        return a is not None and e is not None and a == e
    raise ValueError(f"mode must be 'equals', 'contains', 'regex' or 'numeric', got {mode!r}")


_VALUE_READ_OPEN_FRAMES = protocol_introspection._VALUE_READ_OPEN_FRAMES
_VALUE_READ_FRAMES = protocol_introspection._VALUE_READ_FRAMES
_VALUE_READ_CAPTURED_FIELD = protocol_introspection._VALUE_READ_CAPTURED_FIELD
_SPLICE_PLACEHOLDER_GUID = protocol_introspection._SPLICE_PLACEHOLDER_GUID
_FIELD_QUERY_PATH_RE = protocol_introspection._FIELD_QUERY_PATH_RE
_DESCRIPTOR_FORM_PATH_RE = protocol_introspection._DESCRIPTOR_FORM_PATH_RE
_splice_header_no_form = protocol_introspection._splice_header_no_form
_retarget_read_to_groups = protocol_introspection._retarget_read_to_groups
_enumerate_capture_fields = protocol_introspection._enumerate_capture_fields
_live_descriptor_blob = protocol_introspection._live_descriptor_blob
_enumerate_live_fields = protocol_introspection._enumerate_live_fields
_normalize_data_ref_link = protocol_introspection._normalize_data_ref_link
_is_bare_create_data_link = protocol_introspection._is_bare_create_data_link
_splice_window_activate_command = protocol_introspection._splice_window_activate_command


def _read_field_value(
    field: str, *, host: str, port: int, capture_dir: str, manager_templates: str, groups: list[str] | None = None
) -> str | None:
    return protocol_introspection._read_field_value(
        field,
        host=host,
        port=port,
        capture_dir=capture_dir,
        manager_templates=manager_templates,
        groups=groups,
    )


@qa_tool()
@testclient_tool(phase="value_read")
def assert_form_value(
    field: str,
    expected: str,
    mode: str = "equals",
    groups: list[str] | None = None,
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture_dir: str = "tm-v1-ro-batchQ3",
    manager_templates: str = VALUE_READ_TEMPLATES,
) -> dict[str, Any]:
    """First-class ASSERT on a form field's live value."""
    try:
        host, port, attachment = _resolve_testclient_endpoint(host, port, phase="value_read")
    except ConnectionError as exc:
        return _attach_tool_error("assert_form_value", "attach", exc, host=host, port=port)
    actual = _read_field_value(
        field,
        host=host,
        port=port,
        capture_dir=capture_dir,
        manager_templates=manager_templates,
        groups=groups,
    )
    result = {
        "field": field,
        "expected": expected,
        "actual": actual,
        "mode": mode,
        "passed": _match_value(actual, expected, mode),
    }
    if attachment is not None:
        result["attached_endpoint"] = attachment
    return result


@qa_tool()
@testclient_tool(phase="value_read")
def wait_for_form_value(
    field: str,
    expected: str,
    mode: str = "equals",
    timeout_sec: float = 10.0,
    interval_sec: float = 0.5,
    groups: list[str] | None = None,
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture_dir: str = "tm-v1-ro-batchQ3",
    manager_templates: str = VALUE_READ_TEMPLATES,
) -> dict[str, Any]:
    """Poll a form field's live value until it matches or the timeout elapses."""
    if timeout_sec < 0 or interval_sec <= 0:
        raise ValueError("timeout_sec must be >= 0 and interval_sec > 0")
    try:
        host, port, attachment = _resolve_testclient_endpoint(host, port, phase="value_read")
    except ConnectionError as exc:
        return _attach_tool_error("wait_for_form_value", "attach", exc, host=host, port=port)
    start = time.monotonic()
    deadline = start + timeout_sec
    polls = 0
    actual: str | None = None
    while True:
        actual = _read_field_value(
            field,
            host=host,
            port=port,
            capture_dir=capture_dir,
            manager_templates=manager_templates,
            groups=groups,
        )
        polls += 1
        if _match_value(actual, expected, mode):
            result = {
                "field": field,
                "expected": expected,
                "actual": actual,
                "mode": mode,
                "satisfied": True,
                "polls": polls,
                "elapsed_sec": round(time.monotonic() - start, 3),
            }
            if attachment is not None:
                result["attached_endpoint"] = attachment
            return result
        if time.monotonic() >= deadline:
            result = {
                "field": field,
                "expected": expected,
                "actual": actual,
                "mode": mode,
                "satisfied": False,
                "polls": polls,
                "elapsed_sec": round(time.monotonic() - start, 3),
            }
            if attachment is not None:
                result["attached_endpoint"] = attachment
            return result
        time.sleep(interval_sec)


def _open_bare_create_form_for_write(
    open_link: str, *, host: str, port: int,
) -> tuple[Any | None, dict[str, Any]]:
    return protocol_foreground.open_bare_create_form_for_write(
        open_link,
        host=host,
        port=port,
        foreground_form_by_link=_foreground_form_by_link,
    )


# Card 103 Wave 3 (live leg) — map an open_main_form step's object-type phrase (as the Gherkin transpiler
# captures it) to the e1cib nav-link prefix. Mirrors `qa_mcp.scenario.smoke._KINDS` but keyed by the otype
# phrase the open-main-form pattern yields (e.g. «основную форму справочника 'X'» → object_type="справочника").
# Link formats LIVE-VERIFIED on vanessa_client (card 106 broadening): catalogs/documents → `e1cib/list/…`;
# reports AND data processors → `e1cib/app/…` (card-106 broaden probe — `e1cib/command/…` does NOT open the form).
_OPEN_MAIN_FORM_PREFIX: dict[str, str] = {
    "справочника": "e1cib/list/Справочник.",
    "списка справочника": "e1cib/list/Справочник.",
    "документа": "e1cib/list/Документ.",
    "обработки": "e1cib/app/Обработка.",
    "отчёта": "e1cib/app/Отчет.",
    "отчета": "e1cib/app/Отчет.",
    "регистра сведений": "e1cib/list/РегистрСведений.",
    "регистра накопления": "e1cib/list/РегистрНакопления.",
}

# Card 106 change 4 — a NEW-object CREATE form opens via `e1cib/data/<Тип>.<Имя>` (no `?ref=`), LIVE-verified on
# vanessa_client: Справочник.Валюты → «Валюта (создание)», Документ.Заказ → «Заказ (создание)». Keyed by the
# object-type phrase the «я создаю новый …» pattern yields. Only catalogs/documents have a create form.
_CREATE_FORM_PREFIX: dict[str, str] = {
    "документ": "e1cib/data/Документ.",
    "справочник": "e1cib/data/Справочник.",
    "элемент справочника": "e1cib/data/Справочник.",
}


def _nav_link_for_step(step: Any) -> str | None:
    """Derive the e1cib nav-link a navigation/open step targets, config-agnostically. `open_list` carries the
    catalog in params (bare «Товары» → Справочник.Товары; an explicit «Тип.Имя» is used verbatim). `open_main_form`
    carries the object name (marker) + the object-type phrase (params["object_type"]). Returns None for an
    unmapped object type or a missing name (the step then reports it did not open)."""
    if step.kind == "open_list":
        # `open_list`'s marker is the literal "e1cib/list/" nav prefix sentinel, NOT a catalog — the catalog
        # lives in params (the «я открываю список 'X'» pattern always sets it).
        catalog = (step.params.get("catalog") or "").strip()
        if not catalog:
            return None
        return f"e1cib/list/{catalog}" if "." in catalog else f"e1cib/list/Справочник.{catalog}"
    if step.kind == "open_main_form":
        name = (step.marker or "").strip()
        prefix = _OPEN_MAIN_FORM_PREFIX.get((step.params.get("object_type") or "").strip().lower())
        if not name or not prefix:
            return None
        # A bare name takes the kind prefix; a fully-qualified «Тип.Имя» is opened as a list verbatim.
        return f"e1cib/list/{name}" if "." in name else f"{prefix}{name}"
    if step.kind == "open_create_form":
        name = (step.marker or "").strip()
        if step.params.get("requires_owner") or step.params.get("subordinate"):
            return None
        prefix = _CREATE_FORM_PREFIX.get((step.params.get("object_type") or "").strip().lower())
        if not name or not prefix:
            return None
        return f"e1cib/data/{name}" if "." in name else f"{prefix}{name}"
    return None


def _build_navigate_resolver() -> Any:
    """Card 103 Wave 3 (live leg): a `navigate_resolver(step, handle)` that EXECUTES an open on the live client.
    Derives the step's nav-link and opens the form by replaying the splice_navigate sequence on the bootstrapped
    handle (`_open_form_by_link` — the config-agnostic, fixture-free mechanism proven live on 8/8 forms via
    read_form_descriptor). Returns a result dict the runner turns into the step's pass/fail + preview.

    The splice header needs the value-read frame (218), which a read scenario's DEFAULT_TEMPLATES lacks. So the
    resolver loads its OWN value-read template set (VALUE_READ_TEMPLATES) lazily on the first open and passes it
    as ``splice_templates`` — open steps then work whatever ``manager_templates`` the read steps use."""
    cache: dict[str, Any] = {}

    def resolver(step: Any, handle: Any) -> dict[str, Any]:
        nav_link = _nav_link_for_step(step)
        if nav_link is None:
            return {"opened": False, "nav_link": None,
                    "reason": f"no nav-link for {step.kind!r} ({step.params})"}
        if "templates" not in cache:
            repo_root = _repo_root()
            cache["templates"] = ProtocolTemplates.load((repo_root / VALUE_READ_TEMPLATES).resolve())
        opened = _open_form_by_link(handle, nav_link, splice_templates=cache["templates"])
        if opened is None:
            return {"opened": False, "nav_link": nav_link}
        caption, secondary_frame, managed_form = opened
        return {"opened": True, "nav_link": nav_link, "caption": caption,
                "secondary_frame": secondary_frame, "managed_form": managed_form}

    return resolver


def _open_form_by_link(handle: Any, nav_link: str, splice_templates: Any = None) -> tuple[str, str, str] | None:
    return protocol_introspection._open_form_by_link(handle, nav_link, splice_templates=splice_templates)


_sweep_form_field_values = protocol_introspection._sweep_form_field_values
_resolve_open_form_by_caption = protocol_introspection._resolve_open_form_by_caption


def _read_open_form_once(
    *, host: str, port: int, caption_match: str,
    capture_dir: str, manager_templates: str,
) -> dict[str, Any]:
    return protocol_introspection._read_open_form_once(
        host=host,
        port=port,
        caption_match=caption_match,
        capture_dir=capture_dir,
        manager_templates=manager_templates,
    )


def _read_open_form_field_values(
    *, host: str, port: int, caption_match: str = "",
    capture_dir: str = "tm-v1-ro-batchQ3", manager_templates: str = VALUE_READ_TEMPLATES,
    retries: int = 4, retry_delay: float = 3.0,
) -> dict[str, Any]:
    attempts = max(1, retries)
    last: dict[str, Any] = {"opened": None, "fields": {}, "field_count": 0, "element_count": 0}
    for attempt in range(attempts):
        last = _read_open_form_once(
            host=host,
            port=port,
            caption_match=caption_match,
            capture_dir=capture_dir,
            manager_templates=manager_templates,
        )
        if last.get("field_count", 0) > 0:
            last["read_attempts"] = attempt + 1
            return last
        if attempt + 1 < attempts:
            time.sleep(retry_delay)
    last["read_attempts"] = attempts
    return last


def _values_equivalent(requested: str, value: str, *, allow_prefix: bool = False) -> bool:
    """Return whether a read-back value confirms a requested write.

    Text writes require normalized equality. Dates may read back with a time suffix
    (``30.06.2026`` -> ``30.06.2026 0:00:00``). Prefix acceptance for references is
    opt-in by field mode; otherwise ``123`` must not verify an old ``123456`` value.
    """
    req = (requested or "").strip()
    val = (value or "").strip()
    if len(req) < 2 or not val:
        return False
    req_cf, val_cf = req.casefold(), val.casefold()
    if req_cf == val_cf:
        return True
    if _looks_like_form_date(req) and val_cf.startswith(req_cf + " "):
        return True
    return bool(allow_prefix and val_cf.startswith(req_cf))


def _value_matches_readback(
    requested: str,
    readback_values: "list[str]",
    *,
    allow_prefix: bool = False,
) -> "str | None":
    """Return the read-back value that confirms ``requested`` was written, or None — the whole-form fallback when a
    field cannot be mapped to its own read-back value by label. A protocol value-read echoes the committed
    form-model value (reference → its presentation «Корнет ЗАО»; date → «30.06.2026 0:00:00»; text → the string).
    Card 125 #4 — verify by VALUE equivalence, not
    exact field name (the writer targets by on-screen LABEL, whose name differs from the descriptor field name)."""
    for value in readback_values:
        if _values_equivalent(requested, value, allow_prefix=allow_prefix):
            return value
    return None


def _readback_field_value(label: str, readback_fields: dict[str, str]) -> "tuple[bool, str | None]":
    """Best-effort map an on-screen LABEL to its OWN read-back field value so verification checks the RIGHT field
    (card 125 #4). Tries an exact field-name key, then a space-/case-insensitive match («Номер договора» → field
    «НомерДоговора», «Дата договора» → «ДатаДоговора»). Returns ``(resolved, value)``: ``resolved`` True with the
    field's value when the label maps to a UNIQUE field, else ``(False, None)`` so the caller falls back to the
    whole-form value-presence check."""
    if label in readback_fields:
        return True, readback_fields[label]
    norm = label.replace(" ", "").casefold()
    hits = [v for n, v in readback_fields.items() if n.replace(" ", "").casefold() == norm]
    if len(hits) == 1:
        return True, hits[0]
    return False, None


def _apply_readback_verification(results: "list[dict[str, Any]]", readback_fields: dict[str, str]) -> None:
    """Set each targeted write item's honest ``committed``/``readback_value`` from a protocol value-read of the open
    form (card 125 #4). ``committed`` is True only when the requested value is confirmed by the read-back —
    preferably against the field's OWN value (mapped by label, so a failed field's value cannot borrow an unrelated
    committed field's value), falling back to a whole-form value-presence check when the label does not map to a
    unique field. A field targeted on screen but not confirmed is ``committed=False`` (no false positives). Items
    that never located their label stay ``committed=False`` with their existing reason. Caveat: verification is by
    value presence, so a field whose committed value equals a form DEFAULT (notably a date that defaults to today)
    can read back as committed even when the write did not change it — write a non-default value to disambiguate."""
    readback_values = list(readback_fields.values())
    for item in results:
        if not item.get("targeted"):
            item.setdefault("committed", False)
            continue
        requested = str(item.get("value", ""))
        allow_prefix = item.get("field_mode") in {"date", "reference"}
        resolved, own = _readback_field_value(str(item.get("label", "")), readback_fields)
        if resolved:
            match = own if _values_equivalent(requested, own or "", allow_prefix=allow_prefix) else None
        else:
            match = _value_matches_readback(requested, readback_values, allow_prefix=allow_prefix)
        item["readback_value"] = match
        item["committed"] = match is not None
        if match is None:
            item.setdefault("reason", "requested value not found in the form value read-back")


def _read_form_descriptor(*, host: str, port: int, capture_dir: str, manager_templates: str, enumerate_live: bool = False, open_link: str | None = None) -> dict[str, Any]:
    return protocol_introspection._read_form_descriptor(
        host=host,
        port=port,
        capture_dir=capture_dir,
        manager_templates=manager_templates,
        enumerate_live=enumerate_live,
        open_link=open_link,
    )


@qa_tool()
@testclient_tool(phase="descriptor")
def read_form_descriptor(
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture_dir: str = "tm-v1-ro-batchQ3",
    manager_templates: str = VALUE_READ_TEMPLATES,
    gherkin: bool = True,
    enumerate_live: bool = False,
    open_link: str | None = None,
) -> dict[str, Any]:
    """Introspect a live form into a full element descriptor natively — the ``get_form_analysis`` equivalent. Opens
    the form then replays the genuine form-analysis QUERY sweep (a per-field value-read of every element) on one
    connection, decoding each element's name->value with ``extract_form_field_values`` (the canonical «стал равен»
    value; markers fa/9a single-byte, 97 UTF-16 checkbox Да/Нет, 8b short-number, 81 empty; ASCII + Cyrillic field
    names). Returns {fields {name: value}, field_count, queried}; with ``gherkin`` (default) also a Gherkin state
    block (``И элемент формы с именем 'X' стал равен "V"``). Both ASCII-named (``PF_*``) and **Cyrillic-named**
    fields are swept — Cyrillic group/leaf paths ride the ``0x97`` UTF-16 envelope, so e.g. the fixture's
    ``Контрагент`` / ``ПолеСоСпискомВыбораСтрока`` are read. SCOPE (honest): captures the EditField value surface —
    form DECORATIONS (static Label captions) are not field values and are omitted (the 3 ``PF_DECORATION_LABEL*`` are
    a separate Label-kind gap). The fixture descriptor is validated against a genuine analysis oracle.

    **``enumerate_live``:** by default the field list comes from ``capture_dir``'s value-read query paths (the
    one-time per-form capture). With ``enumerate_live=True`` the field list is enumerated LIVE off the open form by
    splice-replaying the genuine get_form_analysis descriptor query (``_enumerate_live_fields`` ->
    ``extract_descriptor_fields``), so introspection needs **NO per-form capture** for the field list. With
    ``open_link`` the engine OPENS that form by nav-link (e.g. ``"e1cib/list/Справочник.Контрагенты"``) — navigate +
    resolve its SecondaryFrame.ManagedForm, point the session at it — and introspects IT (no per-form capture at
    all): **introspect ANY form by its nav-link**. The descriptor query enumerates EditFields + Buttons/Tables/Groups;
    a list form has its content in a dynlist Table (few form-level EditFields).

    **The ``open_link`` open is CONFIG-AGNOSTIC** (no fixture required): the engine bootstraps to the bare desktop,
    window-lists the LIVE desktop MainFrame, and navigates straight to the target form — it does NOT open the suite
    fixture first. Every splice rides a header built with NO form open (``_splice_header_no_form``: the header's only
    live fields are the bootstrap ack_guid + sequence; the form GUIDs are after the marker the splice discards), and
    the navigate is retargeted onto the live desktop. So ``open_link`` introspects any form on ANY real config that
    has no suite fixture. Live-verified (fixture config: 46 EditFields incl. Cyrillic; Контрагенты opened +
    introspected to 79 elements with NO fixture open)."""
    try:
        result = _read_form_descriptor(
            host=host,
            port=port,
            capture_dir=capture_dir,
            manager_templates=manager_templates,
            enumerate_live=enumerate_live,
            open_link=open_link,
        )
    except ConnectionError as exc:
        return _attach_tool_error("read_form_descriptor", "attach", exc, host=host, port=port)
    except ValueError as exc:
        if not open_link and _is_missing_current_form_guid_error(exc):
            return _open_link_required_error("read_form_descriptor", "descriptor", host=host, port=port)
        raise
    except Exception as exc:
        attachment = current_application_context().attachment
        if isinstance(attachment, _AttachedTestClientContext) and (
            host, int(port)
        ) == (attachment.host, attachment.port):
            return _attach_tool_error("read_form_descriptor", "bootstrap", exc, host=host, port=port)
        raise
    if open_link and _descriptor_result_is_empty(result):
        result.update({
            "ok": False,
            "error": "descriptor-empty",
            "phase": "descriptor",
            "diagnostic": (
                "descriptor returned no opened form, fields or elements after bounded in-session navigation warmup"
            ),
            "warmup_attempts": max(1, _SETTINGS.descriptor_warmup_attempts),
        })
    if gherkin and "fields" in result:                         # the open_link path returns an element list, not values
        result["gherkin"] = "\n".join(
            f"\tИ элемент формы с именем '{name}' стал равен \"{value}\""
            for name, value in sorted(result["fields"].items())
        )
    return result


@qa_tool()
@testclient_tool(phase="descriptor")
def read_record(
    record_type: str,
    ref: str,
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    gherkin: bool = True,
    capture_dir: str = "tm-v1-ro-batchQ3",
    manager_templates: str = VALUE_READ_TEMPLATES,
) -> dict[str, Any]:
    """Read the actual object-attribute VALUES of an EXISTING POPULATED catalog/document RECORD natively (no
    per-form capture). Opens the record's form by its reference navigation link
    (``e1cib/data/<record_type>?ref=<ref>``) and value-reads every object attribute, decoding the canonical «стал
    равен» value (string / number / date / enum-presentation / UTF-16; ASCII + Cyrillic). ``record_type`` is the
    metadata full name (e.g. ``Справочник.Товары``); ``ref`` is the object's reference UUID — pass the natural
    dashed form (the OData ``Ref_Key`` / ``УникальныйИдентификатор``, e.g. ``a7a30aaf-321b-11dd-8d3a-000d8843cd1b``)
    and it is auto-encoded to the e1cib hex token, or pass the 32-hex token directly. Returns {opened, record_type,
    ref, fields {name: value}, field_count, elements, element_count} (+ a Gherkin state block when ``gherkin``).

    Live-verified (against OData): Товары/«Доставка» -> {Наименование: «Доставка», Код: «000000037», Вид:
    «Услуга», Родитель: «Услуги», …} (12 attribute values); Контрагенты/«Покупатели» -> {Наименование: «Покупатели»,
    Код: «000000002»}. The reference-link ref encoding (UUID groups g4·g5·g3·g2·g1) was decoded from the genuine
    open-card capture.

    COLD-CLIENT BOUNDARY: small / catalog-group (``ФормаГруппы``) record forms read reliably on a freshly launched
    client. A LARGE item form (e.g. an 80-element Товар card) materialises its attribute DATA only once the client
    PROCESS has fully opened a form at least once — the first cold open enumerates the element tree but the per-field
    reads echo with no value (``field_count`` 0 with ``element_count`` > 0). To read a large record cold, WARM the
    client first with one read of a DIFFERENT record (any small/group record), then read the target; re-opening the
    SAME record does not help (a 2nd same-caption window breaks newest-window detection). This is the same
    cold-client boundary the dynlist reads observe."""
    from .protocol.navigation import e1cib_data_link

    link = e1cib_data_link(record_type, ref)
    try:
        host, port, attachment = _resolve_testclient_endpoint(host, port, phase="descriptor")
    except ConnectionError as exc:
        return _attach_tool_error("read_record", "attach", exc, host=host, port=port)
    result = _read_form_descriptor(host=host, port=port, capture_dir=capture_dir,
                                   manager_templates=manager_templates, open_link=link)
    out = {"record_type": record_type, "ref": ref, "open_link": link,
           "opened": result.get("opened"), "fields": result.get("fields", {}),
           "field_count": result.get("field_count", 0),
           "elements": result.get("elements", []), "element_count": result.get("element_count", 0)}
    if attachment is not None:
        out["attached_endpoint"] = attachment
    if gherkin:
        out["gherkin"] = "\n".join(
            f"\tИ элемент формы с именем '{name}' стал равен \"{value}\""
            for name, value in sorted(out["fields"].items())
        )
    return out


_table_groups = protocol_introspection._table_groups


def _read_table_cell(*, host: str, port: int, capture_dir: str, manager_templates: str,
                     table: str, column: str, open_link: str | None = None) -> dict[str, Any]:
    return protocol_introspection._read_table_cell(
        host=host,
        port=port,
        capture_dir=capture_dir,
        manager_templates=manager_templates,
        table=table,
        column=column,
        open_link=open_link,
    )


@qa_tool()
@testclient_tool(phase="table_read")
def read_table_cell(
    table: str,
    column: str,
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    open_link: str | None = None,
    capture_dir: str = "tm-v1-ro-batchQ3",
    manager_templates: str = VALUE_READ_TEMPLATES,
) -> dict[str, Any]:
    """Read the CURRENT ROW's value of a form-TABLE cell natively — the ``ТаблицаФормы … ТекущиеДанные`` / «я
    запоминаю значение поля с именем …» equivalent. Addresses the table by name (``table``, e.g. ``PF_TABLE_ITEMS``)
    + the column BY NAME (``column``, e.g. ``PF_TABLE_TEXT``) and decodes the canonical «стал равен» value (string /
    number / date / UTF-16; ASCII + Cyrillic). Opens the suite fixture form by default; pass ``open_link``
    (``e1cib/list|data/…``) to read a cell on ANY form config-agnostically (the table's enclosing groups are
    discovered from the live descriptor). Returns {table, column, value, groups, opened?}. SCOPE: reads the CURRENT
    ROW — a form table populated on open has row 1 current (live-verified: fixture PF_TABLE_ITEMS ->
    PF_TABLE_TEXT="PF_ROW_001_TEXT", PF_TABLE_NUMBER="1,10"). A DYNLIST freshly opened by nav-link may have NO active
    current row yet (value None) — see ``read_list_column``."""
    try:
        host, port, attachment = _resolve_testclient_endpoint(host, port, phase="table_read")
    except ConnectionError as exc:
        return _attach_tool_error("read_table_cell", "attach", exc, host=host, port=port)
    try:
        result = _read_table_cell(host=host, port=port, capture_dir=capture_dir, manager_templates=manager_templates,
                                  table=table, column=column, open_link=open_link)
    except ValueError as exc:
        if not open_link and _is_missing_current_form_guid_error(exc):
            return _open_link_required_error("read_table_cell", "table_read", host=host, port=port)
        raise
    if attachment is not None:
        result["attached_endpoint"] = attachment
    return result


def _descriptor_table_names(descriptor: dict[str, Any]) -> list[str]:
    seen: list[str] = []
    for element in descriptor.get("elements") or []:
        if not isinstance(element, dict):
            continue
        if element.get("kind") != "Table":
            continue
        name = str(element.get("name") or "")
        if name and name not in seen:
            seen.append(name)
    return seen


def _descriptor_is_empty(descriptor: dict[str, Any]) -> bool:
    """A cold-client / not-opened descriptor: no opened form AND no elements. A genuinely empty
    catalog still exposes a Table element, so this only matches a form that never rendered (e.g. a
    heavy configuration still warming up right after client launch)."""
    return not (descriptor.get("elements") or []) and not descriptor.get("opened")


def _metadata_leaf_from_open_link(open_link: str) -> str | None:
    target = open_link.split("?", 1)[0].rstrip("/").rsplit("/", 1)[-1]
    if "." in target:
        return target.rsplit(".", 1)[-1] or None
    return target or None


def _list_table_diagnostic(
    error: str,
    *,
    open_link: str,
    requested_table: str | None,
    available_tables: list[str],
    reason: str,
    detail: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "ok": False,
        "error": error,
        "phase": "list_read",
        "open_link": open_link,
        "requested_table": requested_table,
        "available_tables": available_tables,
        "reason": reason,
    }
    if detail:
        result["detail"] = detail
    if extra:
        result.update(extra)
    return result


def _resolve_list_table_for_read(
    *,
    host: str,
    port: int,
    open_link: str,
    requested_table: str | None = None,
    descriptor_capture_dir: str = "tm-v1-ro-batchQ3",
    manager_templates: str = VALUE_READ_TEMPLATES,
) -> tuple[str | None, dict[str, Any]]:
    attempts = max(1, _SETTINGS.descriptor_warmup_attempts)
    delay = max(0.0, _SETTINGS.descriptor_warmup_delay_sec)
    descriptor: dict[str, Any] = {}
    warmup_retries = 0
    for attempt in range(1, attempts + 1):
        try:
            descriptor = _read_form_descriptor(
                host=host,
                port=port,
                capture_dir=descriptor_capture_dir,
                manager_templates=manager_templates,
                enumerate_live=True,
                open_link=open_link,
            )
        except Exception as exc:  # noqa: BLE001 - table resolution is reported as a list-read diagnostic
            if is_manager_handshake_drift_error(exc):
                drift = manager_handshake_drift_diagnostic(exc)
                return None, _list_table_diagnostic(
                    "manager-handshake-moved",
                    open_link=open_link,
                    requested_table=requested_table,
                    available_tables=[],
                    reason=(
                        "live manager handshake did not match the selected capture; "
                        "the list was not read"
                    ),
                    detail=f"{type(exc).__name__}: {exc}",
                    extra={"handshake_drift": drift},
                )
            return None, _list_table_diagnostic(
                "list-table-unresolved",
                open_link=open_link,
                requested_table=requested_table,
                available_tables=[],
                reason="list table could not be resolved from the live form descriptor; the list was not read",
                detail=f"{type(exc).__name__}: {exc}",
            )
        # A descriptor with no opened form AND no elements is a cold client whose managed form is
        # not ready yet (a heavy configuration warming up after launch), not a genuinely empty list
        # (a real empty catalog still exposes a Table element). Retry briefly before giving up.
        if not _descriptor_is_empty(descriptor) or attempt >= attempts:
            break
        warmup_retries = attempt
        if delay > 0:
            time.sleep(delay)

    tables = _descriptor_table_names(descriptor)
    meta: dict[str, Any] = {
        "source": "descriptor",
        "opened": descriptor.get("opened"),
        "available_tables": tables,
        "requested_table": requested_table,
    }
    if warmup_retries:
        meta["descriptor_warmup_retries"] = warmup_retries
    if requested_table:
        if requested_table in tables:
            return requested_table, meta
        return None, _list_table_diagnostic(
            "list-table-not-found",
            open_link=open_link,
            requested_table=requested_table,
            available_tables=tables,
            reason=(
                f"requested table {requested_table!r} is not present in the live form descriptor; "
                "the list was not read"
            ),
        )
    if len(tables) == 1:
        return tables[0], meta

    leaf = _metadata_leaf_from_open_link(open_link)
    if leaf and leaf in tables:
        meta["selection_reason"] = "metadata-name-match"
        return leaf, meta
    if "Список" in tables:
        meta["selection_reason"] = "legacy-table-present"
        return "Список", meta
    if not tables:
        if _descriptor_is_empty(descriptor):
            return None, _list_table_diagnostic(
                "list-table-unresolved",
                open_link=open_link,
                requested_table=requested_table,
                available_tables=[],
                reason=(
                    f"the live form descriptor was empty after {attempts} attempt(s) — the client "
                    "form may still be warming up (heavy configuration) or the link did not open a "
                    "list; the list was not read"
                ),
                extra={"descriptor_empty": True, "warmup_attempts": attempts},
            )
        return None, _list_table_diagnostic(
            "list-table-unresolved",
            open_link=open_link,
            requested_table=requested_table,
            available_tables=[],
            reason="the live form descriptor did not expose any Table elements; the list was not read",
        )
    return None, _list_table_diagnostic(
        "list-table-ambiguous",
        open_link=open_link,
        requested_table=requested_table,
        available_tables=tables,
        reason="multiple descriptor tables are available and no primary list table could be selected; pass table explicitly",
    )


@qa_tool()
@testclient_tool(phase="list_read")
def read_list_column(
    column: str,
    open_link: str,
    table: str | None = None,
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture_dir: str = "listform-read",
    refresh: bool = True,
) -> dict[str, Any]:
    """Read the CURRENT (first) ROW's value of a dynamic-list (dynlist) column natively — the «Я открываю основную
    форму списка справочника … + перехожу к первой строке + я запоминаю значение поля с именем 'X'» equivalent for a
    catalog LIST form. Opens the list at ``open_link`` (e.g. ``e1cib/list/Справочник.Товары``), positions to the
    first row, and reads ``column`` (e.g. ``Наименование`` / ``Код``) of the resolved dynlist table. By default
    the table is resolved from the live descriptor (single table -> that table; metadata-name/legacy ``Список``
    matches when needed); pass ``table`` to select explicitly. Returns {table, column, nav_link, value,
    captured_value, list_refresh, table_resolution}.

    MECHANISM: a FAITHFUL FULL-SEQUENCE replay of a genuine list-form read (navigate -> activate -> render/data-load
    -> position -> read), with ``GUID rebinder`` rebinding the per-session window GUIDs and the nav-link + column
    re-targeted in-frame. (A piecemeal splice does NOT work — the dynlist needs the interaction-ready open state a
    splice cannot reach; use ``read_table_cell`` for FORM tables, where row 1 is current on open.) Live-verified
    (against OData): Товары/Наименование->«Обувь», Товары/Код->«000000001», Контрагенты/Наименование->«Покупатели»,
    Валюты/Наименование->«EUR». CURRENCY: a dynamic list is async/eventually-consistent, so
    ``refresh=True`` (default) forces an «Обновить»/F5 requery and polls-until-stable before reporting, so a
    ``value=None`` only ever means a genuinely empty cell — never a not-yet-loaded list; ``refresh=False`` opts out
    (records "no refresh applied") for absence assertions. ``list_refresh`` records the refresh method + poll
    outcome. Table-resolution failures return structured ``list-table-*`` diagnostics and do NOT run a wrong-table
    replay or call the list genuinely empty."""
    from .protocol.native_write import derive_read_list_column, read_list_column_replay

    try:
        host, port, attachment = _resolve_testclient_endpoint(host, port, phase="list_read")
    except ConnectionError as exc:
        return _attach_tool_error("read_list_column", "attach", exc, host=host, port=port)
    resolved_table, table_meta = _resolve_list_table_for_read(
        host=host, port=port, open_link=open_link, requested_table=table)
    if resolved_table is None:
        if attachment is not None:
            table_meta["attached_endpoint"] = attachment
        return table_meta
    descriptor_swept = _cold_state_sweep()
    template = derive_read_list_column(resolve_capture_dir(capture_dir, _repo_root()))
    out, fresh = _ensure_list_fresh(
        read_once=lambda: read_list_column_replay(
            template, open_link=open_link, column=column, table=resolved_table, host=host, port=port),
        count_of=lambda o: 0 if o.get("value") is None else 1,
        refresh=refresh,
    )
    result = {"table": resolved_table, "column": out["column"], "nav_link": out["nav_link"],
              "value": out["value"], "captured_value": out["captured_value"],
              "list_refresh": _list_refresh_summary(fresh),
              "table_resolution": table_meta}
    if descriptor_swept:
        result["descriptor_clean_state_swept"] = True
    if fresh.get("clean_state_swept"):
        result["clean_state_swept"] = True
    if out["value"] is None:
        result["reason"] = _list_zero_reason_after_table_resolution(
            refresh=refresh,
            refresh_method=fresh["refresh_method"],
            swept=fresh.get("clean_state_swept", False),
            descriptor_swept=descriptor_swept,
            refresh_error=fresh.get("refresh_error"),
            sweep_error=fresh.get("sweep_error"),
        )
    _mark_uncertain_zero_list_read(
        result,
        tool="read_list_column",
        zero_data=out["value"] is None,
        refresh=refresh,
        fresh=fresh,
        descriptor_swept=descriptor_swept,
    )
    if attachment is not None:
        result["attached_endpoint"] = attachment
    return result


@qa_tool()
@testclient_tool(phase="list_read")
def read_list_row(
    open_link: str,
    columns: list[str],
    where: dict[str, str] | None = None,
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture_dir: str = "listform-read",
    refresh: bool = True,
) -> dict[str, Any]:
    """Read SEVERAL columns of a dynamic-list row in ONE call. Opens the list at ``open_link`` (e.g.
    ``e1cib/list/Справочник.Товары``) and reads each name in ``columns`` (e.g. ``["Код", "Наименование"]``) of the
    standard dynlist table ``Список``. Returns {table, nav_link, row: {column: value}, list_refresh} (+ ``where``
    when given).

    ``where`` selects the ROW: omit it to read the FIRST (current) row; pass a single ``{column: value}`` (e.g.
    ``{"Наименование": "Молоко"}``) to position the list to the row WHERE column == value first — the «в таблице
    "Список" я перехожу к строке: | col | value |» equivalent — then read THAT row. The where-row path is a faithful
    full-sequence replay of a genuine DYNLIST go-to-row-by-value capture (a splice of the FORM-table «перехожу к
    строке» onto a live dynlist did NOT reposition; the full-sequence replay does), value retargeted in-frame;
    live-verified on Товары (Наименование=Молоко -> Код 000000026 vs OData). Matching by «Наименование» is the
    verified path. One row read per fresh ``launch_test_client`` (the cold-client boundary), reading all requested
    columns inside the one materialised session (message-id kept, sequence bumped). CURRENCY:
    ``refresh=True`` (default) forces an «Обновить»/F5 requery + poll-until-stable so an all-None row is only ever a
    genuinely empty row, not a not-yet-loaded list; ``refresh=False`` opts out. For iterating every row use
    ``read_list_grid``; ``read_list_column`` for a single cell; ``read_table_cell`` for FORM tables."""
    try:
        host, port, attachment = _resolve_testclient_endpoint(host, port, phase="list_read")
    except ConnectionError as exc:
        return _attach_tool_error("read_list_row", "attach", exc, host=host, port=port)
    row_count = lambda o: 0 if all(v is None for v in (o.get("row") or {}).values()) else 1  # noqa: E731
    if where:
        if len(where) != 1:
            raise ValueError("where must be a single {column: value}, e.g. {'Наименование': 'Молоко'}")
        ((wcol, wval),) = where.items()
        from .protocol.native_write import read_list_row_by_value_replay

        cap = resolve_capture_dir("rowbyvalue", _repo_root())
        out, fresh = _ensure_list_fresh(
            read_once=lambda: read_list_row_by_value_replay(
                cap, where_value=wval, where_column=wcol, open_link=open_link, columns=columns, host=host, port=port),
            count_of=row_count,
            refresh=refresh,
        )
        result = {"table": "Список", "nav_link": out["nav_link"], "where": out["where"], "row": out["row"],
                  "list_refresh": _list_refresh_summary(fresh)}
        if fresh.get("clean_state_swept"):
            result["clean_state_swept"] = True
        zero = row_count(out) == 0
        if zero:
            result["reason"] = _list_zero_reason(
                refresh=refresh,
                refresh_method=fresh["refresh_method"],
                swept=fresh.get("clean_state_swept", False),
                refresh_error=fresh.get("refresh_error"),
                sweep_error=fresh.get("sweep_error"),
            )
        _mark_uncertain_zero_list_read(
            result,
            tool="read_list_row",
            zero_data=zero,
            refresh=refresh,
            fresh=fresh,
        )
        if attachment is not None:
            result["attached_endpoint"] = attachment
        return result

    from .protocol.native_write import derive_read_list_column, read_list_row_replay

    template = derive_read_list_column(resolve_capture_dir(capture_dir, _repo_root()))
    out, fresh = _ensure_list_fresh(
        read_once=lambda: read_list_row_replay(template, open_link=open_link, columns=columns, host=host, port=port),
        count_of=row_count,
        refresh=refresh,
    )
    result = {"table": "Список", "nav_link": out["nav_link"], "row": out["row"],
              "list_refresh": _list_refresh_summary(fresh)}
    if fresh.get("clean_state_swept"):
        result["clean_state_swept"] = True
    zero = row_count(out) == 0
    if zero:
        result["reason"] = _list_zero_reason(
            refresh=refresh,
            refresh_method=fresh["refresh_method"],
            swept=fresh.get("clean_state_swept", False),
            refresh_error=fresh.get("refresh_error"),
            sweep_error=fresh.get("sweep_error"),
        )
    _mark_uncertain_zero_list_read(
        result,
        tool="read_list_row",
        zero_data=zero,
        refresh=refresh,
        fresh=fresh,
    )
    if attachment is not None:
        result["attached_endpoint"] = attachment
    return result


def _display_backend_error_result(tool: str, exc: Exception) -> dict[str, Any]:
    if isinstance(exc, client_display.DisplayBackendError):
        return exc.to_result(tool, remote_client=_display_remote_client_enabled())
    return {
        "ok": False,
        "error": "display-backend-error",
        "tool": tool,
        # Generic transport/decoder exceptions can also echo credentials or
        # private configuration; their prose is not a public diagnostic.
        "detail": "display backend request failed",
        "mode": "remote-client" if _display_remote_client_enabled() else "local",
    }


def _display_error_note(error: dict[str, Any]) -> str:
    code = str(error.get("error") or "display-backend-error")
    detail = str(error.get("detail") or "display backend primitive failed")
    note = f"{code}: {detail}"
    if error.get("install_command"):
        note += f" Install/configure: {error['install_command']}"
    return note


def _normalize_display_note(note: Any) -> tuple[str | None, dict[str, Any] | None]:
    if note is None:
        return None, None
    if isinstance(note, dict):
        return _display_error_note(note), note
    text = str(note)
    return (text if text else None), None


def _normalize_sweep_result(result: Any) -> tuple[bool, dict[str, Any] | None]:
    if isinstance(result, tuple) and len(result) == 2:
        swept, error = result
        return bool(swept), error if isinstance(error, dict) else None
    return bool(result), None


def _cold_state_sweep(times: int = 8, settle_sec: float = 0.4, *, return_error: bool = False) -> bool | tuple[bool, dict[str, Any] | None]:
    """Collapse accumulated form tabs to the start page before a cold-replay read (best-effort, never raises).

    The cold-replay list reads assume a CLEAN desktop: with pre-existing tabs the GUID rebinder mis-binds the
    window GUIDs and the replay surfaces a stale tab, so the read comes back empty (a silent 0 rows that looks
    like an empty list). Escape closes the active form (list/object forms just close; the start page can't be
    closed), so a bounded Escape sweep collapses any accumulated tabs — config-agnostic + idempotent on an
    already-clean client (the SAME clean-working-area machinery the write-by-label foreground uses). Needs a
    display backend: local X11 in model A, or the host display agent (QA_MCP_HOST_AGENT, focusing
    QA_MCP_HOST_AGENT_WINDOW) in model B. A no-op returning False when no backend is reachable — robustness
    must never break the read."""
    try:
        backend = _display_backend()
    except Exception as exc:  # noqa: BLE001
        error = _display_backend_error_result("cold_state_sweep", exc)
        return (False, error) if return_error else False
    display = os.environ.get("DISPLAY") or ":89"  # model A: the X display; model B (host agent) ignores it
    swept = False
    for _ in range(times):
        try:
            backend.send_keys(["Escape"], display=display, settle_sec=settle_sec)
            swept = True
        except Exception as exc:  # noqa: BLE001
            error = _display_backend_error_result("cold_state_sweep", exc)
            return (swept, error) if return_error else swept
    return (swept, None) if return_error else swept


def _force_list_refresh(settle_sec: float = 0.4) -> tuple[str, str | dict[str, Any] | None]:
    """Force a dynamic-list requery so a just-created record becomes visible (card 125 Change 5).

    A dynamic list is async/eventually-consistent: a record committed a moment ago is not in the list result
    until the list query re-runs. Prefer a protocol replay of the list form's «Обновить»/F5 command (deterministic,
    no OS-key/focus dependency); no genuine «Обновить» capture exists yet, so fall back to an OS-level ``F5``
    keystroke into the focused list window — exactly what a user presses — via the same display backend the
    Escape sweep uses (local X11 in model A / the host display agent in model B). Best-effort: never raises;
    returns ``(method, note)`` where ``method`` is ``"f5"`` when the keystroke was delivered, else ``"none"`` with
    a note (no display backend reachable), so the caller can report an honest "could not force-refresh" diagnostic
    instead of a silent no-op."""
    # Protocol «Обновить» command replay is preferred but not yet captured → fall through to the F5 keystroke.
    try:
        backend = _display_backend()
    except Exception as exc:  # noqa: BLE001
        return "none", _display_backend_error_result("force_list_refresh", exc)
    display = os.environ.get("DISPLAY") or ":89"
    try:
        backend.send_keys(["F5"], display=display, settle_sec=settle_sec)
        return "f5", None
    except Exception as exc:  # noqa: BLE001
        return "none", _display_backend_error_result("force_list_refresh", exc)


def _ensure_list_fresh(
    *,
    read_once: "Callable[[], dict[str, Any]]",
    count_of: "Callable[[dict[str, Any]], int]",
    refresh: bool = True,
    wait_for_rows: int | None = None,
    poll_attempts: int | None = None,
    settle_sec: float | None = None,
    sweep_on_zero: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Shared refresh-and-poll engine for the dynlist read primitives (card 125 Change 5).

    ``read_once`` performs ONE full cold-replay read and returns its raw ``out`` dict; ``count_of`` extracts the
    current row count from that ``out``. Policy:

    1. If ``refresh``, force the on-screen list to requery once up front (`_force_list_refresh`).
    2. Poll ``read_once`` until the row count is STABLE (two equal successive reads) or non-zero — or, when
       ``wait_for_rows`` is set, until at least that many rows are read — bounded by ``poll_attempts``.
    3. Because a 2nd read on the SAME warm client returns a reduced/stale load (the cold-client boundary), each
       RE-read is preceded by a clean-state Escape sweep (`_cold_state_sweep`) so the re-opened list is a genuine
       fresh query, not a warm-cache 0.

    Returns ``(out, meta)`` where ``out`` is the last read and ``meta`` records the refresh method, poll outcome,
    read count, whether a sweep was applied and (when requested) whether ``wait_for_rows`` was met — so a
    currency-correct read is observable and auditable rather than implicit. Never raises for the refresh/sweep
    side-effects; a missing display backend degrades to a recorded diagnostic."""
    poll_attempts = LIST_POLL_ATTEMPTS if poll_attempts is None else poll_attempts
    settle_sec = LIST_POLL_SETTLE_SEC if settle_sec is None else settle_sec
    poll_attempts = max(1, int(poll_attempts))

    meta: dict[str, Any] = {"refresh": bool(refresh)}
    if refresh:
        method, note = _force_list_refresh(settle_sec=settle_sec)
    else:
        method, note = "none", "no refresh applied (refresh opt-out)"
    meta["refresh_method"] = method
    note_text, refresh_error = _normalize_display_note(note)
    if note_text:
        meta["refresh_note"] = note_text
    if refresh_error:
        meta["refresh_error"] = refresh_error

    prev: int | None = None
    out: dict[str, Any] = {}
    outcome = "timeout"
    reads = 0
    swept_any = False
    for attempt in range(poll_attempts):
        out = read_once()
        reads += 1
        count = int(count_of(out) or 0)
        if wait_for_rows is not None:
            if count >= int(wait_for_rows):
                outcome = "wait_for_rows_met"
                break
        elif count > 0:
            outcome = "nonzero"
            break
        elif prev is not None and count == prev:
            outcome = "stable"
            break
        prev = count
        if attempt < poll_attempts - 1:
            # Reset the list state before re-reading: a 2nd read on the same warm client otherwise repeats the
            # stale/reduced load (the cold-client boundary). A clean-state Escape sweep re-cold-boots the desktop;
            # a re-refresh re-runs the on-screen list query. If NEITHER is possible (no display backend reachable),
            # a re-read cannot change the result — stop early instead of burning cold reads.
            acted = False
            if sweep_on_zero:
                swept, sweep_error = _normalize_sweep_result(_cold_state_sweep(return_error=True))
                if sweep_error:
                    meta["sweep_error"] = sweep_error
                if swept:
                    swept_any = True
                    acted = True
            if refresh:
                refresh_method, refresh_note = _force_list_refresh(settle_sec=settle_sec)
                note_text, refresh_error = _normalize_display_note(refresh_note)
                if note_text:
                    meta["refresh_note"] = note_text
                if refresh_error:
                    meta["refresh_error"] = refresh_error
                if refresh_method != "none":
                    acted = True
                    meta["refresh_method"] = refresh_method
            if not acted:
                break
            if settle_sec and settle_sec > 0:
                time.sleep(settle_sec)

    meta["poll_reads"] = reads
    meta["poll_outcome"] = outcome
    if swept_any:
        meta["clean_state_swept"] = True
    if wait_for_rows is not None:
        meta["wait_for_rows"] = int(wait_for_rows)
        meta["wait_for_rows_met"] = outcome == "wait_for_rows_met"
    return out, meta


def _list_zero_reason(
    *,
    refresh: bool,
    refresh_method: str,
    swept: bool,
    refresh_error: dict[str, Any] | None = None,
    sweep_error: dict[str, Any] | None = None,
) -> str:
    """Honest 0-rows diagnostic for the dynlist reads (card 125 Change 5), keyed to what the read actually did."""
    if not refresh:
        return (
            "0 rows (refresh opt-out: no refresh applied) — EITHER a genuinely empty list OR a not-yet-refreshed "
            "dynamic list / cold-client boundary. Re-run with refresh=True (the default) to force a "
            "currency-correct read."
        )
    if refresh_method == "none":
        if refresh_error:
            return (
                "0 rows — a refresh was requested but display refresh failed with "
                f"{_display_error_note(refresh_error)}; the list could not be force-refreshed. "
                "A 0 here may be a not-yet-loaded dynamic list rather than an empty one."
            )
        return (
            "0 rows — a refresh was requested but no display backend was reachable to send «Обновить»/F5, so the "
            "list could not be force-refreshed; a 0 here may be a not-yet-loaded dynamic list rather than an empty "
            "one. Set QA_MCP_HOST_AGENT (+ QA_MCP_HOST_AGENT_WINDOW) or run under an X display so reads self-refresh."
        )
    if sweep_error:
        return (
            "0 rows after a forced list refresh, but the clean-state sweep failed with "
            f"{_display_error_note(sweep_error)}; stale open-window state may still be affecting the read."
        )
    return (
        "0 rows after a forced list refresh + poll-until-stable"
        + (" and a clean-state sweep" if swept else "")
        + " — the list is genuinely empty (refreshed)."
    )


def _list_zero_reason_after_table_resolution(
    *,
    refresh: bool,
    refresh_method: str,
    swept: bool,
    descriptor_swept: bool,
    refresh_error: dict[str, Any] | None = None,
    sweep_error: dict[str, Any] | None = None,
) -> str:
    reason = _list_zero_reason(
        refresh=refresh,
        refresh_method=refresh_method,
        swept=swept,
        refresh_error=refresh_error,
        sweep_error=sweep_error,
    )
    if sweep_error or descriptor_swept or not reason.startswith("0 rows after a forced list refresh"):
        return reason
    return (
        "0 rows after resolving the list table from the descriptor, but the descriptor-open form state was not "
        "confirmed clean before replay; this may still be a not-yet-loaded dynamic list or stale open-window state "
        "rather than confirmed empty data."
    )


def _list_uncertain_zero_error(
    *,
    refresh: bool,
    refresh_method: str,
    descriptor_swept: bool | None = None,
    refresh_error: dict[str, Any] | None = None,
    sweep_error: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if refresh_error:
        return refresh_error
    if sweep_error:
        return sweep_error
    if descriptor_swept is False:
        return {
            "ok": False,
            "error": "window-discovery-unconfirmed",
            "tool": "cold_state_sweep",
            "detail": "clean-state sweep did not confirm the target window before list replay",
            "mode": "remote-client" if _display_remote_client_enabled() else "local",
        }
    if refresh and refresh_method == "none":
        return {
            "ok": False,
            "error": "refresh-not-confirmed",
            "tool": "force_list_refresh",
            "detail": "refresh was requested but no display refresh method was delivered",
            "mode": "remote-client" if _display_remote_client_enabled() else "local",
        }
    return None


def _is_1c_window(info: dict[str, Any]) -> bool:
    cls = str(info.get("class") or info.get("Class") or "").lower()
    if cls.startswith("v8toplevelframe"):
        return True
    title = str(info.get("title") or "").lower()
    return "1c" in title or "1с" in title


def _remote_client_list_diagnostic(tool: str) -> dict[str, Any] | None:
    if not _display_remote_client_enabled():
        return None
    diagnostic: dict[str, Any] = {"mode": "remote-client"}
    try:
        backend = _display_backend()
        configured_window = str(backend.target_window or "").strip()
        target_window = configured_window if configured_window not in {"", "*"} else None
        if target_window is not None:
            diagnostic["target_window"] = target_window
        else:
            diagnostic["target_source"] = (
                "active-client-target" if backend.client_target_required else "client-port"
            )
        try:
            windows = backend.list_windows("", geometry=True)
            one_c_windows = [w for w in windows if isinstance(w, dict) and _is_1c_window(w)]
            diagnostic["windows"] = one_c_windows
            diagnostic["window_count"] = len(one_c_windows)
            diagnostic["all_window_count"] = len(windows)
        except Exception as exc:  # noqa: BLE001 - diagnostic must not hide the list failure
            diagnostic["window_error"] = _display_backend_error_result(f"{tool}.window_discovery", exc)
        try:
            diagnostic["visible_cells"] = backend.visible_list_cells(window=target_window)
        except Exception as exc:  # noqa: BLE001 - diagnostic must not hide the list failure
            diagnostic["visible_cells_error"] = _display_backend_error_result(f"{tool}.visible_cells", exc)
    except Exception as exc:  # noqa: BLE001
        diagnostic["error"] = _display_backend_error_result(f"{tool}.remote_window_diagnostic", exc)
    return diagnostic


def _mark_uncertain_zero_list_read(
    result: dict[str, Any],
    *,
    tool: str,
    zero_data: bool,
    refresh: bool,
    fresh: dict[str, Any],
    descriptor_swept: bool | None = None,
) -> dict[str, Any]:
    if not zero_data:
        result.setdefault("ok", True)
        result.setdefault("data_confidence", "confirmed")
        return result
    underlying = _list_uncertain_zero_error(
        refresh=refresh,
        refresh_method=str(fresh.get("refresh_method") or "none"),
        descriptor_swept=descriptor_swept,
        refresh_error=fresh.get("refresh_error"),
        sweep_error=fresh.get("sweep_error"),
    )
    if underlying is None:
        result.setdefault("ok", True)
        result.setdefault("data_confidence", "confirmed")
        return result
    result["ok"] = False
    result["error"] = "list-read-uncertain-zero"
    result["data_confidence"] = "unknown"
    result["underlying_error"] = underlying
    result.setdefault(
        "detail",
        "list read returned zero/empty data after refresh, sweep, or window discovery could not be confirmed",
    )
    remote_diagnostic = _remote_client_list_diagnostic(tool)
    if remote_diagnostic is not None:
        result["remote_window_diagnostic"] = remote_diagnostic
    return result


def _list_refresh_summary(meta: dict[str, Any]) -> dict[str, Any]:
    """Compact, observable record of what the refresh-and-poll engine did — embedded as ``list_refresh`` on each
    dynlist read result so a currency-correct read (or an honest opt-out / could-not-refresh) is auditable."""
    summary: dict[str, Any] = {
        "refresh": meta["refresh"],
        "method": meta["refresh_method"],
        "poll_outcome": meta["poll_outcome"],
    }
    if meta.get("refresh_note"):
        summary["note"] = meta["refresh_note"]
    if meta.get("refresh_error"):
        summary["error"] = meta["refresh_error"]
    if meta.get("sweep_error"):
        summary["sweep_error"] = meta["sweep_error"]
    if "wait_for_rows" in meta:
        summary["wait_for_rows"] = meta["wait_for_rows"]
        summary["wait_for_rows_met"] = meta["wait_for_rows_met"]
    return summary


@qa_tool()
@testclient_tool(phase="list_read")
def read_list_grid(
    open_link: str,
    columns: list[str],
    max_rows: int = 25,
    flat: bool = False,
    table: str | None = None,
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture_dir: str | None = None,
    refresh: bool = True,
    wait_for_rows: int | None = None,
) -> dict[str, Any]:
    """Read MANY ROWS × columns of a dynamic list (the whole visible grid) in ONE call. Opens the list at
    ``open_link`` (e.g. ``e1cib/list/Справочник.Товары``), reads the first row's ``columns`` (e.g. ``["Код",
    "Наименование"]`` of the resolved dynlist table), then steps «перехожу к следующей строке» and reads again, up
    to ``max_rows`` rows or end-of-list. By default the table is resolved from the live descriptor; pass ``table`` to
    select explicitly. Returns {table, nav_link, row_count, rows: [{column: value}, …], list_refresh,
    table_resolution}.

    ``flat`` (default False) reads the list's CURRENT view/sort order. A HIERARCHICAL catalog (e.g. Товары) defaults
    to a grouped view, so the grid then exposes only the TOP-LEVEL folders (Обувь/Продукты/…). Set ``flat=True`` to
    first switch the list to flat «Список» view (the standard catalog-list-form «ФормаСписок» view-mode command,
    baked into the genuine capture) so NESTED items are read too — live-verified on Товары (flat -> Bosch1234/Sony
    К3456P/Босоножки/… nested rows, codes vs OData). ``flat`` selects the capture; pass ``capture_dir`` to override
    explicitly.

    CURRENCY: a 1C dynamic list is async/eventually-consistent, so ``refresh=True`` (default) forces an
    «Обновить»/F5 requery and polls-until-stable before reporting — a freshly-created record shows up and a reported
    ``0 rows`` only ever means a genuinely empty list. ``refresh=False`` opts out (records "no refresh applied") for
    an absence assertion. ``wait_for_rows=N`` blocks until at least N rows are read or the bounded poll timeout
    elapses (``list_refresh.wait_for_rows_met`` reports which). ``list_refresh`` records the refresh method + poll
    outcome. Table-resolution failures return structured ``list-table-*`` diagnostics and do NOT run a wrong-table
    replay or call the list genuinely empty.

    Mechanism: a genuine next-row capture replayed cold (faithful full-replay through the first read — which for the
    flat capture also replays the view-switch — then the genuine go-to-next-row block, the decoded next-row action
    GUID ``d267315b…``, replayed + the reads, all on the one materialised socket, message-id kept + sequence bumped).
    Live-verified the cursor advances. One grid read per fresh ``launch_test_client`` (the cold-client boundary). Use
    ``read_list_row`` for a single row (or a row by value), ``read_list_column`` for a single cell,
    ``read_table_cell`` for FORM tables."""
    from .protocol.native_write import derive_read_list_column, read_list_grid_replay

    try:
        host, port, attachment = _resolve_testclient_endpoint(host, port, phase="list_read")
    except ConnectionError as exc:
        return _attach_tool_error("read_list_grid", "attach", exc, host=host, port=port)
    resolved_table, table_meta = _resolve_list_table_for_read(
        host=host, port=port, open_link=open_link, requested_table=table)
    if resolved_table is None:
        if attachment is not None:
            table_meta["attached_endpoint"] = attachment
        return table_meta
    descriptor_swept = _cold_state_sweep()
    cap = capture_dir or ("nextrow-flat" if flat else "nextrow")
    template = derive_read_list_column(resolve_capture_dir(cap, _repo_root()))
    out, fresh = _ensure_list_fresh(
        read_once=lambda: read_list_grid_replay(template, open_link=open_link, columns=columns, max_rows=max_rows,
                                                table=resolved_table, host=host, port=port),
        count_of=lambda o: o.get("row_count", 0) or 0,
        refresh=refresh,
        wait_for_rows=wait_for_rows,
    )
    result = {"table": resolved_table, "nav_link": out["nav_link"], "row_count": out["row_count"], "rows": out["rows"],
              "list_refresh": _list_refresh_summary(fresh), "table_resolution": table_meta}
    if descriptor_swept:
        result["descriptor_clean_state_swept"] = True
    if fresh.get("clean_state_swept"):
        result["clean_state_swept"] = True
    if out["row_count"] == 0:
        result["reason"] = _list_zero_reason_after_table_resolution(
            refresh=refresh,
            refresh_method=fresh["refresh_method"],
            swept=fresh.get("clean_state_swept", False),
            descriptor_swept=descriptor_swept,
            refresh_error=fresh.get("refresh_error"),
            sweep_error=fresh.get("sweep_error"),
        )
    _mark_uncertain_zero_list_read(
        result,
        tool="read_list_grid",
        zero_data=out["row_count"] == 0,
        refresh=refresh,
        fresh=fresh,
        descriptor_swept=descriptor_swept,
    )
    if attachment is not None:
        result["attached_endpoint"] = attachment
    return result


def _read_testclient_windows(*, host: str, port: int, capture_dir: str, manager_templates: str) -> dict[str, Any]:
    return protocol_introspection._read_testclient_windows(
        host=host,
        port=port,
        capture_dir=capture_dir,
        manager_templates=manager_templates,
    )


@qa_tool()
@testclient_tool(phase="window_list")
def get_window_list_testclient(
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    capture_dir: str = "tm-v1-ro-batchQ3",
    manager_templates: str = VALUE_READ_TEMPLATES,
) -> dict[str, Any]:
    """Enumerate the 1C-internal windows/tabs open in the TestClient natively. This is the protocol-level list (the
    1C windows the client tracks — main desktop, an open form/list/card tab, a dialog), DISTINCT from
    ``get_window_list`` which lists OS top-level X windows (1C opens forms as MDI tabs inside ONE X window, so the OS
    list does not see them). Replays the genuine window-list query on a live session (grafted onto a live value-read
    header so the session GUIDs match — a raw replay is rejected) and decodes each window's caption + frame kind
    (SecondaryFrame | MainFrame | HomePage). Each window record's ``caption`` is the window title (Cyrillic-aware).
    SCOPE: like ``read_form_descriptor``, each call is a FRESH session, so it lists the windows of the session it
    opens (the fixture form + desktop + home page); address an individual window with ``activate_window`` /
    ``close_window``. If you only need to prove MCP-to-TestClient connectivity without a form target, run
    ``qa_mcp_doctor`` and inspect its ``testclient_smoke`` check. Form-level reads that need a target should pass
    ``open_link`` such as ``e1cib/list/<metadata>``. Returns {count, windows:[{kind, guid, caption}]}. Decoded +
    validated against a genuine analysis oracle (4 windows)."""
    arguments = {
        "host": host,
        "port": port,
        "capture_dir": capture_dir,
        "manager_templates": manager_templates,
    }
    return _execute_composed_operation(
        OperationKind.READ,
        "get_window_list_testclient",
        arguments,
        lambda: _get_window_list_testclient_impl(**arguments),
    )


def _get_window_list_testclient_impl(
    host: str,
    port: int,
    capture_dir: str,
    manager_templates: str,
) -> dict[str, Any]:
    try:
        host, port, attachment = _resolve_testclient_endpoint(host, port, phase="window_list")
    except ConnectionError as exc:
        return _attach_tool_error("get_window_list_testclient", "attach", exc, host=host, port=port)
    result = _read_testclient_windows(host=host, port=port, capture_dir=capture_dir, manager_templates=manager_templates)
    if attachment is not None:
        result["attached_endpoint"] = attachment
    return result


@qa_tool()
@testclient_tool(phase="measure_scenario", local_boot=True)
def measure_scenario(
    feature_text: str,
    host: str = DEFAULT_CLIENT_HOST,
    port: int = DEFAULT_CLIENT_PORT,
    env_file: str = ".ai1c/vanessa-qa-mcp.env",
    src_root: str = "",
    max_ms: float = 0.0,
) -> dict[str, Any]:
    """Code COVERAGE + PERFORMANCE for a scenario via the 1C debug protocol. Self-contained: starts the 1C debug
    server (`dbgs`), boots a debug-attached TestClient (`/DEBUG -http /DEBUGGERURL`), drives the decoded `/e1crdbg/`
    debugger handshake, runs ``feature_text`` under a headless «Замер производительности», collects the
    `PerformanceInfoMain` result, parses it to per-line {frequency -> coverage, durability -> perf µs}, and tears
    everything down (restarts Apache). The scenario must exercise real BSL (a create form / a posting / a query —
    cached list opens alone produce no measure data). ``src_root`` (the EDT config ``src`` dir, e.g.
    ``/path/to/config/src``) resolves module names (Документ.Заказ :: ФормаДокумента / МодульОбъекта). ``max_ms`` > 0
    sets a perf assertion on the total measured time (``perf_ok``). Opt-in (the замер
    adds overhead). Returns {ok, scenario_ok, perf_ok, report{modules,totals}, report_text}."""
    from .debug.measure import measure_scenario as _measure

    return _measure(feature_text, host=host, port=port, env_file=env_file,
                    src_root=src_root or None, max_ms=(max_ms or None))


def profile_tool_names(profile: str) -> tuple[str, ...]:
    """Return the deterministic tool names for a named public profile."""

    normalized = profile.strip().lower()
    if normalized == "research":
        names = set(_TOOL_CATALOG)
    elif normalized == "standalone":
        names = set(_TOOL_CATALOG) - _RESEARCH_ONLY_TOOL_NAMES
    else:
        raise ValueError(f"unknown qa-mcp tool profile: {profile!r}")
    return tuple(sorted(names))


# Each public name has one declared policy.  This is deliberately independent
# of decorators and positive-result schemas: decorators describe mechanics,
# while this inventory decides whether a target-bound call needs a session
# route before any provider-owned arguments or endpoint work is evaluated.
_NATIVE_SESSION_BOUND_TOOLS = frozenset({
    "activate_window", "add_table_row", "advanced_search", "answer_dialog",
    "assert_form_value", "capture_screenshot", "choose_from_list", "choose_from_menu",
    "click_command", "close_window", "copy_table_row", "delete_table_row",
    "get_window_list", "get_window_list_testclient", "measure_scenario", "move_table_row",
    "open_card", "open_external_processor", "open_list", "read_form_descriptor",
    "read_list_column", "read_list_grid", "read_list_row", "read_record",
    "read_spreadsheet_cell", "read_table_cell", "read_user_messages", "run_report",
    "run_scenario", "run_step", "run_write_scenario_tool", "search_list",
    "select_all_table_rows", "select_table_row", "send_keys", "set_choice",
    "set_list_view", "set_reference_field", "set_table_cell", "set_table_date_cell",
    "switch_page", "toggle_checkbox", "wait_for_form_value", "write_form_date",
    "write_form_fields_by_label", "write_form_value", "write_form_value_xtest",
    "write_form_values",
})
_LIFECYCLE_TOOLS = frozenset({
    "attach_test_client", "launch_test_client", "stop_test_client", "test_client_status",
})
_PROVIDER_DATA_TOOLS = frozenset({
    "assert_com_count", "assert_data", "assert_data_count", "com_connector_doctor",
    "query_com", "role_data_matrix", "write_test_report",
})
_PURE_READINESS_TOOLS = frozenset({
    "autofill_required_fields", "echo_jsonrpc_arguments", "generate_smoke_suite",
    "get_state", "get_test_results", "infobase_info", "qa_mcp_doctor",
    "search_for_steps", "transpile",
})
_TOOL_ROUTE_CLASSIFICATIONS = MappingProxyType({
    **{name: "native-session-bound" for name in _NATIVE_SESSION_BOUND_TOOLS},
    **{name: "lifecycle" for name in _LIFECYCLE_TOOLS},
    **{name: "provider-data" for name in _PROVIDER_DATA_TOOLS},
    **{name: "pure/readiness" for name in _PURE_READINESS_TOOLS},
})

if _NATIVE_SESSION_BOUND_TOOLS != (NATIVE_SESSION_OPERATION_NAMES & set(_TOOL_CATALOG)):
    raise RuntimeError("native session tool inventory diverged from shared operation admission")
if set(_TOOL_ROUTE_CLASSIFICATIONS) != set(_TOOL_CATALOG):
    raise RuntimeError("public tool route classification is incomplete")


def _bound_tool_preflight(
    context: ApplicationContext, name: str, *, shared_operation_extension: bool = False,
) -> dict[str, Any] | None:
    """Fail closed for native and unclassified calls before hidden arguments."""

    if is_explicitly_unbound_context(context):
        return None
    if shared_operation_extension:
        return None
    classification = _TOOL_ROUTE_CLASSIFICATIONS.get(name)
    if classification != "native-session-bound":
        if classification is not None:
            return None
        return OperationResult.blocked(
            OperationRequest(OperationKind.WRITE, name),
            code="runtime-target-route-blocked",
            message="operation route was not admitted",
        ).to_dict()
    refusal = blocked_bound_route(
        context, OperationRequest(OperationKind.WRITE, name, {}),
    )
    return refusal.to_dict() if refusal is not None else None


def _call_tool_function(fn: Callable[..., Any]) -> Callable[[OperationRequest], Any]:
    def handler(request: OperationRequest) -> Any:
        return fn(**dict(request.arguments))

    return handler


def _scenario_read_handler(request: OperationRequest) -> Any:
    arguments = dict(request.arguments)
    session = arguments.pop("session")
    # Bound active-window predicates are evaluated by the shared operation
    # seam after this native read; never forward the private carrier to the
    # TestClient/session API.
    arguments.pop("_expected_window", None)
    if request.name == "read_active_window":
        return session.get_active_window_context(**arguments).to_result()
    if request.name == "read_form_summary":
        return session.get_form_summary(**arguments)
    if request.name == "read_element":
        return session.get_form_element_details(**arguments)
    raise ValueError(f"unsupported scenario read operation: {request.name}")


def _capture_screenshot_handler(request: OperationRequest) -> OperationResult:
    context = current_application_context()
    if context.runtime_target is None:
        # Deliberately unbound standalone/direct compatibility retains its file.
        value = _capture_screenshot_impl(**dict(request.arguments))
        path = value.get("path") if type(value) is dict else None
        if type(path) is not str or not Path(path).is_file():
            return OperationResult.failure(
                request, code="display-evidence-missing", message="screenshot evidence was not retained"
            )
        digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        artifact = ArtifactReference(
            f"screenshot.{digest[:16]}", "image/png", f"sha256:{digest}", path, "internal"
        )
        return OperationResult(request, OperationVerdict.SUCCESS, value=value, artifacts=(artifact,))

    scope = _current_evidence_scope()
    if (scope is None or scope._ledger is not context.evidence_ledger
            or scope._operation != request.name):
        return OperationResult.failure(request, code="display-evidence-missing",
                                       message="screenshot production scope was not admitted")
    try:
        # Fresh exclusive destination owned before backend entry. Caller and
        # backend result paths do not decide which file may be retained/removed.
        destination = scope._allocate_screenshot()
        value = _display_backend().capture_screenshot(
            request.arguments["display"], destination, window=request.arguments.get("window")
        )
        if (type(value) is not dict or len(value) > 64
                or any(type(key) is not str for key in value)
                or type(value.get("path")) is not str or value["path"] != str(destination)):
            raise ValueError("invalid production result")
        record = context.evidence_ledger._file_record(destination)
        if record.identity[2] == 0:
            raise ValueError("empty production")
        if "sha256" in value and (type(value["sha256"]) is not str
                or value["sha256"] not in (record.sha256, record.sha256[7:])):
            raise ValueError("production digest mismatch")
        if "size_bytes" in value and (type(value["size_bytes"]) is not int
                or value["size_bytes"] != record.identity[2]):
            raise ValueError("production size mismatch")
        artifact = ArtifactReference(
            "screenshot." + record.sha256[7:23], "image/png", record.sha256,
            str(destination), "internal",
        )
        scope.record(artifact.artifact_id, destination)
        return OperationResult(request, OperationVerdict.SUCCESS,
                               value={"size_bytes": record.identity[2]}, artifacts=(artifact,))
    except Exception:
        # Scope finalization cleans only this producer's allocated destination,
        # including backend/metadata failures. Borrowed result paths stay inert.
        return OperationResult.failure(request, code="display-evidence-missing",
                                       message="screenshot evidence was not retained")


def _default_executor(settings: Settings) -> QAExecutor:
    handlers = {
        (OperationKind.READ, "get_window_list_testclient"): _call_tool_function(
            _get_window_list_testclient_impl
        ),
        (OperationKind.READ, "get_window_list"): _get_window_list_handler,
        (OperationKind.READ, "read_active_window"): _scenario_read_handler,
        (OperationKind.READ, "read_form_summary"): _scenario_read_handler,
        (OperationKind.READ, "read_element"): _scenario_read_handler,
        (OperationKind.WRITE, "send_keys"): _call_tool_function(_send_keys_impl),
        (OperationKind.LIFECYCLE, "test_client_status"): _call_tool_function(
            _test_client_status_impl
        ),
        (OperationKind.DISPLAY, "capture_screenshot"): _capture_screenshot_handler,
    }
    executor_type = WindowsHostQAExecutor if settings.remote_client else LocalQAExecutor
    return executor_type(handlers)


def _tool_argument_defaults(fn: Callable[..., Any], settings: Settings) -> dict[str, Any]:
    """Resolve import-time tool defaults against one composed application."""

    defaults: dict[str, Any] = {}
    parameters = inspect.signature(fn).parameters
    if parameters.get("host") is not None and parameters["host"].default == DEFAULT_CLIENT_HOST:
        defaults["host"] = settings.client_host
    if parameters.get("port") is not None and parameters["port"].default == DEFAULT_CLIENT_PORT:
        defaults["port"] = settings.client_port
    templates = parameters.get("manager_templates")
    if templates is not None and templates.default == DEFAULT_TEMPLATES:
        defaults["manager_templates"] = settings.manager_templates
    elif templates is not None and templates.default == VALUE_READ_TEMPLATES:
        defaults["manager_templates"] = settings.value_read_templates
    return defaults


@_resolved_annotations
def _bound_launch_test_client(
    headless: bool = True,
    manage_apache: bool = False,
    wait_sec: float = 90.0,
    use_hardware_licenses: bool | None = None,
) -> dict[str, Any]:
    return launch_test_client(
        port=current_application_context().settings.client_port,
        headless=headless, manage_apache=manage_apache, display="auto",
        wait_sec=wait_sec, use_hardware_licenses=use_hardware_licenses,
    )


@_resolved_annotations
def _bound_attach_test_client(connect_timeout_sec: float = 0.5) -> dict[str, Any]:
    settings = current_application_context().settings
    return attach_test_client(
        host=settings.client_host, port=settings.client_port,
        connect_timeout_sec=connect_timeout_sec,
    )


@_resolved_annotations
def _bound_test_client_status() -> dict[str, Any]:
    settings = current_application_context().settings
    return test_client_status(host=settings.client_host, port=settings.client_port)


@_resolved_annotations
def _bound_stop_test_client() -> dict[str, Any]:
    return _project_bound_cleanup()


_PROJECT_BOUND_TOOLS: Mapping[str, Callable[..., Any]] = {
    "launch_test_client": _bound_launch_test_client,
    "attach_test_client": _bound_attach_test_client,
    "test_client_status": _bound_test_client_status,
    "stop_test_client": _bound_stop_test_client,
}


def _project_hidden_arguments(
    fn: Callable[..., Any], settings: Settings, runtime_target: RuntimeTargetResolution,
) -> dict[str, Any]:
    parameters = inspect.signature(fn).parameters
    config = runtime_target._physical_config
    evidence_root = runtime_target.binding.evidence_root

    def display() -> str:
        attachment = current_application_context().attachment
        if type(attachment) is not _AttachedTestClientContext:
            raise RuntimeError("target-bound display is unavailable")
        if type(attachment.display) is str:
            return attachment.display
        raise RuntimeError("target-bound display is unavailable")

    com_tool = fn.__name__ in {"query_com", "assert_com_count", "com_connector_doctor"}
    candidates: dict[str, Any] = {
        "host": settings.client_host,
        "port": settings.client_port,
        "env_file": "",
        "infobase_path": config.infobase_path,
        "connection_string": config.connection_string,
        "user": config.test_client_user if com_tool else settings.odata_user,
        "password": config.test_client_password if com_tool else settings.odata_password,
        "odata_password": settings.odata_password,
        "base_url": settings.odata_url,
        "com_infobase_path": "", "com_user": "", "com_password": "", "com_query": "",
        "src_root": config.source_root,
        "enum_src_root": config.source_root,
        "display": display,
        "capture_dir": parameters["capture_dir"].default if "capture_dir" in parameters else "",
        "out_path": lambda: str(evidence_root / f"{fn.__name__}-{uuid.uuid4().hex}.png"),
        "out_dir": lambda: str(evidence_root / f"{fn.__name__}-{uuid.uuid4().hex}"),
        "manager_templates": _tool_argument_defaults(fn, settings).get(
            "manager_templates", settings.manager_templates
        ),
    }
    return {name: value for name, value in candidates.items() if name in parameters}


def create_mcp_server(
    *,
    settings: Settings | None = None,
    executor: QAExecutor | None = None,
    tool_profile: str = "standalone",
    target: TargetIdentity | None = None,
    runtime_target: RuntimeTargetResolution | None = None,
    runtime_target_env: Mapping[str, str] | None = None,
    session: SessionIdentity | None = None,
    extra_tools: Mapping[str, Callable[..., Any]] | None = None,
    extra_tool_classes: Mapping[str, str] | None = None,
) -> FastMCP:
    """Compose an isolated qa-mcp server from public settings and contracts.

    ``extra_tools`` is an explicit downstream integration seam. Each callable
    is context-bound before registration; no entry-point discovery or reverse
    import of a downstream package occurs in the public core. A bound
    extension is blocked by default. The only opt-in class is
    ``shared-operation``: it may compose ``execute_mcp_operation``, which
    performs its own route admission, but is not a native-route grant.
    """

    if runtime_target is not None and runtime_target_env is not None:
        raise ValueError("pass either runtime_target or runtime_target_env, not both")
    resolved_runtime_target = (
        resolve_runtime_target(runtime_target_env)
        if runtime_target_env is not None
        else runtime_target
    )
    if resolved_runtime_target is not None:
        validate_runtime_target_resolution(resolved_runtime_target)
        if target is not None and target != resolved_runtime_target.binding.target:
            raise RuntimeTargetBindingError(
                "runtime-target-mismatch",
                "target",
                "explicit target differs from runtime-target binding",
            )
        target = resolved_runtime_target.binding.target
    resolved_settings = settings or Settings.from_env()
    context = ApplicationContext(
        settings=resolved_settings,
        executor=executor or _default_executor(resolved_settings),
        target=target,
        runtime_target=resolved_runtime_target,
        session=session,
    )
    server = FastMCP("qa-native-manager")
    tool_names = profile_tool_names(tool_profile)
    if resolved_runtime_target is not None:
        tool_names = tuple(name for name in tool_names if name != "role_data_matrix")
    for name in tool_names:
        fn = _PROJECT_BOUND_TOOLS.get(name, _TOOL_CATALOG[name]) if resolved_runtime_target else _TOOL_CATALOG[name]
        server.tool(name=name)(
            bind_application_context(
                fn,
                context,
                argument_defaults=_tool_argument_defaults(fn, resolved_settings),
                hidden_arguments=(
                    _project_hidden_arguments(fn, resolved_settings, resolved_runtime_target)
                    if resolved_runtime_target is not None else None
                ),
                before_call=lambda name=name: _bound_tool_preflight(context, name),
            )
        )
    declared_extra_classes = dict(extra_tool_classes or {})
    extras = dict(extra_tools or {})
    if set(declared_extra_classes) - set(extras):
        raise ValueError("extra tool classification names must be registered")
    if any(value != "shared-operation" for value in declared_extra_classes.values()):
        raise ValueError("extra tool classification is not supported")
    for name, fn in sorted(extras.items()):
        if name in _TOOL_CATALOG:
            raise ValueError(f"extra tool collides with public qa-mcp tool: {name}")
        # Bound extensions have no implicit native authority. A declared
        # shared-operation adapter must enter execute_mcp_operation itself.
        server.tool(name=name)(
            bind_application_context(
                fn,
                context,
                before_call=lambda name=name: _bound_tool_preflight(
                    context,
                    name,
                    shared_operation_extension=(
                        declared_extra_classes.get(name) == "shared-operation"
                    ),
                ),
            )
        )
    setattr(server, "_qa_mcp_application_context", context)
    setattr(server, "_qa_mcp_tool_profile", tool_profile.strip().lower())
    return server


def application_context(server: FastMCP) -> ApplicationContext:
    context = getattr(server, "_qa_mcp_application_context", None)
    if not isinstance(context, ApplicationContext):
        raise ValueError("FastMCP server was not created by create_mcp_server")
    return context


def _canonical_profile_schema(value: Any, *, parent_key: str = "") -> Any:
    """Remove generator-only metadata and normalize unordered schema members.

    FastMCP/Pydantic may derive cosmetic ``title`` values and union/member
    ordering through Python's typing implementation. Bundled-template defaults
    also contain the installation root. Those details can change between
    machines without changing the MCP wire contract. Required fields, logical
    defaults, descriptions and every validation keyword stay in the snapshot.
    """

    if isinstance(value, dict):
        return {
            key: _canonical_profile_schema(item, parent_key=key)
            for key, item in sorted(value.items())
            if key != "title"
        }
    if isinstance(value, list):
        items = [_canonical_profile_schema(item) for item in value]
        if parent_key in {"anyOf", "oneOf", "required", "enum", "type"}:
            return sorted(
                items,
                key=lambda item: json.dumps(
                    item,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            )
        return items
    if isinstance(value, str):
        normalized_path = value.replace("\\", "/")
        bundled_marker = "/qa_mcp/_bundled/"
        if bundled_marker in normalized_path:
            bundled_path = normalized_path.split(bundled_marker, 1)[1]
            return f"qa_mcp://_bundled/{bundled_path}"
    return value


def _profile_schema_snapshot(profile: str) -> list[dict[str, Any]]:
    async def collect() -> list[dict[str, Any]]:
        server = create_mcp_server(settings=_SETTINGS, tool_profile=profile)
        tools = await server.list_tools()
        return [
            _canonical_profile_schema({
                "name": tool.name,
                "parameters": tool.parameters,
                "output_schema": tool.output_schema,
            })
            for tool in sorted(tools, key=lambda item: item.name)
        ]

    return asyncio.run(collect())


def profile_schema_digest(profile: str) -> str:
    """Return a stable digest over selected tool names and JSON schemas."""

    encoded = json.dumps(
        _profile_schema_snapshot(profile),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


_DEFAULT_APPLICATION_CONTEXT.executor = _default_executor(_SETTINGS)


def _schema_title(name: str) -> str:
    return name.replace("_", " ").title()


def _normalize_schema_metadata(schema: Any, *, root_title: str | None = None) -> None:
    if not isinstance(schema, dict):
        return
    if root_title is not None:
        schema.setdefault("title", root_title)
    if schema.get("additionalProperties") is False:
        schema.pop("additionalProperties", None)
    properties = schema.get("properties")
    if isinstance(properties, dict):
        for property_name, property_schema in properties.items():
            if isinstance(property_schema, dict):
                property_schema.setdefault("title", _schema_title(str(property_name)))
                _normalize_schema_metadata(property_schema)
    for value in schema.values():
        if isinstance(value, dict):
            _normalize_schema_metadata(value)
        elif isinstance(value, list):
            for item in value:
                _normalize_schema_metadata(item)


def _normalize_registered_tool_schemas_for_fastmcp3() -> None:
    """Preserve the pre-migration schema metadata shape for tools/list clients."""
    provider = getattr(mcp, "_local_provider", None)
    components = getattr(provider, "_components", {})
    if not isinstance(components, dict):
        return
    for tool in components.values():
        name = getattr(tool, "name", None)
        if not isinstance(name, str):
            continue
        raw_doc = getattr(getattr(tool, "fn", None), "__doc__", None)
        if isinstance(raw_doc, str) and raw_doc.strip():
            tool.description = raw_doc
        _normalize_schema_metadata(
            getattr(tool, "parameters", None),
            root_title=f"{name}Arguments",
        )
        _normalize_schema_metadata(
            getattr(tool, "output_schema", None),
            root_title=f"{name}DictOutput",
        )


_normalize_registered_tool_schemas_for_fastmcp3()


def _truthy_env(value: str | None) -> bool:
    return env_flag(value)


def _is_loopback_http_host(host: str) -> bool:
    normalized = host.strip().lower()
    return normalized in {"127.0.0.1", "localhost", "::1", "[::1]"}


def _is_wildcard_http_host(host: str) -> bool:
    normalized = host.strip().lower()
    return normalized in {"", "0.0.0.0", "::", "[::]", "*"}


def _resolve_http_bind(env: dict[str, str] | None = None) -> tuple[str, int]:
    settings = Settings.from_env(env)
    host = settings.http_host
    port = settings.http_port
    unsafe_bind = _is_wildcard_http_host(host) or not _is_loopback_http_host(host)
    if unsafe_bind and settings.http_transport == "sse":
        raise ValueError(
            "authenticated non-loopback SSE is not supported; use QA_MCP_TRANSPORT=streamable-http"
        )
    if unsafe_bind and not settings.bearer_token_present:
        raise ValueError(
            "QA_MCP_HTTP_HOST is non-loopback but QA_MCP_BEARER_TOKEN is not configured. "
            "Use 127.0.0.1 for local-only access or set a strong standalone bearer token."
        )
    return host, port


def _http_header(scope: dict[str, Any], name: bytes) -> str:
    wanted = name.lower()
    for raw_name, raw_value in scope.get("headers") or []:
        if raw_name.lower() == wanted:
            return raw_value.decode("latin1")
    return ""


def _content_type_parts(value: str) -> tuple[str, dict[str, str]]:
    parts = [part.strip() for part in value.split(";") if part.strip()]
    media_type = parts[0].lower() if parts else ""
    params: dict[str, str] = {}
    for part in parts[1:]:
        key, sep, raw = part.partition("=")
        if sep:
            params[key.strip().lower()] = raw.strip().strip('"').lower()
    return media_type, params


def _is_json_http_request(scope: dict[str, Any]) -> bool:
    if scope.get("type") != "http" or str(scope.get("method") or "").upper() != "POST":
        return False
    media_type, _params = _content_type_parts(_http_header(scope, b"content-type"))
    return media_type == "application/json" or media_type.endswith("+json")


async def _send_jsonrpc_utf8_error(
    send: Any,
    *,
    status_code: int,
    code: str,
    message: str,
    detail: str,
) -> None:
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32080,
                "message": message,
                "data": {
                    "error": code,
                    "detail": detail,
                    "expected_content_type": "application/json; charset=utf-8",
                },
            },
        },
        ensure_ascii=False,
    ).encode("utf-8")
    await send({
        "type": "http.response.start",
        "status": status_code,
        "headers": [
            (b"content-type", b"application/json; charset=utf-8"),
            (b"content-length", str(len(body)).encode("ascii")),
        ],
    })
    await send({"type": "http.response.body", "body": body, "more_body": False})


class _JsonRpcUtf8BodyMiddleware:
    """Fail closed on non-UTF-8 JSON request bodies before FastMCP dispatch."""

    def __init__(self, app: Any):
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if not _is_json_http_request(scope):
            await self.app(scope, receive, send)
            return

        _media_type, params = _content_type_parts(_http_header(scope, b"content-type"))
        charset = params.get("charset")
        normalized_charset = (charset or "utf-8").replace("_", "-")
        if normalized_charset not in {"utf-8", "utf8"}:
            await _send_jsonrpc_utf8_error(
                send,
                status_code=415,
                code="jsonrpc-non-utf8-charset",
                message="JSON-RPC request bodies must use UTF-8",
                detail=f"received charset={charset!r}",
            )
            return

        chunks: list[bytes] = []
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            if message["type"] != "http.request":
                continue
            chunks.append(message.get("body", b""))
            if not message.get("more_body", False):
                break
        body = b"".join(chunks)
        try:
            body.decode("utf-8")
        except UnicodeDecodeError as exc:
            await _send_jsonrpc_utf8_error(
                send,
                status_code=400,
                code="jsonrpc-invalid-utf8",
                message="JSON-RPC request body is not valid UTF-8",
                detail=str(exc),
            )
            return

        replayed = False

        async def replay_receive() -> dict[str, Any]:
            nonlocal replayed
            if replayed:
                # Streamable HTTP keeps listening for a real disconnect after
                # consuming the JSON-RPC request.  Forward the original ASGI
                # receive channel here; repeatedly synthesizing an empty
                # request creates a busy loop that starves the SSE response.
                return await receive()
            replayed = True
            return {"type": "http.request", "body": body, "more_body": False}

        await self.app(scope, replay_receive, send)


async def _send_http_json(send: Any, status: int, payload: dict[str, Any], *, authenticate: bool = False) -> None:
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    headers = [
        (b"content-type", b"application/json; charset=utf-8"),
        (b"content-length", str(len(body)).encode("ascii")),
    ]
    if authenticate:
        headers.append((b"www-authenticate", b"Bearer"))
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": body, "more_body": False})


class _StandaloneHttpMiddleware:
    """Serve bounded health and authenticate MCP before protocol dispatch."""

    def __init__(self, app: Any, *, bearer_token: str):
        self.app = app
        self._expected = f"Bearer {bearer_token}".encode("utf-8") if bearer_token else b""

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return
        path = str(scope.get("path") or "")
        if path == "/health":
            await _send_http_json(send, 200, {"status": "ok"})
            return
        if self._expected and (path == "/mcp" or path.startswith("/mcp/")):
            supplied = _http_header(scope, b"authorization").encode("utf-8")
            if not hmac.compare_digest(supplied, self._expected):
                await _send_http_json(
                    send,
                    401,
                    {"error": "unauthorized"},
                    authenticate=True,
                )
                return
        await self.app(scope, receive, send)


def _streamable_http_app_with_utf8_gate(
    server: FastMCP | None = None,
    *,
    bearer_token: str | None = None,
) -> Any:
    selected_server = server or mcp
    token = os.environ.get("QA_MCP_BEARER_TOKEN", "").strip() if bearer_token is None else bearer_token
    return _StandaloneHttpMiddleware(
        _JsonRpcUtf8BodyMiddleware(
            selected_server.http_app(path="/mcp", transport="streamable-http")
        ),
        bearer_token=token,
    )


def _run_streamable_http_with_utf8_gate(
    host: str,
    port: int,
    server: FastMCP | None = None,
) -> None:  # pragma: no cover - exercised by focused runner unit tests
    import uvicorn

    app = _streamable_http_app_with_utf8_gate(server)
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
    )
    server = uvicorn.Server(config)
    import anyio

    anyio.run(server.serve)


def main() -> None:
    # Transport: stdio by default (Agent spawns the process); set QA_MCP_TRANSPORT=http for the Docker
    # delivery (the Agent connects over the network to the published port). Host/port come from env so a
    # `docker run -p` needs no in-image config.
    settings = Settings.from_env()
    tool_profile = os.environ.get("QA_MCP_TOOL_PROFILE", "standalone")
    try:
        server = create_mcp_server(
            settings=settings,
            tool_profile=tool_profile,
            runtime_target_env=os.environ,
        )
    except RuntimeTargetBindingError as error:
        print(
            f"qa-mcp runtime-target binding refused: {error.code}: {error.field}",
            file=sys.stderr,
        )
        raise SystemExit(1) from None
    transport = settings.http_transport
    if transport in ("http", "streamable-http", "sse"):
        try:
            host, port = _resolve_http_bind()
        except ValueError as error:
            print(f"qa-mcp HTTP bind refused: {error}", file=sys.stderr)
            raise SystemExit(1) from None
        if transport == "sse":
            server.run(transport="sse", host=host, port=port, show_banner=False)
        else:
            _run_streamable_http_with_utf8_gate(host, port, server)
    else:
        server.run(show_banner=False)


if __name__ == "__main__":
    main()
