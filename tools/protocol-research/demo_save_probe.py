#!/usr/bin/env python3
"""Card 98 blocker #1 — FORCED COMMIT via save (Записать). Replays the genuine demo write+save capture
(type Наименование → Записать → read) capture-free with the value RE-TARGETED to an arbitrary string, against
a FRESH demo_1_0_41_3 client, and checks the post-save read-back shows the new value. Save commits all pending
edits (before validation) + persists the object — the generalizable commit trigger for handler-less fields
(the focus-change alone does not commit a field without an OnChange handler on the bare replay).

    PYTHONPATH=src python3 tools/protocol-research/demo_save_probe.py [port] [new_value]
"""
from __future__ import annotations

import socket
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import _read_chunks, read_field_value_near, retarget_value  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card98-demo-save"
FIELD = "Наименование"
CAPTURED = "QADEMO2026"
READ_FRAME = 31  # the «запоминаю значение поля» read after Записать (genuine resp reads back the value)


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15392
    new_value = sys.argv[2] if len(sys.argv) > 2 else "ZZGATEOK26"
    mgr = _read_chunks(CAP, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAP, CLIENT_TO_MANAGER)
    last = min(READ_FRAME, len(mgr) - 1)
    reb = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    set_resp = b""
    read_resp = b""
    diverged = None
    with socket.create_connection(("127.0.0.1", port), timeout=15.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        reb.observe_response(_read_available(sock, 0.6, 0.15))
        for i in range(0, last + 1):
            wire = retarget_value(reb.apply(mgr[i]), CAPTURED, new_value)
            try:
                sock.sendall(wire)
            except OSError:
                diverged = i
                break
            resp = _read_available(sock, 0.8, 0.2)  # save round-trip can be slower
            reb.observe_response(resp)
            if (bytes([len(CAPTURED.encode())]) + CAPTURED.encode()) in mgr[i]:
                set_resp += resp
            if i == READ_FRAME:
                read_resp += resp
    nb, n16 = new_value.encode(), new_value.encode("utf-16-le")
    cb, c16 = CAPTURED.encode(), CAPTURED.encode("utf-16-le")
    out = REPO / "runtime/protocol-research/demo-save-replay"
    out.mkdir(parents=True, exist_ok=True)
    (out / "set_resp.bin").write_bytes(set_resp)
    (out / "read_resp.bin").write_bytes(read_resp)
    print(f"field={FIELD!r} captured={CAPTURED!r} new={new_value!r} replay_to={last} read_frame={READ_FRAME}")
    print(f"diverged_at={diverged}")
    print(f"set_response_echoes_new={nb in set_resp or n16 in set_resp}")
    print(f"read_after_save_value={read_field_value_near(read_resp, FIELD)!r}")
    print(f"new_in_readback={nb in read_resp or n16 in read_resp}  captured_in_readback={cb in read_resp or c16 in read_resp}")
    committed = (nb in read_resp or n16 in read_resp) and not (cb in read_resp or c16 in read_resp)
    print("RESULT:", "COMMITTED — arbitrary value written + SAVED + read back, capture-free (write generalizes "
          "to demo_1_0_41_3 via the Записать commit)" if committed
          else f"NOT committed (diverged={diverged})")
    return 0 if committed else 2


if __name__ == "__main__":
    raise SystemExit(main())
