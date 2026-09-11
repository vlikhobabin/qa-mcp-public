#!/usr/bin/env python3
"""Card 98 follow-up — verify the DYNLIST go-to-row-by-value replay positions to the WHERE row and reads it.

Faithful full-sequence replay of genuine-card98-rowbyvalue, with the match value retargeted. The genuine capture
matched Наименование=Сапоги (код 000000002). Default test: Наименование=Молоко (6 chars, same length as Сапоги →
no resize) → expect код 000000026 per OData.

    .venv/bin/python tools/protocol-research/dynlist_rowbyvalue_probe.py [value] [expected_code] [port]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol.native_write import read_list_row_by_value_replay  # noqa: E402

VALUE = sys.argv[1] if len(sys.argv) > 1 else "Молоко"
EXPECT = sys.argv[2] if len(sys.argv) > 2 else "000000026"
PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 15381
CAP = REPO / "runtime/protocol-research/captures/genuine-card98-rowbyvalue"
LINK = "e1cib/list/Справочник.Товары"


def main() -> int:
    r = srv.launch_test_client(port=PORT, manage_apache=(PORT == 15381), display="auto", wait_sec=180.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    try:
        out = read_list_row_by_value_replay(
            CAP, where_value=VALUE, open_link=LINK, columns=["Наименование", "Код"], port=PORT)
        row = out["row"]
        ok_name = row.get("Наименование") == VALUE
        ok_code = row.get("Код") == EXPECT
        print(f"where Наименование={VALUE!r} -> row={row}")
        print(f"  Наименование match: {ok_name} ({row.get('Наименование')!r} == {VALUE!r})")
        print(f"  Код match:          {ok_code} ({row.get('Код')!r} == {EXPECT!r})")
        print("PASS" if (ok_name and ok_code) else "FAIL")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=(PORT == 15381))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
