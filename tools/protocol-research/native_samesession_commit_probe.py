#!/usr/bin/env python3
"""Card 80 LIVE test: does a value-INPUT commit when replayed in the capture's OWN session?

Card 79's effect probe spliced two sessions: open from tm-v1-ro-batchQ3 + input from
fixture-input-capture, on a synthesized bootstrap, GUID-rebound. The SET was ACKed but never
committed. Card 80 offline forensics refuted an unrebound wire token (the only non-rebound
session-variant field is a per-frame nonce proven harmless-when-stale). The remaining suspect is the
manager-originated SESSION IDENTITY (card 76 wall) that the cross-capture splice carries stale.

This probe removes the splice: it replays `fixture-input-capture` VERBATIM in its OWN bootstrap
(GuidRebinder learns live client GUIDs; manager-originated handshake GUIDs are replayed as-is, which
card 76 showed the client accepts), through the SET (mgr ord 282/283) and on to the capture's OWN
post-SET value-read (mgr ord ~467-470, whose original client response carries PF_INPUT_PROOF). It
captures the LIVE response to those read frames and reports whether the value committed.

  committed (read shows PF_INPUT_PROOF) -> the SPLICE was the blocker; same-session capture+replay
      commits => true write-effect verification is achievable without a genuine manager input path.
  not committed (read shows the default / no marker) -> even faithful same-session replay does not
      commit => the gate is manager-side runtime state (Fork 3 required).

Run (needs a live TestClient): PYTHONPATH=src python3 tools/protocol-research/native_samesession_commit_probe.py \
    --capture fixture-input-capture --host 127.0.0.1 --port 15381
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import socket  # noqa: E402

from replay_probe import (  # type: ignore  # noqa: E402
    CLIENT_TO_MANAGER,
    MANAGER_TO_CLIENT,
    read_capture_chunks,
    select_chunks,
    timestamp_name,
)
from qa_mcp.protocol.bootstrap import resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.native_mutation import GuidRebinder, _read_available  # noqa: E402
from qa_mcp.scenario.replay import find_marker_ordinal  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", default="fixture-input-capture")
    parser.add_argument("--marker", default="PF_INPUT_PROOF")
    parser.add_argument("--default-value", default="PF_EDIT_STRING_VALUE")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=15381)
    parser.add_argument("--read-frames", default=None,
                        help="manager ordinal range a-b of the post-SET value-read to inspect; "
                             "default = auto (the PF_EDIT_STRING frames just after the SET)")
    parser.add_argument("--stop-after", type=int, default=None,
                        help="stop replay after this manager ordinal (default: last read frame + 2)")
    parser.add_argument("--retarget", default=None,
                        help="de-novo value test (Fork 2): substitute the captured marker value with THIS "
                             "new value (both UTF-8 and UTF-16LE) in every replayed frame, then verify the "
                             "NEW value commits. Use a SAME-LENGTH replacement to avoid length/prefix fixups.")
    parser.add_argument("--read-timeout-sec", type=float, default=1.2)
    parser.add_argument("--idle-timeout-sec", type=float, default=0.2)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    cap = resolve_capture_dir(args.capture, repo_root)
    chunks = read_capture_chunks(cap)
    mgr = select_chunks(chunks, MANAGER_TO_CLIENT)
    cli = select_chunks(chunks, CLIENT_TO_MANAGER)

    set_ord = find_marker_ordinal(mgr, args.marker)
    if set_ord is None:
        print(json.dumps({"error": f"marker {args.marker} not in {args.capture}"}))
        return 2

    # auto-locate the post-SET value-read frames (manager PF_EDIT_STRING refs after the SET pair)
    if args.read_frames:
        lo, _, hi = args.read_frames.partition("-")
        read_frames = list(range(int(lo), int(hi) + 1))
    else:
        read_frames = [i for i, c in enumerate(mgr) if i > set_ord + 1 and b"PF_EDIT_STRING" in c["payload"]][:6]
    if not read_frames:
        print(json.dumps({"error": "no post-SET PF_EDIT_STRING read frames found"}))
        return 2
    stop_after = args.stop_after if args.stop_after is not None else read_frames[-1] + 2

    # the client echoes field text as UTF-16LE (sometimes UTF-8) — check BOTH or a present value reads
    # as a false negative (card 80 diagnostic 2026-06-16).
    marker_b = args.marker.encode("utf-8")
    marker16 = args.marker.encode("utf-16-le")
    default_b = args.default_value.encode("utf-8")
    default16 = args.default_value.encode("utf-16-le")

    def _has(blob: bytes, *needles: bytes) -> bool:
        return any(n in blob for n in needles)

    # Fork-2 retarget: substitute the captured value with a NEW one (same length) in every frame, and
    # verify the NEW value (not the captured marker) commits.
    retarget_b = args.retarget.encode("utf-8") if args.retarget else None
    retarget16 = args.retarget.encode("utf-16-le") if args.retarget else None
    if retarget_b is not None and len(args.retarget) != len(args.marker):
        print(json.dumps({"error": f"--retarget must be the same length as --marker "
                                    f"({len(args.marker)} chars) to avoid length fixups"}))
        return 2
    expect_b = retarget_b if retarget_b is not None else marker_b
    expect16 = retarget16 if retarget16 is not None else marker16

    rebinder = GuidRebinder.from_client_chunks(cli)

    read_responses: dict[int, bytes] = {}
    set_resp = b""
    diverged_at = None
    sent = 0
    with socket.create_connection((args.host, args.port), timeout=10.0) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        rebinder.observe_response(_read_available(sock, args.read_timeout_sec, args.idle_timeout_sec))
        empty_frames = []
        consec_empty = 0
        real_divergence = None
        for index, chunk in enumerate(mgr):
            if index > stop_after:
                break
            payload = rebinder.apply(chunk["payload"])
            if retarget_b is not None:
                payload = payload.replace(marker_b, retarget_b).replace(marker16, retarget16)
            try:
                sock.sendall(payload)
            except OSError:
                real_divergence = index  # real disconnect
                break
            sent += 1
            response = _read_available(sock, args.read_timeout_sec, args.idle_timeout_sec)
            rebinder.observe_response(response)
            if index in (set_ord, set_ord + 1):
                set_resp += response
            if index in read_frames:
                read_responses[index] = response
            if not response:
                # tiny control/ACK frames (≤16 B) are one-way and legitimately get NO response (runs of
                # 4-byte frames are normal) — never count them as divergence. Only a RUN of SUBSTANTIVE
                # frames with no response means the session is actually dead. (A truly closed socket trips
                # the sendall OSError above.)
                if diverged_at is None:
                    diverged_at = index  # first empty (informational)
                empty_frames.append(index)
                if len(payload) > 16:
                    consec_empty += 1
                    if consec_empty >= 8:
                        real_divergence = index
                        break
            else:
                consec_empty = 0

    read_blob = b"".join(read_responses.values())
    committed = _has(read_blob, expect_b, expect16) and not _has(read_blob, default_b, default16)
    report = {
        "schema": "card80.samesession-commit-probe.v1",
        "capture": args.capture,
        "set_ordinal": set_ord,
        "read_frames": read_frames,
        "stop_after": stop_after,
        "frames_sent": sent,
        "diverged_at": diverged_at,
        "real_divergence_at": real_divergence,
        "first_empty_response_at": empty_frames[0] if empty_frames else None,
        "empty_response_count": len(empty_frames),
        "reached_set": sent > set_ord,
        "retarget": args.retarget,
        "set_response_has_marker": _has(set_resp, expect_b, expect16),
        "read_response_has_marker": _has(read_blob, expect_b, expect16),
        "read_response_has_default": _has(read_blob, default_b, default16),
        "committed": committed,
        "verdict": (
            "COMMITTED in same-session replay -> the SPLICE was the blocker (write-effect achievable "
            "without a genuine manager input path)"
            if committed
            else "NOT committed even in faithful same-session replay -> manager-side runtime state "
            "gates the commit (Fork 3 required)"
        ),
    }
    out_dir = (args.output_dir or repo_root / "runtime" / "protocol-research" / "samesession-commit-probe" / timestamp_name()).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for i, resp in read_responses.items():
        (out_dir / f"read_resp_{i}.bin").write_bytes(resp)
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
