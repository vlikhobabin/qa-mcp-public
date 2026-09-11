"""Card 62: synthesized bootstrap frames 1..3 reproduce captured frames byte-for-byte.

Offline proof that frames 1..3 are fully described by the in-repo static template plus two
dynamic fields (the message-counter base and the frame-3 ticket GUID) — no captured bytes are
read at session time. The gold fixture is an INDEPENDENT session (not the template source), so
a match proves the model generalizes across sessions.
"""

from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.protocol.bootstrap_synth import SYNTH_TEMPLATE_VERSION, synthesize_bootstrap  # noqa: E402

FIXTURE = json.loads(
    (REPO_ROOT / "tests" / "fixtures" / "bootstrap_frames_1to3_independent.json").read_text(
        encoding="utf-8"
    )
)


def test_synth_reproduces_independent_session_frames() -> None:
    base = int(FIXTURE["counter_base"])
    guid = bytes.fromhex(FIXTURE["ticket_guid_hex"])
    syn = synthesize_bootstrap(counter_base=base, ticket_guid=guid)
    for idx in (1, 2, 3):
        expected = bytes.fromhex(FIXTURE["frames"][str(idx)])
        assert syn.frame(idx) == expected, f"frame {idx} mismatch for independent session"


def test_frame4_round_trips_for_independent_session() -> None:
    base = int(FIXTURE["counter_base"])
    ack_guid = FIXTURE["frame4_ack_guid"]
    syn = synthesize_bootstrap(counter_base=base, ticket_guid=b"\x00" * 16)
    # frame 4 is deterministic (ack_guid text + counter, no random nonce)
    assert syn.render_frame4(ack_guid) == bytes.fromhex(FIXTURE["frame4_hex"])
    assert syn.frame4_sequence == base + 3


def test_counter_base_must_be_five_digits() -> None:
    import pytest

    with pytest.raises(ValueError):
        synthesize_bootstrap(counter_base=999, ticket_guid=b"\x00" * 16)


def test_random_defaults_are_well_formed() -> None:
    syn = synthesize_bootstrap()
    assert 10000 <= syn.counter_base <= 99996
    assert len(syn.ticket_guid) == 16
    assert [len(syn.frame(i)) for i in (1, 2, 3)] == [548, 580, 612]
    # counter increments by 1 per frame at offset 43
    for idx in (1, 2, 3):
        digits = syn.frame(idx)[43:48].decode("ascii")
        assert int(digits) == syn.counter_base + (idx - 1)
    # frame-3 token carries the ticket GUID at decoded offset 66
    token_b64 = syn.frame(3)[333 : 333 + 112].decode("ascii")
    assert base64.b64decode(token_b64)[66:82] == syn.ticket_guid


def test_random_counter_base_leaves_room_for_frame4(monkeypatch) -> None:
    import qa_mcp.protocol.bootstrap_synth as synth_mod

    monkeypatch.setattr(synth_mod.secrets, "randbelow", lambda upper: upper - 1)

    syn = synthesize_bootstrap(ticket_guid=b"\x00" * 16, platform_version=SYNTH_TEMPLATE_VERSION)

    assert syn.counter_base == 99996
    assert syn.frame4_sequence == 99999
    syn.render_frame4("11111111-2222-3333-4444-555555555555")


def test_explicit_counter_base_can_still_fail_frame4_overflow() -> None:
    import pytest

    syn = synthesize_bootstrap(
        counter_base=99997,
        ticket_guid=b"\x00" * 16,
        platform_version=SYNTH_TEMPLATE_VERSION,
    )

    with pytest.raises(ValueError, match="frame4 counter 100000"):
        syn.render_frame4("11111111-2222-3333-4444-555555555555")


def test_two_sessions_differ_only_in_dynamic_fields() -> None:
    a = synthesize_bootstrap(counter_base=26847, ticket_guid=b"\x11" * 16)
    b = synthesize_bootstrap(counter_base=16076, ticket_guid=b"\x22" * 16)
    for idx in (1, 2):
        diffs = [j for j in range(len(a.frame(idx))) if a.frame(idx)[j] != b.frame(idx)[j]]
        # only the 5-digit counter (offset 43..47) may differ in frames 1 and 2
        assert all(43 <= j <= 47 for j in diffs), f"frame {idx} differs outside the counter: {diffs}"


# --- epic 112 P2/P3: version-aware synth (the ONLY change the 8.5 handshake needs) ---

from qa_mcp.protocol.bootstrap_synth import (  # noqa: E402
    resolve_synth_platform_version,
)


def _has(synth, ver: str) -> bool:
    return any(ver.encode("ascii") in synth.frame(i) for i in (1, 2, 3))


def test_default_synth_declares_template_version(monkeypatch) -> None:
    # clean env → resolution falls back to the default 8.3 root → no version change (byte-identical to before)
    monkeypatch.delenv("QA_MCP_PLATFORM_VERSION", raising=False)
    monkeypatch.delenv("PLATFORM_ROOT", raising=False)
    s = synthesize_bootstrap(counter_base=12345, ticket_guid=b"\x00" * 16)
    assert _has(s, SYNTH_TEMPLATE_VERSION) and not _has(s, "8.5.1.1343")


def test_explicit_8_5_version_is_injected() -> None:
    s = synthesize_bootstrap(counter_base=12345, ticket_guid=b"\x00" * 16, platform_version="8.5.1.1343")
    assert _has(s, "8.5.1.1343") and not _has(s, SYNTH_TEMPLATE_VERSION)
    # injecting a different-length version is length-safe (tail-marker framing, no length field):
    base = synthesize_bootstrap(counter_base=12345, ticket_guid=b"\x00" * 16, platform_version=SYNTH_TEMPLATE_VERSION)
    assert len(s.frame(1)) == len(base.frame(1)) - 1  # "8.3.27.2130" (11) → "8.5.1.1343" (10)


def test_resolve_synth_version_prefers_full_env_override(monkeypatch) -> None:
    monkeypatch.setenv("QA_MCP_PLATFORM_VERSION", "8.5.1.1343")
    assert resolve_synth_platform_version() == "8.5.1.1343"
    # a bare family ("8.5") is NOT a full version → falls back to PLATFORM_ROOT
    monkeypatch.setenv("QA_MCP_PLATFORM_VERSION", "8.5")
    monkeypatch.setenv("PLATFORM_ROOT", "/opt/1cv8/x86_64/8.5.1.1343")
    assert resolve_synth_platform_version() == "8.5.1.1343"


def test_resolve_synth_version_reads_project_target_env(monkeypatch, tmp_path) -> None:
    target = tmp_path / "qa-target.env"
    target.write_text(
        "QA_MCP_PLATFORM_VERSION=8.3.27.2214\n"
        "PLATFORM_ROOT=/opt/1cv8/x86_64/8.3.27.2214\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("QA_MCP_PLATFORM_VERSION", raising=False)
    monkeypatch.delenv("PLATFORM_ROOT", raising=False)
    monkeypatch.setenv("QA_MCP_TARGET_ENV_FILE", str(target))

    assert resolve_synth_platform_version() == "8.3.27.2214"
