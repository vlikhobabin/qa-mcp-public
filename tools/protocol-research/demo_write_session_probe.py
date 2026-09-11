#!/usr/bin/env python3
"""Card 98 gate — demo_1_0_41_3 WRITE via the SHIPPED NativeWriteSession path (what the MCP write_form_value
tool uses): opens the form via the setup prefix, then write() re-sends activate+SET+focus-change with the
per-frame sequence counter bumped (_set_seq) + read-back. Same as the MCP tool, on a foreign Cyrillic field.

    PYTHONPATH=src python3 tools/protocol-research/demo_write_session_probe.py [port] [new_value]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.native_write import NativeWriteSession, derive_write_template  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card98-demo-write"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15392
    new_value = sys.argv[2] if len(sys.argv) > 2 else "ZZGATEOK26"
    template = derive_write_template(CAP, "Наименование", "QADEMO2026", default_value="")
    print(f"NativeWriteSession write field='Наименование' new={new_value!r} "
          f"setup_end={template.setup_end} write_block={template.write_block}")
    with NativeWriteSession(template, host="127.0.0.1", port=port) as sess:
        result = sess.write(new_value, field="Наименование")
    for k, v in result.items():
        print(f"  {k}={v!r}")
    ok = bool(result.get("committed"))
    print("RESULT:", "COMMITTED (shipped NativeWriteSession path)" if ok
          else f"NOT committed (echo={result.get('set_response_echoes_new')})")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
