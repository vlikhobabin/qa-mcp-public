#!/usr/bin/env python3
"""Card 79 static forensics: characterize the value-INPUT (write-commit) sequence in an action capture.

Pure static analysis (no live TestClient) — portable to Linux. Pins the PF_EDIT_STRING input sequence,
tests the two cheap failure hypotheses for the effect-probe write-commit gap, and reports the capture's
macro-structure so the next LIVE experiment is well-targeted:

  - input sequence:        focus(lowercase ui-id) -> read pair -> set pair (carrying the input marker)
  - hypothesis A (frame):  is there a skipped edit-mode activation frame BEFORE the probe's lead-in?
  - hypothesis B (guid):   does native_effect_probe's GUID extraction match the input frames' form GUIDs?
  - macro-structure:       is the fixture form opened WITHIN this capture (replayable standalone) or
                           pre-opened (so the open must be spliced from another capture)?

Run: PYTHONPATH=src python3 tools/protocol-research/analyze_input_editmode.py [--capture NAME] [--marker M]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from replay_probe import (  # type: ignore  # noqa: E402
    CLIENT_TO_MANAGER,
    MANAGER_TO_CLIENT,
    read_capture_chunks,
    select_chunks,
)
from qa_mcp.protocol.bootstrap import resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.frames import extract_managed_form_guid, extract_secondary_frame_guid  # noqa: E402
from qa_mcp.scenario.replay import find_marker_ordinal  # noqa: E402

GUID = rb"([0-9a-f-]{36})"


def edit_mode_byte(blob: bytes) -> str:
    m = re.search(rb"EditField\[PF_EDIT_STRING\](.)", blob)
    return m.group(1).hex() if m else "-"


def classify(blob: bytes, marker: bytes) -> str:
    if marker in blob:
        return "SET (carries input marker)"
    if b"pf_edit_string" in blob:  # lowercase ui-id == focus / activate command
        return "FOCUS/activate"
    if b"PF_EDIT_STRING" in blob:
        return "READ (data path)"
    return "other"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", default="fixture-input-capture")
    parser.add_argument("--marker", default="PF_INPUT_PROOF")
    parser.add_argument("--lead-in", type=int, default=3, help="probe lead-in: frames before the input ordinal")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    cap = resolve_capture_dir(args.capture, repo_root)
    chunks = read_capture_chunks(cap)
    mgr = select_chunks(chunks, MANAGER_TO_CLIENT)
    cli = select_chunks(chunks, CLIENT_TO_MANAGER)
    marker_b = args.marker.encode("utf-8")

    ordinal = find_marker_ordinal(mgr, args.marker)
    if ordinal is None:
        print(json.dumps({"error": f"marker {args.marker} not found in {args.capture}"}))
        return 2

    # The probe replays range(ordinal - lead_in, ordinal + 2).
    lead_start = ordinal - args.lead_in
    replayed = list(range(lead_start, ordinal + 2))

    sequence = [
        {
            "ordinal": i,
            "len": mgr[i]["byte_count"],
            "edit_mode_byte": edit_mode_byte(mgr[i]["payload"]),
            "op": classify(mgr[i]["payload"], marker_b),
            "in_probe_lead_in": i in replayed,
        }
        for i in range(ordinal - args.lead_in - 3, ordinal + 3)
    ]

    # Hypothesis A — focus/activate frames (lowercase ui-id) anywhere, and any BEFORE the lead-in start.
    focus_frames = [i for i, c in enumerate(mgr) if b"pf_edit_string" in c["payload"]]
    activation_before_lead_in = [i for i in focus_frames if i < lead_start]

    # Hypothesis B — does the probe's GUID extraction match the input frames' form GUIDs?
    captured_mfg = captured_sfg = None
    for ch in cli:
        captured_mfg = extract_managed_form_guid(ch["payload"]) or captured_mfg
        captured_sfg = extract_secondary_frame_guid(ch["payload"]) or captured_sfg
    input_blob = b"".join(mgr[i]["payload"] for i in replayed if 0 <= i < len(mgr))
    input_mfgs = sorted({g.decode() for g in re.findall(rb"ManagedForm\[" + GUID + rb"\]", input_blob)})
    input_sfgs = sorted({g.decode() for g in re.findall(rb"SecondaryFrame\[" + GUID + rb"\]", input_blob)})

    # Macro-structure — is the form opened within this capture, or pre-opened?
    home_frames = sum(1 for c in mgr if b"HomePage" in c["payload"])
    first_secondary = next((i for i, c in enumerate(mgr) if b"SecondaryFrame[" in c["payload"]), None)
    cibutton = any(b"qa mcp protocol fixture v1" in c["payload"] for c in mgr)

    report = {
        "schema": "card79.input-editmode-analysis.v1",
        "capture": args.capture,
        "marker": args.marker,
        "input_ordinal": ordinal,
        "probe_lead_in_replayed": replayed,
        "sequence": sequence,
        "hypothesis_A_missing_activation_frame": {
            "focus_frames_total": focus_frames,
            "activation_before_lead_in": activation_before_lead_in,
            "refuted": not activation_before_lead_in,
            "note": "the only focus/activate frame is the input's own; nothing edit-mode is skipped",
        },
        "hypothesis_B_wrong_guid_rebind": {
            "probe_extracted_mfg": captured_mfg,
            "probe_extracted_sfg": captured_sfg,
            "input_frame_mfgs": input_mfgs,
            "input_frame_sfgs": input_sfgs,
            "mfg_matches": captured_mfg in input_mfgs if captured_mfg else False,
            "sfg_matches": captured_sfg in input_sfgs if captured_sfg else False,
            "refuted": (captured_mfg in input_mfgs) and (captured_sfg in input_sfgs),
        },
        "macro_structure": {
            "homepage_frames": home_frames,
            "first_secondary_frame_ordinal": first_secondary,
            "cibutton_open_present": cibutton,
            "form_pre_opened": home_frames == 0 and not cibutton,
            "note": "pre-opened => cannot replay standalone to OPEN the form; open must be spliced in",
        },
    }
    out = args.output or repo_root / "runtime" / "protocol-research" / "input-editmode-analysis.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # human summary
    print(f"capture={args.capture} marker={args.marker} input_ordinal={ordinal}")
    print(f"probe replays manager frames {replayed}")
    print("input sequence:")
    for s in sequence:
        if s["op"] != "other":
            mark = "*" if s["in_probe_lead_in"] else " "
            print(f"  {mark} M{s['ordinal']:>3} len={s['len']:>4} mode={s['edit_mode_byte']:>2}  {s['op']}")
    A = report["hypothesis_A_missing_activation_frame"]
    B = report["hypothesis_B_wrong_guid_rebind"]
    M = report["macro_structure"]
    print(f"hypothesis A (skipped activation frame): {'REFUTED' if A['refuted'] else 'POSSIBLE'} "
          f"(focus frames={A['focus_frames_total']}, before lead-in={A['activation_before_lead_in']})")
    print(f"hypothesis B (wrong GUID rebind): {'REFUTED' if B['refuted'] else 'POSSIBLE'} "
          f"(extracted mfg={B['probe_extracted_mfg']} sfg={B['probe_extracted_sfg']})")
    print(f"macro-structure: form_pre_opened={M['form_pre_opened']} "
          f"(homepage_frames={M['homepage_frames']}, cibutton_open={M['cibutton_open_present']})")
    print(f"report -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
