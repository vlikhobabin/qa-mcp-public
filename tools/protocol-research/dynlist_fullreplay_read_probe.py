#!/usr/bin/env python3
"""Card 98 — DYNLIST column read via a FAITHFUL FULL-SEQUENCE replay (no Vanessa).

Replay the WHOLE `genuine-card98-listform-read` manager stream — navigate (f7 nav-link) → activate
[27] (`88 81 81 e0 4b 55`) → render/data queries [29]/[31] → position [33-39] (`88 82 81 …`) → read
[41] (`88 81 81 e0 4b 55 eb 53 … Наименование`) — against the SAME vanessa_client config the capture
was taken on, with `GuidRebinder` rebinding the per-session window GUIDs by first-appearance. This is
the card-80 full-stream replay (the `set_reference_field` / `read_spreadsheet_cell` loop), NOT a
piecemeal splice.

WHY this and not the splice: the prior 4 reconstructions failed because `_open_form_by_link` inserts
window-list / resolve / descriptor INTROSPECTION queries the genuine INTERACTION flow does not, leaving
a different active-form/focus state so positioning never took. A faithful replay reproduces the exact
interaction-ready open, so positioning takes and the read returns the row value. Same config → no
retarget needed; GuidRebinder handles the only per-session difference (the window GUIDs). The value
parser (`extract_table_cell_value`) is already verified against this capture's response («Обувь»).

    .venv/bin/python tools/protocol-research/dynlist_fullreplay_read_probe.py [port]
"""
from __future__ import annotations

import socket
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import _read_chunks  # noqa: E402
from qa_mcp.protocol.responses import extract_table_cell_value  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card98-listform-read"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
READ_SIG = bytes.fromhex("888181e04b55eb53")  # the table-cell-read opcode (the read frame mgr[20])
VALUE_ENVELOPE = bytes.fromhex("818181e04b53")  # canonical «стал равен» response value envelope
ECHO_OPCODE = bytes.fromhex("8a8181e04b55")    # the client echoing the command (no value = no current row)
# generous timeouts: the dynlist DATA load (render queries) can take a beat on first open
READ_TIMEOUT = 6.0
IDLE_TIMEOUT = 1.5


def main() -> int:
    r = srv.launch_test_client(port=PORT, manage_apache=(PORT == 15381), display="auto", wait_sec=180.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} listening={r.get('listening')} infobase={r.get('connection', {}).get('infobase_path')}")
    mgr = _read_chunks(CAP, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAP, CLIENT_TO_MANAGER)
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    print(f"capture: {len(mgr)} mgr frames / {len(cli)} cli frames; captured GUIDs={len(rebinder.captured_order)}")

    seen = bytearray()
    read_resp = b""
    read_idx = -1
    value = None
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=10.0) as sock:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            rebinder.observe_response(_read_available(sock, READ_TIMEOUT, IDLE_TIMEOUT))
            for i in range(len(mgr)):
                wire = rebinder.apply(mgr[i])
                sock.sendall(wire)
                resp = _read_available(sock, READ_TIMEOUT, IDLE_TIMEOUT)
                rebinder.observe_response(resp)
                seen += resp
                tag = ""
                if READ_SIG in mgr[i]:
                    read_resp = resp
                    read_idx = i
                    tag = "  <-- READ COMMAND"
                print(f"  mgr[{i:2d}] sent={len(wire):4d} recv={len(resp):4d} guids={len(rebinder.guid_map)}{tag}")

        print(f"\nread frame = mgr[{read_idx}], response {len(read_resp)} bytes")
        if read_resp:
            has_value = VALUE_ENVELOPE in read_resp
            has_echo = ECHO_OPCODE in read_resp
            print(f"  response has value-envelope(81 81 81 e0 4b 53)={has_value}  command-echo(8a 81 81 e0 4b 55)={has_echo}")
            j = read_resp.find(READ_SIG[:3])  # crude opcode peek
            if j < 0:
                j = max(0, len(read_resp) - 80)
            print(f"  response opcode region: {read_resp[j:j+64].hex()}")
        # decode: prefer the read-frame response, fall back to the whole stream
        value = extract_table_cell_value(read_resp)
        src = "read-frame response"
        if value is None:
            value = extract_table_cell_value(bytes(seen))
            src = "full stream"
        print(f"\nVALUE = {value!r}  (from {src})")
        ok = value is not None
        print("\nPASS — dynlist column read via faithful full-sequence replay" if ok
              else "\nFAIL — no value (the faithful replay did not establish the current row / read)")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=(PORT == 15381))
    return 0 if value is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
