#!/usr/bin/env python3
"""Card 98 #2 (remainder) — REPLAY get_window_list_testclient by SPLICING the command body onto a live header.
The value-read frame (218) and the window-list query share the header `…cb 53 81 a3 cb 23 95` then a command
body. So: render 218 live (engine rebinds the session GUIDs), keep its header up to `cb 23 95`, graft the
window-list command body (from the genuine query) after it → a frame with LIVE session + the window-list
command. Send it, parse with extract_testclient_windows.

    .venv/bin/python tools/protocol-research/windowlist_splice_probe.py
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
from qa_mcp.protocol.native_write import _read_chunks  # noqa: E402
from qa_mcp.protocol.responses import extract_testclient_windows  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

WL_CAP = REPO / "runtime/protocol-research/captures/genuine-card98-windowlist-20260620"
OPEN_FRAMES = list(range(11, 18))
SPLIT = b"\xcb\x23\x95"


def main() -> int:
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} listening={r.get('listening')}")
    repo = srv._repo_root()
    qmgr = _read_chunks(WL_CAP, MANAGER_TO_CLIENT)            # [4B control, 101B q1, 105B q2]
    wl_bodies = []
    for q in qmgr[1:]:
        i = q.rfind(SPLIT)
        wl_bodies.append(q[i + len(SPLIT):])                 # the command body after cb 23 95 (incl. tail)
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo))
    templates = ProtocolTemplates.load((repo / srv.VALUE_READ_TEMPLATES).resolve())
    synth = synthesize_bootstrap()
    out = repo / "runtime/protocol-research/native-mcp" / timestamp_name()
    try:
        with TestClientSession(host="127.0.0.1", port=15381) as s:
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            h.run_segment(OPEN_FRAMES, query_id="form-element-details")
            # render a value-read frame (218-221) live to obtain a header carrying the LIVE session GUIDs
            sent0 = len(h.state.sent_stream)
            h.run_segment([218], query_id="form-value-read")
            rendered = bytes(h.state.sent_stream[sent0:])
            j = rendered.rfind(SPLIT)
            header = rendered[: j + len(SPLIT)]               # live header up to cb 23 95
            print(f"rendered-218 {len(rendered)}B; header {len(header)}B; wl bodies {[len(b) for b in wl_bodies]}")
            for n, body in enumerate(wl_bodies, 1):
                spliced = header + body
                before = len(h.state.received_stream)
                res = h.run_action(spliced, query_id=f"window-list-splice{n}")
                blob = bytes(h.state.received_stream[before:])
                wins = extract_testclient_windows(blob)
                print(f"\n[splice q{n}] sent={len(spliced)}B resp={len(blob)}B windows={len(wins)}")
                for w in wins:
                    print(f"    {w['kind']:16} {w['caption']!r}")
                if not wins and blob:
                    import re
                    u16 = [m.decode("utf-16-le", "replace") for m in re.findall(rb"(?:[\x20-\x7e\x00][\x00\x04]){4,}", blob)]
                    print(f"    (no windows) utf16: {u16[:8]}")
                if wins:
                    print(f"  >>> splice q{n} SUCCESS")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
