#!/usr/bin/env python3
"""Card 78 Phase A live spike: in ONE synthesized (capture-free) session, bootstrap → navigate/read to
the fixture form → execute an ACTION (input) via SessionHandle.run_action with the captured->live
managed-form-GUID rebinder. No Vanessa. Proves an action can run in the synthesized session
(client accepts it, no reset)."""

from __future__ import annotations

import argparse
import json
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
from qa_mcp.protocol.session import extract_managed_form_guid
from qa_mcp.scenario.model import Step
from qa_mcp.scenario.replay import build_single_session_action_resolver


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=15381)
    parser.add_argument("--capture-dir", default="tm-v1-ro-batchQ3")
    parser.add_argument("--manager-templates", type=Path, required=True)
    parser.add_argument("--action-capture", default="fixture-input-capture")
    parser.add_argument("--marker", default="PF_INPUT_PROOF")
    parser.add_argument("--kind", default="input_text", help="action step kind (input_text / click_button / ...)")
    parser.add_argument("--ordinal", type=int, default=None, help="explicit manager-frame ordinal of the command (when the marker is not unique)")
    parser.add_argument("--verify-value", help="Card 78 dir2: after the action, replay the value-read frames and assert this value is present (read-after-write effect verification)")
    parser.add_argument("--verify-frames", default="218-221", help="manager-frame range (a-b) of the value-read (ПолучитьПредставлениеДанных) to replay after the action")
    parser.add_argument("--verify-default", help="the field's default value (asserted to be ABSENT after the action, proving the value really changed)")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir(args.capture_dir, repo_root))
    templates = ProtocolTemplates.load(args.manager_templates.resolve())
    synthesized = synthesize_bootstrap()

    action_cap = resolve_capture_dir(args.action_capture, repo_root)
    chunks = read_capture_chunks(action_cap)
    action_mgr = select_chunks(chunks, MANAGER_TO_CLIENT)
    action_cli = select_chunks(chunks, CLIENT_TO_MANAGER)
    captured_mfg = None
    for chunk in action_cli:
        guid = extract_managed_form_guid(chunk["payload"])
        if guid:
            captured_mfg = guid
    marker_ordinals = {args.marker: args.ordinal} if args.ordinal is not None else None
    resolver = build_single_session_action_resolver(
        action_mgr, captured_mfg, captured_input_value=(args.marker if args.kind == "input_text" else None),
        marker_ordinals=marker_ordinals,
    )

    output_dir = (
        args.output_dir or repo_root / "runtime" / "protocol-research" / "action-session-spike" / timestamp_name()
    ).resolve()

    report: dict = {"schema": "card78.action-session-spike.v1", "captured_managed_form_guid": captured_mfg}
    with TestClientSession(host=args.host, port=args.port) as session:
        handle = session.open_and_bootstrap(
            bootstrap=bootstrap, templates=templates, output_dir=output_dir, synthesized=synthesized
        )
        report["bootstrap_ack_guid"] = handle.state.ack_guid
        # navigate/read to reach the fixture form (advance the cursor + learn the live managed-form GUID)
        nav1 = handle.run_segment([11], query_id="active-window-context")
        nav2 = handle.run_segment(list(range(12, 18)), query_id="form-summary")
        report["nav"] = [
            {"name": "active-window", "status": nav1.status, "frames": len(nav1.frames)},
            {"name": "form-summary", "status": nav2.status, "frames": len(nav2.frames)},
        ]
        report["live_managed_form_guid"] = handle.state.managed_form_guid
        # ACTION: input into PF_EDIT_STRING (identity retarget — proves the command is accepted live)
        step_params = {"old_value": args.marker, "new_value": args.marker} if args.kind == "input_text" else {}
        step = Step(kind=args.kind, name=f"{args.kind}-action", marker=args.marker, params=step_params)
        payload, rebinder = resolver(step, handle)
        summary = handle.run_action(payload, query_id=f"{args.kind}-action", rebinder=rebinder)
        report["action"] = summary
        # Card 78 dir2: dump the action RESPONSE so we can check whether it reflects the effect.
        recv = summary.get("recv_bytes", 0)
        action_response = bytes(handle.state.received_stream[-recv:]) if recv else b""
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "action_response.bin").write_bytes(action_response)
        for probe in ("PF_INPUT_PROOF", "PF_EDIT_STRING", "PF_LAST_ACTION", "PF_ACTION_COUNTER"):
            report.setdefault("response_markers", {})[probe] = (
                probe.encode("utf-8") in action_response or probe.encode("utf-16le") in action_response
            )
        # Card 78 dir2: VERIFY THE EFFECT — read element details (frames 101..106, > cursor) AFTER the
        # action and check the field's live value reflects the input (read-after-write, in-session).
        if args.verify_value:
            before = len(handle.state.received_stream)
            lo, _, hi = args.verify_frames.partition("-")
            verify_frames = list(range(int(lo), int(hi) + 1))
            verify = handle.run_segment(verify_frames, query_id="form-element-details")
            verify_bytes = bytes(handle.state.received_stream[before:])
            (output_dir / "verify_read_response.bin").write_bytes(verify_bytes)
            def _present(s: str) -> bool:
                return s.encode("utf-8") in verify_bytes or s.encode("utf-16le") in verify_bytes
            report["verify"] = {
                "status": verify.status,
                "expected_value_present": _present(args.verify_value),
                "default_value_present": _present(args.verify_default) if args.verify_default else None,
            }
            report["effect_confirmed"] = report["verify"]["expected_value_present"]

    report["status"] = "ok" if report.get("action", {}).get("accepted") else "failed"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "action_session_spike_result.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
