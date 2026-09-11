#!/usr/bin/env python3
"""Card 97 change 3 — report / ТабличныйДокумент decode: find the spreadsheet cell markers (PF_RPT_R1C1 …)
in the PF_RUN_REPORT click response and dump how the spreadsheet content rides the wire (manager->client), so
we can decode the spreadsheet read.

Run: python3 card97_report_decode.py [traffic.jsonl]
"""
import base64
import json
import sys
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[2] / "runtime/protocol-research/captures/genuine-card97-ch3-report-20260619/traffic.jsonl"
CELLS = ["PF_RPT_R1C1", "PF_RPT_R1C2", "PF_RPT_R2C1", "PF_RPT_R2C2"]


def load(path):
    rows = []
    for line in Path(path).read_text().splitlines():
        if line.strip():
            d = json.loads(line)
            d["payload"] = base64.b64decode(d["payload_b64"])
            rows.append(d)
    return rows


def hexwin(buf, idx, before=24, after=64):
    a = max(0, idx - before); b = min(len(buf), idx + after)
    return buf[a:b].hex(" ")


def main(argv):
    path = argv[0] if argv else DEFAULT
    rows = load(path)
    m2c = [r for r in rows if r["direction"] == "manager_to_client"]
    print(f"{len(rows)} chunks ({len(m2c)} manager->client)\n")
    for cell in CELLS:
        u16 = cell.encode("utf-16-le"); u8 = cell.encode("utf-8")
        for i, r in enumerate(m2c):
            b = r["payload"]
            pos = b.find(u16); enc = "utf16le"
            if pos < 0:
                pos = b.find(u8); enc = "utf8" if pos >= 0 else None
            if pos < 0:
                continue
            print(f"{cell:14s} m2c#{i:2d} bytes={r['byte_count']:5d} pos={pos} enc={enc}")
            print(f"   {hexwin(b, pos, 16, 40)}")
    # which frame carries the most cells (the spreadsheet payload frame)
    print("\n=== cells per frame ===")
    for i, r in enumerate(m2c):
        b = r["payload"]
        hits = [c for c in CELLS if c.encode("utf-16-le") in b or c.encode("utf-8") in b]
        if hits:
            print(f"  m2c#{i:2d} bytes={r['byte_count']:5d} cells={hits}")


if __name__ == "__main__":
    main(sys.argv[1:])
