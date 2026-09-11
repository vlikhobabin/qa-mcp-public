#!/usr/bin/env python3
"""Replay a manager-fixture marker request against a running 1C TestClient."""

from __future__ import annotations

import argparse
import base64
import json
import secrets
import sys
import uuid
from pathlib import Path
from typing import Any

from python_manager_client import (
    BootstrapFrameRenderer,
    CaptureBootstrap,
    TestClientSession,
    adapt_manager_header_guid,
    extract_client_ack_guid,
    manager_frame_sequence,
    preview_hex,
    read_available,
    replace_body_ranges,
    repo_root_from_script,
    response_summary,
    sha256_hex,
    timestamp_name,
    utc_now,
)

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import report_manager_fixture_v1 as manager_report  # noqa: E402


DEFAULT_CAPTURE_ID = "20260605-live-full-readonly-bootstrap-second-boundary-guard"


def resolve_capture_dir(value: str | Path, repo_root: Path) -> Path:
    path = Path(value)
    if path.exists():
        return path.resolve()
    candidate = repo_root / "runtime" / "protocol-research" / "captures" / str(value)
    if candidate.exists():
        return candidate.resolve()
    raise FileNotFoundError(f"Capture directory not found: {value}")


def read_manifest_command(capture_dir: Path, case_id: str) -> dict[str, Any]:
    manifest = manager_report.read_json(capture_dir / "manager_harness_manifest.json")
    for command in manifest.get("commands", []):
        if command.get("case_id") == case_id:
            return dict(command)
    raise KeyError(f"case_id not found in manager harness manifest: {case_id}")


def selected_chunks_for_case(capture_dir: Path, case_id: str) -> list[dict[str, Any]]:
    case_events = manager_report.read_jsonl(capture_dir / "case_events.jsonl")
    traffic_events = manager_report.read_jsonl(capture_dir / "traffic.jsonl")
    pairs = manager_report.event_pairs_by_case(case_events)
    pair = pairs.get(case_id) or {}
    before = manager_report.parse_timestamp((pair.get("before") or {}).get("timestamp"))
    after = manager_report.parse_timestamp((pair.get("after") or {}).get("timestamp"))
    if before is None or after is None:
        raise RuntimeError(f"case {case_id} does not have before/after event timestamps")
    before, after, _adjustment = manager_report.effective_chunk_window(before, after)
    return manager_report.traffic_chunks_in_window(manager_report.chunk_events(traffic_events), before, after)


def first_manager_payload_for_case(capture_dir: Path, case_id: str) -> bytes:
    payloads = manager_payloads_for_case(capture_dir, case_id)
    if payloads:
        return payloads[0]
    raise RuntimeError(f"case {case_id} does not have manager_to_client chunks")


def payload_for_chunk(chunk: dict[str, Any]) -> bytes:
    payload_b64 = chunk.get("payload_b64")
    if payload_b64:
        return base64.b64decode(str(payload_b64))
    aggregate_path = Path(str(chunk["aggregate_path"]))
    with aggregate_path.open("rb") as file_obj:
        file_obj.seek(int(chunk["aggregate_offset"]))
        return file_obj.read(int(chunk["byte_count"]))


def manager_payloads_for_case(capture_dir: Path, case_id: str) -> list[bytes]:
    payloads: list[bytes] = []
    for chunk in selected_chunks_for_case(capture_dir, case_id):
        if chunk.get("direction") == manager_report.MANAGER_TO_CLIENT:
            payloads.append(payload_for_chunk(chunk))
    return payloads


def render_marker_frame(template_payload: bytes, ack_guid: str, frame4_sequence: int, delta: int) -> tuple[bytes, list[dict[str, Any]]]:
    replacements = {
        2: uuid.UUID(ack_guid).bytes_le,
        19: (frame4_sequence + delta).to_bytes(2, byteorder="little"),
        68: secrets.token_bytes(16),
    }
    rendered, originals = replace_body_ranges(template_payload, replacements)
    return rendered, [
        {
            "name": "ack_guid" if offset == 2 else "sequence" if offset == 19 else "nonce",
            "offset": offset,
            "length": len(value),
            "original_hex": originals[offset],
            "replacement_hex": value.hex(),
            "value": ack_guid if offset == 2 else frame4_sequence + delta if offset == 19 else value.hex(),
        }
        for offset, value in sorted(replacements.items())
    ]


def payload_contains_marker(payload: bytes, marker: str) -> bool:
    if not marker:
        return False
    return marker.encode("utf-8", errors="ignore").lower() in payload.lower()


def marker_text_matches(expected: str, observed: str) -> bool:
    left = expected.strip().lower()
    right = observed.strip().lower()
    return bool(left and right and (left == right or left in right or right in left))


def response_marker_list(payload: bytes, command: dict[str, Any]) -> list[str]:
    markers: list[str] = []
    for marker in [command.get("target_marker"), command.get("expected_marker")]:
        marker_text = str(marker or "")
        if marker_text and payload_contains_marker(payload, marker_text) and marker_text not in markers:
            markers.append(marker_text)
    for token in manager_report.semantic_payload_tokens(payload):
        if token not in markers:
            markers.append(token)
    return markers


def merged_markers(frames: list[dict[str, Any]], label: str) -> list[str]:
    markers: list[str] = []
    for frame in frames:
        if frame.get("label") != label:
            continue
        for marker in frame.get("response_markers") or []:
            marker_text = str(marker)
            if marker_text not in markers:
                markers.append(marker_text)
    return markers


def write_step_bytes(output_dir: Path, name: str, payload: bytes) -> None:
    steps_dir = output_dir / "steps"
    steps_dir.mkdir(parents=True, exist_ok=True)
    (steps_dir / name).write_bytes(payload)


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from_script()
    capture_dir = resolve_capture_dir(args.capture_dir, repo_root)
    bootstrap = CaptureBootstrap.load(capture_dir)
    command = read_manifest_command(capture_dir, args.case_id)
    expected_marker = args.expected_marker or str(command.get("expected_marker") or command.get("target_marker") or "")

    output_dir = args.output_dir
    if output_dir is None:
        output_dir = repo_root / "runtime" / "protocol-research" / "manager-fixture-marker-probe" / timestamp_name()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    events: list[dict[str, Any]] = []
    frames: list[dict[str, Any]] = []
    sent_stream = bytearray()
    received_stream = bytearray()
    active_window_template = first_manager_payload_for_case(capture_dir, "tm-v1-active-window")
    marker_templates = manager_payloads_for_case(capture_dir, args.case_id)
    if not marker_templates:
        raise RuntimeError(f"case {args.case_id} does not have manager_to_client chunks")
    if args.replay_mode == "first":
        marker_templates = marker_templates[:1]
    elif args.max_case_frames is not None:
        marker_templates = marker_templates[: args.max_case_frames]
    ack_guid: str | None = None
    frame4_sequence: int | None = None

    manifest = {
        "schema": "manager-fixture-marker-probe.manifest.v1",
        "started_at": utc_now(),
        "capture_dir": str(capture_dir),
        "case_id": args.case_id,
        "query": "manager-fixture-marker",
        "target_marker": command.get("target_marker"),
        "expected_marker": expected_marker,
        "target_host": args.host,
        "target_port": args.port,
        "replay_mode": args.replay_mode,
        "case_manager_frame_count": len(marker_templates),
        "max_case_frames": args.max_case_frames,
        "warmup_active_window": bool(args.warmup_active_window),
        "output_dir": str(output_dir),
    }
    (output_dir / "probe_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    with TestClientSession(
        host=args.host,
        port=args.port,
        connect_timeout_sec=args.connect_timeout_sec,
        read_timeout_sec=args.read_timeout_sec,
        idle_timeout_sec=args.idle_timeout_sec,
    ) as session:
        initial = session.read_initial()
        received_stream.extend(initial)
        write_step_bytes(output_dir, "initial_read.bin", initial)
        events.append({"ts": utc_now(), "event": "initial_read", "byte_count": len(initial), "sha256": sha256_hex(initial) if initial else ""})

        for frame_index in range(1, 6):
            captured = bootstrap.captured_frame(frame_index)
            replacements: list[dict[str, Any]] = []
            source = "captured"
            payload = captured
            if frame_index == 4:
                if ack_guid is None:
                    raise RuntimeError("Cannot render frame 4 before ACK GUID is observed")
                payload, original_guid = adapt_manager_header_guid(captured, ack_guid)
                frame4_sequence = manager_frame_sequence(captured)
                replacements = [{"name": "ack_guid", "original": original_guid, "replacement": ack_guid}]
                source = "captured_text_template"
            elif frame_index == 5:
                if ack_guid is None or frame4_sequence is None:
                    raise RuntimeError("Cannot render frame 5 before frame 4 state is known")
                rendered = BootstrapFrameRenderer.render_frame5(captured, ack_guid, frame4_sequence)
                payload = rendered.payload
                replacements = rendered.replacements
                source = rendered.source

            write_step_bytes(output_dir, f"sent_{frame_index:03d}_manager_to_client.bin", payload)
            session.socket.sendall(payload)
            sent_stream.extend(payload)
            events.append(
                {
                    "ts": utc_now(),
                    "event": "sent",
                    "send_index": frame_index,
                    "source": source,
                    "byte_count": len(payload),
                    "sha256": sha256_hex(payload),
                    "head_hex": preview_hex(payload),
                    "replacements": replacements,
                }
            )
            response = read_available(session.socket, args.read_timeout_sec, args.idle_timeout_sec)
            write_step_bytes(output_dir, f"response_after_send_{frame_index:03d}_client_to_manager.bin", response)
            received_stream.extend(response)
            events.append(
                {
                    "ts": utc_now(),
                    "event": "response",
                    "after_send_index": frame_index,
                    "byte_count": len(response),
                    "sha256": sha256_hex(response) if response else "",
                    "head_hex": preview_hex(response),
                }
            )
            if frame_index == 3:
                ack_guid = extract_client_ack_guid(response)
                events.append({"ts": utc_now(), "event": "observed_ack_guid", "after_send_index": frame_index, "ack_guid": ack_guid})

        if ack_guid is None or frame4_sequence is None:
            raise RuntimeError("Handshake did not produce ACK GUID and frame 4 sequence")

        marker_frames: list[tuple[str, int, int, bytes]] = []
        if args.warmup_active_window:
            marker_frames.append(("warmup-active-window", 0, 2, active_window_template))
        first_marker_delta = 3 if args.warmup_active_window else 2
        for ordinal, marker_template in enumerate(marker_templates, start=1):
            marker_frames.append((args.case_id, ordinal, first_marker_delta + ordinal - 1, marker_template))

        for label, ordinal, delta, template_payload in marker_frames:
            payload, replacements = render_marker_frame(template_payload, ack_guid, frame4_sequence, delta)
            send_index = 4 + delta
            suffix = label if ordinal == 0 else f"{label}_{ordinal:03d}"
            write_step_bytes(output_dir, f"sent_{send_index:03d}_{suffix}_manager_to_client.bin", payload)
            session.socket.sendall(payload)
            sent_stream.extend(payload)
            events.append(
                {
                    "ts": utc_now(),
                    "event": "sent",
                    "send_index": send_index,
                    "label": label,
                    "case_frame_ordinal": ordinal or None,
                    "source": "manager_fixture_marker_template",
                    "byte_count": len(payload),
                    "sha256": sha256_hex(payload),
                    "head_hex": preview_hex(payload),
                    "replacements": replacements,
                }
            )
            response = read_available(session.socket, args.read_timeout_sec, args.idle_timeout_sec)
            write_step_bytes(output_dir, f"response_after_send_{send_index:03d}_{suffix}_client_to_manager.bin", response)
            received_stream.extend(response)
            summary = response_summary(send_index, response, replacements)
            summary["label"] = label
            summary["case_frame_ordinal"] = ordinal or None
            summary["response_markers"] = response_marker_list(response, command)
            frames.append(summary)
            events.append(
                {
                    "ts": utc_now(),
                    "event": "response",
                    "after_send_index": send_index,
                    "label": label,
                    "case_frame_ordinal": ordinal or None,
                    "byte_count": len(response),
                    "sha256": sha256_hex(response) if response else "",
                    "head_hex": preview_hex(response),
                    "response_markers": summary["response_markers"],
                }
            )

    (output_dir / "sent_manager_to_client.bin").write_bytes(bytes(sent_stream))
    (output_dir / "received_client_to_manager.bin").write_bytes(bytes(received_stream))
    manager_report.write_jsonl(output_dir / "probe_events.jsonl", events)

    response_markers = merged_markers(frames, args.case_id)
    marker_observed = any(marker_text_matches(expected_marker, str(marker)) for marker in response_markers)
    probe_status = "accepted" if marker_observed else "rejected"
    result = {
        "schema": "protocol-case-probe-evidence.v1",
        "kind": "direct_python_manager_marker_replay",
        "status": "ok",
        "probe_status": probe_status,
        "case_id": args.case_id,
        "query": "manager-fixture-marker",
        "capture_dir": str(capture_dir),
        "output_dir": str(output_dir),
        "ack_guid": ack_guid,
        "frame4_sequence": frame4_sequence,
        "replay_mode": args.replay_mode,
        "case_manager_frame_count": len(marker_templates),
        "sent_byte_count": len(sent_stream),
        "received_byte_count": len(received_stream),
        "target_marker": command.get("target_marker"),
        "expected_marker": expected_marker,
        "response_markers": response_markers,
        "response_marker_count": len(response_markers),
        "marker_observed": marker_observed,
        "frames": frames,
        "finished_at": utc_now(),
        "notes": "Read-only marker replay uses captured manager-fixture request shape and dynamic ACK/sequence/nonce replacement.",
    }
    (output_dir / "manager_fixture_marker_probe_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=15381)
    parser.add_argument("--capture-dir", default=DEFAULT_CAPTURE_ID)
    parser.add_argument("--case-id", default="tm-v1-active-form")
    parser.add_argument("--expected-marker", default=None)
    parser.add_argument("--replay-mode", choices=["first", "window"], default="first")
    parser.add_argument("--max-case-frames", type=int)
    parser.add_argument("--warmup-active-window", action="store_true", default=True)
    parser.add_argument("--no-warmup-active-window", action="store_false", dest="warmup_active_window")
    parser.add_argument("--connect-timeout-sec", type=float, default=10.0)
    parser.add_argument("--read-timeout-sec", type=float, default=5.0)
    parser.add_argument("--idle-timeout-sec", type=float, default=0.25)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    result = run_probe(parse_args())
    if result.get("status") == "ok":
        if "--json" in sys.argv:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"probe_status={result['probe_status']}")
            print(f"output_dir={result['output_dir']}")
            print(f"response_markers={result['response_markers']}")
        return 0 if result.get("probe_status") == "accepted" else 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
