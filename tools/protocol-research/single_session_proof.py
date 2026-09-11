#!/usr/bin/env python3
"""Card 74 Phase 2 proof: bootstrap ONCE, then run multiple operation segments on one socket
(no re-bootstrap), against a live TestClient. Synthesized capture-free bootstrap, no Vanessa."""

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
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=15381)
    parser.add_argument("--capture-dir", default="tm-v1-ro-batchQ3")
    parser.add_argument("--manager-templates", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir(args.capture_dir, repo_root))
    templates = ProtocolTemplates.load(args.manager_templates.resolve())
    synthesized = synthesize_bootstrap()
    output_dir = (args.output_dir or repo_root / "runtime" / "protocol-research" / "single-session" / timestamp_name()).resolve()

    report: dict = {"schema": "card74.single-session-proof.v1", "segments": []}
    with TestClientSession(host=args.host, port=args.port) as session:
        handle = session.open_and_bootstrap(
            bootstrap=bootstrap, templates=templates, output_dir=output_dir, synthesized=synthesized
        )
        report["bootstrap_ack_guid"] = handle.state.ack_guid
        report["bootstrap_frame4_sequence"] = handle.state.frame4_sequence
        # Segment 1: active-window query (frame 11). Segment 2: form-summary continuation (12..17).
        seg1 = handle.run_segment([11], query_id="active-window-context")
        seg2 = handle.run_segment(list(range(12, 18)), query_id="form-summary")
        for name, ctx in (("active-window", seg1), ("form-summary", seg2)):
            report["segments"].append(
                {"name": name, "status": ctx.status, "frame_count": len(ctx.frames), "frame4_sequence": ctx.frame4_sequence}
            )

    report["status"] = "ok" if all(s["status"] == "ok" and s["frame_count"] > 0 for s in report["segments"]) else "failed"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "single_session_result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
