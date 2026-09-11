#!/usr/bin/env python3
"""Card 79: open the fixture form FIRST, then read the value.

Root cause (proven): the synth session lands on HomePage and never opens the fixture SecondaryFrame,
so value-reads return 0x88 stubs. This probe replays tm-v1-ro-batchQ3's OWN open sequence (frames 8-17:
MainFrame.CI -> CIButton 'qa mcp protocol fixture v1' -> SecondaryFrame opens) on top of the synth
bootstrap, then runs the value-read (218-221) rebound to the freshly-opened fixture ManagedForm GUID.
Expect the active form to flip HomePage->SecondaryFrame and the value-read to carry 0x81 ... 0xfa<len><value>."""

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
FRAME_REF_RE = re.compile(rb"(HomePage|MainFrame|SecondaryFrame)\[([0-9a-f-]{36})\]")


def markers(blob: bytes) -> dict[str, int]:
    c: Counter = Counter()
    for m in EDITFIELD_RE.finditer(blob):
        c[blob[m.end() : m.end() + 1].hex()] += 1
    return dict(c)


def form_refs(blob: bytes) -> list[str]:
    return sorted({f"{m.group(1).decode()}[{m.group(2).decode()[:8]}]" for m in FRAME_REF_RE.finditer(blob)})


def values(blob: bytes) -> list[str]:
    return sorted({t.decode() for t in re.findall(rb"[A-Z_]{3,}_VALUE", blob)})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=15381)
    parser.add_argument("--capture-dir", default="tm-v1-ro-batchQ3")
    parser.add_argument("--manager-templates", type=Path, required=True)
    parser.add_argument("--open-frames", default="11-17", help="contiguous open sequence to send after bootstrap")
    parser.add_argument("--value-frames", default="218-221")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir(args.capture_dir, repo_root))
    templates = ProtocolTemplates.load(args.manager_templates.resolve())
    synthesized = synthesize_bootstrap()
    output_dir = (
        args.output_dir or repo_root / "runtime" / "protocol-research" / "openform-probe" / timestamp_name()
    ).resolve()

    def rng(spec: str) -> list[int]:
        lo, _, hi = spec.partition("-")
        return list(range(int(lo), int(hi) + 1))

    report: dict = {"schema": "card79.openform-probe.v1"}
    with TestClientSession(host=args.host, port=args.port) as session:
        handle = session.open_and_bootstrap(
            bootstrap=bootstrap, templates=templates, output_dir=output_dir, synthesized=synthesized
        )
        report["bootstrap_ack_guid"] = handle.state.ack_guid
        report["bootstrap_managed_form_guid"] = handle.state.managed_form_guid

        def segment(frames: list[int], name: str) -> dict:
            before = len(handle.state.received_stream)
            ctx = handle.run_segment(frames, query_id="form-element-details")
            blob = bytes(handle.state.received_stream[before:])
            return {
                "name": name,
                "frames": f"{frames[0]}..{frames[-1]}",
                "status": ctx.status,
                "recv_bytes": len(blob),
                "form_refs": form_refs(blob),
                "editfield_markers": markers(blob),
                "values": values(blob),
            }

        segs = [segment(rng(args.open_frames), "open-sequence")]
        report["managed_form_guid_after_open"] = handle.state.managed_form_guid
        segs.append(segment(rng(args.value_frames), "value-read"))
        report["segments"] = segs

        whole = bytes(handle.state.received_stream)
        report["session_form_refs"] = form_refs(whole)
        report["session_editfield_markers"] = markers(whole)
        report["session_values"] = values(whole)
        report["secondary_frame_opened"] = any(r.startswith("SecondaryFrame") for r in report["session_form_refs"])
        report["value_mode_on"] = "81" in report["session_editfield_markers"]
        report["pf_edit_string_value_seen"] = "PF_EDIT_STRING_VALUE" in report["session_values"]

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "openform_probe_result.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
