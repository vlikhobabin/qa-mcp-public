#!/usr/bin/env python3
"""Card 98 #2 — live-verify the productized get_window_list_testclient MCP tool against a fresh native
/TESTCLIENT (no Vanessa). Expects the fixture form + desktop + home page windows.

    .venv/bin/python tools/protocol-research/get_window_list_testclient_verify.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import get_window_list_testclient, launch_test_client, stop_test_client  # noqa: E402


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} listening={r.get('listening')}")
    try:
        result = get_window_list_testclient(port=15381)
        print(json.dumps(result, ensure_ascii=False, indent=1))
        captions = [w["caption"] for w in result["windows"]]
        ok = "QA MCP Protocol Fixture V1" in captions and result["count"] >= 2
        print(f"\ncount={result['count']} captions={captions}")
        print("PASS" if ok else "FAIL")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
