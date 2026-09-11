#!/usr/bin/env python3
"""Replay captured TestManager chunks directly to a running 1C TestClient."""

from __future__ import annotations

import argparse
import base64
import codecs
import hashlib
import json
import re
import secrets
import socket
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MANAGER_TO_CLIENT = "manager_to_client"
CLIENT_TO_MANAGER = "client_to_manager"
TAIL_MARKER = bytes.fromhex("6653b2a6")
GUID_PATTERN = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
CLIENT_ACK_GUID_RE = re.compile(
    r'\{"#",' + GUID_PATTERN + r",\s*\r?\n\{(" + GUID_PATTERN + r")\}",
    re.IGNORECASE,
)
MANAGER_HEADER_GUID_RE = re.compile(r"^\{0,(" + GUID_PATTERN + r"),", re.IGNORECASE)
MANAGED_FORM_GUID_RE = re.compile(rb"ManagedForm\[(?P<guid>" + GUID_PATTERN.encode("ascii") + rb")\]")
UI_PATH_KINDS = ("MainFrame", "SecondaryFrame", "ManagedForm")
UI_PATH_GUID_RE = re.compile(
    rb"(?P<kind>MainFrame|SecondaryFrame|ManagedForm)\[(?P<guid>"
    + GUID_PATTERN.encode("ascii")
    + rb")\]"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def timestamp_name() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def latest_capture_dir(repo_root: Path) -> Path:
    captures_dir = repo_root / "runtime" / "protocol-research" / "captures"
    candidates = [path for path in captures_dir.iterdir() if path.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"No capture directories found under {captures_dir}")
    return max(candidates, key=lambda path: path.name)


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def preview_hex(payload: bytes, limit: int = 48) -> str:
    return payload[:limit].hex()


def split_tail_marker(payload: bytes) -> tuple[bytes, bytes]:
    if payload.endswith(TAIL_MARKER):
        return payload[: -len(TAIL_MARKER)], TAIL_MARKER
    return payload, b""


def decode_utf8_frame_text(payload: bytes) -> str | None:
    body, _tail = split_tail_marker(payload)
    if body.startswith(codecs.BOM_UTF8):
        body = body[len(codecs.BOM_UTF8) :]
    try:
        return body.decode("utf-8")
    except UnicodeDecodeError:
        return None


def extract_client_ack_guid(payload: bytes) -> str | None:
    text = decode_utf8_frame_text(payload)
    if text is None:
        return None
    match = CLIENT_ACK_GUID_RE.search(text)
    if not match:
        return None
    return match.group(1).lower()


def extract_managed_form_guid(payload: bytes) -> str | None:
    body, _tail = split_tail_marker(payload)
    match = MANAGED_FORM_GUID_RE.search(body)
    if not match:
        return None
    return match.group("guid").decode("ascii").lower()


def find_ui_path_guid_references(payload: bytes) -> list[dict[str, Any]]:
    body, _tail = split_tail_marker(payload)
    references: list[dict[str, Any]] = []
    for match in UI_PATH_GUID_RE.finditer(body):
        references.append(
            {
                "kind": match.group("kind").decode("ascii"),
                "encoding": "ascii",
                "offset": match.start("guid"),
                "guid": match.group("guid").decode("ascii").lower(),
            }
        )

    suffix = "]".encode("utf-16le")
    for kind in UI_PATH_KINDS:
        prefix = f"{kind}[".encode("utf-16le")
        search_from = 0
        while True:
            prefix_offset = body.find(prefix, search_from)
            if prefix_offset < 0:
                break
            guid_start = prefix_offset + len(prefix)
            guid_end = guid_start + 36 * 2
            suffix_end = guid_end + len(suffix)
            if len(body) >= suffix_end and body[guid_end:suffix_end] == suffix:
                try:
                    guid_text = body[guid_start:guid_end].decode("utf-16le").lower()
                except UnicodeDecodeError:
                    guid_text = ""
                if re.fullmatch(GUID_PATTERN, guid_text, re.IGNORECASE):
                    references.append(
                        {
                            "kind": kind,
                            "encoding": "utf-16le",
                            "offset": guid_start,
                            "guid": guid_text,
                        }
                    )
            search_from = prefix_offset + len(prefix)

    return references


def find_managed_form_guid_references(payload: bytes) -> list[dict[str, Any]]:
    return [reference for reference in find_ui_path_guid_references(payload) if reference["kind"] == "ManagedForm"]


def adapt_ui_path_guids(payload: bytes, replacements_by_kind: dict[str, str]) -> tuple[bytes, list[dict[str, Any]]]:
    body, tail = split_tail_marker(payload)
    mutable = bytearray(body)
    replacements: list[dict[str, Any]] = []
    for reference in find_ui_path_guid_references(payload):
        kind = str(reference["kind"])
        replacement_guid = replacements_by_kind.get(kind)
        if replacement_guid is None:
            continue
        original_guid = str(reference["guid"]).lower()
        if original_guid == replacement_guid:
            continue
        encoding = str(reference["encoding"])
        offset = int(reference["offset"])
        replacement = replacement_guid.encode(encoding)
        end = offset + len(replacement)
        original = bytes(mutable[offset:end])
        mutable[offset:end] = replacement
        replacements.append(
            {
                **reference,
                "original_hex": original.hex(),
                "replacement_guid": replacement_guid,
                "replacement_hex": replacement.hex(),
            }
        )
    return bytes(mutable) + tail, replacements


def adapt_managed_form_guid(payload: bytes, replacement_guid: str) -> tuple[bytes, list[dict[str, Any]]]:
    return adapt_ui_path_guids(payload, {"ManagedForm": replacement_guid})


def adapt_manager_header_guid(payload: bytes, replacement_guid: str) -> tuple[bytes, str]:
    body, tail = split_tail_marker(payload)
    has_bom = body.startswith(codecs.BOM_UTF8)
    if has_bom:
        body = body[len(codecs.BOM_UTF8) :]

    text = body.decode("utf-8")
    match = MANAGER_HEADER_GUID_RE.search(text)
    if not match:
        raise ValueError("manager frame does not start with a TestManager text header")

    original_guid = match.group(1).lower()
    adapted_text = MANAGER_HEADER_GUID_RE.sub(f"{{0,{replacement_guid},", text, count=1)
    adapted_body = adapted_text.encode("utf-8")
    if has_bom:
        adapted_body = codecs.BOM_UTF8 + adapted_body
    return adapted_body + tail, original_guid


def adapt_binary_uuid_le(payload: bytes, original_guid: str, replacement_guid: str) -> tuple[bytes, list[int]]:
    original_bytes = uuid.UUID(original_guid).bytes_le
    replacement_bytes = uuid.UUID(replacement_guid).bytes_le
    offsets: list[int] = []
    search_from = 0
    while True:
        offset = payload.find(original_bytes, search_from)
        if offset < 0:
            break
        offsets.append(offset)
        search_from = offset + len(original_bytes)
    if not offsets:
        return payload, offsets
    return payload.replace(original_bytes, replacement_bytes), offsets


def replace_body_ranges(payload: bytes, replacements: dict[int, bytes]) -> tuple[bytes, dict[int, str]]:
    body, tail = split_tail_marker(payload)
    mutable = bytearray(body)
    originals: dict[int, str] = {}
    for offset, replacement in replacements.items():
        end = offset + len(replacement)
        if len(mutable) < end:
            raise ValueError(f"payload is too short for replacement at offset {offset}")
        originals[offset] = bytes(mutable[offset:end]).hex()
        mutable[offset:end] = replacement
    return bytes(mutable) + tail, originals


def parse_frame_set(value: str) -> set[int]:
    frames: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            frames.update(range(int(start_text), int(end_text) + 1))
        else:
            frames.add(int(part))
    return frames


def load_manager_templates(path: Path) -> dict[int, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    templates = data.get("templates", [])
    return {int(template["frame_index"]): template for template in templates}


def render_manager_template(
    template: dict[str, Any],
    ack_guid: str,
    frame4_sequence: int | None = None,
    managed_form_guid: str | None = None,
) -> tuple[bytes, dict[str, Any]]:
    body = bytearray(bytes.fromhex(template["body_hex"]))
    replacements: list[dict[str, Any]] = []
    for field in template.get("dynamic_fields", []):
        offset = int(field["offset"])
        length = int(field["length"])
        kind = field["kind"]
        if kind == "uuid_le":
            replacement = uuid.UUID(ack_guid).bytes_le
            value: Any = ack_guid
        elif kind == "uint16_le":
            if frame4_sequence is not None and "delta_from_frame4_sequence" in field:
                sequence = frame4_sequence + int(field["delta_from_frame4_sequence"])
            else:
                sequence = int(field["template_value"])
            replacement = sequence.to_bytes(length, byteorder="little")
            value = sequence
        elif kind == "random_bytes":
            replacement = secrets.token_bytes(length)
            value = replacement.hex()
        elif kind == "managed_form_guid_ascii":
            if managed_form_guid is None:
                raise ValueError("managed_form_guid_ascii template field requires a live ManagedForm GUID")
            replacement = managed_form_guid.encode("ascii")
            value = managed_form_guid
        elif kind == "managed_form_guid_utf16le":
            if managed_form_guid is None:
                raise ValueError("managed_form_guid_utf16le template field requires a live ManagedForm GUID")
            replacement = managed_form_guid.encode("utf-16le")
            value = managed_form_guid
        else:
            raise ValueError(f"Unsupported template field kind: {kind}")

        end = offset + length
        original = bytes(body[offset:end])
        if len(original) != length:
            raise ValueError(f"Template field is out of range: {field}")
        body[offset:end] = replacement
        replacements.append(
            {
                "name": field.get("name", ""),
                "kind": kind,
                "offset": offset,
                "length": length,
                "original_hex": original.hex(),
                "replacement_hex": replacement.hex(),
                "value": value,
            }
        )

    tail = bytes.fromhex(template.get("tail_hex", ""))
    return bytes(body) + tail, {"replacements": replacements}


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


def read_capture_chunks(capture_dir: Path) -> list[dict[str, Any]]:
    traffic_path = capture_dir / "traffic.jsonl"
    if not traffic_path.exists():
        raise FileNotFoundError(f"traffic.jsonl not found: {traffic_path}")

    chunks: list[dict[str, Any]] = []
    with traffic_path.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("event") != "chunk":
                continue
            payload = payload_from_record(record)
            chunks.append(
                {
                    "direction": record["direction"],
                    "chunk_no": int(record["chunk_no"]),
                    "byte_count": int(record["byte_count"]),
                    "sha256": record.get("sha256", sha256_hex(payload)),
                    "payload": payload,
                }
            )
    return chunks


def select_chunks(chunks: list[dict[str, Any]], direction: str) -> list[dict[str, Any]]:
    return [chunk for chunk in chunks if chunk["direction"] == direction]


def read_available(sock: socket.socket, first_timeout_sec: float, idle_timeout_sec: float) -> bytes:
    chunks: list[bytes] = []
    deadline = time.monotonic() + first_timeout_sec
    got_any = False

    while True:
        timeout = idle_timeout_sec if got_any else max(0.0, deadline - time.monotonic())
        if timeout <= 0:
            break
        sock.settimeout(timeout)
        try:
            payload = sock.recv(65536)
        except socket.timeout:
            break
        if not payload:
            break
        chunks.append(payload)
        got_any = True

    return b"".join(chunks)


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as file_obj:
        for record in records:
            file_obj.write(json.dumps(record, ensure_ascii=False) + "\n")


def compare_payload(actual: bytes, expected: bytes | None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "actual_byte_count": len(actual),
        "actual_sha256": sha256_hex(actual) if actual else "",
        "actual_head_hex": preview_hex(actual),
    }
    if expected is None:
        result["expected_present"] = False
        return result

    result.update(
        {
            "expected_present": True,
            "expected_byte_count": len(expected),
            "expected_sha256": sha256_hex(expected),
            "expected_head_hex": preview_hex(expected),
            "exact_match": actual == expected,
            "same_length": len(actual) == len(expected),
            "same_prefix_8": actual[:8] == expected[:8],
            "same_prefix_16": actual[:16] == expected[:16],
        }
    )
    return result


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from_script()
    capture_dir = args.capture_dir.resolve() if args.capture_dir else latest_capture_dir(repo_root)
    chunks = read_capture_chunks(capture_dir)
    manager_chunks = select_chunks(chunks, MANAGER_TO_CLIENT)
    client_chunks = select_chunks(chunks, CLIENT_TO_MANAGER)
    manager_templates: dict[int, dict[str, Any]] = {}
    template_frame_indexes: set[int] = set()
    if args.manager_templates:
        template_path = args.manager_templates.resolve()
        manager_templates = load_manager_templates(template_path)
        template_frame_indexes = parse_frame_set(args.template_frames) if args.template_frames else set(manager_templates)

    if not manager_chunks:
        raise RuntimeError(f"No {MANAGER_TO_CLIENT} chunks found in {capture_dir}")
    if not client_chunks:
        raise RuntimeError(f"No {CLIENT_TO_MANAGER} chunks found in {capture_dir}")

    send_count = min(args.send_count, len(manager_chunks))
    if send_count < 1:
        raise ValueError("--send-count must be positive")

    replay_dir = args.output_dir
    if replay_dir is None:
        replay_dir = capture_dir / "replay" / timestamp_name()
    replay_dir = replay_dir.resolve()
    replay_dir.mkdir(parents=True, exist_ok=True)
    steps_dir = replay_dir / "steps"
    steps_dir.mkdir(parents=True, exist_ok=True)

    events: list[dict[str, Any]] = []
    sent_stream = replay_dir / "sent_manager_to_client.bin"
    received_stream = replay_dir / "received_client_to_manager.bin"

    manifest = {
        "schema": "protocol-replay-probe.manifest.v1",
        "started_at": utc_now(),
        "capture_dir": str(capture_dir),
        "replay_dir": str(replay_dir),
        "target_host": args.host,
        "target_port": args.port,
        "send_count": send_count,
        "read_timeout_sec": args.read_timeout_sec,
        "idle_timeout_sec": args.idle_timeout_sec,
        "adapt_frame4_guid": args.adapt_frame4_guid,
        "adapt_frame5_guid": args.adapt_frame5_guid,
        "adapt_frame5_random_blocks": args.adapt_frame5_random_blocks,
        "adapt_frame6_7": args.adapt_frame6_7,
        "adapt_binary_guid_through": args.adapt_binary_guid_through,
        "adapt_binary_single_block_through": args.adapt_binary_single_block_through,
        "adapt_binary_single_block_frames": args.adapt_binary_single_block_frames,
        "adapt_managed_form_guid": args.adapt_managed_form_guid,
        "adapt_ui_path_guids": args.adapt_ui_path_guids,
        "manager_templates": str(args.manager_templates.resolve()) if args.manager_templates else None,
        "template_frames": sorted(template_frame_indexes),
    }
    (replay_dir / "replay_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with socket.create_connection((args.host, args.port), timeout=args.connect_timeout_sec) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        events.append({"ts": utc_now(), "event": "connected"})

        initial = read_available(sock, args.read_timeout_sec, args.idle_timeout_sec)
        initial_path = steps_dir / "initial_read.bin"
        initial_path.write_bytes(initial)
        received_stream.write_bytes(initial)
        initial_expected = client_chunks[0]["payload"] if client_chunks else None
        events.append(
            {
                "ts": utc_now(),
                "event": "initial_read",
                "path": str(initial_path),
                **compare_payload(initial, initial_expected),
            }
        )

        sent_bytes = bytearray()
        received_bytes = bytearray(initial)
        frame4_guid: str | None = None
        captured_frame4_guid: str | None = None
        frame4_sequence: int | None = None
        managed_form_guid: str | None = None
        ui_path_guids: dict[str, str] = {}
        single_block_adapt_through = args.adapt_binary_single_block_through
        single_block_adapt_frames = parse_frame_set(args.adapt_binary_single_block_frames)
        if args.adapt_frame6_7:
            single_block_adapt_frames.update({6, 7})
        if single_block_adapt_through:
            single_block_adapt_frames.update(range(6, single_block_adapt_through + 1))
        guid_adapt_frames = set(single_block_adapt_frames)
        if args.adapt_binary_guid_through:
            guid_adapt_frames.update(range(6, args.adapt_binary_guid_through + 1))
        for index in range(send_count):
            manager_chunk = manager_chunks[index]
            payload = manager_chunk["payload"]
            send_index = index + 1
            if args.adapt_frame4_guid and index == 3:
                if frame4_guid is None:
                    raise RuntimeError("Cannot adapt manager frame 4: no GUID observed after manager frame 3")
                adapted_payload, original_guid = adapt_manager_header_guid(payload, frame4_guid)
                captured_frame4_guid = original_guid
                text = decode_utf8_frame_text(payload)
                if text:
                    header = text.splitlines()[0].strip().strip("{}")
                    header_fields = [field.strip() for field in header.split(",")]
                    if len(header_fields) >= 3 and header_fields[2].isdigit():
                        frame4_sequence = int(header_fields[2])
                events.append(
                    {
                        "ts": utc_now(),
                        "event": "adapted_manager_frame",
                        "send_index": send_index,
                        "source": "client_response_after_send_3",
                        "original_guid": original_guid,
                        "replacement_guid": frame4_guid,
                        "original_sha256": sha256_hex(payload),
                        "adapted_sha256": sha256_hex(adapted_payload),
                        "byte_count": len(adapted_payload),
                    }
                )
                payload = adapted_payload
            used_template_payload = False
            if send_index in template_frame_indexes:
                if frame4_guid is None:
                    raise RuntimeError(
                        f"Cannot render manager template frame {send_index}: no GUID observed after manager frame 3"
                    )
                template = manager_templates.get(send_index)
                if template is None:
                    raise RuntimeError(f"Manager template frame {send_index} is not present in template file")
                rendered_payload, render_info = render_manager_template(
                    template,
                    frame4_guid,
                    frame4_sequence,
                    managed_form_guid,
                )
                events.append(
                    {
                        "ts": utc_now(),
                        "event": "rendered_manager_template_frame",
                        "send_index": send_index,
                        "template_frame_index": int(template["frame_index"]),
                        "template_body_length": int(template["body_length"]),
                        "template_semantic_guess": (template.get("response") or {}).get("semantic_guess", ""),
                        "frame4_sequence": frame4_sequence,
                        "ack_guid": frame4_guid,
                        "managed_form_guid": managed_form_guid,
                        "original_sha256": sha256_hex(payload),
                        "rendered_sha256": sha256_hex(rendered_payload),
                        "byte_count": len(rendered_payload),
                        **render_info,
                    }
                )
                payload = rendered_payload
                used_template_payload = True
            if args.adapt_frame5_guid and index == 4:
                if frame4_guid is None or captured_frame4_guid is None:
                    raise RuntimeError(
                        "Cannot adapt manager frame 5: run with --adapt-frame4-guid so the live GUID is known"
                    )
                adapted_payload, offsets = adapt_binary_uuid_le(payload, captured_frame4_guid, frame4_guid)
                events.append(
                    {
                        "ts": utc_now(),
                        "event": "adapted_binary_manager_frame",
                        "send_index": send_index,
                        "source": "client_response_after_send_3",
                        "encoding": "uuid.bytes_le",
                        "original_guid": captured_frame4_guid,
                        "replacement_guid": frame4_guid,
                        "offsets": offsets,
                        "occurrence_count": len(offsets),
                        "original_sha256": sha256_hex(payload),
                        "adapted_sha256": sha256_hex(adapted_payload),
                        "byte_count": len(adapted_payload),
                    }
                )
                if not offsets:
                    raise RuntimeError("Cannot adapt manager frame 5: captured GUID was not found as UUID bytes_le")
                payload = adapted_payload
            if args.adapt_frame5_random_blocks and index == 4:
                replacements = {
                    67: secrets.token_bytes(16),
                    88: secrets.token_bytes(16),
                }
                adapted_payload, originals = replace_body_ranges(payload, replacements)
                events.append(
                    {
                        "ts": utc_now(),
                        "event": "adapted_binary_manager_frame_blocks",
                        "send_index": send_index,
                        "source": "random",
                        "offsets": sorted(replacements),
                        "original_blocks": originals,
                        "replacement_blocks": {
                            offset: replacement.hex() for offset, replacement in replacements.items()
                        },
                        "original_sha256": sha256_hex(payload),
                        "adapted_sha256": sha256_hex(adapted_payload),
                        "byte_count": len(adapted_payload),
                    }
                )
                payload = adapted_payload
            if not used_template_payload and send_index in guid_adapt_frames:
                if frame4_guid is None or captured_frame4_guid is None:
                    raise RuntimeError(
                        "Cannot adapt binary manager frames: run with --adapt-frame4-guid so the live GUID is known"
                    )
                adapted_payload, offsets = adapt_binary_uuid_le(payload, captured_frame4_guid, frame4_guid)
                if not offsets:
                    raise RuntimeError(
                        f"Cannot adapt manager frame {send_index}: captured GUID was not found as UUID bytes_le"
                    )
                event: dict[str, Any] = {
                    "ts": utc_now(),
                    "event": "adapted_binary_manager_guid_frame",
                    "send_index": send_index,
                    "source": "client_response_after_send_3",
                    "encoding": "uuid.bytes_le",
                    "original_guid": captured_frame4_guid,
                    "replacement_guid": frame4_guid,
                    "guid_offsets": offsets,
                    "original_sha256": sha256_hex(payload),
                    "adapted_sha256": sha256_hex(adapted_payload),
                    "byte_count": len(adapted_payload),
                }
                if send_index in single_block_adapt_frames:
                    replacements = {
                        68: secrets.token_bytes(16),
                    }
                    adapted_payload, originals = replace_body_ranges(adapted_payload, replacements)
                    event.update(
                        {
                            "event": "adapted_binary_manager_single_block_frame",
                            "source": "client_response_after_send_3/random",
                            "block_offsets": sorted(replacements),
                            "original_blocks": originals,
                            "replacement_blocks": {
                                offset: replacement.hex() for offset, replacement in replacements.items()
                            },
                            "adapted_sha256": sha256_hex(adapted_payload),
                            "byte_count": len(adapted_payload),
                        }
                    )
                events.append(event)
                payload = adapted_payload
            if not used_template_payload and args.adapt_ui_path_guids:
                ui_path_references = find_ui_path_guid_references(payload)
                if ui_path_references:
                    missing_kinds = sorted(
                        {str(reference["kind"]) for reference in ui_path_references if reference["kind"] not in ui_path_guids}
                    )
                    if missing_kinds:
                        raise RuntimeError(
                            f"Cannot adapt manager frame {send_index}: no live UI path GUID observed for "
                            + ", ".join(missing_kinds)
                        )
                    adapted_payload, replacements = adapt_ui_path_guids(payload, ui_path_guids)
                    if replacements:
                        events.append(
                            {
                                "ts": utc_now(),
                                "event": "adapted_ui_path_guids",
                                "send_index": send_index,
                                "source": "latest_observed_client_response",
                                "ui_path_guids": dict(ui_path_guids),
                                "references": ui_path_references,
                                "replacements": replacements,
                                "original_sha256": sha256_hex(payload),
                                "adapted_sha256": sha256_hex(adapted_payload),
                                "byte_count": len(adapted_payload),
                            }
                        )
                        payload = adapted_payload
            if not used_template_payload and args.adapt_managed_form_guid:
                managed_form_references = find_managed_form_guid_references(payload)
                if managed_form_references:
                    if managed_form_guid is None:
                        raise RuntimeError(
                            f"Cannot adapt manager frame {send_index}: no live ManagedForm GUID observed"
                        )
                    adapted_payload, replacements = adapt_managed_form_guid(payload, managed_form_guid)
                    if replacements:
                        events.append(
                            {
                                "ts": utc_now(),
                                "event": "adapted_managed_form_guid",
                                "send_index": send_index,
                                "source": "latest_observed_client_response",
                                "replacement_guid": managed_form_guid,
                                "references": managed_form_references,
                                "replacements": replacements,
                                "original_sha256": sha256_hex(payload),
                                "adapted_sha256": sha256_hex(adapted_payload),
                                "byte_count": len(adapted_payload),
                            }
                        )
                        payload = adapted_payload
            sock.sendall(payload)
            sent_bytes.extend(payload)
            sent_path = steps_dir / f"sent_{index + 1:03d}_manager_to_client.bin"
            sent_path.write_bytes(payload)
            expected_response = client_chunks[index + 1]["payload"] if index + 1 < len(client_chunks) else None
            events.append(
                {
                    "ts": utc_now(),
                    "event": "sent",
                    "send_index": send_index,
                    "path": str(sent_path),
                    "capture_chunk_no": manager_chunk["chunk_no"],
                    "byte_count": len(payload),
                    "sha256": sha256_hex(payload),
                    "head_hex": preview_hex(payload),
                }
            )

            response = read_available(sock, args.read_timeout_sec, args.idle_timeout_sec)
            received_bytes.extend(response)
            response_path = steps_dir / f"response_after_send_{index + 1:03d}_client_to_manager.bin"
            response_path.write_bytes(response)
            expected_path = None
            if expected_response is not None:
                expected_path = steps_dir / f"expected_after_send_{index + 1:03d}_client_to_manager.bin"
                expected_path.write_bytes(expected_response)
            events.append(
                {
                    "ts": utc_now(),
                    "event": "response",
                    "after_send_index": send_index,
                    "path": str(response_path),
                    "expected_path": str(expected_path) if expected_path else None,
                    **compare_payload(response, expected_response),
                }
            )
            if args.adapt_frame4_guid and index == 2:
                frame4_guid = extract_client_ack_guid(response)
                events.append(
                    {
                        "ts": utc_now(),
                        "event": "observed_frame4_guid",
                        "after_send_index": index + 1,
                        "guid": frame4_guid,
                        "source_response_path": str(response_path),
                    }
                )
            observed_managed_form_guid = extract_managed_form_guid(response)
            if observed_managed_form_guid and observed_managed_form_guid != managed_form_guid:
                managed_form_guid = observed_managed_form_guid
                events.append(
                    {
                        "ts": utc_now(),
                        "event": "observed_managed_form_guid",
                        "after_send_index": index + 1,
                        "guid": managed_form_guid,
                        "source_response_path": str(response_path),
                    }
                )
            if args.adapt_ui_path_guids:
                for reference in find_ui_path_guid_references(response):
                    kind = str(reference["kind"])
                    guid = str(reference["guid"])
                    if ui_path_guids.get(kind) == guid:
                        continue
                    ui_path_guids[kind] = guid
                    events.append(
                        {
                            "ts": utc_now(),
                            "event": "observed_ui_path_guid",
                            "after_send_index": send_index,
                            "kind": kind,
                            "guid": guid,
                            "encoding": reference["encoding"],
                            "offset": reference["offset"],
                            "source_response_path": str(response_path),
                        }
                    )
            if args.stop_on_no_response and not response:
                events.append(
                    {
                        "ts": utc_now(),
                        "event": "stopped",
                        "reason": "no response",
                        "after_send_index": index + 1,
                    }
                )
                break

        sent_stream.write_bytes(bytes(sent_bytes))
        received_stream.write_bytes(bytes(received_bytes))

    summary = {
        "schema": "protocol-replay-probe.summary.v1",
        "status": "ok",
        "capture_dir": str(capture_dir),
        "replay_dir": str(replay_dir),
        "sent_byte_count": sent_stream.stat().st_size,
        "received_byte_count": received_stream.stat().st_size,
        "event_count": len(events),
        "finished_at": utc_now(),
    }
    (replay_dir / "replay_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_jsonl(replay_dir / "replay_events.jsonl", events)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "capture_dir",
        nargs="?",
        type=Path,
        help="Capture directory. Defaults to latest runtime/protocol-research/captures/<timestamp>.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=15381)
    parser.add_argument("--send-count", type=int, default=1)
    parser.add_argument("--connect-timeout-sec", type=float, default=10.0)
    parser.add_argument("--read-timeout-sec", type=float, default=5.0)
    parser.add_argument("--idle-timeout-sec", type=float, default=0.25)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--stop-on-no-response", action="store_true")
    parser.add_argument(
        "--adapt-frame4-guid",
        action="store_true",
        help="Replace manager frame 4 header GUID with the GUID observed in the live response after frame 3.",
    )
    parser.add_argument(
        "--adapt-frame5-guid",
        action="store_true",
        help="Replace the captured frame 4 GUID inside binary manager frame 5 using UUID little-endian bytes.",
    )
    parser.add_argument(
        "--adapt-frame5-random-blocks",
        action="store_true",
        help="Replace two 16-byte binary manager frame 5 blocks at offsets 67 and 88 with random bytes.",
    )
    parser.add_argument(
        "--adapt-frame6-7",
        action="store_true",
        help="Adapt binary manager frames 6 and 7: replace ACK GUID at offset 2 and random block at offset 68.",
    )
    parser.add_argument(
        "--adapt-binary-single-block-through",
        type=int,
        default=0,
        metavar="N",
        help="Adapt binary manager frames 6..N: replace ACK GUID at offset 2 and random block at offset 68.",
    )
    parser.add_argument(
        "--adapt-binary-single-block-frames",
        default="",
        metavar="FRAMES",
        help="Additional binary manager frames/ranges for GUID plus random-block adaptation, for example 123-124.",
    )
    parser.add_argument(
        "--adapt-binary-guid-through",
        type=int,
        default=0,
        metavar="N",
        help="Adapt binary manager frames 6..N by replacing only the ACK GUID at offset 2.",
    )
    parser.add_argument(
        "--adapt-managed-form-guid",
        action="store_true",
        help="Replace raw ManagedForm[...] GUID references with the latest live ManagedForm GUID observed in responses.",
    )
    parser.add_argument(
        "--adapt-ui-path-guids",
        action="store_true",
        help="Replace raw MainFrame/SecondaryFrame/ManagedForm GUID references with latest live GUIDs observed in responses.",
    )
    parser.add_argument(
        "--manager-templates",
        type=Path,
        help="manager_frame_templates.json generated by extract_manager_templates.py.",
    )
    parser.add_argument(
        "--template-frames",
        default="",
        help="Frame indexes to render from --manager-templates, for example 8-10. Defaults to all templates.",
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run_probe(args)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"status={summary['status']}")
        print(f"replay_dir={summary['replay_dir']}")
        print(f"sent_byte_count={summary['sent_byte_count']}")
        print(f"received_byte_count={summary['received_byte_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
