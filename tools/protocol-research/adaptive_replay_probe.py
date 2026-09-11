"""Adaptive full-flow replay of a captured TestManager session to a live TestClient.

Unlike ``replay_probe.py`` (frame-index tuned for the short read bootstrap), this
replays an arbitrary-length captured manager command stream and learns the live
per-session GUIDs as they appear, substituting them into every subsequent
command in all encodings (ASCII path text, UTF-16LE path text and little-endian
UUID bytes).

Learning is by first-appearance order: the k-th distinct GUID seen in the
captured client responses maps to the k-th distinct GUID seen in the live client
responses. For a deterministic flow (same object-creation order) this rebinds
SecondaryFrame / ManagedForm / ack GUIDs without per-frame configuration.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import uuid
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from qa_mcp.protocol.native_mutation import retarget_row_value  # noqa: E402

# Reuse the proven capture/socket/adapt helpers.
from replay_probe import (  # type: ignore
    MANAGER_TO_CLIENT,
    CLIENT_TO_MANAGER,
    adapt_binary_uuid_le,
    read_available,
    read_capture_chunks,
    repo_root_from_script,
    select_chunks,
    sha256_hex,
    timestamp_name,
    utc_now,
)

_GUID_RE = re.compile(
    rb"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)


def ascii_guids_in_order(payload: bytes) -> list[str]:
    """Distinct GUIDs in ASCII text order of first appearance."""

    seen: list[str] = []
    for match in _GUID_RE.findall(payload):
        guid = match.decode("ascii").lower()
        if guid not in seen:
            seen.append(guid)
    return seen


def substitute_guid_all_encodings(payload: bytes, captured: str, live: str) -> bytes:
    if captured == live:
        return payload
    out = payload
    for text in (captured, captured.upper()):
        out = out.replace(text.encode("ascii"), live.encode("ascii"))
        out = out.replace(text.encode("utf-16le"), live.encode("utf-16le"))
    try:
        out, _ = adapt_binary_uuid_le(out, captured, live)
    except ValueError:
        pass
    return out


def apply_guid_map(payload: bytes, guid_map: dict[str, str]) -> bytes:
    out = payload
    for captured, live in guid_map.items():
        out = substitute_guid_all_encodings(out, captured, live)
    return out


def captured_guid_order(client_chunks: list[dict[str, Any]]) -> list[str]:
    order: list[str] = []
    for chunk in client_chunks:
        for guid in ascii_guids_in_order(chunk["payload"]):
            if guid not in order:
                order.append(guid)
    return order


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from_script()
    capture_dir = args.capture_dir.resolve()
    chunks = read_capture_chunks(capture_dir)
    manager_chunks = select_chunks(chunks, MANAGER_TO_CLIENT)
    client_chunks = select_chunks(chunks, CLIENT_TO_MANAGER)
    captured_order = captured_guid_order(client_chunks)

    retarget_substitutions = 0
    retarget_spec = args.retarget_row
    if args.retarget_row_file:
        # robust UTF-8 path (avoids shell arg mojibake for Cyrillic values)
        lines = args.retarget_row_file.read_text(encoding="utf-8").splitlines()
        retarget_spec = f"{lines[0]}:{lines[1]}"
    if retarget_spec:
        old_value, new_value = retarget_spec.split(":", 1)
        manager_chunks, retarget_substitutions = retarget_row_value(
            manager_chunks, old_value, new_value
        )

    out_dir = args.output_dir or (capture_dir / "adaptive-replay" / timestamp_name())
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    send_count = min(args.send_count, len(manager_chunks)) if args.send_count else len(manager_chunks)
    events: list[dict[str, Any]] = []
    guid_map: dict[str, str] = {}
    live_order: list[str] = []

    def learn_from_response(response: bytes) -> list[str]:
        learned: list[str] = []
        for guid in ascii_guids_in_order(response):
            if guid not in live_order:
                live_order.append(guid)
                k = len(live_order) - 1
                if k < len(captured_order):
                    cap = captured_order[k]
                    if cap not in guid_map:
                        guid_map[cap] = guid
                        learned.append(f"{cap}->{guid}")
        return learned

    matched = 0
    diverged_at: int | None = None
    with socket.create_connection((args.host, args.port), timeout=args.connect_timeout_sec) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        initial = read_available(sock, args.read_timeout_sec, args.idle_timeout_sec)
        learn_from_response(initial)
        events.append({"event": "initial_read", "byte_count": len(initial), "learned": []})

        for index in range(send_count):
            captured_payload = manager_chunks[index]["payload"]
            payload = apply_guid_map(captured_payload, guid_map)
            adapted = payload != captured_payload
            sock.sendall(payload)
            response = read_available(sock, args.read_timeout_sec, args.idle_timeout_sec)
            learned = learn_from_response(response)
            expected = client_chunks[index]["payload"] if index < len(client_chunks) else None
            same_len = expected is not None and len(response) == len(expected)
            if response:
                matched += 1
            event = {
                "event": "exchange",
                "send_index": index + 1,
                "adapted": adapted,
                "sent_bytes": len(payload),
                "recv_bytes": len(response),
                "expected_bytes": len(expected) if expected is not None else None,
                "same_length": same_len,
                "guid_map_size": len(guid_map),
                "learned": learned,
            }
            events.append(event)
            if not response:
                diverged_at = index + 1
                if args.stop_on_no_response:
                    break

    summary = {
        "schema": "qa-mcp.adaptive-replay-probe.v1",
        "generated_at": utc_now(),
        "capture_dir": str(capture_dir),
        "output_dir": str(out_dir),
        "target": f"{args.host}:{args.port}",
        "manager_frames_total": len(manager_chunks),
        "captured_guid_count": len(captured_order),
        "exchanges_attempted": min(send_count, len(events)),
        "exchanges_with_response": matched,
        "guid_map_final_size": len(guid_map),
        "diverged_at_send_index": diverged_at,
        "retarget_row": retarget_spec,
        "retarget_substitutions": retarget_substitutions,
    }
    (out_dir / "adaptive_replay_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "adaptive_replay_events.jsonl").write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events), encoding="utf-8"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture_dir", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=15382)
    parser.add_argument("--send-count", type=int, default=0, help="0 = all manager frames")
    parser.add_argument("--connect-timeout-sec", type=float, default=10.0)
    parser.add_argument("--read-timeout-sec", type=float, default=6.0)
    parser.add_argument("--idle-timeout-sec", type=float, default=1.5)
    parser.add_argument("--stop-on-no-response", action="store_true")
    parser.add_argument(
        "--retarget-row",
        default=None,
        help="Re-target navigation to a different row, e.g. 'Средний:Большой' (same length)",
    )
    parser.add_argument(
        "--retarget-row-file",
        type=Path,
        default=None,
        help="UTF-8 file with old value on line 1, new value on line 2 (robust for Cyrillic)",
    )
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    summary = run(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
