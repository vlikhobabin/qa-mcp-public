"""Render demo-catalog-mutation write-command frames for the Python manager.

The write template is decoded from two byte-identical reference captures (see
``docs/protocol-research/evidence/.../decode-findings.md``). Each manager command
frame carries a small, fully characterized set of dynamic fields:

- ``per_frame_message_id`` (offset 2, 16 bytes): a fresh per-frame UUID;
- ``uint16_le_sequence`` (offset 19, 2 bytes): the frame sequence number;
- ``random_bytes`` (nonce, 16 bytes): a fresh per-frame nonce;
- ``session_guid_ascii`` / ``session_guid_utf16le``: the runtime-assigned
  SecondaryFrame / ManagedForm GUIDs, rendered as ASCII and UTF-16LE path text.

``render_write_frame`` substitutes live values into one template frame so the
manager can construct (and later send) the write opcode against a fresh session,
rather than replaying captured bytes verbatim.

CORRECTION (2026-06-12, write-synthesis gate): the offset-2 16-byte field labeled
``per_frame_message_id`` above is actually the **per-session ack/connection GUID**
(constant across ~857/861 frames, learnable as an ASCII guid). It must be
*rebound* to the live session value, NOT regenerated. ``render_write_frame``
substitutes only the SecondaryFrame/ManagedForm session GUIDs, so it leaves the
ack GUID stale and the live client rejects the write (uniform 665 response). The
correct live write synthesizer is ``qa_mcp.protocol.navigation.render_form_command``
(global GUID rebind in all encodings, incl. the binary ack GUID) plus a fresh
offset-68 nonce; ``render_write_frame`` is kept only for the offline template
round-trip. See ``write_synthesis_gate_resolved.json``.
"""

from __future__ import annotations

import secrets
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RenderedWriteFrame:
    payload: bytes
    replacements: list[dict[str, Any]] = field(default_factory=list)


def _put(buffer: bytearray, offset: int, value: bytes) -> bytes:
    original = bytes(buffer[offset : offset + len(value)])
    buffer[offset : offset + len(value)] = value
    return original


def render_write_frame(
    template_frame: dict[str, Any],
    *,
    message_id: uuid.UUID | None = None,
    sequence: int | None = None,
    nonce: bytes | None = None,
    session_guid_map: dict[str, str] | None = None,
) -> RenderedWriteFrame:
    """Render one template command frame with fresh live dynamic fields.

    ``session_guid_map`` maps each template (captured) session GUID to the live
    GUID assigned by the current session. Missing entries keep the captured GUID.
    """

    body = bytearray(bytes.fromhex(template_frame["body_hex"]))
    message_id = message_id or uuid.uuid4()
    session_guid_map = session_guid_map or {}
    replacements: list[dict[str, Any]] = []

    for field_item in template_frame.get("dynamic_fields", []):
        kind = field_item["kind"]
        offset = int(field_item["offset"])
        length = int(field_item["length"])

        if kind == "per_frame_message_id":
            value = message_id.bytes_le[:length]
        elif kind == "uint16_le_sequence":
            seq = int(sequence) if sequence is not None else int.from_bytes(body[offset : offset + length], "little")
            value = seq.to_bytes(length, "little")
        elif kind == "random_bytes":
            value = (nonce or secrets.token_bytes(length))[:length]
        elif kind in ("session_guid_ascii", "session_guid_utf16le"):
            old_guid = field_item.get("guid")
            new_guid = session_guid_map.get(old_guid, old_guid)
            text = str(new_guid)
            value = text.encode("ascii") if kind == "session_guid_ascii" else text.encode("utf-16le")
            if len(value) != length:
                raise ValueError(f"session guid field length mismatch at offset {offset}: {field_item}")
        else:
            raise ValueError(f"unsupported write-template field kind: {kind}")

        original = _put(body, offset, value)
        replacements.append(
            {
                "name": field_item.get("name", kind),
                "kind": kind,
                "offset": offset,
                "length": length,
                "original_hex": original.hex(),
                "replacement_hex": value.hex(),
            }
        )

    return RenderedWriteFrame(payload=bytes(body), replacements=replacements)
