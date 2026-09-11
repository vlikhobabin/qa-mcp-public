#!/usr/bin/env python3
"""Card 97 #2 DATE grid cell — pure-MOUSE calendar-picker approach. Synthetic XTEST keystrokes don't reach 1C's
masked date editor (proven: type AND per-key, in every focus state, leave the value unchanged; the plain string
field DOES accept type). But mouse events DO reach the window. So: protocol-activate the cell (edit mode → the
calendar dropdown button appears), click the dropdown, and drive the calendar popup by mouse.

Step 1 here: open the calendar and screenshot it (to see the popup layout / nav / day-grid coords).

    .venv/bin/python tools/protocol-research/date_cell_calendar_probe.py
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
from qa_mcp.protocol.bootstrap import resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.native_mutation import _read_available  # noqa: E402
from qa_mcp.protocol.native_write import (  # noqa: E402
    NativeWriteSession, build_write_frame, derive_table_cell_write, read_table_cell_value,
)
from qa_mcp.protocol.native_xtest import calendar_day_cell, calendar_month_cell  # noqa: E402

CAP = "genuine-card90-table-20260617/traffic-selfcontained"
SHOT = "runtime/protocol-research/screenshots"
CAL_BTN_XY = (1248, 370)   # the calendar dropdown button at the right of the active-row date cell (matchbox)


def _xdo(display: str, *args: str) -> None:
    subprocess.run(["xdotool", *args], env={**os.environ, "DISPLAY": display},
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r.get("display")
    print(f"launched pid={pid} listening={r.get('listening')} display={display}")
    wm = subprocess.Popen(["matchbox-window-manager", "-use_titlebar", "no"],
                          env={**os.environ, "DISPLAY": display},
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    try:
        template = derive_table_cell_write(resolve_capture_dir(CAP, _repo_root()), "PF_TABLE_TEXT", "CELLAA",
                                           commit_partner_field="PF_EDIT_STRING", commit_partner_value="C90CMT")
        with NativeWriteSession(template, host="127.0.0.1", port=15381) as s:
            lo, hi = s.t.write_block
            for i in range(lo, hi + 1):
                wire = build_write_frame(s._rebinder.apply(s._mgr[i]), s.t.captured_value, "CELLAA",
                                         base_field=s.t.field, target_field="PF_TABLE_DATE", seq=s._seq)
                s._seq += 1
                s._sock.sendall(wire)
                s._rebinder.observe_response(_read_available(s._sock, s.rt, s.it))
            time.sleep(1.2)
            x, y = CAL_BTN_XY
            _xdo(display, "mousemove", str(x), str(y))
            _xdo(display, "click", "1")          # open the calendar dropdown
            time.sleep(1.0)
            c = capture_screenshot(display, out_path=f"{SHOT}/date-calendar-open.png")
            print(f"calendar-open -> {c.get('path')}")
            # year is already 2026. Click the month then the day — coords from the calendar geometry helpers.
            mx, my = calendar_month_cell(8)        # Авг
            dx, dy = calendar_day_cell(2026, 8, 15)  # 15.08.2026
            _xdo(display, "mousemove", str(mx), str(my)); _xdo(display, "click", "1")
            time.sleep(0.8)
            _xdo(display, "mousemove", str(dx), str(dy)); _xdo(display, "click", "1")
            time.sleep(1.0)
            p = capture_screenshot(display, out_path=f"{SHOT}/date-calendar-picked.png")
            print(f"calendar-picked -> {p.get('path')}  (clicked Авг + 15 -> cell shows 15.08.2026)")
            # commit the cell edit (Enter) so the value lands in the row data, then read it back
            _xdo(display, "key", "Return")
            time.sleep(1.0)
            cm = capture_screenshot(display, out_path=f"{SHOT}/date-calendar-committed.png")
            print(f"committed -> {cm.get('path')}")
            rb = b""
            for i in s.t.read_frames:
                if i < len(s._mgr):
                    s._sock.sendall(s._rebinder.apply(s._mgr[i]))
                    rb += _read_available(s._sock, s.rt, s.it)
            print(f"readback PF_TABLE_DATE -> {read_table_cell_value(rb, 'PF_TABLE_DATE')!r}")
            time.sleep(0.4)
    finally:
        wm.terminate()
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
