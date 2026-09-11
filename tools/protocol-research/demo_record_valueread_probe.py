#!/usr/bin/env python3
"""Card 98 change-5 follow-up — navigated RECORD value-read on the demo БСП. Lists have 0 Group.EditField and the
fixture DataProcessor opened by nav-link returns only its command bar; a real catalog RECORD form has
Group.EditField (Наименование/Код/…). Try several demo record/edit nav-links and report, per link: opened /
element_count / EditField names in the tree / form-field VALUES. Any link that yields Group.EditField VALUES
verifies the navigated value-read end-to-end.

    .venv/bin/python tools/protocol-research/demo_record_valueread_probe.py [link ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import launch_test_client, read_form_descriptor, stop_test_client  # noqa: E402

IB = "/opt/1c-dev/demo_1_0_41_3"
PORT = 15382
LINKS = sys.argv[1:] or [
    "e1cib/data/Справочник.Валюты",
    "e1cib/data/Справочник.ФизическиeЛица",
    "e1cib/data/Справочник.Пользователи",
    "e1cib/data/Справочник.Организации",
]


def main() -> int:
    r = launch_test_client(infobase_path=IB, port=PORT, user="Администратор", kind="thick",
                           display="auto", manage_apache=False, wait_sec=150.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched demo pid={pid} listening={r.get('listening')}")
    rc = 1
    try:
        for link in LINKS:
            print(f"\n=== {link} ===")
            try:
                d = read_form_descriptor(port=PORT, open_link=link, gherkin=False)
            except Exception as e:  # noqa: BLE001
                print(f"  EXCEPTION: {type(e).__name__}: {e}")
                continue
            edits = [e["name"] for e in d.get("elements", []) if e.get("kind") == "EditField"]
            print(f"  opened={d.get('opened')!r} elements={d.get('element_count')} "
                  f"EditFields={len(edits)} form-field VALUES={d.get('field_count')}")
            print(f"  EditField names: {edits[:14]}")
            if d.get("field_count"):
                print(f"  VALUES: {json.dumps(d.get('fields', {}), ensure_ascii=False)[:600]}")
                print("  ⇒ NAVIGATED RECORD VALUE-READ PASS")
                rc = 0
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=False)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
