#!/usr/bin/env python3
"""Card 101 — CROSS-CONFIG proof of the fixture-free foreground. Boot a thick TestClient against demo БСП
(/opt/1c-dev/demo_1_0_41_3 — a real 1C:БСП base with NO suite fixture) and replay `_foreground_form_by_link`
(the genuine cold catalog-list-open sequence, nav-link retargeted) against a DEMO form. If the demo form comes to
the FOREGROUND with no fixture, the fixture-free foreground primer is config-agnostic.

    .venv/bin/python tools/protocol-research/demo_fixturefree_foreground_probe.py [nav_link]
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402

IB = "/opt/1c-dev/demo_1_0_41_3"
PORT = 15382
LINK = sys.argv[1] if len(sys.argv) > 1 else "e1cib/list/Справочник.Валюты"
OUT = REPO / "runtime" / "protocol-research" / "screenshots" / "demofg"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    r = srv.launch_test_client(infobase_path=IB, port=PORT, user="Администратор", kind="thick",
                               display="auto", manage_apache=False, wait_sec=150.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched demo БСП pid={pid} display={display} port={PORT} link={LINK}")
    wm = subprocess.Popen(["matchbox-window-manager", "-use_titlebar", "no"],
                          env={**os.environ, "DISPLAY": display}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.5)

    def shot(name):
        srv.capture_screenshot(display, out_path=str(OUT / f"{name}.png")); print(f"  shot {name}")

    try:
        shot("10_desktop")
        sock = srv._foreground_form_by_link(LINK, host="127.0.0.1", port=PORT)
        print(f"foreground replay -> {'socket held' if sock is not None else 'DIVERGED'}")
        if sock is not None:
            try:
                time.sleep(2.5)
                shot("20_foreground")
            finally:
                sock.close()
        shot("30_after_close")
    finally:
        wm.terminate()
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=False)
    print(f"\nscreenshots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
