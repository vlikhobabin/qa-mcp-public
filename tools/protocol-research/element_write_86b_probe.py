#!/usr/bin/env python3
"""Card 86b — live proof of capture-free WRITE addressing, on ONE NativeWriteSession (open-once).

A single session (avoids the cross-session persistent-form desync from card 80) writes to several fields by
re-targeting the element path leaf off the PF_EDIT_STRING capture template — no per-field capture:
  1) PF_EDIT_STRING  (baseline, same type as the template)        -> expect commit
  2) PF_EDIT_NUMBER  (capture-free, DIFFERENT field, number type)  -> commit iff a string-SET suits a number
  3) PF_EDIT_STRING  (again)                                       -> confirms the session stayed healthy
  4) PF_EDIT_READONLY (negative control: addressed but read-only)  -> expect NO commit

    uv run --frozen python tools/protocol-research/element_write_86b_probe.py [port]
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.native_write import NativeWriteSession, derive_write_template  # noqa: E402

CAPTURE = REPO / "runtime/protocol-research/captures/genuine-commit-conn"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    t = derive_write_template(CAPTURE, "PF_EDIT_STRING", "QAGENUINE2026", "PF_EDIT_STRING_VALUE")
    plan = [
        ("PF_EDIT_STRING", "QA86B_AAA", True),
        ("PF_EDIT_NUMBER", "777", None),       # unknown: does a string-SET commit on a number field?
        ("PF_EDIT_STRING", "QA86B_BBB", True),  # session-health check after the number write
        ("PF_EDIT_READONLY", "SHOULDNT", False),
    ]
    print(f"== capture-free WRITE addressing on ONE session, port {port} ==")
    with NativeWriteSession(t, host="127.0.0.1", port=port) as s:
        for field, value, expect in plan:
            r = s.write(value, field=field)
            verdict = "" if expect is None else ("  OK" if bool(r["committed"]) == expect else "  UNEXPECTED")
            print(f"  write {field:<18} = {value!r:<14} committed={r['committed']!s:<5} "
                  f"readback={r['readback_value']!r}{verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
