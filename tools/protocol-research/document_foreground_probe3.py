#!/usr/bin/env python3
"""Card 100 Blocker 1 (exp3) — disambiguate WHY the fixture form foregrounds but a nav-link document form does not.
In ONE session: bootstrap (desktop), open the FIXTURE via the genuine open frames 11-17 (screenshot), THEN navigate
to Документ.Заказ (screenshot). If the fixture is foreground but Заказ is not, the genuine fixture-open frames carry
a "show/activate form" command the nav-link splice omits → study+adapt them. Also screenshots after replaying the
fixture-open frames' tail again retargeted to the navigated form's S.F.

    .venv/bin/python tools/protocol-research/document_foreground_probe3.py
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
from qa_mcp.protocol.native_write import splice_window_list_queries  # noqa: E402
from qa_mcp.protocol.responses import extract_testclient_windows  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

ORDER_REF = "0faf2b04-fc04-11e1-bbef-0050ba5c8877"
LINK = e1cib_data_link("Документ.Заказ", ORDER_REF)
OUT = REPO / "runtime" / "protocol-research" / "screenshots" / "docforeground3"


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

    def windows(handle):
        before = len(handle.state.received_stream)
        for q in splice_window_list_queries(srv._splice_header_no_form(handle)):
            handle.run_action(q, query_id="window-list")
        wl = extract_testclient_windows(bytes(handle.state.received_stream[before:]))
        return [(w["kind"], w.get("caption", "")[:34]) for w in wl]

    try:
        with TestClientSession(host="127.0.0.1", port=15381) as s:
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            time.sleep(1.2)
            shot("10_desktop")
            print(f"windows @desktop: {windows(h)}")

            # (A) open the FIXTURE via the genuine open frames 11-17 (the path that foregrounds the fixture).
            h.run_segment(srv._VALUE_READ_OPEN_FRAMES, query_id="form-element-details")
            time.sleep(2.5)
            shot("20_fixture_open")
            print(f"windows @fixture: {windows(h)}")

            # (B) now navigate to Документ.Заказ on the SAME session.
            resolved = srv._open_form_by_link(h, LINK)
            print(f"resolved Заказ: {resolved}")
            time.sleep(2.5)
            shot("30_zakaz_open")
            print(f"windows @zakaz: {windows(h)}")
    finally:
        wm.terminate()
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print(f"\nscreenshots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
