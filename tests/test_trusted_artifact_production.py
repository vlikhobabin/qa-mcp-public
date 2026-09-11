"""C1-C3: real shared factories, trusted production, and per-operation ownership."""
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import threading

import pytest

from qa_mcp import mcp_server
from qa_mcp.core import (
    ArtifactReference, EvidenceReceipt, LocalQAExecutor, OperationError,
    OperationKind, OperationRequest, OperationResult, OperationVerdict,
    SessionIdentity, WindowsHostQAExecutor, activate_application_context,
    admit_operation_provenance, execute_scenario_operation, normalize_operation_result,
)
from qa_mcp.core import boundary
from tests.test_screenshot_retention import Backend, PAYLOAD, _tool
from tests.test_target_bound_evidence_cleanup import _context

DIGEST = "sha256:" + hashlib.sha256(PAYLOAD).hexdigest()


def _factory(root, policy="sanitized", remote=False):
    root.mkdir(parents=True, exist_ok=True)
    server, context = _context(root, evidence_policy=policy, remote=remote)
    if remote:
        server = mcp_server.create_mcp_server(
            settings=replace(context.settings, host_agent="http://bridge.example.invalid"),
            runtime_target=context.runtime_target,
        )
        context = mcp_server.application_context(server)
    context.session = SessionIdentity("session-7", context.target, 7)
    context.attachment = mcp_server._AttachedTestClientContext(
        "127.0.0.1", 15444, 1.0, {}, target=context.target,
        session=context.session, binding_generation=7, ownership_class="owned",
        lifecycle_id="local-7", display=":109",
    )
    assert type(context.executor) is (WindowsHostQAExecutor if remote else LocalQAExecutor)
    return server, context


def _capture(server, context, route="mcp", window=None):
    if route == "mcp":
        return json.loads(asyncio.run(_tool(server).run({"window": window})).content[0].text)
    with activate_application_context(context):
        return execute_scenario_operation(
            context, OperationRequest(OperationKind.DISPLAY, "capture_screenshot",
                                      {"display": ":109", "window": window}),
        ).to_dict()


def _fail(result, code):
    assert result["verdict"] == "failure"
    assert result["error"]["code"] == code
    assert result.get("artifacts", []) == []
    assert result.get("value") is None


def _alter_result(context, transform):
    original = context.executor.execute
    calls = []
    def execute(request, **kwargs):
        calls.append((request.name, kwargs["target"], kwargs["session"]))
        return transform(original(request, **kwargs), request)
    context.executor.execute = execute
    return calls


@pytest.mark.parametrize("policy", ["sanitized", "full_local"])
@pytest.mark.parametrize("route", ["mcp", "scenario"])
@pytest.mark.parametrize("variant,code", [
    ("old-file", "invalid-evidence-receipt"),
    ("absent-production", "invalid-evidence-receipt"),
    ("false-hash", "invalid-evidence-receipt"),
    ("empty-hash", "invalid-evidence-receipt"),
    ("invalid-id", "invalid-executor-result"),
    ("invalid-hash", "invalid-executor-result"),
    ("lookalike", "invalid-executor-result"),
    ("duplicate", "invalid-executor-result"),
    ("oversize", "result-too-large"),
])
def test_c1_raw_claims_never_mint_authority_and_keep_error_order(tmp_path, policy, route, variant, code):
    server, context = _factory(tmp_path, policy)
    borrowed = context.evidence_ledger.root / "old.png"
    borrowed.write_bytes(PAYLOAD)
    artifact = ArtifactReference("screenshot.claim", "image/png", DIGEST, str(borrowed), "internal")
    artifacts = () if variant == "absent-production" else (artifact,)
    if variant == "false-hash": artifacts = (replace(artifact, sha256="sha256:" + "0" * 64),)
    if variant == "empty-hash": artifacts = (replace(artifact, sha256=""),)
    if variant == "invalid-id": artifacts = (replace(artifact, artifact_id="BAD"),)
    if variant == "invalid-hash": artifacts = (replace(artifact, sha256="bad"),)
    if variant == "lookalike":
        class Lookalike(ArtifactReference): pass
        artifacts = (Lookalike("screenshot.claim"),)
    if variant == "duplicate": artifacts = (artifact, artifact)
    if variant == "oversize": artifacts = tuple(replace(artifact, artifact_id=f"shot.{i}") for i in range(65))
    calls = []
    def claim(request, **kwargs):
        calls.append((request.name, kwargs["target"], kwargs["session"]))
        return OperationResult(request, OperationVerdict.SUCCESS, artifacts=artifacts)
    context.executor.execute = claim
    result = _capture(server, context, route)
    _fail(result, code)
    assert str(tmp_path) not in json.dumps(result)
    assert borrowed.read_bytes() == PAYLOAD
    assert calls == [("capture_screenshot", context.target, context.session)]
    assert context.evidence_ledger._records == context.evidence_ledger._active == {}


@pytest.mark.parametrize("policy", ["sanitized", "full_local"])
@pytest.mark.parametrize("remote", [False, True])
@pytest.mark.parametrize("route", ["mcp", "scenario"])
def test_c2_default_factories_bind_actual_bytes_and_policy(tmp_path, monkeypatch, policy, remote, route):
    backend = Backend()
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    server, context = _factory(tmp_path, policy, remote)
    result = _capture(server, context, route, "own-window")
    assert result["verdict"] == "success"
    assert result["value"] == {"size_bytes": len(PAYLOAD)}
    assert len(backend.destinations) == 1
    destination = backend.destinations[0]
    assert destination.parent == context.evidence_ledger.root
    expected = {"artifact_id": "screenshot." + DIGEST[7:23], "media_type": "image/png",
                "sha256": DIGEST, "sensitivity": "internal"}
    if policy == "full_local":
        expected["path"] = str(destination)
        assert destination.read_bytes() == PAYLOAD
    else:
        assert not destination.exists()
        assert str(tmp_path) not in json.dumps(result)
    assert result["artifacts"] == [expected]
    assert "own-window" not in json.dumps(result)
    assert context.evidence_ledger._records == context.evidence_ledger._active == {}


@pytest.mark.parametrize("policy", ["sanitized", "full_local"])
@pytest.mark.parametrize("remote", [False, True])
@pytest.mark.parametrize("mode", ["borrowed", "symlink", "false-hash", "false-size", "empty", "raise-after-write"])
def test_c2_invalid_backend_production_preserves_foreign_files(tmp_path, monkeypatch, policy, remote, mode):
    server, context = _factory(tmp_path, policy, remote)
    borrowed = context.evidence_ledger.root / "borrowed.png"
    borrowed.write_bytes(b"foreign-sentinel")
    opened = []
    original_open = os.open
    def guarded_open(path, *args, **kwargs):
        if Path(path) == borrowed:
            opened.append(path)
            raise AssertionError("borrowed path must not be read")
        return original_open(path, *args, **kwargs)
    monkeypatch.setattr(boundary.os, "open", guarded_open)
    class BadBackend(Backend):
        def capture_screenshot(self, display, out_path, *, window=None):
            assert out_path.exists() and out_path.read_bytes() == b""  # exclusively allocated before backend
            value = super().capture_screenshot(display, out_path, window=window)
            if mode == "borrowed": value["path"] = str(borrowed)
            if mode == "symlink": out_path.unlink(); out_path.symlink_to(borrowed)
            if mode == "false-hash": value["sha256"] = "sha256:" + "0" * 64
            if mode == "false-size": value["size_bytes"] = len(PAYLOAD) + 1
            if mode == "empty": out_path.write_bytes(b""); value["size_bytes"] = 0
            if mode == "raise-after-write": raise RuntimeError("PRIVATE-BACKEND")
            return value
    backend = BadBackend()
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    result = _capture(server, context)
    _fail(result, "executor-failure")
    assert opened == []
    assert borrowed.read_bytes() == b"foreign-sentinel"
    assert set(context.evidence_ledger.root.iterdir()) == {borrowed}
    assert context.evidence_ledger._records == context.evidence_ledger._active == {}
    assert "PRIVATE-BACKEND" not in json.dumps(result)


@pytest.mark.parametrize("policy", ["sanitized", "full_local"])
@pytest.mark.parametrize("mode,code", [
    ("false-hash", "invalid-evidence-receipt"), ("empty-hash", "invalid-evidence-receipt"),
    ("changed-bytes", "invalid-evidence-receipt"), ("replaced-same-bytes", "invalid-evidence-receipt"),
    ("symlink", "invalid-evidence-receipt"), ("false-size", "invalid-evidence-receipt"),
    ("malformed", "invalid-executor-result"), ("overflow", "result-too-large"),
    ("raise", "executor-failure"),
    ("media", "invalid-evidence-receipt"), ("sensitivity", "invalid-evidence-receipt"),
])
def test_c2_postproduction_tampering_fails_and_cleans_own_capture(tmp_path, monkeypatch, policy, mode, code):
    server, context = _factory(tmp_path, policy)
    backend = Backend()
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    foreign = context.evidence_ledger.root / "foreign.png"
    foreign.write_bytes(PAYLOAD)
    def transform(raw, request):
        assert raw.verdict is OperationVerdict.SUCCESS
        artifact = raw.artifacts[0]
        produced = Path(artifact.path)
        if mode == "false-hash": return replace(raw, artifacts=(replace(artifact, sha256="sha256:" + "0" * 64),))
        if mode == "empty-hash": return replace(raw, artifacts=(replace(artifact, sha256=""),))
        if mode == "media": return replace(raw, artifacts=(replace(artifact, media_type="text/plain"),))
        if mode == "sensitivity": return replace(raw, artifacts=(replace(artifact, sensitivity="public"),))
        if mode == "changed-bytes": produced.write_bytes(b"changed")
        if mode == "replaced-same-bytes":
            replacement = tmp_path / "replacement.png"
            replacement.write_bytes(PAYLOAD)
            replacement.replace(produced)
        if mode == "symlink": produced.unlink(); produced.symlink_to(foreign)
        if mode == "false-size": return replace(raw, value={"size_bytes": len(PAYLOAD) + 1})
        if mode == "malformed": return replace(raw, artifacts=(replace(artifact, sha256="bad"),))
        if mode == "overflow": return replace(raw, artifacts=tuple(replace(artifact, artifact_id=f"shot.{i}") for i in range(65)))
        if mode == "raise": raise RuntimeError("PRIVATE-RESULT")
        return raw
    calls = _alter_result(context, transform)  # negative injection after real default producer
    result = _capture(server, context)
    _fail(result, code)
    assert calls == [("capture_screenshot", context.target, context.session)]
    assert set(context.evidence_ledger.root.iterdir()) == {foreign}
    assert foreign.read_bytes() == PAYLOAD
    assert context.evidence_ledger._records == context.evidence_ledger._active == {}
    assert boundary._current_evidence_scope() is None
    assert "PRIVATE-RESULT" not in json.dumps(result)


@pytest.mark.parametrize("kind", ["stale", "foreign", "lookalike", "wrong-operation", "path-lookalike"])
def test_c1_exact_receipt_scope_and_operation_remain_mandatory(tmp_path, kind):
    _, context = _factory(tmp_path / "current", "full_local")
    _, other = _factory(tmp_path / "foreign", "full_local")
    request = OperationRequest(OperationKind.DISPLAY, "capture_screenshot")
    target = context.runtime_target.binding
    provenance = admit_operation_provenance(operation=request.name, target=context.target.logical_id,
        session=context.session.session_id, binding=target.binding_ref, fingerprint=context.target.fingerprint,
        generation=7, evidence_policy="full_local")
    a = context.evidence_ledger.root / "a.png"; a.write_bytes(PAYLOAD)
    b = other.evidence_ledger.root / "b.png"; b.write_bytes(PAYLOAD)
    raw = OperationResult(request, OperationVerdict.SUCCESS, artifacts=(ArtifactReference("shot", "image/png", DIGEST),))
    with context.evidence_ledger.operation() as old:
        stale = old.record("shot", a)
    with other.evidence_ledger.operation() as foreign, context.evidence_ledger.operation(
        "read_active_window" if kind == "wrong-operation" else "capture_screenshot"
    ) as scope:
        receipt = scope.record("shot", a)
        if kind == "stale": receipt = stale
        if kind == "foreign": receipt = foreign.record("shot", b)
        if kind == "lookalike":
            class Lookalike(EvidenceReceipt): pass
            receipt = Lookalike(receipt.artifact_id, receipt.path, receipt._ledger, receipt._scope)
        callbacks = []
        if kind == "path-lookalike":
            class PathLookalike:
                def __eq__(self, other):
                    callbacks.append(other)
                    return True
            object.__setattr__(receipt, "path", PathLookalike())
        result = normalize_operation_result(context, request, raw, provenance, scope=scope, receipts=(receipt,))
        assert callbacks == []
        _fail(result.to_dict(), "invalid-evidence-receipt")
    assert a.read_bytes() == b.read_bytes() == PAYLOAD


@pytest.mark.parametrize("same_ledger", [False, True])
@pytest.mark.parametrize("current_policy", ["sanitized", "full_local"])
@pytest.mark.parametrize("fail_current", [False, True])
def test_c3_overlapping_production_preserves_paused_sibling(tmp_path, monkeypatch, same_ledger, current_policy, fail_current):
    server, context = _factory(tmp_path / "current", current_policy)
    sibling_server, sibling_context = (server, context) if same_ledger else _factory(
        tmp_path / "sibling", "full_local" if current_policy == "sanitized" else "sanitized", remote=True)
    ready, release = threading.Event(), threading.Event()
    destinations = {}
    class ConcurrentBackend(Backend):
        def capture_screenshot(self, display, out_path, *, window=None):
            destinations[window] = (current_application := mcp_server.current_application_context(), out_path, display)
            assert current_application in (context, sibling_context)
            return super().capture_screenshot(display, out_path, window=window)
    backend = ConcurrentBackend()
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    def pause_or_fail(raw, request):
        scope = boundary._current_evidence_scope()
        assert scope._ledger._records[(scope._token, raw.artifacts[0].artifact_id)].sha256 == DIGEST
        if request.arguments.get("window") == "sibling":
            ready.set()
            assert release.wait(15)
        elif fail_current:
            raise RuntimeError("PRIVATE-CURRENT")
        return raw
    calls = _alter_result(context, pause_or_fail)
    sibling_calls = calls if same_ledger else _alter_result(sibling_context, pause_or_fail)
    sentinel = tmp_path / "foreign-sentinel"; sentinel.write_bytes(b"unrelated")
    with ThreadPoolExecutor(max_workers=2) as pool:
        future = pool.submit(_capture, sibling_server, sibling_context, "mcp", "sibling")
        try:
            assert ready.wait(15)
            sibling_path = destinations["sibling"][1]
            before_bytes = sibling_path.read_bytes()
            before_records = dict(sibling_context.evidence_ledger._records)
            result = _capture(server, context, "mcp", "current")
            # Immediate comparison while sibling is still paused; no aggregate-after-both oracle.
            assert not future.done()
            assert sibling_path.read_bytes() == before_bytes == PAYLOAD
            assert sibling_context.evidence_ledger._records == before_records
            assert sentinel.read_bytes() == b"unrelated"
            current_path = destinations["current"][1]
            assert current_path != sibling_path
            assert destinations["current"] == (context, current_path, ":109")
            assert destinations["sibling"] == (sibling_context, sibling_path, ":109")
            if fail_current:
                _fail(result, "executor-failure")
                assert not current_path.exists()
            elif current_policy == "full_local":
                assert result["artifacts"][0]["path"] == str(current_path)
                assert current_path.read_bytes() == PAYLOAD
            else:
                assert result["verdict"] == "success" and "path" not in result["artifacts"][0]
                assert not current_path.exists()
            if not fail_current:
                assert result["artifacts"][0]["artifact_id"] == next(iter(before_records))[1]
                assert result["artifacts"][0]["sha256"] == DIGEST
        finally:
            release.set()
        sibling_result = future.result(timeout=15)
    assert sibling_result["verdict"] == "success"
    assert sibling_path.exists() is (sibling_context.evidence_ledger.policy == "full_local")
    assert len(backend.destinations) == 2
    assert calls == ([("capture_screenshot", context.target, context.session)] * 2 if same_ledger
                     else [("capture_screenshot", context.target, context.session)])
    if not same_ledger:
        assert sibling_calls == [("capture_screenshot", sibling_context.target, sibling_context.session)]
    assert context.evidence_ledger._records == sibling_context.evidence_ledger._records == {}
    assert context.evidence_ledger._active == sibling_context.evidence_ledger._active == {}
    assert boundary._current_evidence_scope() is None


@pytest.mark.parametrize("fail", [False, True])
def test_c3_original_callback_restores_parent_scope_on_success_and_failure(tmp_path, monkeypatch, fail):
    server, context = _factory(tmp_path, "sanitized")
    backend = Backend(fail=fail)
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    tool = _tool(server)
    with context.evidence_ledger.operation() as parent:
        result = tool.fn(window=None)  # same task/context; FastMCP task isolation cannot hide a missing reset
        assert boundary._current_evidence_scope() is parent
        assert list(context.evidence_ledger._active.values()) == [parent]
        assert context.evidence_ledger._records == {}
    assert result["verdict"] == ("failure" if fail else "success")
    assert boundary._current_evidence_scope() is None


def test_c3_cleanup_failure_restores_context_and_preserves_foreign_record(tmp_path, monkeypatch):
    server, context = _factory(tmp_path, "sanitized")
    backend = Backend()
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    foreign = context.evidence_ledger.root / "foreign.png"
    foreign.write_bytes(PAYLOAD)
    original_unlink = Path.unlink
    def denied(path, *args, **kwargs):
        if path in backend.destinations:
            raise PermissionError("PRIVATE-CLEANUP")
        return original_unlink(path, *args, **kwargs)
    with context.evidence_ledger.operation() as parent:
        parent.record("foreign", foreign)
        before = dict(context.evidence_ledger._records)
        with monkeypatch.context() as patch:
            patch.setattr(Path, "unlink", denied)
            result = _tool(server).fn(window=None)
        _fail(result, "invalid-executor-result")
        assert boundary._current_evidence_scope() is parent
        assert context.evidence_ledger._records == before
        assert list(context.evidence_ledger._active.values()) == [parent]
        assert foreign.read_bytes() == PAYLOAD
    assert backend.destinations[0].read_bytes() == PAYLOAD
    assert "PRIVATE-CLEANUP" not in json.dumps(result)
    backend.destinations[0].unlink()  # owned fixture cleanup after the injected failure
    assert context.evidence_ledger._records == context.evidence_ledger._active == {}


@pytest.mark.parametrize("remote", [False, True])
def test_c2_unbound_default_and_direct_screenshot_remain_readable(tmp_path, monkeypatch, remote):
    from qa_mcp.config import Settings
    backend = Backend()
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    server = mcp_server.create_mcp_server(settings=Settings(
        remote_client=remote, host_agent="http://bridge.example.invalid" if remote else "",
        manager_templates="manager.json", value_read_templates="value.json",
    ))
    context = mcp_server.application_context(server)
    assert type(context.executor) is (WindowsHostQAExecutor if remote else LocalQAExecutor)
    direct_path, registered_path = tmp_path / "direct.png", tmp_path / "registered.png"
    with activate_application_context(context):
        direct = mcp_server.capture_screenshot(display=":109", window=None, out_path=str(direct_path))
    registered = json.loads(asyncio.run(_tool(server).run(
        {"display": ":109", "window": None, "out_path": str(registered_path)}
    )).content[0].text)
    assert direct["path"] == str(direct_path)
    assert registered["path"] == str(registered_path)
    assert direct_path.read_bytes() == registered_path.read_bytes() == PAYLOAD
    assert backend.destinations == [direct_path, registered_path]
    assert context.evidence_ledger._records == context.evidence_ledger._active == {}
