#!/usr/bin/env python3
"""Card 98 — generalize the faithful-full-replay dynlist read across columns + lists (no Vanessa).

Boots ONE native TestClient against vanessa_client, then runs `read_list_column_replay` for several cases
(each a fresh socket / faithful full-stream replay of `genuine-card98-listform-read` with the nav-link +
column retargeted). Confirms the mechanism generalizes beyond the verbatim Товары/Наименование→«Обувь» case:
  - verbatim:        Товары / Наименование  -> expect «Обувь»          (regression of the proven case)
  - column retarget: Товары / Код           -> expect «000000001»       (different column, same list)
  - list retarget:   Контрагенты / Наименование                        (different list)
  - list retarget:   Валюты / Наименование                             (different list)

    .venv/bin/python tools/protocol-research/dynlist_read_generalize_probe.py [port]
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
    ("verbatim   ", "e1cib/list/Справочник.Товары", "Наименование", "Обувь"),
    ("column-rt   ", "e1cib/list/Справочник.Товары", "Код", "000000001"),
    ("list-rt Контр", "e1cib/list/Справочник.Контрагенты", "Наименование", None),
    ("list-rt Валюты", "e1cib/list/Справочник.Валюты", "Наименование", None),
]


def main() -> int:
    r = srv.launch_test_client(port=PORT, manage_apache=(PORT == 15381), display="auto", wait_sec=180.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} listening={r.get('listening')}\n")
    template = derive_read_list_column(CAP)
    print(f"template: {template.nav_link} / {template.column} (captured «{template.captured_value}»)\n")
    results = []
    try:
        for label, link, col, expect in CASES:
            try:
                out = read_list_column_replay(template, open_link=link, column=col, port=PORT)
                val = out["value"]
            except Exception as exc:  # noqa: BLE001 — probe: report, keep going
                val = f"<error: {exc}>"
            ok = (val == expect) if expect is not None else (val is not None and not str(val).startswith("<error"))
            verdict = "PASS" if ok else "----"
            exp = f"== {expect!r}" if expect is not None else "(non-None)"
            print(f"  [{verdict}] {label}  {link.split('.')[-1]:14s} {col:14s} -> {val!r:24} {exp}")
            results.append(ok)
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=(PORT == 15381))
    passed = sum(1 for x in results if x)
    print(f"\n{passed}/{len(results)} cases passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
