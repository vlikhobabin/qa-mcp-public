#!/usr/bin/env python3
"""Card 98 #2 — live-verify the state/window/results/infobase parity tools against a fresh native /TESTCLIENT:
infobase_info + get_state report the live connection, get_test_results aggregates a real run, and
get_window_list enumerates the client's OS window via xdotool.

    .venv/bin/python tools/protocol-research/change2_state_verify.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import (  # noqa: E402
    get_state, get_test_results, get_window_list, infobase_info, launch_test_client, run_step, stop_test_client,
)


def show(label: str, value: object) -> None:
    print(f"\n=== {label} ===")
    print(json.dumps(value, ensure_ascii=False, indent=1))


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r.get("display")
    print(f"launched pid={pid} listening={r.get('listening')} display={display}")
    try:
        show("infobase_info (live)", infobase_info(port=15381))
        show("get_state (live, pre-run)", get_state(pid=pid, port=15381))

        res = run_step(kind="read_active_window", port=15381)
        print(f"\nran read_active_window -> status={res.get('status')}")
        show("get_test_results (after 1 run)", get_test_results())

        show("get_window_list (OS, via xdotool)", get_window_list(display))
        show("get_state (live, post-run)", {"run_session": get_state(pid=pid, port=15381)["run_session"]})
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
