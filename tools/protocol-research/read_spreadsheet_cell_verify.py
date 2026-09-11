#!/usr/bin/env python3
"""Card 97 change 3 — live-verify read_spreadsheet_cell capture-free (no Vanessa, no .mxl decode).

For each cell address, boots a fresh native /TESTCLIENT, replays the genuine flow (open form → run the report →
navigate to the cell) with the address re-targeted, and reads the cell VALUE from the client response (the value
rides the wire as the card-79 \\x9a<len><utf-8> shape — the cell is read by an in-client 1C method on the live
ТабличныйДокумент, never as a binary blob). The returned value IS the proof:
  R1C1 -> PF_RPT_R1C1   R1C2 -> PF_RPT_R1C2   R2C1 -> PF_RPT_R2C1   R2C2 -> PF_RPT_R2C2

    .venv/bin/python tools/protocol-research/read_spreadsheet_cell_verify.py [R1C1 R2C2 ...]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol.native_write import derive_read_spreadsheet_cell, read_spreadsheet_cell  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card97-ch3-cellread-20260619"


def main(argv: list[str]) -> int:
    addresses = argv or ["R1C1", "R1C2", "R2C1", "R2C2"]
    t = derive_read_spreadsheet_cell(CAP)
    print(f"template field={t.field} captured_address={t.captured_address} captured_value={t.captured_value!r}")
    ok = 0
    for addr in addresses:
        r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
        pid, xvfb = r["pid"], r.get("xvfb_pid")
        try:
            res = read_spreadsheet_cell(t, addr, port=15381)
            expected = "PF_RPT_" + addr  # PF_RPT_R1C1 etc.
            good = res.get("value") == expected
            ok += good
            print(f"  {addr} -> value={res.get('value')!r} expected={expected!r} {'OK' if good else 'MISMATCH'}")
        finally:
            stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
            time.sleep(1.0)
    print(f"PASS {ok}/{len(addresses)}")
    return 0 if ok == len(addresses) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
