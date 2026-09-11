#!/usr/bin/env python3
"""Card 90 table-cell decode: locate the genuine cell-SET frames in the self-contained table capture
and extract the table-cell element path + value buffer, comparing to a plain-field SET.

Cell values input by the capture feature: CELLAA then CELLBB (both into PF_TABLE_TEXT).
Run: python3 card90_table_decode.py [traffic.jsonl]
"""
import base64
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from qa_mcp.protocol.element_ref import extract_element_paths  # noqa: E402

DEFAULT = REPO / "runtime/protocol-research/captures/genuine-card90-table-20260617/traffic-selfcontained/traffic.jsonl"
SET_TAG = bytes.fromhex("e0418181ba")          # value-SET tag
ACT_TAG = bytes.fromhex("e04b")                # activate-with-action family (checkbox/choice)
VALUES = [b"CELLAA", b"CELLBB"]


def load(path):
    rows = []
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        d["payload"] = base64.b64decode(d["payload_b64"])
        rows.append(d)
    return rows


def hexwin(buf, idx, before=24, after=48):
    a = max(0, idx - before)
    b = min(len(buf), idx + after)
    return buf[a:b].hex(" ")


def main(argv):
    path = argv[0] if argv else DEFAULT
    rows = load(path)
    m2c = [r for r in rows if r["direction"] == "manager_to_client"]
    print(f"loaded {len(rows)} chunks ({len(m2c)} manager->client)\n")

    # 1) Find chunks carrying the cell values.
    for val in VALUES:
        print(f"===== value {val!r} =====")
        for r in m2c:
            buf = r["payload"]
            pos = buf.find(val)
            if pos < 0:
                # value may be UTF-16LE for table cells; check that too
                pos = buf.find(val.decode().encode("utf-16-le"))
                enc = "utf16le" if pos >= 0 else None
            else:
                enc = "latin1/ascii"
            if pos < 0:
                continue
            print(f"  chunk#{r['chunk_no']} bytes={r['byte_count']} valpos={pos} enc={enc}")
            # element paths in this frame
            paths = extract_element_paths(buf)
            for p in paths:
                print(f"     path: {p}")
            # SET tag occurrences
            for m in re.finditer(re.escape(SET_TAG), buf):
                print(f"     SET@{m.start()} : {hexwin(buf, m.start())}")
            # value window
            print(f"     VAL@{pos} : {hexwin(buf, pos, 36, 24)}")
            print()


if __name__ == "__main__":
    main(sys.argv[1:])
