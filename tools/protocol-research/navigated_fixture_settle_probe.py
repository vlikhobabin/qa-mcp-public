#!/usr/bin/env python3
"""Diagnostic — does the navigated FIXTURE form's descriptor grow if we SETTLE (the form renders async)?
Open the fixture DataProcessor by nav-link, resolve its S.F, then query the descriptor REPEATEDLY with a
window-list round-trip (a natural settle) between each, printing blob size + element/EditField count. If the
count grows, the 5-element result was a render race; if it stays small, the nav-link open is structurally
different.

    .venv/bin/python tools/protocol-research/navigated_fixture_settle_probe.py
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import qa_mcp.mcp_server as srv  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.native_write import splice_descriptor_query  # noqa: E402
from qa_mcp.protocol.responses import extract_descriptor_elements  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

LINK = "e1cib/data/Обработка.ФикстураПротоколаTestClient"


def main() -> int:
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid}")
    repo = srv._repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo))
    templates = ProtocolTemplates.load((repo / srv.VALUE_READ_TEMPLATES).resolve())
    synth = synthesize_bootstrap()
    out = repo / "runtime/protocol-research/native-mcp" / timestamp_name()
    try:
        with TestClientSession(host="127.0.0.1", port=15381) as s:
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            resolved = srv._open_form_by_link(h, LINK)
            print(f"resolved: {resolved}")
            if not resolved:
                print("FAIL — not resolved")
                return 1
            caption, sf, mf = resolved
            for i in range(6):
                # settle: a window-list round-trip lets the client finish rendering
                srv._open_form_by_link  # noqa: B018
                hdr = srv._splice_header_no_form(h)
                from qa_mcp.protocol.native_write import splice_window_list_queries
                for q in splice_window_list_queries(hdr):
                    h.run_action(q, query_id="settle-wl")
                before = len(h.state.received_stream)
                h.run_action(splice_descriptor_query(srv._splice_header_no_form(h), sf, mf), query_id="descriptor")
                blob = bytes(h.state.received_stream[before:])
                els = extract_descriptor_elements(blob)
                kinds = Counter(e["kind"] for e in els)
                edits = [e["name"] for e in els if e["kind"] == "EditField"]
                print(f"  pass {i}: descriptor {len(blob)}B, {len(els)} elements, kinds={dict(kinds)}, "
                      f"EditFields={edits[:8]}")
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
