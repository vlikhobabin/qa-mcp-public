"""Project schemas, representative evidence and teardown stay target-bound."""

from __future__ import annotations

import asyncio
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType, SimpleNamespace
from typing import Any

import pytest

from tests.support.runtime_targets import TargetProfileInputs

import qa_mcp.data as qa_data
from qa_mcp import mcp_server
from qa_mcp.config import Settings
from qa_mcp.core import (
    ArtifactReference,
    OperationKind,
    OperationRequest,
    OperationResult,
    SessionIdentity,
    WindowsHostQAExecutor,
    activate_application_context,
    execute_mcp_operation,
    resolve_runtime_target,
)


def _handoff_env(tmp_path: Path, *, target_kind: str = "file") -> dict[str, str]:
    return TargetProfileInputs(tmp_path, target_kind=target_kind, principal="principal").handoff_env()


def _resolution(
    tmp_path: Path, *, evidence_policy: str = "sanitized", target_kind: str = "file",
):
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    base = tmp_path / "base"
    base.mkdir()
    platform = tmp_path / "platform"
    platform.mkdir()
    (platform / "1cv8").write_text("binary", encoding="utf-8")
    physical = tmp_path / "target.env"
    target_config = (
        f"INFOBASE_PATH={base}\n"
        if target_kind == "file"
        else 'CONNECTION_STRING=Srvr="private";Ref="qa";Pwd="PRIVATE-CONNECTION"\n'
    )
    physical.write_text(
        target_config + f"PLATFORM_ROOT={platform}\n"
        "TEST_CLIENT_USER=Declared\nTEST_CLIENT_PASSWORD=PRIVATE-SENTINEL\n"
        "SRC_ROOT=/PRIVATE/SOURCE\n",
        encoding="utf-8",
    )
    inputs = TargetProfileInputs(
        tmp_path, target_kind=target_kind, principal="principal",
        evidence_policy=evidence_policy,
        non_production_approved=evidence_policy == "full_local",
    )
    inputs.write_profile()
    result = resolve_runtime_target(inputs.handoff_env())
    assert result is not None
    return result


def _settings(*, remote: bool = False) -> Settings:
    return Settings.from_env({
        "QA_MCP_CLIENT_HOST": "host.docker.internal" if remote else "127.0.0.1",
        "QA_MCP_CLIENT_PORT": "15444",
        "QA_MCP_REMOTE_CLIENT": "1" if remote else "0",
        "QA_MCP_HOST_AGENT_CLIENT_PORT": "15445" if remote else "0",
    })


def _context(
    tmp_path: Path, *, remote: bool = False, executor: Any = None,
    evidence_policy: str = "sanitized", extra_tools: dict[str, Any] | None = None,
):
    resolution = _resolution(tmp_path, evidence_policy=evidence_policy)
    server = mcp_server.create_mcp_server(
        settings=_settings(remote=remote), runtime_target=resolution, executor=executor,
        extra_tools=extra_tools,
    )
    return server, mcp_server.application_context(server)


def test_bound_schemas_hide_target_endpoint_credentials_and_retention(tmp_path: Path) -> None:
    bound, _ = _context(tmp_path)
    unbound = mcp_server.create_mcp_server(settings=_settings())
    bound_tools = {tool.name: tool for tool in asyncio.run(bound.list_tools())}
    unbound_tools = {tool.name: tool for tool in asyncio.run(unbound.list_tools())}

    assert set(bound_tools["launch_test_client"].parameters["properties"]) == {
        "headless", "manage_apache", "wait_sec", "use_hardware_licenses",
    }
    assert set(bound_tools["attach_test_client"].parameters["properties"]) == {
        "connect_timeout_sec",
    }
    assert bound_tools["test_client_status"].parameters["properties"] == {}
    assert bound_tools["stop_test_client"].parameters["properties"] == {}
    assert set(bound_tools["get_window_list"].parameters["properties"]) == {"geometry"}
    assert set(bound_tools["capture_screenshot"].parameters["properties"]) == {"window"}
    forbidden = {
        "host", "port", "env_file", "infobase_path", "connection_string",
        "com_infobase_path", "com_user", "com_password", "com_query", "out_path",
        "out_dir", "base_url", "user", "password", "odata_password", "display",
        "capture_dir", "manager_templates", "src_root", "enum_src_root",
    }
    def property_names(value: Any) -> set[str]:
        if isinstance(value, dict):
            names = set(value.get("properties", {}))
            return names.union(*(property_names(item) for item in value.values()))
        if isinstance(value, list):
            return set().union(*(property_names(item) for item in value))
        return set()

    assert all(forbidden.isdisjoint(property_names(tool.parameters)) for tool in bound_tools.values())
    assert "role_data_matrix" not in bound_tools
    assert {"host", "port"} <= set(unbound_tools["attach_test_client"].parameters["properties"])
    assert "out_path" in unbound_tools["capture_screenshot"].parameters["properties"]
    assert "base_url" in unbound_tools["assert_data"].parameters["properties"]
    assert "role_data_matrix" in unbound_tools
    assert "out_dir" in unbound_tools["write_test_report"].parameters["properties"]


def test_public_tool_classification_covers_both_profiles_and_direct_routes() -> None:
    classifications = mcp_server._TOOL_ROUTE_CLASSIFICATIONS
    standalone = set(mcp_server.profile_tool_names("standalone"))
    research = set(mcp_server.profile_tool_names("research"))

    assert standalone <= research == set(mcp_server._TOOL_CATALOG)
    assert set(classifications) == research
    assert set(classifications.values()) == {
        "native-session-bound", "lifecycle", "provider-data", "pure/readiness",
    }
    assert {
        name for name, fn in mcp_server._TOOL_CATALOG.items()
        if getattr(fn, "_qa_mcp_testclient_tool", False)
    } <= mcp_server._NATIVE_SESSION_BOUND_TOOLS
    assert {"click_command", "get_window_list", "capture_screenshot", "open_external_processor"} <= (
        mcp_server._NATIVE_SESSION_BOUND_TOOLS
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "session", "attachment", "generation", "runtime-target",
        "stale-sequence", "future-sequence", "malformed-ledger", "malformed-guard",
    ],
)
def test_registered_click_command_blocks_before_hidden_or_native_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str,
) -> None:
    server, context = _context(tmp_path)
    session = SessionIdentity("session-7", context.target, 7)
    context.session = session
    context.attachment = mcp_server._AttachedTestClientContext(
        "127.0.0.1", 15444, 1.0, {}, target=context.target, session=session,
        binding_generation=7, ownership_class="owned", lifecycle_id="local-7", display=":109",
    )
    if mutation == "session":
        context.session = None
    elif mutation == "attachment":
        context.attachment = None
    elif mutation == "generation":
        context.attachment = replace(context.attachment, binding_generation=8)
    elif mutation == "runtime-target":
        object.__setattr__(context, "runtime_target", None)
    elif mutation in {"stale-sequence", "future-sequence"}:
        sequence = 6 if mutation == "stale-sequence" else 8
        context.session = SessionIdentity("session-7", context.target, sequence)
        context.attachment = replace(context.attachment, session=context.session)
    elif mutation == "malformed-ledger":
        object.__setattr__(context, "evidence_ledger", None)
    else:
        object.__setattr__(context, "_operation_boundary_guard", None)
    before = (
        context.target, context.runtime_target, context.session, context.attachment,
        context.evidence_ledger, context._operation_boundary_guard,
    )
    effects: list[object] = []
    monkeypatch.setattr(
        mcp_server, "_resolve_testclient_endpoint",
        lambda *_args, **_kwargs: effects.append("endpoint") or pytest.fail("endpoint was probed"),
    )
    monkeypatch.setattr(
        mcp_server, "native_click_command",
        lambda *_args, **_kwargs: effects.append("native") or {"ok": True},
    )

    tool = {item.name: item for item in asyncio.run(server.list_tools())}["click_command"]
    payload = json.loads(asyncio.run(tool.run({"target_button": "PF_SAVE"})).content[0].text)

    assert payload["error"]["code"] == "runtime-target-route-blocked"
    assert effects == []
    assert (
        context.target, context.runtime_target, context.session, context.attachment,
        context.evidence_ledger, context._operation_boundary_guard,
    ) == before


@pytest.mark.parametrize("sequence", [6, 8])
def test_stale_or_future_session_sequence_blocks_registered_and_shared_routes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, sequence: int,
) -> None:
    calls: list[OperationRequest] = []

    class Executor:
        name = "external-spy"

        def execute(self, request, *, target, session):
            calls.append(request)
            return OperationResult.success(request, value={"unexpected": True})

    server, context = _context(tmp_path, executor=Executor())
    session = SessionIdentity("session-7", context.target, sequence)
    context.session = session
    context.attachment = mcp_server._AttachedTestClientContext(
        "127.0.0.1", 15444, 1.0, {}, target=context.target, session=session,
        binding_generation=7, ownership_class="owned", lifecycle_id="local-7", display=":109",
    )
    before = (context.target, context.runtime_target, context.session, context.attachment)
    effects: list[object] = []
    monkeypatch.setattr(
        mcp_server, "_resolve_testclient_endpoint",
        lambda *_args, **_kwargs: effects.append("endpoint") or pytest.fail("endpoint was probed"),
    )
    monkeypatch.setattr(
        mcp_server, "native_click_command",
        lambda *_args, **_kwargs: effects.append("native") or {"ok": True},
    )

    tool = {item.name: item for item in asyncio.run(server.list_tools())}["click_command"]
    payload = json.loads(asyncio.run(tool.run({"target_button": "PF_SAVE"})).content[0].text)
    shared = execute_mcp_operation(
        context, OperationRequest(OperationKind.WRITE, "click_command", {}),
    )

    assert payload["error"]["code"] == "runtime-target-route-blocked"
    assert shared.error and shared.error.code == "runtime-target-route-blocked"
    assert effects == [] and calls == []
    assert (context.target, context.runtime_target, context.session, context.attachment) == before


def test_bound_unknown_extension_blocks_before_callback_and_unbound_extension_remains_usable(
    tmp_path: Path,
) -> None:
    calls: list[object] = []

    def future_native_route() -> dict[str, bool]:
        calls.append(mcp_server.current_application_context())
        return {"ok": True}

    bound, bound_context = _context(
        tmp_path, extra_tools={"future_native_route": future_native_route},
    )
    before = (
        bound_context.target, bound_context.runtime_target,
        bound_context.session, bound_context.attachment,
    )
    bound_tool = {item.name: item for item in asyncio.run(bound.list_tools())}["future_native_route"]
    blocked = json.loads(asyncio.run(bound_tool.run({})).content[0].text)

    unbound = mcp_server.create_mcp_server(
        settings=_settings(), extra_tools={"future_native_route": future_native_route},
    )
    unbound_context = mcp_server.application_context(unbound)
    unbound_tool = {item.name: item for item in asyncio.run(unbound.list_tools())}["future_native_route"]
    admitted = json.loads(asyncio.run(unbound_tool.run({})).content[0].text)

    assert blocked["error"]["code"] == "runtime-target-route-blocked"
    assert calls == [unbound_context]
    assert admitted == {"ok": True}
    assert (
        bound_context.target, bound_context.runtime_target,
        bound_context.session, bound_context.attachment,
    ) == before


def test_registered_click_command_gate_sensitivity_reaches_native_only_when_bypassed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The C1 zero-effect control is sensitive to removal of registered admission."""

    server, _ = _context(tmp_path)
    effects: list[tuple[str | None, str, int]] = []
    monkeypatch.setattr(mcp_server, "_bound_tool_preflight", lambda *_args: None)
    monkeypatch.setattr(mcp_server, "derive_command_click", lambda *_args: object())
    monkeypatch.setattr(
        mcp_server, "_resolve_testclient_endpoint", lambda host, port, **_kwargs: (host, port, None),
    )
    monkeypatch.setattr(
        mcp_server,
        "native_click_command",
        lambda _template, target_button, *, host, port: effects.append(
            (target_button, host, port)
        ) or {"ok": True},
    )

    tool = {item.name: item for item in asyncio.run(server.list_tools())}["click_command"]
    asyncio.run(tool.run({"target_button": "PF_SAVE"}))

    assert effects == [("PF_SAVE", "127.0.0.1", 15444)]


def test_schema_missing_and_unknown_bound_operations_fail_closed_before_executor(tmp_path: Path) -> None:
    calls: list[OperationRequest] = []

    class Executor:
        name = "external-spy"

        def execute(self, request, *, target, session):
            calls.append(request)
            return OperationResult.success(request, value={"unexpected": True})

    _, context = _context(tmp_path, executor=Executor())
    before = (context.target, context.runtime_target, context.session, context.attachment)
    known = execute_mcp_operation(
        context, OperationRequest(OperationKind.WRITE, "click_command", {}),
    )
    unknown = execute_mcp_operation(
        context, OperationRequest(OperationKind.WRITE, "future_native_route", {}),
    )

    assert [item.error.code for item in (known, unknown) if item.error] == [
        "runtime-target-route-blocked", "runtime-target-route-blocked",
    ]
    assert calls == []
    assert (context.target, context.runtime_target, context.session, context.attachment) == before


@pytest.mark.parametrize("target_kind", ["file", "client-server"])
def test_registered_hidden_consumer_keeps_admitted_snapshot_after_fixture_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, target_kind: str,
) -> None:
    resolution = _resolution(tmp_path, target_kind=target_kind)
    physical = resolution.profile.physical_env_file
    physical.write_text(
        "INFOBASE_PATH=/changed/base\nPLATFORM_ROOT=/changed/platform\n"
        "TEST_CLIENT_USER=Changed\nTEST_CLIENT_PASSWORD=CHANGED-SECRET\nSRC_ROOT=/changed/src\n",
        encoding="utf-8",
    )
    captured: list[dict[str, str]] = []

    def query_com(
        infobase_path: str, connection_string: str, user: str, password: str, src_root: str,
        query: str,
    ) -> dict[str, bool]:
        captured.append({
            "infobase_path": infobase_path,
            "connection_string": connection_string,
            "user": user,
            "password": password,
            "src_root": src_root,
        })
        return {"ok": bool(query)}

    monkeypatch.setitem(mcp_server._TOOL_CATALOG, "query_com", query_com)
    server = mcp_server.create_mcp_server(settings=_settings(), runtime_target=resolution)
    tool = {item.name: item for item in asyncio.run(server.list_tools())}["query_com"]
    result = json.loads(asyncio.run(tool.run({"query": "SELECT 1"})).content[0].text)

    assert result == {"ok": True}
    assert captured == [{
        "infobase_path": str(tmp_path / "base") if target_kind == "file" else "",
        "connection_string": "" if target_kind == "file" else 'Srvr="private";Ref="qa";Pwd="PRIVATE-CONNECTION"',
        "user": "Declared",
        "password": "PRIVATE-SENTINEL",
        "src_root": "/PRIVATE/SOURCE",
    }]


def test_new_resolution_is_the_only_snapshot_rebind_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = _resolution(tmp_path)
    physical = original.profile.physical_env_file
    changed_base = tmp_path / "changed-base"
    changed_base.mkdir()
    changed_platform = tmp_path / "changed-platform"
    changed_platform.mkdir()
    (changed_platform / "1cv8").write_text("binary", encoding="utf-8")
    physical.write_text(
        f"INFOBASE_PATH={changed_base}\nPLATFORM_ROOT={changed_platform}\n"
        "TEST_CLIENT_USER=Changed\nTEST_CLIENT_PASSWORD=CHANGED-SECRET\nSRC_ROOT=/changed/src\n",
        encoding="utf-8",
    )
    rebound = resolve_runtime_target(_handoff_env(tmp_path))
    assert rebound is not None and rebound.binding.target is not original.binding.target

    stale = SessionIdentity("old", original.binding.target, sequence=7)
    with pytest.raises(ValueError, match="session"):
        mcp_server.create_mcp_server(
            settings=_settings(), runtime_target=rebound, session=stale,
        )
    admitted = SessionIdentity("new", rebound.binding.target, sequence=7)
    server = mcp_server.create_mcp_server(
        settings=_settings(), runtime_target=rebound, session=admitted,
    )
    assert mcp_server.application_context(server).session is admitted

    targets: list[Any] = []

    class Handle:
        def status(self):
            return {"pid": 321, "alive": True, "listening": True, "owns_process": True}

    old_server = mcp_server.create_mcp_server(settings=_settings(), runtime_target=original)
    monkeypatch.setattr(
        mcp_server.client_lifecycle, "launch_test_client",
        lambda target, **_kwargs: targets.append(target) or Handle(),
    )
    with activate_application_context(mcp_server.application_context(old_server)):
        mcp_server.launch_test_client(port=15444, wait_sec=0)
    with activate_application_context(mcp_server.application_context(server)):
        mcp_server.launch_test_client(port=15444, wait_sec=0)

    assert [(target.infobase_path, target.user, target.password) for target in targets] == [
        (str(tmp_path / "base"), "Declared", "PRIVATE-SENTINEL"),
        (str(changed_base), "Changed", "CHANGED-SECRET"),
    ]


@pytest.mark.parametrize("target_kind", ["file", "client-server"])
def test_bound_registered_diagnostics_serialize_only_logical_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, target_kind: str,
) -> None:
    resolution = _resolution(tmp_path, target_kind=target_kind)
    server = mcp_server.create_mcp_server(settings=_settings(), runtime_target=resolution)
    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", lambda *_args: False)

    payloads = [
        json.loads(asyncio.run(tools["infobase_info"].run({})).content[0].text),
        json.loads(asyncio.run(tools["get_state"].run({})).content[0].text),
    ]
    encoded = json.dumps(payloads)

    assert all(payload["target"] == {
        "logical_id": "project-demo",
        "kind": target_kind,
        "fingerprint": "sha256:" + "a" * 64,
        "binding_ref": "qa-demo",
        "binding_generation": 7,
    } for payload in payloads)
    for marker in (
        str(tmp_path / "base"), "PRIVATE-CONNECTION", "Declared", "PRIVATE-SENTINEL",
        str(tmp_path / "platform"), "/PRIVATE/SOURCE",
    ):
        assert marker not in encoded


def test_bound_endpoint_and_output_overrides_fail_before_side_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    server, _ = _context(tmp_path)
    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    odata_calls: list[tuple[Any, ...]] = []
    monkeypatch.setattr(qa_data, "ODataClient", lambda *args: odata_calls.append(args) or object())
    monkeypatch.setattr(qa_data, "assert_data_value", lambda *_args, **_kwargs: {"ok": True})

    try:
        asyncio.run(tools["assert_data"].run({
            "entity_set": "Catalog_Items", "field": "Code", "expected": "1",
            "base_url": "https://attacker.invalid/odata/",
        }))
    except Exception:
        pass
    hostile_output = tmp_path / "model-output"
    try:
        asyncio.run(tools["write_test_report"].run({"out_dir": str(hostile_output)}))
    except Exception:
        pass

    assert odata_calls == []
    assert not hostile_output.exists()


def test_bound_read_and_display_use_executor_identity_and_sanitized_artifact(tmp_path: Path) -> None:
    calls: list[tuple[OperationRequest, Any, Any]] = []

    class Executor:
        name = "spy"

        def execute(self, request, *, target, session):
            calls.append((request, target, session))
            if request.kind is OperationKind.DISPLAY:
                return OperationResult(
                    request, mcp_server.OperationVerdict.SUCCESS,
                    value={"size_bytes": 7, "path": "/PRIVATE/raw.png"},
                    artifacts=(ArtifactReference(
                        "screenshot.0123456789abcdef", "image/png",
                        "sha256:" + "a" * 64, "/PRIVATE/raw.png", "internal",
                    ),),
                )
            return OperationResult.success(
                request, value={"count": 0, "windows": [{"title": "PRIVATE-UI"}]},
            )

    server, context = _context(tmp_path, executor=Executor())
    session = SessionIdentity("session-7", context.target, 7)
    context.session = session
    context.attachment = mcp_server._AttachedTestClientContext(
        "127.0.0.1", 15444, 1.0, {}, target=context.target, session=session,
        binding_generation=7, ownership_class="owned", lifecycle_id="local-7", display=":109",
    )
    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    read = asyncio.run(tools["get_window_list"].run({"geometry": False}))
    display = asyncio.run(tools["capture_screenshot"].run({"window": None}))
    read_payload = read.content[0].text
    display_payload = display.content[0].text

    assert [item[0].kind for item in calls] == [OperationKind.READ, OperationKind.DISPLAY], (
        calls, read_payload, display_payload
    )
    assert all(item[1] is context.target and item[2] is session for item in calls)
    assert '"provenance"' in read_payload and '"session":"session-7"' in read_payload
    assert "PRIVATE-UI" not in read_payload
    # A custom executor's metadata-only claim is not trusted production.
    display_result = json.loads(display_payload)
    assert display_result["verdict"] == "failure"
    assert display_result["error"]["code"] == "invalid-evidence-receipt"
    assert "artifacts" not in display_result
    assert display_result["provenance"]["session"] == "session-7"
    assert "PRIVATE/raw.png" not in display_payload


def test_registered_admitted_write_uses_exact_attachment_once_per_application(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A real registered write keeps each composed application's route isolated."""

    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    first_server, first = _context(first_root)
    second_server, second = _context(second_root)
    first_session = SessionIdentity("first-session", first.target, 7)
    second_session = SessionIdentity("second-session", second.target, 7)
    first.session = first_session
    second.session = second_session
    first.attachment = mcp_server._AttachedTestClientContext(
        "127.0.0.1", 15444, 1.0, {}, target=first.target, session=first_session,
        binding_generation=7, ownership_class="owned", lifecycle_id="first", display=":101",
    )
    second.attachment = mcp_server._AttachedTestClientContext(
        "127.0.0.1", 15445, 1.0, {}, target=second.target, session=second_session,
        binding_generation=7, ownership_class="owned", lifecycle_id="second", display=":102",
    )
    before = [
        (first.target, first.session, first.attachment),
        (second.target, second.session, second.attachment),
    ]
    calls: list[tuple[str | None, str, int, Any]] = []
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", lambda *_args: True)
    monkeypatch.setattr(
        mcp_server,
        "native_click_command",
        lambda _template, target_button, *, host, port: calls.append(
            (target_button, host, port, mcp_server.current_application_context())
        ) or {"ok": True, "accepted": True},
    )

    first_tool = {tool.name: tool for tool in asyncio.run(first_server.list_tools())}["click_command"]
    second_tool = {tool.name: tool for tool in asyncio.run(second_server.list_tools())}["click_command"]
    first_payload = json.loads(asyncio.run(first_tool.run({"target_button": "FIRST"})).content[0].text)
    second_payload = json.loads(asyncio.run(second_tool.run({"target_button": "SECOND"})).content[0].text)

    assert [call[:3] for call in calls] == [
        ("FIRST", "127.0.0.1", 15444),
        ("SECOND", "127.0.0.1", 15445),
    ]
    assert [call[3] for call in calls] == [first, second]
    assert first_payload["accepted"] is True and second_payload["accepted"] is True
    assert [
        (first.target, first.session, first.attachment),
        (second.target, second.session, second.attachment),
    ] == before


@pytest.mark.parametrize("dispatch", ["mcp", "registered-callback"])
def test_overlapping_registered_writes_keep_each_application_route_and_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, dispatch: str,
) -> None:
    first_root = tmp_path / "first-overlap"
    second_root = tmp_path / "second-overlap"
    first_root.mkdir()
    second_root.mkdir()
    first_server, first = _context(first_root)
    second_server, second = _context(second_root)
    first_session = SessionIdentity("first-session", first.target, 7)
    second_session = SessionIdentity("second-session", second.target, 7)
    first.session, second.session = first_session, second_session
    first.attachment = mcp_server._AttachedTestClientContext(
        "127.0.0.1", 15444, 1.0, {}, target=first.target, session=first_session,
        binding_generation=7, ownership_class="owned", lifecycle_id="first", display=":101",
    )
    second.attachment = mcp_server._AttachedTestClientContext(
        "127.0.0.1", 15445, 1.0, {}, target=second.target, session=second_session,
        binding_generation=7, ownership_class="owned", lifecycle_id="second", display=":102",
    )
    before = [
        (first.target, first.session, first.attachment),
        (second.target, second.session, second.attachment),
    ]
    barrier = threading.Barrier(2)
    calls: list[tuple[str | None, str, int, Any]] = []
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", lambda *_args: True)
    monkeypatch.setattr(
        mcp_server,
        "native_click_command",
        lambda _template, target_button, *, host, port: (
            calls.append((target_button, host, port, mcp_server.current_application_context())),
            barrier.wait(timeout=3),
            {"ok": True, "accepted": True},
        )[-1],
    )
    first_tool = {tool.name: tool for tool in asyncio.run(first_server.list_tools())}["click_command"]
    second_tool = {tool.name: tool for tool in asyncio.run(second_server.list_tools())}["click_command"]

    def invoke_registered(
        tool: Any, button: str, caller_context: Any,
    ) -> tuple[str, dict[str, Any], Any, Any]:
        async def invoke_in_caller_context() -> tuple[str, dict[str, Any], Any, Any]:
            with activate_application_context(caller_context):
                prior_context = mcp_server.current_application_context()
                if dispatch == "mcp":
                    result = await tool.run({"target_button": button})
                    payload = json.loads(result.content[0].text)
                else:
                    payload = tool.fn(target_button=button)
                restored_context = mcp_server.current_application_context()
            return button, payload, prior_context, restored_context

        return asyncio.run(invoke_in_caller_context())

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(invoke_registered, tool, button, caller_context)
            for tool, button, caller_context in (
                (first_tool, "FIRST", second), (second_tool, "SECOND", first),
            )
        ]
        results = [future.result(timeout=5) for future in futures]

    assert len(calls) == 2
    assert {(*call[:3], id(call[3])) for call in calls} == {
        ("FIRST", "127.0.0.1", 15444, id(first)),
        ("SECOND", "127.0.0.1", 15445, id(second)),
    }
    assert len(results) == 2
    worker_contexts = {
        button: (prior_context, restored_context)
        for button, _payload, prior_context, restored_context in results
    }
    assert worker_contexts["FIRST"][0] is second
    assert worker_contexts["FIRST"][1] is second
    assert worker_contexts["SECOND"][0] is first
    assert worker_contexts["SECOND"][1] is first
    payloads = [payload for _button, payload, _prior_context, _restored_context in results]
    assert all(payload["accepted"] is True for payload in payloads)
    assert [
        (first.target, first.session, first.attachment),
        (second.target, second.session, second.attachment),
    ] == before


def test_bound_remote_read_and_display_use_lifecycle_window_without_xvfb_display(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[OperationRequest] = []
    monkeypatch.setattr(
        mcp_server.client_display, "remote_agent_configured", lambda **_kwargs: True,
    )

    def handler(request):
        requests.append(request)
        if request.kind is OperationKind.DISPLAY:
            return OperationResult(
                request, mcp_server.OperationVerdict.SUCCESS,
                value={"size_bytes": 7},
                artifacts=(ArtifactReference(
                    "screenshot.0123456789abcdef", "image/png",
                    "sha256:" + "a" * 64, None, "internal",
                ),),
            )
        return OperationResult.success(request, value={"count": 0})

    executor = WindowsHostQAExecutor({
        (OperationKind.READ, "get_window_list"): handler,
        (OperationKind.DISPLAY, "capture_screenshot"): handler,
    })
    server, context = _context(tmp_path, remote=True, executor=executor)
    with activate_application_context(context):
        mcp_server._remember_bound_testclient(
            {
                "host": "host.docker.internal", "port": 15444, "pid": 4321,
                "alive": True, "listening": True, "owns_process": True,
                "native_port": 15445,
                "lifecycle_handle": {
                    "id": "remote-7", "pid": 4321, "port": 15445,
                },
                "client_target": {
                    "kind": "host-agent-testclient", "lifecycle_id": "remote-7",
                    "pid": 4321, "port": 15445,
                },
            },
            operation="launch_test_client",
            ownership_class="owned",
            lifecycle_id="remote-7",
        )
    assert context.attachment.display == ""
    assert context.attachment.status["client_target"]["lifecycle_id"] == "remote-7"
    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    read = asyncio.run(tools["get_window_list"].run({"geometry": False}))
    display = asyncio.run(tools["capture_screenshot"].run({"window": None}))

    assert [request.kind for request in requests] == [
        OperationKind.READ, OperationKind.DISPLAY,
    ], (read.content[0].text, display.content[0].text)
    assert [request.arguments["display"] for request in requests] == ["", ""]


@pytest.mark.parametrize("evidence_policy", ["sanitized", "full_local"])
def test_default_screenshot_uses_provider_evidence_and_exact_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, evidence_policy: str,
) -> None:
    workspace = tmp_path / "conflicting-workspace"
    process_root = tmp_path / "process-only-root"
    destinations: list[Path] = []

    class Backend:
        def capture_screenshot(self, _display, out_path, *, window=None):
            destinations.append(Path(out_path))
            Path(out_path).write_bytes(b"provider-owned-png")
            return {
                "path": str(out_path), "size_bytes": 18,
                "window": window, "ui_text": "PRIVATE-UI",
            }

    server, context = _context(tmp_path, evidence_policy=evidence_policy)
    # The bound evidence root is independently admitted: it must win even
    # when this factory's workspace and the ambient process root disagree.
    context.settings = replace(context.settings, home=str(workspace))
    monkeypatch.setenv("QA_MCP_HOME", str(process_root))
    session = SessionIdentity("session-7", context.target, 7)
    context.session = session
    context.attachment = mcp_server._AttachedTestClientContext(
        "127.0.0.1", 15444, 1.0, {}, target=context.target, session=session,
        binding_generation=7, ownership_class="owned", lifecycle_id="local-7", display=":109",
    )
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: Backend())

    tool = {item.name: item for item in asyncio.run(server.list_tools())}["capture_screenshot"]
    result = asyncio.run(tool.run({"window": None})).content[0].text
    payload = json.loads(result)
    digest = "sha256:1bee1c17b28ba4d5cf97c0f99a67454a58b5771d1a8a940ac333c9eabefac012"
    artifacts = payload["artifacts"]

    assert payload["verdict"] == "success" and artifacts[0]["sha256"] == digest
    assert "PRIVATE-UI" not in result and "ui_text" not in result
    assert destinations and all(path.is_relative_to(context.runtime_target.binding.evidence_root) for path in destinations)
    assert not workspace.exists() and not process_root.exists()
    evidence_files = list(context.runtime_target.binding.evidence_root.glob("*.png"))
    if evidence_policy == "sanitized":
        assert "path" not in artifacts[0] and evidence_files == []
    else:
        assert evidence_files == [Path(artifacts[0]["path"])]
        assert evidence_files[0].read_bytes() == b"provider-owned-png"


def test_bound_local_cleanup_refuses_override_then_stops_exact_owned_handle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, context = _context(tmp_path)
    monkeypatch.setattr(mcp_server.client_lifecycle, "launch_test_client", lambda *_a, **_k: SimpleNamespace(
        status=lambda: {"pid": 4321, "xvfb_pid": 4322, "alive": True, "listening": True,
                        "owns_process": True, "apache_stopped": True, "display": ":109"},
    ))
    stopped: list[tuple[int, int | None, bool]] = []
    monkeypatch.setattr(
        mcp_server.client_lifecycle, "stop_by_pid",
        lambda pid, *, xvfb_pid, restore_apache: stopped.append(
            (pid, xvfb_pid, restore_apache)
        ) or {"stopped": True, "state": "stopped"},
    )

    with activate_application_context(context):
        launched = mcp_server.launch_test_client(
            port=15444, manage_apache=True, display=":109"
        )
        refused = mcp_server.stop_test_client(pid=9999)
        cleaned = mcp_server._project_bound_cleanup()

    assert refused["error"]["code"] == "runtime-target-override-forbidden"
    assert stopped == [(4321, 4322, True)], (launched, refused, cleaned)
    assert cleaned["stopped"] is True, cleaned
    assert context.attachment is None and context.session is None


def test_bound_nonowned_cleanup_detaches_without_signal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, context = _context(tmp_path)
    # Cleanup accepts a previously admitted attachment. Public attach admission
    # has its own tests and now rejects endpoints without target observations.
    context.session = SessionIdentity("previously-admitted", context.target, 7)
    context.attachment = mcp_server._AttachedTestClientContext(
        host="127.0.0.1", port=15444, attached_at=1.0,
        status={"pid": 8765, "alive": True, "listening": True, "owns_process": False},
        target=context.target, session=context.session, binding_generation=7,
        ownership_class="attached",
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle, "stop_by_pid",
        lambda *_args, **_kwargs: pytest.fail("non-owned process must not be signalled"),
    )

    with activate_application_context(context):
        cleaned = mcp_server._project_bound_cleanup()

    assert cleaned["state"] == "detached" and cleaned["stopped"] is False
    assert context.attachment is None and context.session is None


def test_remote_cleanup_uses_native_handle_port_not_protocol_relay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, context = _context(tmp_path, remote=True)
    observed: list[dict[str, Any]] = []

    class Backend:
        def launch_test_client(self, **_kwargs):
            return {
                "ok": True, "pid": 4321, "port": 15445, "alive": True,
                "listening": True, "owns_process": True, "lifecycle_id": "launch-7",
                "lifecycle_handle": {"id": "launch-7", "pid": 4321, "port": 15445},
                "client_target": {"pid": 4321, "port": 15445, "lifecycle_id": "launch-7"},
            }

        def stop_test_client(self, **kwargs):
            observed.append(kwargs)
            return {"ok": True, "state": "stopped", "stopped": True}

    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda **_kwargs: True)
    monkeypatch.setattr(
        mcp_server.client_display.RemoteAgentBackend, "from_settings",
        classmethod(lambda cls, _settings: Backend()),
    )
    monkeypatch.setattr(mcp_server, "_remote_protocol_endpoint", lambda _target: ("127.0.0.1", 15446))

    with activate_application_context(context):
        launched = mcp_server.launch_test_client(port=15444)
        cleaned = mcp_server._project_bound_cleanup()

    assert cleaned["stopped"] is True, (launched, cleaned)
    assert observed[0]["port"] == 15445
    assert observed[0]["lifecycle_handle"]["id"] == "launch-7"
    assert context.attachment is None and context.session is None


@pytest.mark.parametrize(
    "mutation",
    [
        "target", "session", "generation", "ownership", "lifecycle_id",
        "cleanup_pid", "cleanup_port", "cleanup_id", "handle_pid", "handle_port", "handle_id",
    ],
)
def test_remote_cleanup_refuses_stale_foreign_or_recycled_identity_without_signal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str,
) -> None:
    _, context = _context(tmp_path, remote=True)

    class Backend:
        def launch_test_client(self, **_kwargs):
            return {
                "ok": True, "pid": 4321, "port": 15445, "alive": True,
                "listening": True, "owns_process": True, "lifecycle_id": "launch-7",
                "lifecycle_handle": {"id": "launch-7", "pid": 4321, "port": 15445},
                "client_target": {"pid": 4321, "port": 15445, "lifecycle_id": "launch-7"},
            }

        def stop_test_client(self, **_kwargs):
            pytest.fail("refused cleanup must not signal the host backend")

    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda **_kwargs: True)
    monkeypatch.setattr(
        mcp_server.client_display.RemoteAgentBackend, "from_settings",
        classmethod(lambda cls, _settings: Backend()),
    )
    monkeypatch.setattr(mcp_server, "_remote_protocol_endpoint", lambda _target: ("127.0.0.1", 15446))

    with activate_application_context(context):
        mcp_server.launch_test_client(port=15444)
        original = context.attachment
        assert original is not None and original.cleanup is not None
        cleanup = dict(original.cleanup)
        handle = dict(cleanup["lifecycle_handle"])
        if mutation == "target":
            changed = replace(original, target=object())
        elif mutation == "session":
            changed = replace(original, session=SessionIdentity("foreign", context.target, 7))
        elif mutation == "generation":
            changed = replace(original, binding_generation=8)
        elif mutation == "ownership":
            changed = replace(original, ownership_class="foreign")
        elif mutation == "lifecycle_id":
            changed = replace(original, lifecycle_id="recycled")
        else:
            field, value = mutation.removeprefix("cleanup_").removeprefix("handle_"), None
            if mutation in {"cleanup_pid", "handle_pid"}:
                value = 9999
            elif mutation in {"cleanup_port", "handle_port"}:
                value = 15555
            else:
                value = "recycled"
            if mutation.startswith("handle_"):
                handle[field] = value
                cleanup["lifecycle_handle"] = MappingProxyType(handle)
            else:
                if field == "id":
                    field = "lifecycle_id"
                cleanup[field] = value
            changed = replace(original, cleanup=MappingProxyType(cleanup))
        context.attachment = changed
        result = mcp_server._project_bound_cleanup()

    assert result["verdict"] == "blocked"
    assert result["error"]["code"] == "runtime-target-cleanup-not-owned"
    assert context.attachment is changed and context.session is original.session
