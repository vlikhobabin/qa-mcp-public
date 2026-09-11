#!/usr/bin/env python3
"""Card 101 Change 2 — disambiguate the foreground trigger. Genuine-card90-openlist opens the fixture via an
`e1cib/app/` navigate (mgr[11-12]) FIRST, then `e1cib/list` (mgr[14-15]); both foreground. Hypothesis: an
`e1cib/app/` navigate from COLD foregrounds + establishes tabbed mode (then list/data navigates foreground), while
`e1cib/list|data` from cold backgrounds. Test: cold bootstrap → navigate the app-link (NO render frames, just
splice_navigate) → screenshot; then navigate the doc data-link → screenshot.

    .venv/bin/python tools/protocol-research/app_navigate_foreground_probe.py
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
APP_LINK = "e1cib/app/Обработка.ФикстураПротоколаTestClient"
OUT = REPO / "runtime" / "protocol-research" / "screenshots" / "appnav"


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
            print(f"navigate APP-link -> {srv._open_form_by_link(h, APP_LINK)}")
            time.sleep(2.5); shot("20_after_app_navigate")
            print(f"navigate DATA-link -> {srv._open_form_by_link(h, DATA_LINK)}")
            time.sleep(2.5); shot("30_after_data_navigate")
    finally:
        wm.terminate()
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print(f"\nscreenshots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
