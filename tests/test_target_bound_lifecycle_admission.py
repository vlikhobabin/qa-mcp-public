"""Project lifecycle admission proves raw target identity before session state."""

from __future__ import annotations

import asyncio
import json
import socket
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from typing import Any

import pytest

from qa_mcp import mcp_server
from qa_mcp.config import Settings
from qa_mcp.core import (
    RuntimeTargetBindingError,
    SessionIdentity,
    activate_application_context,
    resolve_runtime_target,
)


def _fingerprint(value: str) -> dict[str, str]:
    return {"algorithm": "sha256", "value": value}


def _bound_context(
    tmp_path: Path, *, remote: bool = False, target_kind: str = "file-infobase",
    return_server: bool = False,
):
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    base = tmp_path / "declared-base"
    base.mkdir()
    platform = tmp_path / "platform"
    platform.mkdir()
    (platform / "1cv8").write_text("binary", encoding="utf-8")
    physical = tmp_path / "declared.env"
    target_value = (
        f"INFOBASE_PATH={base}\n" if target_kind == "file-infobase"
        else 'CONNECTION_STRING=Srvr="declared";Ref="qa";\n'
    )
    physical.write_text(
        target_value + f"PLATFORM_ROOT={platform}\n"
        "TEST_CLIENT_USER=DeclaredUser\nTEST_CLIENT_PASSWORD=PRIVATE-SENTINEL\n"
        "SRC_ROOT=/PRIVATE/SOURCE\n",
        encoding="utf-8",
    )
    profile = tmp_path / "profile.json"
    profile.write_text(
        json.dumps({
            "schema": "qa-mcp.runtime-target-profile.v1",
            "binding_ref": "qa-demo",
            "target": {
                "id": "project-demo", "kind": target_kind,
                "fingerprint": _fingerprint("target-observed"),
            },
            "physical_config": {"env_file": str(physical)},
            "evidence": {
                "policy": "sanitized", "root": str(evidence),
                "non_production_approved": False,
            },
            "observation": {
                "target_id": "project-demo", "target_kind": target_kind,
                "target_fingerprint": _fingerprint("target-observed"),
                "effective_principal_fingerprint": _fingerprint("principal-observed"),
                "platform_fingerprint": _fingerprint("platform-observed"),
                "extension_profile_fingerprint": _fingerprint("extensions-observed"),
                "process_config_fingerprint": _fingerprint("process-observed"),
                "security_receipt_id": "receipt-7", "binding_generation": 7,
            },
        }),
        encoding="utf-8",
    )
    resolution = resolve_runtime_target({
        "AI1C_RUNTIME_TARGET_ID": "project-demo",
        "AI1C_RUNTIME_TARGET_KIND": target_kind,
        "AI1C_RUNTIME_TARGET_FINGERPRINT": "target-observed",
        "AI1C_RUNTIME_TARGET_FINGERPRINT_ALGORITHM": "sha256",
        "AI1C_AGENT_PRINCIPAL_ID": "qa-agent",
        "AI1C_AGENT_EXPECTED_PRINCIPAL_FINGERPRINT": "principal-observed",
        "AI1C_AGENT_EXPECTED_PRINCIPAL_FINGERPRINT_ALGORITHM": "sha256",
        "AI1C_AGENT_TEST_SECURITY_RECEIPT_ID": "receipt-7",
        "AI1C_RUNTIME_TARGET_BINDING_GENERATION": "7",
        "AI1C_RUNTIME_TARGET_OBSERVATIONS": ".ai/runtime-provider-observations.json",
        "AI1C_RUNTIME_TARGET_BINDING_REF": "qa-demo",
        "QA_MCP_RUNTIME_TARGET_PROFILE": str(profile),
        "QA_MCP_RUNTIME_EVIDENCE_ALLOW_ROOT": str(evidence),
    })
    assert resolution is not None
    settings = Settings.from_env({
        "QA_MCP_CLIENT_HOST": "host.docker.internal" if remote else "127.0.0.1",
        "QA_MCP_CLIENT_PORT": "15444",
        "QA_MCP_REMOTE_CLIENT": "1" if remote else "0",
        "QA_MCP_HOST_AGENT_CLIENT_PORT": "15444",
    })
    server = mcp_server.create_mcp_server(settings=settings, runtime_target=resolution)
    context = mcp_server.application_context(server)
    return (context, physical, server) if return_server else (context, physical)


def _owned_remote_result(port: int = 15444) -> dict[str, Any]:
    return {
        "ok": True, "pid": 4321, "port": port, "alive": True,
        "listening": True, "owns_process": True, "lifecycle_id": "launch-1",
        "lifecycle_handle": {"id": "launch-1", "pid": 4321, "port": port},
        "client_target": {"pid": 4321, "port": port, "lifecycle_id": "launch-1"},
    }


def _remote_backend(monkeypatch: pytest.MonkeyPatch, result: dict[str, Any], calls: list[Any]):
    class Backend:
        def launch_test_client(self, **kwargs):
            calls.append(kwargs)
            return result

    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda **_kwargs: True)
    monkeypatch.setattr(
        mcp_server.client_display.RemoteAgentBackend,
        "from_settings", classmethod(lambda cls, _settings: Backend()),
    )


def test_project_local_launch_uses_profile_and_admits_immutable_secret_safe_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    context, physical = _bound_context(tmp_path)
    calls: list[Any] = []

    class Handle:
        def status(self):
            return {
                "pid": 321, "alive": True, "listening": True,
                "owns_process": True, "host": "127.0.0.1", "port": 15444,
                "connection": {"password": "PRIVATE-SENTINEL"},
                "out_dir": "/private/stage",
            }

    monkeypatch.setattr(
        mcp_server.client_lifecycle, "launch_test_client",
        lambda target, **kwargs: calls.append((target, kwargs)) or Handle(),
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle, "ensure_test_client",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("legacy fallback")),
    )
    with activate_application_context(context):
        result = mcp_server.launch_test_client(port=15444, wait_sec=0)

    target = calls[0][0]
    assert target.infobase_path == str(physical.parent / "declared-base")
    assert target.user == "DeclaredUser" and target.port == 15444
    assert context.session is context.attachment.session
    assert context.attachment.target is context.target
    assert context.attachment.binding_generation == 7
    assert context.attachment.ownership_class == "owned"
    assert context.attachment.lifecycle_id
    with pytest.raises(FrozenInstanceError):
        context.attachment.binding_generation = 8
    assert result["target"]["logical_id"] == "project-demo"
    assert result["session"]["sequence"] == 7
    assert not {"host", "port", "connection", "out_dir", "lifecycle_handle"} & result.keys()
    assert "PRIVATE-SENTINEL" not in json.dumps(result)


def test_project_client_server_launch_uses_declared_connection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    context, _ = _bound_context(tmp_path, target_kind="client-server-infobase")
    targets: list[Any] = []

    class Handle:
        def status(self):
            return {"pid": 322, "alive": True, "listening": True, "owns_process": True}

    monkeypatch.setattr(
        mcp_server.client_lifecycle, "launch_test_client",
        lambda target, **_kwargs: targets.append(target) or Handle(),
    )
    with activate_application_context(context):
        result = mcp_server.launch_test_client(port=15444, wait_sec=0)

    assert targets[0].infobase_path is None
    assert targets[0].connection_string == 'Srvr="declared";Ref="qa";'
    assert result["target"]["kind"] == "client-server-infobase"


@pytest.mark.parametrize("kwargs", [
    {"infobase_path": "/alternate/base"}, {"user": "Other"},
    {"kind": "thin"}, {"port": 15555}, {"env_file": "/alternate/private.env"},
])
def test_project_launch_override_blocks_before_profile_or_lifecycle_side_effect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kwargs: dict[str, Any],
) -> None:
    context, _ = _bound_context(tmp_path)
    monkeypatch.setattr(
        mcp_server.client_lifecycle, "load_env_file",
        lambda _path: (_ for _ in ()).throw(AssertionError("profile read after override")),
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle, "launch_test_client",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("launch side effect")),
    )
    with activate_application_context(context):
        result = mcp_server.launch_test_client(**kwargs)

    assert result["verdict"] == "blocked"
    assert result["error"]["code"] == "runtime-target-override-forbidden"
    assert context.session is None and context.attachment is None
    assert "alternate" not in json.dumps(result)


def test_project_launch_keeps_admitted_config_after_fixture_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    context, physical = _bound_context(tmp_path)
    alternate_base = tmp_path / "alternate-base"
    alternate_base.mkdir()
    alternate_platform = tmp_path / "alternate-platform"
    alternate_platform.mkdir()
    (alternate_platform / "1cv8").write_text("binary", encoding="utf-8")
    physical.write_text(
        f"INFOBASE_PATH={alternate_base}\nPLATFORM_ROOT={alternate_platform}\n"
        "TEST_CLIENT_USER=Changed\nTEST_CLIENT_PASSWORD=CHANGED-SECRET\nSRC_ROOT=/changed/src\n",
        encoding="utf-8",
    )
    targets: list[Any] = []

    class Handle:
        def status(self):
            return {"pid": 321, "alive": True, "listening": True, "owns_process": True}

    monkeypatch.setattr(
        mcp_server.client_lifecycle, "launch_test_client",
        lambda target, **_kwargs: targets.append(target) or Handle(),
    )
    with activate_application_context(context):
        rewritten = mcp_server.launch_test_client(port=15444, wait_sec=0)

    physical.unlink()
    with activate_application_context(context):
        absent = mcp_server.launch_test_client(port=15444, wait_sec=0)

    replacement = tmp_path / "replacement.env"
    replacement.write_text(
        f"INFOBASE_PATH={alternate_base}\nPLATFORM_ROOT={alternate_platform}\n"
        "TEST_CLIENT_USER=Symlinked\nTEST_CLIENT_PASSWORD=SYMLINKED-SECRET\nSRC_ROOT=/symlinked/src\n",
        encoding="utf-8",
    )
    physical.symlink_to(replacement)
    with activate_application_context(context):
        symlinked = mcp_server.launch_test_client(port=15444, wait_sec=0)

    for target in targets:
        assert target.infobase_path == str(physical.parent / "declared-base")
        assert target.platform_root == str(physical.parent / "platform")
        assert target.user == "DeclaredUser"
        assert target.password == "PRIVATE-SENTINEL"
    assert len(targets) == 3
    assert all(result["verdict"] == "success" for result in (rewritten, absent, symlinked))
    assert "CHANGED-SECRET" not in json.dumps((rewritten, absent, symlinked))


def test_project_composition_rejects_a_stale_session_for_the_resolution(tmp_path: Path) -> None:
    context, _ = _bound_context(tmp_path)

    with pytest.raises(RuntimeTargetBindingError, match="session"):
        mcp_server.create_mcp_server(
            settings=context.settings,
            runtime_target=context.runtime_target,
            session=SessionIdentity("stale", context.target, sequence=6),
        )


@pytest.mark.parametrize("remote", [False, True])
def test_project_attach_rejects_declared_profile_without_current_process_observation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, remote: bool,
) -> None:
    context, _ = _bound_context(tmp_path, remote=remote)
    calls: list[Any] = []

    monkeypatch.setattr(
        mcp_server.client_lifecycle, "attach_test_client",
        lambda **kwargs: calls.append(kwargs) or (_ for _ in ()).throw(
            AssertionError("protocol attach before current target observation")
        ),
    )
    with activate_application_context(context):
        result = mcp_server.attach_test_client(
            host="host.docker.internal" if remote else "127.0.0.1", port=15444
        )

    assert result["verdict"] == "blocked"
    assert result["error"]["code"] == "runtime-target-observation-missing"
    assert calls == []
    assert context.session is None and context.attachment is None


def test_remote_attach_does_not_treat_pid_port_or_listening_as_target_observation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    context, _ = _bound_context(tmp_path, remote=True)
    host_status_calls: list[dict[str, Any]] = []

    class Backend:
        def test_client_status(self, **kwargs):
            host_status_calls.append(kwargs)
            return {
                "ok": True, "listening": True, "port": 15444,
                "client_target": {"pid": 4321, "port": 15444},
            }

    monkeypatch.setattr(
        mcp_server.client_lifecycle, "attach_test_client",
        lambda **_kwargs: (_ for _ in ()).throw(AssertionError("protocol probe before admission")),
    )
    monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda **_kwargs: True)
    monkeypatch.setattr(
        mcp_server.client_display.RemoteAgentBackend,
        "from_settings", classmethod(lambda cls, _settings: Backend()),
    )
    with activate_application_context(context):
        result = mcp_server.attach_test_client(host="host.docker.internal", port=15444)

    assert result["error"]["code"] == "runtime-target-observation-missing"
    assert host_status_calls == []
    assert context.session is None and context.attachment is None


@pytest.mark.parametrize("remote", [False, True])
@pytest.mark.parametrize("with_owned_session", [False, True])
def test_registered_bound_attach_refuses_reachable_endpoint_without_mutating_admitted_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, remote: bool, with_owned_session: bool,
) -> None:
    context, _, server = _bound_context(tmp_path, remote=remote, return_server=True)
    lifecycle_calls: list[dict[str, Any]] = []
    host_agent_calls: list[tuple[str, dict[str, Any]]] = []

    class LocalHandle:
        def status(self):
            return {
                "pid": 321, "alive": True, "listening": True,
                "owns_process": True, "host": "127.0.0.1",
                "port": context.settings.client_port,
            }

    class RemoteBackend:
        def launch_test_client(self, **kwargs):
            host_agent_calls.append(("launch", kwargs))
            return _owned_remote_result(port=context.settings.client_port)

        def test_client_status(self, **kwargs):
            host_agent_calls.append(("status", kwargs))
            return {
                "ok": True, "listening": True, "port": context.settings.client_port,
                "client_target": {"pid": 4321, "port": context.settings.client_port},
            }

    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "attach_test_client",
        lambda **kwargs: lifecycle_calls.append(kwargs) or (_ for _ in ()).throw(
            AssertionError("bound attach reached lifecycle transport")
        ),
    )
    if remote:
        monkeypatch.setattr(mcp_server.client_display, "remote_agent_configured", lambda **_kwargs: True)
        monkeypatch.setattr(
            mcp_server.client_display.RemoteAgentBackend,
            "from_settings", classmethod(lambda cls, _settings: RemoteBackend()),
        )
    else:
        monkeypatch.setattr(
            mcp_server.client_lifecycle,
            "launch_test_client",
            lambda _target, **kwargs: lifecycle_calls.append(kwargs) or LocalHandle(),
        )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as reachable:
        reachable.bind(("127.0.0.1", 0))
        reachable.listen()
        port = reachable.getsockname()[1]
        context.settings = replace(
            context.settings,
            client_port=port,
            host_agent_client_port=port,
        )
        if with_owned_session:
            launch = asyncio.run(server.call_tool("launch_test_client", {"wait_sec": 0}))
            assert launch.structured_content["verdict"] == "success"

        before = {
            "target": context.target,
            "generation": context.runtime_target.binding.binding_generation,
            "session": context.session,
            "attachment": context.attachment,
            "attachment_status": dict(context.attachment.status) if context.attachment else None,
            "ownership": context.attachment.ownership_class if context.attachment else None,
            "lifecycle_id": context.attachment.lifecycle_id if context.attachment else None,
            "lifecycle_calls": list(lifecycle_calls),
            "host_agent_calls": list(host_agent_calls),
        }
        result = asyncio.run(server.call_tool("attach_test_client", {})).structured_content

    assert result["verdict"] == "blocked"
    assert result["error"]["code"] == "runtime-target-observation-missing"
    assert context.target is before["target"]
    assert context.runtime_target.binding.binding_generation == before["generation"]
    assert context.session is before["session"]
    assert context.attachment is before["attachment"]
    if context.attachment is not None:
        assert dict(context.attachment.status) == before["attachment_status"]
        assert context.attachment.ownership_class == before["ownership"] == "owned"
        assert context.attachment.lifecycle_id == before["lifecycle_id"]
    assert lifecycle_calls == before["lifecycle_calls"]
    assert host_agent_calls == before["host_agent_calls"]


def test_remote_launch_uses_profile_platform_and_nonzero_configured_port(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    context, _ = _bound_context(tmp_path, remote=True)
    context.settings = replace(context.settings, host_agent_client_port=0)
    calls: list[Any] = []
    _remote_backend(monkeypatch, _owned_remote_result(), calls)
    monkeypatch.setattr(
        mcp_server, "_SETTINGS", replace(mcp_server._SETTINGS, platform_version="9.9.9.9")
    )
    monkeypatch.setattr(mcp_server, "platform_version_from_root", lambda _root: "8.3.27.2130")
    with activate_application_context(context):
        result = mcp_server.launch_test_client(port=15444, wait_sec=0)

    assert calls[0]["port"] == 15444
    assert calls[0]["platform_version"] == "8.3.27.2130"
    assert result["verdict"] == "success" and result["ownership_class"] == "owned"


def _mutate_raw_identity(result: dict[str, Any], mutation: str) -> None:
    container, field, value = mutation.split(":", 2)
    target = result if container == "top" else result[
        "client_target" if container == "client" else "lifecycle_handle"
    ]
    if value == "missing":
        target.pop(field, None)
    elif value == "zero":
        target[field] = 0
    elif value == "bool":
        target[field] = True
    elif value == "string":
        target[field] = "15444" if field == "port" else "4321"
    elif value == "blank":
        target[field] = " "
    elif value == "alias":
        target.pop("lifecycle_id", None)
        target["id"] = "launch-1"
    elif value == "other":
        target[field] = 15555 if field == "port" else (9999 if field == "pid" else "other")


@pytest.mark.parametrize("mutation", [
    "top:pid:missing", "top:pid:bool", "top:lifecycle_id:missing",
    "client:pid:zero", "client:pid:string", "client:port:missing",
    "client:port:zero", "client:port:bool", "client:port:string",
    "client:lifecycle_id:missing", "client:lifecycle_id:blank",
    "client:lifecycle_id:alias", "handle:pid:bool", "handle:port:zero",
    "handle:id:missing", "client:pid:other", "handle:pid:other",
    "handle:port:other", "top:lifecycle_id:other", "handle:id:other",
])
def test_remote_launch_fails_closed_on_incomplete_or_incoherent_raw_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str,
) -> None:
    context, _ = _bound_context(tmp_path, remote=True)
    raw = _owned_remote_result()
    _mutate_raw_identity(raw, mutation)
    calls: list[Any] = []
    _remote_backend(monkeypatch, raw, calls)
    monkeypatch.setattr(
        mcp_server, "_wait_for_remote_testclient",
        lambda *_args: (_ for _ in ()).throw(AssertionError("downstream endpoint probe")),
    )
    with activate_application_context(context):
        result = mcp_server.launch_test_client(port=15444, wait_sec=0)

    assert calls and result["verdict"] == "blocked"
    assert result["error"]["code"] == "runtime-target-mismatch"
    assert context.session is None and context.attachment is None


@pytest.mark.parametrize("collision", ["subordinate-floats", "boolean-pid-one"])
def test_remote_launch_rejects_python_numeric_equality_collisions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, collision: str,
) -> None:
    context, _ = _bound_context(tmp_path, remote=True)
    raw = _owned_remote_result()
    if collision == "subordinate-floats":
        for projection in (raw["client_target"], raw["lifecycle_handle"]):
            projection["pid"] = 4321.0
            projection["port"] = 15444.0
    else:
        raw["pid"] = 1
        raw["client_target"]["pid"] = True
        raw["lifecycle_handle"]["pid"] = True
    _remote_backend(monkeypatch, raw, [])
    monkeypatch.setattr(
        mcp_server, "_wait_for_remote_testclient",
        lambda *_args: (_ for _ in ()).throw(AssertionError("downstream endpoint probe")),
    )

    with activate_application_context(context):
        result = mcp_server.launch_test_client(port=15444, wait_sec=0)

    assert result["error"]["code"] == "runtime-target-mismatch"
    assert context.session is None and context.attachment is None


def test_project_status_rejects_override_and_stale_session_before_probe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    context, _ = _bound_context(tmp_path)
    probes: list[Any] = []
    monkeypatch.setattr(
        mcp_server.client_lifecycle, "port_is_listening",
        lambda *_args, **_kwargs: probes.append(True) is None,
    )
    with activate_application_context(context):
        overridden = mcp_server.test_client_status(host="203.0.113.7", port=15444)
        missing = mcp_server.test_client_status(host="127.0.0.1", port=15444)
        mcp_server._remember_attached_testclient({
            "attached": True, "owns_process": False, "listening": True,
            "host": "127.0.0.1", "port": 15444,
        })
        context.session = None
        stale = mcp_server.test_client_status(host="127.0.0.1", port=15444)

    assert overridden["error"]["code"] == "runtime-target-override-forbidden"
    assert missing["error"]["code"] == "runtime-target-session-required"
    assert stale["error"]["code"] == "runtime-target-mismatch"
    assert probes == []


def test_unbound_standalone_lifecycle_behavior_and_schema_remain_explicit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Handle:
        def status(self):
            return {"pid": 77, "alive": True, "listening": True}

    seen: list[Any] = []
    monkeypatch.setattr(
        mcp_server.client_lifecycle, "load_env_file", lambda _path: {"PLATFORM_ROOT": "/platform"}
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle, "ensure_test_client",
        lambda **kwargs: seen.append(kwargs) or Handle(),
    )
    context = mcp_server.ApplicationContext(
        settings=Settings.from_env({}), executor=mcp_server.LocalQAExecutor()
    )
    server = mcp_server.create_mcp_server(settings=context.settings)
    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    with activate_application_context(context):
        result = mcp_server.launch_test_client(infobase_path="/explicit/base", port=15555)

    assert result["pid"] == 77 and seen[0]["infobase_path"] == "/explicit/base"
    assert seen[0]["port"] == 15555
    assert {"infobase_path", "port", "user", "kind", "env_file"} <= set(
        tools["launch_test_client"].parameters["properties"]
    )


def test_unbound_standalone_attach_remains_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Handle:
        def status(self):
            return {
                "attached": True,
                "owns_process": False,
                "listening": True,
                "host": "127.0.0.1",
                "port": 15555,
            }

    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(
        mcp_server.client_lifecycle,
        "attach_test_client",
        lambda **kwargs: calls.append(kwargs) or Handle(),
    )
    context = mcp_server.ApplicationContext(
        settings=Settings.from_env({}), executor=mcp_server.LocalQAExecutor()
    )
    with activate_application_context(context):
        result = mcp_server.attach_test_client(host="127.0.0.1", port=15555)

    assert calls == [{"host": "127.0.0.1", "port": 15555, "connect_timeout_sec": 0.5}]
    assert result["attached"] is True
    assert result["owns_process"] is False
    assert result["active_attachment"]["host"] == "127.0.0.1"
    assert result["active_attachment"]["port"] == 15555
