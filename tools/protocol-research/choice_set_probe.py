#!/usr/bin/env python3
"""Card 90 — capture-free radio CHOICE-set, verified by reading the choice value back (ASCII).

Decode (evidence genuine-card90-checkbox-decode-2026-06-17 §3.1): a radio commit ACTIVATES the EditField and
carries the selected variant as a length-prefixed string (`…EditField[NAME] … e0 4b 53 <0x9a><len><variant>`,
variant = the value NAME, e.g. PF_CHOICE_C). So a set = the genuine choose block with its EditField leaf +
the variant string re-targeted (build_write_frame).

This probe opens ONE persistent connection, replays the form-open prefix, then on the SAME live session:
  read PF_CHOICE_MODE  ->  set PF_CHOICE_C  ->  read (expect PF_CHOICE_C)  ->  set PF_CHOICE_A  ->  read
  (expect PF_CHOICE_A). The choice value reads back as ASCII directly (no side-effect field needed).

    uv run --frozen python tools/protocol-research/choice_set_probe.py [port] [capture_dir]
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
    _find_checkbox_toggle, _read_chunks, _seq_of, _set_seq, build_write_frame, read_field_value_near,
)

DEFAULT_CAP = REPO / "runtime/protocol-research/captures/genuine-card90-choice-20260617/traffic-selfcontained"
FIELD = "PF_CHOICE_MODE"
CAPTURED_VARIANT = "PF_CHOICE_A"


def _read_run_after(mgr: list[bytes], field: str, after: int) -> list[int]:
    """The read-SWEEP run for ``field``: the LAST contiguous EditField[field] run (the late get_form_analysis
    sweep), not an intermediate action block. Must start after ``after`` (the genuine action blocks)."""
    leaf = f"EditField[{field}]"
    idxs = [i for i, p in enumerate(mgr) if any(path.endswith(leaf) for path in extract_element_paths(p))]
    if not idxs:
        raise ValueError(f"no frames for {leaf!r}")
    # split into contiguous runs; take the last run (the read sweep)
    runs: list[list[int]] = [[idxs[0]]]
    for i in idxs[1:]:
        (runs[-1].append(i) if i == runs[-1][-1] + 1 else runs.append([i]))
    last = runs[-1]
    if last[0] <= after:
        raise ValueError(f"last {leaf!r} run {last} is not after the action block ({after})")
    return last


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 15381
    cap = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CAP
    mgr = _read_chunks(cap, MANAGER_TO_CLIENT)
    cli = _read_chunks(cap, CLIENT_TO_MANAGER)
    rebinder = GuidRebinder.from_client_chunks([{"payload": c} for c in cli])

    lo, hi = _find_checkbox_toggle(mgr, FIELD)        # the first contiguous EditField[FIELD] run = the choose block
    setup_end = lo - 1
    read_run = _read_run_after(mgr, FIELD, hi)        # the later read-sweep run
    print(f"capture={cap.name} setup_end={setup_end} choice_block=({lo},{hi}) read_run={read_run}")

    with socket.create_connection(("127.0.0.1", port), timeout=10.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, 0.6, 0.15))
        last = 0
        for i in range(0, setup_end + 1):
            wire = rebinder.apply(mgr[i]); sock.sendall(wire)
            rebinder.observe_response(_read_available(sock, 0.6, 0.15)); last = max(last, _seq_of(wire))
        seq = last + 1

        def read_choice() -> str | None:
            nonlocal seq
            val = None
            for i in read_run:
                wire = _set_seq(rebinder.apply(mgr[i]), seq); seq += 1
                sock.sendall(wire); resp = _read_available(sock, 0.6, 0.15)
                rebinder.observe_response(resp)
                got = read_field_value_near(resp, FIELD)
                if got is not None:
                    val = got
            return val

        def set_choice_to(variant: str) -> bool:
            nonlocal seq
            acc = False
            for i in range(lo, hi + 1):
                wire = build_write_frame(rebinder.apply(mgr[i]), CAPTURED_VARIANT, variant,
                                         base_field=FIELD, target_field=FIELD, seq=seq)
                seq += 1
                sock.sendall(wire); resp = _read_available(sock, 0.6, 0.15)
                rebinder.observe_response(resp)
                acc = acc or bool(resp)
            return acc

        baseline = read_choice()
        print(f"  baseline {FIELD} = {baseline!r}")
        results = {}
        for variant in ("PF_CHOICE_C", "PF_CHOICE_A"):
            acc = set_choice_to(variant)
            got = read_choice()
            results[variant] = got
            print(f"  set {variant} (accepted={acc}): {FIELD} = {got!r}  {'OK' if got == variant else 'FAIL'}")

    ok = all(results.get(v) == v for v in ("PF_CHOICE_C", "PF_CHOICE_A"))
    print("RESULT:", "PASS — capture-free radio choice-set commits" if ok else "INCONCLUSIVE")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
