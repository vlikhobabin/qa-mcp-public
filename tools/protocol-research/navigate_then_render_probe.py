#!/usr/bin/env python3
"""Card 101 Change 2 — the decisive config-agnostic foreground test. The fixture-open render/activate frames
(_VALUE_READ_OPEN_FRAMES 11-17) foreground the fixture. If those frames operate on the session's CURRENT form,
then navigating the TARGET first (background) and THEN replaying the render frames should foreground the TARGET —
fixture-free, config-agnostic. Test: cold bootstrap → navigate Заказ (bg) → run_segment(11..16) → screenshot →
run_segment(17) → screenshot. If Заказ foregrounds, the primer is generic.

    .venv/bin/python tools/protocol-research/navigate_then_render_probe.py
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
DATA_LINK = e1cib_data_link("Документ.Заказ", ORDER_REF)
OUT = REPO / "runtime" / "protocol-research" / "screenshots" / "navrender"


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

    def shot(name):
        srv.capture_screenshot(display, out_path=str(OUT / f"{name}.png")); print(f"  shot {name}")

    try:
        with TestClientSession(host="127.0.0.1", port=15381) as s:
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            time.sleep(1.2); shot("10_desktop")
            print(f"navigate Заказ (bg) -> {srv._open_form_by_link(h, DATA_LINK)}")
            time.sleep(2.0); shot("20_after_navigate_bg")
            # replay the generic render/activate frames (no fixture SF until 17) on the current form
            try:
                h.run_segment([11, 12, 13, 14, 15, 16], query_id="form-element-details")
            except Exception as e:  # noqa: BLE001
                print(f"  run_segment(11..16) exc: {e}")
            time.sleep(2.0); shot("30_after_render_11_16")
            try:
                h.run_segment([17], query_id="form-element-details")
            except Exception as e:  # noqa: BLE001
                print(f"  run_segment(17) exc: {e}")
            time.sleep(2.0); shot("40_after_render_17")
    finally:
        wm.terminate()
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print(f"\nscreenshots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
