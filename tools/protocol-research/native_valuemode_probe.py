#!/usr/bin/env python3
"""Card 79 diagnostic: does sending the form-open/element sweep frames CONTIGUOUSLY (18..106)
flip the synthesized session into the client's value-realization mode (byte 0x81 after EditField,
carrying \\xfa<len><value>) instead of the structure-only mode (byte 0x88) we get when we jump
straight from the form-summary (17) to the value-read (218-221)?

In the original capture, 0x81 (value mode) is present from the FIRST EditField read (mgr frame 40)
and 0x88 NEVER appears. Our skip-replay synth session is globally in 0x88 mode. This probe sends
11 -> 106 contiguously (no skip) and then the value-read 218-221, and reports the byte-after-EditField
distribution per segment, so we can see WHERE/IF value mode turns on."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from python_manager_client import (  # type: ignore
    CaptureBootstrap,
    ProtocolTemplates,
    TestClientSession,
    repo_root_from_script,
    resolve_capture_dir,
    timestamp_name,
)
from qa_mcp.protocol.bootstrap_synth import synthesize_bootstrap

EDITFIELD_RE = re.compile(rb"EditField\[[A-Z_0-9]+\]")


def marker_dist(blob: bytes) -> dict[str, int]:
    c: Counter = Counter()
    for m in EDITFIELD_RE.finditer(blob):
        c[blob[m.end() : m.end() + 1].hex()] += 1
    return dict(c)


def value_tokens(blob: bytes) -> list[str]:
    return sorted({t.decode() for t in re.findall(rb"[A-Z_]{3,}_VALUE", blob)})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=15381)
    parser.add_argument("--capture-dir", default="tm-v1-ro-batchQ3")
    parser.add_argument("--manager-templates", type=Path, required=True)
    parser.add_argument("--realize-to", type=int, default=106, help="send 18..realize_to contiguously")
    parser.add_argument("--value-frames", default="218-221")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir(args.capture_dir, repo_root))
    templates = ProtocolTemplates.load(args.manager_templates.resolve())
    synthesized = synthesize_bootstrap()
    output_dir = (
        args.output_dir or repo_root / "runtime" / "protocol-research" / "valuemode-probe" / timestamp_name()
    ).resolve()

    lo, _, hi = args.value_frames.partition("-")
    value_frames = list(range(int(lo), int(hi) + 1))

    report: dict = {"schema": "card79.valuemode-probe.v1", "realize_to": args.realize_to}
    with TestClientSession(host=args.host, port=args.port) as session:
        handle = session.open_and_bootstrap(
            bootstrap=bootstrap, templates=templates, output_dir=output_dir, synthesized=synthesized
        )
        report["bootstrap_ack_guid"] = handle.state.ack_guid

        def segment(frames: list[int], name: str) -> dict:
            before = len(handle.state.received_stream)
            ctx = handle.run_segment(frames, query_id=name)
            blob = bytes(handle.state.received_stream[before:])
            return {
                "name": name,
                "frames": f"{frames[0]}..{frames[-1]}",
                "status": ctx.status,
                "recv_bytes": len(blob),
                "editfield_markers": marker_dist(blob),
                "value_tokens": value_tokens(blob),
            }

        segs = []
        segs.append(segment([11], "active-window-context"))
        segs.append(segment(list(range(12, 18)), "form-summary"))
        # THE TEST: contiguous form-open/element sweep, no skip
        segs.append(segment(list(range(18, args.realize_to + 1)), "form-element-details"))
        report["live_managed_form_guid"] = handle.state.managed_form_guid
        # now the value-read
        segs.append(segment(value_frames, "form-element-details"))
        report["segments"] = segs

        whole = bytes(handle.state.received_stream)
        report["session_editfield_markers"] = marker_dist(whole)
        report["session_value_tokens"] = value_tokens(whole)
        report["value_mode_on"] = "81" in report["session_editfield_markers"]
        report["pf_edit_string_value_seen"] = "PF_EDIT_STRING_VALUE" in report["session_value_tokens"]

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "valuemode_probe_result.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
