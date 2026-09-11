"""Focused C1-C3 coverage for bound active-window observation/assertion semantics."""

from pathlib import Path
from dataclasses import asdict
import hashlib
from types import SimpleNamespace
import asyncio
import json

from qa_mcp import mcp_server
from qa_mcp.config import Settings
import pytest

from qa_mcp.core import (
    LocalQAExecutor, OperationKind, WindowsHostQAExecutor, OperationRequest,
    current_application_context, execute_mcp_operation,
    OperationResult, OperationVerdict, SessionIdentity, resolve_runtime_target,
    ArtifactReference,
    OperationError,
)
from qa_mcp.core.boundary import normalize_operation_result
from tests.support.runtime_targets import TargetProfileInputs
from qa_mcp.protocol.evidence import get_readonly_operation_descriptor
from qa_mcp.protocol.session import ActiveWindowContext, InitialUiContext
from qa_mcp.scenario import Scenario, ScenarioRunner, Step

from tests.test_positive_operation_boundary_integration import _context


class _Session:
    def __init__(self, context: ActiveWindowContext):
        self.context = context
        self.calls = 0
        self.native_arguments = None
        self.failure = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def get_active_window_context(self, **arguments):
        assert "_expected_window" not in arguments
        self.native_arguments = arguments
        self.calls += 1
        if self.failure is not None:
            raise self.failure
        return self.context

def _actual_context(tmp_path: Path, ref: str | None, markers: list[str], *, status: str = "ok") -> ActiveWindowContext:
    base = InitialUiContext(
        status=status,
        capture_dir=tmp_path,
        templates_path=tmp_path / "templates.json",
        output_dir=tmp_path,
        descriptor=get_readonly_operation_descriptor("active-window-context"),
        ack_guid=None,
        frame4_sequence=None,
        sent_byte_count=0,
        received_byte_count=0,
        frames=[],
    )
    return ActiveWindowContext(base, ref, markers)


def _runner(tmp_path: Path, session: _Session, executor_type=LocalQAExecutor) -> ScenarioRunner:
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
    return ScenarioRunner(
        session_factory=lambda: session,
        bootstrap=object(),
        templates=object(),
        output_dir=tmp_path / "run",
        operation_context=context,
    )


@pytest.mark.parametrize("executor_type", [LocalQAExecutor, WindowsHostQAExecutor])
def test_bound_observation_states_and_marker_count(tmp_path: Path, executor_type) -> None:
    for ref, markers, state in [
        (".MainFrame[x]", [".MainFrame[x]", "caption"], "observed"),
        (None, [], "missing"),
        (".Other[x]", ["caption"], "ambiguous"),
    ]:
        session = _Session(_actual_context(tmp_path, ref, markers))
        result = _runner(tmp_path, session, executor_type).run(Scenario("state", [Step("read_active_window", "read")]))
        value = __import__("json").loads(result.steps[0].preview)["value"]
        assert value == {"window_state": state, "marker_count": len(markers)}
        assert session.calls == 1


@pytest.mark.parametrize("executor_type", [LocalQAExecutor, WindowsHostQAExecutor])
def test_bound_predicate_matches_actual_markers_only_and_stays_private(tmp_path: Path, executor_type) -> None:
    session = _Session(_actual_context(tmp_path, ".MainFrame[secret-ref]", [".MainFrame[secret-ref]"]))
    runner = _runner(tmp_path, session, executor_type)
    result = runner.run(Scenario("match", [Step("read_active_window", "read", expect_contains="MainFrame")]))
    assert result.status == "passed"
    assert result.steps[0].assertion is True
    assert "secret-ref" not in result.steps[0].preview
    assert session.calls == 1

    mismatch = _Session(_actual_context(tmp_path, ".MainFrame[secret-ref]", [".MainFrame[secret-ref]"]))
    result = _runner(tmp_path, mismatch, executor_type).run(Scenario("mismatch", [Step("read_active_window", "read", expect_contains="success")]))
    assert result.status == "failed"
    assert result.steps[0].assertion is False


@pytest.mark.parametrize("executor_type", [LocalQAExecutor, WindowsHostQAExecutor])
@pytest.mark.parametrize(
    ("ref", "markers", "expected", "passed"),
    [
        (None, [], "observed", False),          # public words must not false-match
        (".Other[ref]", ["caption"], "Other", False),
        (".MainFrame[ref]", [".MainFrame[ref]"], "MainFrame", True),
        (".MainFrame[ref]", [".MainFrame[ref]"], "Missing", False),
        (".MainFrame[ref]", ["caption"], "MainFrame", False),
    ],
)
def test_bound_predicate_states_are_request_local_and_private(
    tmp_path: Path, executor_type, ref: str | None, markers: list[str], expected: str, passed: bool
) -> None:
    session = _Session(_actual_context(tmp_path, ref, markers))
    result = _runner(tmp_path, session, executor_type).run(
        Scenario("predicate", [Step("read_active_window", "read", expect_contains=expected)])
    )
    assert result.steps[0].assertion is passed
    assert session.calls == 1
    rendered = json.dumps(result.steps[0].__dict__, ensure_ascii=False, default=str)
    assert expected not in rendered
    assert all(fragment not in rendered for fragment in (".MainFrame[ref]", "caption", str(tmp_path)))


@pytest.mark.parametrize("executor_type", [LocalQAExecutor, WindowsHostQAExecutor])
def test_registered_shared_operation_uses_real_default_factory_and_one_native_read(
    tmp_path: Path, executor_type
) -> None:
    session = _Session(_actual_context(tmp_path, ".MainFrame[real-ref]", [".MainFrame[real-ref]"]))
    seed = _context(tmp_path, LocalQAExecutor())
    server = mcp_server.create_mcp_server(
        settings=Settings(
            manager_templates="manager.json", value_read_templates="value.json",
            remote_client=executor_type is WindowsHostQAExecutor,
        ),
        runtime_target=seed.runtime_target,
        session=seed.session,
        extra_tools={"shared_read": lambda: execute_mcp_operation(
            current_application_context(),
            OperationRequest(OperationKind.READ, "read_active_window", {
                "session": session, "bootstrap": object(), "templates": object(),
                "output_dir": tmp_path / "native", "synthesized": None,
            }),
        ).to_dict()},
        extra_tool_classes={"shared_read": "shared-operation"},
    )
    context = mcp_server.application_context(server)
    context.attachment = seed.attachment

    server_context = context
    assert type(server_context.executor) is executor_type
    payload = asyncio.run(server.call_tool("shared_read", {})).structured_content
    assert payload and payload["value"] == {"window_state": "observed", "marker_count": 1}
    assert session.calls == 1
    assert set(session.native_arguments) == {"bootstrap", "templates", "output_dir", "synthesized"}


def test_unsuccessful_native_observation_fails_closed(tmp_path: Path) -> None:
    session = _Session(_actual_context(tmp_path, ".MainFrame[x]", [".MainFrame[x]"], status="error"))
    result = _runner(tmp_path, session).run(Scenario("bad", [Step("read_active_window", "read")]))
    assert result.status == "failed"
    assert "executor reported an operation failure" in (result.steps[0].error or "")


@pytest.mark.parametrize(
    "context_factory",
    [
        lambda p: _actual_context(p, 7, [".MainFrame[x"]),
        lambda p: _actual_context(p, ".MainFrame[x]", ["x"] * 65),
        lambda p: _actual_context(p, ".MainFrame[x]", ["x" * 2049]),
    ],
)
def test_malformed_or_oversized_native_observation_is_fixed_private_failure(tmp_path: Path, context_factory) -> None:
    session = _Session(context_factory(tmp_path))
    result = _runner(tmp_path, session).run(Scenario("hostile", [Step("read_active_window", "read")]))
    assert result.status == "failed"
    rendered = json.dumps(result.steps[0].__dict__, ensure_ascii=False, default=str)
    assert "invalid" not in rendered or "executor" in rendered
    assert "MainFrame" not in rendered and str(tmp_path) not in rendered


def test_legacy_empty_redaction_negative_control_still_fails_real_match(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scoped test-only control: the pre-FIX-07 empty projection cannot satisfy a real predicate."""
    import qa_mcp.core.operations as operations

    monkeypatch.setattr(
        operations,
        "_project_bound_active_window",
        lambda raw, request: raw.__class__(request, raw.verdict, value={}, error=raw.error,
                                           artifacts=raw.artifacts, provenance=raw.provenance),
    )
    session = _Session(_actual_context(tmp_path, ".MainFrame[legacy]", [".MainFrame[legacy]"]))
    result = _runner(tmp_path, session).run(
        Scenario("legacy-negative", [Step("read_active_window", "read", expect_contains="MainFrame")])
    )
    assert result.status == "failed"
    assert result.steps[0].assertion is False


def test_unbound_direct_and_scenario_paths_retain_legacy_context_data(tmp_path: Path) -> None:
    session = _Session(_actual_context(tmp_path, ".Legacy[ref]", [".Legacy[ref]"]))
    context = mcp_server.application_context(mcp_server.create_mcp_server())
    operation = execute_mcp_operation(context, OperationRequest(
        OperationKind.READ, "read_active_window", {"session": session},
    ))
    assert operation.verdict is OperationVerdict.SUCCESS
    assert operation.value["active_window_ref"] == ".Legacy[ref]"
    assert session.calls == 1
    direct = ScenarioRunner(
        session_factory=lambda: session,
        bootstrap=object(), templates=object(), output_dir=tmp_path / "legacy",
    ).run(Scenario("legacy", [Step("read_active_window", "read")]))
    assert direct.status == "passed"
    assert ".Legacy[ref]" in direct.steps[0].preview
    assert session.calls == 2


def _policy_factory(tmp_path, executor_type, policy, session):
    """Actual admission and default registry; only the native session is fake."""
    (tmp_path / "evidence").mkdir(exist_ok=True)
    (tmp_path / "target.env").write_text("INFOBASE_PATH=/private/fixture\n")
    inputs = TargetProfileInputs(tmp_path, evidence_policy=policy,
                                non_production_approved=policy == "full_local")
    inputs.write_profile()
    resolution = resolve_runtime_target(inputs.handoff_env())
    assert resolution is not None
    identity = SessionIdentity("session-7", resolution.binding.target, 7)
    native = {"bootstrap": object(), "templates": object(),
              "output_dir": tmp_path / "native", "synthesized": None}

    def shared_read(expected: str | None = None) -> dict:
        arguments = {"session": session, **native}
        if expected is not None:
            arguments["_expected_window"] = expected
        return execute_mcp_operation(current_application_context(), OperationRequest(
            OperationKind.READ, "read_active_window", arguments,
        )).to_dict()

    server = mcp_server.create_mcp_server(
        settings=Settings(manager_templates="manager.json", value_read_templates="value.json",
                          remote_client=executor_type is WindowsHostQAExecutor,
                          client_host="127.0.0.1", client_port=15381),
        runtime_target=resolution, session=identity,
        extra_tools={"shared_read": shared_read},
        extra_tool_classes={"shared_read": "shared-operation"},
    )
    context = mcp_server.application_context(server)
    context.attachment = {"target": context.target, "session": identity,
                          "binding_generation": 7, "host": "127.0.0.1",
                          "port": 15381, "display": ":99"}
    assert type(context.executor) is executor_type
    return server, context, native


@pytest.mark.parametrize("executor_type", [LocalQAExecutor, WindowsHostQAExecutor])
@pytest.mark.parametrize("policy", ["sanitized", "full_local"])
def test_c1_c2_real_factory_public_and_scenario_partition(tmp_path, executor_type, policy):
    ref = ".MainFrame[WINDOW-PRIVATE]"
    dto = _actual_context(tmp_path / "CAPTURE-PRIVATE", ref, [ref, "CAPTION-PRIVATE"])
    dto.base_context.frames = [{"private": "FRAME-PRIVATE"}]
    session = _Session(dto)
    server, context, native = _policy_factory(tmp_path, executor_type, policy, session)
    runner = ScenarioRunner(lambda: session, native["bootstrap"], native["templates"],
                            tmp_path / "run", operation_context=context)
    caller = current_application_context()
    # Same application and session across different expectations and failures.
    rows = [(ref, [ref, "CAPTION-PRIVATE"], "MainFrame", True, "observed"),
            (ref, [ref], "ABSENT-PRIVATE", False, "observed"),
            (ref, [ref], "CAPTURE-PRIVATE", False, "observed"),
            (ref, [ref], "FRAME-PRIVATE", False, "observed"),
            (ref, [ref], "success", False, "observed"),
            (ref, [ref], "observed", False, "observed"),
            (None, [], "MainFrame", False, "missing"),
            (ref, ["CAPTION-PRIVATE"], "CAPTION-PRIVATE", False, "ambiguous"),
            (ref, [ref], "", False, "observed"),
            (ref, [ref], "MainFrame", True, "observed")]
    for active_ref, markers, expected, passed, state in rows:
        dto.active_window_ref, dto.active_window_markers = active_ref, markers
        before = session.calls
        payload = asyncio.run(server.call_tool("shared_read", {"expected": expected})).structured_content
        assert payload["verdict"] == "success"
        assert payload["value"] == {"window_state": state, "marker_count": len(markers),
                                    "assertion_passed": passed}
        assert session.calls == before + 1 and session.native_arguments == native
        scenario = runner.run(Scenario("partition", [Step("read_active_window", "read",
                                                        expect_contains=expected)]))
        step = scenario.steps[0]
        assert step.assertion is passed
        assert step.status == ("ok" if passed else "assert_failed")
        assert session.calls == before + 2
        assert session.native_arguments == {**native, "output_dir": tmp_path / "run" / "step_01_read_active_window"}
        rendered = json.dumps([payload, asdict(step)])
        for fragment in (ref, "WINDOW-PRIVATE", "CAPTION-PRIVATE", "FRAME-PRIVATE",
                         "CAPTURE-PRIVATE", "ABSENT-PRIVATE", str(tmp_path), "_expected_window"):
            assert fragment not in rendered
        assert current_application_context() is caller
        assert context.evidence_ledger._active == {}
    payload = asyncio.run(server.call_tool("shared_read", {})).structured_content
    assert payload["value"] == {"window_state": "observed", "marker_count": 1}
    assert "assertion_passed" not in payload["value"]


def test_c2_bound_missing_boolean_cannot_fallback_to_public_preview(tmp_path, monkeypatch):
    import qa_mcp.core.operations as operations
    session = _Session(_actual_context(tmp_path, ".MainFrame[x]", [".MainFrame[x]"]))
    runner = _runner(tmp_path, session)
    monkeypatch.setattr(operations, "_project_bound_active_window",
                        lambda raw, request: OperationResult.success(request, value={}))
    step = runner.run(Scenario("no-fallback", [Step("read_active_window", "read",
                                                  expect_contains="success")])).steps[0]
    assert '"verdict": "success"' in step.preview
    assert step.assertion is False and step.status == "assert_failed"
    assert session.calls == 1


@pytest.mark.parametrize("items", [64, 65])
def test_c3_projection_preserves_raw_top_level_item_bound(tmp_path, items):
    session = _Session(_actual_context(tmp_path, ".MainFrame[x]", [".MainFrame[x]"]))
    _, context, _ = _policy_factory(tmp_path, LocalQAExecutor, "sanitized", session)
    raw = session.context.to_result()
    raw.update({f"unknown{i}": "PRIVATE-EXTRA" for i in range(items - len(raw))})
    context.executor = LocalQAExecutor({(OperationKind.READ, "read_active_window"): lambda request: raw})
    result = execute_mcp_operation(context, OperationRequest(OperationKind.READ, "read_active_window"))
    if items == 64:
        assert result.verdict is OperationVerdict.SUCCESS
        assert result.value == {"window_state": "observed", "marker_count": 1}
    else:
        assert result.verdict is OperationVerdict.FAILURE
        assert result.error.code == "result-too-large"
        assert result.value is None and result.artifacts == ()
    assert "PRIVATE-EXTRA" not in json.dumps(result.to_dict())
    assert context.evidence_ledger._active == {}


@pytest.mark.parametrize("value", [
    {"window_state": "PRIVATE-STATE"}, {"window_state": True},
    {"marker_count": True}, {"marker_count": -1}, {"marker_count": 2**31},
    {"assertion_passed": 1}, {"assertion_passed": "PRIVATE-BOOL"},
    {"window_state": type("PrivateString", (str,), {})("observed")},
])
def test_c3_actual_production_schema_rejects_wrong_classes_and_literals(tmp_path, value):
    session = _Session(_actual_context(tmp_path, ".MainFrame[x]", [".MainFrame[x]"]))
    _, context, native = _policy_factory(tmp_path, LocalQAExecutor, "sanitized", session)
    request = OperationRequest(OperationKind.READ, "read_active_window", {"session": session, **native})
    admitted = execute_mcp_operation(context, request)
    assert admitted.verdict is OperationVerdict.SUCCESS
    result = normalize_operation_result(context, request, OperationResult.success(request, value=value),
                                        admitted.provenance)
    assert result.verdict is OperationVerdict.FAILURE
    assert result.error.code == "invalid-executor-result"
    assert result.value is None and result.artifacts == ()
    assert "PRIVATE" not in json.dumps(result.to_dict())


@pytest.mark.parametrize("executor_type", [LocalQAExecutor, WindowsHostQAExecutor])
@pytest.mark.parametrize("policy", ["sanitized", "full_local"])
@pytest.mark.parametrize("mode", ["status", "exception", "ref-type", "marker-subclass", "list-subclass", "count", "scalar"])
def test_c1_c2_failures_are_private_and_next_request_recovers(tmp_path, executor_type, policy, mode):
    ref = ".MainFrame[PRIVATE-REF]"
    dto = _actual_context(tmp_path / "PRIVATE-CAPTURE", ref, [ref])
    session = _Session(dto)
    server, context, native = _policy_factory(tmp_path, executor_type, policy, session)
    if mode == "status":
        dto.base_context.status = "error"
    elif mode == "exception":
        session.failure = RuntimeError("PRIVATE-EXCEPTION")
    elif mode == "ref-type":
        dto.active_window_ref = 7
    elif mode == "marker-subclass":
        dto.active_window_markers = [type("Marker", (str,), {})(ref)]
    elif mode == "list-subclass":
        dto.active_window_markers = type("Markers", (list,), {})([ref])
    elif mode == "count":
        dto.active_window_markers = [ref] * 65
    else:
        dto.active_window_markers = ["PRIVATE-MARKER" * 2048]
    payload = asyncio.run(server.call_tool("shared_read", {"expected": "PRIVATE-EXPECTED"})).structured_content
    assert payload["verdict"] == "failure"
    expected_code = ("executor-failure" if mode in {"status", "exception"}
                     else "result-too-large" if mode == "count" else "invalid-executor-result")
    expected_message = ("executor reported an operation failure" if expected_code == "executor-failure"
                        else "operation result was not admitted")
    assert payload["error"] == {"code": expected_code, "message": expected_message, "retryable": False}
    assert "value" not in payload and "artifacts" not in payload
    assert session.calls == 1 and session.native_arguments == native
    runner = ScenarioRunner(lambda: session, native["bootstrap"], native["templates"],
                            tmp_path / "run", operation_context=context)
    step = runner.run(Scenario("failure", [Step("read_active_window", "read",
                                              expect_contains="PRIVATE-EXPECTED")])).steps[0]
    assert step.status == "error" and step.assertion is None
    assert session.calls == 2
    rendered = json.dumps([payload, asdict(step)])
    assert "PRIVATE" not in rendered and str(tmp_path) not in rendered
    assert context.evidence_ledger._active == {}
    session.failure = None
    session.context = _actual_context(tmp_path, ref, [ref])
    recovered = runner.run(Scenario("recovery", [Step("read_active_window", "read", expect_contains="MainFrame")]))
    assert recovered.status == "passed" and recovered.steps[0].assertion is True
    assert session.calls == 3 and context.evidence_ledger._active == {}


@pytest.mark.parametrize("expected", [False, 42, [], {"private": "PRIVATE-EXPECTED"},
                                      type("Expected", (str,), {})("MainFrame"), "x" * 2049])
def test_c2_invalid_expectation_fails_closed_without_native_forwarding(tmp_path, expected):
    session = _Session(_actual_context(tmp_path, ".MainFrame[x]", [".MainFrame[x]"]))
    runner = _runner(tmp_path, session)
    step = runner.run(Scenario("invalid", [Step("read_active_window", "read", expect_contains=expected)])).steps[0]
    assert step.status == "assert_failed" and step.assertion is False
    assert session.calls == 1 and "_expected_window" not in session.native_arguments
    assert "PRIVATE-EXPECTED" not in json.dumps(asdict(step))


def test_c3_actual_catalog_provenance_and_scope_receipts_stay_authoritative(tmp_path):
    contexts = []
    for owner in ("one", "two"):
        root = tmp_path / owner
        root.mkdir()
        session = _Session(_actual_context(root, ".MainFrame[x]", [".MainFrame[x]"]))
        _, context, native = _policy_factory(root, LocalQAExecutor, "full_local", session)
        request = OperationRequest(OperationKind.READ, "read_active_window", {"session": session, **native})
        admitted = execute_mcp_operation(context, request)
        assert admitted.verdict is OperationVerdict.SUCCESS
        artifact_path = context.evidence_ledger.root / "shot.png"
        artifact_path.write_bytes(b"synthetic-current-evidence")
        contexts.append((context, request, admitted.provenance, artifact_path))
    first, request, provenance, path = contexts[0]
    second, _, _, other_path = contexts[1]
    with pytest.raises(TypeError):
        first.operation_schemas["read_active_window"] = ()
    digest = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    raw = OperationResult.success(request, value={"window_state": "observed", "marker_count": 1})
    raw = OperationResult(raw.request, raw.verdict, value=raw.value,
                          artifacts=(ArtifactReference("shot.one", "image/png", digest, "PRIVATE-CLAIM", "internal"),),
                          provenance={"token": "PRIVATE-PROVENANCE"})
    with first.evidence_ledger.operation() as expired:
        stale = expired.record("shot.one", path)
    with first.evidence_ledger.operation() as current, second.evidence_ledger.operation() as foreign:
        receipt = current.record("shot.one", path)
        other = foreign.record("shot.one", other_path)
        before_other = dict(second.evidence_ledger._records)
        accepted = normalize_operation_result(first, request, raw, provenance,
                                             scope=current, receipts=(receipt,))
        assert accepted.verdict is OperationVerdict.SUCCESS
        assert accepted.artifacts[0].path == str(path.resolve())
        assert accepted.provenance == provenance
        assert "PRIVATE" not in json.dumps(accepted.to_dict())
        for claim in (other, stale, SimpleNamespace(artifact_id="shot.one", path=path)):
            rejected = normalize_operation_result(first, request, raw, provenance,
                                                 scope=current, receipts=(claim,))
            assert rejected.verdict is OperationVerdict.FAILURE
            assert rejected.error.code == "invalid-evidence-receipt"
            assert rejected.value is None and rejected.artifacts == ()
            assert rejected.provenance == provenance
            assert "PRIVATE" not in json.dumps(rejected.to_dict())
            assert second.evidence_ledger._records == before_other
        forged = normalize_operation_result(first, request, raw, {"token": "PRIVATE"},
                                           scope=current, receipts=(receipt,))
        assert forged.error.code == "invalid-executor-result" and forged.provenance is None
    assert first.evidence_ledger._active == second.evidence_ledger._active == {}
    assert first.evidence_ledger._records == second.evidence_ledger._records == {}


def test_c3_success_with_error_remains_a_complete_invalid_result(tmp_path):
    session = _Session(_actual_context(tmp_path, ".MainFrame[x]", [".MainFrame[x]"]))
    _, context, _ = _policy_factory(tmp_path, LocalQAExecutor, "sanitized", session)
    context.executor = LocalQAExecutor({(OperationKind.READ, "read_active_window"):
        lambda request: OperationResult(request, OperationVerdict.SUCCESS,
            value=session.context.to_result(), error=OperationError("PRIVATE", "PRIVATE"))})
    result = execute_mcp_operation(context, OperationRequest(OperationKind.READ, "read_active_window"))
    assert result.verdict is OperationVerdict.FAILURE
    assert result.error.code == "invalid-executor-result"
    assert result.value is None and result.artifacts == ()
    assert "PRIVATE" not in json.dumps(result.to_dict())


def test_c3_projection_rejects_non_string_keys_without_comparison_callbacks(tmp_path):
    calls = []
    class Key:
        def __hash__(self):
            return hash("status")
        def __eq__(self, other):
            calls.append(other)
            return False
    session = _Session(_actual_context(tmp_path, ".MainFrame[x]", [".MainFrame[x]"]))
    _, context, _ = _policy_factory(tmp_path, LocalQAExecutor, "sanitized", session)
    raw = {Key(): "ok", "active_window_ref": ".MainFrame[x]", "active_window_markers": [".MainFrame[x]"]}
    assert calls == []
    context.executor = LocalQAExecutor({(OperationKind.READ, "read_active_window"): lambda request: raw})
    result = execute_mcp_operation(context, OperationRequest(OperationKind.READ, "read_active_window"))
    assert result.error.code == "invalid-executor-result"
    assert result.value is None and result.artifacts == ()
    assert calls == []
