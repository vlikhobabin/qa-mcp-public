#!/usr/bin/env python3
"""Card 100 — LIVE-VERIFY the productized set_table_date_cell(open_link=…, column_title=…) MCP tool end-to-end on
the real Документ.Заказ Товары.Дата cell, CONFIG-AGNOSTIC (auto-localize the cell from the column header «Дата»,
no measured coords, no per-form capture). Launches a client, calls the shipped tool, screenshots the proof, stops.

    .venv/bin/python tools/protocol-research/document_datecell_tool_verify.py [DD.MM.YYYY]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol.navigation import e1cib_data_link  # noqa: E402

ORDER_REF = "0faf2b04-fc04-11e1-bbef-0050ba5c8877"
LINK = e1cib_data_link("Документ.Заказ", ORDER_REF)


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "15.08.2026"
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={display} target={target}")
    try:
        res = srv.set_table_date_cell(
            date=target,
            open_link=LINK,
            column="ТоварыДата",
            table="Товары",
            column_title="Дата",         # auto-localize the cell from the on-screen header — no measured coords
            port=15381,
            display=display,
            manage_wm=True,
            prime=True,
        )
        print(json.dumps(res, ensure_ascii=False, indent=2))
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
