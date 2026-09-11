#!/usr/bin/env python3
"""Card 99 change-1 — POPULATED navigated-record value-read, end-to-end through the SHIPPED ``read_record`` MCP
tool. Opens an EXISTING populated catalog RECORD capture-free by its reference (the natural dashed OData
``Ref_Key`` — the tool auto-encodes it to the proven e1cib ``?ref=`` hex) and value-reads its object attributes,
then compares against an OData oracle captured offline BEFORE the client boots (the native client stops
Apache/OData while it runs).

    .venv/bin/python tools/protocol-research/populated_record_valueread_probe.py [port]

Writes an evidence JSON under evidence/card99-populated-record-valueread-2026-06-20/ when run on the default lab.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import launch_test_client, read_record, stop_test_client  # noqa: E402

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
EVID = REPO / "evidence" / "card99-populated-record-valueread-2026-06-20"

# Oracle captured offline from OData (vanessa_client) — test data, not secret. ``ref`` is the dashed Ref_Key;
# ``read_record`` auto-encodes it (proves the natural caller surface). ORDER matters by the cold-client boundary:
# the small group form «Покупатели» reads cold AND warms the client process; the large 80-element «Доставка»
# item form then reads its 12 attribute values on the now-warm process.
RECORDS = [
    {
        "label": "Контрагенты/Покупатели (group form — reads cold, warms the client)",
        "type": "Справочник.Контрагенты",
        "ref": "9d5c422d-8c4c-11db-a9b0-00055d49b45e",
        "oracle": {"Наименование": "Покупатели", "Код": "000000002"},
    },
    {
        "label": "Товары/Доставка (large item form — 12 attributes on the warm client)",
        "type": "Справочник.Товары",
        "ref": "a7a30aaf-321b-11dd-8d3a-000d8843cd1b",
        "oracle": {"Наименование": "Доставка", "Код": "000000037", "Вид": "Услуга", "Родитель": "Услуги"},
    },
]


def main() -> int:
    r = launch_test_client(port=PORT, manage_apache=(PORT == 15381), display="auto", wait_sec=150.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} port={PORT}")
    results = []
    all_pass = True
    try:
        for rec in RECORDS:
            print(f"\n########## {rec['label']} ##########")
            try:
                d = read_record(record_type=rec["type"], ref=rec["ref"], port=PORT, gherkin=False)
            except Exception as e:  # noqa: BLE001
                print(f"    EXCEPTION: {type(e).__name__}: {e}")
                results.append({**rec, "error": f"{type(e).__name__}: {e}"})
                continue
            fields = d.get("fields", {})
            matched = {k: v for k, v in rec["oracle"].items() if fields.get(k) == v and v}
            print(f"    open_link={d.get('open_link')}")
            print(f"    opened={d.get('opened')!r} elements={d.get('element_count')} field_VALUES={d.get('field_count')}")
            print(f"    VALUES: {json.dumps(fields, ensure_ascii=False)[:500]}")
            print(f"    oracle_matched: {json.dumps(matched, ensure_ascii=False)}  (of {json.dumps(rec['oracle'], ensure_ascii=False)})")
            ok = bool(matched)
            print("    ⇒ " + ("✅ PASS" if ok else "✗ no oracle match"))
            if not ok:
                all_pass = False
            results.append({"label": rec["label"], "type": rec["type"], "ref": rec["ref"],
                            "open_link": d.get("open_link"), "opened": d.get("opened"),
                            "field_count": d.get("field_count"), "fields": fields,
                            "oracle": rec["oracle"], "oracle_matched": matched, "pass": ok})
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=(PORT == 15381))
    rc = 0 if (all_pass and results) else 1
    if PORT == 15381:
        EVID.mkdir(parents=True, exist_ok=True)
        (EVID / "read_record_run.json").write_text(
            json.dumps({"port": PORT, "infobase": "vanessa_client", "all_pass": all_pass, "results": results},
                       ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nevidence → {EVID / 'read_record_run.json'}")
    print(f"\nRESULT: {'PASS' if rc == 0 else 'INCONCLUSIVE'}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
