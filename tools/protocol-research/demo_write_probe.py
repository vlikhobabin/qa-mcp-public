#!/usr/bin/env python3
"""Card 98 / change 5 (the 🚩 GATE) — WRITE path generalizes to a 2nd (real, non-fixture) config.

Replays a genuine demo_1_0_41_3 WRITE capture (input into the БСП catalog ``Справочник.Валюты`` field
``Наименование``) capture-free, with the value RE-TARGETED to an ARBITRARY new string, against a FRESH
demo_1_0_41_3 TestClient — and verifies the new value COMMITTED (read back). Exercises the SAME engine as the
fixture on a Cyrillic-named field (needs the UTF-16LE element-path support added for card 98). Reads back two
ways on the SAME session socket: (a) the genuine in-stream read frame, (b) a re-activate of the field.

    PYTHONPATH=src python3 tools/protocol-research/demo_write_probe.py [port] [new_value]
"""
from __future__ import annotations

import socket
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import (  # noqa: E402
    _read_chunks,
    derive_write_template,
    editfields_in,
    read_field_value_near,
    retarget_value,
)

CAP = REPO / "runtime/protocol-research/captures/genuine-card98-demo-write"
FIELD = "Наименование"
CAPTURED = "QADEMO2026"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15392
    new_value = sys.argv[2] if len(sys.argv) > 2 else "ZZGATEOK26"
    template = derive_write_template(CAP, FIELD, CAPTURED, default_value="")
    mgr = _read_chunks(CAP, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAP, CLIENT_TO_MANAGER)

    val_seq = bytes([len(CAPTURED.encode())]) + CAPTURED.encode()
    set_ord = next(i for i, p in enumerate(mgr) if val_seq in p)
    activate_idxs = [i for i in range(template.write_block[0], set_ord) if FIELD in editfields_in(mgr[i])]
    # replay through the genuine in-stream read frame(s) IN ORDER (their value-read needs prior setup frames)
    last = max([template.stop_after] + template.read_frames)
    print(f"field={FIELD!r} captured={CAPTURED!r} new={new_value!r} write_block={template.write_block} "
          f"focus_end={template.stop_after} read_frames={template.read_frames} activate_idxs={activate_idxs} replay_to={last}")

    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    set_resp = b""
    instream_read = b""
    reactivate_read = b""
    diverged = None
    consec_empty = 0
    with socket.create_connection(("127.0.0.1", port), timeout=15.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, 0.6, 0.15))
        for i in range(0, last + 1):
            wire = retarget_value(rebinder.apply(mgr[i]), CAPTURED, new_value)
            try:
                sock.sendall(wire)
            except OSError:
                diverged = i
                break
            resp = _read_available(sock, 0.6, 0.15)
            rebinder.observe_response(resp)
            if val_seq in mgr[i] or CAPTURED.encode("utf-16-le") in mgr[i]:
                set_resp += resp
            if i in template.read_frames:
                instream_read += resp
            if not resp and len(wire) > 16:
                consec_empty += 1
                if consec_empty >= 8:
                    diverged = i
                    break
            elif resp:
                consec_empty = 0
        # second read-back method: re-activate the field on the still-open session
        if diverged is None:
            for i in activate_idxs:
                try:
                    sock.sendall(rebinder.apply(mgr[i]))
                except OSError:
                    break
                reactivate_read += _read_available(sock, 0.6, 0.15)

    out = REPO / "runtime/protocol-research/demo-write-replay"
    out.mkdir(parents=True, exist_ok=True)
    (out / "set_resp.bin").write_bytes(set_resp)
    (out / "instream_read.bin").write_bytes(instream_read)
    (out / "reactivate_read.bin").write_bytes(reactivate_read)

    nb, n16 = new_value.encode(), new_value.encode("utf-16-le")
    cb, c16 = CAPTURED.encode(), CAPTURED.encode("utf-16-le")

    def has(blob: bytes) -> bool:
        return nb in blob or n16 in blob

    print(f"diverged_at={diverged}")
    print(f"set_response_echoes_new={has(set_resp)}")
    print(f"instream_read_has_new={has(instream_read)}  readback={read_field_value_near(instream_read, FIELD)!r}")
    print(f"reactivate_read_has_new={has(reactivate_read)}  readback={read_field_value_near(reactivate_read, FIELD)!r}")
    blob = instream_read + reactivate_read
    committed = has(blob) and not (cb in blob or c16 in blob)
    print("RESULT:", "COMMITTED — arbitrary new value written + READ BACK from the live form, capture-free "
          "(write generalizes to demo_1_0_41_3)" if committed
          else f"value accepted (echo={has(set_resp)}) but NOT read back as committed (diverged={diverged})")
    return 0 if committed else 2


if __name__ == "__main__":
    raise SystemExit(main())
