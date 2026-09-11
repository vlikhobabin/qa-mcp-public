#!/usr/bin/env python3
"""Card 98 — verify splice_table_cell_read reads a real VALUE on the FIXTURE form table (controlled current row).
The fixture populates PF_TABLE_ITEMS with 3 default rows (row 1 PF_TABLE_TEXT="PF_ROW_001_TEXT", PF_TABLE_NUMBER
=1.10). Open the fixture (frames 11-17), then splice-read each column of the CURRENT row. If it returns the
default value, the decode + splice are proven for a form table; if empty, the current row needs activation first.

    .venv/bin/python tools/protocol-research/fixture_table_read_probe.py [activate]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.native_write import splice_table_cell_read  # noqa: E402
from qa_mcp.protocol.responses import extract_table_cell_value  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

GROUPS = ["PF_GROUP_MAIN"]
TABLE = "PF_TABLE_ITEMS"
COLUMNS = ["PF_TABLE_TEXT", "PF_TABLE_NUMBER", "PF_TABLE_MARKER"]


def main() -> int:
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid}")
    repo = srv._repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo))
    templates = ProtocolTemplates.load((repo / srv.VALUE_READ_TEMPLATES).resolve())
    synth = synthesize_bootstrap()
    out = repo / "runtime/protocol-research/native-mcp" / timestamp_name()
    rc = 1
    try:
        with TestClientSession(host="127.0.0.1", port=15381) as s:
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            h.run_segment(srv._VALUE_READ_OPEN_FRAMES, query_id="form-element-details")  # open the fixture form
            sf, mf = h.state.secondary_frame_guid, h.state.managed_form_guid
            print(f"fixture open: S={sf} F={mf}")
            for col in COLUMNS:
                header = srv._splice_header_no_form(h)
                before = len(h.state.received_stream)
                try:
                    h.run_action(splice_table_cell_read(header, sf, mf, GROUPS, TABLE, col), query_id="table-read")
                except Exception as e:  # noqa: BLE001
                    print(f"  {col}: EXCEPTION {type(e).__name__}: {e}")
                    continue
                resp = bytes(h.state.received_stream[before:])
                value = extract_table_cell_value(resp)
                env = b"\xe0\x4b\x53" in resp
                print(f"  {col}: resp {len(resp)}B, value-envelope={env}, value={value!r}")
                if value:
                    rc = 0
            print("\nPASS — fixture form-table cell value read capture-free" if rc == 0
                  else "\nFAIL — no value (current row may need activation)")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
