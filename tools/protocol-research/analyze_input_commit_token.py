#!/usr/bin/env python3
"""Card 80 static forensics: is the value-INPUT commit gated on a CLIENT-issued live token?

Card 79 proved a verbatim wire-replay of the SET (focus -> read pair -> set pair), rebound for
mfg+sfg GUIDs, is ACKed but never commits (no PF_INPUT_PROOF echo). Two remaining explanations:
  (a) the SET carries a session-variant byte we do NOT rebind (a client-issued edit/generation
      token the client emits in a response and the SET must echo live), or
  (b) the commit does not depend on the SET request bytes at all (manager-side / off-wire state).

This tool distinguishes them OFFLINE on the one genuine SET capture: it finds every byte run the SET
request shares with the client responses that PRECEDE it in the same session, then classifies each as
a KNOWN rebound field (mfg/sfg/ack GUID, in ASCII or binary-LE), an ASCII name/marker, the tail, or a
MYSTERY echo. A MYSTERY echo = candidate unrebound live token => hypothesis (a) (fork-3-via-rebind is
feasible). No mystery echo beyond the known GUIDs => hypothesis (b) (the SET bytes don't carry the gate;
a genuine manager input path is required).

Run: PYTHONPATH=src python3 tools/protocol-research/analyze_input_commit_token.py [--capture NAME] [--marker M]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from replay_probe import (  # type: ignore  # noqa: E402
    CLIENT_TO_MANAGER,
    MANAGER_TO_CLIENT,
    extract_client_ack_guid,
    read_capture_chunks,
    select_chunks,
    split_tail_marker,
)
from qa_mcp.protocol.bootstrap import resolve_capture_dir  # noqa: E402
from qa_mcp.protocol.frames import extract_managed_form_guid, extract_secondary_frame_guid  # noqa: E402
from qa_mcp.scenario.replay import find_marker_ordinal  # noqa: E402

MINLEN = 6  # shortest shared byte run we report (shorter = coincidental protocol bytes)


def guid_forms(guid: str | None) -> list[bytes]:
    """ASCII + binary-LE encodings of a GUID, the way it can appear on the wire."""
    if not guid:
        return []
    forms = [guid.encode("ascii")]
    try:
        import uuid

        forms.append(uuid.UUID(guid).bytes_le)
    except Exception:
        pass
    return forms


def shared_runs(needle_body: bytes, haystack: bytes, minlen: int = MINLEN) -> list[tuple[int, bytes]]:
    """All maximal runs (offset_in_needle, bytes) of length >= minlen that occur in haystack."""
    runs: list[tuple[int, bytes]] = []
    i, n = 0, len(needle_body)
    while i < n:
        # extend the longest run starting at i that is a substring of haystack
        j = i + 1
        best = 0
        while j <= n and needle_body[i:j] in haystack:
            best = j - i
            j += 1
        if best >= minlen:
            runs.append((i, needle_body[i : i + best]))
            i += best
        else:
            i += 1
    return runs


def classify(run: bytes, known: dict[str, list[bytes]]) -> str:
    if len(set(run)) == 1:
        return "filler(constant-byte-run)"
    for label, forms in known.items():
        for form in forms:
            if form and (run in form or form in run):
                return label
    try:
        text = run.decode("ascii")
        if text.isprintable():
            return f"ascii:{text!r}"
    except Exception:
        pass
    return "MYSTERY"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", default="fixture-input-capture")
    parser.add_argument("--marker", default="PF_INPUT_PROOF")
    parser.add_argument("--preceding", type=int, default=12, help="how many preceding client responses to scan")
    parser.add_argument("--minlen", type=int, default=MINLEN)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    cap = resolve_capture_dir(args.capture, repo_root)
    chunks = read_capture_chunks(cap)
    mgr = select_chunks(chunks, MANAGER_TO_CLIENT)
    cli = select_chunks(chunks, CLIENT_TO_MANAGER)

    ordinal = find_marker_ordinal(mgr, args.marker)
    if ordinal is None:
        print(json.dumps({"error": f"marker {args.marker} not found in {args.capture}"}))
        return 2

    set_chunk = mgr[ordinal]
    set_chunk_no = set_chunk["chunk_no"]
    set_body, _tail = split_tail_marker(set_chunk["payload"])

    # known per-session fields we ALREADY rebind (so an echo of these is expected, not a gap)
    mfg = sfg = None
    for c in cli:
        mfg = extract_managed_form_guid(c["payload"]) or mfg
        sfg = extract_secondary_frame_guid(c["payload"]) or sfg
    ack = None
    for c in cli:
        ack = extract_client_ack_guid(c["payload"]) or ack
    known = {
        "known:managed_form_guid": guid_forms(mfg),
        "known:secondary_frame_guid": guid_forms(sfg),
        "known:ack_guid": guid_forms(ack),
        "known:marker": [args.marker.encode("utf-8")],
        "known:field_name": [b"PF_EDIT_STRING", b"pf_edit_string"],
    }

    # client responses that PRECEDE the SET in global session order
    preceding = [c for c in cli if c["chunk_no"] < set_chunk_no]
    window = preceding[-args.preceding :]

    findings = []
    mystery_total = 0
    for c in window:
        resp_body, _ = split_tail_marker(c["payload"])
        for offset, run in shared_runs(set_body, resp_body, args.minlen):
            kind = classify(run, known)
            if kind == "MYSTERY":
                mystery_total += 1
            findings.append(
                {
                    "from_client_chunk_no": c["chunk_no"],
                    "set_offset": offset,
                    "len": len(run),
                    "kind": kind,
                    "hex": run.hex(),
                }
            )

    # de-dup mystery echoes by (set_offset, hex)
    mystery = sorted(
        {(f["set_offset"], f["hex"]) for f in findings if f["kind"] == "MYSTERY"}
    )

    report = {
        "schema": "card80.input-commit-token.v1",
        "capture": args.capture,
        "marker": args.marker,
        "set_ordinal": ordinal,
        "set_chunk_no": set_chunk_no,
        "set_len": len(set_chunk["payload"]),
        "known_fields": {"managed_form_guid": mfg, "secondary_frame_guid": sfg, "ack_guid": ack},
        "preceding_responses_scanned": [c["chunk_no"] for c in window],
        "mystery_echo_count": len(mystery),
        "mystery_echoes": [{"set_offset": o, "hex": h} for o, h in mystery],
        "hypothesis_a_unrebound_live_token": len(mystery) > 0,
        "all_shared_runs": findings,
    }
    out = args.output or repo_root / "runtime" / "protocol-research" / "input-commit-token-analysis.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"capture={args.capture} marker={args.marker} SET=mgr[{ordinal}] chunk_no={set_chunk_no} len={len(set_chunk['payload'])}")
    print(f"known rebound fields: mfg={mfg} sfg={sfg} ack={ack}")
    print(f"scanned {len(window)} preceding client responses: {[c['chunk_no'] for c in window]}")
    print("shared byte runs (SET request <-> preceding client responses):")
    seen = set()
    for f in findings:
        key = (f["set_offset"], f["hex"])
        if key in seen:
            continue
        seen.add(key)
        print(f"  off={f['set_offset']:>3} len={f['len']:>3} {f['kind']:<28} {f['hex'][:48]}")
    verdict = (
        "HYPOTHESIS (a): SET carries MYSTERY client-issued echo(es) -> candidate unrebound live token"
        if mystery
        else "HYPOTHESIS (b): no mystery echo -> SET bytes carry no unrebound token; gate is manager-side"
    )
    print(f"MYSTERY echoes = {len(mystery)} -> {verdict}")
    print(f"report -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
