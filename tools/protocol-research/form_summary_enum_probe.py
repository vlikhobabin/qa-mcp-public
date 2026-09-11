#!/usr/bin/env python3
"""Card 98 change-1 generalization probe — does the open's form_summary enumerate the LIVE form's element tree?
If yes, read_form_descriptor can swap the capture-derived field list for this live enumeration (works on ANY
form). Prints the element count + names/types/paths from handle.form_summary().

    .venv/bin/python tools/protocol-research/form_summary_enum_probe.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import _repo_root, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

CAP = "tm-v1-ro-batchQ3"
TPL = "runtime/protocol-research/templates/tm-v1-open-plus-valueread/manager_frame_templates.json"


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
            summary = handle.form_summary()
            elements = summary.elements
            print(f"\nform_summary enumerated {len(elements)} elements")
            kinds: dict[str, int] = {}
            for e in elements:
                kinds[e.get("type", "?")] = kinds.get(e.get("type", "?"), 0) + 1
            print("by type:", kinds)
            print("first 25 (type name):")
            for e in elements[:25]:
                print(f"  {e.get('type'):14s} {e.get('name')}")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
