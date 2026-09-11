#!/usr/bin/env python3
"""Extract payload strings and nonce echo evidence from protocol captures/replays."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MANAGER_TO_CLIENT = "manager_to_client"
CLIENT_TO_MANAGER = "client_to_manager"
TAIL_MARKER = bytes.fromhex("6653b2a6")
ASCII_STRING_RE = re.compile(rb"[ -~]{5,}")
UI_ASCII_MARKERS = ("MainFrame", "HomePage", "e1cib/", "navigationpoint")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def captures_root(repo_root: Path) -> Path:
    return repo_root / "runtime" / "protocol-research" / "captures"


def resolve_input_path(value: str, repo_root: Path) -> Path:
    path = Path(value)
    if path.exists():
        return path.resolve()
    candidate = captures_root(repo_root) / value
    if candidate.exists():
        return candidate.resolve()
    raise FileNotFoundError(f"Input path not found: {value}")


def strip_tail(payload: bytes) -> bytes:
    if payload.endswith(TAIL_MARKER):
        return payload[: -len(TAIL_MARKER)]
    return payload


def payload_from_record(record: dict[str, Any]) -> bytes:
    payload_b64 = record.get("payload_b64")
    if payload_b64:
        return base64.b64decode(payload_b64)

    aggregate_path = Path(record["aggregate_path"])
    offset = int(record["aggregate_offset"])
    byte_count = int(record["byte_count"])
    with aggregate_path.open("rb") as file_obj:
        file_obj.seek(offset)
        return file_obj.read(byte_count)


def read_capture_payloads(capture_dir: Path) -> tuple[list[bytes], list[bytes]]:
    traffic_path = capture_dir / "traffic.jsonl"
    if not traffic_path.exists():
        raise FileNotFoundError(f"traffic.jsonl not found: {traffic_path}")

    manager: list[bytes] = []
    client: list[bytes] = []
    with traffic_path.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("event") != "chunk":
                continue
            payload = payload_from_record(record)
            if record.get("direction") == MANAGER_TO_CLIENT:
                manager.append(payload)
            elif record.get("direction") == CLIENT_TO_MANAGER:
                client.append(payload)
    return manager, client


def read_replay_events(replay_dir: Path) -> list[dict[str, Any]]:
    events_path = replay_dir / "replay_events.jsonl"
    if not events_path.exists():
        return []
    events: list[dict[str, Any]] = []
    with events_path.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            if line.strip():
                events.append(json.loads(line))
    return events


def replay_replacement_blocks(events: list[dict[str, Any]]) -> dict[int, dict[int, bytes]]:
    by_send: dict[int, dict[int, bytes]] = {}
    for event in events:
        if event.get("event") not in (
            "adapted_binary_manager_frame_blocks",
            "adapted_binary_manager_single_block_frame",
        ):
            continue
        send_index = int(event["send_index"])
        blocks = by_send.setdefault(send_index, {})
        for offset, value in event.get("replacement_blocks", {}).items():
            blocks[int(offset)] = bytes.fromhex(value)
    return by_send


def read_replay_pair(replay_dir: Path, send_index: int) -> tuple[bytes | None, bytes | None, bytes | None]:
    steps_dir = replay_dir / "steps"
    sent_path = steps_dir / f"sent_{send_index:03d}_manager_to_client.bin"
    response_path = steps_dir / f"response_after_send_{send_index:03d}_client_to_manager.bin"
    expected_path = steps_dir / f"expected_after_send_{send_index:03d}_client_to_manager.bin"
    sent = sent_path.read_bytes() if sent_path.exists() else None
    response = response_path.read_bytes() if response_path.exists() else None
    expected = expected_path.read_bytes() if expected_path.exists() else None
    return sent, response, expected


def ascii_strings(payload: bytes, limit: int = 24) -> list[str]:
    strings: list[str] = []
    for match in ASCII_STRING_RE.finditer(payload):
        value = match.group(0).decode("ascii", errors="replace")
        if value not in strings:
            strings.append(value)
        if len(strings) >= limit:
            break
    return strings


def allowed_utf16_char(char: str) -> bool:
    code = ord(char)
    if char in " \t\r\n.,:;_-\\/[](){}":
        return True
    if 0x30 <= code <= 0x39:
        return True
    if 0x41 <= code <= 0x5A or 0x61 <= code <= 0x7A:
        return True
    if 0x0400 <= code <= 0x052F:
        return True
    return False


def looks_meaningful_text(value: str) -> bool:
    stripped = value.strip()
    if len(stripped) < 4:
        return False
    letters = sum(1 for char in stripped if char.isalpha())
    return letters >= 3


def utf16le_strings(payload: bytes, limit: int = 24) -> list[dict[str, Any]]:
    body = strip_tail(payload)
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for offset in range(0, max(0, len(body) - 1)):
        if offset >= 2:
            previous = chr(int.from_bytes(body[offset - 2 : offset], byteorder="little"))
            if allowed_utf16_char(previous):
                continue
        chars: list[str] = []
        cursor = offset
        while cursor + 1 < len(body):
            char = chr(int.from_bytes(body[cursor : cursor + 2], byteorder="little"))
            if not allowed_utf16_char(char):
                break
            chars.append(char)
            cursor += 2
        if not chars:
            continue
        value = "".join(chars).strip()
        if not looks_meaningful_text(value) or value in seen:
            continue
        seen.add(value)
        found.append({"offset": offset, "text": value})
        if len(found) >= limit:
            break
    return found


def block_candidates(sent: bytes, send_index: int) -> dict[int, bytes]:
    body = strip_tail(sent)
    blocks: dict[int, bytes] = {}
    if send_index == 5:
        for offset in (67, 88):
            if len(body) >= offset + 16:
                blocks[offset] = body[offset : offset + 16]
    elif send_index >= 6:
        offset = 68
        if len(body) >= offset + 16:
            blocks[offset] = body[offset : offset + 16]
    return blocks


def find_positions(payload: bytes, needle: bytes) -> list[int]:
    positions: list[int] = []
    start = 0
    while needle:
        position = payload.find(needle, start)
        if position < 0:
            return positions
        positions.append(position)
        start = position + 1
    return positions


def ui_identifiers(ascii_values: list[str], utf16_values: list[dict[str, Any]]) -> list[str]:
    identifiers: list[str] = []
    for value in ascii_values:
        if any(marker in value for marker in UI_ASCII_MARKERS) and value not in identifiers:
            identifiers.append(value)
    for item in utf16_values:
        text = item["text"]
        if text not in identifiers:
            identifiers.append(text)
    return identifiers


def semantic_guess(identifiers: list[str]) -> str:
    joined = "\n".join(identifiers)
    has_main_frame = "MainFrame" in joined
    has_home_page = "HomePage" in joined
    has_startpage = "e1cib/navigationpoint/startpage" in joined
    has_managed_form = "ManagedForm" in joined
    has_form_name = "\u0424\u043e\u0440\u043c\u0430" in joined
    has_form_elements = ".ManagedForm[" in joined and "[" in joined and "]" in joined
    if "EditField[" in joined:
        return "form_element_summary"
    if has_managed_form and has_form_name:
        return "active_form_descriptor"
    if has_form_elements:
        return "managed_form_ref"
    if has_main_frame and has_home_page:
        return "main_frame_with_home_page"
    if has_home_page and has_startpage:
        return "home_page_navigation_point"
    if has_home_page:
        return "home_page"
    if identifiers:
        return "ui_payload"
    return ""


def analyze_pair(
    send_index: int,
    sent: bytes,
    response: bytes,
    expected: bytes | None,
    override_blocks: dict[int, bytes] | None = None,
) -> dict[str, Any]:
    response_body = strip_tail(response)
    blocks = override_blocks if override_blocks is not None and override_blocks else block_candidates(sent, send_index)
    nonce_echoes = [
        {
            "manager_offset": offset,
            "block_hex": block.hex(),
            "response_positions": find_positions(response_body, block),
        }
        for offset, block in sorted(blocks.items())
    ]
    ascii_values = ascii_strings(response_body)
    utf16_values = utf16le_strings(response_body)
    identifiers = ui_identifiers(ascii_values, utf16_values)
    expected_len = len(expected) if expected is not None else None
    return {
        "send_index": send_index,
        "sent_byte_count": len(sent),
        "response_byte_count": len(response),
        "expected_response_byte_count": expected_len,
        "same_response_size_as_expected": expected_len is not None and len(response) == expected_len,
        "response_sha256": sha256_hex(response),
        "response_head_hex": response[:64].hex(),
        "nonce_echoes": nonce_echoes,
        "ascii_strings": ascii_values,
        "utf16le_strings": utf16_values,
        "ui_identifiers": identifiers,
        "semantic_guess": semantic_guess(identifiers),
    }


def extract_replay(replay_dir: Path, frame_from: int, frame_to: int) -> dict[str, Any]:
    events = read_replay_events(replay_dir)
    replacement_blocks = replay_replacement_blocks(events)
    frames: list[dict[str, Any]] = []
    for send_index in range(frame_from, frame_to + 1):
        sent, response, expected = read_replay_pair(replay_dir, send_index)
        if sent is None or response is None:
            continue
        frames.append(analyze_pair(send_index, sent, response, expected, replacement_blocks.get(send_index)))
    return {
        "input_kind": "replay",
        "input_dir": str(replay_dir),
        "frames": frames,
    }


def extract_capture(capture_dir: Path, frame_from: int, frame_to: int) -> dict[str, Any]:
    manager, client = read_capture_payloads(capture_dir)
    frames: list[dict[str, Any]] = []
    for send_index in range(frame_from, frame_to + 1):
        manager_index = send_index - 1
        client_index = send_index
        if manager_index >= len(manager) or client_index >= len(client):
            continue
        frames.append(analyze_pair(send_index, manager[manager_index], client[client_index], None))
    return {
        "input_kind": "capture",
        "input_dir": str(capture_dir),
        "frames": frames,
    }


def markdown_table(rows: list[list[Any]], headers: list[str]) -> str:
    def cell(value: Any) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell(value) for value in row) + " |")
    return "\n".join(lines)


def write_report(result: dict[str, Any], output_dir: Path) -> Path:
    report_path = output_dir / "payload_extract.md"
    rows = []
    for frame in result["frames"]:
        echo_summary = [
            f"{item['manager_offset']}->{item['response_positions']}" for item in frame["nonce_echoes"]
        ]
        rows.append(
            [
                frame["send_index"],
                frame["sent_byte_count"],
                frame["response_byte_count"],
                frame["expected_response_byte_count"],
                frame["same_response_size_as_expected"],
                echo_summary,
                frame["semantic_guess"],
                frame["ui_identifiers"],
            ]
        )

    lines: list[str] = []
    lines.append("# Protocol Payload Extract")
    lines.append("")
    lines.append(f"- Generated at: `{result['generated_at']}`")
    lines.append(f"- Input kind: `{result['input_kind']}`")
    lines.append(f"- Input dir: `{result['input_dir']}`")
    lines.append("")
    lines.append("## Frame Summary")
    lines.append("")
    lines.append(
        markdown_table(
            rows,
            [
                "frame",
                "sent bytes",
                "response bytes",
                "expected bytes",
                "same size",
                "nonce echoes",
                "semantic guess",
                "UI identifiers",
            ],
        )
        if rows
        else "No frames extracted."
    )
    lines.append("")

    for frame in result["frames"]:
        lines.append(f"## Frame {frame['send_index']}")
        lines.append("")
        lines.append(f"- Response bytes: `{frame['response_byte_count']}`")
        lines.append(f"- Semantic guess: `{frame['semantic_guess']}`")
        lines.append(f"- Response head: `{frame['response_head_hex']}`")
        lines.append(f"- Nonce echoes: `{frame['nonce_echoes']}`")
        if frame["ascii_strings"]:
            lines.append("- ASCII strings:")
            for value in frame["ascii_strings"]:
                lines.append(f"  - `{value}`")
        if frame["utf16le_strings"]:
            lines.append("- UTF-16LE strings:")
            for item in frame["utf16le_strings"]:
                lines.append(f"  - `{item['offset']}`: `{item['text']}`")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", help="Capture/replay directory or capture name under runtime/protocol-research/captures.")
    parser.add_argument("--frame-from", type=int, default=8)
    parser.add_argument("--frame-to", type=int, default=10)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_script()
    input_dir = resolve_input_path(args.input_dir, repo_root)
    if (input_dir / "replay_events.jsonl").exists():
        result = extract_replay(input_dir, args.frame_from, args.frame_to)
    elif (input_dir / "traffic.jsonl").exists():
        result = extract_capture(input_dir, args.frame_from, args.frame_to)
    else:
        raise FileNotFoundError(f"Input is neither replay nor capture evidence: {input_dir}")

    result["schema"] = "protocol-payload-extract.v1"
    result["generated_at"] = utc_now()
    result["frame_from"] = args.frame_from
    result["frame_to"] = args.frame_to

    output_dir = args.output_dir.resolve() if args.output_dir else input_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "payload_extract.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path = write_report(result, output_dir)

    if args.json:
        print(json.dumps({"json_path": str(json_path), "report_path": str(report_path)}, ensure_ascii=False, indent=2))
    else:
        print(f"json={json_path}")
        print(f"report={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
