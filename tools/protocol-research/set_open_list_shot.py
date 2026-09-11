#!/usr/bin/env python3
"""Card 90 — capture-free OPEN-LIST, verified VISUALLY (a separate list window opens).

A nav-link open-list (`e1cib/list/Справочник.Товары`) is a top-level navigation command. This launches the
TestClient on an OWNED display, replays the genuine open-list capture (connect → open fixture form → the
open-list command) with live GUID rebinding, and screenshots before/after — a separate "Товары" list window
must appear. Optionally re-targets the catalog (same-length, via navigation.retarget_nav_link).

    uv run --frozen python tools/protocol-research/set_open_list_shot.py [catalog]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import capture_screenshot, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol.native_write import derive_open_list, open_list as native_open_list  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card90-openlist-20260617/traffic-selfcontained"


def main() -> int:
    catalog = sys.argv[1] if len(sys.argv) > 1 else None  # e.g. "Справочник.Склады" (re-target via nav link)
    out = REPO / "runtime/protocol-research/openlist-shot" / timestamp_name()
    out.mkdir(parents=True, exist_ok=True)
    template = derive_open_list(CAP)
    print(f"setup_end={template.setup_end} open_list_block={template.open_list_block} retarget={catalog!r}")

    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, disp = r["pid"], r.get("xvfb_pid"), r["display"]
    print(f"launched pid={pid} display={disp} listening={r.get('listening')}")
    try:
        # the productized standalone: connect → replay setup (open form) → send the nav-link open command
        res = native_open_list(template, catalog, port=15381)
        print("open_list result:", res)
        time.sleep(2.0)
        a = capture_screenshot(disp, out_path=str(out / "after.png"))
        print("after png:", a.get("size_bytes"))
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    print("out=", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
