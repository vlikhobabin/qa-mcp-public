#!/usr/bin/env python3
"""Card 96 / E3 — EXPLORATORY: can a descriptor-less windows capture replay against a warm-cached client?

The windows{,2,3} captures are descriptor-less (~31 mgr chunks vs 79 for open_card) because they were taken
with a warm client form-cache (descriptors not re-sent on the wire). The open question (handoff Task 1, point 3):
does a REPLAY client — which shares the same on-disk `~/.1cv8` form cache — establish the session anyway, making
the cold-cache re-capture unnecessary?

This probe replays the FULL manager stream of a windows capture with GuidRebinder (exactly like open_card),
tracks divergence, and dumps every client response so we can SEE whether the session establishes and what the
client reports back through the genuine window-CLOSE commands (the 150-byte `88 82 81` frames on the card /
fixture SecondaryFrames). Read-only / non-mutating: a window close in an ephemeral TestClient is harmless.

    PYTHONPATH=src python3 tools/protocol-research/windows_explore_probe.py [port] [capture_dir] [out_dir]
"""
from __future__ import annotations

import re
import socket
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.native_write import _read_chunks, _all_secondary_frames  # noqa: E402
from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402

DEFAULT_CAP = REPO / "runtime/protocol-research/captures/genuine-card96-windows3-20260618/traffic"


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    cap = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CAP
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else REPO / "runtime/protocol-research/windows-explore"
    out.mkdir(parents=True, exist_ok=True)

    mgr = _read_chunks(cap, MANAGER_TO_CLIENT)
    cli = _read_chunks(cap, CLIENT_TO_MANAGER)
    sf = _all_secondary_frames(mgr + cli)
    form_sf = max(sf, key=lambda g: sf[g]) if sf else None
    # The genuine window-CLOSE commands = 88 82 81 on a SecondaryFrame (skip the SF-less bootstrap ones).
    close_idx = [i for i, b in enumerate(mgr)
                 if b"\x88\x82\x81" in b and any(g in b for g in sf)]
    print(f"capture={cap.parent.name} mgr={len(mgr)} cli={len(cli)} SFs={len(sf)}")
    print(f"  window-close frames (88 82 81 on an SF): mgr{close_idx}")

    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])
    seen = bytearray()
    per_frame = []
    consec_empty = 0
    divergence = None
    with socket.create_connection(("127.0.0.1", port), timeout=10.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, 0.6, 0.15))
        for i in range(len(mgr)):
            wire = rebinder.apply(mgr[i])
            try:
                sock.sendall(wire)
            except OSError:
                divergence = divergence or i
                per_frame.append((i, len(wire), -1))
                break
            resp = _read_available(sock, 0.6, 0.15)
            rebinder.observe_response(resp)
            seen += resp
            per_frame.append((i, len(wire), len(resp)))
            if not resp and len(wire) > 16:
                consec_empty += 1
                if consec_empty >= 8 and divergence is None:
                    divergence = i
            elif resp:
                consec_empty = 0

    (out / "seen.bin").write_bytes(bytes(seen))
    # did responses keep flowing THROUGH each close frame?
    print(f"  total response bytes={len(seen)} divergence_at={divergence}")
    print("  per-frame [idx wire->resp] (only close frames + their neighbours):")
    interesting = set()
    for c in close_idx:
        interesting.update({c - 1, c, c + 1})
    for i, w, r in per_frame:
        if i in interesting:
            tag = "  <== CLOSE" if i in close_idx else ""
            print(f"    mgr[{i:02d}] wire={w:4d} resp={r:4d}{tag}")

    # what does the client report back AFTER the last window-close? (utf-16 markers)
    def u16(b):
        try:
            s = b.decode("utf-16le", "ignore")
        except Exception:
            return []
        return sorted({m.group(0).strip() for m in re.finditer(r"[Ѐ-ӿA-Za-z0-9 _().:/\\-]{6,}", s)})[:12]

    print(f"  utf-16 markers in ALL responses: {u16(bytes(seen))}")
    reached_all_closes = (divergence is None) or all(divergence > c for c in close_idx)
    print("RESULT:", "session ESTABLISHED through all window-close frames (descriptor-less replay WORKS)"
          if reached_all_closes else f"replay DIVERGED at mgr[{divergence}] before all closes")
    return 0 if reached_all_closes else 1


if __name__ == "__main__":
    raise SystemExit(main())
