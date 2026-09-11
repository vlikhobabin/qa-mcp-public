#!/usr/bin/env python3
"""Card 100 Blockers 2/3/4 (e2e) — set a DATE in the real Документ.Заказ Товары date cell, config-agnostic, no
per-form capture. Flow: prime tab mode (fixture frames 11-17) → navigate Заказ (foreground, Blocker 1 SOLVED) →
dismiss any crypto nag → ON-SCREEN double-click the row-1 Дата cell to enter edit mode (Blocker 3, no protocol
write_block / no genuine-card90-table capture) → reuse the generic locate_calendar_button + calendar month/day/
year pick (card 99, form-agnostic) → screenshot proof.

This first proof MEASURES the date-cell screen coords from the known layout; generalizing the localization (Дата
column header subimage-search) is the productization follow-up.

    .venv/bin/python tools/protocol-research/document_datecell_e2e_probe.py [DD.MM.YYYY]
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import date as _date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.navigation import e1cib_data_link  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402
from qa_mcp.protocol.native_xtest import (  # noqa: E402
    CALENDAR_DAY_DELTA, CALENDAR_MONTH_DELTA, CALENDAR_YEAR_MAX_STEP,
    calendar_day_cell, calendar_month_cell, calendar_year_row,
    locate_calendar_button, xtest_click, xtest_key,
)

ORDER_REF = "0faf2b04-fc04-11e1-bbef-0050ba5c8877"
LINK = e1cib_data_link("Документ.Заказ", ORDER_REF)
OUT = REPO / "runtime" / "protocol-research" / "screenshots" / "docdatecell"
# Row-1 Дата cell center, measured from the foreground Заказ form (Товары table, rightmost col, first row).
DATE_CELL_XY = (1160, 471)
SETTLE = 1.2


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "15.08.2026"
    d, m, y = (int(p) for p in target.split("."))
    OUT.mkdir(parents=True, exist_ok=True)
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={display} target={target}")
    wm = subprocess.Popen(["matchbox-window-manager", "-use_titlebar", "no"],
                          env={**os.environ, "DISPLAY": display}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    repo = srv._repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo))
    templates = ProtocolTemplates.load((repo / srv.VALUE_READ_TEMPLATES).resolve())
    synth = synthesize_bootstrap()
    out = repo / "runtime/protocol-research/native-mcp" / timestamp_name()

    def shot(name: str) -> str:
        p = str(OUT / f"{name}.png")
        srv.capture_screenshot(display, out_path=p)
        print(f"  shot {name}")
        return p

    try:
        with TestClientSession(host="127.0.0.1", port=15381) as s:
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            time.sleep(1.2)
            h.run_segment(srv._VALUE_READ_OPEN_FRAMES, query_id="form-element-details")  # prime tab mode
            time.sleep(1.5)
            resolved = srv._open_form_by_link(h, LINK)                                   # foreground Заказ
            print(f"resolved: {resolved}")
            if not resolved:
                return 1
            time.sleep(2.5)
            shot("10_form_foreground")

            # Blocker 3 — ON-SCREEN activate the date cell (double-click), no protocol write_block.
            cx, cy = DATE_CELL_XY
            xtest_click(display, cx, cy); time.sleep(0.2)
            xtest_click(display, cx, cy); time.sleep(SETTLE)          # double-click -> edit mode
            act = shot("20_after_dblclick")
            # Localize the calendar button CONSTRAINED to the activated cell's row band — the form has OTHER date
            # fields (the doc header «Дата») whose calendar glyph would otherwise win the global subimage-search.
            band_y0 = max(0, cy - 22)
            band = str(OUT / "20b_rowband.png")
            subprocess.run(["convert", act, "-crop", f"1280x44+0+{band_y0}", "+repage", band], check=False)
            rel = locate_calendar_button(band)
            button = (rel[0], rel[1] + band_y0) if rel else None
            print(f"calendar button (row-band) @ {button}")
            if button is None:
                print("BLOCKED: calendar button not localized after activation")
                return 2

            # Blocker 4 — reuse the proven calendar pick (form-agnostic).
            bx, by = button
            month_origin = (bx + CALENDAR_MONTH_DELTA[0], by + CALENDAR_MONTH_DELTA[1])
            day_origin = (bx + CALENDAR_DAY_DELTA[0], by + CALENDAR_DAY_DELTA[1])
            xtest_click(display, bx, by); time.sleep(SETTLE)         # open calendar dropdown
            shot("30_calendar_open")
            current_year = _date.today().year                        # empty cell opens on today
            remaining = y - current_year
            print(f"year-nav: current={current_year} target={y} offset={remaining}")
            while remaining > 0:
                step = min(remaining, CALENDAR_YEAR_MAX_STEP)
                xtest_click(display, *calendar_year_row((bx, by), 0)); time.sleep(SETTLE)
                xtest_click(display, *calendar_year_row((bx, by), step)); time.sleep(SETTLE)
                remaining -= step
            shot("31_after_yearnav")
            mx, my = calendar_month_cell(m, origin=month_origin)
            xtest_click(display, mx, my); time.sleep(SETTLE)
            shot("32_after_month")
            dx, dy = calendar_day_cell(y, m, d, origin=day_origin)
            xtest_click(display, dx, dy); time.sleep(SETTLE)
            xtest_key(display, "Return"); time.sleep(SETTLE)
            picked = shot("40_after_pick")
            # verify in the ROW BAND (the doc-header «Дата» glyph elsewhere would false-positive)
            vband = str(OUT / "40b_rowband.png")
            subprocess.run(["convert", picked, "-crop", f"1280x44+0+{band_y0}", "+repage", vband], check=False)
            still_open = locate_calendar_button(vband) is not None
            print(f"PICK DONE target={target} still_open_in_row={still_open} proof={picked}")
    finally:
        wm.terminate()
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print(f"\nscreenshots in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
