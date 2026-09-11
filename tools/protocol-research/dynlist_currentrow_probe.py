#!/usr/bin/env python3
"""Card 98 — establish a dynlist CURRENT ROW so the table-cell read returns a value. Open the demo Валюты list,
then try, in order: (1) read immediately, (2) read after settling (window-list round-trips, letting the server
query populate + row 1 become current), (3) read after a TABLE-ACTIVATE command (splice the table-level
`88 82 81 20 20 20` invoke at Table[Список] — the select/activate family), (4) read after activating the column
field. Report which (if any) yields a value — that's how read_list_column should position the current row.

    .venv/bin/python tools/protocol-research/dynlist_currentrow_probe.py [port] [ib] [list-link] [table] [column]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.native_write import WINDOW_LIST_HEADER_MARKER, splice_table_cell_read, splice_window_list_queries  # noqa: E402
from qa_mcp.protocol.element_ref import encode_element_path_block  # noqa: E402
from qa_mcp.protocol.responses import extract_table_cell_value  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 15382
IB = sys.argv[2] if len(sys.argv) > 2 else "/opt/1c-dev/demo_1_0_41_3"
LINK = sys.argv[3] if len(sys.argv) > 3 else "e1cib/list/Справочник.Валюты"
TABLE = sys.argv[4] if len(sys.argv) > 4 else "Список"
COLUMN = sys.argv[5] if len(sys.argv) > 5 else "Наименование"
MANAGE = PORT == 15381


def read_cell(h, sf, mf, groups):
    before = len(h.state.received_stream)
    h.run_action(splice_table_cell_read(srv._splice_header_no_form(h), sf, mf, groups, TABLE, COLUMN), query_id="tr")
    resp = bytes(h.state.received_stream[before:])
    return extract_table_cell_value(resp), resp


def settle(h, n=2):
    for _ in range(n):
        for q in splice_window_list_queries(srv._splice_header_no_form(h)):
            h.run_action(q, query_id="settle")


def table_activate(h, sf, mf, groups):
    """Splice the table-level activate/select invoke at Table[Список] (the `88 82 81 20 20 20` command family)."""
    header = srv._splice_header_no_form(h)
    parts = [f"SecondaryFrame[{sf}]", f"ManagedForm[{mf}]"] + [f"Group[{g}]" for g in groups] + [f"Table[{TABLE}]"]
    path = encode_element_path_block(".".join(parts))
    from qa_mcp.protocol.native_write import TABLE_READ_NONCE
    cmd = header + TABLE_READ_NONCE + path + b"\x88\x82\x81\x20\x20\x20" + b"\x66\x53\xb2\xa6"
    h.run_action(cmd, query_id="table-activate")


def main() -> int:
    r = srv.launch_test_client(port=PORT, infobase_path=(None if MANAGE else IB),
                               user=(None if MANAGE else "Администратор"), kind=(None if MANAGE else "thick"),
                               manage_apache=MANAGE, display="auto", wait_sec=150.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} link={LINK} table={TABLE} column={COLUMN}")
    repo = srv._repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo))
    templates = ProtocolTemplates.load((repo / srv.VALUE_READ_TEMPLATES).resolve())
    synth = synthesize_bootstrap()
    out = repo / "runtime/protocol-research/native-mcp" / timestamp_name()
    try:
        with TestClientSession(host="127.0.0.1", port=PORT) as s:
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            resolved = srv._open_form_by_link(h, LINK)
            print(f"resolved: {resolved}")
            if not resolved:
                return 1
            _, sf, mf = resolved
            h.state.secondary_frame_guid, h.state.managed_form_guid = sf, mf
            blob = srv._live_descriptor_blob(h, (sf, mf))
            groups = srv._table_groups(blob, TABLE)
            print(f"groups={groups}")

            v, resp = read_cell(h, sf, mf, groups)
            print(f"(1) immediate: value={v!r}  head={resp[resp.rfind(WINDOW_LIST_HEADER_MARKER)+3: resp.rfind(WINDOW_LIST_HEADER_MARKER)+3+40].hex() if WINDOW_LIST_HEADER_MARKER in resp else resp[:40].hex()}")

            settle(h, 3)
            v2, _ = read_cell(h, sf, mf, groups)
            print(f"(2) after settle: value={v2!r}")

            try:
                table_activate(h, sf, mf, groups)
                v3, _ = read_cell(h, sf, mf, groups)
                print(f"(3) after table-activate(88 82 81): value={v3!r}")
            except Exception as e:  # noqa: BLE001
                print(f"(3) table-activate EXCEPTION: {type(e).__name__}: {e}")

            best = next((x for x in (v, v2, v3 if 'v3' in dir() else None) if x), None)
            print("\nPASS — a dynlist current-row value was read" if best else "\nFAIL — no current-row value via settle/activate")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=MANAGE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
