#!/usr/bin/env python3
"""Card 97 change 4 — live-verify the dynamic-list VIEW-MODE (grouping) toggle capture-free, by screenshot.

Each run boots a FRESH native /TESTCLIENT, replays the genuine «Режим просмотра» click from the card97-ch4
view-mode capture re-targeted to the requested mode (Список / Дерево / Иерархический), and screenshots. The
view-mode command is the `…Button[<UTF-16 name>] 88 82 81 20 20 20` family (same as the row ops). ``accepted``
confirms the server applied the command; the screenshot shows the list REPRESENTATION if the dynlist re-render
brings it into view.

    .venv/bin/python tools/protocol-research/set_list_view_verify_shot.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import capture_screenshot, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol.native_write import set_list_view  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card97-ch4-viewmode-20260619"
MODES = ["Список", "Дерево", "Иерархический"]


def main() -> int:
    out = REPO / "runtime/protocol-research/viewmode-shot" / timestamp_name()
    out.mkdir(parents=True, exist_ok=True)
    for i, mode in enumerate(MODES, 1):
        r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
        pid, xvfb, disp = r["pid"], r.get("xvfb_pid"), r["display"]
        try:
            res = set_list_view(CAP, mode, port=15381)
            time.sleep(1.5)
            shot = out / f"{i:02d}-{res['mode']}.png"
            a = capture_screenshot(disp, out_path=str(shot))
            print(f"{mode:14s} mode={res['mode']} button={res['button']} accepted={res['accepted']} "
                  f"display={disp} png={a.get('size_bytes')}B -> {shot.name}")
        finally:
            stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
            time.sleep(1.0)
    print("out=", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
