#!/usr/bin/env python3
"""Card 90 decode pass 2 — confirm checkbox = activate/click (no value SET) vs string = value SET.

(1) Prove the SET-tag detector works: show the PF_EDIT_STRING 'C90STR' value-SET frame (should carry
    e0418181ba + the 'C90STR' bytes).
(2) Dump a full PF_CHECKBOX_FALSE frame head+tail and compare its shape to the string SET frame and to a
    plain activate/focus frame, to confirm the checkbox carries NO value buffer.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CAP = REPO / "runtime/protocol-research/captures/genuine-card90-20260617/traffic/traffic.jsonl"
SET_TAG = bytes.fromhex("e0418181ba")


def ascii(b: bytes) -> str:
    return "".join(chr(c) if 32 <= c < 127 else "." for c in b)


def show(label, payload, idx):
    print(f"\n=== {label} chunk#{idx} len={len(payload)} ===")
    print(f"  head[0:24]  {payload[:24].hex()}")
    print(f"  tail[-20:]  {payload[-20:].hex()}  ascii {ascii(payload[-20:])}")
    sp = payload.find(SET_TAG)
    if sp >= 0:
        print(f"  SET tag @ {sp}: {payload[sp:sp+48].hex()}")
        print(f"            ascii {ascii(payload[sp:sp+48])}")
    else:
        print("  NO SET tag")


def main():
    chunks = []
    with CAP.open() as f:
        for line in f:
            r = json.loads(line)
            chunks.append((r["direction"], base64.b64decode(r["payload_b64"])))
    m2c = [(i, p) for i, (d, p) in enumerate(chunks) if d == "manager_to_client"]

    # (1) string value SET for C90STR
    print("######## STRING value-SET frames carrying 'C90STR' ########")
    for i, p in m2c:
        if b"C90STR" in p:
            show("C90STR", p, i)
    print(f"\n  total m2c frames with SET tag e0418181ba: {sum(1 for _, p in m2c if SET_TAG in p)}")
    print(f"  total m2c frames with 'Истина'/'Ложь' utf?  checking literal bytes...")
    for needle in (b"\xc8\xf1\xf2\xe8\xed\xe0", "Истина".encode("utf-16-le"), "Ложь".encode("utf-16-le")):
        print(f"    needle {needle.hex()}: {sum(1 for _, p in m2c if needle in p)} frames")

    # (2) one checkbox FALSE frame full
    print("\n######## CHECKBOX frames (full head+tail) ########")
    shown = 0
    for i, p in m2c:
        if b"PF_CHECKBOX_FALSE" in p and shown < 3:
            show("PF_CHECKBOX_FALSE", p, i); shown += 1


if __name__ == "__main__":
    main()
