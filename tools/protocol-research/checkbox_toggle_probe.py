#!/usr/bin/env python3
"""Card 90 — capture-free checkbox TOGGLE, verified by a server side-effect read-back.

Decode (evidence genuine-card90-checkbox-decode-2026-06-17): a checkbox commits with NO value buffer — the
wire just ACTIVATES the EditField (`…EditField[NAME] … e0 4b 55`, identical for set & clear) and the server
flips the Boolean + fires ПриИзменении. So a toggle = the genuine toggle frame with its EditField leaf
re-targeted (the EditField twin of the 86d page-switch).

This probe opens ONE persistent connection, replays the form-open prefix, then on the SAME live session:
  baseline read of PF_LAST_ACTION  ->  toggle PF_CHECKBOX_FALSE  ->  read PF_LAST_ACTION (expect
  "PF_CHECKBOX_FALSE")  ->  toggle PF_CHECKBOX_TRUE (RE-TARGETED, capture-free)  ->  read (expect
  "PF_CHECKBOX_TRUE"). The fixture's ПриИзменении sets PF_LAST_ACTION = the toggled checkbox's NAME — an
  ASCII side-effect that proves the toggle COMMITTED server-side (the Boolean itself reads back as Да/Нет,
  Cyrillic, which the ASCII read parser can't see).

    uv run --frozen python tools/protocol-research/checkbox_toggle_probe.py [port] [capture_dir]
"""
from __future__ import annotations

import socket
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from qa_mcp.protocol.element_ref import extract_element_paths, retarget_element_leaf  # noqa: E402
from qa_mcp.protocol.frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.protocol.native_write import (  # noqa: E402
    _find_checkbox_toggle, _read_chunks, _seq_of, _set_seq, read_field_value_near,
)

DEFAULT_CAP = REPO / "runtime/protocol-research/captures/genuine-card90-20260617/traffic-selfcontained"
READ_FIELD = "PF_LAST_ACTION"


def _read_run(mgr: list[bytes], field: str) -> list[int]:
    leaf = f"EditField[{field}]"
    idxs = [i for i, p in enumerate(mgr) if any(path.endswith(leaf) for path in extract_element_paths(p))]
    if not idxs:
        raise ValueError(f"no read frames for {leaf!r} in the capture")
    # the contiguous run starting at the first occurrence (the read-sweep block for this field)
    run = [idxs[0]]
    for i in idxs[1:]:
        if i == run[-1] + 1:
            run.append(i)
        else:
            break
    return run


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    cap = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CAP
    mgr = _read_chunks(cap, MANAGER_TO_CLIENT)
    cli = _read_chunks(cap, CLIENT_TO_MANAGER)
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])

    setup_lo, setup_hi = _find_checkbox_toggle(mgr, "PF_CHECKBOX_FALSE")
    toggle_block = (setup_lo, setup_hi)
    setup_end = setup_lo - 1
    read_run = _read_run(mgr, READ_FIELD)
    print(f"capture={cap.name} setup_end={setup_end} toggle_block={toggle_block} read_run({READ_FIELD})={read_run}")

    with socket.create_connection(("127.0.0.1", port), timeout=10.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, 0.6, 0.15))
        last = 0
        for i in range(0, setup_end + 1):
            wire = rebinder.apply(mgr[i]); sock.sendall(wire)
            rebinder.observe_response(_read_available(sock, 0.6, 0.15)); last = max(last, _seq_of(wire))
        seq = last + 1

        def send(i: int, retarget: tuple[str, str] | None) -> bytes:
            nonlocal seq
            wire = rebinder.apply(mgr[i])
            if retarget is not None:
                wire, _ = retarget_element_leaf(wire, retarget[0], retarget[1], kind="EditField")
            wire = _set_seq(wire, seq); seq += 1
            sock.sendall(wire)
            resp = _read_available(sock, 0.6, 0.15)
            rebinder.observe_response(resp)
            return resp

        def read_last_action() -> str | None:
            val = None
            for i in read_run:
                resp = send(i, None)
                got = read_field_value_near(resp, READ_FIELD)
                if got is not None:
                    val = got
            return val

        def toggle(target: str) -> bool:
            acc = False
            for i in range(toggle_block[0], toggle_block[1] + 1):
                rt = None if target == "PF_CHECKBOX_FALSE" else ("PF_CHECKBOX_FALSE", target)
                resp = send(i, rt)
                acc = acc or bool(resp)
            return acc

        baseline = read_last_action()
        print(f"  baseline PF_LAST_ACTION = {baseline!r}")
        acc_f = toggle("PF_CHECKBOX_FALSE")
        after_false = read_last_action()
        print(f"  after toggle PF_CHECKBOX_FALSE (accepted={acc_f}): PF_LAST_ACTION = {after_false!r}  "
              f"{'OK' if after_false == 'PF_CHECKBOX_FALSE' else 'FAIL'}")
        acc_t = toggle("PF_CHECKBOX_TRUE")
        after_true = read_last_action()
        print(f"  after toggle PF_CHECKBOX_TRUE  (accepted={acc_t}): PF_LAST_ACTION = {after_true!r}  "
              f"{'OK' if after_true == 'PF_CHECKBOX_TRUE' else 'FAIL'}")

    ok = after_false == "PF_CHECKBOX_FALSE" and after_true == "PF_CHECKBOX_TRUE"
    print("RESULT:", "PASS — capture-free checkbox toggle commits (base + re-targeted)" if ok else "INCONCLUSIVE")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
