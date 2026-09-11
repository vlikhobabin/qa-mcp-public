#!/usr/bin/env python3
"""Card 97 #2 DATE grid cell via the XTEST HYBRID — protocol opens/renders the form, OS keystrokes enter the
date into the PF_TABLE_DATE cell (the protocol text-SET is ruled out: the date column returns committed=False).

Holds ONE manager connection so the form stays rendered, scrolls to the PF_TABLE_ITEMS grid, then xdotool
double-clicks the active row's date cell (rightmost column), types a new date, and commits with Return — the
same focus-by-protocol + OS-input mechanism as write_form_value_xtest (object-attribute write). Verified by an
after-screenshot (the new date shows in the grid).

    .venv/bin/python tools/protocol-research/date_cell_xtest_probe.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import _repo_root, capture_screenshot, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

CAP = "tm-v1-ro-batchQ3"
TPL = "runtime/protocol-research/templates/tm-v1-open-plus-valueread/manager_frame_templates.json"
NEW_DATE = "15.08.2026"           # the date to type into PF_TABLE_DATE row 1 (was 10.01.2026 9:00:00)
DATE_CELL_XY = (1130, 485)        # PF_ROW_001 date cell under matchbox-MAXIMIZED layout (date-xtest-typed.png)


def _xdo(display: str, *args: str) -> str:
    p = subprocess.run(["xdotool", *args], env={**os.environ, "DISPLAY": display},
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return p.stdout.strip()


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r.get("display")
    print(f"launched pid={pid} listening={r.get('listening')} display={display}")
    wm = subprocess.Popen(["matchbox-window-manager", "-use_titlebar", "no"],
                          env={**os.environ, "DISPLAY": display},
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # WM → keyboard focus
    time.sleep(1.0)
    try:
        repo = _repo_root()
        bootstrap = CaptureBootstrap.load(resolve_capture_dir(CAP, repo))
        templates = ProtocolTemplates.load((repo / TPL).resolve())
        out_dir = repo / "runtime" / "protocol-research" / "native-mcp" / timestamp_name()
        with TestClientSession(host="127.0.0.1", port=15381) as session:
            handle = session.open_and_bootstrap(bootstrap=bootstrap, templates=templates,
                                                 output_dir=out_dir, synthesized=synthesize_bootstrap())
            handle.run_segment(list(range(11, 18)), query_id="form-element-details")
            time.sleep(2.0)
            _xdo(display, "mousemove", "700", "600")
            for _ in range(14):
                _xdo(display, "click", "5")
                time.sleep(0.08)
            time.sleep(1.0)
            b = capture_screenshot(display, out_path="runtime/protocol-research/screenshots/date-xtest-before.png")
            print(f"before -> {b.get('path')}")

            # matchbox gives the 1C window keyboard focus (xdotool key/type otherwise go nowhere with no WM).
            wid = _xdo(display, "search", "--onlyvisible", "--name", "тестирования")
            print(f"window search -> {wid!r}")
            if wid:
                _xdo(display, "windowactivate", "--sync", wid.split("\n")[0])
                time.sleep(0.4)
            x, y = DATE_CELL_XY
            _xdo(display, "mousemove", str(x), str(y))
            _xdo(display, "click", "1")          # select the cell
            time.sleep(0.5)
            _xdo(display, "key", "Return")       # Enter on a selected 1C grid cell ENTERS edit (value selected)
            time.sleep(0.9)
            e = capture_screenshot(display, out_path="runtime/protocol-research/screenshots/date-xtest-edit.png")
            print(f"edit   -> {e.get('path')}")
            # send the date KEY-BY-KEY (xdotool `key` reaches 1C's custom-drawn editor where `type` does not);
            # "." -> the 'period' keysym. The value is auto-selected on edit-open, so the first key replaces it.
            keymap = {".": "period"}
            for ch in NEW_DATE:
                _xdo(display, "key", keymap.get(ch, ch))
                time.sleep(0.1)
            time.sleep(0.6)
            t = capture_screenshot(display, out_path="runtime/protocol-research/screenshots/date-xtest-typed.png")
            print(f"typed  -> {t.get('path')}")
            _xdo(display, "key", "Return")       # commit the edited cell
            time.sleep(1.2)
            a = capture_screenshot(display, out_path="runtime/protocol-research/screenshots/date-xtest-after.png")
            print(f"after  -> {a.get('path')}   (typed {NEW_DATE!r} into the active-row PF_TABLE_DATE cell)")
            time.sleep(0.5)
    finally:
        wm.terminate()
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
