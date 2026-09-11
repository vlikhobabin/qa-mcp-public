#!/usr/bin/env python3
"""Card 98 — verify the dynlist read generalizes (column + list retarget) with a FRESH client per case.

The diagnostic proved the read works on the FIRST faithful full-replay against a fresh client but NOT on a
2nd replay against the same client (the warm form-cache returns a reduced data-load so the dynlist row data
isn't materialized → the read echoes without a value). So generalization must be tested cold: boot a fresh
client, run ONE `read_list_column_replay`, stop. This boots once PER case.

Cases (each cold): verbatim Товары/Наименование→«Обувь» · column-rt Товары/Код→«000000001» ·
list-rt Контрагенты/Наименование · list-rt Валюты/Наименование.

    .venv/bin/python tools/protocol-research/dynlist_read_freshcase_probe.py [port]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol.native_write import derive_read_list_column, read_list_column_replay  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card98-listform-read"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 15381

CASES = [
    ("verbatim ", "e1cib/list/Справочник.Товары", "Наименование", "Обувь"),
    ("column-rt", "e1cib/list/Справочник.Товары", "Код", "000000001"),
    ("list-rt-К", "e1cib/list/Справочник.Контрагенты", "Наименование", None),
    ("list-rt-В", "e1cib/list/Справочник.Валюты", "Наименование", None),
]


def one(link: str, col: str) -> object:
    """Boot a fresh client, run a single cold replay, stop."""
    r = srv.launch_test_client(port=PORT, manage_apache=(PORT == 15381), display="auto", wait_sec=180.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    try:
        template = derive_read_list_column(CAP)
        out = read_list_column_replay(template, open_link=link, column=col, port=PORT)
        return out["value"]
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=(PORT == 15381))


def main() -> int:
    results = []
    for label, link, col, expect in CASES:
        try:
            val = one(link, col)
        except Exception as exc:  # noqa: BLE001
            val = f"<error: {exc}>"
        ok = (val == expect) if expect is not None else (val is not None and not str(val).startswith("<error"))
        exp = f"== {expect!r}" if expect is not None else "(non-None)"
        print(f"[{'PASS' if ok else '----'}] {label}  {link.split('.')[-1]:14s} {col:14s} -> {val!r:24} {exp}")
        results.append(ok)
    passed = sum(1 for x in results if x)
    print(f"\n{passed}/{len(results)} cold cases passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
