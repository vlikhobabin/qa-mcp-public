#!/usr/bin/env python3
"""Card 98 — isolate why an injected 2nd dynlist read fails (3 id/seq variants + dump the response).

The cold session reads the captured column fine («Обувь»); an injected extra read returned a 481-byte
non-value response. This probe, in ONE boot, sends THREE variants of an extra «Код» read on the same socket
right after the captured read and dumps each response head, to tell whether the breakage is the message-id
regen, the sequence bump, or something structural:
  V1 verbatim-ids : column retarget only, KEEP captured msg-id (off2) + seq (off19)
  V2 bump-seq     : column retarget + seq+1 (keep msg-id)
  V3 fresh-ids    : column retarget + fresh msg-id + seq+1   (the original failing attempt)

    .venv/bin/python tools/protocol-research/dynlist_multiread_variants_probe.py [port]
"""
from __future__ import annotations

import socket
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol.element_ref import encode_element_path_block  # noqa: E402
from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import _read_chunks  # noqa: E402
from qa_mcp.protocol.responses import extract_table_cell_value  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card98-listform-read"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
READ_IDX = 20
GEN_COL = "Наименование"
RT, IT = 6.0, 1.5


def classify(resp: bytes) -> str:
    if not resp:
        return "EMPTY"
    if b"\x81\x81\x81\xe0\x4b\x53" in resp:
        return "VALUE-ENV"
    if b"\x8a\x81\x81\xe0\x4b\x55" in resp:
        return "CMD-ECHO"
    return "OTHER"


def main() -> int:
    r = srv.launch_test_client(port=PORT, manage_apache=(PORT == 15381), display="auto", wait_sec=180.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched listening={r.get('listening')}")
    mgr = _read_chunks(CAP, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAP, CLIENT_TO_MANAGER)
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    old_col = b"\xeb\x53" + encode_element_path_block(GEN_COL)
    new_col = b"\xeb\x53" + encode_element_path_block("Код")
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=10.0) as sock:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            rebinder.observe_response(_read_available(sock, RT, IT))
            base_read = b""
            cap_seq = 0
            for i in range(READ_IDX + 1):
                wire = rebinder.apply(mgr[i])
                sock.sendall(wire)
                resp = _read_available(sock, RT, IT)
                rebinder.observe_response(resp)
                if i == READ_IDX:
                    base_read = wire.replace(old_col, new_col)  # the read frame, column -> Код
                    cap_seq = int.from_bytes(wire[19:21], "little")
                    print(f"  captured read -> {extract_table_cell_value(resp)!r} (cap_seq={cap_seq})")

            def send(label: str, frame: bytes) -> None:
                sock.sendall(frame)
                resp = _read_available(sock, RT, IT)
                rebinder.observe_response(resp)
                print(f"  [{label}] -> val={extract_table_cell_value(resp)!r} recv={len(resp)} {classify(resp)}")
                print(f"       head: {resp[:64].hex()}")

            # V1 verbatim ids
            send("V1 verbatim-ids", base_read)
            # V2 bump seq only
            b2 = bytearray(base_read); b2[19:21] = ((cap_seq + 1) & 0xFFFF).to_bytes(2, "little")
            send("V2 bump-seq    ", bytes(b2))
            # V3 fresh msg-id + bump seq
            b3 = bytearray(base_read); b3[2:18] = uuid.uuid4().bytes_le
            b3[19:21] = ((cap_seq + 2) & 0xFFFF).to_bytes(2, "little")
            send("V3 fresh-ids   ", bytes(b3))
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=(PORT == 15381))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
