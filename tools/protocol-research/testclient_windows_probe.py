#!/usr/bin/env python3
"""Card 98 #2 (remainder) — investigate window enumeration when a SECOND window is opened. Boots a native
/TESTCLIENT, lists OS windows (baseline), opens a catalog list (a new 1C window), then re-lists — to determine
whether the OS-level `get_window_list` already enumerates a newly-opened 1C window (the practical
`get_window_list_testclient` need) before investing in a protocol-level SecondaryFrame decode.

    .venv/bin/python tools/protocol-research/testclient_windows_probe.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import (  # noqa: E402
    capture_screenshot, get_window_list, launch_test_client, open_list, stop_test_client,
)


def titles(win: dict) -> list[str]:
    return [w["title"] for w in win["windows"] if w["title"]]


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r.get("display")
    print(f"launched pid={pid} listening={r.get('listening')} display={display}")
    try:
        before = get_window_list(display)
        print(f"\n=== windows BEFORE open_list (count={before['count']}) ===")
        print(json.dumps(before["windows"], ensure_ascii=False, indent=1))

        res = open_list(port=15381)               # opens the Справочник.Товары list window
        print(f"\nopen_list -> accepted={res.get('accepted')} target={res.get('target_link')}")
        time.sleep(2.0)                            # let the window map

        after = get_window_list(display)
        print(f"\n=== windows AFTER open_list (count={after['count']}) ===")
        print(json.dumps(after["windows"], ensure_ascii=False, indent=1))

        new_titles = sorted(set(titles(after)) - set(titles(before)))
        print(f"\nNEW window titles after open_list: {new_titles}")
        print(f"count delta: {after['count'] - before['count']}")

        shot = capture_screenshot(display)
        print(f"screenshot: {shot.get('path')} ({shot.get('size_bytes')} bytes)")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
