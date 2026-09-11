#!/usr/bin/env python3
"""Render the fixture form on a held connection and screenshot it — to see the PF_TABLE_ITEMS grid layout
(esp. the PF_TABLE_DATE column) for the date-cell XTEST approach (the protocol text-SET is ruled out: the date
column returns committed=False even at fitting width).

    .venv/bin/python tools/protocol-research/date_cell_render_probe.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import _repo_root, capture_screenshot, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402
import os, subprocess  # noqa: E402


def _xdo(display: str, *args: str) -> None:
    subprocess.run(["xdotool", *args], env={**os.environ, "DISPLAY": display},
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

CAP = "tm-v1-ro-batchQ3"
TPL = "runtime/protocol-research/templates/tm-v1-open-plus-valueread/manager_frame_templates.json"


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r.get("display")
    print(f"launched pid={pid} listening={r.get('listening')} display={display}")
    try:
        repo = _repo_root()
        bootstrap = CaptureBootstrap.load(resolve_capture_dir(CAP, repo))
        templates = ProtocolTemplates.load((repo / TPL).resolve())
        out_dir = repo / "runtime" / "protocol-research" / "native-mcp" / timestamp_name()
        with TestClientSession(host="127.0.0.1", port=15381) as session:
            handle = session.open_and_bootstrap(bootstrap=bootstrap, templates=templates,
                                                 output_dir=out_dir, synthesized=synthesize_bootstrap())
            handle.run_segment(list(range(11, 18)), query_id="form-element-details")  # open the fixture form
            time.sleep(2.0)
            # scroll the form down to reveal the PF_TABLE_ITEMS grid (mouse wheel over the content area)
            _xdo(display, "mousemove", "700", "600")
            for _ in range(14):
                _xdo(display, "click", "5")  # button 5 = scroll down
                time.sleep(0.08)
            time.sleep(1.0)
            shot = capture_screenshot(display, out_path="runtime/protocol-research/screenshots/date-form-grid.png")
            print(f"screenshot -> {shot.get('path')} ({shot.get('size_bytes')} bytes) window={shot.get('matched_window_id')}")
            time.sleep(0.5)
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
