#!/usr/bin/env python3
"""Card 74 Phase 3 step 2: drive a live ACTION scenario via the scenario action registry.

No Vanessa: builds renderers from a scenario's action steps (qa_mcp.scenario.replay.
build_action_renderers → render_action) and replays the captured manager flow live with GUID
rebinding (qa_mcp.protocol.native_mutation.run_replay_with_renderers). The captured flow supplies
the command templates (write-from-capture); the scenario re-targets them parametrically.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from replay_probe import (  # type: ignore  # noqa: E402
    CLIENT_TO_MANAGER,
    MANAGER_TO_CLIENT,
    read_capture_chunks,
    select_chunks,
    timestamp_name,
)
from qa_mcp.protocol.native_mutation import build_poll_skip_set, run_replay_with_renderers  # noqa: E402
from qa_mcp.scenario import Scenario  # noqa: E402
from qa_mcp.scenario.replay import build_action_renderers  # noqa: E402

# Default = the proven warehouse navigation flow, re-targeted parametrically (identity row by
# default → zero-divergence baseline that proves the bridge drives the live replay).
DEFAULT_SCENARIO = {
    "name": "native-action-warehouse-nav",
    "steps": [
        {"kind": "form_command", "name": "open-list", "marker": "e1cib/list/"},
        {"kind": "select_row", "name": "select-row", "marker": "Средний",
         "params": {"old_value": "Средний", "new_value": "Средний"}},
        {"kind": "form_command", "name": "open-card", "marker": "Изменить"},
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture_dir", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=15382)
    parser.add_argument("--scenario", type=Path)
    parser.add_argument("--keep-every-poll", type=int, default=1)
    parser.add_argument("--max-ordinal", type=int, default=None,
                        help="skip all manager ordinals > N (bound the replay to the nav+action prefix, "
                             "e.g. to stop before a write — safe nav-only proof, also avoids the long tail)")
    parser.add_argument("--read-timeout-sec", type=float, default=6.0)
    parser.add_argument("--idle-timeout-sec", type=float, default=1.5)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    chunks = read_capture_chunks(args.capture_dir.resolve())
    manager_chunks = select_chunks(chunks, MANAGER_TO_CLIENT)
    client_chunks = select_chunks(chunks, CLIENT_TO_MANAGER)

    scenario_data = json.loads(args.scenario.read_text(encoding="utf-8")) if args.scenario else DEFAULT_SCENARIO
    scenario = Scenario.from_dict(scenario_data)
    renderers, plan = build_action_renderers(manager_chunks, scenario.steps)

    skip_ordinals = build_poll_skip_set(manager_chunks, keep_every=args.keep_every_poll) if args.keep_every_poll > 1 else set()
    if args.max_ordinal is not None:
        skip_ordinals = set(skip_ordinals) | {i for i in range(len(manager_chunks)) if i > args.max_ordinal}

    summary = run_replay_with_renderers(
        host=args.host,
        port=args.port,
        manager_chunks=manager_chunks,
        client_chunks=client_chunks,
        renderers=renderers,
        skip_ordinals=skip_ordinals,
        read_timeout_sec=args.read_timeout_sec,
        idle_timeout_sec=args.idle_timeout_sec,
    )

    report = {
        "schema": "card74.native-action-scenario.v1",
        "scenario": scenario.name,
        "plan": plan,
        "diverged_at_send_index": summary.get("diverged_at_send_index"),
        "frames_sent": summary.get("frames_sent"),
        "exchanges_with_response": summary.get("exchanges_with_response"),
        "status": "ok" if summary.get("diverged_at_send_index") is None and all(p["ordinal"] is not None for p in plan) else "failed",
    }
    out_dir = (args.output_dir or args.capture_dir / "native-action-scenario" / timestamp_name()).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "action_scenario_result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
