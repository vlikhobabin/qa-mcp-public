#!/usr/bin/env python3
"""Card 97 #5 — live-verify assert_form_value + wait_for_form_value capture-free against a fresh native
/TESTCLIENT (no Vanessa). Reads the fixture's baseline fields off the wire (card-79 read path) and exercises
both assert outcomes (pass/fail/regex) and both wait outcomes (immediate satisfy / timeout).

    .venv/bin/python tools/protocol-research/assert_wait_verify.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import (  # noqa: E402
    assert_form_value, launch_test_client, stop_test_client, wait_for_form_value,
)


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb = r["pid"], r.get("xvfb_pid")
    print(f"launched pid={pid} listening={r.get('listening')}")
    try:
        # The value-read query resolves the PF_EDIT_* region; the LEB128 parser fix (card 97 #5) reads ALL of
        # its string fields (not just the 20-char PF_EDIT_STRING). PF_GROUP_MAIN status markers return the 0x88
        # stub (other region) — a documented read-decode follow-up.
        checks = [
            ("assert equals (string)", assert_form_value("PF_EDIT_STRING", "PF_EDIT_STRING_VALUE")),
            ("assert equals (readonly)", assert_form_value("PF_EDIT_READONLY", "PF_EDIT_READONLY_VALUE")),
            ("assert equals (wrong)", assert_form_value("PF_EDIT_STRING", "WRONG_VALUE")),
            ("assert contains", assert_form_value("PF_EDIT_DISABLED", "DISABLED", mode="contains")),
            ("assert regex", assert_form_value("PF_EDIT_STRING", r"PF_EDIT_\w+", mode="regex")),
            ("wait satisfy (immediate)", wait_for_form_value("PF_EDIT_STRING", "PF_EDIT_STRING_VALUE",
                                                             timeout_sec=10.0, interval_sec=0.5)),
            ("wait timeout", wait_for_form_value("PF_EDIT_STRING", "NEVER_APPEARS",
                                                 timeout_sec=2.0, interval_sec=0.5)),
        ]
        for label, res in checks:
            print(f"  {label:28s} -> {res}")
    finally:
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
