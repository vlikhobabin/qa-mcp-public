from __future__ import annotations

import asyncio
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import pytest

from tests.support.boundary_inputs import encoded as _encoded, nested_arrays as _nested_arrays
from tests.support.runtime_targets import TargetProfileInputs

from qa_mcp import mcp_server
from qa_mcp.config import Settings
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
    current_application_context,
    execute_mcp_operation,
    execute_scenario_operation,
    resolve_runtime_target,
)
from qa_mcp.scenario import Scenario, ScenarioRunner, Step
from qa_mcp.protocol.session import ActiveWindowContext, InitialUiContext
from qa_mcp.protocol.evidence import get_readonly_operation_descriptor


REQUEST = OperationRequest(OperationKind.READ, "read_active_window")
CANONICAL_URL = "https://docs.example.com/safe%20guide"



def _settings() -> Settings:
    return Settings(
        manager_templates="manager.json",
        value_read_templates="value.json",
        client_host="127.0.0.1",
        client_port=15381,
    )


def _resolution(tmp_path: Path):
    (tmp_path / "evidence").mkdir(exist_ok=True)
    (tmp_path / "target.env").write_text("INFOBASE_PATH=/private/test\n", encoding="utf-8")
    inputs = TargetProfileInputs(tmp_path)
    inputs.write_profile()
    resolution = resolve_runtime_target(inputs.handoff_env())
    assert resolution is not None
    return resolution


def _attachment(context: ApplicationContext, **changes: Any) -> dict[str, Any]:
    assert context.runtime_target is not None and context.session is not None
    values = {
        "target": context.runtime_target.binding.target,
        "session": context.session,
        "binding_generation": context.runtime_target.binding.binding_generation,
        "host": "127.0.0.1",
        "port": 15381,
        "display": ":99",
    }
    values.update(changes)
    return values


def _raw(request: OperationRequest, verdict: OperationVerdict, value: Any, *, details: Any = None) -> OperationResult:
    error = None
    if verdict is not OperationVerdict.SUCCESS:
        error = OperationError(
            "EXECUTOR-PRIVATE",
            "executor private detail",
            True,
            details if details is not None else {"referenceLabel": "Reference label 7"},
        )
    return OperationResult(
        request=OperationRequest(OperationKind.WRITE, "executor_replacement"),
        verdict=verdict,
        value=value,
        error=error,
        provenance={"token": "EXECUTOR-PROVENANCE"},
    )


class _Session:
    def __enter__(self):
        return self

    def __exit__(self, *exc: object) -> None:
        return None


def _context(tmp_path: Path, executor: Any) -> ApplicationContext:
    resolution = _resolution(tmp_path)
    session = SessionIdentity(
        "session-7", resolution.binding.target, resolution.binding.binding_generation,
    )
    context = ApplicationContext(
        settings=_settings(),
        executor=executor,
        target=resolution.binding.target,
        runtime_target=resolution,
        session=session,
    )
    context.attachment = _attachment(context)
    return context


def _assert_provenance(payload: dict[str, Any]) -> None:
    assert payload["provenance"] == {
        "operation": "read_active_window",
        "target": "project-demo",
        "binding": "qa-demo",
        "fingerprint": "sha256:" + "a" * 64,
        "generation": 7,
        "evidence_policy": "sanitized",
        "session": "session-7",
    }
    assert "EXECUTOR-PROVENANCE" not in json.dumps(payload)


@pytest.mark.parametrize("executor_type", [LocalQAExecutor, WindowsHostQAExecutor])
@pytest.mark.parametrize(
    "mutation",
    [
        "target",
        "session-missing",
        "attachment-missing",
        "session-target",
        "session-id",
        "session-id-symmetric",
        "runtime-target-none",
        "runtime-target-delete",
        "attachment-target",
        "attachment-session",
        "generation",
        "host",
        "port",
        "display",
        "arguments",
    ],
)
def test_bound_route_rejects_before_local_or_windows_adapter(
    tmp_path: Path, executor_type: type, mutation: str
) -> None:
    calls: list[OperationRequest] = []

    def handler(request: OperationRequest) -> OperationResult:
        calls.append(request)
        return _raw(request, OperationVerdict.SUCCESS, {"status": "ok", "active_window_ref": ".MainFrame[x]", "active_window_markers": [".MainFrame[x]"]})

    context = _context(
        tmp_path,
        executor_type({(OperationKind.READ, "read_active_window"): handler}),
    )
    arguments: Any = {"host": "127.0.0.1", "port": 15381, "display": ":99"}
    foreign = TargetIdentity("foreign", "sha256:" + "f" * 64)
    if mutation == "target":
        context.target = foreign
    elif mutation == "session-missing":
        context.session = None
    elif mutation == "attachment-missing":
        context.attachment = None
    elif mutation == "session-target":
        context.session = SessionIdentity("session-7", foreign, context.session.sequence)
    elif mutation == "session-id":
        context.session = SessionIdentity("C:private", context.target, context.session.sequence)
    elif mutation == "session-id-symmetric":
        context.session = SessionIdentity("C:private", context.target, context.session.sequence)
        context.attachment["session"] = context.session
    elif mutation == "runtime-target-none":
        object.__setattr__(context, "runtime_target", None)
    elif mutation == "runtime-target-delete":
        object.__delattr__(context, "runtime_target")
    elif mutation == "attachment-target":
        context.attachment["target"] = foreign
    elif mutation == "attachment-session":
        context.attachment["session"] = SessionIdentity("other", context.target, context.session.sequence)
    elif mutation == "generation":
        context.attachment["binding_generation"] = 8
    elif mutation in {"host", "port", "display"}:
        arguments[mutation] = {"host": "foreign", "port": 15444, "display": ":100"}[mutation]
    else:
        arguments = {"host": "127.0.0.1"}
        arguments = type("Arguments", (dict,), {})(arguments)

    result = execute_mcp_operation(
        context, OperationRequest(OperationKind.READ, "read_active_window", arguments)
    )
    assert result.verdict is OperationVerdict.BLOCKED
    assert result.error and result.error.code == "runtime-target-route-blocked"
    assert calls == []
    rendered = json.dumps(result.to_dict(), sort_keys=True)
    assert "foreign" not in rendered and ":100" not in rendered and "15444" not in rendered


@pytest.mark.parametrize("executor_type", [LocalQAExecutor, WindowsHostQAExecutor])
def test_post_admission_identity_drift_cannot_change_adapter_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, executor_type: type
) -> None:
    seen: list[tuple[Any, Any]] = []

    class RecordingExecutor(executor_type):
        def execute(self, request, *, target, session):
            seen.append((target, session))
            return super().execute(request, target=target, session=session)

    context = _context(
        tmp_path,
        RecordingExecutor(
            {
                (OperationKind.READ, "read_active_window"): lambda request: _raw(
                    request, OperationVerdict.SUCCESS, {"status": "ok", "active_window_ref": ".MainFrame[x]", "active_window_markers": [".MainFrame[x]"]}
                )
            }
        ),
    )
    admitted_target, admitted_session = context.target, context.session
    original_operation = type(context.evidence_ledger).operation

    @contextmanager
    def drifting_operation(ledger, operation=None):
        with original_operation(ledger, operation) as scope:
            foreign = TargetIdentity("foreign", "sha256:" + "f" * 64)
            context.target = foreign
            context.session = SessionIdentity("foreign-session", foreign, 4)
            yield scope

    monkeypatch.setattr(type(context.evidence_ledger), "operation", drifting_operation)
    result = execute_mcp_operation(context, REQUEST)

    assert result.verdict is OperationVerdict.SUCCESS
    assert seen == [(admitted_target, admitted_session)]
    _assert_provenance(result.to_dict())
    assert context.evidence_ledger._active == {}


@pytest.mark.parametrize("executor_type", [LocalQAExecutor, WindowsHostQAExecutor])
def test_exact_bound_route_executes_once_inside_scope(tmp_path: Path, executor_type: type) -> None:
    calls: list[OperationRequest] = []
    active: list[int] = []
    context: ApplicationContext

    def handler(request: OperationRequest) -> OperationResult:
        calls.append(request)
        active.append(len(context.evidence_ledger._active))
        return _raw(request, OperationVerdict.SUCCESS, {"status": "ok", "active_window_ref": ".MainFrame[x]", "active_window_markers": [".MainFrame[x]"]})

    context = _context(
        tmp_path,
        executor_type({(OperationKind.READ, "read_active_window"): handler}),
    )
    marker = object()
    result = execute_mcp_operation(
        context,
        OperationRequest(
            OperationKind.READ,
            "read_active_window",
            {
                "host": "127.0.0.1",
                "port": 15381,
                "display": ":99",
                "session": marker,
            },
        ),
    )
    assert result.verdict is OperationVerdict.SUCCESS
    assert result.value == {"window_state": "observed", "marker_count": 1}
    _assert_provenance(result.to_dict())
    assert calls[0].arguments["session"] is marker
    assert len(calls) == 1 and active == [1] and context.evidence_ledger._active == {}


def test_concurrent_operations_keep_distinct_scopes_and_close_them(tmp_path: Path) -> None:
    barrier = threading.Barrier(2)
    active_snapshots: list[frozenset[object]] = []
    context: ApplicationContext

    def handler(request: OperationRequest) -> OperationResult:
        barrier.wait(timeout=3)
        active_snapshots.append(frozenset(context.evidence_ledger._active))
        barrier.wait(timeout=3)
        return _raw(request, OperationVerdict.SUCCESS, {"status": "ok", "active_window_ref": ".MainFrame[x]", "active_window_markers": [".MainFrame[x]"]})

    context = _context(
        tmp_path,
        LocalQAExecutor({(OperationKind.READ, "read_active_window"): handler}),
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(execute_mcp_operation, context, REQUEST) for _ in range(2)]
        results = [future.result(timeout=5) for future in futures]

    assert [result.verdict for result in results] == [
        OperationVerdict.SUCCESS,
        OperationVerdict.SUCCESS,
    ]
    assert len(active_snapshots) == 2
    assert all(len(snapshot) == 2 for snapshot in active_snapshots)
    assert context.evidence_ledger._active == {}


def test_unbound_and_pre_session_lifecycle_compatibility_remain(tmp_path: Path) -> None:
    calls: list[OperationRequest] = []

    def handler(request: OperationRequest) -> OperationResult:
        calls.append(request)
        return OperationResult.success(request, value={"legacy": True})

    executor = LocalQAExecutor(
        {
            (OperationKind.READ, "read_active_window"): handler,
            (OperationKind.LIFECYCLE, "test_client_status"): handler,
        }
    )
    unbound = ApplicationContext(settings=_settings(), executor=executor)
    assert execute_mcp_operation(unbound, REQUEST).value == {"legacy": True}

    resolution = _resolution(tmp_path)
    bound = ApplicationContext(
        settings=_settings(),
        executor=executor,
        target=resolution.binding.target,
        runtime_target=resolution,
    )
    lifecycle = OperationRequest(OperationKind.LIFECYCLE, "test_client_status")
    assert execute_mcp_operation(bound, lifecycle).value == {"legacy": True}
    assert [item.kind for item in calls] == [OperationKind.READ, OperationKind.LIFECYCLE]


def _public_payload(
    path: str,
    tmp_path: Path,
    verdict: OperationVerdict,
    value: Any,
    *,
    generic_details: bool = False,
) -> dict[str, Any]:
    def handler(request: OperationRequest) -> OperationResult:
        if generic_details:
            return _raw(request, OperationVerdict.FAILURE, None, details=value)
        return _raw(request, verdict, value)

    resolution = _resolution(tmp_path)
    session = SessionIdentity(
        "session-7", resolution.binding.target, resolution.binding.binding_generation,
    )
    executor = WindowsHostQAExecutor(
        {(OperationKind.READ, "read_active_window"): handler}
    )
    if path == "mcp":
        def shared_read() -> dict[str, Any]:
            result = execute_mcp_operation(current_application_context(), REQUEST)
            return result.to_dict()

        server = mcp_server.create_mcp_server(
            settings=_settings(),
            executor=executor,
            runtime_target=resolution,
            session=session,
            extra_tools={"shared_read": shared_read},
            extra_tool_classes={"shared_read": "shared-operation"},
        )
        context = mcp_server.application_context(server)
        context.attachment = _attachment(context)
        result = asyncio.run(server.call_tool("shared_read", {}))
        assert result.structured_content is not None
        return result.structured_content

    context = ApplicationContext(
        settings=_settings(),
        executor=executor,
        target=resolution.binding.target,
        runtime_target=resolution,
        session=session,
    )
    context.attachment = _attachment(context)
    runner = ScenarioRunner(
        session_factory=_Session,
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path / "scenario",
        operation_context=context,
    )
    scenario = runner.run(
        Scenario("public-boundary", [Step("read_active_window", "shared")])
    )
    step = scenario.steps[0]
    serialized = step.preview if step.status == "ok" else (step.error or "")
    if "operation_result=" in serialized:
        serialized = serialized.split("operation_result=", 1)[1]
    return json.loads(serialized)


@pytest.mark.parametrize("executor_type", [LocalQAExecutor, WindowsHostQAExecutor])
def test_default_scenario_handler_converts_trusted_active_window_context(
    tmp_path: Path, executor_type: type
) -> None:
    class TestClient(_Session):
        def get_active_window_context(self, **arguments: Any) -> ActiveWindowContext:
            assert {"bootstrap", "templates", "output_dir", "synthesized"} == set(arguments)
            base = InitialUiContext(
                status="ok", capture_dir=tmp_path, templates_path=tmp_path / "templates.json",
                output_dir=tmp_path, descriptor=get_readonly_operation_descriptor("active-window-context"),
                ack_guid=None, frame4_sequence=None, sent_byte_count=0, received_byte_count=0, frames=[],
            )
            return ActiveWindowContext(base, ".MainFrame[trusted]", [".MainFrame[trusted]"])

    seed = _context(tmp_path, LocalQAExecutor())
    server = mcp_server.create_mcp_server(
        settings=Settings(
            manager_templates="manager.json", value_read_templates="value.json",
            remote_client=executor_type is WindowsHostQAExecutor,
        ),
        runtime_target=seed.runtime_target,
        session=seed.session,
    )
    context = mcp_server.application_context(server)
    context.attachment = seed.attachment
    assert type(context.executor) is executor_type
    runner = ScenarioRunner(
        session_factory=TestClient,
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path / "default-handler",
        operation_context=context,
    )
    scenario = runner.run(
        Scenario("default-handler", [Step("read_active_window", "shared")])
    )
    payload = json.loads(scenario.steps[0].preview)

    assert scenario.steps[0].status == "ok"
    assert payload["verdict"] == "success"
    assert payload["value"] == {"window_state": "observed", "marker_count": 1}
    _assert_provenance(payload)
    assert "PRIVATE" not in json.dumps(payload)


def test_runner_uses_pre_execute_integration_snapshot(tmp_path: Path) -> None:
    runner: ScenarioRunner

    def handler(request: OperationRequest) -> OperationResult:
        runner.operation_context = None
        return _raw(
            request,
            OperationVerdict.FAILURE,
            {"referenceLabel": "Reference label 7"},
        )

    context = _context(
        tmp_path,
        WindowsHostQAExecutor(
            {(OperationKind.READ, "read_active_window"): handler}
        ),
    )
    runner = ScenarioRunner(
        session_factory=_Session,
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path / "runner-mutation",
        operation_context=context,
    )
    result = runner.run(
        Scenario("runner-mutation", [Step("read_active_window", "shared")])
    )
    error = result.steps[0].error or ""
    payload = json.loads(error.split("operation_result=", 1)[1])

    assert result.steps[0].status == "error"
    assert payload["verdict"] == "failure"
    _assert_provenance(payload)
    assert "AttributeError" not in error


@pytest.mark.parametrize("mutation", ["none", "delete"])
def test_runner_keeps_formerly_bound_route_failure_complete(
    tmp_path: Path, mutation: str
) -> None:
    calls: list[OperationRequest] = []

    def handler(request: OperationRequest) -> OperationResult:
        calls.append(request)
        return _raw(request, OperationVerdict.SUCCESS, {"status": "ok", "active_window_ref": ".MainFrame[x]", "active_window_markers": [".MainFrame[x]"]})

    context = _context(
        tmp_path,
        LocalQAExecutor({(OperationKind.READ, "read_active_window"): handler}),
    )
    if mutation == "none":
        object.__setattr__(context, "runtime_target", None)
    else:
        object.__delattr__(context, "runtime_target")
    runner = ScenarioRunner(
        session_factory=_Session,
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path / f"runner-formerly-bound-{mutation}",
        operation_context=context,
    )
    result = runner.run(
        Scenario("runner-formerly-bound", [Step("read_active_window", "shared")])
    )
    error = result.steps[0].error or ""
    payload = json.loads(error.split("operation_result=", 1)[1])

    assert calls == []
    assert payload["verdict"] == "blocked"
    assert payload["error"]["code"] == "runtime-target-route-blocked"
    assert "provenance" not in payload
    assert "AttributeError" not in error


@pytest.mark.parametrize("path", ["mcp", "scenario"])
@pytest.mark.parametrize("verdict", list(OperationVerdict))
def test_real_public_paths_preserve_four_verdicts_and_provenance(
    tmp_path: Path, path: str, verdict: OperationVerdict
) -> None:
    payload = _public_payload(
        path,
        tmp_path,
        verdict,
        {"status": "ok", "active_window_ref": ".MainFrame[x]", "active_window_markers": [".MainFrame[x]"]},
    )
    assert payload["verdict"] == verdict.value
    if verdict is OperationVerdict.SUCCESS:
        assert payload["value"] == {"window_state": "observed", "marker_count": 1}
    else:
        assert payload.get("value", {}) == {}
    _assert_provenance(payload)
    assert "EXECUTOR-PRIVATE" not in json.dumps(payload)
    assert "EXECUTOR-UNKNOWN" not in json.dumps(payload)


@pytest.mark.parametrize("path", ["mcp", "scenario"])
@pytest.mark.parametrize(
    "value",
    [
        {"active": 1},
        {"sequence": True},
        {"duration": float("inf")},
        {"referenceCount": -1},
        {"referenceLabel": "not-declared"},
        {"documentationURL": "http://127.0.0.1/private"},
    ],
)
def test_declared_mismatches_have_one_complete_public_result(
    tmp_path: Path, path: str, value: dict[str, Any]
) -> None:
    payload = _public_payload(path, tmp_path, OperationVerdict.SUCCESS, value, generic_details=True)
    assert payload["verdict"] == "failure"
    assert payload["error"] == {
        "code": "invalid-executor-result",
        "message": "operation result was not admitted",
        "retryable": False,
    }
    assert "value" not in payload and "artifacts" not in payload
    _assert_provenance(payload)


def _decoded_fragments(value: str) -> set[str]:
    fragments = {value}
    for _ in range(5):
        value = unquote(value)
        fragments.add(value)
    return fragments


@pytest.mark.parametrize("path", ["mcp", "scenario"])
@pytest.mark.parametrize("depth", range(1, 6))
@pytest.mark.parametrize("case", ["credential", "user", "userpass", "control"])
def test_real_public_paths_execute_exact_40_cell_url_matrix(
    tmp_path: Path, path: str, depth: int, case: str
) -> None:
    if case == "credential":
        url = "https://docs.example.com/" + _encoded("token=URL-SECRET", depth)
    elif case in {"user", "userpass"}:
        authority = "user@docs.example.com" if case == "user" else "user:pass@docs.example.com"
        url = "https://" + _encoded(authority, depth) + "/guide"
    else:
        url = "https://docs.example.com/" + _encoded("safe guide", depth)

    payload = _public_payload(path, tmp_path, OperationVerdict.SUCCESS, {"documentationURL": url}, generic_details=True)
    if case == "control" and depth <= 4:
        assert payload["error"]["details"]["documentationURL"] == CANONICAL_URL
    else:
        assert payload["error"]["code"] == "invalid-executor-result"
        assert payload["verdict"] == "failure"
        assert "details" not in payload["error"] and "value" not in payload
        rendered = json.dumps(payload, ensure_ascii=False)
        for fragment in _decoded_fragments(url):
            assert fragment not in rendered
        assert "URL-SECRET" not in rendered and "user:pass" not in rendered


@pytest.mark.parametrize("path", ["mcp", "scenario"])
@pytest.mark.parametrize(
    ("value", "accepted"),
    [
        ({"nested": _nested_arrays(5)}, True),
        ({"nested": _nested_arrays(6)}, True),
        ({"nested": _nested_arrays(7)}, False),
        ({**{f"unknown{i}": i for i in range(62)}, "active": True}, True),
        ({**{f"unknown{i}": i for i in range(63)}, "active": True}, True),
        ({**{f"unknown{i}": i for i in range(64)}, "active": True}, False),
    ],
)
def test_real_public_paths_preserve_structural_boundaries(
    tmp_path: Path, path: str, value: dict[str, Any], accepted: bool
) -> None:
    payload = _public_payload(path, tmp_path, OperationVerdict.SUCCESS, value, generic_details=True)
    assert payload["verdict"] == "failure"
    if accepted:
        assert payload["error"]["code"] == "executor-failure"
        expected = {key: value[key] for key in ("nested", "active") if key in value}
        assert payload["error"]["details"] == expected
    else:
        assert payload["error"]["code"] == "result-too-large"
        assert "details" not in payload["error"] and "value" not in payload
    assert len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()) <= 65_536


def _byte_value(tail_length: int) -> dict[str, Any]:
    prefix = "https://docs.example.com/"
    links = [prefix + "x" * (2048 - len(prefix)) for _ in range(31)]
    links.append(prefix + "y" * tail_length)
    return {"links": links}


@pytest.mark.parametrize("path", ["mcp", "scenario"])
def test_real_public_paths_preserve_exact_final_byte_boundary(
    tmp_path: Path, path: str
) -> None:
    seed = _public_payload(path, tmp_path, OperationVerdict.SUCCESS, _byte_value(1), generic_details=True)
    seed_size = len(
        json.dumps(seed, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    )
    tail = 1 + 65_535 - seed_size
    assert 1 <= tail <= 2_000
    below = _public_payload(path, tmp_path, OperationVerdict.SUCCESS, _byte_value(tail), generic_details=True)
    exact = _public_payload(path, tmp_path, OperationVerdict.SUCCESS, _byte_value(tail + 1), generic_details=True)
    above = _public_payload(path, tmp_path, OperationVerdict.SUCCESS, _byte_value(tail + 2), generic_details=True)
    compact = lambda payload: len(  # noqa: E731 - exact byte oracle stays local
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    )
    assert compact(below) == 65_535
    assert compact(exact) == 65_536
    assert above["error"]["code"] == "result-too-large"
    assert compact(above) < 65_536


def test_exceptional_adapter_closes_scope_and_returns_total_failure(tmp_path: Path) -> None:
    class ExplodingExecutor:
        name = "exploding"
        calls = 0

        def execute(self, request, *, target, session):
            del request, target, session
            self.calls += 1
            raise RuntimeError("PRIVATE-TRACE")

    executor = ExplodingExecutor()
    context = _context(tmp_path, executor)
    payload = execute_scenario_operation(context, REQUEST).to_dict()
    assert payload["verdict"] == "failure"
    assert payload["error"]["code"] == "executor-failure"
    assert executor.calls == 1 and context.evidence_ledger._active == {}
    assert "PRIVATE-TRACE" not in json.dumps(payload)
