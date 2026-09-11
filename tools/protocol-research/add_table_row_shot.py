#!/usr/bin/env python3
"""Card 90 follow-up #2 — verify the productized add_table_row (click PF_ADD_ROW) capture-free, by screenshot:
a 4th row (PF_ROW_ADDED_4 / PF_ADDED_TEXT) must appear and become active.

    uv run --frozen python tools/protocol-research/add_table_row_shot.py
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

CAP = REPO / "runtime/protocol-research/captures/genuine-card90-addrow-20260617/traffic-selfcontained"


def main() -> int:
    out = REPO / "runtime/protocol-research/addrow-shot" / timestamp_name()
    out.mkdir(parents=True, exist_ok=True)
    t = derive_command_click(CAP, "PF_ADD_ROW")
    print(f"setup_end={t.setup_end} click_block={t.click_block}")
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, disp = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={disp}")
    try:
        res = click_command(t, None, port=15381)  # add_table_row = click PF_ADD_ROW
        print("add_table_row:", res)
        time.sleep(1.5)
        a = capture_screenshot(disp, out_path=str(out / "after.png"))
        print("after png:", a.get("size_bytes"))
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print("out=", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
