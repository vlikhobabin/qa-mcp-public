#!/usr/bin/env python3
"""Card 86b — capture-free WRITE to a DIFFERENT writable STRING field in ANOTHER group (cross-group).

PF_EDIT_STRING and the only other writable string field PF_PAGE_A_FIELD live in different groups, so a
leaf-swap is not enough — the FULL element path suffix (groups + leaf) is grafted onto the live frame's
`SecondaryFrame[S].ManagedForm[F]` prefix. The target suffix is what live introspection (read_form_summary's
element tree) yields; here it is read from the capture. Single session (no cross-session desync).

    uv run --frozen python tools/protocol-research/element_write_crossgroup_probe.py [port] [field] [value]
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.element_ref import extract_element_paths, retarget_element_path  # noqa: E402
from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import (  # noqa: E402
    _read_chunks, _seq_of, _set_seq, derive_write_template, read_field_value_near, retarget_value,
)

CAPTURE = REPO / "runtime/protocol-research/captures/genuine-commit-conn"
BASE = "PF_EDIT_STRING"
BASE_VALUE = "QAGENUINE2026"


def _suffix_for(mgr: list[bytes], field: str) -> str | None:
    """The element path suffix (from the first `Group[` onward) for `field`, read from the capture."""
    for p in mgr:
        for path in extract_element_paths(p):
            if path.endswith(f"EditField[{field}]") and ".Group[" in path:
                return "Group[" + path.split(".Group[", 1)[1]
    return None


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    target = sys.argv[2] if len(sys.argv) > 2 else "PF_PAGE_A_FIELD"
    value = sys.argv[3] if len(sys.argv) > 3 else "QA86B_PAGEA"

    t = derive_write_template(CAPTURE, BASE, BASE_VALUE, "PF_EDIT_STRING_VALUE")
    mgr = _read_chunks(CAPTURE, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAPTURE, CLIENT_TO_MANAGER)
    suffix = _suffix_for(mgr, target)
    if suffix is None:
        print(f"no element path found for {target}"); return 1
    print(f"target suffix: {suffix}")

    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    with socket.create_connection(("127.0.0.1", port), timeout=10.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, 0.6, 0.15))
        last = 0
        for i in range(0, t.setup_end + 1):
            wire = rebinder.apply(mgr[i])
            sock.sendall(wire)
            rebinder.observe_response(_read_available(sock, 0.6, 0.15))
            last = max(last, _seq_of(wire))
        seq = last + 1
        readback = None
        for i in list(range(t.write_block[0], t.write_block[1] + 1)) + list(t.read_frames):
            if i >= len(mgr):
                continue
            wire = rebinder.apply(mgr[i])
            for op in extract_element_paths(wire):  # full-path (cross-group) retarget of the base leaf
                if op.endswith(f"EditField[{BASE}]"):
                    prefix = op.split(".Group[", 1)[0]  # SecondaryFrame[S].ManagedForm[F]
                    wire, _ = retarget_element_path(wire, op, f"{prefix}.{suffix}")
            wire = retarget_value(wire, BASE_VALUE, value)
            wire = _set_seq(wire, seq)
            seq += 1
            sock.sendall(wire)
            resp = _read_available(sock, 0.6, 0.15)
            rebinder.observe_response(resp)
            if i in t.read_frames:
                got = read_field_value_near(resp, target)
                if got is not None:
                    readback = got
        committed = readback == value
        print(f"write {target} = {value!r}  committed={committed}  readback={readback!r}")
        return 0 if committed else 2


if __name__ == "__main__":
    raise SystemExit(main())
