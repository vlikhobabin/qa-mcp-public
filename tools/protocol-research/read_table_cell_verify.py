#!/usr/bin/env python3
"""Card 98 — live-verify the productized read_table_cell MCP tool on the fixture form table (3 default rows).

    .venv/bin/python tools/protocol-research/read_table_cell_verify.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import launch_test_client, read_table_cell, stop_test_client  # noqa: E402

EXPECT = {"PF_TABLE_TEXT": "PF_ROW_001_TEXT", "PF_TABLE_NUMBER": "1,10", "PF_TABLE_MARKER": "PF_ROW_001"}


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid}")
    ok = True
    try:
        for col, exp in EXPECT.items():
            d = read_table_cell("PF_TABLE_ITEMS", col, port=15381)
            got = d.get("value")
            mark = "PASS" if got == exp else "FAIL"
            ok = ok and got == exp
            print(f"  {col}: value={got!r} (expect {exp!r}) groups={d.get('groups')} -> {mark}")
        print("\nPASS — read_table_cell reads fixture form-table cells" if ok else "\nFAIL")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
