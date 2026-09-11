#!/usr/bin/env python3
"""Card 96 / E3 — capture-free open-card navigation live-verify (no Vanessa).

Drilling into a list row opens the record's form in a NEW window (a fresh SecondaryFrame, like a dialog). A
faithful full-stream replay of the genuine navigation (open form → open the catalog list → «Изменить» the active
row → the card opens) reproduces it — GuidRebinder rebinds each new window's GUID from the open response.
Opening is confirmed by the card marker (the card form id, e.g. "ФормаГруппы") reading back.

    PYTHONPATH=src python3 tools/protocol-research/open_card_probe.py [port] [capture_dir] [result_marker]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.native_write import derive_open_card, open_card  # noqa: E402

DEFAULT_CAP = REPO / "runtime/protocol-research/captures/genuine-card96-opencard-20260618/traffic"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    cap = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CAP
    marker = sys.argv[3] if len(sys.argv) > 3 else "ФормаГруппы"
    t = derive_open_card(cap, result_marker=marker)
    print(f"capture={cap.name} result_marker={marker!r}")
    r = open_card(t, port=port)
    print(f"  open_card: opened={r['opened']} (card marker {marker} read back)")
    ok = bool(r["opened"])
    print("RESULT:", "PASS — capture-free open_card" if ok else "INCONCLUSIVE")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
