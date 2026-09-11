#!/usr/bin/env python3
"""Card 98 change-1 generalization — splice-replay the get_form_analysis DESCRIPTOR query to enumerate a live
form's elements with NO per-form capture. The descriptor query shares the `…cb 23 95` header with the value-read
(spliceable) and embeds the form path SecondaryFrame[S].ManagedForm[F]; render a value-read frame live (live
GUIDs), graft the descriptor body with the form path retargeted to the live S/F, send → the descriptor response
enumerates every element path.

    .venv/bin/python tools/protocol-research/form_descriptor_query_splice_probe.py
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
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

OPEN_FRAMES = list(range(11, 18))
SPLIT = b"\xcb\x23\x95"
# descriptor query body (from genuine-card98-formanalysis-20260620, chunk#44): <33B nonce> 9a 66 <form-path> <opcode><tail>
PREPATH = bytes.fromhex("0a102bc90b462c40b5aeb6e2329a7234d556b8b81da321984a897449a89068b3b89a66")
POSTPATH = bytes.fromhex("888181e1828181818181812020206653b2a6")
PATH_RE = re.compile(rb"SecondaryFrame\[([0-9a-f-]{36})\]\.ManagedForm\[([0-9a-f-]{36})\]")


def main() -> int:
    r = srv.launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} listening={r.get('listening')}")
    repo = srv._repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir("tm-v1-ro-batchQ3", repo))
    templates = ProtocolTemplates.load((repo / srv.VALUE_READ_TEMPLATES).resolve())
    synth = synthesize_bootstrap()
    out = repo / "runtime/protocol-research/native-mcp" / timestamp_name()
    try:
        with TestClientSession(host="127.0.0.1", port=15381) as s:
            h = s.open_and_bootstrap(bootstrap=bootstrap, templates=templates, output_dir=out, synthesized=synth)
            h.run_segment(OPEN_FRAMES, query_id="form-element-details")
            sent0 = len(h.state.sent_stream)
            h.run_segment([218], query_id="form-value-read")          # render a live header + path
            rendered = bytes(h.state.sent_stream[sent0:])
            m = PATH_RE.search(rendered)
            live_s, live_f = m.group(1).decode(), m.group(2).decode()
            print(f"live form path: S={live_s} F={live_f}")
            header = rendered[: rendered.rfind(SPLIT) + len(SPLIT)]
            form_path = f"SecondaryFrame[{live_s}].ManagedForm[{live_f}]".encode("latin1")
            descriptor_query = header + PREPATH + form_path + POSTPATH
            before = len(h.state.received_stream)
            res = h.run_action(descriptor_query, query_id="form-descriptor")
            blob = bytes(h.state.received_stream[before:])
            print(f"\ndescriptor query sent={len(descriptor_query)}B resp={len(blob)}B accepted={res['accepted']}")
            edit = re.findall(rb"((?:Group\[[A-Za-z0-9_]+\]\.)+EditField\[[A-Za-z0-9_]+\])", blob)
            buttons = re.findall(rb"Button\[([A-Za-z0-9_]+)\]", blob)
            tables = re.findall(rb"Table\[([A-Za-z0-9_]+)\]", blob)
            print(f"EditField paths: {len(edit)} | Button: {len(set(buttons))} | Table: {len(set(tables))}")
            for p in edit[:8]:
                print("   ", p.decode())
            err = re.findall(rb"(?:[\x20-\x7e\x00][\x00\x04]){5,}", blob[:200])
            if not edit and err:
                print("  (no elements) utf16 head:", [e.decode("utf-16-le", "replace") for e in err[:4]])
    finally:
        srv.stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
