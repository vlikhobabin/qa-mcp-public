from __future__ import annotations

import base64
import json
import uuid
from pathlib import Path

import pytest

from qa_mcp.protocol import (
    CLIENT_TO_MANAGER,
    MANAGER_TO_CLIENT,
    TAIL_MARKER,
    CaptureBootstrap,
    ProtocolTemplates,
    adapt_manager_header_guid,
    extract_client_ack_guid,
    manager_frame_sequence,
    split_tail_marker,
)


def test_frame_header_and_ack_helpers() -> None:
    original = "11111111-1111-1111-1111-111111111111"
    replacement = "22222222-2222-2222-2222-222222222222"
    payload = f"{{0,{original},42}}\nbody".encode("utf-8") + TAIL_MARKER

    adapted, observed = adapt_manager_header_guid(payload, replacement)

    assert observed == original
    assert adapted.startswith(f"{{0,{replacement},42}}".encode("utf-8"))
    assert manager_frame_sequence(adapted) == 42
    assert split_tail_marker(adapted)[1] == TAIL_MARKER

    ack_payload = (
        f'{{"#",{original},\n'
        f"{{{replacement}}}"
    ).encode("utf-8")
    assert extract_client_ack_guid(ack_payload) == replacement


def test_protocol_templates_render_dynamic_fields(tmp_path: Path) -> None:
    body = bytearray(b"\x00" * 140)
    template_path = tmp_path / "manager_frame_templates.json"
    template_path.write_text(
        json.dumps(
            {
                "templates": [
                    {
                        "frame_index": 8,
                        "body_hex": bytes(body).hex(),
                        "tail_hex": TAIL_MARKER.hex(),
                        "dynamic_fields": [
                            {"name": "ack", "kind": "uuid_le", "offset": 2, "length": 16},
                            {
                                "name": "sequence",
                                "kind": "uint16_le",
                                "offset": 19,
                                "length": 2,
                                "delta_from_frame4_sequence": 4,
                            },
                            {"name": "nonce", "kind": "random_bytes", "offset": 68, "length": 16},
                            {
                                "name": "form_guid",
                                "kind": "managed_form_guid_ascii",
                                "offset": 90,
                                "length": 36,
                            },
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    ack_guid = "33333333-3333-3333-3333-333333333333"
    form_guid = "44444444-4444-4444-4444-444444444444"

    rendered = ProtocolTemplates.load(template_path).render(
        frame_index=8,
        ack_guid=ack_guid,
        frame4_sequence=10,
        managed_form_guid=form_guid,
    )

    assert rendered.payload.endswith(TAIL_MARKER)
    assert rendered.payload[2:18] == uuid.UUID(ack_guid).bytes_le
    assert rendered.payload[19:21] == (14).to_bytes(2, byteorder="little")
    assert rendered.payload[90:126] == form_guid.encode("ascii")
    assert [item["name"] for item in rendered.replacements] == ["ack", "sequence", "nonce", "form_guid"]


def test_capture_bootstrap_loads_directional_frames(tmp_path: Path) -> None:
    capture_dir = tmp_path / "capture"
    capture_dir.mkdir()
    traffic_path = capture_dir / "traffic.jsonl"
    rows = []
    for index in range(1, 11):
        rows.append(
            {
                "event": "chunk",
                "direction": MANAGER_TO_CLIENT,
                "chunk_no": index,
                "payload_b64": base64.b64encode(f"manager-{index}".encode("ascii")).decode("ascii"),
            }
        )
        rows.append(
            {
                "event": "chunk",
                "direction": CLIENT_TO_MANAGER,
                "chunk_no": index,
                "payload_b64": base64.b64encode(f"client-{index}".encode("ascii")).decode("ascii"),
            }
        )
    traffic_path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

    bootstrap = CaptureBootstrap.load(capture_dir)

    assert bootstrap.captured_frame(1) == b"manager-1"
    assert bootstrap.captured_frame(10) == b"manager-10"
    assert bootstrap.client_frames[0] == b"client-1"


def test_capture_bootstrap_rejects_incomplete_manager_frames(tmp_path: Path) -> None:
    capture_dir = tmp_path / "capture"
    capture_dir.mkdir()
    row = {
        "event": "chunk",
        "direction": MANAGER_TO_CLIENT,
        "chunk_no": 1,
        "payload_b64": base64.b64encode(b"manager-1").decode("ascii"),
    }
    (capture_dir / "traffic.jsonl").write_text(json.dumps(row), encoding="utf-8")

    with pytest.raises(RuntimeError, match="does not contain manager frames"):
        CaptureBootstrap.load(capture_dir)
