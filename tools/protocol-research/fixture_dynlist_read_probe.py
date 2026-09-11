#!/usr/bin/env python3
"""Card 98 — does the table-cell read work on a POPULATED DYNLIST? The fixture form hosts a dynamic list
`ДенамическийСписокИерархия` over Catalog.Товары (vanessa_client Товары has rows: Молоко, Творог, …). Open the
fixture (frames 11-17), then read the dynlist's CURRENT ROW columns via read_table_cell. If a column returns a
Товары value, dynlist read works on a populated list (the demo Валюты was empty/different); if None, a dynlist
needs explicit current-row positioning.

    .venv/bin/python tools/protocol-research/fixture_dynlist_read_probe.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import launch_test_client, read_table_cell, stop_test_client  # noqa: E402

TABLE = "ДенамическийСписокИерархия"
COLUMNS = ["Наименование", "Код", "Артикул"]


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid}; reading dynlist {TABLE} (over Catalog.Товары)")
    got_any = False
    try:
        for col in COLUMNS:
            d = read_table_cell(TABLE, col, port=15381)
            v = d.get("value")
            got_any = got_any or bool(v)
            print(f"  {col}: value={v!r} groups={d.get('groups')}")
        print("\nPASS — populated dynlist current-row read works" if got_any
              else "\nFAIL — dynlist returns no value even when populated (needs current-row positioning)")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0 if got_any else 1


if __name__ == "__main__":
    raise SystemExit(main())
