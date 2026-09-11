#!/usr/bin/env python3
"""Card 98 blocker #1 — timing test: replay the demo write through the focus-change, then POLL the read frame
repeatedly (with delays) to see whether the committed value appears after the commit round-trip propagates
(the fixture's read is ~200 frames downstream; demo's is right after the focus-change). Genuine value by
default (faithful replay).

    PYTHONPATH=src python3 tools/protocol-research/demo_write_poll_probe.py [port] [new_value]
"""
from __future__ import annotations

import socket
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import _read_chunks, derive_write_template, read_field_value_near, retarget_value  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card98-demo-write"
FIELD = "Наименование"
CAPTURED = "QADEMO2026"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15392
    new_value = sys.argv[2] if len(sys.argv) > 2 else CAPTURED
    t = derive_write_template(CAP, FIELD, CAPTURED, default_value="")
    mgr = _read_chunks(CAP, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAP, CLIENT_TO_MANAGER)
    read_frame = t.read_frames[0] if t.read_frames else 28
    reb = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    with socket.create_connection(("127.0.0.1", port), timeout=15.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        reb.observe_response(_read_available(sock, 0.6, 0.15))
        for i in range(0, t.stop_after + 1):  # through the focus-change (commit)
            wire = retarget_value(reb.apply(mgr[i]), CAPTURED, new_value)
            sock.sendall(wire)
            reb.observe_response(_read_available(sock, 0.6, 0.15))
        print(f"replayed [0..{t.stop_after}] (commit); now polling read frame mgr[{read_frame}] with delays:")
        for poll in range(6):
            time.sleep(0.6)
            sock.sendall(reb.apply(mgr[read_frame]))
            resp = _read_available(sock, 0.8, 0.2)
            rv = read_field_value_near(resp, FIELD)
            has = new_value.encode() in resp or new_value.encode("utf-16-le") in resp
            print(f"  poll {poll}: resp_len={len(resp)} read_Наим={rv!r} hasTarget={has}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
