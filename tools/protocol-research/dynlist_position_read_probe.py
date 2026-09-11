#!/usr/bin/env python3
"""Card 98 — DYNLIST position-then-read: replay the decoded «перехожу к первой строке» table commands
(genuine-card98-dynlist-read [33]/[35] `88 82 81 20 20 20` + [37]/[39] `88 82 81 e1 20 20 20`, retargeted to the
live Table path) to establish the current row, THEN read a column. On the demo Валюты dynlist (named columns).

    .venv/bin/python tools/protocol-research/dynlist_position_read_probe.py [port] [ib] [link] [table] [column]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.element_ref import encode_element_path_block  # noqa: E402
from qa_mcp.protocol.native_write import WINDOW_LIST_HEADER_MARKER, splice_table_cell_read  # noqa: E402
from qa_mcp.protocol.responses import extract_table_cell_value  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 15382
IB = sys.argv[2] if len(sys.argv) > 2 else "/opt/1c-dev/demo_1_0_41_3"
LINK = sys.argv[3] if len(sys.argv) > 3 else "e1cib/list/Справочник.Валюты"
TABLE = sys.argv[4] if len(sys.argv) > 4 else "Список"
COLUMN = sys.argv[5] if len(sys.argv) > 5 else "Наименование"
MANAGE = PORT == 15381
# genuine position-command nonces (echoed, not session-validated)
NONCE1 = bytes.fromhex("754ee15d6fb6f64f9a9c819ed06cd42bd5a719411d3b48724fb9e909d74b25b8f0")
NONCE2 = bytes.fromhex("3e312772a733f14a928d66945ecff123d51bdd3f72b47be443a9f3456621c73aa8")
TAIL = b"\x66\x53\xb2\xa6"


def table_path(sf, mf, groups):
    parts = [f"SecondaryFrame[{sf}]", f"ManagedForm[{mf}]"] + [f"Group[{g}]" for g in groups] + [f"Table[{TABLE}]"]
    return encode_element_path_block(".".join(parts))


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
            groups = srv._table_groups(srv._live_descriptor_blob(h, (sf, mf)), TABLE)
            print(f"groups={groups}")

            def position():
                path = table_path(sf, mf, groups)
                hdr = srv._splice_header_no_form(h)
                # [33]/[35]: 88 82 81 20 20 20 then 81 81 81 20 20 20
                h.run_action(hdr + NONCE1 + path + b"\x88\x82\x81\x20\x20\x20" + TAIL, query_id="pos1a")
                h.run_action(hdr + NONCE1 + path + b"\x81\x81\x81\x20\x20\x20" + TAIL, query_id="pos1b")
                # [37]/[39]: 88 82 81 e1 20 20 20 then 81 81 81 e1 20 20 20
                hdr2 = srv._splice_header_no_form(h)
                h.run_action(hdr2 + NONCE2 + path + b"\x88\x82\x81\xe1\x20\x20\x20" + TAIL, query_id="pos2a")
                h.run_action(hdr2 + NONCE2 + path + b"\x81\x81\x81\xe1\x20\x20\x20" + TAIL, query_id="pos2b")

            def read():
                before = len(h.state.received_stream)
                h.run_action(splice_table_cell_read(srv._splice_header_no_form(h), sf, mf, groups, TABLE, COLUMN),
                             query_id="tr")
                resp = bytes(h.state.received_stream[before:])
                return extract_table_cell_value(resp), resp

            v0, _ = read()
            print(f"(0) before position: value={v0!r}")
            position()
            v1, resp = read()
            print(f"(1) after position: value={v1!r}")
            if v1 is None:
                j = resp.rfind(WINDOW_LIST_HEADER_MARKER)
                print("    resp opcode after Table:", resp[j+3:j+3+60].hex() if j >= 0 else resp[:60].hex())
            print("\nPASS — dynlist current-row read works after positioning" if v1 else "\nFAIL — still no value after positioning")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=MANAGE)
    return 0 if v1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
