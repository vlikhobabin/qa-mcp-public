#!/usr/bin/env python3
"""Card 86c — commit a NUMBER field using the GENUINE number SET already in the capture (no new capture).

genuine-commit-conn contains the genuine PF_EDIT_NUMBER input (activate 353-354, SET 355-356 = '777,77') from
card 80's two-input feature, but it was NOT committed (no focus-change after it). The commit trigger is
"activate ANY other field" (that is exactly what committed PF_EDIT_STRING — the activate of PF_EDIT_NUMBER).
So: setup -> activate PF_EDIT_NUMBER + SET(value) -> activate PF_EDIT_STRING (focus-change) -> read back.

    uv run --frozen python tools/protocol-research/element_write_number_probe.py [port] [value]
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import (  # noqa: E402
    _EDITFIELD_RE, _read_chunks, _seq_of, _set_seq, read_field_value_near, retarget_value,
)

CAPTURE = REPO / "runtime/protocol-research/captures/genuine-commit-conn"
CAPTURED_NUM = "777,77"
SETUP_END = 347            # everything before the inputs
NUM_BLOCK = [353, 354, 355, 356]   # activate PF_EDIT_NUMBER + SET 777,77
FOCUS_AWAY = [348, 349]            # activate PF_EDIT_STRING -> commits PF_EDIT_NUMBER


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    value = sys.argv[2] if len(sys.argv) > 2 else CAPTURED_NUM
    mgr = _read_chunks(CAPTURE, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAPTURE, CLIENT_TO_MANAGER)
    # genuine PF_EDIT_NUMBER value-read frames from the read sweep (single-field, before the input)
    read_frames = [i for i, p in enumerate(mgr)
                   if i < 230 and {m.group(1) for m in _EDITFIELD_RE.finditer(p)} == {b"PF_EDIT_NUMBER"}][:3]
    print(f"read_frames(PF_EDIT_NUMBER)={read_frames}")
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])

    with socket.create_connection(("127.0.0.1", port), timeout=10.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, 0.6, 0.15))
        last = 0
        for i in range(0, SETUP_END + 1):
            wire = rebinder.apply(mgr[i]); sock.sendall(wire)
            rebinder.observe_response(_read_available(sock, 0.6, 0.15)); last = max(last, _seq_of(wire))
        seq = last + 1

        def send(i: int, retarget: bool) -> bytes:
            nonlocal seq
            wire = rebinder.apply(mgr[i])
            if retarget and value != CAPTURED_NUM:
                wire = retarget_value(wire, CAPTURED_NUM, value)
            wire = _set_seq(wire, seq); seq += 1
            sock.sendall(wire)
            resp = _read_available(sock, 0.6, 0.15); rebinder.observe_response(resp)
            return resp

        for i in NUM_BLOCK:
            send(i, retarget=True)     # activate + SET (value retargeted)
        for i in FOCUS_AWAY:
            send(i, retarget=False)    # focus-change -> commit
        readback = None
        for i in read_frames:
            resp = send(i, retarget=False)
            got = read_field_value_near(resp, "PF_EDIT_NUMBER")
            if got is not None:
                readback = got
        committed = readback == value
        print(f"NUMBER write {value!r}: committed={committed} readback={readback!r}")
        return 0 if committed else 2


if __name__ == "__main__":
    raise SystemExit(main())
