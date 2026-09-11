#!/usr/bin/env python3
"""Card 98 blocker #1 (commit fidelity) — instrumented demo_1_0_41_3 write replay. Replays the genuine demo
write capture frame-by-frame (default: GENUINE value, no retarget — so the per-frame responses should MATCH
the capture if the replay is faithful) and prints, per manager frame: fields, response length, the value-mode
read of Наименование, and whether the response carries the target value. Compare against the genuine baseline
(mgr[18] SET echo + mgr[28] read both carry the value) to localize WHERE the value is lost.

    PYTHONPATH=src python3 tools/protocol-research/demo_write_trace_probe.py [port] [new_value]
"""
from __future__ import annotations

import socket
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import _read_chunks, editfields_in, read_field_value_near, retarget_value  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card98-demo-write"
FIELD = "Наименование"
CAPTURED = "QADEMO2026"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15392
    new_value = sys.argv[2] if len(sys.argv) > 2 else CAPTURED  # default: genuine value (faithful replay)
    mgr = _read_chunks(CAP, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAP, CLIENT_TO_MANAGER)
    target = new_value.encode()
    target16 = new_value.encode("utf-16-le")
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    print(f"REPLAY new={new_value!r} (retarget {'OFF' if new_value == CAPTURED else 'ON'}); per-frame 14..len:")
    with socket.create_connection(("127.0.0.1", port), timeout=15.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, 0.6, 0.15))
        for i, payload in enumerate(mgr):
            wire = retarget_value(rebinder.apply(payload), CAPTURED, new_value)
            try:
                sock.sendall(wire)
            except OSError:
                print(f"  mgr[{i}] SEND FAILED (socket closed)")
                break
            resp = _read_available(sock, 0.6, 0.15)
            rebinder.observe_response(resp)
            outdir = REPO / "runtime/protocol-research/demo-trace-replay"
            outdir.mkdir(parents=True, exist_ok=True)
            (outdir / f"resp_{i:02d}.bin").write_bytes(resp)
            if i < 14:
                continue
            flds = sorted(editfields_in(payload))
            rv = read_field_value_near(resp, FIELD)
            has = target in resp or target16 in resp
            setv = " SET" if (bytes([len(CAPTURED.encode())]) + CAPTURED.encode()) in payload else ""
            print(f"  mgr[{i}] flds={flds}{setv} | resp_len={len(resp)} read_Наим={rv!r} hasTarget={has}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
