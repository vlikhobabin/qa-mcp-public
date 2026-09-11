#!/usr/bin/env python3
"""Card 98 — DIAGNOSE why retargeted dynlist reads return None (verbatim works, retarget fails).

Boots ONE client, then runs the faithful full-replay with PER-FRAME tracing for 3 cases:
  - verbatim       Товары / Наименование      (control: returns «Обувь»)
  - column-rt      Товары / Код               (navigate verbatim; only the read frame's column resizes)
  - list-rt        Валюты / Наименование      (SAME-LENGTH nav-link as Товары → no resize; column verbatim)

For each, prints per-frame sent/recv sizes (to see WHERE the stream diverges after a retarget) and the
read-frame response opcode region (value-envelope `81 81 81 e0 4b 53` vs command-echo `8a 81 81 e0 4b 55`
vs empty). This isolates: frame-length desync vs GuidRebinder/state mismatch vs column-not-found.

    .venv/bin/python tools/protocol-research/dynlist_read_diag_probe.py [port]
"""
from __future__ import annotations

import socket
import sys
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
GEN_LINK = "e1cib/list/Справочник.Товары"
GEN_COL = "Наименование"
RT = 6.0
IT = 1.5


def run(label: str, nav: str, col: str) -> None:
    mgr = _read_chunks(CAP, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAP, CLIENT_TO_MANAGER)
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    old_link, new_link = GEN_LINK.encode("utf-16le"), nav.encode("utf-16le")
    old_col = b"\xeb\x53" + encode_element_path_block(GEN_COL)
    new_col = b"\xeb\x53" + encode_element_path_block(col)
    print(f"\n=== {label}: nav={nav.split('.')[-1]} col={col} "
          f"(navResize={len(new_link)-len(old_link)}B colResize={len(new_col)-len(old_col)}B) ===")
    read_resp = b""
    with socket.create_connection(("127.0.0.1", PORT), timeout=10.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, RT, IT))
        for i in range(len(mgr)):
            wire = rebinder.apply(mgr[i])
            did = ""
            if old_link != new_link and old_link in wire:
                wire = wire.replace(old_link, new_link)
                pos = wire.find(new_link)
                if pos >= 2 and wire[pos - 2] == 0xf7:
                    wire = wire[: pos - 2] + b"\xf7" + bytes([len(nav)]) + wire[pos:]
                did = " NAV-RT"
            is_read = old_col in wire
            if is_read and old_col != new_col:
                wire = wire.replace(old_col, new_col)
                did += " COL-RT"
            sock.sendall(wire)
            resp = _read_available(sock, RT, IT)
            rebinder.observe_response(resp)
            if is_read:
                read_resp = resp
                did += " <READ"
            flag = "" if resp else "  !! NO RESP"
            if did or not resp or i >= 11:
                print(f"  mgr[{i:2d}] sent={len(wire):4d} recv={len(resp):4d} guids={len(rebinder.guid_map):2d}{did}{flag}")
    val = extract_table_cell_value(read_resp)
    has_val = b"\x81\x81\x81\xe0\x4b\x53" in read_resp
    has_echo = b"\x8a\x81\x81\xe0\x4b\x55" in read_resp
    print(f"  READ resp {len(read_resp)}B  value-env={has_val} cmd-echo={has_echo}  VALUE={val!r}")
    if read_resp:
        a = read_resp.find(b"\xe0\x4b")
        print(f"  resp@e04b: {read_resp[max(0,a-6):a+40].hex() if a>=0 else read_resp[-48:].hex()}")


def main() -> int:
    r = srv.launch_test_client(port=PORT, manage_apache=(PORT == 15381), display="auto", wait_sec=180.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} listening={r.get('listening')}")
    try:
        run("verbatim#1", GEN_LINK, GEN_COL)
        run("verbatim#2", GEN_LINK, GEN_COL)   # repeat: isolates sequential-replay / warm-cache from retarget
        run("column-rt ", GEN_LINK, "Код")
        run("list-rt   ", "e1cib/list/Справочник.Валюты", GEN_COL)
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=(PORT == 15381))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
