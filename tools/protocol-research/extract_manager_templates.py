#!/usr/bin/env python3
"""Build manager frame templates from captured 1C TestManager protocol frames."""

from __future__ import annotations

import argparse
import base64
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from extract_payloads import (
    CLIENT_TO_MANAGER,
    MANAGER_TO_CLIENT,
    TAIL_MARKER,
    ascii_strings,
    semantic_guess,
    strip_tail,
    ui_identifiers,
    utf16le_strings,
)


GUID_PATTERN = rb"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
MANAGED_FORM_GUID_RE = re.compile(rb"ManagedForm\[(" + GUID_PATTERN + rb")\]")
UTF16LE_GUID_CHAR_PATTERN = b"[0-9a-fA-F]\x00"
UTF16LE_GUID_PATTERN = (
    UTF16LE_GUID_CHAR_PATTERN * 8
    + b"-\x00"
    + UTF16LE_GUID_CHAR_PATTERN * 4
    + b"-\x00"
    + UTF16LE_GUID_CHAR_PATTERN * 4
    + b"-\x00"
    + UTF16LE_GUID_CHAR_PATTERN * 4
    + b"-\x00"
    + UTF16LE_GUID_CHAR_PATTERN * 12
)
MANAGED_FORM_GUID_UTF16LE_RE = re.compile(
    re.escape("ManagedForm[".encode("utf-16le"))
    + rb"(?P<guid>"
    + UTF16LE_GUID_PATTERN
    + rb")"
    + re.escape("]".encode("utf-16le"))
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def timestamp_name() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def captures_root(repo_root: Path) -> Path:
    return repo_root / "runtime" / "protocol-research" / "captures"


def resolve_capture_dir(value: str, repo_root: Path) -> Path:
    path = Path(value)
    if path.exists():
        return path.resolve()
    candidate = captures_root(repo_root) / value
    if candidate.exists():
        return candidate.resolve()
    raise FileNotFoundError(f"Capture directory not found: {value}")


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


def read_capture_payloads(capture_dir: Path) -> dict[str, list[bytes]]:
    traffic_path = capture_dir / "traffic.jsonl"
    if not traffic_path.exists():
        raise FileNotFoundError(f"traffic.jsonl not found: {traffic_path}")

    result = {
        MANAGER_TO_CLIENT: [],
        CLIENT_TO_MANAGER: [],
    }
    with traffic_path.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("event") != "chunk":
                continue
            direction = record.get("direction")
            if direction in result:
                result[direction].append(payload_from_record(record))
    return result


def parse_frame_list(value: str) -> list[int]:
    frames: list[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            frames.extend(range(start, end + 1))
        else:
            frames.append(int(part))
    return sorted(dict.fromkeys(frames))


def split_tail(payload: bytes) -> tuple[bytes, bytes]:
    if payload.endswith(TAIL_MARKER):
        return payload[: -len(TAIL_MARKER)], TAIL_MARKER
    return payload, b""


def hex_slice(payload: bytes, start: int, length: int) -> str:
    return payload[start : start + length].hex()


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


def decode_utf16le_ascii(value: bytes) -> str:
    return value.decode("utf-16le", errors="replace").lower()


def dynamic_fields_for_frame(frame_index: int, body: bytes) -> list[dict[str, Any]]:
    fields = [
        {
            "name": "ack_guid",
            "kind": "uuid_le",
            "offset": 2,
            "length": 16,
            "source": "client_response_after_manager_frame_3",
            "template_hex": hex_slice(body, 2, 16),
        },
        {
            "name": "sequence",
            "kind": "uint16_le",
            "offset": 19,
            "length": 2,
            "source": "template_frame4_sequence_plus_delta",
            "delta_from_frame4_sequence": frame_index - 4,
            "template_value": int.from_bytes(body[19:21], byteorder="little"),
            "template_hex": hex_slice(body, 19, 2),
        },
    ]
    if frame_index == 5:
        fields.extend(
            [
                {
                    "name": "nonce_a",
                    "kind": "random_bytes",
                    "offset": 67,
                    "length": 16,
                    "source": "manager_generated",
                    "template_hex": hex_slice(body, 67, 16),
                    "expected_response_offsets": [30],
                },
                {
                    "name": "nonce_b",
                    "kind": "random_bytes",
                    "offset": 88,
                    "length": 16,
                    "source": "manager_generated",
                    "template_hex": hex_slice(body, 88, 16),
                    "expected_response_offsets": [51],
                },
            ]
        )
    elif frame_index >= 6:
        fields.append(
            {
                "name": "nonce",
                "kind": "random_bytes",
                "offset": 68,
                "length": 16,
                "source": "manager_generated",
                "template_hex": hex_slice(body, 68, 16),
                "expected_response_offsets": [30],
            }
        )
    managed_form_matches = list(MANAGED_FORM_GUID_RE.finditer(body))
    for index, match in enumerate(managed_form_matches, start=1):
        guid_offset = match.start(1)
        fields.append(
            {
                "name": "managed_form_guid" if len(managed_form_matches) == 1 else f"managed_form_guid_{index}",
                "kind": "managed_form_guid_ascii",
                "offset": guid_offset,
                "length": 36,
                "source": "latest_client_response_managed_form_ref",
                "template_value": match.group(1).decode("ascii"),
                "template_hex": hex_slice(body, guid_offset, 36),
            }
        )
    managed_form_utf16le_matches = list(MANAGED_FORM_GUID_UTF16LE_RE.finditer(body))
    for index, match in enumerate(managed_form_utf16le_matches, start=1):
        guid_bytes = match.group("guid")
        guid_offset = match.start("guid")
        fields.append(
            {
                "name": (
                    "managed_form_guid_utf16le"
                    if len(managed_form_utf16le_matches) == 1
                    else f"managed_form_guid_utf16le_{index}"
                ),
                "kind": "managed_form_guid_utf16le",
                "offset": guid_offset,
                "length": len(guid_bytes),
                "source": "latest_client_response_managed_form_ref",
                "template_value": decode_utf16le_ascii(guid_bytes),
                "template_hex": hex_slice(body, guid_offset, len(guid_bytes)),
            }
        )
    return fields


def stable_ranges(body_length: int, dynamic_fields: list[dict[str, Any]]) -> list[dict[str, int]]:
    ranges: list[dict[str, int]] = []
    cursor = 0
    for field in sorted(dynamic_fields, key=lambda item: int(item["offset"])):
        start = int(field["offset"])
        if cursor < start:
            ranges.append({"start": cursor, "end": start, "length": start - cursor})
        cursor = max(cursor, start + int(field["length"]))
    if cursor < body_length:
        ranges.append({"start": cursor, "end": body_length, "length": body_length - cursor})
    return ranges


def response_summary(response: bytes, dynamic_fields: list[dict[str, Any]]) -> dict[str, Any]:
    response_body = strip_tail(response)
    ascii_values = ascii_strings(response_body)
    utf16_values = utf16le_strings(response_body)
    identifiers = ui_identifiers(ascii_values, utf16_values)
    nonce_echoes: list[dict[str, Any]] = []
    for field in dynamic_fields:
        if field.get("kind") != "random_bytes":
            continue
        template_value = bytes.fromhex(field["template_hex"])
        nonce_echoes.append(
            {
                "field": field["name"],
                "manager_offset": field["offset"],
                "template_hex": field["template_hex"],
                "response_positions": find_positions(response_body, template_value),
                "expected_response_offsets": field.get("expected_response_offsets", []),
            }
        )
    return {
        "byte_count": len(response),
        "head_hex": response[:64].hex(),
        "ascii_strings": ascii_values,
        "utf16le_strings": utf16_values,
        "ui_identifiers": identifiers,
        "semantic_guess": semantic_guess(identifiers),
        "nonce_echoes": nonce_echoes,
    }


def build_template(capture_dir: Path, frame_index: int, manager: list[bytes], client: list[bytes]) -> dict[str, Any]:
    manager_index = frame_index - 1
    client_index = frame_index
    if manager_index >= len(manager):
        raise IndexError(f"Manager frame {frame_index} is missing in {capture_dir.name}")
    payload = manager[manager_index]
    body, tail = split_tail(payload)
    dynamic_fields = dynamic_fields_for_frame(frame_index, body)
    response = client[client_index] if client_index < len(client) else b""
    return {
        "frame_index": frame_index,
        "direction": MANAGER_TO_CLIENT,
        "body_length": len(body),
        "payload_length": len(payload),
        "body_hex": body.hex(),
        "tail_hex": tail.hex(),
        "dynamic_fields": dynamic_fields,
        "stable_ranges": stable_ranges(len(body), dynamic_fields),
        "response": response_summary(response, dynamic_fields) if response else None,
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
    report_path = output_dir / "manager_frame_templates.md"
    rows = []
    for template in result["templates"]:
        response = template.get("response") or {}
        rows.append(
            [
                template["frame_index"],
                template["body_length"],
                [
                    f"{field['name']}@{field['offset']}:{field['length']}:{field['kind']}"
                    for field in template["dynamic_fields"]
                ],
                response.get("byte_count", ""),
                response.get("semantic_guess", ""),
                response.get("ui_identifiers", []),
            ]
        )

    lines: list[str] = []
    lines.append("# Manager Frame Templates")
    lines.append("")
    lines.append(f"- Generated at: `{result['generated_at']}`")
    lines.append(f"- Capture dir: `{result['capture_dir']}`")
    lines.append("")
    lines.append(
        markdown_table(
            rows,
            ["frame", "body bytes", "dynamic fields", "response bytes", "semantic guess", "UI identifiers"],
        )
    )
    lines.append("")
    for template in result["templates"]:
        lines.append(f"## Frame {template['frame_index']}")
        lines.append("")
        lines.append(f"- Stable ranges: `{template['stable_ranges']}`")
        lines.append(f"- Dynamic fields: `{template['dynamic_fields']}`")
        if template.get("response"):
            lines.append(f"- Response nonce echoes: `{template['response']['nonce_echoes']}`")
        lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture_dir", help="Capture directory or name under runtime/protocol-research/captures.")
    parser.add_argument("--frames", default="8-10", help="Frame indexes, for example 8-10 or 8,9,10.")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_script()
    capture_dir = resolve_capture_dir(args.capture_dir, repo_root)
    payloads = read_capture_payloads(capture_dir)
    frames = parse_frame_list(args.frames)
    output_dir = args.output_dir
    if output_dir is None:
        output_dir = repo_root / "runtime" / "protocol-research" / "templates" / timestamp_name()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "schema": "protocol-manager-frame-templates.v1",
        "generated_at": utc_now(),
        "capture_dir": str(capture_dir),
        "frames": frames,
        "templates": [
            build_template(capture_dir, frame, payloads[MANAGER_TO_CLIENT], payloads[CLIENT_TO_MANAGER])
            for frame in frames
        ],
    }
    json_path = output_dir / "manager_frame_templates.json"
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
