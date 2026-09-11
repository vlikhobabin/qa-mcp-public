#!/usr/bin/env python3
"""Card 96 / E2 — capture-free reference selection live-verify (no Vanessa).

A CatalogRef InputField resolves a TYPED name to a ref (выбор по строке) on focus-change. Decode: the typed
name is carried as `e0 41 81 81 b7 <char-count><utf-16le name><space pad>` (the value-SET family with a UTF-16
choice value). set_reference_field faithfully replays the genuine reference-input session (open form → type the
name into the field → focus-change commit → read-back), re-targeting the UTF-16 name to ``value`` — a valid
catalog element NAME (e.g. "Пантера АО"). Commit is confirmed by the resolved presentation reading back.

    PYTHONPATH=src python3 tools/protocol-research/set_reference_field_probe.py [port] [capture_dir] [value]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.native_write import derive_set_reference_field, set_reference_field  # noqa: E402

DEFAULT_CAP = REPO / "runtime/protocol-research/captures/genuine-card96-ref-20260618/traffic"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    cap = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CAP
    value = sys.argv[3] if len(sys.argv) > 3 else "Пантера АО"
    t = derive_set_reference_field(cap)
    print(f"capture={cap.name} field={t.field} captured={t.captured_value!r} -> value={value!r}")
    r = set_reference_field(t, value, port=port)
    print(f"  set {t.field}={value!r}: committed={r['committed']} (presentation read back)")
    ok = bool(r["committed"])
    print("RESULT:", f"PASS — capture-free reference set ({value})" if ok else "INCONCLUSIVE")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
