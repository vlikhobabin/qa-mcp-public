#!/usr/bin/env python3
"""Card 98 — can ONE cold session read MULTIPLE columns of the dynlist's current row?

The cold-client boundary is per-CLIENT-PROCESS (a fresh process reads fine even with a warm on-disk cache;
a 2nd full-replay in the SAME process fails). So the lever is to read everything we need INSIDE the one cold
session where the row data is materialised — instead of one read per fresh client. This probe does a cold
full-replay through the captured read (mgr[20] → «Обувь»), then on the SAME socket sends extra table-cell read
commands for more columns (reusing the rebound read frame, column retargeted, with a fresh message-id @off2 and
a bumped sequence @off19 per command). If those return values, `read_list_row(columns=[…])` is viable.

    .venv/bin/python tools/protocol-research/dynlist_multiread_probe.py [port]
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
READ_IDX = 20  # the captured read frame (mgr ordinal)
GEN_COL = "Наименование"
EXTRA_COLUMNS = ["Код", "Наименование", "Код"]  # read these AFTER the captured read, on the SAME socket
RT, IT = 6.0, 1.5


def with_fresh_ids(frame: bytes, seq: int) -> bytes:
    """Fresh per-frame message-id (offset 2, 16B bytes_le) + sequence (offset 19, u16 LE)."""
    b = bytearray(frame)
    b[2:18] = uuid.uuid4().bytes_le
    b[19:21] = (seq & 0xFFFF).to_bytes(2, "little")
    return bytes(b)


def main() -> int:
    r = srv.launch_test_client(port=PORT, manage_apache=(PORT == 15381), display="auto", wait_sec=180.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched listening={r.get('listening')}")
    mgr = _read_chunks(CAP, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAP, CLIENT_TO_MANAGER)
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    old_col = b"\xeb\x53" + encode_element_path_block(GEN_COL)
    results: list[tuple[str, object]] = []
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=10.0) as sock:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            rebinder.observe_response(_read_available(sock, RT, IT))
            base_read = b""
            seq = 0
            for i in range(READ_IDX + 1):  # cold replay through the captured read (skip the teardown frames)
                wire = rebinder.apply(mgr[i])
                sock.sendall(wire)
                resp = _read_available(sock, RT, IT)
                rebinder.observe_response(resp)
                if i == READ_IDX:
                    base_read = wire
                    seq = int.from_bytes(wire[19:21], "little")
                    v = extract_table_cell_value(resp)
                    print(f"  captured read (mgr[20], {GEN_COL}) -> {v!r}")
                    results.append((f"{GEN_COL} [captured]", v))
            # extra reads on the SAME socket (row data already materialised)
            for col in EXTRA_COLUMNS:
                new_col = b"\xeb\x53" + encode_element_path_block(col)
                seq += 1
                rd = with_fresh_ids(base_read.replace(old_col, new_col) if col != GEN_COL else base_read, seq)
                sock.sendall(rd)
                resp = _read_available(sock, RT, IT)
                rebinder.observe_response(resp)
                v = extract_table_cell_value(resp)
                has_val = b"\x81\x81\x81\xe0\x4b\x53" in resp
                print(f"  extra read (seq={seq}, {col}) -> {v!r}  recv={len(resp)} value-env={has_val}")
                results.append((col, v))
        ok = sum(1 for _, v in results if v is not None)
        print(f"\n{ok}/{len(results)} reads returned a value")
        print("MULTI-READ-IN-SESSION: " + ("WORKS" if ok == len(results) else "PARTIAL/FAIL"))
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=(PORT == 15381))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
