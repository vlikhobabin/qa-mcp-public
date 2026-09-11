#!/usr/bin/env python3
"""Card 101 Change 1 (recon) — find the path to «Параметры» / «Режим открытия форм» so the form-open mode can be
set to «В отдельных окнах» (a per-user IB setting; persists once set). Boot a client, open the top-right main menu
(«Сервис и настройки») and the top-left ☰, screenshot each so the exact menu structure is visible.

    .venv/bin/python tools/protocol-research/sepwin_menu_recon_probe.py
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
from qa_mcp.protocol.native_xtest import xtest_click  # noqa: E402

OUT = REPO / "runtime" / "protocol-research" / "screenshots" / "sepwin"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={display}")
    wm = subprocess.Popen(["matchbox-window-manager", "-use_titlebar", "no"],
                          env={**os.environ, "DISPLAY": display}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.5)

    def shot(name: str) -> None:
        srv.capture_screenshot(display, out_path=str(OUT / f"{name}.png"))
        print(f"  shot {name}")

    try:
        shot("00_desktop")
        # top-right «Сервис и настройки» (the ☰/gear near the user name «Администратор»), ~x=1163 y=15
        xtest_click(display, 1163, 15); time.sleep(1.5); shot("01_topright_menu")
        # press Escape, then open the top-left main menu ☰ (~x=62 y=15)
        subprocess.run(["xdotool", "key", "Escape"], env={**os.environ, "DISPLAY": display}, check=False)
        time.sleep(0.8)
        xtest_click(display, 62, 15); time.sleep(1.5); shot("02_topleft_menu")
    finally:
        wm.terminate()
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print(f"\nscreenshots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
