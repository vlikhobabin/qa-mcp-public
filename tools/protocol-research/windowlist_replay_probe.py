#!/usr/bin/env python3
"""Card 98 #2 (remainder) — attempt to REPLAY the genuine get_window_list_testclient query on a live session
and parse the window list. Opens the fixture form (so windows exist), then sends the captured window-list query
frames (raw, then with seq bumped) via run_action, decoding the response with extract_testclient_windows.

    .venv/bin/python tools/protocol-research/windowlist_replay_probe.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.frames import MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_write import _read_chunks, _seq_of, _set_seq  # noqa: E402
from qa_mcp.protocol.responses import extract_testclient_windows  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

WL_CAP = REPO / "runtime/protocol-research/captures/genuine-card98-windowlist-20260620"
OPEN_FRAMES = list(range(11, 18))


def main() -> int:
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} listening={r.get('listening')}")
    repo = srv._repo_root()
    qmgr = _read_chunks(WL_CAP, MANAGER_TO_CLIENT)   # [4B control, 101B q1, 105B q2]
    print(f"window-list query frames: {[len(c) for c in qmgr]}")
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo))
    templates = ProtocolTemplates.load((repo / srv.VALUE_READ_TEMPLATES).resolve())
    synth = synthesize_bootstrap()
    out = repo / "runtime/protocol-research/native-mcp" / timestamp_name()
    try:
        with TestClientSession(host="127.0.0.1", port=15381) as s:
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            h.run_segment(OPEN_FRAMES, query_id="form-element-details")
            print("fixture form opened; sending window-list query...")
            for variant in ("raw", "seq-bumped"):
                before = len(h.state.received_stream)
                for q in qmgr[1:]:                 # the two command frames (skip the 4B control)
                    payload = q
                    if variant == "seq-bumped":
                        payload = _set_seq(q, _seq_of(bytes(h.state.sent_stream[-200:])) + 1)
                    res = h.run_action(payload, query_id=f"window-list-{variant}")
                blob = bytes(h.state.received_stream[before:])
                wins = extract_testclient_windows(blob)
                print(f"\n[{variant}] resp_bytes={len(blob)} windows={len(wins)}")
                for w in wins:
                    print(f"    {w['kind']:16} {w['caption']!r}")
                if wins:
                    print(f"  >>> {variant} SUCCESS")
                    break
                # diagnostics: what IS in the response?
                import re
                ascii_paths = re.findall(rb"(?:SecondaryFrame|MainFrame|HomePage)\[[0-9a-f-]{36}\]", blob)
                print(f"  ascii frame-paths: {len(ascii_paths)} {[p.decode() for p in ascii_paths[:6]]}")
                u16 = [m.decode("utf-16-le", "replace") for m in re.findall(rb"(?:[\x20-\x7e\x00][\x00\x04]){4,}", blob)]
                print(f"  utf16 strings: {u16[:12]}")
                print(f"  head hex: {blob[:48].hex(' ')}")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
