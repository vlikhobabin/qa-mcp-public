#!/usr/bin/env python3
"""Card 90 — capture-free write into a SPECIFIC EXISTING row, verified by screenshot. The capture's setup
includes a genuine row-select (e.g. position to row 2), so replaying it makes that row active and the cell SET
lands there. Proves "адресная запись в конкретную строку" composes (row-select in setup + active-row cell SET).

    uv run --frozen python tools/protocol-research/set_table_cell_row_shot.py <capture_dir> <captured_value> <new_value> [commit_partner_value]
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


def main() -> int:
    cap = Path(sys.argv[1])
    captured = sys.argv[2]
    new_value = sys.argv[3] if len(sys.argv) > 3 else "ROW2OK"
    partner = sys.argv[4] if len(sys.argv) > 4 else "C90RC"
    out = REPO / "runtime/protocol-research/table-cell-row-shot" / timestamp_name()
    out.mkdir(parents=True, exist_ok=True)
    t = derive_table_cell_write(cap, column="PF_TABLE_TEXT", captured_value=captured,
                                commit_partner_field="PF_EDIT_STRING", commit_partner_value=partner)
    print(f"setup_end={t.setup_end} write_block={t.write_block} commit_block={t.commit_block}")

    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, disp = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={disp} listening={r.get('listening')}")
    try:
        with NativeWriteSession(t, port=15381) as s:
            time.sleep(1.5)
            capture_screenshot(disp, out_path=str(out / "0-before.png"))
            res = s.set_table_cell(new_value)
            print("write:", res)
            time.sleep(1.5)
            capture_screenshot(disp, out_path=str(out / "1-after.png"))
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print("out=", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
