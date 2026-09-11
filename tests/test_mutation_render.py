from __future__ import annotations

import uuid
from pathlib import Path

from qa_mcp.protocol.mutation import render_write_frame


def _synthetic_template_frame() -> dict:
    old_guid = "d107afff-b899-4eea-90ba-4c50ac244bff"
    # 140-byte body: message id @2, sequence @19, nonce @68, guid ascii @96 (+36=132)
    body = bytearray(140)
    body[96 : 96 + 36] = old_guid.encode("ascii")
    return {
        "ordinal": 0,
        "direction": "manager_to_client",
        "byte_count": 140,
        "body_hex": bytes(body).hex(),
        "dynamic_fields": [
            {"name": "message_id", "offset": 2, "length": 16, "kind": "per_frame_message_id"},
            {"name": "sequence", "offset": 19, "length": 2, "kind": "uint16_le_sequence"},
            {"name": "nonce", "offset": 68, "length": 16, "kind": "random_bytes"},
            {
                "name": "session_guid_ascii",
                "offset": 96,
                "length": 36,
                "kind": "session_guid_ascii",
                "guid": old_guid,
            },
        ],
    }


def test_render_substitutes_all_dynamic_fields() -> None:
    template = _synthetic_template_frame()
    mid = uuid.UUID("11111111-2222-3333-4444-555555555555")
    nonce = bytes(range(16))
    new_guid = "abcdef01-2345-6789-abcd-ef0123456789"
    rendered = render_write_frame(
        template,
        message_id=mid,
        sequence=7,
        nonce=nonce,
        session_guid_map={"d107afff-b899-4eea-90ba-4c50ac244bff": new_guid},
    )
    payload = rendered.payload
    assert len(payload) == 140
    assert payload[2:18] == mid.bytes_le
    assert payload[19:21] == (7).to_bytes(2, "little")
    assert payload[68:84] == nonce
    assert payload[96:132] == new_guid.encode("ascii")
    # the captured guid must be gone
    assert b"d107afff-b899-4eea-90ba-4c50ac244bff" not in payload
    kinds = {r["kind"] for r in rendered.replacements}
    assert kinds == {
        "per_frame_message_id",
        "uint16_le_sequence",
        "random_bytes",
        "session_guid_ascii",
    }


def test_render_keeps_captured_guid_when_unmapped() -> None:
    template = _synthetic_template_frame()
    rendered = render_write_frame(template, message_id=uuid.uuid4(), sequence=1)
    # no session_guid_map => the captured guid stays in place at its offset
    assert rendered.payload[96:132] == b"d107afff-b899-4eea-90ba-4c50ac244bff"


def test_render_real_template_frame_if_present() -> None:
    template_path = (
        Path(__file__).resolve().parents[1]
        / "runtime"
        / "protocol-research"
        / "templates"
        / "demo_catalog_mutation_write_template.json"
    )
    if not template_path.exists():
        return  # raw template lives under ignored runtime/; skip when absent
    import json

    template = json.loads(template_path.read_text(encoding="utf-8"))
    frame0 = template["frames"][0]
    rendered = render_write_frame(frame0, message_id=uuid.uuid4(), sequence=123)
    assert len(rendered.payload) == frame0["byte_count"]
    assert rendered.payload[19:21] == (123).to_bytes(2, "little")
