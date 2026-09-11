"""Manager-frame template rendering for direct TestClient protocol sessions."""

from __future__ import annotations

import json
import secrets
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .frames import replace_body_ranges


@dataclass(frozen=True)
class RenderedFrame:
    payload: bytes
    replacements: list[dict[str, Any]]
    source: str


class ProtocolTemplates:
    """Renderer for captured manager-frame templates with live dynamic fields."""

    def __init__(self, path: Path, templates: dict[int, dict[str, Any]]) -> None:
        self.path = path
        self.templates = templates

    @classmethod
    def load(cls, path: Path) -> "ProtocolTemplates":
        resolved = path.resolve()
        data = json.loads(resolved.read_text(encoding="utf-8-sig"))
        templates = {int(template["frame_index"]): template for template in data.get("templates", [])}
        return cls(path=resolved, templates=templates)

    def render(
        self,
        frame_index: int,
        ack_guid: str,
        frame4_sequence: int,
        managed_form_guid: str | None = None,
        secondary_frame_guid: str | None = None,
    ) -> RenderedFrame:
        template = self.templates.get(frame_index)
        if template is None:
            raise RuntimeError(f"Manager template {frame_index} not found")

        body = bytearray(bytes.fromhex(template["body_hex"]))
        replacements: list[dict[str, Any]] = []
        for field_item in template.get("dynamic_fields", []):
            offset = int(field_item["offset"])
            length = int(field_item["length"])
            kind = field_item["kind"]
            if kind == "uuid_le":
                replacement = uuid.UUID(ack_guid).bytes_le
                value: Any = ack_guid
            elif kind == "uint16_le":
                sequence = frame4_sequence + int(field_item.get("delta_from_frame4_sequence", 0))
                # The wire field is `length` bytes wide; the message counter (5-digit ASCII elsewhere)
                # exceeds it, so the narrow numeric field wraps modulo its width (e.g. uint16).
                replacement = (sequence & ((1 << (8 * length)) - 1)).to_bytes(length, byteorder="little")
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
            elif kind == "secondary_frame_guid_ascii":
                if secondary_frame_guid is None:
                    raise ValueError("secondary_frame_guid_ascii template field requires a live SecondaryFrame GUID")
                replacement = secondary_frame_guid.encode("ascii")
                value = secondary_frame_guid
            elif kind == "secondary_frame_guid_utf16le":
                if secondary_frame_guid is None:
                    raise ValueError("secondary_frame_guid_utf16le template field requires a live SecondaryFrame GUID")
                replacement = secondary_frame_guid.encode("utf-16le")
                value = secondary_frame_guid
            else:
                raise ValueError(f"Unsupported template field kind: {kind}")

            end = offset + length
            original = bytes(body[offset:end])
            if len(original) != length:
                raise ValueError(f"Template field out of range: {field_item}")
            body[offset:end] = replacement
            replacements.append(
                {
                    "name": field_item.get("name", ""),
                    "kind": kind,
                    "offset": offset,
                    "length": length,
                    "original_hex": original.hex(),
                    "replacement_hex": replacement.hex(),
                    "value": value,
                }
            )

        payload = bytes(body) + bytes.fromhex(template.get("tail_hex", ""))
        return RenderedFrame(payload=payload, replacements=replacements, source="generated_manager_template_json")


class BootstrapFrameRenderer:
    """Renderer for frames still derived from the captured bootstrap."""

    @staticmethod
    def render_frame5(captured: bytes, ack_guid: str, frame4_sequence: int) -> RenderedFrame:
        replacements = {
            2: uuid.UUID(ack_guid).bytes_le,
            19: ((frame4_sequence + 1) & 0xFFFF).to_bytes(2, byteorder="little"),
            67: secrets.token_bytes(16),
            88: secrets.token_bytes(16),
        }
        rendered, originals = replace_body_ranges(captured, replacements)
        return RenderedFrame(
            payload=rendered,
            source="generated_frame5_template",
            replacements=[
                {
                    "name": "ack_guid" if offset == 2 else "sequence" if offset == 19 else f"nonce_{offset}",
                    "offset": offset,
                    "length": len(value),
                    "original_hex": originals[offset],
                    "replacement_hex": value.hex(),
                }
                for offset, value in sorted(replacements.items())
            ],
        )

    @staticmethod
    def render_single_block_frame(
        captured: bytes,
        ack_guid: str,
        frame4_sequence: int,
        frame_index: int,
    ) -> RenderedFrame:
        replacements = {
            2: uuid.UUID(ack_guid).bytes_le,
            19: ((frame4_sequence + (frame_index - 4)) & 0xFFFF).to_bytes(2, byteorder="little"),
            68: secrets.token_bytes(16),
        }
        rendered, originals = replace_body_ranges(captured, replacements)
        return RenderedFrame(
            payload=rendered,
            source="generated_single_block_from_capture_template",
            replacements=[
                {
                    "name": "ack_guid" if offset == 2 else "sequence" if offset == 19 else "nonce",
                    "offset": offset,
                    "length": len(value),
                    "original_hex": originals[offset],
                    "replacement_hex": value.hex(),
                }
                for offset, value in sorted(replacements.items())
            ],
        )
