"""Low-level frame helpers for the native 1C TestClient protocol."""

from __future__ import annotations

import codecs
import hashlib
import re
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
SECONDARY_FRAME_GUID_RE = re.compile(rb"SecondaryFrame\[(?P<guid>" + GUID_PATTERN.encode("ascii") + rb")\]")


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def preview_hex(payload: bytes, limit: int = 64) -> str:
    return payload[:limit].hex()


def split_tail_marker(payload: bytes) -> tuple[bytes, bytes]:
    if payload.endswith(TAIL_MARKER):
        return payload[: -len(TAIL_MARKER)], TAIL_MARKER
    return payload, b""


def strip_tail(payload: bytes) -> bytes:
    return split_tail_marker(payload)[0]


def decode_utf8_frame_text(payload: bytes) -> str | None:
    body, _tail = split_tail_marker(payload)
    if body.startswith(codecs.BOM_UTF8):
        body = body[len(codecs.BOM_UTF8) :]
    try:
        return body.decode("utf-8")
    except UnicodeDecodeError:
        return None


def extract_client_ack_guid(payload: bytes) -> str:
    text = decode_utf8_frame_text(payload)
    if text is None:
        raise ValueError("client response is not a UTF-8 text frame")
    match = CLIENT_ACK_GUID_RE.search(text)
    if not match:
        raise ValueError("client ACK GUID not found in response after manager frame 3")
    return match.group(1).lower()


def extract_managed_form_guid(payload: bytes) -> str | None:
    body, _tail = split_tail_marker(payload)
    match = MANAGED_FORM_GUID_RE.search(body)
    if not match:
        return None
    return match.group("guid").decode("ascii").lower()


def extract_secondary_frame_guid(payload: bytes) -> str | None:
    body, _tail = split_tail_marker(payload)
    match = SECONDARY_FRAME_GUID_RE.search(body)
    if not match:
        return None
    return match.group("guid").decode("ascii").lower()


def manager_frame_sequence(payload: bytes) -> int:
    text = decode_utf8_frame_text(payload)
    if text is None:
        raise ValueError("manager frame is not a UTF-8 text frame")
    first_line = text.splitlines()[0].strip().strip("{}")
    fields = [field.strip() for field in first_line.split(",")]
    if len(fields) < 3 or not fields[2].isdigit():
        raise ValueError(f"manager frame sequence not found: {first_line}")
    return int(fields[2])


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


def payload_summary(payload: bytes) -> dict[str, Any]:
    body, tail = split_tail_marker(payload)
    return {
        "byte_count": len(payload),
        "body_byte_count": len(body),
        "tail_hex": tail.hex(),
        "sha256": sha256_hex(payload),
        "head_hex": preview_hex(payload),
    }
