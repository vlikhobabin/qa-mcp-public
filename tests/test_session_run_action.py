"""Card 78 Phase A: SessionHandle.run_action — send a captured action command frame on the
already-open synthesized session (offline plumbing tests with a fake socket session)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.protocol.session import SessionHandle, _ExchangeState  # noqa: E402


class _FakeSession:
    """Records sent payloads and returns a canned response from send_and_read."""

    def __init__(self, response: bytes) -> None:
        self.response = response
        self.sent: list[bytes] = []

    def send_and_read(self, payload: bytes) -> bytes:
        self.sent.append(payload)
        return self.response


class _Rebinder:
    """captured->live substitution (mimics GuidRebinder.apply)."""

    def __init__(self, mapping: dict[bytes, bytes]) -> None:
        self.mapping = mapping

    def apply(self, payload: bytes) -> bytes:
        out = payload
        for cap, live in self.mapping.items():
            out = out.replace(cap, live)
        return out


def _handle(session: _FakeSession, tmp_path: Path) -> SessionHandle:
    return SessionHandle(
        session=session,  # type: ignore[arg-type]
        bootstrap=None,  # type: ignore[arg-type]
        templates=None,  # type: ignore[arg-type]
        synthesized=None,
        state=_ExchangeState(),
        steps_dir=tmp_path,
    )


def test_run_action_sends_payload_and_records_response(tmp_path: Path) -> None:
    session = _FakeSession(response=b"\x01\x02\x03ok")
    handle = _handle(session, tmp_path)
    summary = handle.run_action(b"COMMAND-FRAME", query_id="click")
    assert session.sent == [b"COMMAND-FRAME"]
    assert summary["accepted"] is True
    assert summary["recv_bytes"] == 5
    assert summary["sent_bytes"] == len(b"COMMAND-FRAME")
    assert summary["adapted"] is False
    assert summary["query_id"] == "click"
    assert bytes(handle.state.sent_stream) == b"COMMAND-FRAME"
    assert bytes(handle.state.received_stream) == b"\x01\x02\x03ok"
    assert handle.state.events[-1]["event"] == "action"


def test_run_action_applies_rebinder(tmp_path: Path) -> None:
    session = _FakeSession(response=b"r")
    handle = _handle(session, tmp_path)
    rebinder = _Rebinder({b"CAP-GUID": b"LIVE-GUID"})
    summary = handle.run_action(b"head CAP-GUID tail", query_id="input", rebinder=rebinder)
    assert session.sent == [b"head LIVE-GUID tail"]
    assert summary["adapted"] is True


def test_run_action_no_response_marks_not_accepted(tmp_path: Path) -> None:
    session = _FakeSession(response=b"")
    handle = _handle(session, tmp_path)
    summary = handle.run_action(b"X", query_id="goto")
    assert summary["accepted"] is False
    assert summary["recv_bytes"] == 0
