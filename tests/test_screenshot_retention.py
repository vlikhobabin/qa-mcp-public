"""Screenshot retention policy partition at the registered factory boundary."""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path

import pytest

from qa_mcp import mcp_server
from qa_mcp.core import SessionIdentity, activate_application_context
from tests.test_target_bound_evidence_cleanup import _context


PAYLOAD = b"synthetic-screenshot-png"


class Backend:
    def __init__(self, *, write: bool = True, fail: bool = False) -> None:
        self.write = write
        self.fail = fail
        self.destinations: list[Path] = []

    def capture_screenshot(self, display, out_path, *, window=None):
        del display
        self.destinations.append(Path(out_path))
        if self.fail:
            raise mcp_server.client_display.DisplayBackendError(
                "host-agent-screenshot-error", "backend-secret",
            )
        if self.write:
            Path(out_path).write_bytes(PAYLOAD)
        return {
            "path": str(out_path) if self.write else None,
            "size_bytes": len(PAYLOAD) if self.write else 0,
            "window": window,
            "display": ":99",
            "matched_window_id": None,
            "tool": "fake",
        }


def _tool(server):
    return {item.name: item for item in asyncio.run(server.list_tools())}["capture_screenshot"]


@pytest.mark.parametrize("out_path", [None, "relative-shot.png", "{absolute}"])
def test_unbound_factory_retains_default_relative_absolute_and_direct_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, out_path: str | None,
) -> None:
    backend = Backend()
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    server = mcp_server.create_mcp_server()
    requested = None if out_path is None else (
        str(tmp_path / "absolute-shot.png") if out_path == "{absolute}" else out_path
    )
    args = {"display": ":99", "window": None}
    if requested is not None:
        args["out_path"] = requested

    with activate_application_context(mcp_server.application_context(server)):
        direct = mcp_server.capture_screenshot(**args)
    assert Path(direct["path"]).is_file()
    assert Path(direct["path"]).read_bytes() == PAYLOAD

    result = json.loads(asyncio.run(_tool(server).run(args)).content[0].text)
    # Unbound registered tools preserve the historical direct-call DTO rather
    # than wrapping it in the bound OperationResult envelope.
    assert Path(result["path"]).is_file()
    assert Path(result["path"]).read_bytes() == PAYLOAD
    # Relative legacy output resolves under the repository root; clean the
    # test-owned file so evidence fingerprinting observes no workspace drift.
    if requested is not None and not Path(requested).is_absolute():
        Path(result["path"]).unlink(missing_ok=True)


@pytest.mark.parametrize("evidence_policy", ["sanitized", "full_local"])
def test_bound_policy_controls_cleanup_and_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, evidence_policy: str,
) -> None:
    backend = Backend()
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    server, context = _context(tmp_path, evidence_policy=evidence_policy)
    context.session = SessionIdentity("session-7", context.target, 7)
    context.attachment = mcp_server._AttachedTestClientContext(
        "127.0.0.1", 15444, 1.0, {}, target=context.target,
        session=context.session, binding_generation=7,
        ownership_class="owned", lifecycle_id="local-7", display=":109",
    )
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_bytes(b"untouched")
    before = sentinel.read_bytes()

    payload = json.loads(asyncio.run(_tool(server).run({"window": None})).content[0].text)
    assert payload["verdict"] == "success"
    artifact = payload["artifacts"][0]
    assert artifact["sha256"] == "sha256:" + hashlib.sha256(PAYLOAD).hexdigest()
    assert sentinel.read_bytes() == before
    evidence = list(context.runtime_target.binding.evidence_root.glob("*.png"))
    if evidence_policy == "sanitized":
        assert "path" not in artifact and evidence == []
    else:
        assert len(evidence) == 1 and evidence[0].read_bytes() == PAYLOAD
        assert artifact["path"] == str(evidence[0])
        assert "PRIVATE" not in json.dumps(payload)


@pytest.mark.parametrize("mode", ["backend", "missing"])
def test_bound_capture_failure_is_truthful_and_preserves_unrelated_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str,
) -> None:
    backend = Backend(write=mode != "missing", fail=mode == "backend")
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    server, context = _context(tmp_path, evidence_policy="sanitized")
    context.session = SessionIdentity("session-7", context.target, 7)
    context.attachment = mcp_server._AttachedTestClientContext(
        "127.0.0.1", 15444, 1.0, {}, target=context.target,
        session=context.session, binding_generation=7,
        ownership_class="owned", lifecycle_id="local-7", display=":109",
    )
    sentinel = tmp_path / "unrelated.bin"
    sentinel.write_bytes(b"before-failure")
    before = sentinel.read_bytes()
    if mode == "backend":
        with pytest.raises(mcp_server.client_display.DisplayBackendError) as error:
            backend.capture_screenshot(":109", tmp_path / "backend-precheck.png")
        assert error.value.code == "host-agent-screenshot-error"
        assert error.value.detail == "backend-secret"
        backend.destinations.clear()
    payload = json.loads(asyncio.run(_tool(server).run({"window": None})).content[0].text)
    assert payload["verdict"] == "failure"
    assert "artifacts" not in payload
    assert sentinel.read_bytes() == before
    assert "backend-secret" not in json.dumps(payload)


def test_bound_sanitized_cleanup_failure_is_not_reported_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    backend = Backend()
    monkeypatch.setattr(mcp_server, "_display_backend", lambda: backend)
    server, context = _context(tmp_path, evidence_policy="sanitized")
    context.session = SessionIdentity("session-7", context.target, 7)
    context.attachment = mcp_server._AttachedTestClientContext(
        "127.0.0.1", 15444, 1.0, {}, target=context.target,
        session=context.session, binding_generation=7,
        ownership_class="owned", lifecycle_id="local-7", display=":109",
    )
    sentinel = tmp_path / "sentinel.bin"
    sentinel.write_bytes(b"before-cleanup")
    original_unlink = Path.unlink

    def reject(path: Path, *args, **kwargs):
        if path in backend.destinations:
            raise OSError("cleanup-secret")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", reject)
    payload = json.loads(asyncio.run(_tool(server).run({"window": None})).content[0].text)
    assert payload["verdict"] == "failure"
    assert "artifacts" not in payload
    assert sentinel.read_bytes() == b"before-cleanup"
    assert "cleanup-secret" not in json.dumps(payload)
