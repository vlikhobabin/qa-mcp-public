#!/usr/bin/env python3
"""Card 90 / 86e DEBUG — write a table cell then replay the LATE read sweep and dump whether the value
committed (search the raw responses for the value, utf-8 + utf-16le) + the EditField[PF_TABLE_TEXT] context.

    uv run --frozen python tools/protocol-research/set_table_cell_debug.py [port] [capture_dir] [value]
"""
from __future__ import annotations

import socket
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.element_ref import extract_element_paths  # noqa: E402
from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import (  # noqa: E402
    _read_chunks, _seq_of, _set_seq, build_write_frame, derive_table_cell_write,
)

DEFAULT_CAP = REPO / "runtime/protocol-research/captures/genuine-card90-table-20260617/traffic-selfcontained"
FIELD = "PF_TABLE_TEXT"


def _runs_for(mgr, leaf_suffix):
    idxs = [i for i, p in enumerate(mgr) if any(path.endswith(leaf_suffix) for path in extract_element_paths(p))]
    runs = []
    for i in idxs:
        if runs and i == runs[-1][-1] + 1:
            runs[-1].append(i)
        else:
            runs.append([i])
    return runs


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    cap = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CAP
    value = sys.argv[3] if len(sys.argv) > 3 else "HELLO9"
    mgr = _read_chunks(cap, MANAGER_TO_CLIENT)
    cli = _read_chunks(cap, CLIENT_TO_MANAGER)
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    t = derive_table_cell_write(cap)
    print(f"setup_end={t.setup_end} write_block={t.write_block} commit_block={t.commit_block}")
    runs = _runs_for(mgr, f"EditField[{FIELD}]")
    print(f"EditField[{FIELD}] runs: {[(r[0], r[-1]) for r in runs]}")
    late = runs[-1]
    print(f"late read run = ({late[0]},{late[-1]})")

    with socket.create_connection(("127.0.0.1", port), timeout=10.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, 0.6, 0.15))
        last = 0
        for i in range(0, t.setup_end + 1):
            wire = rebinder.apply(mgr[i]); sock.sendall(wire)
            rebinder.observe_response(_read_available(sock, 0.6, 0.15)); last = max(last, _seq_of(wire))
        seq = last + 1
        # write block + commit (focus-change)
        blocks = list(range(t.write_block[0], t.write_block[1] + 1))
        blocks += list(range(t.commit_block[0], t.commit_block[1] + 1)) if t.commit_block else []
        setresp = b""
        for i in blocks:
            wire = build_write_frame(rebinder.apply(mgr[i]), t.captured_value, value,
                                     base_field=FIELD, target_field=FIELD, seq=seq); seq += 1
            sock.sendall(wire); resp = _read_available(sock, 0.6, 0.15)
            rebinder.observe_response(resp); setresp += resp
        # late read sweep
        readresp = b""
        for i in late:
            wire = _set_seq(rebinder.apply(mgr[i]), seq); seq += 1
            sock.sendall(wire); resp = _read_available(sock, 0.8, 0.2)
            rebinder.observe_response(resp); readresp += resp

    vb, v16 = value.encode("utf-8"), value.encode("utf-16-le")
    cap_b = t.captured_value.encode("utf-8")
    print(f"value {value!r}: in setresp={vb in setresp or v16 in setresp}  in readsweep={vb in readresp or v16 in readresp}")
    print(f"captured {t.captured_value!r} in readsweep={cap_b in readresp}")
    blob = readresp
    anchor = f"EditField[{FIELD}]".encode("latin1")
    j = blob.find(anchor)
    print(f"readsweep {len(blob)}B; EditField[{FIELD}] at {j}")
    if j >= 0:
        print("ctx:", blob[j:j + 80].hex(" "))
    # any printable run near the written value
    k = blob.find(vb)
    if k >= 0:
        print(f"value ctx @{k}:", blob[max(0, k - 16):k + 24].hex(" "))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
