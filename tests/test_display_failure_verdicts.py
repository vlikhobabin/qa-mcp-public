"""Acceptance proofs for truthful window-list operation verdicts."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from tests.support.runtime_targets import TargetProfileInputs

from qa_mcp import mcp_server
from qa_mcp.config import Settings
from qa_mcp.core import (
    HandlerQAExecutor,
    OperationKind,
    OperationRequest,
    OperationResult,
    OperationVerdict,
    activate_application_context,
    resolve_runtime_target,
)


class DisplayFixture:
    name = "fixture-display"

    def __init__(self, outcome: Any) -> None:
        self.outcome = outcome
        self.calls: list[tuple[str, bool]] = []

    def list_windows(self, display: str, *, geometry: bool = True) -> list[dict[str, Any]]:
        self.calls.append((display, geometry))
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        return list(self.outcome)


def _settings(*, remote: bool = False) -> Settings:
    return Settings.from_env({
        "QA_MCP_CLIENT_HOST": "host.docker.internal" if remote else "127.0.0.1",
        "QA_MCP_CLIENT_PORT": "15444",
        "QA_MCP_REMOTE_CLIENT": "1" if remote else "0",
        "QA_MCP_HOST_AGENT_CLIENT_PORT": "15445" if remote else "0",
    })


def _resolution(tmp_path: Path):
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    base = tmp_path / "base"
    base.mkdir()
    platform = tmp_path / "platform"
    platform.mkdir()
    (platform / "1cv8").write_text("binary", encoding="utf-8")
    inputs = TargetProfileInputs(
        tmp_path, target_kind="file", principal="principal", evidence_policy="sanitized",
    )
    (tmp_path / "target.env").write_text(
        f"INFOBASE_PATH={base}\nPLATFORM_ROOT={platform}\n"
        "TEST_CLIENT_USER=Declared\nTEST_CLIENT_PASSWORD=PRIVATE-SENTINEL\n"
        "SRC_ROOT=/PRIVATE/SOURCE\n",
        encoding="utf-8",
    )
    inputs.write_profile()
    result = resolve_runtime_target(inputs.handoff_env())
    assert result is not None
    return result


def _bound_server(tmp_path: Path, *, remote: bool = False):
    resolution = _resolution(tmp_path)
    server = mcp_server.create_mcp_server(
        settings=_settings(remote=remote), runtime_target=resolution,
    )
    context = mcp_server.application_context(server)
    with activate_application_context(context):
        mcp_server._remember_bound_testclient(
            {
                "host": "host.docker.internal" if remote else "127.0.0.1",
                "port": 15444,
                "pid": 4321,
                "alive": True,
                "listening": True,
                "owns_process": True,
                "display": ":109" if not remote else "",
                "client_target": (
                    {"kind": "host-agent-testclient", "lifecycle_id": "remote-7", "pid": 4321, "port": 15445}
                    if remote else None
                ),
            },
            operation="launch_test_client", ownership_class="owned", lifecycle_id="local-7" if not remote else "remote-7",
        )
    return server, context


def _payload(server: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["get_window_list"]
    result = asyncio.run(tool.run(arguments))
    return json.loads(result.content[0].text)


@pytest.mark.parametrize("remote", [False, True])
@pytest.mark.parametrize("failure", [
    mcp_server.client_display.DisplayBackendError(
        "window-not-found", "SECRET caption /PRIVATE/path token=PRIVATE", status=404,
        install_command="PRIVATE install command",
    ),
    RuntimeError("SECRET backend prose /PRIVATE/path"),
])
def test_c1_registered_bound_failures_remain_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, remote: bool, failure: BaseException,
) -> None:
    backend = DisplayFixture(failure)
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    if remote:
        monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda **_kwargs: True)
    server, _context = _bound_server(tmp_path, remote=remote)
    payload = _payload(server, {"geometry": False})
    assert backend.calls == [("" if remote else ":109", False)]
    assert payload["verdict"] == "failure"
    assert payload["error"]["code"] == "executor-failure"
    serialized = json.dumps(payload)
    assert all(fragment not in serialized for fragment in ("SECRET", "/PRIVATE/path", "PRIVATE install command"))


def test_c1_unbound_registered_failures_and_actual_backend_call(monkeypatch: pytest.MonkeyPatch) -> None:
    backend = DisplayFixture(mcp_server.client_display.DisplayBackendError("window-not-found", "hostile"))
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    server = mcp_server.create_mcp_server(settings=_settings())
    payload = _payload(server, {"display": ":77", "geometry": True})
    assert backend.calls == [(":77", True)]
    assert payload["verdict"] == "failure"
    assert payload["error"]["code"] == "window-not-found"


def test_c2_inventory_counts_and_explicit_generic_verdicts(monkeypatch: pytest.MonkeyPatch) -> None:
    for windows in ([], [{"id": "7", "title": "Fixture"}]):
        backend = DisplayFixture(windows)
        monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
        server = mcp_server.create_mcp_server(settings=_settings())
        payload = _payload(server, {"display": ":77", "geometry": False})
        # Unbound composed success retains the documented direct inventory DTO.
        assert payload["count"] == len(windows)
        assert backend.calls == [(":77", False)]

    request = OperationRequest(OperationKind.READ, "unrelated")
    value = {"ok": False, "error": "data", "verdict": "not-a-result"}
    executor = HandlerQAExecutor({(request.kind, request.name): lambda _request: value})
    result = executor.execute(request, target=None, session=None)
    assert result.verdict is OperationVerdict.SUCCESS and result.value == value

    typed = OperationResult.failure(request, code="typed", message="typed failure")
    executor = HandlerQAExecutor({(request.kind, request.name): lambda _request: typed})
    assert executor.execute(request, target=None, session=None) is typed


def test_c2_old_window_adapter_is_a_scoped_sensitivity_control(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend = DisplayFixture(mcp_server.client_display.DisplayBackendError("window-not-found", "hostile"))
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    _server, context = _bound_server(tmp_path)
    context.executor._handlers[(OperationKind.READ, "get_window_list")] = (
        lambda request: mcp_server._get_window_list_impl(**dict(request.arguments))
    )
    result = context.executor.execute(
        OperationRequest(OperationKind.READ, "get_window_list", {"display": ":109", "geometry": False}),
        target=context.target, session=context.session,
    )
    with pytest.raises(AssertionError):
        assert result.verdict is OperationVerdict.FAILURE


def test_c3_direct_legacy_error_and_inventory_shapes(monkeypatch: pytest.MonkeyPatch) -> None:
    typed_backend = DisplayFixture(mcp_server.client_display.DisplayBackendError("window-not-found", "private"))
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: typed_backend)
    legacy_error = mcp_server.get_window_list(":77", geometry=False)
    assert legacy_error["ok"] is False and legacy_error["error"] == "window-not-found"

    inventory = DisplayFixture([{"id": "1", "title": "Fixture"}, {"id": "2", "title": "Other"}])
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: inventory)
    legacy_success = mcp_server.get_window_list(":77", geometry=False)
    assert legacy_success["count"] == 2 and len(legacy_success["windows"]) == 2
