#!/usr/bin/env python3
"""Card 97 change 3 — experiment: does a VARIABLE-length cell navigate work via FRAME RESIZE (keep the 3 trailing
spaces, grow the frame) instead of padding-consume? Also confirms the 12x12 grid filled via a same-length far cell.

  .venv/bin/python tools/protocol-research/cell_resize_experiment.py
"""
from __future__ import annotations
import socket
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.mcp_server import launch_test_client, stop_test_client  # noqa: E402
from qa_mcp.protocol.native_write import _read_chunks, read_field_value_near  # noqa: E402
from qa_mcp.protocol.frames import MANAGER_TO_CLIENT, CLIENT_TO_MANAGER  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402

CAP = REPO / "runtime/protocol-research/captures/genuine-card97-ch3-cellread-20260619"
OLD = "R1C1"


def retarget_pad(frame: bytes, new: str) -> bytes:
    """padding-consume (current impl): fa<len>new + shrink trailing spaces, frame size constant."""
    needle = bytes([0xfa, len(OLD)]) + OLD.encode()
    i = frame.find(needle)
    if i < 0:
        return frame
    vend = i + len(needle)
    pad = 0
    while vend + pad < len(frame) and frame[vend + pad] == 0x20:
        pad += 1
    region = len(needle) + pad
    nb = bytes([0xfa, len(new)]) + new.encode()
    return frame[:i] + nb + b"\x20" * (region - len(nb)) + frame[i + region:]


def retarget_resize(frame: bytes, new: str) -> bytes:
    """RESIZE: fa<len>new, KEEP the original trailing spaces (frame grows/shrinks by the address-length delta)."""
    needle = bytes([0xfa, len(OLD)]) + OLD.encode()
    i = frame.find(needle)
    if i < 0:
        return frame
    nb = bytes([0xfa, len(new)]) + new.encode()
    return frame[:i] + nb + frame[i + len(needle):]


def read_cell(address: str, retarget, port=15381) -> str | None:
    mgr = _read_chunks(CAP, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAP, CLIENT_TO_MANAGER)
    reb = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    seen = bytearray()
    with socket.create_connection(("127.0.0.1", port), timeout=10) as s:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        reb.observe_response(_read_available(s, 0.6, 0.15))
        for fr in mgr:
            wire = retarget(reb.apply(fr), address) if retarget else reb.apply(fr)
            s.sendall(wire)
            resp = _read_available(s, 0.6, 0.15)
            reb.observe_response(resp)
            seen += resp
    return read_field_value_near(bytes(seen), "PF_REPORT")


def main() -> int:
    trials = [
        ("R5C5", "same-length (grid check)", lambda f, a: f),   # 4-char == OLD len -> verbatim (grid fill check via... no, need retarget)
    ]
    # R5C5 is 4 chars like R1C1 -> use padding (no-op delta) to actually navigate there
    cases = [
        ("R5C5", retarget_pad, "PF_RPT_R5C5"),     # same length -> confirms grid filled + same-length nav
        ("R1C12", retarget_pad, "PF_RPT_R1C12"),   # +1 char, padding-consume (the failing path)
        ("R1C12", retarget_resize, "PF_RPT_R1C12"), # +1 char, RESIZE (keep 3 spaces)
        ("R12C12", retarget_resize, "PF_RPT_R12C12"), # +2 char, RESIZE
    ]
    for addr, rt, exp in cases:
        r = launch_test_client(port=15381, manage_apache=True, display="auto", wait_sec=120.0)
        pid, xvfb = r["pid"], r.get("xvfb_pid")
        try:
            val = read_cell(addr, rt, port=15381)
            tag = "pad" if rt is retarget_pad else "resize"
            print(f"  {addr:7s} [{tag:6s}] -> {val!r}  expected {exp!r}  {'OK' if val == exp else 'MISMATCH'}")
        finally:
            stop_test_client(pid, xvfb_pid=xvfb, manage_apache=True)
            time.sleep(1.0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
