#!/usr/bin/env python3
"""Card 97 #2 DATE grid cell — test whether our protocol value-SET drives a date grid cell capture-free.

Offline decode (genuine-multiaction): the standalone date field input rides the protocol as a TEXT value-SET,
byte-identical to a string/number cell — ``EditField[PF_EDIT_DATE] … e0 41 81 81 ba 0a "17.06.2026"``. The
numdate finding's «Неподходящий тип элемента управления» was VANESSA's step-level pre-check (`я ввожу текст`
refuses a calendar control before sending), not a 1C rejection. Our `set_table_cell` sends the raw SET and
bypasses that check, so it should drive the PF_TABLE_DATE column too. This probe tests that live and screenshots.

    .venv/bin/python tools/protocol-research/date_cell_probe.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import (  # noqa: E402
    launch_test_client, set_table_cell, stop_test_client,
)


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r.get("display")
    print(f"launched pid={pid} listening={r.get('listening')} display={display}")
    try:
        # control: the number cell (known-good via this exact path) — confirms the harness works this session
        num = set_table_cell(value="424242", column="PF_TABLE_NUMBER")
        print(f"\n[control] PF_TABLE_NUMBER=424242 -> committed={num.get('committed')} readback={num.get('readback_value')!r}")

        # the date grid cell — the card-97 target. The captured PF_TABLE_TEXT slot is 9 bytes wide (card-80
        # fixed-width buffer), so try date forms that FIT <=9 chars (1C parses single-/two-digit forms). This
        # answers whether the date column ACCEPTS a protocol text-SET at all. Verification = IN-SESSION SET-echo
        # readback (each call is its own session, so a separate read can't see it).
        for val in ("15.8.2026", "15.08.26", "1.1.2026", "15.08.2026"):  # 9, 8, 8, 10(too wide)
            try:
                d = set_table_cell(value=val, column="PF_TABLE_DATE")
                print(f"[date]    PF_TABLE_DATE={val!r:14} -> committed={d.get('committed')} readback={d.get('readback_value')!r}")
            except Exception as e:
                print(f"[date]    PF_TABLE_DATE={val!r:14} -> ERROR {type(e).__name__}: {e}")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
