#!/usr/bin/env python3
"""Card 99 #2 path B — introspect a REAL document form (Документ.Заказ) opened config-agnostically by the native
client: dump its element tree (tabular-section Table + its columns), and try a config-agnostic tabular-cell read.
Foundation for config-agnostic date-cell ACTIVATION on a non-fixture form.

    .venv/bin/python tools/protocol-research/document_form_introspect_probe.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import launch_test_client, read_form_descriptor, read_table_cell, stop_test_client  # noqa: E402
from qa_mcp.protocol.navigation import e1cib_data_link  # noqa: E402

# Документ.Заказ №000000001 (vanessa_client), with a «Товары» tabular section.
ORDER_REF = "0faf2b04-fc04-11e1-bbef-0050ba5c8877"
LINK = e1cib_data_link("Документ.Заказ", ORDER_REF)


def main() -> int:
    print(f"open_link = {LINK}")
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid}")
    try:
        d = read_form_descriptor(port=15381, open_link=LINK, gherkin=False)
        els = d.get("elements", [])
        print(f"opened={d.get('opened')!r} element_count={d.get('element_count')}")
        kinds: dict[str, int] = {}
        for e in els:
            kinds[e.get("kind", "?")] = kinds.get(e.get("kind", "?"), 0) + 1
        print(f"element kinds: {kinds}")
        tables = [e for e in els if e.get("kind") == "Table"]
        print(f"tables: {[t.get('name') for t in tables]}")
        # columns = EditFields that sit under a Table in the tree (best-effort by name proximity)
        cols = [e.get("name") for e in els if e.get("kind") == "EditField"]
        print(f"EditField leaves ({len(cols)}): {cols[:40]}")
        # try a config-agnostic tabular-cell read on the «Товары» table (current/first row)
        for tbl in [t.get("name") for t in tables] or ["Товары"]:
            for col in cols[:6]:
                try:
                    rc = read_table_cell(table=tbl, column=col, port=15381, open_link=LINK)
                    if rc.get("value") is not None:
                        print(f"  read_table_cell({tbl},{col}) -> {rc.get('value')!r}  groups={rc.get('groups')}")
                except Exception as e:  # noqa: BLE001
                    print(f"  read_table_cell({tbl},{col}) EXC {type(e).__name__}: {e}")
        (REPO / "runtime/protocol-research").mkdir(parents=True, exist_ok=True)
        (REPO / "runtime/protocol-research/zakaz_descriptor.json").write_text(
            json.dumps({"opened": d.get("opened"), "element_count": d.get("element_count"),
                        "elements": els}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("descriptor saved -> runtime/protocol-research/zakaz_descriptor.json")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
