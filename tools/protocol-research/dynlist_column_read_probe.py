#!/usr/bin/env python3
"""Card 98 follow-up — DYNLIST COLUMN read feasibility. A list form's content is `Table[Список].EditField[col]`
(a different surface than form-fields). Open the demo Валюты LIST (populated rows), enumerate its Table columns
from the descriptor, and try the value-read retargeted to `…Table[Список].EditField[col]` — does it return the
CURRENT ROW's column value? Decisive: if a column reads back a real value, dynlist-column read works via the
value-read path; if not, it needs Vanessa's table-read command (a genuine capture).

    .venv/bin/python tools/protocol-research/dynlist_column_read_probe.py [port] [ib] [list-link]
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
from qa_mcp.protocol.element_ref import (  # noqa: E402
    extract_element_paths, path_is_latin1, retarget_element_path, retarget_element_path_reencode,
)
from qa_mcp.protocol.responses import extract_descriptor_elements, extract_form_field_values  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 15382
IB = sys.argv[2] if len(sys.argv) > 2 else "/opt/1c-dev/demo_1_0_41_3"
LINK = sys.argv[3] if len(sys.argv) > 3 else "e1cib/list/Справочник.Валюты"
MANAGE = PORT == 15381
TABLE = "Список"  # the standard dynlist table name


def column_rewriter(sf: str, mf: str, table: str, column: str):
    """Swap the captured value-read path for `SecondaryFrame[sf].ManagedForm[mf].Table[table].EditField[column]`."""
    new_path = f"SecondaryFrame[{sf}].ManagedForm[{mf}].Table[{table}].EditField[{column}]"

    def rw(_i: int, payload: bytes) -> bytes:
        out = payload
        for p in extract_element_paths(payload):
            if p.endswith(f"EditField[{srv._VALUE_READ_CAPTURED_FIELD}]"):
                try:
                    if path_is_latin1(new_path):
                        out, _ = retarget_element_path(out, p, new_path)
                    else:
                        out, _ = retarget_element_path_reencode(out, p, new_path)
                except ValueError:
                    pass
        return out
    return rw


def main() -> int:
    r = srv.launch_test_client(port=PORT, infobase_path=(None if MANAGE else IB),
                               user=(None if MANAGE else "Администратор"), kind=(None if MANAGE else "thick"),
                               manage_apache=MANAGE, display="auto", wait_sec=150.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} port={PORT} link={LINK}")
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
            els = extract_descriptor_elements(blob)
            cols = [e["name"] for e in els if e["kind"] == "EditField"]
            print(f"descriptor {len(blob)}B → {len(cols)} EditField columns: {cols[:14]}")
            for col in cols[:8]:
                before = len(h.state.received_stream)
                try:
                    h.run_segment(srv._VALUE_READ_FRAMES, query_id="form-value-read",
                                  frame_rewriter=column_rewriter(sf, mf, TABLE, col))
                except Exception as e:  # noqa: BLE001
                    print(f"  col {col}: EXCEPTION {type(e).__name__}: {e}")
                    continue
                vblob = bytes(h.state.received_stream[before:])
                vals = extract_form_field_values(vblob)
                has_env = b"\xe0\x4b\x53" in vblob
                print(f"  col {col}: resp {len(vblob)}B, value-envelope={has_env}, parsed={vals}")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=MANAGE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
