#!/usr/bin/env python3
"""Analyze repeated TestManager request frames in a capture or replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from extract_payloads import (
    ascii_strings,
    read_capture_payloads,
    read_replay_pair,
    repo_root_from_script,
    resolve_input_path,
    semantic_guess,
    strip_tail,
    ui_identifiers,
    utf16le_strings,
)


GUID_PATTERN = rb"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
MANAGED_FORM_REF_RE = re.compile(
    rb"(?P<ref>`?HomePage\[[^\]]+\]\.ManagedForm\[(?P<guid>" + GUID_PATTERN + rb")\])"
)
TEXT_GUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
TEXT_MANAGED_FORM_REF_RE = re.compile(
    r"(?P<ref>`?HomePage\[[^\]]+\]\.ManagedForm\[(?P<guid>"
    + TEXT_GUID_RE.pattern
    + r")\])"
)
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
TEXT_ELEMENT_REF_RE = re.compile(
    r"(?P<path>.*?\.ManagedForm\[" + TEXT_GUID_RE.pattern + r"\]\.(?P<type>[A-Za-z]+)\[(?P<name>[^\]]+)\])"
)
OPERATION_TOKEN_OFFSET = 51
OPERATION_TOKEN_LENGTH = 16


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def uuid_le_at(payload: bytes, offset: int) -> str:
    body = strip_tail(payload)
    if len(body) < offset + 16:
        return ""
    return str(uuid.UUID(bytes_le=body[offset : offset + 16]))


def uint16_le_at(payload: bytes, offset: int) -> int | None:
    body = strip_tail(payload)
    if len(body) < offset + 2:
        return None
    return int.from_bytes(body[offset : offset + 2], byteorder="little")


def hex_slice(payload: bytes, offset: int, length: int) -> str:
    body = strip_tail(payload)
    if len(body) < offset + length:
        return ""
    return body[offset : offset + length].hex()


def find_positions(payload: bytes, needle: bytes) -> list[int]:
    if not needle:
        return []
    positions: list[int] = []
    start = 0
    while True:
        position = payload.find(needle, start)
        if position < 0:
            return positions
        positions.append(position)
        start = position + 1


def managed_form_refs(payload: bytes) -> list[dict[str, str]]:
    body = strip_tail(payload)
    refs: list[dict[str, str]] = []
    seen: set[str] = set()
    for match in MANAGED_FORM_REF_RE.finditer(body):
        value = match.group("ref").decode("ascii", errors="replace")
        if value in seen:
            continue
        seen.add(value)
        refs.append(
            {
                "ref": value,
                "guid": match.group("guid").decode("ascii", errors="replace").lower(),
                "encoding": "ascii",
            }
        )
    for item in utf16le_strings(body, limit=64):
        text = item["text"]
        for match in TEXT_MANAGED_FORM_REF_RE.finditer(text):
            value = match.group("ref")
            if value in seen:
                continue
            seen.add(value)
            refs.append(
                {
                    "ref": value,
                    "guid": match.group("guid").lower(),
                    "encoding": "utf16le",
                }
            )
    return refs


def element_refs(identifiers: list[str]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    seen: set[str] = set()
    for identifier in identifiers:
        match = TEXT_ELEMENT_REF_RE.search(identifier)
        if not match:
            continue
        path = match.group("path")
        if path in seen:
            continue
        seen.add(path)
        refs.append(
            {
                "path": path,
                "type": match.group("type"),
                "name": match.group("name"),
            }
        )
    return refs


def request_semantic(identifiers: list[str]) -> str:
    response_like = semantic_guess(identifiers)
    if response_like == "managed_form_ref":
        return "managed_form_ref_request"
    if response_like:
        return f"{response_like}_request"
    return ""


def analyze_text_payload(payload: bytes) -> dict[str, Any]:
    body = strip_tail(payload)
    ascii_values = ascii_strings(body)
    utf16_values = utf16le_strings(body)
    identifiers = ui_identifiers(ascii_values, utf16_values)
    return {
        "ascii_strings": ascii_values,
        "utf16le_strings": utf16_values,
        "ui_identifiers": identifiers,
        "semantic_guess": semantic_guess(identifiers),
    }


def analyze_request_payload(payload: bytes) -> dict[str, Any]:
    text = analyze_text_payload(payload)
    identifiers = text["ui_identifiers"]
    return {
        "byte_count": len(payload),
        "body_byte_count": len(strip_tail(payload)),
        "sha256": sha256_hex(payload),
        "head_hex": payload[:64].hex(),
        "uuid_le_at_2": uuid_le_at(payload, 2),
        "sequence_le_at_19": uint16_le_at(payload, 19),
        "operation_token_51_hex": hex_slice(payload, OPERATION_TOKEN_OFFSET, OPERATION_TOKEN_LENGTH),
        "nonce_68_hex": hex_slice(payload, 68, 16),
        "managed_form_refs": managed_form_refs(payload),
        "element_refs": element_refs(identifiers),
        "ascii_strings": text["ascii_strings"],
        "utf16le_strings": text["utf16le_strings"],
        "ui_identifiers": identifiers,
        "semantic_guess": request_semantic(identifiers),
    }


def analyze_response_payload(
    payload: bytes | None,
    expected: bytes | None,
    operation_token: bytes | None = None,
) -> dict[str, Any]:
    if payload is None:
        return {
            "byte_count": None,
            "expected_byte_count": len(expected) if expected is not None else None,
            "same_size_as_expected": False,
            "semantic_guess": "",
            "ui_identifiers": [],
            "operation_token_echo_positions": [],
        }
    text = analyze_text_payload(payload)
    expected_len = len(expected) if expected is not None else None
    body = strip_tail(payload)
    return {
        "byte_count": len(payload),
        "expected_byte_count": expected_len,
        "same_size_as_expected": expected_len is not None and len(payload) == expected_len,
        "sha256": sha256_hex(payload),
        "head_hex": payload[:64].hex(),
        "ui_identifiers": text["ui_identifiers"],
        "extra_ui_identifiers": [
            identifier
            for identifier in text["ui_identifiers"]
            if ".EditField[" not in identifier and ".ManagedForm[" not in identifier
        ],
        "semantic_guess": text["semantic_guess"],
        "operation_token_echo_positions": find_positions(body, operation_token or b""),
    }


def read_capture_pairs(capture_dir: Path, frame_from: int, frame_to: int) -> list[dict[str, Any]]:
    manager, client = read_capture_payloads(capture_dir)
    pairs: list[dict[str, Any]] = []
    for frame_index in range(frame_from, frame_to + 1):
        manager_index = frame_index - 1
        client_index = frame_index
        if manager_index >= len(manager):
            continue
        pairs.append(
            {
                "frame_index": frame_index,
                "request": manager[manager_index],
                "response": client[client_index] if client_index < len(client) else None,
                "expected": None,
            }
        )
    return pairs


def read_replay_pairs(replay_dir: Path, frame_from: int, frame_to: int) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for frame_index in range(frame_from, frame_to + 1):
        sent, response, expected = read_replay_pair(replay_dir, frame_index)
        if sent is None:
            continue
        pairs.append(
            {
                "frame_index": frame_index,
                "request": sent,
                "response": response,
                "expected": expected,
            }
        )
    return pairs


def variable_ranges(requests: list[tuple[int, bytes]]) -> list[dict[str, Any]]:
    bodies = [(frame, strip_tail(payload)) for frame, payload in requests]
    if len(bodies) < 2:
        return []
    lengths = {len(body) for _frame, body in bodies}
    if len(lengths) != 1:
        return [
            {
                "start": 0,
                "end": max(lengths),
                "length": max(lengths),
                "reason": "request_body_lengths_differ",
            }
        ]

    body_length = lengths.pop()
    variable_positions = [
        index
        for index in range(body_length)
        if len({body[index] for _frame, body in bodies}) > 1
    ]
    ranges: list[dict[str, Any]] = []
    if not variable_positions:
        return ranges

    start = variable_positions[0]
    previous = variable_positions[0]
    for position in variable_positions[1:] + [-1]:
        if position == previous + 1:
            previous = position
            continue
        end = previous + 1
        ranges.append(
            {
                "start": start,
                "end": end,
                "length": end - start,
                "values_by_frame": [
                    {"frame_index": frame, "hex": body[start:end].hex()} for frame, body in bodies
                ],
            }
        )
        start = position
        previous = position
    return ranges


def known_dynamic_ranges(requests: list[tuple[int, bytes]]) -> list[dict[str, Any]]:
    if not requests:
        return []
    bodies = [(frame, strip_tail(payload)) for frame, payload in requests]
    first_body = bodies[0][1]
    ranges: list[dict[str, Any]] = []

    def append_range(name: str, start: int, end: int) -> None:
        if len(first_body) < end:
            return
        ranges.append(
            {
                "name": name,
                "start": start,
                "end": end,
                "length": end - start,
                "values_by_frame": [
                    {"frame_index": frame, "hex": body[start:end].hex()}
                    for frame, body in bodies
                    if len(body) >= end
                ],
            }
        )

    append_range("ack_guid_uuid_le", 2, 18)
    append_range("sequence_uint16_le", 19, 21)
    append_range("nonce", 68, 84)
    for index, match in enumerate(MANAGED_FORM_REF_RE.finditer(first_body), start=1):
        start = match.start("guid")
        append_range("managed_form_guid_ascii" if index == 1 else f"managed_form_guid_ascii_{index}", start, start + 36)
    for index, match in enumerate(MANAGED_FORM_GUID_UTF16LE_RE.finditer(first_body), start=1):
        start = match.start("guid")
        append_range(
            "managed_form_guid_utf16le" if index == 1 else f"managed_form_guid_utf16le_{index}",
            start,
            start + len(match.group("guid")),
        )
    return ranges


def normalized_shape_sha256(requests: list[tuple[int, bytes]], ranges: list[dict[str, Any]]) -> str:
    if not requests:
        return ""
    bodies = [strip_tail(payload) for _frame, payload in requests]
    if len({len(body) for body in bodies}) != 1:
        return ""
    body = bytearray(bodies[0])
    for item in ranges:
        if item.get("reason"):
            continue
        start = int(item["start"])
        end = int(item["end"])
        body[start:end] = b"\x00" * (end - start)
    return sha256_hex(bytes(body))


def summarize(frames: list[dict[str, Any]], variable: list[dict[str, Any]]) -> dict[str, Any]:
    body_lengths = Counter(frame["request"]["body_byte_count"] for frame in frames)
    response_sizes = Counter(str(frame["response"]["byte_count"]) for frame in frames)
    request_semantics = Counter(frame["request"]["semantic_guess"] for frame in frames)
    response_semantics = Counter(frame["response"]["semantic_guess"] for frame in frames)
    sequences = [frame["request"]["sequence_le_at_19"] for frame in frames]
    ack_guids = sorted({frame["request"]["uuid_le_at_2"] for frame in frames if frame["request"]["uuid_le_at_2"]})
    managed_form_guids = sorted(
        {
            ref["guid"]
            for frame in frames
            for ref in frame["request"]["managed_form_refs"]
            if ref.get("guid")
        }
    )
    return {
        "frame_count": len(frames),
        "request_body_lengths": dict(body_lengths),
        "response_byte_counts": dict(response_sizes),
        "request_semantic_counts": dict(request_semantics),
        "response_semantic_counts": dict(response_semantics),
        "sequence_le_at_19_values": sequences,
        "unique_ack_guids_at_2": ack_guids,
        "unique_managed_form_guids": managed_form_guids,
        "variable_range_count": len(variable),
    }


def build_shape_groups(requests: list[tuple[int, bytes]]) -> list[dict[str, Any]]:
    grouped: dict[int, list[tuple[int, bytes]]] = {}
    for frame_index, payload in requests:
        grouped.setdefault(len(strip_tail(payload)), []).append((frame_index, payload))

    groups: list[dict[str, Any]] = []
    for body_length, items in sorted(grouped.items()):
        variable = variable_ranges(items)
        known_dynamic = known_dynamic_ranges(items)
        groups.append(
            {
                "body_byte_count": body_length,
                "frame_indices": [frame_index for frame_index, _payload in items],
                "frame_count": len(items),
                "variable_ranges": variable,
                "known_dynamic_ranges": known_dynamic,
                "normalized_request_shape_sha256": normalized_shape_sha256(items, variable),
                "canonical_request_shape_sha256": normalized_shape_sha256(items, known_dynamic),
            }
        )
    return groups


def build_operation_groups(frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for frame in frames:
        token = frame["request"].get("operation_token_51_hex", "")
        if not token:
            continue
        grouped.setdefault(token, []).append(frame)

    groups: list[dict[str, Any]] = []
    for token, items in grouped.items():
        items.sort(key=lambda frame: int(frame["frame_index"]))
        extra_identifiers = sorted(
            {
                identifier
                for frame in items
                for identifier in frame["response"].get("extra_ui_identifiers", [])
                if identifier
            }
        )
        element_names = [
            ref["name"]
            for frame in items
            for ref in frame["request"].get("element_refs", [])
            if ref.get("name")
        ]
        unique_element_names = list(dict.fromkeys(element_names))
        groups.append(
            {
                "operation_token_hex": token,
                "frame_indices": [int(frame["frame_index"]) for frame in items],
                "request_body_lengths": [frame["request"]["body_byte_count"] for frame in items],
                "response_byte_counts": [frame["response"]["byte_count"] for frame in items],
                "element_names": unique_element_names,
                "response_extra_identifiers": extra_identifiers,
                "operation_token_echo_positions": [
                    {
                        "frame_index": int(frame["frame_index"]),
                        "positions": frame["response"].get("operation_token_echo_positions", []),
                    }
                    for frame in items
                ],
                "observed_response_class": "caption_or_value" if extra_identifiers else "reference_only",
            }
        )
    groups.sort(key=lambda group: min(group["frame_indices"]))
    for index, group in enumerate(groups, start=1):
        group["operation_ordinal"] = index
        group["label"] = f"editfield_detail_op_{index}_{group['observed_response_class']}"
    return groups


def build_result(input_dir: Path, frame_from: int, frame_to: int) -> dict[str, Any]:
    if (input_dir / "replay_events.jsonl").exists():
        input_kind = "replay"
        pairs = read_replay_pairs(input_dir, frame_from, frame_to)
    elif (input_dir / "traffic.jsonl").exists():
        input_kind = "capture"
        pairs = read_capture_pairs(input_dir, frame_from, frame_to)
    else:
        raise FileNotFoundError(f"Input is neither replay nor capture evidence: {input_dir}")

    frames: list[dict[str, Any]] = []
    requests: list[tuple[int, bytes]] = []
    for pair in pairs:
        frame_index = int(pair["frame_index"])
        request = pair["request"]
        request_analysis = analyze_request_payload(request)
        operation_token_hex = request_analysis.get("operation_token_51_hex", "")
        operation_token = bytes.fromhex(operation_token_hex) if operation_token_hex else None
        requests.append((frame_index, request))
        frames.append(
            {
                "frame_index": frame_index,
                "request": request_analysis,
                "response": analyze_response_payload(pair.get("response"), pair.get("expected"), operation_token),
            }
        )

    variable = variable_ranges(requests)
    known_dynamic = known_dynamic_ranges(requests)
    return {
        "schema": "protocol-request-series.v1",
        "generated_at": utc_now(),
        "input_kind": input_kind,
        "input_dir": str(input_dir),
        "frame_from": frame_from,
        "frame_to": frame_to,
        "frames": frames,
        "summary": summarize(frames, variable),
        "variable_ranges": variable,
        "known_dynamic_ranges": known_dynamic,
        "shape_groups": build_shape_groups(requests),
        "operation_groups": build_operation_groups(frames),
        "normalized_request_shape_sha256": normalized_shape_sha256(requests, variable),
        "canonical_request_shape_sha256": normalized_shape_sha256(requests, known_dynamic),
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
    report_path = output_dir / "request_series.md"
    rows: list[list[Any]] = []
    for frame in result["frames"]:
        request = frame["request"]
        response = frame["response"]
        rows.append(
            [
                frame["frame_index"],
                request["body_byte_count"],
                request["sequence_le_at_19"],
                request["operation_token_51_hex"],
                request["semantic_guess"],
                [ref["name"] for ref in request["element_refs"]],
                response["byte_count"],
                response["expected_byte_count"],
                response["same_size_as_expected"],
                response["semantic_guess"],
            ]
        )

    lines: list[str] = []
    lines.append("# Protocol Request Series")
    lines.append("")
    lines.append(f"- Generated at: `{result['generated_at']}`")
    lines.append(f"- Input kind: `{result['input_kind']}`")
    lines.append(f"- Input dir: `{result['input_dir']}`")
    lines.append(f"- Frames: `{result['frame_from']}..{result['frame_to']}`")
    lines.append(f"- Normalized request shape SHA-256: `{result['normalized_request_shape_sha256']}`")
    lines.append(f"- Canonical request shape SHA-256: `{result['canonical_request_shape_sha256']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for key, value in result["summary"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Frames")
    lines.append("")
    lines.append(
        markdown_table(
            rows,
            [
                "frame",
                "request body",
                "seq@19",
                "op token@51",
                "request semantic",
                "element names",
                "response bytes",
                "expected bytes",
                "same size",
                "response semantic",
            ],
        )
        if rows
        else "No frames analyzed."
    )
    lines.append("")
    lines.append("## Variable Request Ranges")
    lines.append("")
    if result["variable_ranges"]:
        range_rows = [
            [
                item["start"],
                item["end"],
                item["length"],
                item.get("reason", ""),
                item.get("values_by_frame", []),
            ]
            for item in result["variable_ranges"]
        ]
        lines.append(markdown_table(range_rows, ["start", "end", "length", "reason", "values by frame"]))
    else:
        lines.append("No byte differences across request bodies.")
    lines.append("")
    lines.append("## Known Dynamic Request Ranges")
    lines.append("")
    if result["known_dynamic_ranges"]:
        known_rows = [
            [
                item["name"],
                item["start"],
                item["end"],
                item["length"],
                item.get("values_by_frame", []),
            ]
            for item in result["known_dynamic_ranges"]
        ]
        lines.append(markdown_table(known_rows, ["name", "start", "end", "length", "values by frame"]))
    else:
        lines.append("No known dynamic request ranges detected.")
    lines.append("")
    lines.append("## Shape Groups")
    lines.append("")
    if result["shape_groups"]:
        group_rows = [
            [
                group["body_byte_count"],
                group["frame_indices"],
                group["normalized_request_shape_sha256"],
                group["canonical_request_shape_sha256"],
                [
                    f"{item['name']}@{item['start']}:{item['length']}"
                    for item in group["known_dynamic_ranges"]
                    if item.get("name")
                ],
            ]
            for group in result["shape_groups"]
        ]
        lines.append(
            markdown_table(
                group_rows,
                ["request body", "frames", "normalized shape SHA-256", "canonical shape SHA-256", "known dynamics"],
            )
        )
    else:
        lines.append("No shape groups detected.")
    lines.append("")
    lines.append("## Operation Token Groups")
    lines.append("")
    if result["operation_groups"]:
        operation_rows = [
            [
                group["operation_ordinal"],
                group["label"],
                group["operation_token_hex"],
                group["frame_indices"],
                group["element_names"],
                group["response_byte_counts"],
                group["response_extra_identifiers"],
                group["operation_token_echo_positions"],
            ]
            for group in result["operation_groups"]
        ]
        lines.append(
            markdown_table(
                operation_rows,
                [
                    "op",
                    "label",
                    "token@51",
                    "frames",
                    "elements",
                    "response bytes",
                    "extra response identifiers",
                    "token echo positions",
                ],
            )
        )
    else:
        lines.append("No operation token groups detected.")
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", help="Capture/replay directory or capture name under runtime/protocol-research/captures.")
    parser.add_argument("--frame-from", type=int, default=18)
    parser.add_argument("--frame-to", type=int, default=30)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_script()
    input_dir = resolve_input_path(args.input_dir, repo_root)
    result = build_result(input_dir, args.frame_from, args.frame_to)

    output_dir = args.output_dir
    if output_dir is None:
        output_dir = input_dir / f"request-series-{args.frame_from:03d}-{args.frame_to:03d}"
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "request_series.json"
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
