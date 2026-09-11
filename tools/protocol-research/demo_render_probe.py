#!/usr/bin/env python3
"""Card 98 hybrid step (1) — does OUR replay /TESTCLIENT render the form on a protocol open (no Vanessa)?
Connects to a native /TESTCLIENT and replays the demo write capture's open+focus frames [0..stop] (connect ->
open Справочник.Валюты -> activate window -> activate field Наименование) via GuidRebinder, then HOLDS the
connection open so the client keeps the form rendered while a screenshot is taken.

    PYTHONPATH=src python3 tools/protocol-research/demo_render_probe.py [port] [stop_frame] [hold_seconds]
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
from qa_mcp.protocol.native_write import _read_chunks  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card98-demo-write"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15393
    stop = int(sys.argv[2]) if len(sys.argv) > 2 else 17  # activate-Наименование (no SET) in the demo capture
    hold = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    mgr = _read_chunks(CAP, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAP, CLIENT_TO_MANAGER)
    reb = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    diverged = None
    consec_empty = 0
    with socket.create_connection(("127.0.0.1", port), timeout=15.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        reb.observe_response(_read_available(sock, 0.6, 0.15))
        for i in range(0, min(stop, len(mgr) - 1) + 1):
            wire = reb.apply(mgr[i])
            try:
                sock.sendall(wire)
            except OSError:
                diverged = i
                break
            resp = _read_available(sock, 0.6, 0.15)
            reb.observe_response(resp)
            if not resp and len(wire) > 16:
                consec_empty += 1
                if consec_empty >= 8:
                    diverged = i
                    break
            elif resp:
                consec_empty = 0
        print(f"replayed [0..{stop}] diverged_at={diverged} -- HOLDING {hold}s for screenshot", flush=True)
        time.sleep(hold)
    print("released")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
