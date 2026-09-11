#!/usr/bin/env python3
"""Card 90 / 86e — capture-free TABLE-CELL write, verified by reading the active-row cell back (ASCII).

Decode (evidence genuine-card90-table-decode-2026-06-17): a table-cell SET is byte-identical to a plain
string-field SET (card 86b/c) — only the element path differs (the column is the `EditField` leaf inside a
`Table[<table>]` segment, NO row index, so the SET commits into the ACTIVE row). So a cell write reuses the
card-86c commit machinery: ``derive_table_cell_write`` (commit-partner ``WriteTemplate``) +
``NativeWriteSession.set_table_cell`` (write block + synthesized focus-change + read-back).

This probe opens ONE persistent connection, replays the form-open prefix (which adds a row → the new row is
the ACTIVE row), then writes two values into the active row's PF_TABLE_TEXT cell and reads each back.

    uv run --frozen python tools/protocol-research/set_table_cell_probe.py [port] [capture_dir]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.native_write import NativeWriteSession, derive_table_cell_write  # noqa: E402

DEFAULT_CAP = REPO / "runtime/protocol-research/captures/genuine-card90-table-20260617/traffic-selfcontained"
# 6-char values fit the captured PF_TABLE_TEXT buffer width (CELLAA = 6 + 3 space pad).
VALUES = ("HELLO9", "TBLOK7")


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    cap = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CAP
    t = derive_table_cell_write(cap)
    print(f"capture={cap.name} field={t.field} setup_end={t.setup_end} "
          f"write_block={t.write_block} commit_block={t.commit_block} read_frames={t.read_frames}")

    results: dict[str, str | None] = {}
    with NativeWriteSession(t, port=port) as s:
        for val in VALUES:
            r = s.set_table_cell(val)
            got = r.get("readback_value")
            results[val] = got
            ok = bool(got) and got.startswith(val)
            print(f"  set PF_TABLE_ITEMS.PF_TABLE_TEXT={val!r}: readback={got!r} "
                  f"committed={r.get('committed')}  {'OK' if ok else 'FAIL'}")

    ok = all(bool(results[v]) and results[v].startswith(v) for v in VALUES)
    print("RESULT:", "PASS — capture-free table-cell write commits (active row)" if ok else "INCONCLUSIVE")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
