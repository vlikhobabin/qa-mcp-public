#!/usr/bin/env python3
"""Card 98 follow-up — verify read_list_grid reads NESTED items in FLAT view via the genuine flat-view capture.

Товары defaults to hierarchical (4 top-level folders). The genuine-card98-nextrow-flat capture bakes the
«ФормаСписок» view-switch into the open sequence, so a faithful full-replay reads the FLAT list (nested items).
Compares the read rows against OData ground truth (Наименование sort order in flat view).

    .venv/bin/python tools/protocol-research/dynlist_flat_grid_probe.py [max_rows] [port]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402

MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 12
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 15381
LINK = "e1cib/list/Справочник.Товары"


def main() -> int:
    r = srv.launch_test_client(port=PORT, manage_apache=(PORT == 15381), display="auto", wait_sec=180.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    try:
        out = srv.read_list_grid(open_link=LINK, columns=["Наименование", "Код"], max_rows=MAX,
                                 capture_dir="genuine-card98-nextrow-flat", port=PORT)
        print(f"FLAT row_count={out['row_count']}")
        nested = {"Кроссовки", "Пинетки", "Молоко", "Bosch1234", "Sony К3456P", "Сапоги", "Туфли"}
        for i, row in enumerate(out["rows"], 1):
            tag = "  <-- NESTED" if row.get("Наименование") in nested else ""
            print(f"  {i:2d}. {row}{tag}")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=(PORT == 15381))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
