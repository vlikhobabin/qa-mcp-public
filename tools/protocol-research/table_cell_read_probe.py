#!/usr/bin/env python3
"""Card 98 — live-verify the DECODED table-cell read (splice_table_cell_read). Open the demo Валюты LIST
(populated rows), splice the genuine table-read command for each column, and parse the CURRENT ROW's value. If a
column reads back a real currency value, the decode is proven AND dynlist-column read works AND the non-empty
navigated value-read is closed (a list row's data is populated).

    .venv/bin/python tools/protocol-research/table_cell_read_probe.py [port] [ib] [list-link] [table]
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
from qa_mcp.protocol.native_write import splice_table_cell_read  # noqa: E402
from qa_mcp.protocol.responses import extract_descriptor_elements, extract_form_field_values  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 15382
IB = sys.argv[2] if len(sys.argv) > 2 else "/opt/1c-dev/demo_1_0_41_3"
LINK = sys.argv[3] if len(sys.argv) > 3 else "e1cib/list/Справочник.Валюты"
TABLE = sys.argv[4] if len(sys.argv) > 4 else "Список"
MANAGE = PORT == 15381


def table_groups(blob: bytes, table: str) -> list[str]:
    """Find the Group chain enclosing Table[table] in the descriptor (ASCII + UTF-16)."""
    try:
        ascii_table = table.encode("latin1")
    except UnicodeEncodeError:
        ascii_table = None
    if ascii_table is not None:
        m = re.compile(rb"((?:Group\[[^\]]+\]\.)*)Table\[" + re.escape(ascii_table) + rb"\]").search(blob)
        if m:
            return [g.decode("latin1") for g in re.findall(rb"Group\[([^\]]+)\]", m.group(1))]
    # UTF-16: match the contiguous (Group[g].)* chain IMMEDIATELY before Table[<table>]
    tu = ("Table[" + table + "]").encode("utf-16-le")
    grp = rb"G\x00r\x00o\x00u\x00p\x00\[\x00(?:(?!\]\x00)..)+?\]\x00\.\x00"
    m = re.search(rb"((?:" + grp + rb")*)" + re.escape(tu), blob)
    if m:
        return [g.decode("utf-16-le", "replace") for g in re.findall(
            rb"G\x00r\x00o\x00u\x00p\x00\[\x00((?:(?!\]\x00)..)+?)\]\x00", m.group(1))]
    return []


def main() -> int:
    r = srv.launch_test_client(port=PORT, infobase_path=(None if MANAGE else IB),
                               user=(None if MANAGE else "Администратор"), kind=(None if MANAGE else "thick"),
                               manage_apache=MANAGE, display="auto", wait_sec=150.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} port={PORT} link={LINK} table={TABLE}")
    repo = srv._repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo))
    templates = ProtocolTemplates.load((repo / srv.VALUE_READ_TEMPLATES).resolve())
    synth = synthesize_bootstrap()
    out = repo / "runtime/protocol-research/native-mcp" / timestamp_name()
    rc = 1
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
            cols = [e["name"] for e in extract_descriptor_elements(blob) if e["kind"] == "EditField"]
            groups = table_groups(blob, TABLE)
            print(f"Table[{TABLE}] groups={groups}; columns={cols[:10]}")
            for col in cols[:6]:
                header = srv._splice_header_no_form(h)
                before = len(h.state.received_stream)
                try:
                    h.run_action(splice_table_cell_read(header, sf, mf, groups, TABLE, col), query_id="table-read")
                except Exception as e:  # noqa: BLE001
                    print(f"  col {col}: EXCEPTION {type(e).__name__}: {e}")
                    continue
                resp = bytes(h.state.received_stream[before:])
                vals = extract_form_field_values(resp)
                has_env = b"\xe0\x4b\x53" in resp
                print(f"  col {col}: resp {len(resp)}B, value-envelope={has_env}, parsed={vals}")
                if col == cols[0]:  # dump the first response to characterize
                    print("    resp hex:", resp.hex())
                    u16 = [m.group(0).decode("utf-16-le", "ignore") for m in re.finditer(rb"(?:..){3,}?", resp)]
                    print("    has 0x88(stub)?", b"\x88\x81\x81" in resp, "| has e0 4b?", b"\xe0\x4b" in resp,
                          "| 'Валют' in resp(u16)?", "Валют".encode("utf-16-le") in resp)
                if vals:
                    rc = 0
            print("\nPASS — table cell value(s) read capture-free" if rc == 0 else "\nFAIL — no cell value parsed")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=MANAGE)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
