#!/usr/bin/env python3
"""Card 99 #2 — live-verify the GENERAL set_table_date_cell tool: set the fixture PF_TABLE_DATE cell with the
calendar button LOCATED ON SCREEN (template-match), no hardcoded coordinates, and read it back.

    .venv/bin/python tools/protocol-research/set_table_date_cell_probe.py [DD.MM.YYYY]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import launch_test_client, set_table_date_cell, stop_test_client  # noqa: E402

DATE = sys.argv[1] if len(sys.argv) > 1 else "15.08.2026"
EVID = REPO / "evidence" / "card99-set-table-date-cell-2026-06-20"


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r.get("display")
    print(f"launched pid={pid} display={display}")
    rc = 1
    try:
        res = set_table_date_cell(date=DATE, display=display, manage_wm=True)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        rc = 0 if (res.get("localized") and res.get("status") == "set") else 1
        EVID.mkdir(parents=True, exist_ok=True)
        (EVID / "set_table_date_cell_run.json").write_text(
            json.dumps({"date": DATE, "display": display, "result": res}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        # crop the date-cell region of the proof screenshot for the evidence bundle
        shot = res.get("screenshot")
        if shot and Path(shot).is_file():
            import subprocess
            subprocess.run(["convert", shot, "-crop", "260x70+1040+340", "+repage",
                            str(EVID / "date_cell_set.png")], check=False)
        print(f"\nevidence → {EVID / 'set_table_date_cell_run.json'}")
        print("⇒ " + (f"✅ PASS — {DATE} set via LOCALIZED calendar (no hardcoded coords); button "
                      f"{res.get('button_xy')} found by template-match; screenshot proof {res.get('screenshot')}"
                      if rc == 0 else f"✗ status={res.get('status')} localized={res.get('localized')}"))
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
