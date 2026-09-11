#!/usr/bin/env python3
"""Card 98 change-1 generalization — replay the descriptor-enumeration frames (18-40) via the new
tm-v1-form-analysis template (run_segment, full seq/GUID injection) and count the element names the live form
returns. If this enumerates the tree, read_form_descriptor can introspect ANY form (no per-form field list).

    .venv/bin/python tools/protocol-research/form_enum_template_probe.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import _repo_root, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

CAP = "tm-v1-ro-batchQ3"
TPL = "runtime/protocol-research/templates/tm-v1-form-analysis/manager_frame_templates.json"


def _names(blob: bytes) -> set[str]:
    return {m.group(1).decode() for m in re.finditer(rb"EditField\[([A-Za-z0-9_]+)\]", blob)}


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} listening={r.get('listening')}")
    try:
        repo = _repo_root()
        bootstrap = CaptureBootstrap.load(resolve_capture_dir(CAP, repo))
        templates = ProtocolTemplates.load((repo / TPL).resolve())
        out_dir = repo / "runtime" / "protocol-research" / "native-mcp" / timestamp_name()
        with TestClientSession(host="127.0.0.1", port=15381) as session:
            handle = session.open_and_bootstrap(bootstrap=bootstrap, templates=templates,
                                                 output_dir=out_dir, synthesized=synthesize_bootstrap())
            handle.run_segment(list(range(11, 18)), query_id="form-element-details")  # open
            before = len(handle.state.received_stream)
            handle.run_segment(list(range(18, 41)), query_id="form-element-details")  # descriptor enumeration
            blob = bytes(handle.state.received_stream[before:])
            names = _names(blob)
            print(f"\nenumeration: {len(blob)} resp bytes, {len(names)} distinct EditField names")
            print("sample:", sorted(names)[:25])
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
