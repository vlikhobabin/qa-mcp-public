#!/usr/bin/env python3
"""Card 98 change-5 follow-up — navigated-form VALUE read: open a form WITH Group.EditField fields by nav-link
(config-agnostic) and read its field VALUES (not just structure). The fixture DataProcessor
(Обработка.ФикстураПротоколаTestClient, defaultForm Форма, useStandardCommands=true) has the known PF_* EditFields
with known values — the controlled oracle for a navigated value-read. Tries several nav-links and reports, for
each, opened / element_count / field_count + the field VALUES + sample EditField element names.

    .venv/bin/python tools/protocol-research/navigated_record_valueread_probe.py [port] [link ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import launch_test_client, read_form_descriptor, stop_test_client  # noqa: E402

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
LINKS = sys.argv[2:] or [
    "e1cib/data/Обработка.ФикстураПротоколаTestClient",
    "e1cib/data/Обработка.ФикстураПротоколаTestClient.Форма",
]


def main() -> int:
    r = launch_test_client(port=PORT, manage_apache=(PORT == 15381), display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} port={PORT}")
    rc = 1
    try:
        for link in LINKS:
            print(f"\n=== open_link={link} ===")
            try:
                d = read_form_descriptor(port=PORT, open_link=link, gherkin=False)
            except Exception as e:  # noqa: BLE001
                print(f"  EXCEPTION: {type(e).__name__}: {e}")
                continue
            edits = [e for e in d.get("elements", []) if e.get("kind") == "EditField"]
            print(f"  opened={d.get('opened')!r} elements={d.get('element_count')} "
                  f"EditFields={len(edits)} field_VALUES={d.get('field_count')}")
            print(f"  EditField names: {[e['name'] for e in edits[:12]]}")
            if d.get("field_count"):
                print(f"  VALUES: {json.dumps(d.get('fields', {}), ensure_ascii=False)[:600]}")
                print("  ⇒ NAVIGATED VALUE-READ PASS (a navigated form's field VALUES read capture-free)")
                rc = 0
            else:
                print("  (0 field VALUES — list/no-Group.EditField, or value-read returned empty)")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=(PORT == 15381))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
