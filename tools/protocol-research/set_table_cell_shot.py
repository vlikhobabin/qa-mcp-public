#!/usr/bin/env python3
"""Card 90 / 86e — capture-free table-cell write, verified VISUALLY (a committed table cell isn't a plain
EditField value-read; it renders into the grid). Launch the TestClient on an OWNED Xvfb display, open the
fixture form (the captured setup adds a row → it is the ACTIVE row), screenshot baseline, write into the
active-row PF_TABLE_TEXT cell, screenshot after — the new row's cell must show the value.

    uv run --frozen python tools/protocol-research/set_table_cell_shot.py [value]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import capture_screenshot, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol.native_write import NativeWriteSession, derive_table_cell_write  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card90-table-20260617/traffic-selfcontained"


def main() -> int:
    value = sys.argv[1] if len(sys.argv) > 1 else "HELLO9"
    out = REPO / "runtime/protocol-research/table-cell-shot" / timestamp_name()
    out.mkdir(parents=True, exist_ok=True)
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, disp = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={disp} listening={r.get('listening')}")
    try:
        t = derive_table_cell_write(CAP)
        with NativeWriteSession(t, port=15381) as s:
            time.sleep(1.5)
            b = capture_screenshot(disp, out_path=str(out / "0-baseline.png"))
            print("baseline png:", b.get("path"), b.get("size_bytes"))
            res = s.set_table_cell(value)
            print("write result:", res)
            time.sleep(1.5)
            a = capture_screenshot(disp, out_path=str(out / "1-after.png"))
            print("after png:", a.get("path"), a.get("size_bytes"))
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print("out=", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
