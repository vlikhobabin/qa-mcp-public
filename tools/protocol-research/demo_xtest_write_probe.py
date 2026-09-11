#!/usr/bin/env python3
"""Card 98 hybrid step (2) — write_form_value_xtest prototype (Vanessa-free). OUR engine opens the form +
focuses the field BY NAME via protocol replay [0..stop]; signals READY; waits for the external xdotool input
(type + Tab blur) to finish (TYPED marker); then reads the field back via the capture's read frame and reports
whether the value committed. Coordinated with run_demo_xtest_write.sh which does the xdotool keystrokes between
READY and TYPED.

    PYTHONPATH=src python3 demo_xtest_write_probe.py <port> <value> <ready_file> <typed_file> [stop] [read_frame]
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
from qa_mcp.protocol.native_write import _read_chunks, read_field_value_near  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card98-demo-write"
FIELD = "Наименование"


def main() -> int:
    port = int(sys.argv[1])
    value = sys.argv[2]
    ready_file = Path(sys.argv[3])
    typed_file = Path(sys.argv[4])
    stop = int(sys.argv[5]) if len(sys.argv) > 5 else 17
    read_frame = int(sys.argv[6]) if len(sys.argv) > 6 else 28
    mgr = _read_chunks(CAP, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAP, CLIENT_TO_MANAGER)
    reb = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    with socket.create_connection(("127.0.0.1", port), timeout=15.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        reb.observe_response(_read_available(sock, 0.6, 0.15))
        for i in range(0, min(stop, len(mgr) - 1) + 1):  # protocol: open form + focus field by name
            sock.sendall(reb.apply(mgr[i]))
            reb.observe_response(_read_available(sock, 0.6, 0.15))
        ready_file.write_text("ready")
        print(f"PROTOCOL open+focus done [0..{stop}] -- READY for xdotool input", flush=True)
        for _ in range(80):  # wait for the external xdotool type + Tab
            if typed_file.exists():
                break
            time.sleep(0.5)
        time.sleep(0.5)
        # read the field back via OUR engine: replay the capture's READ SEQUENCE [rstart..read_frame] in order
        # (the «запоминаю значение поля» server-call needs its setup frames; after xdotool type+Tab the form
        # state ~= genuine [0..24], so the post-focus read sequence reads the committed value). GUID-rebound.
        rstart = int(sys.argv[7]) if len(sys.argv) > 7 else read_frame
        read_resp = b""
        for rf in range(rstart, read_frame + 1):
            if rf < len(mgr):
                sock.sendall(reb.apply(mgr[rf]))
                read_resp += _read_available(sock, 0.9, 0.2)
        rv = read_field_value_near(read_resp, FIELD)
        has = value.encode() in read_resp or value.encode("utf-16-le") in read_resp
        print(f"readback_value={rv!r} value_in_readback={has}", flush=True)
        print("RESULT:", "COMMITTED via hybrid (our engine open/focus + xdotool input)" if has
              else "readback inconclusive (see screenshot)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
