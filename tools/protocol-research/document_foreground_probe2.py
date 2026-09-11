#!/usr/bin/env python3
"""Card 100 Blocker 1 (exp2) — is the navigated Заказ form a SEPARATE OS window? If so, OS-level window activation
(xdotool, config-agnostic, the same OS layer card-96 keyboard / XTEST hybrid already use) foregrounds it without
decoding a protocol "show form" command. Open the form, enumerate OS windows (name+geometry+map state), try
raising each candidate, screenshot after each. Also tries replaying the descriptor RENDER to see if that paints it.

    .venv/bin/python tools/protocol-research/document_foreground_probe2.py
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
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

ORDER_REF = "0faf2b04-fc04-11e1-bbef-0050ba5c8877"
LINK = e1cib_data_link("Документ.Заказ", ORDER_REF)
OUT = REPO / "runtime" / "protocol-research" / "screenshots" / "docforeground2"


def xdo(display: str, *args: str) -> str:
    try:
        return subprocess.run(["xdotool", *args], env={**os.environ, "DISPLAY": display},
                              capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception as e:  # noqa: BLE001
        return f"<exc {e}>"


def list_windows(display: str) -> list[tuple[str, str, str, str]]:
    ids = xdo(display, "search", "--onlyvisible", "--name", "").splitlines()
    rows = []
    for wid in ids:
        wid = wid.strip()
        if not wid:
            continue
        name = xdo(display, "getwindowname", wid)
        geo = xdo(display, "getwindowgeometry", wid).replace("\n", " | ")
        rows.append((wid, name, geo, ""))
    return rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={display}")
    wm = subprocess.Popen(["matchbox-window-manager", "-use_titlebar", "no"],
                          env={**os.environ, "DISPLAY": display}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    repo = srv._repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo))
    templates = ProtocolTemplates.load((repo / srv.VALUE_READ_TEMPLATES).resolve())
    synth = synthesize_bootstrap()
    out = repo / "runtime/protocol-research/native-mcp" / timestamp_name()

    def shot(name: str) -> None:
        srv.capture_screenshot(display, out_path=str(OUT / f"{name}.png"))
        print(f"  shot {name}")

    try:
        print("== OS windows BEFORE open ==")
        for row in list_windows(display):
            print(f"  {row[0]}  name={row[1]!r}  geo={row[2]}")
        with TestClientSession(host="127.0.0.1", port=15381) as s:
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            time.sleep(1.0)
            resolved = srv._open_form_by_link(h, LINK)
            print(f"resolved: {resolved}")
            if not resolved:
                return 1
            caption, sf, mf = resolved
            time.sleep(2.5)
            shot("20_after_open")
            print("== OS windows AFTER open ==")
            wins = list_windows(display)
            for row in wins:
                print(f"  {row[0]}  name={row[1]!r}  geo={row[2]}")

            # Try raising EACH window (activate + raise), screenshot after each.
            for wid, name, geo, _ in wins:
                xdo(display, "windowactivate", wid)
                xdo(display, "windowraise", wid)
                time.sleep(1.2)
                shot(f"30_raise_{wid}_{name[:14].replace(' ','_').replace('/','_')}")

            # Also: replay the descriptor RENDER on the navigated form (does it paint it?).
            h.state.secondary_frame_guid = sf
            h.state.managed_form_guid = mf
            try:
                srv._live_descriptor_blob(h, (sf, mf))
            except Exception as e:  # noqa: BLE001
                print(f"descriptor render exc: {e}")
            time.sleep(2.0)
            shot("40_after_descriptor_render")
    finally:
        wm.terminate()
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print(f"\nscreenshots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
