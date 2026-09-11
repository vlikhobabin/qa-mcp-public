#!/usr/bin/env python3
"""Card 90 follow-up #1 — capture-free row-select RETARGET by value. The genuine select command carries the
search column + value as length-prefixed strings (`… 9a<len>COLUMN … 9a<len>VALUE …`). Re-targeting the VALUE
(fixed-width) selects a DIFFERENT row. This replays the row2write capture but swaps the select value, then
writes a cell — the row matching the new value must change (proving arbitrary-row select by value).

    uv run --frozen python tools/protocol-research/rowselect_retarget_shot.py <cap> <captured_select_value> <target_select_value> <captured_cell_value> <new_cell_value> [commit_partner]
"""
from __future__ import annotations

import socket
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import capture_screenshot, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import (  # noqa: E402
    _read_chunks, _seq_of, _set_seq, build_write_frame, derive_table_cell_write, retarget_value,
)
from qa_mcp.protocol.session import timestamp_name  # noqa: E402


def main() -> int:
    cap = Path(sys.argv[1])
    sel_from, sel_to = sys.argv[2], sys.argv[3]
    cell_from, cell_to = sys.argv[4], sys.argv[5]
    partner = sys.argv[6] if len(sys.argv) > 6 else "C90RC"
    out = REPO / "runtime/protocol-research/rowselect-retarget-shot" / timestamp_name()
    out.mkdir(parents=True, exist_ok=True)

    mgr = _read_chunks(cap, MANAGER_TO_CLIENT)
    cli = _read_chunks(cap, CLIENT_TO_MANAGER)
    t = derive_table_cell_write(cap, column="PF_TABLE_TEXT", captured_value=cell_from,
                                commit_partner_field="PF_EDIT_STRING", commit_partner_value=partner)
    # retarget the row-select value (fixed-width) wherever it appears in the setup
    sel_hits = [i for i in range(t.setup_end + 1) if sel_from.encode("latin1") in mgr[i]]
    print(f"setup_end={t.setup_end} write_block={t.write_block} commit_block={t.commit_block} "
          f"select-value frames={sel_hits} ({sel_from!r}->{sel_to!r})")

    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, disp = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={disp}")
    try:
        rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
        with socket.create_connection(("127.0.0.1", 15381), timeout=10.0) as sock:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            rebinder.observe_response(_read_available(sock, 0.6, 0.15))
            last = 0
            for i in range(0, t.setup_end + 1):
                frame = mgr[i]
                if sel_from.encode("latin1") in frame:
                    frame = retarget_value(frame, sel_from, sel_to)  # select a DIFFERENT row by value
                wire = rebinder.apply(frame); sock.sendall(wire)
                rebinder.observe_response(_read_available(sock, 0.6, 0.15)); last = max(last, _seq_of(wire))
            seq = last + 1
            time.sleep(1.5); capture_screenshot(disp, out_path=str(out / "0-before.png"))
            # cell write block + commit
            lo, hi = t.write_block
            commit = list(range(t.commit_block[0], t.commit_block[1] + 1)) if t.commit_block else []
            for i in list(range(lo, hi + 1)) + commit:
                wire = build_write_frame(rebinder.apply(mgr[i]), cell_from, cell_to,
                                         base_field="PF_TABLE_TEXT", target_field="PF_TABLE_TEXT", seq=seq)
                seq += 1
                sock.sendall(wire); rebinder.observe_response(_read_available(sock, 0.6, 0.15))
            time.sleep(1.5); capture_screenshot(disp, out_path=str(out / "1-after.png"))
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print("out=", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
