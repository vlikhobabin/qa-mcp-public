#!/usr/bin/env python3
"""Card 90 decode — locate and dissect the genuine Boolean (checkbox) SET frames.

Capture: runtime/protocol-research/captures/genuine-card90-20260617 (action-only, single
manager<->client connection). The feature set PF_CHECKBOX_FALSE (->Да/true) and cleared
PF_CHECKBOX_TRUE (->Нет/false). We find the manager->client frames carrying each checkbox
element path and dump the bytes around the path + the e0/41 SET tag so we can see the
boolean value buffer (true vs false) and compare it to the string/number SET law.

    python3 tools/protocol-research/card90_checkbox_decode.py
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CAP = REPO / "runtime/protocol-research/captures/genuine-card90-20260617/traffic/traffic.jsonl"

NAMES = [b"PF_CHECKBOX_FALSE", b"PF_CHECKBOX_TRUE", b"PF_EDIT_STRING", b"PF_CHOICE_MODE", b"PF_TABLE"]
SET_TAG = bytes.fromhex("e0418181ba")  # the per-type SET tag (type-identical across types)


def ascii(b: bytes) -> str:
    return "".join(chr(c) if 32 <= c < 127 else "." for c in b)


def dump(label: str, payload: bytes, idx: int) -> None:
    name = next((n for n in NAMES if n in payload), None)
    pos = payload.find(name) if name else -1
    print(f"\n=== {label} chunk#{idx} len={len(payload)} name={name.decode() if name else None}@{pos} ===")
    if pos >= 0:
        # 0x9a length-prefixed path marker usually precedes the path; show a window before+after the name
        lo = max(0, pos - 48)
        hi = min(len(payload), pos + len(name) + 24)
        seg = payload[lo:hi]
        print(f"  path window [{lo}:{hi}]:")
        print(f"    hex   {seg.hex()}")
        print(f"    ascii {ascii(seg)}")
    sp = payload.find(SET_TAG)
    if sp >= 0:
        seg = payload[sp:sp + 40]
        print(f"  SET tag @ {sp}: {seg.hex()}")
        print(f"           ascii {ascii(seg)}")
    else:
        print("  (no e0418181ba SET tag in this frame)")


def main() -> int:
    chunks = []
    with CAP.open() as f:
        for line in f:
            r = json.loads(line)
            chunks.append((r["direction"], base64.b64decode(r["payload_b64"])))
    m2c = [(i, p) for i, (d, p) in enumerate(chunks) if d == "manager_to_client"]
    print(f"loaded {len(chunks)} chunks; {len(m2c)} manager->client")

    for target in (b"PF_CHECKBOX_FALSE", b"PF_CHECKBOX_TRUE"):
        hits = [(i, p) for i, p in m2c if target in p]
        print(f"\n######## {target.decode()}: {len(hits)} manager->client frames ########")
        for i, p in hits[:6]:
            dump(target.decode(), p, i)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
