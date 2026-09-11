"""Card 98 #2 (remainder) — TestClient window-list response parser (extract_testclient_windows). Tests the
record structure on a synthetic blob (always) + the genuine manager capture when present (lab-local)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.protocol.responses import extract_testclient_windows  # noqa: E402
from qa_mcp.protocol.native_write import (  # noqa: E402
    WINDOW_LIST_HEADER_MARKER,
    WINDOW_LIST_QUERY_BODIES,
    splice_window_list_queries,
)


def _record(kind: str, guid: str, caption: str) -> bytes:
    """Build one on-wire window record: ``<Kind>[<guid>] 82 <marker> <len> <caption>`` (fa=ASCII, f7=UTF-16)."""
    path = f"{kind}[{guid}]".encode("latin1")
    try:
        ascii_cap = caption.encode("latin1")
        block = b"\x82\xfa" + bytes([len(ascii_cap)]) + ascii_cap
    except UnicodeEncodeError:
        u16 = caption.encode("utf-16-le")
        block = b"\x82\xf7" + bytes([len(u16) // 2]) + u16
    return path + block + b"\xfa\x0eSecondaryFrame\x81\xe1"  # + trailing type/nav noise


G1 = "177ba36f-a529-4994-b1bb-98466dd69d59"
G2 = "2a0c5124-a2d1-492d-ad91-4ed02ea1798a"
G3 = "6ca75e50-62a3-4842-b6cd-b429f7591ef2"


def test_extract_windows_synthetic() -> None:
    blob = (
        b"\x42\x8f\x60\xa0HEAD"
        + _record("SecondaryFrame", G1, "Товары")                      # UTF-16 caption (f7)
        + _record("SecondaryFrame", G2, "QA MCP Protocol Fixture V1")  # ASCII caption (fa)
        + _record("MainFrame", G3, "Демонстрационное приложение")
        + _record("HomePage", G3, "Начальная страница")
        + b"\x20\xa1\xa3TAIL"
    )
    wins = extract_testclient_windows(blob)
    assert [w["caption"] for w in wins] == [
        "Товары", "QA MCP Protocol Fixture V1", "Демонстрационное приложение", "Начальная страница",
    ]
    assert [w["kind"] for w in wins] == ["SecondaryFrame", "SecondaryFrame", "MainFrame", "HomePage"]
    assert wins[0]["guid"] == G1


def test_extract_windows_dedupes_segmented_record() -> None:
    # the same record can arrive twice across TCP segments — dedup by (kind, guid)
    rec = _record("SecondaryFrame", G1, "Товары")
    wins = extract_testclient_windows(b"HEAD" + rec + rec)
    assert len(wins) == 1 and wins[0]["caption"] == "Товары"


def test_extract_windows_empty() -> None:
    assert extract_testclient_windows(b"no windows here") == []


# --- the splice replay (graft the window-list command body onto a live value-read header) ---

def test_splice_window_list_queries() -> None:
    # a rendered value-read frame: <live header … cb 23 95> <value-read body> <tail>
    rendered = b"HDR" + bytes(30) + b"\xcb\x53\x81\xa3" + WINDOW_LIST_HEADER_MARKER + b"VALUEREAD" + b"\x66\x53\xb2\xa6"
    queries = splice_window_list_queries(rendered)
    assert len(queries) == 2
    header = rendered[: rendered.rfind(WINDOW_LIST_HEADER_MARKER) + len(WINDOW_LIST_HEADER_MARKER)]
    for q, body in zip(queries, WINDOW_LIST_QUERY_BODIES):
        assert q == header + body                       # header (live GUIDs) + the session-independent command body
        assert q.endswith(b"\x66\x53\xb2\xa6")          # frame tail marker preserved
    # the 2nd query carries the comprehensive-list opcode (e1 82 81 83 …)
    assert b"\x81\x88\x81\x81\xe1\x82\x81\x83" in queries[1]


def test_splice_requires_header_marker() -> None:
    with pytest.raises(ValueError):
        splice_window_list_queries(b"no marker here at all")


# --- grounded on the genuine manager capture when present (lab-local, gitignored) ---
_CAP = REPO_ROOT / "runtime/protocol-research/captures/genuine-card98-windowlist-20260620"


@pytest.mark.skipif(not (_CAP / "traffic.jsonl").exists(), reason="genuine window-list capture not present")
def test_extract_windows_on_genuine_capture() -> None:
    from qa_mcp.protocol.frames import CLIENT_TO_MANAGER
    from qa_mcp.protocol.native_write import _read_chunks

    blob = b"".join(_read_chunks(_CAP, CLIENT_TO_MANAGER))
    wins = extract_testclient_windows(blob)
    # matches the Vanessa get_window_list_testclient oracle: 4 windows
    assert [w["caption"] for w in wins] == [
        "Товары", "QA MCP Protocol Fixture V1", "Демонстрационное приложение", "Начальная страница",
    ]
