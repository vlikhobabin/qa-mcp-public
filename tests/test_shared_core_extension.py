"""Public shared-core composition and downstream extension contracts."""

from __future__ import annotations

import asyncio
import ast
import json
import os
import socket
import urllib.error
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest

from qa_mcp import mcp_server
from qa_mcp.config import Settings
from qa_mcp.protocol import display_backend as display_backend
from qa_mcp.protocol import transport as client_transport
from qa_mcp.core import (
    ApplicationContext,
    LocalQAExecutor,
    OperationError,
    OperationKind,
    OperationRequest,
    OperationResult,
    OperationVerdict,
    SessionIdentity,
    TargetIdentity,
    WindowsHostQAExecutor,
    activate_application_context,
    current_application_context,
    execute_mcp_operation,
    execute_scenario_operation,
)
from qa_mcp.config import active_application_settings
from qa_mcp.scenario import Scenario, ScenarioResult, ScenarioRunner, Step


def _settings() -> Settings:
    return Settings(manager_templates="manager.json", value_read_templates="value.json")


class RecordingExecutor:
    name = "fake-downstream"

    def __init__(self) -> None:
        self.requests: list[OperationRequest] = []

    def execute(
        self,
        request: OperationRequest,
        *,
        target: TargetIdentity | None,
        session: SessionIdentity | None,
    ) -> OperationResult:
        self.requests.append(request)
        return OperationResult.success(
            request,
            value={
                "executor": self.name,
                "target": target.logical_id if target else None,
                "session": session.session_id if session else None,
            },
        )


def test_public_models_are_product_neutral_and_secret_safe() -> None:
    target = TargetIdentity(logical_id="demo", fingerprint="sha256:abc")
    session = SessionIdentity(session_id="session-1", target=target)
    request = OperationRequest(OperationKind.READ, "active_window")
    result = OperationResult.success(request, value={"caption": "Main"})

    assert session.target == target
    assert result.verdict is OperationVerdict.SUCCESS
    assert result.to_dict() == {
        "operation": "active_window",
        "kind": "read",
        "verdict": "success",
        "value": {"caption": "Main"},
    }


def test_mcp_and_scenario_paths_share_executor_and_verdict_taxonomy() -> None:
    executor = RecordingExecutor()
    target = TargetIdentity(logical_id="demo", fingerprint="sha256:abc")
    context = ApplicationContext(
        settings=_settings(),
        executor=executor,
        target=target,
        session=SessionIdentity(session_id="session-1", target=target),
    )

    for kind in OperationKind:
        request = OperationRequest(kind, f"representative_{kind.value}")
        mcp_result = execute_mcp_operation(context, request)
        scenario_result = execute_scenario_operation(context, request)
        assert mcp_result.verdict is scenario_result.verdict is OperationVerdict.SUCCESS

    assert [request.kind for request in executor.requests] == [
        kind for kind in OperationKind for _ in range(2)
    ]


def test_factory_binds_fake_downstream_executor_without_private_imports() -> None:
    executor = RecordingExecutor()
    target = TargetIdentity(logical_id="demo", fingerprint="sha256:abc")

    def probe_executor() -> dict[str, Any]:
        request = OperationRequest(OperationKind.READ, "probe")
        return execute_mcp_operation(current_application_context(), request).to_dict()

    server = mcp_server.create_mcp_server(
        settings=_settings(),
        executor=executor,
        tool_profile="standalone",
        target=target,
        extra_tools={"probe_executor": probe_executor},
    )
    result = asyncio.run(server.call_tool("probe_executor", {}))

    assert result.structured_content == {
        "operation": "probe",
        "kind": "read",
        "verdict": "success",
        "value": {"executor": "fake-downstream", "target": "demo", "session": None},
    }
    assert executor.requests[-1].name == "probe"

    lifecycle = asyncio.run(
        server.call_tool("test_client_status", {"host": "ignored", "port": 1})
    )
    assert lifecycle.structured_content == {
        "executor": "fake-downstream",
        "target": "demo",
        "session": None,
    }
    assert executor.requests[-1].kind is OperationKind.LIFECYCLE
    assert executor.requests[-1].name == "test_client_status"


def test_factory_binds_omitted_tool_defaults_to_each_settings_instance() -> None:
    configured = (
        ("203.0.113.77", 54321, "manager-a.json", "value-a.json"),
        ("198.51.100.18", 15444, "manager-b.json", "value-b.json"),
    )

    for host, port, manager_templates, value_templates in configured:
        executor = RecordingExecutor()
        settings = Settings(
            manager_templates=manager_templates,
            value_read_templates=value_templates,
            client_host=host,
            client_port=port,
        )
        server = mcp_server.create_mcp_server(settings=settings, executor=executor)

        asyncio.run(server.call_tool("test_client_status", {}))
        assert executor.requests[-1].arguments == {"pid": None, "host": host, "port": port}
        asyncio.run(server.call_tool("get_window_list_testclient", {}))
        assert executor.requests[-1].arguments == {
            "host": host,
            "port": port,
            "capture_dir": "tm-v1-ro-batchQ3",
            "manager_templates": value_templates,
        }

        tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}
        status_schema = tools["test_client_status"].parameters["properties"]
        window_schema = tools["get_window_list_testclient"].parameters["properties"]
        scenario_schema = tools["run_scenario"].parameters["properties"]
        assert status_schema["host"]["default"] == host
        assert status_schema["port"]["default"] == port
        assert window_schema["manager_templates"]["default"] == value_templates
        assert scenario_schema["manager_templates"]["default"] == manager_templates


class TaxonomyExecutor:
    name = "taxonomy-fake"

    def __init__(self, verdict: OperationVerdict) -> None:
        self.verdict = verdict
        self.requests: list[OperationRequest] = []

    def execute(
        self,
        request: OperationRequest,
        *,
        target: TargetIdentity | None,
        session: SessionIdentity | None,
    ) -> OperationResult:
        del target, session
        self.requests.append(request)
        if self.verdict is OperationVerdict.SUCCESS:
            return OperationResult.success(request, value={"marker": "shared-read"})
        return OperationResult(
            request=request,
            verdict=self.verdict,
            error=OperationError(
                code=f"synthetic-{self.verdict.value}",
                message=f"synthetic {self.verdict.value}",
            ),
        )


class TaxonomySession:
    def __enter__(self) -> "TaxonomySession":
        return self

    def __exit__(self, *exc: object) -> None:
        return None


@pytest.mark.parametrize("verdict", list(OperationVerdict))
def test_real_mcp_and_scenario_paths_preserve_shared_taxonomy(tmp_path, verdict) -> None:
    executor = TaxonomyExecutor(verdict)
    context = ApplicationContext(settings=_settings(), executor=executor)

    def shared_read() -> dict[str, Any]:
        return execute_mcp_operation(
            current_application_context(),
            OperationRequest(OperationKind.READ, "read_active_window"),
        ).to_dict()

    server = mcp_server.create_mcp_server(
        settings=_settings(),
        executor=executor,
        extra_tools={"shared_read": shared_read},
    )
    mcp_result = asyncio.run(server.call_tool("shared_read", {})).structured_content

    runner = ScenarioRunner(
        session_factory=TaxonomySession,
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path,
        operation_context=context,
    )
    scenario_result = runner.run(
        Scenario(name="taxonomy", steps=[Step(kind="read_active_window", name="shared")])
    )

    assert mcp_result["verdict"] == verdict.value
    assert [request.name for request in executor.requests] == [
        "read_active_window",
        "read_active_window",
    ]
    if verdict is OperationVerdict.SUCCESS:
        assert scenario_result.passed
        assert "shared-read" in scenario_result.steps[0].preview
    else:
        assert not scenario_result.passed
        assert f"{verdict.value}: synthetic {verdict.value}" in scenario_result.steps[0].error


def test_factory_instances_isolate_runtime_state() -> None:
    def context_marker() -> dict[str, Any]:
        context = current_application_context()
        return {
            "session": context.session.session_id if context.session else None,
            "attachment": context.attachment,
            "results": list(context.results_log),
        }

    first = mcp_server.create_mcp_server(
        settings=_settings(),
        executor=RecordingExecutor(),
        session=SessionIdentity(session_id="first"),
        extra_tools={"context_marker": context_marker},
    )
    second = mcp_server.create_mcp_server(
        settings=_settings(),
        executor=RecordingExecutor(),
        session=SessionIdentity(session_id="second"),
        extra_tools={"context_marker": context_marker},
    )
    first_context = mcp_server.application_context(first)
    second_context = mcp_server.application_context(second)
    first_context.attachment = {"host": "first-host"}
    first_context.results_log.append({"scenario": "first"})

    first_result = asyncio.run(first.call_tool("context_marker", {})).structured_content
    second_result = asyncio.run(second.call_tool("context_marker", {})).structured_content

    assert first_result == {
        "session": "first",
        "attachment": {"host": "first-host"},
        "results": [{"scenario": "first"}],
    }
    assert second_result == {"session": "second", "attachment": None, "results": []}


def test_real_factories_keep_display_settings_out_of_process_environment(monkeypatch, tmp_path) -> None:
    """Composition selects each factory's backend without replacing that constructor."""

    process_environment = {
        "QA_MCP_REMOTE_CLIENT": "1",
        "QA_MCP_HOST_AGENT": "foreign.example:8001",
        "QA_MCP_HOST_AGENT_TOKEN": "foreign-token",
    }
    for name, value in process_environment.items():
        monkeypatch.setenv(name, value)

    requests: list[tuple[str, str | None, float, dict[str, Any] | None]] = []
    local_calls: list[tuple[list[str], str]] = []

    class FakeResponse:
        headers = {"Content-Type": "application/json"}

        def __init__(self, payload: dict[str, Any]) -> None:
            self.payload = json.dumps(payload).encode("utf-8")

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *exc: object) -> bool:
            return False

        def read(self) -> bytes:
            return self.payload

    def fake_urlopen(request, timeout):  # noqa: ANN001 - mirrors urllib boundary
        payload = json.loads(request.data) if request.data is not None else None
        requests.append((request.full_url, request.get_header("X-qa-mcp-agent-token"), timeout, payload))
        if request.full_url.endswith("/v1/capabilities"):
            return FakeResponse({
                "api": display_backend.HOST_BRIDGE_API,
                "api_major": display_backend.HOST_BRIDGE_API_MAJOR,
                "version": display_backend.HOST_AGENT_VERSION,
                "display_protocol": display_backend.HOST_AGENT_DISPLAY_PROTOCOL,
                "sha256": "remote-sha",
                "capabilities": sorted(display_backend.HOST_BRIDGE_REQUIRED_CAPABILITIES),
            })
        return FakeResponse({"ok": True})

    monkeypatch.setattr(display_backend.urllib.request, "urlopen", fake_urlopen)
    from qa_mcp.protocol import native_xtest

    monkeypatch.setattr(
        native_xtest,
        "send_keys",
        lambda keys, *, display, settle_sec: local_calls.append((list(keys), display)) or {"ok": True},
    )

    remote = mcp_server.create_mcp_server(settings=Settings(
        manager_templates="remote-manager.json",
        value_read_templates="remote-value.json",
        remote_client=True,
        host_agent="remote.example:8123",
        host_agent_token="remote-token",
        host_agent_expected_version=display_backend.HOST_AGENT_VERSION,
        host_agent_expected_sha256="remote-sha",
        host_agent_window="remote-window",
        host_agent_client_port=15444,
        client_port=15390,
        host_agent_timeout=23.0,
    ))
    local = mcp_server.create_mcp_server(settings=Settings(
        manager_templates="local-manager.json",
        value_read_templates="local-value.json",
        remote_client=False,
    ))
    missing = mcp_server.create_mcp_server(settings=Settings(
        manager_templates="missing-manager.json",
        value_read_templates="missing-value.json",
        remote_client=True,
        host_agent="",
    ))

    remote_result = asyncio.run(remote.call_tool("send_keys", {"keys": ["F5"]})).structured_content
    local_result = asyncio.run(local.call_tool("send_keys", {"keys": ["F6"]})).structured_content
    missing_result = asyncio.run(
        missing.call_tool("capture_screenshot", {"display": ":99", "out_path": str(tmp_path / "never.png")})
    ).structured_content

    assert remote_result["backend"] == "remote-agent"
    assert local_result["backend"] == "local-xtest"
    assert requests == [
        ("http://remote.example:8123/v1/capabilities", "remote-token", 23.0, None),
        (
            "http://remote.example:8123/send_keys",
            "remote-token",
            23.0,
            {"keys": ["F5"], "settle_sec": 0.15, "window": "remote-window", "client_port": 15444},
        ),
    ]
    assert local_calls == [(["F6"], ":89")]
    assert missing_result["error"] == "display-backend-unavailable-remote-client"
    assert missing_result["mode"] == "remote-client"
    assert "foreign" not in repr(missing_result)
    assert not (tmp_path / "never.png").exists()


def test_real_factory_configured_host_agent_failure_is_bounded_and_secret_safe(monkeypatch) -> None:
    """A hostile host-agent error cannot escape through composed MCP results."""

    token = "REVIEW-SYNTHETIC-TOKEN"
    private = "REVIEW-PRIVATE-CONFIGURATION"
    monkeypatch.setenv("QA_MCP_REMOTE_CLIENT", "0")
    monkeypatch.setenv("QA_MCP_HOST_AGENT", "foreign.invalid:8999")
    calls: list[str] = []

    def fake_urlopen(request, timeout):  # noqa: ANN001 - urllib boundary
        del timeout
        calls.append(request.full_url)
        body = json.dumps({
            "ok": False,
            "error": "host-agent-configuration-invalid",
            "detail": f"{token} {private} " + "x" * 4096,
            "token": token,
            "config": private,
        }).encode()
        raise urllib.error.HTTPError(
            request.full_url, 400, "Bad Request", hdrs=None, fp=BytesIO(body),
        )

    monkeypatch.setattr(display_backend.urllib.request, "urlopen", fake_urlopen)
    server = mcp_server.create_mcp_server(settings=Settings(
        manager_templates="remote-manager.json",
        value_read_templates="remote-value.json",
        remote_client=True,
        host_agent="review.invalid:8123",
        host_agent_token=token,
    ))

    result = asyncio.run(server.call_tool("send_keys", {"keys": ["F5"]})).structured_content

    assert calls == ["http://review.invalid:8123/v1/capabilities"]
    assert result == {
        "ok": False,
        "error": "host-agent-configuration-invalid",
        "tool": "send_keys",
        "detail": "host agent request failed",
        "mode": "remote-client",
        "status": 400,
    }
    assert token not in repr(result) and private not in repr(result)
    missing = mcp_server.create_mcp_server(settings=Settings(
        manager_templates="missing-manager.json", value_read_templates="missing-value.json",
        remote_client=True, host_agent="",
    ))
    stop = asyncio.run(missing.call_tool("stop_test_client", {
        "pid": 7, "port": 15444, "lifecycle_id": "owned",
        "lifecycle_handle": {"id": "owned", "pid": 7, "port": 15444},
    })).structured_content
    assert stop["error"] == "host-agent-not-configured"
    assert stop["mode"] == "remote-client"
    assert calls == ["http://review.invalid:8123/v1/capabilities"]


@pytest.mark.parametrize("transport", ["http-error", "json-error"])
@pytest.mark.parametrize("failure_path", ["/v1/capabilities", "operation"])
@pytest.mark.parametrize("tool", ["send_keys", "stop_test_client"])
@pytest.mark.parametrize("remote_code, expected_code", [
    ("REVIEW-SYNTHETIC-TOKEN REVIEW-PRIVATE-CONFIGURATION " + "x" * 4096, "host-agent-error"),
    ("unknown-but-well-formed-code", "host-agent-error"),
    ("foreground-denied", "foreground-denied"),
    ("stale-client-target", "stale-client-target"),
], ids=["secret-and-oversized", "unknown-code", "known-display-code", "known-lifecycle-code"])
def test_real_factory_untrusted_error_codes_have_a_closed_public_contract(
    monkeypatch, transport, failure_path, tool, remote_code, expected_code,
) -> None:
    """Both error transports and MCP consumers reject arbitrary remote codes."""
    token = "REVIEW-SYNTHETIC-TOKEN"
    private = "REVIEW-PRIVATE-CONFIGURATION"
    calls: list[str] = []

    class Response(BytesIO):
        headers = {"Content-Type": "application/json"}

    def fake_urlopen(request, timeout):
        del timeout
        calls.append(request.full_url)
        if failure_path == "operation" and request.full_url.endswith("/v1/capabilities"):
            return Response(json.dumps({
                "api": display_backend.HOST_BRIDGE_API,
                "api_major": display_backend.HOST_BRIDGE_API_MAJOR,
                "version": display_backend.HOST_AGENT_VERSION,
                "display_protocol": display_backend.HOST_AGENT_DISPLAY_PROTOCOL,
                "capabilities": sorted(display_backend.HOST_BRIDGE_REQUIRED_CAPABILITIES),
            }).encode())
        body = json.dumps({
            "ok": False, "error": remote_code, "status": 409,
            "detail": f"{token} {private}", "token": token, "config": private,
        }).encode()
        if transport == "http-error":
            raise urllib.error.HTTPError(request.full_url, 409, "Conflict", None, BytesIO(body))
        return Response(body)

    monkeypatch.setenv("QA_MCP_REMOTE_CLIENT", "0")
    monkeypatch.setenv("QA_MCP_HOST_AGENT", "foreign.invalid:8999")
    monkeypatch.setattr(display_backend.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(socket, "create_connection", lambda *a, **kw: pytest.fail("unexpected socket"))
    monkeypatch.setattr(display_backend.LocalXTestBackend, "send_keys", lambda *a, **kw: pytest.fail("unexpected X11"))
    server = mcp_server.create_mcp_server(settings=Settings(
        manager_templates="remote-manager.json", value_read_templates="remote-value.json",
        remote_client=True, host_agent="review.invalid:8123", host_agent_token=token,
    ))
    arguments = {"keys": ["F5"]} if tool == "send_keys" else {
        "pid": 7, "port": 15444, "lifecycle_id": "owned",
        "lifecycle_handle": {"id": "owned", "pid": 7, "port": 15444},
    }
    result = asyncio.run(server.call_tool(tool, arguments)).structured_content
    assert result["ok"] is False
    assert result["error"] == expected_code
    assert result["status"] == 409
    assert result["mode"] == "remote-client"
    assert result["detail"] == "host agent request failed"
    assert token not in repr(result) and private not in repr(result)
    assert len(json.dumps(result)) < 512
    operation_path = "/send_keys" if tool == "send_keys" else "/testclient/stop"
    expected_paths = ["/v1/capabilities"]
    if failure_path == "operation":
        expected_paths.append(operation_path)
    assert calls == ["http://review.invalid:8123" + path for path in expected_paths]


def test_real_factories_isolate_host_lifecycle_settings_and_current_attachment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Lifecycle construction follows its factory, never the process environment."""

    process_environment = {
        "QA_MCP_REMOTE_CLIENT": "1",
        "QA_MCP_HOST_AGENT": "foreign.example:8001",
        "QA_MCP_HOST_AGENT_TOKEN": "foreign-token",
    }
    for name, value in process_environment.items():
        monkeypatch.setenv(name, value)
    before_environment = dict(os.environ)
    constructions: list[tuple[str, str, str, int, float, str, str]] = []
    operations: list[tuple[str, str, int]] = []
    status_probes: list[tuple[str, int]] = []
    launches: dict[str, int] = {}
    stops: list[tuple[str, int, int, str, dict[str, Any] | None]] = []

    class Backend:
        def __init__(self, settings: Settings) -> None:
            self.settings = settings

        def launch_test_client(self, **kwargs: Any) -> dict[str, Any]:
            port = kwargs["port"]
            launches[self.settings.host_agent] = launches.get(self.settings.host_agent, 0) + 1
            ordinal = launches[self.settings.host_agent]
            pid = port * 10 + ordinal
            lifecycle_id = f"{self.settings.host_agent}-launch-{ordinal}"
            operations.append(("launch", self.settings.host_agent, port))
            return {
                "ok": True, "pid": pid, "port": port, "alive": True,
                "listening": True, "owns_process": True, "lifecycle_id": lifecycle_id,
                "lifecycle_handle": {"id": lifecycle_id, "pid": pid, "port": port},
                "client_target": {"pid": pid, "port": port, "lifecycle_id": lifecycle_id},
            }

        def test_client_status(self, *, port: int) -> dict[str, Any]:
            operations.append(("attach", self.settings.host_agent, port))
            return {"ok": True, "pid": port, "port": port, "listening": True}

        def stop_test_client(self, *, pid: int, port: int, lifecycle_id: str | None = None,
                             lifecycle_handle: dict[str, Any] | None = None, **_kwargs: Any) -> dict[str, Any]:
            operations.append(("stop", self.settings.host_agent, port))
            stops.append((self.settings.host_agent, pid, port, str(lifecycle_id), lifecycle_handle))
            return {"ok": True, "state": "stopped", "stopped": True}

    def from_settings(cls, settings: Settings) -> Backend:  # noqa: ANN001 - classmethod seam
        del cls
        constructions.append((
            settings.host_agent, settings.host_agent_token, settings.host_agent_expected_version,
            settings.host_agent_client_port, settings.host_agent_timeout,
            settings.host_agent_window, settings.platform_version,
        ))
        return Backend(settings)

    monkeypatch.setattr(
        mcp_server.client_display.RemoteAgentBackend, "from_settings", classmethod(from_settings),
    )
    monkeypatch.setattr(
        mcp_server.client_display.RemoteAgentBackend, "from_env",
        classmethod(lambda _cls, *_args, **_kwargs: pytest.fail("factory lifecycle must not read process env")),
    )
    def target_from_env(cls, _env: dict[str, str], **kwargs: Any):  # noqa: ANN001 - classmethod seam
        kwargs.update(infobase_path="/factory", platform_root="/platform", user="factory")
        return cls(**kwargs)

    monkeypatch.setattr(
        mcp_server.client_lifecycle.TestClientTarget, "from_env", classmethod(target_from_env),
    )
    monkeypatch.setattr(
        mcp_server.client_lifecycle, "attach_test_client",
        lambda **kwargs: type("Attached", (), {"status": lambda self: {
            "host": kwargs["host"], "port": kwargs["port"], "pid": kwargs["port"],
            "listening": True, "owns_process": False,
        }})(),
    )
    def port_is_listening(host: str, port: int) -> bool:
        status_probes.append((host, port))
        return len(status_probes) <= 2

    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", port_is_listening)

    def factory_settings(address: str, port: int, token: str, version: str) -> Settings:
        return Settings(
            manager_templates=f"{address}-manager.json", value_read_templates=f"{address}-value.json",
            remote_client=True, host_agent=address, host_agent_token=token,
            host_agent_expected_version=version, host_agent_expected_sha256=f"{address}-sha",
            host_agent_window=f"{address}-window", host_agent_client_port=port,
            client_host=f"{address}-client", client_port=port - 1,
            host_agent_timeout=float(port) / 1000, platform_version=f"{address}-platform",
        )

    first = mcp_server.create_mcp_server(
        settings=factory_settings("first.example:8101", 15441, "first-token", "first-version"),
    )
    second = mcp_server.create_mcp_server(
        settings=factory_settings("second.example:8102", 15442, "second-token", "second-version"),
    )

    first_launch = asyncio.run(first.call_tool("launch_test_client", {})).structured_content
    second_launch = asyncio.run(second.call_tool("launch_test_client", {})).structured_content
    first_status = asyncio.run(first.call_tool("test_client_status", {})).structured_content
    second_status = asyncio.run(second.call_tool("test_client_status", {})).structured_content
    first_attach = asyncio.run(first.call_tool("attach_test_client", {})).structured_content
    replacement_launch = asyncio.run(first.call_tool("launch_test_client", {})).structured_content
    stopped = asyncio.run(first.call_tool("stop_test_client", {
        "pid": replacement_launch["pid"], "port": replacement_launch["lifecycle_handle"]["port"],
        "lifecycle_id": replacement_launch["lifecycle_id"],
        "lifecycle_handle": replacement_launch["lifecycle_handle"],
    })).structured_content

    assert first_launch["host"] == "first.example:8101-client"
    assert second_launch["host"] == "second.example:8102-client"
    assert first_status["host"] == "first.example:8101-client"
    assert second_status["host"] == "second.example:8102-client"
    assert first_attach["host"] == "first.example:8101-client"
    assert stopped["stopped"] is True
    assert first_launch["lifecycle_id"] == "first.example:8101-launch-1"
    assert replacement_launch["lifecycle_id"] == "first.example:8101-launch-2"
    assert replacement_launch["client_target"]["lifecycle_id"] != first_launch["client_target"]["lifecycle_id"]
    assert stops == [(
        "first.example:8101", replacement_launch["pid"], replacement_launch["port"],
        replacement_launch["lifecycle_id"], replacement_launch["lifecycle_handle"],
    )]
    assert mcp_server.application_context(first).attachment is None
    second_attachment = mcp_server.application_context(second).attachment
    assert second_attachment is not None
    assert second_attachment.status["client_target"]["lifecycle_id"] == "second.example:8102-launch-1"
    assert constructions == [
        ("first.example:8101", "first-token", "first-version", 15441, 15.441,
         "first.example:8101-window", "first.example:8101-platform"),
        ("second.example:8102", "second-token", "second-version", 15442, 15.442,
         "second.example:8102-window", "second.example:8102-platform"),
        ("first.example:8101", "first-token", "first-version", 15441, 15.441,
         "first.example:8101-window", "first.example:8101-platform"),
        ("first.example:8101", "first-token", "first-version", 15441, 15.441,
         "first.example:8101-window", "first.example:8101-platform"),
        ("first.example:8101", "first-token", "first-version", 15441, 15.441,
         "first.example:8101-window", "first.example:8101-platform"),
    ]
    assert operations == [
        ("launch", "first.example:8101", 15440),
        ("launch", "second.example:8102", 15441),
        ("attach", "first.example:8101", 15441),
        ("launch", "first.example:8101", 15440),
        ("stop", "first.example:8101", 15440),
    ]
    assert status_probes == [
        ("first.example:8101-client", 15440),
        ("second.example:8102-client", 15441),
        ("first.example:8101-client", 15440),
    ]
    assert dict(os.environ) == before_environment


def test_real_factories_route_replacement_lifecycle_handles_to_the_current_attachment(monkeypatch) -> None:
    """Real HTTP backend construction keeps A-old/A-new/B lifecycle targets separate."""

    calls: list[tuple[str, dict[str, Any]]] = []
    launches: dict[str, int] = {}

    class Response:
        headers = {"Content-Type": "application/json"}

        def __init__(self, value: dict[str, Any]) -> None:
            self.value = json.dumps(value).encode()

        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *exc: object) -> bool:
            return False

        def read(self) -> bytes:
            return self.value

    def fake_urlopen(request, timeout):  # noqa: ANN001 - urllib boundary
        del timeout
        body = json.loads(request.data) if request.data else {}
        calls.append((request.full_url, body))
        if request.full_url.endswith("/v1/capabilities"):
            return Response({
                "api": display_backend.HOST_BRIDGE_API,
                "api_major": display_backend.HOST_BRIDGE_API_MAJOR,
                "version": display_backend.HOST_AGENT_VERSION,
                "display_protocol": display_backend.HOST_AGENT_DISPLAY_PROTOCOL,
                "capabilities": sorted(display_backend.HOST_BRIDGE_REQUIRED_CAPABILITIES),
            })
        if request.full_url.endswith("/testclient/launch"):
            host = request.full_url.split("/")[2]
            launches[host] = launches.get(host, 0) + 1
            ordinal = launches[host]
            pid = (1000 if host.startswith("first") else 2000) + ordinal
            lifecycle_id = f"{host}-launch-{ordinal}"
            return Response({"ok": True, "alive": True, "listening": True,
                             "owns_process": True, "pid": pid, "port": body["port"],
                             "lifecycle_id": lifecycle_id,
                             "lifecycle_handle": {"id": lifecycle_id, "pid": pid, "port": body["port"]},
                             "client_target": {"kind": "host-agent-testclient", "pid": pid,
                                               "port": body["port"], "lifecycle_id": lifecycle_id}})
        return Response({"ok": True, "state": "stopped", "stopped": True})

    monkeypatch.setattr(display_backend.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(mcp_server.client_lifecycle, "load_env_file", lambda _path: {})

    def target_from_env(cls, _env, **kwargs):  # noqa: ANN001 - classmethod seam
        kwargs.update(infobase_path="/factory", platform_root="/platform", user="factory")
        return cls(**kwargs)

    monkeypatch.setattr(mcp_server.client_lifecycle.TestClientTarget, "from_env", classmethod(target_from_env))

    def settings(host: str, port: int) -> Settings:
        return Settings(manager_templates=f"{host}.json", value_read_templates=f"{host}-value.json",
                        remote_client=True, host_agent=host, host_agent_token=f"{host}-token",
                        client_host=f"{host}-client", client_port=port - 1,
                        host_agent_client_port=port)

    first = mcp_server.create_mcp_server(settings=settings("first.example:8123", 15441))
    second = mcp_server.create_mcp_server(settings=settings("second.example:8123", 15442))
    first_old = asyncio.run(first.call_tool("launch_test_client", {})).structured_content
    second_current = asyncio.run(second.call_tool("launch_test_client", {})).structured_content
    first_new = asyncio.run(first.call_tool("launch_test_client", {})).structured_content
    assert first_old["lifecycle_id"] != first_new["lifecycle_id"]
    assert first_new["client_target"]["lifecycle_id"] == first_new["lifecycle_id"]
    assert second_current["client_target"]["lifecycle_id"] == second_current["lifecycle_id"]
    assert asyncio.run(first.call_tool("send_keys", {"keys": ["F5"]})).structured_content["backend"] == "remote-agent"
    assert asyncio.run(second.call_tool("send_keys", {"keys": ["F6"]})).structured_content["backend"] == "remote-agent"
    stopped = asyncio.run(first.call_tool("stop_test_client", {
        "pid": first_new["pid"], "port": first_new["port"],
        "lifecycle_id": first_new["lifecycle_id"], "lifecycle_handle": first_new["lifecycle_handle"],
    })).structured_content
    assert stopped["stopped"] is True
    assert mcp_server.application_context(first).attachment is None
    assert mcp_server.application_context(second).attachment.status["lifecycle_id"] == second_current["lifecycle_id"]
    sends = [(url, body["client_target"]["lifecycle_id"]) for url, body in calls if url.endswith("/send_keys")]
    assert sends == [
        ("http://first.example:8123/send_keys", first_new["lifecycle_id"]),
        ("http://second.example:8123/send_keys", second_current["lifecycle_id"]),
    ]
    stops = [(url, body) for url, body in calls if url.endswith("/testclient/stop")]
    assert stops == [("http://first.example:8123/testclient/stop", {
        "pid": first_new["pid"], "port": first_new["port"],
        "lifecycle_id": first_new["lifecycle_id"], "lifecycle_handle": first_new["lifecycle_handle"],
    })]


def test_factory_context_survives_interleaved_and_exceptional_async_calls() -> None:
    """Contextvars isolate nested factory work and restore the direct caller."""

    caller = current_application_context()

    async def first_probe(*, fail: bool = False) -> dict[str, str]:
        await asyncio.sleep(0)
        context = current_application_context()
        if fail:
            raise RuntimeError(f"first failure on {context.settings.host_agent}")
        return {"factory": "first", "host_agent": context.settings.host_agent}

    async def second_probe() -> dict[str, str]:
        await asyncio.sleep(0)
        return {"factory": "second", "host_agent": current_application_context().settings.host_agent}

    first = mcp_server.create_mcp_server(
        settings=Settings(
            manager_templates="first-manager.json", value_read_templates="first-value.json",
            remote_client=True, host_agent="first.example:8101",
        ),
        extra_tools={"probe": first_probe},
    )
    second = mcp_server.create_mcp_server(
        settings=Settings(
            manager_templates="second-manager.json", value_read_templates="second-value.json",
            remote_client=True, host_agent="second.example:8102",
        ),
        extra_tools={"probe": second_probe},
    )

    async def interleave() -> tuple[dict[str, Any], dict[str, Any]]:
        first_result, second_result = await asyncio.gather(
            first.call_tool("probe", {}), second.call_tool("probe", {}),
        )
        return first_result.structured_content, second_result.structured_content

    first_result, second_result = asyncio.run(interleave())
    assert first_result == {"factory": "first", "host_agent": "first.example:8101"}
    assert second_result == {"factory": "second", "host_agent": "second.example:8102"}
    with pytest.raises(Exception, match="first failure"):
        asyncio.run(first.call_tool("probe", {"fail": True}))
    assert current_application_context() is caller

    legacy = display_backend.RemoteAgentBackend.from_env({
        "QA_MCP_REMOTE_CLIENT": "1", "QA_MCP_HOST_AGENT": "legacy.example:8123",
        "QA_MCP_HOST_AGENT_TOKEN": "legacy-token", "QA_MCP_CLIENT_PORT": "15390",
        "QA_MCP_HOST_AGENT_CLIENT_PORT": "15444", "QA_MCP_HOST_AGENT_TIMEOUT": "23",
    })
    assert (legacy.address, legacy.token, legacy.client_port, legacy.timeout) == (
        "legacy.example:8123", "legacy-token", 15444, 23.0,
    )


def test_real_factories_bind_distinct_transport_settings_without_environment_mutation(monkeypatch) -> None:
    """Composed tools expose their factory Settings, not a conflicting process relay."""

    monkeypatch.setenv("QA_MCP_TESTCLIENT_RELAY_ENDPOINT", "process.example:15382")
    monkeypatch.setenv("QA_MCP_TESTCLIENT_RELAY_TOKEN", "process-synthetic-token")
    bound_environment = dict(os.environ)
    sockets: list[object] = []
    destinations: list[tuple[str, int]] = []

    class RelaySocket:
        def __init__(self) -> None:
            self.reply = bytearray(b"OK\n")
            self.sent: list[bytes] = []
            self.closed = False

        def sendall(self, payload: bytes) -> None:
            self.sent.append(payload)

        def recv(self, count: int) -> bytes:
            if not self.reply:
                return b""
            result = bytes(self.reply[:count])
            del self.reply[:count]
            return result

        def close(self) -> None:
            self.closed = True

    def create_connection(address: tuple[str, int], **_kwargs: object) -> RelaySocket:
        destinations.append(address)
        relay_socket = RelaySocket()
        sockets.append(relay_socket)
        return relay_socket

    monkeypatch.setattr(client_transport.socket, "create_connection", create_connection)

    async def probe() -> dict[str, str]:
        settings = active_application_settings()
        assert settings is not None
        assert await asyncio.to_thread(active_application_settings) is settings
        host, port = settings.testclient_relay_endpoint.rsplit(":", 1)
        client_transport.connect_testclient((host, int(port)), timeout=0.25).close()
        return {
            "endpoint": settings.testclient_relay_endpoint,
            "token": settings.testclient_relay_token,
        }

    first = mcp_server.create_mcp_server(settings=Settings(
        manager_templates="first-manager.json", value_read_templates="first-value.json",
        testclient_relay_endpoint="first.example:15382", testclient_relay_token="first-synthetic-token",
    ), extra_tools={"transport_scope_probe": probe})
    second = mcp_server.create_mcp_server(settings=Settings(
        manager_templates="second-manager.json", value_read_templates="second-value.json",
        testclient_relay_endpoint="second.example:15383", testclient_relay_token="second-synthetic-token",
    ), extra_tools={"transport_scope_probe": probe})

    async def interleave() -> tuple[dict[str, str], dict[str, str]]:
        first_result, second_result = await asyncio.gather(
            first.call_tool("transport_scope_probe", {}), second.call_tool("transport_scope_probe", {}),
        )
        return first_result.structured_content, second_result.structured_content

    assert asyncio.run(interleave()) == (
        {"endpoint": "first.example:15382", "token": "first-synthetic-token"},
        {"endpoint": "second.example:15383", "token": "second-synthetic-token"},
    )
    assert set(destinations) == {("first.example", 15382), ("second.example", 15383)}
    assert {relay_socket.sent[0] for relay_socket in sockets} == {
        b"QA-MCP-TESTCLIENT-RELAY/1 first-synthetic-token\n",
        b"QA-MCP-TESTCLIENT-RELAY/1 second-synthetic-token\n",
    }
    assert all(relay_socket.closed for relay_socket in sockets)
    assert dict(os.environ) == bound_environment


def test_real_factories_keep_workspace_output_out_of_conflicting_process_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Factory-bound capture output follows A/B/empty Settings, never process root C."""

    process_root = tmp_path / "process-c"
    static_root = tmp_path / "static-fallback"
    monkeypatch.setenv("QA_MCP_HOME", str(process_root))
    monkeypatch.setattr(mcp_server, "__file__", str(static_root / "src/qa_mcp/mcp_server.py"))

    class Backend:
        def capture_screenshot(self, _display: str, out_path: Path, *, window: str | None = None) -> dict[str, object]:
            del window
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(b"factory-owned-output")
            return {"path": str(out_path), "size_bytes": out_path.stat().st_size}

    monkeypatch.setattr(mcp_server, "_display_backend", lambda: Backend())

    def capture_default() -> dict[str, object]:
        screenshot = mcp_server._capture_screenshot_impl(":109", None, None)
        return {"path": screenshot["path"], "capture": str(mcp_server.resolve_capture_dir("fixture", mcp_server._repo_root()))}

    def factory(home: str) -> object:
        return mcp_server.create_mcp_server(settings=Settings(
            manager_templates="manager.json", value_read_templates="value.json", home=home,
        ), extra_tools={"capture_default": capture_default})

    first = factory(str(tmp_path / "app-a"))
    second = factory(str(tmp_path / "app-b"))
    empty = factory("")
    for root, label in ((tmp_path / "app-a", "A"), (tmp_path / "app-b", "B"), (static_root, "empty")):
        capture = root / "runtime" / "protocol-research" / "captures" / "fixture"
        capture.mkdir(parents=True)
        (capture / "marker.txt").write_text(label, encoding="utf-8")
        (root / "manager.json").write_text(label, encoding="utf-8")
    before = {root: sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
              for root in (tmp_path / "app-a", tmp_path / "app-b", static_root, process_root)}
    results = [
        asyncio.run(server.call_tool("capture_default", {})).structured_content
        for server in (first, second, empty)
    ]
    paths = [Path(result["path"]) for result in results]
    capture_paths = [Path(result["capture"]) for result in results]

    assert [path.read_bytes() for path in paths] == [b"factory-owned-output"] * 3
    assert paths[0].is_relative_to(tmp_path / "app-a" / "runtime")
    assert paths[1].is_relative_to(tmp_path / "app-b" / "runtime")
    assert paths[2].is_relative_to(static_root / "runtime")
    assert [path.joinpath("marker.txt").read_text(encoding="utf-8") for path in capture_paths] == ["A", "B", "empty"]
    assert all(not path.is_relative_to(process_root) for path in [*paths, *capture_paths])
    after = {root: sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
             for root in (tmp_path / "app-a", tmp_path / "app-b", static_root, process_root)}
    assert after[process_root] == before[process_root] == []
    assert all(path.relative_to(root).as_posix() in set(after[root]) - set(before[root])
               for root, path in zip((tmp_path / "app-a", tmp_path / "app-b", static_root), paths, strict=True))
    assert not process_root.exists()


def test_real_factories_load_capture_templates_and_default_output_from_their_own_roots(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """The real scenario callback reads A/B/empty captures and templates before writing output."""

    process_root = tmp_path / "process-c"
    static_root = tmp_path / "static-fallback"
    monkeypatch.setenv("QA_MCP_HOME", str(process_root))
    monkeypatch.setattr(mcp_server, "__file__", str(static_root / "src/qa_mcp/mcp_server.py"))
    loads: list[tuple[str, Path, bytes]] = []

    class Bootstrap:
        @staticmethod
        def load(path: Path) -> object:
            loads.append(("capture", path, (path / "traffic.jsonl").read_bytes()))
            return object()

    class Templates:
        @staticmethod
        def load(path: Path) -> object:
            loads.append(("template", path, path.read_bytes()))
            return object()

    class Runner:
        def __init__(self, *_args: object, output_dir: Path, **_kwargs: object) -> None:
            self.output_dir = output_dir

        def run_single_session(self, scenario: Scenario) -> ScenarioResult:
            self.output_dir.mkdir(parents=True)
            (self.output_dir / "factory-output.txt").write_text(scenario.name, encoding="utf-8")
            return ScenarioResult(name=scenario.name, status="passed", steps=[])

    monkeypatch.setattr(mcp_server, "CaptureBootstrap", Bootstrap)
    monkeypatch.setattr(mcp_server, "ProtocolTemplates", Templates)
    monkeypatch.setattr(mcp_server, "ScenarioRunner", Runner)
    monkeypatch.setattr(mcp_server, "synthesize_bootstrap", lambda: object())
    monkeypatch.setattr(mcp_server.client_lifecycle, "port_is_listening", lambda *_args: True)

    roots = ((tmp_path / "app-a", b"A"), (tmp_path / "app-b", b"B"), (static_root, b"empty"))
    servers = [mcp_server.create_mcp_server(settings=Settings(
        manager_templates="manager.json", value_read_templates="value.json", home=str(root),
    )) for root, _label in roots[:2]]
    servers.append(mcp_server.create_mcp_server(settings=Settings(
        manager_templates="manager.json", value_read_templates="value.json", home="",
    )))
    for root, label in roots:
        capture = root / "runtime/protocol-research/captures/factory"
        capture.mkdir(parents=True)
        (capture / "traffic.jsonl").write_bytes(label + b"-capture")
        (root / "manager.json").write_bytes(label + b"-template")

    feature = 'Scenario: factory root\n  Given I read active window\n'
    monitored_roots = [root for root, _label in roots] + [process_root]
    for server, (owner, _label) in zip(servers, roots, strict=True):
        before = {
            root: {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            for root in monitored_roots if root.exists()
        }
        tool = {tool.name: tool for tool in asyncio.run(server.list_tools())}["run_scenario"]
        result = tool.fn(capture_dir="factory", scenario_json=None, feature_text=feature)
        assert result["status"] == "passed"
        after = {
            root: {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            for root in monitored_roots if root.exists()
        }
        for foreign in monitored_roots:
            if foreign != owner:
                assert after.get(foreign, {}) == before.get(foreign, {})
        additions = set(after[owner]) - set(before[owner])
        assert len(additions) == 1
        assert next(iter(additions)).name == "factory-output.txt"

    assert loads == [
        (kind, root / relative, label + suffix)
        for root, label in roots
        for kind, relative, suffix in (
            ("capture", Path("runtime/protocol-research/captures/factory"), b"-capture"),
            ("template", Path("manager.json"), b"-template"),
        )
    ]


def test_nested_factory_root_scope_restores_outer_and_direct_env_compatibility(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Nested failure restores exact roots; unbound direct calls still read env."""

    process_root = tmp_path / "process-c"
    process_ownership = tmp_path / "process-c-owned"
    monkeypatch.setenv("QA_MCP_HOME", str(process_root))
    monkeypatch.setenv("QA_MCP_TESTCLIENT_OWNERSHIP_ROOT", str(process_ownership))
    outer_root = tmp_path / "app-a"
    inner_root = tmp_path / "app-b"
    outer_ownership = tmp_path / "app-a-owned"
    inner_ownership = tmp_path / "app-b-owned"
    static_root = tmp_path / "static-fallback"
    static_ownership = static_root / "runtime/protocol-research/testclient-lifecycle"
    monkeypatch.setattr(mcp_server, "__file__", str(static_root / "src/qa_mcp/mcp_server.py"))
    monkeypatch.setattr(mcp_server.client_lifecycle, "DEFAULT_OWNERSHIP_ROOT", static_ownership)

    trace: list[tuple[str, ApplicationContext, Path, Path]] = []

    def observe(label: str) -> None:
        trace.append((
            label, current_application_context(), mcp_server._repo_root(),
            mcp_server.client_lifecycle.ownership_root(),
        ))

    async def fail_inside_b() -> None:
        observe("inner")
        raise RuntimeError("inner root failure")

    inner = mcp_server.create_mcp_server(settings=Settings(
        manager_templates="manager.json", value_read_templates="value.json", home=str(inner_root),
        testclient_ownership_root=str(inner_ownership),
    ), extra_tools={"fail_inside_b": fail_inside_b})

    inner_tool = {tool.name: tool for tool in asyncio.run(inner.list_tools())}["fail_inside_b"]

    async def observe_outer() -> None:
        observe("outer-before")
        with pytest.raises(Exception, match="inner root failure"):
            # Invoke the actual registered callback in the caller's task. A
            # separate call_tool task could mask a missing context reset.
            await inner_tool.fn()
        observe("outer-after")

    outer = mcp_server.create_mcp_server(settings=Settings(
        manager_templates="manager.json", value_read_templates="value.json", home=str(outer_root),
        testclient_ownership_root=str(outer_ownership),
    ), extra_tools={"observe_outer": observe_outer})
    outer_tool = {tool.name: tool for tool in asyncio.run(outer.list_tools())}["observe_outer"]
    caller = ApplicationContext(settings=Settings(
        manager_templates="manager.json", value_read_templates="value.json", home=str(tmp_path / "caller"),
    ), executor=LocalQAExecutor())

    async def invoke_registered() -> None:
        with activate_application_context(caller):
            observe("caller-before")
            await outer_tool.fn()
            observe("caller-after")

    asyncio.run(invoke_registered())

    async def observe_empty() -> str:
        return f"{id(current_application_context())}|{mcp_server._repo_root()}|{mcp_server.client_lifecycle.ownership_root()}"

    empty = mcp_server.create_mcp_server(settings=Settings(
        manager_templates="manager.json", value_read_templates="value.json", home="", testclient_ownership_root="",
    ), extra_tools={"observe_empty": observe_empty})
    empty_tool = {tool.name: tool for tool in asyncio.run(empty.list_tools())}["observe_empty"]
    empty_result = asyncio.run(empty_tool.fn())

    assert trace == [
        ("caller-before", caller, tmp_path / "caller", tmp_path / "caller" / "runtime/protocol-research/testclient-lifecycle"),
        ("outer-before", mcp_server.application_context(outer), outer_root, outer_ownership),
        ("inner", mcp_server.application_context(inner), inner_root, inner_ownership),
        ("outer-after", mcp_server.application_context(outer), outer_root, outer_ownership),
        ("caller-after", caller, tmp_path / "caller", tmp_path / "caller" / "runtime/protocol-research/testclient-lifecycle"),
    ]
    assert empty_result == f"{id(mcp_server.application_context(empty))}|{static_root}|{static_ownership}"
    assert mcp_server._repo_root() == process_root
    assert mcp_server.client_lifecycle.ownership_root() == process_ownership


def test_nested_async_factories_preserve_attachment_target_and_context(monkeypatch) -> None:
    """Nested calls keep each real backend's application-local attachment."""

    calls: list[tuple[str, dict[str, Any]]] = []

    class Response:
        headers = {"Content-Type": "application/json"}

        def __init__(self, value: dict[str, Any]) -> None:
            self.value = json.dumps(value).encode()

        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *exc: object) -> bool:
            return False

        def read(self) -> bytes:
            return self.value

    def fake_urlopen(request, timeout):  # noqa: ANN001 - urllib boundary
        del timeout
        body = json.loads(request.data) if request.data else {}
        calls.append((request.full_url, body))
        if request.full_url.endswith("/v1/capabilities"):
            return Response({
                "api": display_backend.HOST_BRIDGE_API,
                "api_major": display_backend.HOST_BRIDGE_API_MAJOR,
                "version": display_backend.HOST_AGENT_VERSION,
                "display_protocol": display_backend.HOST_AGENT_DISPLAY_PROTOCOL,
                "capabilities": sorted(display_backend.HOST_BRIDGE_REQUIRED_CAPABILITIES),
            })
        return Response({"ok": True})

    monkeypatch.setattr(display_backend.urllib.request, "urlopen", fake_urlopen)
    before_environment = dict(os.environ)

    async def failing_nested_probe() -> None:
        assert current_application_context() is second_context
        assert active_application_settings() is second_context.settings
        assert second_context.attachment is second_attachment
        await asyncio.sleep(0)
        raise RuntimeError("inner B failure")

    second = mcp_server.create_mcp_server(settings=Settings(
        manager_templates="second-manager.json", value_read_templates="second-value.json",
        remote_client=True, host_agent="second.example:8123", host_agent_token="second-token",
        host_agent_client_port=15442,
    ), extra_tools={"failing_nested_probe": failing_nested_probe})
    second_context = mcp_server.application_context(second)
    second_context.attachment = mcp_server._AttachedTestClientContext(
        host="second-client", port=15442, attached_at=2.0,
        status={"client_target": {"kind": "host-agent-testclient", "pid": 202,
                                  "port": 15442, "lifecycle_id": "second-current"}},
    )
    second_attachment = second_context.attachment
    caller = current_application_context()

    async def nested_probe(*, fail: bool = False) -> dict[str, str]:
        assert current_application_context() is first_context
        assert active_application_settings() is first_context.settings
        nested = await second.call_tool("send_keys", {"keys": ["F2"]})
        assert nested.structured_content["backend"] == "remote-agent"
        assert current_application_context() is first_context
        assert active_application_settings() is first_context.settings
        with pytest.raises(Exception, match="inner B failure"):
            await second.call_tool("failing_nested_probe", {})
        assert current_application_context() is first_context
        assert active_application_settings() is first_context.settings
        assert first_context.attachment is first_attachment
        assert second_context.attachment is second_attachment
        resumed = await first.call_tool("send_keys", {"keys": ["F7"]})
        assert resumed.structured_content["backend"] == "remote-agent"
        assert current_application_context() is first_context
        await asyncio.sleep(0)
        if fail:
            raise RuntimeError("nested failure")
        return {"outer": first_context.settings.host_agent, "nested": second_context.settings.host_agent}

    first = mcp_server.create_mcp_server(settings=Settings(
        manager_templates="first-manager.json", value_read_templates="first-value.json",
        remote_client=True, host_agent="first.example:8123", host_agent_token="first-token",
        host_agent_client_port=15441,
    ), extra_tools={"nested_probe": nested_probe})
    first_context = mcp_server.application_context(first)
    first_context.attachment = mcp_server._AttachedTestClientContext(
        host="first-client", port=15441, attached_at=1.0,
        status={"client_target": {"kind": "host-agent-testclient", "pid": 101,
                                  "port": 15441, "lifecycle_id": "first-old"}},
    )
    first_attachment = first_context.attachment

    async def interleave() -> tuple[dict[str, Any], dict[str, Any]]:
        return await asyncio.gather(
            first.call_tool("nested_probe", {}), second.call_tool("send_keys", {"keys": ["F3"]}),
        )

    assert asyncio.run(first.call_tool("send_keys", {"keys": ["F1"]})).structured_content["backend"] == "remote-agent"
    nested, direct = asyncio.run(interleave())
    assert nested.structured_content == {"outer": "first.example:8123", "nested": "second.example:8123"}
    assert direct.structured_content["backend"] == "remote-agent"
    with pytest.raises(Exception, match="nested failure"):
        asyncio.run(first.call_tool("nested_probe", {"fail": True}))
    assert asyncio.run(first.call_tool("send_keys", {"keys": ["F4"]})).structured_content["backend"] == "remote-agent"
    assert current_application_context() is caller
    assert first_context.attachment.status["client_target"]["lifecycle_id"] == "first-old"
    assert second_context.attachment.status["client_target"]["lifecycle_id"] == "second-current"
    sent = [(url, body["client_target"], body["client_port"]) for url, body in calls if url.endswith("/send_keys")]
    first_request = (
        "http://first.example:8123/send_keys",
        {"kind": "host-agent-testclient", "pid": 101, "port": 15441, "lifecycle_id": "first-old"},
        15441,
    )
    second_request = (
        "http://second.example:8123/send_keys",
        {"kind": "host-agent-testclient", "pid": 202, "port": 15442, "lifecycle_id": "second-current"},
        15442,
    )
    assert sent[0] == sent[-1] == first_request
    assert sent.count(first_request) == 4 and sent.count(second_request) == 3
    assert len(sent) == 7
    assert dict(os.environ) == before_environment


def test_profiles_are_deterministic_and_omit_research_tools() -> None:
    standalone = mcp_server.profile_tool_names("standalone")
    research = mcp_server.profile_tool_names("research")

    assert standalone == tuple(sorted(standalone))
    assert research == tuple(sorted(research))
    assert len(research) == 68
    assert set(research) - set(standalone) == {
        "autofill_required_fields",
        "echo_jsonrpc_arguments",
        "generate_smoke_suite",
        "measure_scenario",
    }
    standalone_digest = mcp_server.profile_schema_digest("standalone")
    research_digest = mcp_server.profile_schema_digest("research")
    assert standalone_digest == (
        "c43228b613662058541644f26b96c8e0e691a2716fb59f352c4eed7795f42ee4"
    )
    assert research_digest == (
        "59f8fa567e4f254ae3307670468eb96290b5a460f1ad5acf2f385a0ccb76c71c"
    )

    first = mcp_server.create_mcp_server(settings=_settings(), tool_profile="standalone")
    second = mcp_server.create_mcp_server(settings=_settings(), tool_profile="research")
    first_names = {tool.name for tool in asyncio.run(first.list_tools())}
    second_names = {tool.name for tool in asyncio.run(second.list_tools())}
    assert first_names == set(standalone)
    assert second_names == set(research)
    assert "measure_scenario" not in first_names


def test_profile_schema_canonicalization_ignores_generator_metadata_and_union_order() -> None:
    first = {
        "title": "PythonPatchSpecificTitle",
        "anyOf": [{"type": "null"}, {"type": "string", "description": "value"}],
        "default": "/opt/checkout/src/qa_mcp/_bundled/8.3/templates/value.json",
        "required": ["second", "first"],
    }
    second = {
        "title": "AnotherGeneratedTitle",
        "anyOf": [{"description": "value", "type": "string"}, {"type": "null"}],
        "default": "C:\\repo\\src\\qa_mcp\\_bundled\\8.3\\templates\\value.json",
        "required": ["first", "second"],
    }

    assert mcp_server._canonical_profile_schema(first) == mcp_server._canonical_profile_schema(second)


def test_local_and_windows_adapters_implement_same_public_contract() -> None:
    request = OperationRequest(OperationKind.LIFECYCLE, "status")
    handler = lambda _request: {"listening": True}

    for executor_type in (LocalQAExecutor, WindowsHostQAExecutor):
        executor = executor_type({(OperationKind.LIFECYCLE, "status"): handler})
        result = executor.execute(request, target=None, session=None)
        assert result.verdict is OperationVerdict.SUCCESS
        assert result.value == {"listening": True}


def test_public_package_has_no_reverse_private_imports() -> None:
    forbidden = {"runtime_proxy", "runtime_relay", "live_mcp", "team_registry", "agent_core"}
    package_root = Path(mcp_server.__file__).resolve().parent
    violations: list[str] = []
    for source in sorted(package_root.rglob("*.py")):
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                root = name.replace("-", "_").split(".", 1)[0]
                if root in forbidden:
                    violations.append(f"{source.relative_to(package_root)}:{node.lineno}:{name}")
    assert violations == []
