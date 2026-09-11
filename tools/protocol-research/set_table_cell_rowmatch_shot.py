#!/usr/bin/env python3
"""Card 90 follow-up #1 — verify the PRODUCTIZED set_table_cell(row_match=…): write into the row whose
PF_TABLE_TEXT equals row_match (the genuine row-select value is re-targeted in the setup). Launch the client,
call the standalone set_table_cell with row_match, screenshot after (the window persists post-disconnect).

    uv run --frozen python tools/protocol-research/set_table_cell_rowmatch_shot.py <cap> <captured_cell> <new_cell> <captured_row_match> <row_match> [commit_partner]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import capture_screenshot, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol.native_write import derive_table_cell_write, set_table_cell  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402


def main() -> int:
    cap = Path(sys.argv[1])
    captured_cell, new_cell = sys.argv[2], sys.argv[3]
    captured_row_match, row_match = sys.argv[4], sys.argv[5]
    partner = sys.argv[6] if len(sys.argv) > 6 else "C90RC"
    out = REPO / "runtime/protocol-research/rowmatch-shot" / timestamp_name()
    out.mkdir(parents=True, exist_ok=True)
    t = derive_table_cell_write(cap, column="PF_TABLE_TEXT", captured_value=captured_cell,
                                commit_partner_field="PF_EDIT_STRING", commit_partner_value=partner)

    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, disp = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={disp}")
    try:
        res = set_table_cell(t, new_cell, row_match=row_match, captured_row_match=captured_row_match, port=15381)
        print("set_table_cell(row_match=%r):" % row_match, res)
        time.sleep(1.5)
        a = capture_screenshot(disp, out_path=str(out / "after.png"))
        print("after png:", a.get("size_bytes"))
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print("out=", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
