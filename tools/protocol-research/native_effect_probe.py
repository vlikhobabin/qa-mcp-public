#!/usr/bin/env python3
"""Card 79 acceptance: native EFFECT verification, no Vanessa.

Full loop in one synthesized session: open the fixture form (CIButton click) -> read PF_EDIT_STRING
value (default) -> input a new value -> read the value again -> assert it CHANGED to the input and no
longer equals the default. Proves the runner can verify an action's EFFECT, not just acceptance."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from python_manager_client import (  # type: ignore
    CaptureBootstrap,
    ProtocolTemplates,
    TestClientSession,
    repo_root_from_script,
    resolve_capture_dir,
    timestamp_name,
)
from replay_probe import (  # type: ignore
    CLIENT_TO_MANAGER,
    MANAGER_TO_CLIENT,
    read_capture_chunks,
    select_chunks,
)
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap
from qa_mcp.protocol.frames import extract_managed_form_guid, extract_secondary_frame_guid
from qa_mcp.scenario.model import Step
from qa_mcp.protocol.native_mutation import substitute_guid_all_encodings
from qa_mcp.scenario.replay import build_single_session_action_resolver, find_marker_ordinal


def value_after(blob: bytes) -> str | None:
    """Extract the PF_EDIT_STRING field value from a value-read response (0x81 ... 0xfa<len><value>)."""
    m = re.search(rb"EditField\[PF_EDIT_STRING\]\x81\x81\x81[\xe0\xfa][^\x14]*\x14([\x20-\x7e]+?)(?:\x20*\xa1|\x20{2,})", blob)
    if not m:
        return None
    return m.group(1).decode("latin1").strip()


def has_value_token(blob: bytes, token: str) -> bool:
    # the client echoes field text as UTF-16LE on the wire (and sometimes UTF-8) — check both,
    # else a present value reads as a false negative (card 80 diagnostic 2026-06-16).
    return token.encode("utf-8") in blob or token.encode("utf-16-le") in blob


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=15381)
    parser.add_argument("--capture-dir", default="tm-v1-ro-batchQ3")
    parser.add_argument("--manager-templates", type=Path, required=True)
    parser.add_argument("--action-capture", default="fixture-input-capture")
    parser.add_argument("--marker", default="PF_INPUT_PROOF")
    parser.add_argument("--default-value", default="PF_EDIT_STRING_VALUE")
    parser.add_argument("--open-frames", default="11-17")
    parser.add_argument("--value-frames", default="218-221")
    parser.add_argument("--lead-in", type=int, default=3,
                        help="input lead-in width: replay frames [ordinal-N .. ordinal+1] before the commit. "
                             "Widen (e.g. 30) to test the cumulative-state hypothesis — the write-commit may "
                             "be gated on form state the frame-skipping session never builds (card 79).")
    parser.add_argument("--commit-frames", default="",
                        help="frames (e.g. 471-474) to replay AFTER the input SET to trigger the COMMIT — a "
                             "focus-change to ANOTHER field. The genuine value-commit is this focus-change, "
                             "NOT the SET (card 80 frame-diff). Empty = card-79 behavior (SET only, no commit).")
    parser.add_argument("--reseq", action="store_true",
                        help="rewrite the binary message counter (offset 19-20 LE) of the input+commit frames "
                             "so they CONTINUE the live session's sequence (frame4_sequence + last-read-delta "
                             "+1, +2, ...). The genuine frames carry their own session's lower counter → a "
                             "backwards sequence the client ignores; monotonic-increasing is the card-80 Fork-3 fix.")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir(args.capture_dir, repo_root))
    templates = ProtocolTemplates.load(args.manager_templates.resolve())
    synthesized = synthesize_bootstrap()
    output_dir = (
        args.output_dir or repo_root / "runtime" / "protocol-research" / "effect-probe" / timestamp_name()
    ).resolve()

    # action capture + its captured GUIDs (to rebind the input frame to the live open form)
    action_cap = resolve_capture_dir(args.action_capture, repo_root)
    chunks = read_capture_chunks(action_cap)
    action_mgr = select_chunks(chunks, MANAGER_TO_CLIENT)
    action_cli = select_chunks(chunks, CLIENT_TO_MANAGER)
    captured_mfg = None
    captured_sfg = None
    for chunk in action_cli:
        captured_mfg = extract_managed_form_guid(chunk["payload"]) or captured_mfg
        captured_sfg = extract_secondary_frame_guid(chunk["payload"]) or captured_sfg
    resolver = build_single_session_action_resolver(
        action_mgr,
        captured_mfg,
        captured_input_value=args.marker,
        captured_secondary_frame_guid=captured_sfg,
    )

    def rng(spec: str) -> list[int]:
        lo, _, hi = spec.partition("-")
        return list(range(int(lo), int(hi) + 1))

    report: dict = {"schema": "card79.effect-probe.v1", "captured_action_mfg": captured_mfg, "captured_action_sfg": captured_sfg}
    with TestClientSession(host=args.host, port=args.port) as session:
        handle = session.open_and_bootstrap(
            bootstrap=bootstrap, templates=templates, output_dir=output_dir, synthesized=synthesized
        )

        def read_segment(label: str) -> tuple[str | None, bytes]:
            before = len(handle.state.received_stream)
            handle.run_segment(rng(args.value_frames), query_id="form-element-details")
            blob = bytes(handle.state.received_stream[before:])
            return value_after(blob), blob

        # 1) open the fixture form
        handle.run_segment(rng(args.open_frames), query_id="form-element-details")
        report["live_managed_form_guid"] = handle.state.managed_form_guid
        report["live_secondary_frame_guid"] = handle.state.secondary_frame_guid

        # 2) read the default value
        default_read, blob1 = read_segment("read-default")
        report["read_default_value"] = default_read

        # 3) input a new value (rebound to the live open form). The capture's input is a multi-frame
        # sequence: a FOCUS/activate on the field, a value-read pair, then the input COMMIT pair. Replay
        # the full lead-in (frames [ordinal-3 .. ordinal+1] = focus..commit) with plain GUID substitution
        # (the captured value is already the marker, so no value retarget is needed). The field must be
        # the active/focused element before the input lands.
        ordinal = find_marker_ordinal(action_mgr, args.marker)
        report["input_ordinal"] = ordinal
        live_mfg = handle.state.managed_form_guid
        live_sfg = handle.state.secondary_frame_guid

        def rebind(frame: bytes) -> bytes:
            out = frame
            if captured_mfg and live_mfg:
                out = substitute_guid_all_encodings(out, captured_mfg, live_mfg)
            if captured_sfg and live_sfg:
                out = substitute_guid_all_encodings(out, captured_sfg, live_sfg)
            return out

        # reseq: continue the live session's binary message counter (offset 19-20 LE). Last read frame's
        # delta is 217 (value-frames 218-221), so the next live sequence = frame4_sequence + 218, then +1 per
        # sent input/commit frame. The genuine frames' own counter is lower → backwards → ignored; this fixes it.
        reseq = {"next": ((handle.state.frame4_sequence or 0) + 218) & 0xFFFF}
        report["reseq_enabled"] = bool(args.reseq)
        report["reseq_start"] = reseq["next"] if args.reseq else None

        def prep(frame: bytes) -> bytes:
            out = rebind(frame)
            if args.reseq and len(out) >= 21:
                buf = bytearray(out)
                buf[19:21] = (reseq["next"] & 0xFFFF).to_bytes(2, "little")
                reseq["next"] += 1
                out = bytes(buf)
            return out

        lead_in = list(range(ordinal - args.lead_in, ordinal + 2))  # focus, read pair, input commit pair
        report["input_lead_in_frames"] = [i + 1 for i in lead_in]
        accepts = []
        action_marker_seen = []
        for i in lead_in:
            before = len(handle.state.received_stream)
            summary = handle.run_action(prep(action_mgr[i]["payload"]), query_id=f"input-{i+1}")
            resp = bytes(handle.state.received_stream[before:])
            accepts.append(bool(summary.get("accepted")))
            action_marker_seen.append(has_value_token(resp, args.marker))
        report["action_accepted"] = all(accepts)
        report["action_accepts"] = accepts
        report["action_response_has_marker"] = action_marker_seen

        # 3b) COMMIT (card 80 fix): replay a focus-change to ANOTHER field. The card-79 lead-in stops at
        # the SET (ordinal+1) and never moves focus off the field, so the edit-text is never committed to
        # the field VALUE. The genuine commit is exactly this focus-change (frame-diff 2026-06-16: SET and
        # focus-change both carry no off-wire token; the commit is the SEQUENCE). Replaying an activate of
        # e.g. PF_EDIT_NUMBER (rebound) makes the server commit PF_EDIT_STRING.
        if args.commit_frames:
            commit_idx = rng(args.commit_frames)
            report["commit_frames"] = [i + 1 for i in commit_idx]
            commit_accepts = []
            for i in commit_idx:
                summary = handle.run_action(prep(action_mgr[i]["payload"]), query_id=f"commit-{i+1}")
                commit_accepts.append(bool(summary.get("accepted")))
            report["commit_accepted"] = all(commit_accepts)
            report["commit_accepts"] = commit_accepts

        # 4) read the value again
        new_read, blob2 = read_segment("read-after-input")
        report["read_after_input_value"] = new_read

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "read_default.bin").write_bytes(blob1)
    (output_dir / "read_after_input.bin").write_bytes(blob2)

    # 5) verdict
    report["default_seen_before"] = has_value_token(blob1, args.default_value)
    report["marker_seen_before"] = has_value_token(blob1, args.marker)
    report["default_seen_after"] = has_value_token(blob2, args.default_value)
    report["marker_seen_after"] = has_value_token(blob2, args.marker)
    report["effect_verified"] = bool(
        report["default_seen_before"] and not report["marker_seen_before"]
        and report["marker_seen_after"] and not report["default_seen_after"]
    )
    report["status"] = "passed" if report["effect_verified"] else "effect-not-verified"

    (output_dir / "effect_probe_result.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["effect_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
