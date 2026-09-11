#!/usr/bin/env python3
"""Card 101 Change 2 — DECISIVE fixture-free foreground test. `genuine-card98-listform-read` opens a REAL catalog
list (Товары) directly from COLD with NO fixture (no PF_, no e1cib/app): navigate → activate (e0 4b 55) → render
(e1 82, list SF) → 88 82 81 window-commands → activate. If a faithful full-sequence replay FOREGROUNDS the list,
then this IS a config-agnostic foreground mechanism already captured — retarget its nav-link to open any form
foreground (the fixture-free primer). Replay the whole manager stream (GuidRebinder) + screenshot.

    .venv/bin/python tools/protocol-research/listform_foreground_probe.py
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import _read_chunks  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card98-listform-read"
OUT = REPO / "runtime" / "protocol-research" / "screenshots" / "listfg"
RT, IT = 6.0, 1.5


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=180.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={display}")
    wm = subprocess.Popen(["matchbox-window-manager", "-use_titlebar", "no"],
                          env={**os.environ, "DISPLAY": display}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.0)

    def shot(name):
        srv.capture_screenshot(display, out_path=str(OUT / f"{name}.png")); print(f"  shot {name}")

    mgr = _read_chunks(CAP, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAP, CLIENT_TO_MANAGER)
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    print(f"capture: {len(mgr)} mgr frames")
    try:
        shot("10_desktop")
        with socket.create_connection(("127.0.0.1", 15381), timeout=10.0) as sock:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            rebinder.observe_response(_read_available(sock, RT, IT))
            for i in range(len(mgr)):
                wire = rebinder.apply(mgr[i])
                sock.sendall(wire)
                resp = _read_available(sock, RT, IT)
                rebinder.observe_response(resp)
                if i in (12, 15, 19, 20):           # after navigate / render / window-cmds / final activate
                    time.sleep(1.5); shot(f"20_after_mgr{i}")
            time.sleep(2.0); shot("30_final")
    finally:
        wm.terminate()
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print(f"\nscreenshots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
