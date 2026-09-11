#!/usr/bin/env python3
"""Diagnostic — does the navigated RECORD value-read RESOLVE (returns an empty-value envelope for an empty field)
or fail to reach the field (the 0x88 no-value stub)? Open the demo Валюты create form by nav-link, point the
session at its S.F, value-read each EditField (groups=[]), and dump the raw response classification + any value.
An empty-but-RESOLVED read proves the mechanism (the create form's fields are simply empty); a stub means the
retargeted path doesn't reach the navigated form.

    .venv/bin/python tools/protocol-research/navigated_valueread_classify_probe.py [port] [ib] [link]
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.responses import extract_descriptor_fields, extract_form_field_values  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 15382
IB = sys.argv[2] if len(sys.argv) > 2 else "/opt/1c-dev/demo_1_0_41_3"
LINK = sys.argv[3] if len(sys.argv) > 3 else "e1cib/data/Справочник.Валюты"
MANAGE = PORT == 15381


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
            specs = extract_descriptor_fields(blob)
            print(f"descriptor {len(blob)}B → fields {specs}")
            for name, groups in specs:
                def rw(_i, payload, _n=name, _g=tuple(groups)):
                    return srv._retarget_read_to_groups(payload, srv._VALUE_READ_CAPTURED_FIELD, _n, list(_g),
                                                        form_ref=(sf, mf))
                before = len(h.state.received_stream)
                try:
                    h.run_segment(srv._VALUE_READ_FRAMES, query_id="form-value-read", frame_rewriter=rw)
                except Exception as e:  # noqa: BLE001
                    print(f"  {name}: render EXCEPTION {type(e).__name__}: {e}")
                    continue
                vblob = bytes(h.state.received_stream[before:])
                vals = extract_form_field_values(vblob)
                stub = b"\x88" in vblob[:40]  # crude: the no-value path stub marker appears early
                has_e0 = b"\xe0\x4b\x53" in vblob  # the «стал равен» value envelope
                print(f"  {name}: resp {len(vblob)}B, e0-4b-53(value-envelope)={has_e0}, parsed={vals}")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=MANAGE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
