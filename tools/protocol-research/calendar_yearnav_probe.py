#!/usr/bin/env python3
"""Card 99 #2 year-nav investigation — open the date calendar and probe its YEAR controls, screenshotting each
step so the behavior is observed (no guessing): does the ‹/› arrow step YEAR or MONTH? does «Сегодня» navigate
(stay open) or select+close? what does clicking the year «2026 ▼» label do? Coords measured from the saved
date-calendar-open.png; the calendar button is localized live.

    .venv/bin/python tools/protocol-research/calendar_yearnav_probe.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol import screenshot as client_screenshot  # noqa: E402
from qa_mcp.protocol.bootstrap import resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.native_mutation import _read_available  # noqa: E402
from qa_mcp.protocol.native_write import NativeWriteSession, build_write_frame, derive_table_cell_write  # noqa: E402
from qa_mcp.protocol.native_xtest import locate_calendar_button, xtest_click, xtest_key, xtest_type  # noqa: E402

OUT = REPO / "runtime" / "protocol-research" / "screenshots" / "yearnav"
CAP = "genuine-card90-table-20260617/traffic-selfcontained"
# best-estimate control coords from date-calendar-open.png (popup with button center (1249,370))
RIGHT_ARROW = (1248, 418)
LEFT_ARROW = (1210, 418)
TODAY_LINK = (960, 625)
YEAR_LABEL = (940, 418)


def main() -> int:
    import os
    import subprocess

    OUT.mkdir(parents=True, exist_ok=True)
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r.get("display")
    print(f"launched pid={pid} display={display}")
    wm = subprocess.Popen(["matchbox-window-manager", "-use_titlebar", "no"],
                          env={**os.environ, "DISPLAY": display}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    template = derive_table_cell_write(resolve_capture_dir(CAP, srv._repo_root()), "PF_TABLE_TEXT", "CELLAA",
                                       commit_partner_field="PF_EDIT_STRING", commit_partner_value="C90CMT")

    def shot(name: str) -> None:
        client_screenshot.capture_screenshot(display, str(OUT / f"{name}.png"))
        print(f"  shot {name}")

    try:
        with NativeWriteSession(template, host="127.0.0.1", port=15381) as s:
            lo, hi = s.t.write_block
            for i in range(lo, hi + 1):
                wire = build_write_frame(s._rebinder.apply(s._mgr[i]), s.t.captured_value, "CELLAA",
                                         base_field=s.t.field, target_field="PF_TABLE_DATE", seq=s._seq)
                s._seq += 1
                s._sock.sendall(wire)
                s._rebinder.observe_response(_read_available(s._sock, s.rt, s.it))
            time.sleep(1.2)
            sh = str(OUT / "00_activated.png")
            client_screenshot.capture_screenshot(display, sh)
            btn = locate_calendar_button(sh)
            print(f"button: {btn}")
            if btn is None:
                return 1
            xtest_click(display, *btn); time.sleep(1.0); shot("01_calendar_open")
            # (A) TYPE-AHEAD in the open year dropdown: open «2026 ▼», then type a target year
            xtest_click(display, 990, 428); time.sleep(0.8); shot("02_year_dropdown_open")
            xtest_type(display, "2028"); time.sleep(0.8); shot("03_typed_2028_in_dropdown")
            xtest_key(display, "Return"); time.sleep(0.8); shot("04_after_return")
            # (B) DROPDOWN ROW pick: re-open, click the row that should be current+2 (=2028 from 2026 top)
            xtest_click(display, 990, 428); time.sleep(0.8); shot("05_year_dropdown_again")
            xtest_click(display, 952, 478); time.sleep(0.8); shot("06_clicked_row2")  # 3rd row from top
    finally:
        wm.terminate()
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print(f"\nscreenshots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
