#!/usr/bin/env python3
"""Card 86c diagnostic — is a string-SET retargeted to a NUMBER field REJECTED, or accepted-but-not-committed?

For PF_EDIT_STRING (works) vs PF_EDIT_NUMBER (does not commit), send the write block on one session and dump
the SET frame's response (len + head) + a value-read of the field right after. Rejection (short/empty/error
response, value unchanged) ⇒ the SET carries a type descriptor a number needs ⇒ genuine per-type capture
required. Accepted-but-no-commit (normal ack, value unchanged) ⇒ the commit (focus-change/ПриИзменении) is the
gap. Single session, fresh client.

    uv run --frozen python tools/protocol-research/element_write_86c_diag.py [port]
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.element_ref import retarget_element_leaf  # noqa: E402
from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import (  # noqa: E402
    _read_chunks, _seq_of, _set_seq, derive_write_template, encode_1c_length,
    read_field_value_near, retarget_value,
)

CAPTURE = REPO / "runtime/protocol-research/captures/genuine-commit-conn"
BASE, BASE_VALUE = "PF_EDIT_STRING", "QAGENUINE2026"


def ascii(b: bytes) -> str:
    return "".join(chr(c) if 32 <= c < 127 else "." for c in b)


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    t = derive_write_template(CAPTURE, BASE, BASE_VALUE, "PF_EDIT_STRING_VALUE")
    mgr = _read_chunks(CAPTURE, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAPTURE, CLIENT_TO_MANAGER)
    set_local = next(i for i in range(*[t.write_block[0], t.write_block[1] + 1])
                     if (encode_1c_length(len(BASE_VALUE.encode())) + BASE_VALUE.encode()) in mgr[i])
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])

    with socket.create_connection(("127.0.0.1", port), timeout=10.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, 0.6, 0.15))
        last = 0
        for i in range(0, t.setup_end + 1):
            wire = rebinder.apply(mgr[i]); sock.sendall(wire)
            rebinder.observe_response(_read_available(sock, 0.6, 0.15)); last = max(last, _seq_of(wire))
        seq = last + 1

        def write_block(field: str, value: str) -> None:
            nonlocal seq
            for i in list(range(t.write_block[0], t.write_block[1] + 1)) + list(t.read_frames):
                if i >= len(mgr):
                    continue
                wire = rebinder.apply(mgr[i])
                if field != BASE:
                    try:
                        wire, _ = retarget_element_leaf(wire, BASE, field)
                    except ValueError:
                        pass
                wire = retarget_value(wire, BASE_VALUE, value)
                wire = _set_seq(wire, seq); seq += 1
                sock.sendall(wire)
                resp = _read_available(sock, 0.6, 0.15)
                rebinder.observe_response(resp)
                if i == set_local:
                    print(f"  SET resp: len={len(resp)} head={resp[:32].hex()} tail={resp[-12:].hex()}")
                    print(f"            ascii={ascii(resp[:48])!r}")
                if i in t.read_frames:
                    print(f"  read-back[{field}] = {read_field_value_near(resp, field)!r}")

        for field, value in [("PF_EDIT_STRING", "DIAG_STR"), ("PF_EDIT_NUMBER", "777")]:
            print(f"== write {field} = {value!r} (SET local idx {set_local}) ==")
            write_block(field, value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
