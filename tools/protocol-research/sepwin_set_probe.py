#!/usr/bin/env python3
"""Card 101 Change 1 — set «Режим открытия форм» = «В отдельных окнах» (per-user IB setting, persists) by driving
the menu: main menu (top-right) → «Настройки» → «Параметры» → click the «В отдельных окнах» radio → «ОК». Each item
is located on screen with locate_text (dogfoods the card-100 helper). Then VERIFY: navigate to Документ.Заказ (NO
fixture primer) and check whether it now opens as a SEPARATE OS WINDOW (xdotool) that can be raised — which would
make Blocker 1 solvable config-agnostically by OS window activation, no protocol decode.

    .venv/bin/python tools/protocol-research/sepwin_set_probe.py
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
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.navigation import e1cib_data_link  # noqa: E402
from qa_mcp.protocol.native_xtest import locate_text, xtest_click  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

ORDER_REF = "0faf2b04-fc04-11e1-bbef-0050ba5c8877"
LINK = e1cib_data_link("Документ.Заказ", ORDER_REF)
OUT = REPO / "runtime" / "protocol-research" / "screenshots" / "sepwin"
MAIN_MENU = (1163, 15)
NASTROIKI = (996, 264)   # «Настройки» submenu in the top-right menu (from recon 01_topright_menu)


def xdo(display, *a):
    return subprocess.run(["xdotool", *a], env={**os.environ, "DISPLAY": display},
                          capture_output=True, text=True).stdout.strip()


def os_windows(display):
    rows = []
    for wid in xdo(display, "search", "--onlyvisible", "--name", "").splitlines():
        wid = wid.strip()
        if wid:
            rows.append((wid, xdo(display, "getwindowname", wid),
                         xdo(display, "getwindowgeometry", wid).replace("\n", " ")))
    return rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={display}")
    wm = subprocess.Popen(["matchbox-window-manager", "-use_titlebar", "no"],
                          env={**os.environ, "DISPLAY": display}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.5)

    def shot(name):
        p = str(OUT / f"{name}.png"); srv.capture_screenshot(display, out_path=p); print(f"  shot {name}"); return p

    def find(shot_png, text, sizes=(13, 12, 14, 11)):
        for sz in sizes:
            xy = locate_text(shot_png, text, pointsize=sz)
            if xy:
                print(f"  locate_text({text!r}, sz={sz}) -> {xy}")
                return xy
        print(f"  locate_text({text!r}) NOT FOUND")
        return None

    try:
        # --- SET the mode via the menu ---
        xtest_click(display, *MAIN_MENU); time.sleep(1.2); shot("10_menu")
        xtest_click(display, *NASTROIKI); time.sleep(1.2); s = shot("11_nastroiki")
        p = find(s, "Параметры")
        if p:
            xtest_click(display, *p); time.sleep(1.5)
        s = shot("12_parametry_dialog")
        radio = find(s, "отдельных") or find(s, "отдельных окнах")
        if radio:
            xtest_click(display, *radio); time.sleep(0.8); s = shot("13_radio_selected")
        ok = find(s, "ОК") or find(s, "OK")
        if ok:
            xtest_click(display, *ok); time.sleep(1.5)
        shot("14_after_ok")

        # --- VERIFY: navigate to a doc (NO primer) and check for a separate OS window ---
        repo = srv._repo_root()
        bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo))
        templates = ProtocolTemplates.load((repo / srv.VALUE_READ_TEMPLATES).resolve())
        synth = synthesize_bootstrap()
        out = repo / "runtime/protocol-research/native-mcp" / timestamp_name()
        print("OS windows BEFORE navigate:")
        for w in os_windows(display):
            print("   ", w)
        with TestClientSession(host="127.0.0.1", port=15381) as sess:
            h = sess.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            time.sleep(1.0)
            print(f"navigate (no primer) -> {srv._open_form_by_link(h, LINK)}")
            time.sleep(2.5)
            shot("20_doc_navigated_nopRimer")
            print("OS windows AFTER navigate:")
            for w in os_windows(display):
                print("   ", w)
    finally:
        wm.terminate()
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print(f"\nscreenshots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
