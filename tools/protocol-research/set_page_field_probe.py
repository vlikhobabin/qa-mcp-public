#!/usr/bin/env python3
"""Card 90 — capture-free PAGE-FIELD input, verified by read-back (ASCII).

A page field is a plain `EditField` nested deeper in the element path (a tab-page Group):
`…Group[PF_GROUP_MAIN].Group[PF_PAGES_MAIN].Group[PF_PAGE_A].EditField[PF_PAGE_A_FIELD]`. Once made editable
(fixture fix 2026-06-17), it commits via the SAME string-SET + focus-change as any field — so it reuses the
existing `write_form_value` with a genuine page-field capture (base==target → the nested path is replayed
as-is; no leaf retarget needed). This proves qa-mcp can input into a field on a tab page, capture-free.

    uv run --frozen python tools/protocol-research/set_page_field_probe.py [port] [capture_dir]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.native_write import NativeWriteSession, derive_write_template  # noqa: E402

DEFAULT_CAP = REPO / "runtime/protocol-research/captures/genuine-card90-pagefield-20260617/traffic-selfcontained"
FIELD = "PF_PAGE_A_FIELD"
CAPTURED = "PGFLDA"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    cap = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CAP
    t = derive_write_template(cap, FIELD, CAPTURED)
    print(f"field={t.field} setup_end={t.setup_end} write_block={t.write_block} read_frames={t.read_frames}")
    results: dict[str, str | None] = {}
    # open the form ONCE, write many (a fresh client accepts one manager session — re-opening desyncs)
    with NativeWriteSession(t, port=port) as s:
        for val in ("PGNEW1", "PGNEW2"):
            r = s.write(val)  # field defaults to the template's PF_PAGE_A_FIELD (the nested page path)
            results[val] = r.get("readback_value")
            ok = bool(r.get("committed"))
            print(f"  write {FIELD}={val!r}: readback={r.get('readback_value')!r} committed={ok}  {'OK' if ok else 'FAIL'}")
    ok = all(results[v] == v for v in results)
    print("RESULT:", "PASS — capture-free page-field input commits" if ok else "INCONCLUSIVE")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
