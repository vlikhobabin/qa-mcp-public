#!/usr/bin/env python3
"""Card 97 #1 — live-verify multi-select (select all rows) capture-free, by screenshot.

Two shots on a fresh native /TESTCLIENT:
  1. FULL-STREAM replay of the connect+open+select-all+refresh capture (one connection) → the genuine
     "select all" Table command runs AND PF_REFRESH_SELECTION materializes PF_SELECTED_ROWS, so the shot shows
     PF_SELECTED_ROWS=PF_SEL[3]=PF_ROW_001,PF_ROW_002,PF_ROW_003 (textual read-back proof + all rows highlighted).
  2. The productized select_all_table_rows (replay setup + the select-all Table command only) → all rows
     highlighted (proves the shipped tool fires the select-all invoke).

    .venv/bin/python tools/protocol-research/multiselect_verify_shot.py
"""
from __future__ import annotations

import socket
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import capture_screenshot, launch_test_client, select_all_table_rows, stop_test_client  # noqa: E402
from qa_mcp.protocol.native_write import (  # noqa: E402
    CLIENT_TO_MANAGER, MANAGER_TO_CLIENT, GuidRebinder, _read_available, _read_chunks, _set_seq, _seq_of,
)
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card97-multiselect-capture-20260619/traffic-selfcontained"


def full_replay(capture_dir: Path, *, host: str = "127.0.0.1", port: int = 15381,
                read_timeout_sec: float = 0.6, idle_timeout_sec: float = 0.15) -> int:
    """Replay the WHOLE manager stream (form-open + select-all + refresh) with live GUID rebind + seq bump."""
    mgr = _read_chunks(capture_dir, MANAGER_TO_CLIENT)
    cli = _read_chunks(capture_dir, CLIENT_TO_MANAGER)
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    with socket.create_connection((host, port), timeout=10.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, read_timeout_sec, idle_timeout_sec))
        last = 0
        for i, payload in enumerate(mgr):
            wire = rebinder.apply(payload)
            seq = _seq_of(wire)
            if seq:
                last = max(last, seq)
            else:
                wire = _set_seq(wire, last + 1); last += 1
            sock.sendall(wire)
            rebinder.observe_response(_read_available(sock, read_timeout_sec, idle_timeout_sec))
    return len(mgr)


def main() -> int:
    out = REPO / "runtime/protocol-research/multiselect-shot" / timestamp_name()
    out.mkdir(parents=True, exist_ok=True)
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, disp = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={disp} listening={r.get('listening')}")
    try:
        n = full_replay(CAP)
        time.sleep(1.5)
        a = capture_screenshot(disp, out_path=str(out / "fullreplay_select_all_refresh.png"))
        print(f"full-replay {n} frames -> fullreplay_select_all_refresh.png ({a.get('size_bytes')}B)")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
        time.sleep(1.0)

    # Shot 2: the productized tool alone (fresh client, baseline) — highlighted rows
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, disp = r["pid"], r.get("xvfb_pid"), r["display"]
    try:
        res = select_all_table_rows(port=15381)
        print("select_all_table_rows:", res)
        time.sleep(1.5)
        a = capture_screenshot(disp, out_path=str(out / "tool_select_all.png"))
        print(f"tool shot -> tool_select_all.png ({a.get('size_bytes')}B)")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print("out=", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
