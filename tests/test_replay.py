from __future__ import annotations

from qa_mcp.protocol.bootstrap_synth import SYNTH_TEMPLATE_VERSION
from qa_mcp.protocol.replay import ReplaySession


class _Rebinder:
    def __init__(self) -> None:
        self.seen: bytes | None = None

    def apply(self, frame: bytes) -> bytes:
        self.seen = frame
        return frame


def test_replay_session_stamps_live_platform_version(monkeypatch):
    monkeypatch.setenv("QA_MCP_PLATFORM_VERSION", "8.5.1.1343")
    session = ReplaySession([], [])
    rebinder = _Rebinder()
    session.rebinder = rebinder

    frame = b"prefix " + SYNTH_TEMPLATE_VERSION.encode("ascii") + b" suffix"
    out = session.apply(frame)

    assert b"8.5.1.1343" in out
    assert SYNTH_TEMPLATE_VERSION.encode("ascii") not in out
    assert rebinder.seen == out


def test_replay_session_leaves_default_platform_unchanged(monkeypatch):
    monkeypatch.setenv("QA_MCP_PLATFORM_VERSION", SYNTH_TEMPLATE_VERSION)
    session = ReplaySession([], [])
    session.rebinder = _Rebinder()

    frame = b"prefix " + SYNTH_TEMPLATE_VERSION.encode("ascii") + b" suffix"

    assert session.apply(frame) == frame
