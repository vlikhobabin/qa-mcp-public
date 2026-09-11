"""Compare two protocol runs of the same action by normalized frame hash.

This is the automatic comparison oracle that replaces eyeballing. It isolates
the action-write frames of a ``demo-catalog-mutation`` capture (via the recorded
``phaseTimeline``), normalizes the per-session dynamic identifiers (secondary
frame / managed form GUIDs rendered both as ASCII path text and as little-endian
UUID bytes), and computes a stable ``normalized_hash`` per direction.

Two modes:

- ``stability`` (reference vs reference): confirms the same Vanessa-driven action
  produces the same normalized hash across runs. This is the prerequisite for
  trusting a decoded template.
- ``acceptance`` (reference vs probe): confirms our Python-manager probe of the
  same action reproduces the reference normalized hash and the same typed
  result. A match is an accepted protocol mapping.

Typed results (``preFlag``/``postFlag``/``recoveryFlag``/``status``) are compared
alongside the wire hash so a hash match with a different effect cannot pass.
"""

from __future__ import annotations

import argparse
import base64
import datetime
import hashlib
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

PLACEHOLDER_GUID = "00000000-0000-0000-0000-000000000000"
_GUID_RE = re.compile(
    rb"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)

# Decoded dynamic-field map of the demo-catalog-mutation write frames, verified
# byte-identical across two independent reference runs. See
# docs/protocol-research/evidence/.../decode-findings.md.
MESSAGE_ID_OFFSET = 2
MESSAGE_ID_LENGTH = 16
SEQUENCE_OFFSET = 19
SEQUENCE_LENGTH = 2
NONCE_LENGTH = 16
NONCE_OFFSET_BY_DIRECTION = {
    "manager_to_client": 68,
    "client_to_manager": 30,
}


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ts(value: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_result(capture_dir: Path) -> dict[str, Any]:
    # generic manifest-driven captures write action_capture_result.json; the
    # original warehouse scenario writes demo_catalog_mutation_result.json.
    for name in ("action_capture_result.json", "demo_catalog_mutation_result.json"):
        path = capture_dir / name
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    raise FileNotFoundError(
        f"no action result json (action_capture_result.json / demo_catalog_mutation_result.json) in {capture_dir}"
    )


def load_phase_frames(capture_dir: Path, phase: str) -> list[dict[str, Any]]:
    """Return raw frames whose timestamp falls in the named phase window."""

    result = load_result(capture_dir)
    phases = result["phaseTimeline"]
    window = None
    for i, item in enumerate(phases):
        if item["phase"] == phase:
            start = _ts(item["started_at"])
            end = _ts(phases[i + 1]["started_at"]) if i + 1 < len(phases) else _ts(item["finished_at"])
            window = (start, end)
            break
    if window is None:
        raise KeyError(f"phase {phase} not found in {capture_dir}")

    frames: list[dict[str, Any]] = []
    traffic = capture_dir / "traffic.jsonl"
    with traffic.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("event") != "chunk":
                continue
            ts = _ts(record["ts"])
            if not (window[0] <= ts < window[1]):
                continue
            payload = base64.b64decode(record["payload_b64"]) if record.get("payload_b64") else b""
            frames.append(
                {
                    "direction": record["direction"],
                    "chunk_no": int(record["chunk_no"]),
                    "payload": payload,
                }
            )
    return frames


def session_guids(frames: list[dict[str, Any]]) -> list[str]:
    """Collect the per-session GUIDs a frame stream carries.

    GUIDs appear in two encodings: ASCII path text and UTF-16LE form text. Some
    frames (e.g. a tabular-section delete referencing the managed-form context)
    carry the managed-form GUID *only* as UTF-16LE, so scanning the raw bytes
    with an ASCII regex misses it. We scan both the raw bytes and a UTF-16LE
    decode; ``normalize_payload`` strips whichever encoding actually occurs.
    """

    seen: list[str] = []
    for frame in frames:
        payload = frame["payload"]
        haystacks = [payload]
        try:
            haystacks.append(payload.decode("utf-16le", "ignore").encode("ascii", "ignore"))
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
        for haystack in haystacks:
            for match in _GUID_RE.findall(haystack):
                guid = match.decode("ascii").lower()
                if guid not in seen and guid != PLACEHOLDER_GUID:
                    seen.append(guid)
    return seen


def _zero(buffer: bytearray, offset: int, length: int) -> None:
    n = max(0, min(length, len(buffer) - offset))
    if n > 0:
        buffer[offset : offset + n] = b"\x00" * n


def normalize_payload(payload: bytes, guids: list[str], direction: str | None = None) -> bytes:
    """Normalize a write frame's per-session/per-frame dynamic fields.

    Strips each session GUID (ASCII path text, UTF-16LE path text and
    little-endian UUID bytes). When ``direction`` is given, also zeroes the
    decoded per-frame message id, the sequence and the per-frame nonce so two
    runs of the same action collapse to identical bytes.
    """

    out = payload
    placeholder_ascii = PLACEHOLDER_GUID.encode("ascii")
    placeholder_utf16 = PLACEHOLDER_GUID.encode("utf-16le")
    for guid in guids:
        for text in (guid, guid.upper()):
            out = out.replace(text.encode("ascii"), placeholder_ascii)
            out = out.replace(text.encode("utf-16le"), placeholder_utf16)
        try:
            le = __import__("uuid").UUID(guid).bytes_le
            out = out.replace(le, b"\x00" * 16)
        except ValueError:
            pass

    if direction is None:
        return out

    buffer = bytearray(out)
    _zero(buffer, MESSAGE_ID_OFFSET, MESSAGE_ID_LENGTH)
    _zero(buffer, SEQUENCE_OFFSET, SEQUENCE_LENGTH)
    nonce_offset = NONCE_OFFSET_BY_DIRECTION.get(direction)
    if nonce_offset is not None and len(buffer) >= nonce_offset + NONCE_LENGTH:
        _zero(buffer, nonce_offset, NONCE_LENGTH)
    return bytes(buffer)


def normalized_hashes(frames: list[dict[str, Any]], guids: list[str]) -> dict[str, Any]:
    per_dir: dict[str, hashlib._Hash] = {}
    counts: dict[str, int] = {}
    norm_frames: dict[str, list[bytes]] = {}
    for frame in frames:
        direction = frame["direction"]
        norm = normalize_payload(frame["payload"], guids, direction)
        per_dir.setdefault(direction, hashlib.sha256()).update(norm)
        counts[direction] = counts.get(direction, 0) + 1
        norm_frames.setdefault(direction, []).append(norm)
    return {
        "hash_by_direction": {d: h.hexdigest() for d, h in per_dir.items()},
        "frame_count_by_direction": counts,
        "norm_frames": norm_frames,
    }


def _ordered_chunk_frames(capture_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """All proxy chunk frames per direction, in capture order, with chunk_no."""

    streams: dict[str, list[dict[str, Any]]] = {}
    with (capture_dir / "traffic.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("event") != "chunk":
                continue
            payload = base64.b64decode(record["payload_b64"]) if record.get("payload_b64") else b""
            streams.setdefault(record["direction"], []).append(
                {"chunk_no": int(record["chunk_no"]), "payload": payload}
            )
    return streams


def phase_ordinals(reference_dir: Path, phase: str) -> dict[str, list[int]]:
    """Per-direction ordinal positions of a reference phase's frames.

    The ordinals index into the per-direction capture-order stream, so the same
    positions can be pulled from a probe capture that replayed the same frame
    sequence (which has no ``phaseTimeline`` of its own).
    """

    phase_frames = load_phase_frames(reference_dir, phase)
    phase_chunk_nos = {f["chunk_no"] for f in phase_frames}
    streams = _ordered_chunk_frames(reference_dir)
    ordinals: dict[str, list[int]] = {}
    for direction, frames in streams.items():
        ordinals[direction] = [i for i, f in enumerate(frames) if f["chunk_no"] in phase_chunk_nos]
    return ordinals


def compare_probe_by_ordinal(reference_dir: Path, probe_dir: Path, phase: str) -> dict[str, Any]:
    """Compare a Python-manager probe to a reference at a phase, aligned by ordinal.

    The probe has no ``phaseTimeline``; the reference's phase ordinals select the
    same frames in the probe's capture-order streams. Acceptance is a normalized
    hash match of the selected frames (the probe carries no typed side channel).
    """

    ordinals = phase_ordinals(reference_dir, phase)
    ref_streams = _ordered_chunk_frames(reference_dir)
    probe_streams = _ordered_chunk_frames(probe_dir)

    def select(streams: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
        frames: list[dict[str, Any]] = []
        for direction, idxs in ordinals.items():
            stream = streams.get(direction, [])
            for o in idxs:
                if o < len(stream):
                    frames.append({"direction": direction, "payload": stream[o]["payload"]})
        return frames

    ref_frames = select(ref_streams)
    probe_frames = select(probe_streams)
    ref_norm = normalized_hashes(ref_frames, session_guids(ref_frames))
    probe_norm = normalized_hashes(probe_frames, session_guids(probe_frames))

    directions = sorted(set(ref_norm["hash_by_direction"]) | set(probe_norm["hash_by_direction"]))
    hash_match = {
        d: ref_norm["hash_by_direction"].get(d) == probe_norm["hash_by_direction"].get(d)
        for d in directions
    }
    structural_match = structural_signature(ref_frames) == structural_signature(probe_frames)
    all_hashes_match = bool(hash_match) and all(hash_match.values())
    verdict = "accepted" if (structural_match and all_hashes_match) else (
        "candidate" if structural_match else "mismatch"
    )
    return {
        "schema": "qa-mcp.compare-probe-reference.by-ordinal.v1",
        "generated_at": utc_now(),
        "mode": "probe-ordinal",
        "phase": phase,
        "reference": str(reference_dir),
        "probe": str(probe_dir),
        "phase_ordinal_counts": {d: len(v) for d, v in ordinals.items()},
        "reference_hash_by_direction": ref_norm["hash_by_direction"],
        "probe_hash_by_direction": probe_norm["hash_by_direction"],
        "hash_match_by_direction": hash_match,
        "structural_match": structural_match,
        "all_hashes_match": all_hashes_match,
        "verdict": verdict,
    }


def typed_result(capture_dir: Path) -> dict[str, Any]:
    result = load_result(capture_dir)
    return {
        "preFlag": result.get("preFlag"),
        "postFlag": result.get("postFlag"),
        "recoveryFlag": result.get("recoveryFlag"),
        "status": result.get("status"),
    }


def structural_signature(frames: list[dict[str, Any]]) -> dict[str, list[int]]:
    """Ordered frame byte-sizes per direction — a normalizer-independent shape."""

    sig: dict[str, list[int]] = {}
    for frame in frames:
        sig.setdefault(frame["direction"], []).append(len(frame["payload"]))
    return sig


def residual_diff_count(
    left_frames: list[dict[str, Any]],
    right_frames: list[dict[str, Any]],
    left_guids: list[str],
    right_guids: list[str],
) -> int:
    """Bytes still differing after current normalization, aligned by direction/ordinal.

    This is the remaining dynamic-field surface (e.g. per-frame random nonces)
    not yet covered by the normalizer.
    """

    def by_dir(frames: list[dict[str, Any]]) -> dict[str, list[bytes]]:
        out: dict[str, list[bytes]] = {}
        for frame in frames:
            out.setdefault(frame["direction"], []).append(frame["payload"])
        return out

    left = by_dir(left_frames)
    right = by_dir(right_frames)
    residual = 0
    for direction in set(left) | set(right):
        la = left.get(direction, [])
        lb = right.get(direction, [])
        for i in range(min(len(la), len(lb))):
            pa = normalize_payload(la[i], left_guids, direction)
            pb = normalize_payload(lb[i], right_guids, direction)
            residual += sum(1 for j in range(min(len(pa), len(pb))) if pa[j] != pb[j])
            residual += abs(len(pa) - len(pb))
    return residual


def compare(left_dir: Path, right_dir: Path, phase: str, mode: str) -> dict[str, Any]:
    left_frames = load_phase_frames(left_dir, phase)
    right_frames = load_phase_frames(right_dir, phase)
    left_guids = session_guids(left_frames)
    right_guids = session_guids(right_frames)
    # Normalize each side using its own session GUIDs so structurally identical
    # actions collapse toward the same bytes.
    left_norm = normalized_hashes(left_frames, left_guids)
    right_norm = normalized_hashes(right_frames, right_guids)

    directions = sorted(set(left_norm["hash_by_direction"]) | set(right_norm["hash_by_direction"]))
    hash_match = {
        d: left_norm["hash_by_direction"].get(d) == right_norm["hash_by_direction"].get(d)
        for d in directions
    }
    all_hashes_match = all(hash_match.values()) and bool(hash_match)

    left_sig = structural_signature(left_frames)
    right_sig = structural_signature(right_frames)
    structural_match = left_sig == right_sig

    left_typed = typed_result(left_dir)
    right_typed = typed_result(right_dir)
    typed_match = left_typed == right_typed

    residual = residual_diff_count(left_frames, right_frames, left_guids, right_guids)

    # Graded verdict — never claim full equivalence while the normalized hash
    # still diverges (random nonces remain uncovered by the normalizer).
    if mode == "stability":
        if structural_match and typed_match and all_hashes_match:
            verdict = "fully_stable"
        elif structural_match and typed_match:
            verdict = "structurally_stable"
        else:
            verdict = "divergent"
    else:  # acceptance
        if structural_match and typed_match and all_hashes_match:
            verdict = "accepted"
        elif structural_match and typed_match:
            verdict = "candidate"
        else:
            verdict = "mismatch"

    return {
        "schema": "qa-mcp.compare-probe-reference.v1",
        "generated_at": utc_now(),
        "mode": mode,
        "phase": phase,
        "left": str(left_dir),
        "right": str(right_dir),
        "left_hash_by_direction": left_norm["hash_by_direction"],
        "right_hash_by_direction": right_norm["hash_by_direction"],
        "hash_match_by_direction": hash_match,
        "all_hashes_match": all_hashes_match,
        "structural_signature_left": left_sig,
        "structural_signature_right": right_sig,
        "structural_match": structural_match,
        "residual_dynamic_bytes": residual,
        "left_typed_result": left_typed,
        "right_typed_result": right_typed,
        "typed_result_match": typed_match,
        "left_frame_count_by_direction": left_norm["frame_count_by_direction"],
        "right_frame_count_by_direction": right_norm["frame_count_by_direction"],
        "verdict": verdict,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=Path, help="Reference capture dir")
    parser.add_argument("right", type=Path, help="Second reference (stability) or probe capture dir")
    parser.add_argument("--phase", default="action_write")
    parser.add_argument(
        "--mode",
        choices=("stability", "acceptance", "probe-ordinal"),
        default="stability",
        help="probe-ordinal: right is a Python-manager probe capture aligned to the reference phase by ordinal",
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    if args.mode == "probe-ordinal":
        report = compare_probe_by_ordinal(args.left.resolve(), args.right.resolve(), args.phase)
    else:
        report = compare(args.left.resolve(), args.right.resolve(), args.phase, args.mode)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    print(f"mode={report['mode']} phase={report['phase']} verdict={report['verdict']}")
    print(
        f"structural_match={report['structural_match']}"
        f" typed_result_match={report.get('typed_result_match', 'n/a')}"
        f" all_hashes_match={report['all_hashes_match']}"
        f" residual_dynamic_bytes={report.get('residual_dynamic_bytes', 'n/a')}"
    )
    for d in sorted(report["hash_match_by_direction"]):
        print(f"  {d}: hash_match={report['hash_match_by_direction'][d]}")
    return 0 if report["verdict"] in ("fully_stable", "structurally_stable", "accepted", "candidate") else 1


if __name__ == "__main__":
    raise SystemExit(main())
