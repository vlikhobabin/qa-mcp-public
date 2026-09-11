#!/usr/bin/env python3
"""Card 97 #1 — live-verify the row-op command clicks (delete / move up-down / copy) capture-free, by
screenshot. Each click_command re-opens the fixture form (replays the connect+open setup from the combined
capture) → baseline table [PF_ROW_001|PF_ROW_002|PF_ROW_003], active row 1 → then ONE row-op command
retargeted from the genuine PF_COPY_ROW click. The form stays rendered after the connection closes, so the
screenshot shows PF_LAST_ACTION (proves the retarget fired the right command) + PF_TABLE_SNAPSHOT (proves the
table changed):
  PF_COPY_ROW      -> PF_TABLE[4]=PF_ROW_001|PF_ROW_001_COPY|PF_ROW_002|PF_ROW_003
  PF_DELETE_ROW    -> PF_TABLE[2]=PF_ROW_002|PF_ROW_003
  PF_MOVE_ROW_DOWN -> PF_TABLE[3]=PF_ROW_002|PF_ROW_001|PF_ROW_003
  PF_MOVE_ROW_UP   -> PF_TABLE[3]=PF_ROW_001|PF_ROW_002|PF_ROW_003 (row 1 already top -> no move; PF_LAST_ACTION proves fire)

    .venv/bin/python tools/protocol-research/rowops_verify_shot.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import capture_screenshot, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol.native_write import click_command, derive_command_click  # noqa: E402
from qa_mcp.protocol.session import timestamp_name  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card97-rowops-combined-20260619/traffic-selfcontained"
TARGETS = ["PF_COPY_ROW", "PF_DELETE_ROW", "PF_MOVE_ROW_DOWN", "PF_MOVE_ROW_UP"]


def main() -> int:
    out = REPO / "runtime/protocol-research/rowops-shot" / timestamp_name()
    out.mkdir(parents=True, exist_ok=True)
    t = derive_command_click(CAP, "PF_COPY_ROW")
    print(f"template base=PF_COPY_ROW setup_end={t.setup_end} click_block={t.click_block}")
    # The fixture form is a SINGLETON that stays open across manager connections and form-open does NOT reset it,
    # so each row-op must run on a FRESH client (clean baseline [001|002|003], active row 1) for a clean shot.
    for tgt in TARGETS:
        r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
        pid, xvfb, disp = r["pid"], r.get("xvfb_pid"), r["display"]
        try:
            res = click_command(t, tgt, port=15381)
            time.sleep(1.5)
            shot = out / f"{tgt}.png"
            a = capture_screenshot(disp, out_path=str(shot))
            print(f"{tgt:18s} accepted={res.get('accepted')} display={disp} png={a.get('size_bytes')}B -> {shot.name}")
        finally:
            stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
            time.sleep(1.0)
    print("out=", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
