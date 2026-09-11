#!/usr/bin/env python3
"""Card 99 change-1 — decode the 1C e1cib ref byte/text encoding from genuine captures (offline, no boot).
Search capture payloads for known OData Ref_Key GUIDs in every plausible encoding, so the navigated-record
``?ref=`` link can be built with the proven encoding (not guessed).

    python3 tools/protocol-research/ref_encoding_decode.py
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CAPROOT = REPO / "runtime/protocol-research/captures"

# (label, GUID) candidates likely referenced by the open-card / ref captures (vanessa_client OData).
KNOWN = [
    ("Товары/Обувь(grp)", "bbb079ae-8c51-11db-a9b0-00055d49b45e"),
    ("Товары/Продукты(grp)", "87f1c226-9679-11db-a9b2-00055d49b45e"),
    ("Товары/Услуги(grp)", "a7a30aae-321b-11dd-8d3a-000d8843cd1b"),
    ("Товары/Доставка", "a7a30aaf-321b-11dd-8d3a-000d8843cd1b"),
    ("Товары/Электротовары(grp)", "e844ecac-9743-11db-a9b2-00055d49b45e"),
    ("Контр/КорнетЗАО", "086715b0-f348-11db-a9c5-00055d49b45e"),
    ("Контр/ПантераАО", "d1cb82a7-8e8b-11db-a9b0-00055d49b45e"),
]

CAPS = [
    "genuine-card96-opencard-20260618",
    "genuine-card96-ref-20260618",
    "genuine-card96-activate-20260618",
]


def encodings(guid: str) -> list[tuple[str, bytes]]:
    h = guid.replace("-", "")
    b = bytes.fromhex(h)
    h1, h2 = h[:16], h[16:]
    # .NET Guid ToByteArray: first 3 groups little-endian, last 2 as-is
    le = bytes([b[3], b[2], b[1], b[0], b[5], b[4], b[7], b[6]]) + b[8:]
    out = [
        ("ascii-dashed", guid.encode("latin1")),
        ("ascii-nodash", h.encode("latin1")),
        ("ascii-halfswap", (h2 + h1).encode("latin1")),
        ("ascii-dashed-UPPER", guid.upper().encode("latin1")),
        ("bin-straight", b),
        ("bin-halfswap", b[8:] + b[:8]),
        ("bin-dotnet-le", le),
        ("bin-dotnet-le-halfswap", le[8:] + le[:8]),
        ("bin-reversed", b[::-1]),
    ]
    return out


def load_payloads(cap: str) -> list[tuple[str, int, bytes]]:
    p = CAPROOT / cap / "traffic" / "traffic.jsonl"
    if not p.is_file():
        return []
    rows = []
    with open(p) as f:
        for line in f:
            try:
                d = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            if d.get("event") != "chunk":
                continue
            rows.append((d.get("direction", "?"), d.get("chunk_no", -1),
                         base64.b64decode(d.get("payload_b64", ""))))
    return rows


def main() -> int:
    any_hit = False
    for cap in CAPS:
        rows = load_payloads(cap)
        if not rows:
            print(f"[skip] {cap} (no traffic)")
            continue
        blob = b"".join(p for _, _, p in rows)
        print(f"\n===== {cap} ({len(rows)} chunks, {len(blob)} bytes) =====")
        for label, guid in KNOWN:
            for enc_name, needle in encodings(guid):
                idx = blob.find(needle)
                if idx >= 0:
                    any_hit = True
                    ctx = blob[max(0, idx - 8): idx + len(needle) + 8]
                    print(f"  HIT {label:24s} enc={enc_name:22s} @{idx} ctx={ctx.hex()}")
    if not any_hit:
        print("\n(no GUID hits in any encoding — refs may be name-resolved only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
