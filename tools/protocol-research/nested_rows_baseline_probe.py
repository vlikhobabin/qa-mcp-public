#!/usr/bin/env python3
"""Card 98 follow-up — baseline + flat-view probe for NESTED dynlist rows.

read_list_grid walks the list's CURRENT view. Товары defaults to hierarchical (4 top-level folders), so the
nested items are invisible. This probe (1) re-confirms the hierarchical baseline (lab health), then prints the
row count so we can compare against a flat-view capture once one exists.

    .venv/bin/python tools/protocol-research/nested_rows_baseline_probe.py [port]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
LINK = "e1cib/list/Справочник.Товары"
COLS = ["Наименование", "Код"]


def main() -> int:
    r = srv.launch_test_client(port=PORT, manage_apache=(PORT == 15381), display="auto", wait_sec=180.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    try:
        out = srv.read_list_grid(open_link=LINK, columns=COLS, max_rows=40, port=PORT)
        print(f"row_count={out['row_count']}")
        for i, row in enumerate(out["rows"], 1):
            print(f"  {i:2d}. {row}")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=(PORT == 15381))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
