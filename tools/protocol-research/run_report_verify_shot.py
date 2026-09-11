#!/usr/bin/env python3
"""Card 97 change 3 — live-verify run_report capture-free, by screenshot (no Vanessa).

Boots a fresh native /TESTCLIENT, replays the genuine connect+open setup + the PF_RUN_REPORT command click
(the `click_command` family). The command fills the form's ТабличныйДокумент attribute PF_REPORT ON THE SERVER
(cells PF_RPT_R1C1…R2C2); the fixture form stays rendered after the connection closes, so the screenshot shows
the produced spreadsheet (the cell content the spreadsheet field renders — the visual "read of the resulting
spreadsheet", since the .mxl cell content is a 1C-packed binary blob on the wire, not plain strings).

    .venv/bin/python tools/protocol-research/run_report_verify_shot.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import capture_screenshot, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol.native_write import click_command, derive_command_click  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card97-ch3-report-20260619"


def main() -> int:
    out = REPO / "runtime/protocol-research/report-shot" / timestamp_name()
    out.mkdir(parents=True, exist_ok=True)
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, disp = r["pid"], r.get("xvfb_pid"), r["display"]
    try:
        t = derive_command_click(CAP, "PF_RUN_REPORT")
        res = click_command(t, None, port=15381)
        time.sleep(1.5)
        shot = out / "run_report.png"
        a = capture_screenshot(disp, out_path=str(shot))
        print(f"run_report accepted={res.get('accepted')} display={disp} png={a.get('size_bytes')}B -> {shot.name}")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print("out=", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
