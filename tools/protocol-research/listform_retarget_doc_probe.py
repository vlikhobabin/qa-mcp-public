#!/usr/bin/env python3
"""Card 101 Change 2 — does the fixture-less foreground sequence open the TARGET document foreground when its
nav-link is retargeted? `genuine-card98-listform-read` foregrounds a catalog list (proven, no fixture). Retarget
its navigate to (A) the Заказ document's LIST `e1cib/list/Документ.Заказ` and (B, separate run) the doc DATA-link.
Replay the full sequence + screenshot. If the target opens foreground with NO fixture → the fixture-free primer.

    .venv/bin/python tools/protocol-research/listform_retarget_doc_probe.py [list|data]
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
from qa_mcp.protocol.native_write import _read_chunks, retarget_list_read_frame  # noqa: E402
from qa_mcp.protocol.navigation import e1cib_data_link  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card98-listform-read"
OLD_NAV = "e1cib/list/Справочник.Товары"
ORDER_REF = "0faf2b04-fc04-11e1-bbef-0050ba5c8877"
OUT = REPO / "runtime" / "protocol-research" / "screenshots" / "listretarget"
RT, IT = 6.0, 1.5


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    new_nav = ("e1cib/list/Документ.Заказ" if mode == "list"
               else e1cib_data_link("Документ.Заказ", ORDER_REF))
    OUT.mkdir(parents=True, exist_ok=True)
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=180.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={display} mode={mode} new_nav={new_nav}")
    wm = subprocess.Popen(["matchbox-window-manager", "-use_titlebar", "no"],
                          env={**os.environ, "DISPLAY": display}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.0)

    def shot(name):
        srv.capture_screenshot(display, out_path=str(OUT / f"{mode}_{name}.png")); print(f"  shot {mode}_{name}")

    mgr = _read_chunks(CAP, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAP, CLIENT_TO_MANAGER)
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    try:
        shot("10_desktop")
        with socket.create_connection(("127.0.0.1", 15381), timeout=10.0) as sock:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            rebinder.observe_response(_read_available(sock, RT, IT))
            for i in range(len(mgr)):
                frame = retarget_list_read_frame(mgr[i], old_nav=OLD_NAV, new_nav=new_nav,
                                                 old_col_block=b"", new_col_block=b"")
                wire = rebinder.apply(frame)
                sock.sendall(wire)
                rebinder.observe_response(_read_available(sock, RT, IT))
                if i in (12, 15, 20):
                    time.sleep(1.5); shot(f"20_after_mgr{i}")
            time.sleep(2.0); shot("30_final")
    finally:
        wm.terminate()
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print(f"\nscreenshots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
