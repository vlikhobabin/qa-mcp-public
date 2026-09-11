#!/usr/bin/env python3
"""Card 100 Blocker 1 — foreground the navigated form. `_open_form_by_link` opens Документ.Заказ as a BACKGROUND
tab (desktop stays foreground). Hypothesis: the card-96 window-level command `…SecondaryFrame[S] 88 82 81 20 20 20`
applied to a BACKGROUND window ACTIVATES it (brings forward). Build that command as a SPLICE onto the no-form
header (like splice_navigate/resolve/descriptor) targeting the navigated form's S, send it on the HELD connection,
and screenshot before/after to observe whether the Заказ form comes to the foreground.

    .venv/bin/python tools/protocol-research/document_foreground_probe.py
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
from qa_mcp.protocol.native_write import (  # noqa: E402
    _read_chunks, MANAGER_TO_CLIENT, CLIENT_TO_MANAGER, _window_sf_for_ref,
    _find_window_close, WINDOW_LIST_HEADER_MARKER, splice_window_list_queries,
)
from qa_mcp.protocol.responses import extract_testclient_windows  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

ORDER_REF = "0faf2b04-fc04-11e1-bbef-0050ba5c8877"
LINK = e1cib_data_link("Документ.Заказ", ORDER_REF)
OUT = REPO / "runtime" / "protocol-research" / "screenshots" / "docforeground"


def _activate_constants() -> tuple[bytes, bytes]:
    """Extract (PREPATH = nonce+`9a 34`, POSTPATH = `88 82 81 20 20 20`+tail) from the genuine activate capture's
    window-level command frame — the bytes around `SecondaryFrame[sf]`."""
    cap = resolve_capture_dir("genuine-card96-activate-20260618/traffic", REPO)
    mgr = _read_chunks(cap, MANAGER_TO_CLIENT)
    cli = _read_chunks(cap, CLIENT_TO_MANAGER)
    ref = "e1cib/app/Обработка.ФикстураПротоколаTestClient"
    sf = _window_sf_for_ref(mgr + cli, ref)
    frame = mgr[_find_window_close(mgr, sf)]
    j = frame.rfind(WINDOW_LIST_HEADER_MARKER)
    body = frame[j + len(WINDOW_LIST_HEADER_MARKER):]
    sfb = f"SecondaryFrame[{sf}]".encode("latin1")
    p = body.find(sfb)
    prepath = body[:p]                 # nonce + `9a 34`
    postpath = body[p + len(sfb):]     # `88 82 81 20 20 20` + tail `66 53 b2 a6`
    return prepath, postpath


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    prepath, postpath = _activate_constants()
    print(f"activate PREPATH={prepath.hex()}  POSTPATH={postpath.hex()}")

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

    def windows(handle):
        before = len(handle.state.received_stream)
        for q in splice_window_list_queries(srv._splice_header_no_form(handle)):
            handle.run_action(q, query_id="window-list")
        return extract_testclient_windows(bytes(handle.state.received_stream[before:]))

    try:
        with TestClientSession(host="127.0.0.1", port=15381) as s:
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            time.sleep(1.5)
            shot("10_desktop")
            resolved = srv._open_form_by_link(h, LINK)
            print(f"resolved: {resolved}")
            if not resolved:
                return 1
            caption, sf, mf = resolved
            time.sleep(2.5)
            shot("20_after_open_background")
            wl = windows(h)
            print(f"windows after open: {[(w['kind'], w.get('caption','')[:30]) for w in wl]}")

            # BUILD + SEND the window-level activate command targeting the navigated form's S, on the held conn.
            header = srv._splice_header_no_form(h)
            s_path = f"SecondaryFrame[{sf}]".encode("latin1")
            activate = header + prepath + s_path + postpath
            before = len(h.state.received_stream)
            h.run_action(activate, query_id="activate-window")
            resp = bytes(h.state.received_stream[before:])
            print(f"activate resp len={len(resp)}  sf_in_resp={sf.encode() in resp}")
            time.sleep(2.5)
            shot("30_after_activate")
            wl2 = windows(h)
            print(f"windows after activate: {[(w['kind'], w.get('caption','')[:30]) for w in wl2]}")
    finally:
        wm.terminate()
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print(f"\nscreenshots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
