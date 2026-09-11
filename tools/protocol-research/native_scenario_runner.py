#!/usr/bin/env python3
"""Run a read-only scenario through the native Python TestManager (card 74, Phase 1).

No Vanessa Automation in the loop: synthesized capture-free bootstrap + the in-repo
ScenarioRunner. Each step opens a TestClientSession against a live TestClient.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from python_manager_client import (
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
from qa_mcp.scenario import Scenario, ScenarioRunner, transpile_feature
from qa_mcp.scenario.replay import build_single_session_action_resolver

DEFAULT_SCENARIO = {
    "name": "native-readonly-smoke",
    "steps": [
        {"kind": "read_active_window", "name": "active-window", "expect_contains": "HomePage"},
        {"kind": "read_form_summary", "name": "form-summary"},
        {"kind": "read_active_window", "name": "active-window-again", "expect_contains": "HomePage"},
    ],
}

# Single-session steps must be in increasing-frame order (linear-template constraint).
SINGLE_SESSION_SCENARIO = {
    "name": "native-single-session-smoke",
    "steps": [
        {"kind": "read_active_window", "name": "active-window", "expect_contains": "HomePage"},
        {"kind": "read_form_summary", "name": "form-summary"},
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=15381)
    parser.add_argument("--capture-dir", default="tm-v1-ro-batchQ3")
    parser.add_argument("--manager-templates", type=Path, required=True)
    parser.add_argument("--scenario", type=Path, help="scenario JSON; default = built-in read-only smoke")
    parser.add_argument("--feature", type=Path, help="Card 74 Phase 4: a .feature (Gherkin ru) file to transpile + run")
    parser.add_argument(
        "--single-session",
        action="store_true",
        help="Card 74 Phase 2: bootstrap once and run all steps on one socket (no re-bootstrap)",
    )
    parser.add_argument("--action-capture", help="Card 78: capture dir whose action command frames back the action steps (enables action steps in single-session mode)")
    parser.add_argument("--action-input-value", help="Card 78: the value baked into the action capture's input command, so .feature input steps retarget the captured value (not the field name)")
    parser.add_argument("--action-ordinals", help="Card 78: comma-separated marker=ordinal pairs (e.g. 'PF_SHOW_CHOICE_MENU=37') to pin command frames when a marker is not unique (button name in both form desc and the click command)")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--connect-timeout-sec", type=float, default=10.0)
    parser.add_argument("--read-timeout-sec", type=float, default=5.0)
    parser.add_argument("--idle-timeout-sec", type=float, default=0.25)
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir(args.capture_dir, repo_root))
    templates = ProtocolTemplates.load(args.manager_templates.resolve())
    synthesized = synthesize_bootstrap()

    if args.feature:
        results = transpile_feature(args.feature.read_text(encoding="utf-8"))
        if not results:
            raise SystemExit(f"no scenarios found in {args.feature}")
        scenario = results[0].scenario
        if results[0].unmapped:
            print(json.dumps({"unmapped_steps": results[0].unmapped}, ensure_ascii=False))
    elif args.scenario:
        scenario = Scenario.from_dict(json.loads(args.scenario.read_text(encoding="utf-8")))
    else:
        scenario = Scenario.from_dict(SINGLE_SESSION_SCENARIO if args.single_session else DEFAULT_SCENARIO)

    output_dir = (args.output_dir or repo_root / "runtime" / "protocol-research" / "native-scenario" / timestamp_name()).resolve()

    def session_factory() -> TestClientSession:
        return TestClientSession(
            host=args.host,
            port=args.port,
            connect_timeout_sec=args.connect_timeout_sec,
            read_timeout_sec=args.read_timeout_sec,
            idle_timeout_sec=args.idle_timeout_sec,
        )

    action_resolver = None
    if args.action_capture:
        action_cap = resolve_capture_dir(args.action_capture, repo_root)
        action_chunks = read_capture_chunks(action_cap)
        action_mgr = select_chunks(action_chunks, MANAGER_TO_CLIENT)
        captured_mfg = None
        for chunk in select_chunks(action_chunks, CLIENT_TO_MANAGER):
            guid = extract_managed_form_guid(chunk["payload"])
            if guid:
                captured_mfg = guid
        marker_ordinals = None
        if args.action_ordinals:
            marker_ordinals = {}
            for pair in args.action_ordinals.split(","):
                marker, _, ordinal = pair.partition("=")
                marker_ordinals[marker.strip()] = int(ordinal)
        action_resolver = build_single_session_action_resolver(
            action_mgr, captured_mfg, captured_input_value=args.action_input_value, marker_ordinals=marker_ordinals
        )

    runner = ScenarioRunner(
        session_factory=session_factory,
        bootstrap=bootstrap,
        templates=templates,
        output_dir=output_dir,
        synthesized=synthesized,
        action_resolver=action_resolver,
    )
    result = runner.run_single_session(scenario) if args.single_session else runner.run(scenario)
    (output_dir / "scenario_result.json").write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
