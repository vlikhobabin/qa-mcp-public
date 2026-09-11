#!/usr/bin/env python3
"""Card 97 #2 DATE grid cell — PROTOCOL-activate + XTEST-type hybrid (the grid analog of write_form_value_xtest).

The date grid cell rejects the protocol text-SET (committed=False), and OS keystrokes into an OS-opened editor
don't land (1C routes keys to its INTERNALLY-focused control). Hypothesis: the protocol cell-ACTIVATE establishes
that internal edit focus — so replay ONLY the write_block (activate+SET, NO commit/focus-change → the cell stays
focused), hold the connection, then xdotool types the FULL date (no 9-byte protocol-buffer limit) and commits.

    .venv/bin/python tools/protocol-research/date_cell_xtest_hybrid_probe.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import _repo_root, capture_screenshot, launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol.bootstrap import resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.native_mutation import _read_available  # noqa: E402
from qa_mcp.protocol.native_write import (  # noqa: E402
    NativeWriteSession, build_write_frame, derive_table_cell_write, read_table_cell_value,
)

CAP = "genuine-card90-table-20260617/traffic-selfcontained"
NEW_DATE = "15.08.2026"
SHOT = "runtime/protocol-research/screenshots"


def _xdo(display: str, *args: str) -> str:
    p = subprocess.run(["xdotool", *args], env={**os.environ, "DISPLAY": display},
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return p.stdout.strip()


def main() -> int:
    r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
    pid, xvfb, display = r["pid"], r.get("xvfb_pid"), r.get("display")
    print(f"launched pid={pid} listening={r.get('listening')} display={display}")
    wm = subprocess.Popen(["matchbox-window-manager", "-use_titlebar", "no"],
                          env={**os.environ, "DISPLAY": display},
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    try:
        template = derive_table_cell_write(resolve_capture_dir(CAP, _repo_root()), "PF_TABLE_TEXT", "CELLAA",
                                           commit_partner_field="PF_EDIT_STRING", commit_partner_value="C90CMT")
        with NativeWriteSession(template, host="127.0.0.1", port=15381) as s:
            # PROTOCOL: send ONLY the write_block (activate + SET) for PF_TABLE_DATE — NOT the commit_block.
            # The activate enters the cell editor (internal focus); the SET value ("CELLAA") is rejected but
            # harmless — we just need the cell focused.
            lo, hi = s.t.write_block
            for i in range(lo, hi + 1):
                wire = s._rebinder.apply(s._mgr[i])
                wire = build_write_frame(wire, s.t.captured_value, "CELLAA",
                                         base_field=s.t.field, target_field="PF_TABLE_DATE", seq=s._seq)
                s._seq += 1
                s._sock.sendall(wire)
                s._rebinder.observe_response(_read_available(s._sock, s.rt, s.it))
            time.sleep(1.2)
            a = capture_screenshot(display, out_path=f"{SHOT}/date-hybrid-activated.png")
            print(f"activated -> {a.get('path')}")

            # OS INPUT: protocol-activate opened the editor, but OS keyboard focus is on the table container
            # (synthetic keys don't route to the inline editor). The control test shows a mouse CLICK grabs OS
            # focus + selects content → type replaces. Click the now-open editor, then type the FULL date.
            _xdo(display, "mousemove", "1130", "370")
            _xdo(display, "click", "1")          # cursor into the editor (confirmed: places a text cursor)
            time.sleep(0.5)
            _xdo(display, "key", "End")          # clear the field char-by-char (masked control may ignore `type`)
            for _ in range(22):
                _xdo(display, "key", "BackSpace")
            time.sleep(0.3)
            keymap = {".": "period"}             # inject the date PER-KEY (real keycodes, not type's remap)
            for ch in NEW_DATE:
                _xdo(display, "key", keymap.get(ch, ch))
                time.sleep(0.08)
            time.sleep(0.5)
            t = capture_screenshot(display, out_path=f"{SHOT}/date-hybrid-typed.png")
            print(f"typed     -> {t.get('path')}")
            _xdo(display, "key", "Return")
            time.sleep(1.2)
            af = capture_screenshot(display, out_path=f"{SHOT}/date-hybrid-after.png")
            print(f"after     -> {af.get('path')}  (typed {NEW_DATE!r})")

            # read-back via the template's read frames (cell value echo)
            rb = b""
            for i in s.t.read_frames:
                if i < len(s._mgr):
                    s._sock.sendall(s._rebinder.apply(s._mgr[i]))
                    rb += _read_available(s._sock, s.rt, s.it)
            print(f"readback PF_TABLE_DATE -> {read_table_cell_value(rb, 'PF_TABLE_DATE')!r}")

            # CONTROL: does xdotool type reach a STANDALONE field (PF_EDIT_STRING) in THIS env? Click it + type.
            _xdo(display, "mousemove", "358", "577")
            _xdo(display, "click", "1")
            time.sleep(0.4)
            _xdo(display, "type", "--delay", "80", "ZZSTRTEST")
            time.sleep(0.6)
            c = capture_screenshot(display, out_path=f"{SHOT}/date-hybrid-control-string.png")
            print(f"control (PF_EDIT_STRING type test) -> {c.get('path')}")
    finally:
        wm.terminate()
        stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
