"""Application-owned list diagnostics at real factories and fake effect boundaries.

Only capture/table fixtures, native list replay, HTTP and XTEST effects are
substituted. Display construction, refresh/sweep, error serialization, uncertain
zero classification and remote-diagnostic gating remain real.
"""
from __future__ import annotations

import asyncio
import json
import os
import socket
import urllib.error
from io import BytesIO
from pathlib import Path

import pytest

from qa_mcp import mcp_server as srv
from qa_mcp.config import Settings
from qa_mcp.core import activate_application_context
from qa_mcp.protocol import display_backend as db, native_write, native_xtest

TOKEN = "SYNTHETIC-LIST-TOKEN"
PRIVATE = "SYNTHETIC-LIST-PRIVATE"


class ListEffects:
    def __init__(self):
        self.http = []
        self.local = []
        self.failure = "typed"
        self.failed_actions = {"F5", "Escape"}
        self.failed_diagnostics = False

    def fail(self):
        if self.failure == "generic":
            raise RuntimeError(f"{TOKEN} {PRIVATE} " + "x" * 4096)
        code = "foreground-denied" if self.failure == "typed" else TOKEN + "x" * 4096
        raise db.DisplayBackendError(code, PRIVATE, status=409, payload={"token": TOKEN})

    def urlopen(self, request, timeout):
        body = json.loads(request.data) if request.data else {}
        self.http.append((request.full_url, body, timeout, request.get_header("X-qa-mcp-agent-token")))
        if request.full_url.endswith("/v1/capabilities"):
            value = {
                "api": db.HOST_BRIDGE_API, "api_major": db.HOST_BRIDGE_API_MAJOR,
                "version": db.HOST_AGENT_VERSION,
                "display_protocol": db.HOST_AGENT_DISPLAY_PROTOCOL,
                "capabilities": sorted(db.HOST_BRIDGE_REQUIRED_CAPABILITIES),
            }
        else:
            failing = bool(set(body.get("keys", [])) & self.failed_actions)
            failing |= self.failed_diagnostics and request.full_url.endswith(("/window_list", "/uia/visible_list_cells"))
            if failing:
                if self.failure == "generic":
                    self.fail()
                code = "foreground-denied" if self.failure == "typed" else TOKEN + "x" * 4096
                error = json.dumps({"ok": False, "error": code, "detail": PRIVATE, "token": TOKEN}).encode()
                raise urllib.error.HTTPError(request.full_url, 409, "Conflict", None, BytesIO(error))
            value = {"ok": True, "windows": [], "cells": []}
        response = BytesIO(json.dumps(value).encode())
        response.headers = {"Content-Type": "application/json"}
        return response

    def send_keys(self, keys, **kwargs):
        self.local.append((keys, kwargs))
        if set(keys) & self.failed_actions:
            self.fail()
        return {"ok": True}


@pytest.fixture
def effects(monkeypatch):
    effect = ListEffects()
    def forbidden(*args, **kwargs):
        pytest.fail("unexpected live socket")
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(db.urllib.request, "urlopen", effect.urlopen)
    monkeypatch.setattr(native_xtest, "send_keys", effect.send_keys)
    monkeypatch.setattr(srv, "resolve_capture_dir", lambda *a, **kw: Path("/synthetic-capture"))
    monkeypatch.setattr(srv, "derive_search_list", lambda *a, **kw: object())
    monkeypatch.setattr(srv, "native_search_list", lambda *a, **kw: {"echoed": True})
    # Descriptor/table selection and captured replay are outside display routing.
    monkeypatch.setattr(srv, "_resolve_list_table_for_read", lambda **kw: ("Список", {"source": "fixture"}))
    monkeypatch.setattr(native_write, "derive_read_list_column", lambda *a, **kw: object())
    monkeypatch.setattr(native_write, "read_list_grid_replay", lambda *a, **kw: {"nav_link": "fixture", "rows": [], "row_count": 0})
    monkeypatch.setattr(native_write, "read_list_row_replay", lambda *a, **kw: {"nav_link": "fixture", "row": {"Name": None}})
    monkeypatch.setattr(native_write, "read_list_column_replay", lambda *a, **kw: {"nav_link": "fixture", "column": "Name", "value": None, "captured_value": "fixture"})
    monkeypatch.setattr(srv, "LIST_POLL_ATTEMPTS", 2)
    monkeypatch.setattr(srv, "LIST_POLL_SETTLE_SEC", 0)
    return effect


def factory(monkeypatch, remote, *, missing=False, extra_tools=None):
    monkeypatch.setenv("QA_MCP_REMOTE_CLIENT", "0" if remote else "1")
    monkeypatch.setenv("QA_MCP_HOST_AGENT", "foreign.invalid:8999")
    monkeypatch.setenv("QA_MCP_HOST_AGENT_TOKEN", "FOREIGN-TOKEN")
    return srv.create_mcp_server(settings=Settings(
        manager_templates="synthetic-manager.json", value_read_templates="synthetic-values.json",
        remote_client=remote, host_agent="" if missing else "application.invalid:8123",
        host_agent_token=TOKEN, host_agent_client_port=15444, host_agent_timeout=7,
    ), extra_tools=extra_tools)


def invoke(app, tool, **updates):
    args = {"value": "x"} if tool == "search_list" else {"open_link": "e1cib/list/Catalog.Fixture"}
    if tool in {"read_list_grid", "read_list_row"}:
        args["columns"] = ["Name"]
    if tool == "read_list_column":
        args["column"] = "Name"
    args.update(updates)
    return asyncio.run(app.call_tool(tool, args)).structured_content


def assert_safe(result):
    serialized = json.dumps(result)
    assert TOKEN not in serialized and PRIVATE not in serialized and "FOREIGN-TOKEN" not in serialized
    assert "foreign.invalid" not in serialized
    assert len(serialized) < 6000


def assert_effect_owner(effects, remote, missing=False):
    if remote:
        assert effects.local == []
        if missing:
            assert effects.http == []
        else:
            assert effects.http
            for url, body, timeout, token in effects.http:
                assert url.startswith("http://application.invalid:8123/")
                assert token == TOKEN and timeout == 7
                if not url.endswith("/v1/capabilities"):
                    assert body["client_port"] == 15444
    else:
        assert effects.http == []
        assert effects.local


@pytest.mark.parametrize("tool", ["search_list", "read_list_grid", "read_list_row", "read_list_column"])
@pytest.mark.parametrize("remote", [True, False], ids=["remote-app-local-env", "local-app-remote-env"])
@pytest.mark.parametrize("failure", ["typed", "unknown-code", "generic"])
def test_public_list_errors_use_application_mode_and_safe_serialization(monkeypatch, effects, tool, remote, failure):
    effects.failure = failure
    app = factory(monkeypatch, remote)
    before = dict(os.environ)
    result = invoke(app, tool)
    expected_mode = "remote-client" if remote else "local"
    expected_code = {"typed": "foreground-denied", "unknown-code": "host-agent-error", "generic": "display-backend-error"}[failure]
    error = result["list_refresh"]["error"]
    assert error["mode"] == expected_mode and error["error"] == expected_code
    assert len(json.dumps(error)) < 512
    if tool != "search_list":
        assert result["error"] == "list-read-uncertain-zero" and result["ok"] is False
        assert result["underlying_error"] == error
        assert result["list_refresh"]["sweep_error"]["mode"] == expected_mode
        if remote:
            assert result["remote_window_diagnostic"]["mode"] == expected_mode
            assert result["remote_window_diagnostic"]["window_count"] == 0
            assert result["remote_window_diagnostic"]["visible_cells"]["cells"] == []
        else:
            assert "remote_window_diagnostic" not in result
    assert_safe(result)
    assert_effect_owner(effects, remote)
    assert dict(os.environ) == before


@pytest.mark.parametrize("tool", ["search_list", "read_list_grid", "read_list_row", "read_list_column"])
def test_public_list_missing_remote_address_never_inherits_process_host(monkeypatch, effects, tool):
    app = factory(monkeypatch, True, missing=True)
    before = dict(os.environ)
    result = invoke(app, tool)
    assert result["list_refresh"]["error"]["error"] == "host-agent-not-configured"
    assert result["list_refresh"]["error"]["mode"] == "remote-client"
    if tool != "search_list":
        for name in ["window_error", "visible_cells_error"]:
            error = result["remote_window_diagnostic"][name]
            assert error["mode"] == "remote-client"
            assert error["error"] == "host-agent-not-configured"
    assert_safe(result)
    assert_effect_owner(effects, True, missing=True)
    assert dict(os.environ) == before


@pytest.mark.parametrize("failed_action", ["F5", "Escape"])
def test_refresh_and_sweep_failures_remain_distinguishable(monkeypatch, effects, failed_action):
    effects.failed_actions = {failed_action}
    app = factory(monkeypatch, True)
    result = invoke(app, "read_list_grid")
    refresh = result["list_refresh"]
    if failed_action == "F5":
        assert refresh["method"] == "none" and "sweep_error" not in refresh
        assert refresh["error"]["tool"] == "force_list_refresh"
    else:
        assert refresh["method"] == "f5" and "error" not in refresh
        assert refresh["sweep_error"]["tool"] == "cold_state_sweep"
    assert result["underlying_error"]["mode"] == "remote-client"
    assert_safe(result)
    assert_effect_owner(effects, True)


@pytest.mark.parametrize("remote", [True, False])
def test_descriptor_uncertain_zero_uses_application_mode_without_refresh_error(monkeypatch, effects, remote):
    monkeypatch.setattr(srv, "LIST_POLL_ATTEMPTS", 1)
    app = factory(monkeypatch, remote)
    result = invoke(app, "read_list_column", refresh=False)
    assert "error" not in result["list_refresh"]
    assert result["underlying_error"]["error"] == "window-discovery-unconfirmed"
    assert result["underlying_error"]["mode"] == ("remote-client" if remote else "local")
    assert ("remote_window_diagnostic" in result) is remote
    assert_safe(result)
    assert_effect_owner(effects, remote)


@pytest.mark.parametrize("remote", [True, False])
def test_refresh_unconfirmed_metadata_is_classified_inside_real_factory(monkeypatch, effects, remote):
    # Exercise the no-error legacy metadata branch without replacing its classifier
    # or diagnostic guard. Normal failing refreshes already carry typed errors.
    def classify() -> dict:
        return srv._mark_uncertain_zero_list_read({}, tool="probe", zero_data=True,
            refresh=True, fresh={"refresh_method": "none"})
    app = factory(monkeypatch, remote, extra_tools={"classify": classify})
    result = asyncio.run(app.call_tool("classify", {})).structured_content
    assert result["underlying_error"]["error"] == "refresh-not-confirmed"
    assert result["underlying_error"]["mode"] == ("remote-client" if remote else "local")
    assert ("remote_window_diagnostic" in result) is remote
    if not remote:
        assert effects.local == effects.http == []
    assert_safe(result)


@pytest.mark.parametrize("failure", ["typed", "unknown-code", "generic"])
def test_window_and_visible_cell_diagnostic_failures_share_safe_mode(monkeypatch, effects, failure):
    effects.failure = failure
    effects.failed_diagnostics = True
    app = factory(monkeypatch, True)
    result = invoke(app, "read_list_grid")
    diagnostic = result["remote_window_diagnostic"]
    for name in ["window_error", "visible_cells_error"]:
        assert diagnostic[name]["mode"] == "remote-client"
        assert len(json.dumps(diagnostic[name])) < 512
    assert_safe(result)
    assert_effect_owner(effects, True)


@pytest.mark.parametrize("remote", [True, False])
def test_legacy_display_diagnostics_keep_explicit_env_adapter_behavior(monkeypatch, effects, remote):
    # Enter the original direct-call context even after creating other factories.
    app = factory(monkeypatch, not remote)
    del app
    monkeypatch.setenv("QA_MCP_REMOTE_CLIENT", "1" if remote else "0")
    monkeypatch.setenv("QA_MCP_HOST_AGENT", "application.invalid:8123")
    monkeypatch.setenv("QA_MCP_HOST_AGENT_TOKEN", TOKEN)
    monkeypatch.setenv("QA_MCP_HOST_AGENT_CLIENT_PORT", "15444")
    monkeypatch.setenv("QA_MCP_HOST_AGENT_TIMEOUT", "7")
    before = dict(os.environ)
    with activate_application_context(srv._DEFAULT_APPLICATION_CONTEXT):
        method, error = srv._force_list_refresh()
        swept, sweep_error = srv._cold_state_sweep(return_error=True)
        diagnostic = srv._remote_client_list_diagnostic("legacy")
        generic = srv._display_backend_error_result("legacy", ValueError(PRIVATE))
    assert method == "none" and swept is False
    assert error["mode"] == sweep_error["mode"] == generic["mode"] == ("remote-client" if remote else "local")
    assert (diagnostic is not None) is remote
    assert_safe([error, sweep_error, diagnostic, generic])
    assert_effect_owner(effects, remote)
    assert dict(os.environ) == before
