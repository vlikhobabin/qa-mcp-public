#!/usr/bin/env python3
"""Card 86a — live proof of capture-free element addressing (READ side, safe / no mutation).

Uses the PROVEN capture-replay read path (the one `native_write` uses live): replay the genuine
`genuine-commit-conn` setup to open the form, then issue a value-read for ARBITRARY fields by RE-TARGETING
the element-address path leaf (same group) in a captured PF_EDIT_STRING value-read frame — NO capture
authored for the target field. Proof: the response realizes value-mode for the field WE addressed (and not
for PF_EDIT_STRING), returning that field's own live value.

    uv run --frozen python tools/protocol-research/element_addressing_read_probe.py [port] [field ...]
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.element_ref import retarget_element_leaf  # noqa: E402
from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import (  # noqa: E402
    _read_chunks, _seq_of, _set_seq, derive_write_template, read_field_value_near,
)
from qa_mcp.protocol.responses import value_mode_present  # noqa: E402

CAPTURE = REPO / "runtime/protocol-research/captures/genuine-commit-conn"
BASE = "PF_EDIT_STRING"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    targets = sys.argv[2:] or ["PF_EDIT_NUMBER", "PF_EDIT_DATE", "PF_EDIT_READONLY"]
    if not (CAPTURE / "traffic.jsonl").exists():
        print(f"capture not found: {CAPTURE}"); return 1

    t = derive_write_template(CAPTURE, BASE, "QAGENUINE2026", "PF_EDIT_STRING_VALUE")
    read_idx = t.read_frames[0]  # a captured PF_EDIT_STRING value-read frame
    mgr = _read_chunks(CAPTURE, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAPTURE, CLIENT_TO_MANAGER)
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])

    with socket.create_connection(("127.0.0.1", port), timeout=10.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, 0.6, 0.15))
        last = 0
        for i in range(0, t.setup_end + 1):  # replay setup -> open the form (proven path)
            wire = rebinder.apply(mgr[i])
            sock.sendall(wire)
            rebinder.observe_response(_read_available(sock, 0.6, 0.15))
            last = max(last, _seq_of(wire))
        seq = last + 1

        def read(field: str) -> bytes:
            nonlocal seq
            frame = mgr[read_idx]
            if field != BASE:
                frame, _ = retarget_element_leaf(frame, BASE, field)  # capture-free addressing
            wire = _set_seq(rebinder.apply(frame), seq)
            seq += 1
            sock.sendall(wire)
            resp = _read_available(sock, 0.6, 0.15)
            rebinder.observe_response(resp)
            return resp

        print(f"== capture-free element addressing (READ), port {port} ==")
        ctrl = read(BASE)
        print(f"[control] {BASE:<22} value_mode={value_mode_present(ctrl, BASE)} "
              f"value={read_field_value_near(ctrl, BASE)!r}")
        ok = True
        for field in targets:
            resp = read(field)
            vm_field = value_mode_present(resp, field)
            vm_base = value_mode_present(resp, BASE)
            flipped = vm_field and not vm_base
            ok = ok and flipped
            print(f"[addr   ] {field:<22} value_mode={vm_field} (base_mode={vm_base}) "
                  f"value={read_field_value_near(resp, field)!r}  addressing={'OK' if flipped else 'FAIL'}")
        print(f"\nRESULT: capture-free read-addressing {'PROVEN' if ok else 'NOT proven'} "
              f"(value-mode follows the element path leaf we substituted)")
        return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
