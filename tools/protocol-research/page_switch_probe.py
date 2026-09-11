#!/usr/bin/env python3
"""Card 86d — capture-free PAGE-SWITCH, verified visually via a screenshot (card 85).

Decode: a page-switch command addresses the target page `…Group[PF_PAGES_MAIN].Group[PF_PAGE_X]` + a fixed
activate structure; switch→B vs switch→A differ ONLY in the offset-19 counter, the nonce, and the page name.
So a switch to any page = the genuine switch frame with its page-Group leaf re-targeted (`retarget_element_leaf
kind='Group'`). This probe: open the fixture form, screenshot (default page), send the GENUINE switch-to-B,
screenshot, send the SYNTHESIZED switch-to-A (retargeted), screenshot — the visible active tab must change.

    uv run --frozen python tools/protocol-research/page_switch_probe.py <port> <display> <out_dir>
"""

from __future__ import annotations

import socket
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.element_ref import retarget_element_leaf  # noqa: E402
from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import _read_chunks, _seq_of, _set_seq  # noqa: E402
from qa_mcp.protocol.screenshot import capture_screenshot  # noqa: E402

CAPTURE = REPO / "runtime/protocol-research/captures/genuine-multiaction-clean-20260617"
SETUP_END = 29          # open form + the (harmless) genuine inputs, before the first page-switch
SWITCH_B = [30, 31]     # genuine switch -> PF_PAGE_B


def main() -> int:
    port = int(sys.argv[1]); display = sys.argv[2]; out = Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
    mgr = _read_chunks(CAPTURE, MANAGER_TO_CLIENT)
    cli = _read_chunks(CAPTURE, CLIENT_TO_MANAGER)
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])

    with socket.create_connection(("127.0.0.1", port), timeout=10.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, 0.6, 0.15))
        last = 0
        for i in range(0, SETUP_END + 1):
            wire = rebinder.apply(mgr[i]); sock.sendall(wire)
            rebinder.observe_response(_read_available(sock, 0.6, 0.15)); last = max(last, _seq_of(wire))
        seq = last + 1

        def shot(tag: str) -> None:
            time.sleep(1.2)
            r = capture_screenshot(display, out / f"{tag}.png")
            print(f"  [{tag}] {r['path']} ({r['size_bytes']} bytes)")

        def send(frame: bytes) -> None:
            nonlocal seq
            wire = _set_seq(rebinder.apply(frame), seq); seq += 1
            sock.sendall(wire); rebinder.observe_response(_read_available(sock, 0.6, 0.15))

        shot("0-default")                                   # form open, default page
        for i in SWITCH_B:
            send(mgr[i])                                    # GENUINE switch -> PF_PAGE_B
        shot("1-pageB")
        for i in SWITCH_B:
            frame, n = retarget_element_leaf(mgr[i], "PF_PAGE_B", "PF_PAGE_A", kind="Group")  # SYNTHESIZED -> A
            send(frame)
        shot("2-pageA-synth")
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
