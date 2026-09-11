#!/usr/bin/env python3
"""Card 97 change 4 — dynamic-list SEARCH-STRING decode: locate the genuine search-string SET frames in the
dynlist-search capture and dump the element path (the SearchStringAddition leaf) + the value buffer + the
surrounding tag bytes, so we can see how the dynlist search command rides the wire and how to retarget it.

Search strings input by the capture feature: 'Молоко' then 'Творог' (into ДенамическийСписокИерархияСтрокаПоиска).
Run: python3 card97_dynlist_search_decode.py [traffic.jsonl]
"""
import base64
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from qa_mcp.protocol.element_ref import extract_element_paths  # noqa: E402

DEFAULT = REPO / "runtime/protocol-research/captures/genuine-card97-ch4-search-20260619/traffic.jsonl"
SET_TAG = bytes.fromhex("e0418181ba")          # value-SET tag (string/number/date/table-cell)
ACT_TAG = bytes.fromhex("e04b")                # activate-with-action family (checkbox/choice/window-cmd)
VALUES = ["Молоко", "Творог"]


def load(path):
    rows = []
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        d["payload"] = base64.b64decode(d["payload_b64"])
        rows.append(d)
    return rows


def hexwin(buf, idx, before=28, after=56):
    a = max(0, idx - before)
    b = min(len(buf), idx + after)
    return buf[a:b].hex(" ")


def main(argv):
    path = argv[0] if argv else DEFAULT
    rows = load(path)
    m2c = [r for r in rows if r["direction"] == "manager_to_client"]
    print(f"loaded {len(rows)} chunks ({len(m2c)} manager->client)\n")

    for val in VALUES:
        needle_u16 = val.encode("utf-16-le")
        needle_u8 = val.encode("utf-8")
        print(f"===== value {val!r} (u16={needle_u16.hex()}) =====")
        for i, r in enumerate(m2c):
            buf = r["payload"]
            pos = buf.find(needle_u16); enc = "utf16le"
            if pos < 0:
                pos = buf.find(needle_u8); enc = "utf8" if pos >= 0 else None
            if pos < 0:
                continue
            print(f"  m2c#{i} chunk#{r.get('chunk_no')} bytes={r.get('byte_count')} valpos={pos} enc={enc}")
            for p in extract_element_paths(buf):
                print(f"     path: {p}")
            for m in re.finditer(re.escape(SET_TAG), buf):
                print(f"     SET@{m.start()} : {hexwin(buf, m.start())}")
            for m in re.finditer(re.escape(ACT_TAG), buf):
                print(f"     ACT@{m.start()} : {hexwin(buf, m.start())}")
            print(f"     VAL@{pos} : {hexwin(buf, pos, 40, 28)}")
            print()


if __name__ == "__main__":
    main(sys.argv[1:])
