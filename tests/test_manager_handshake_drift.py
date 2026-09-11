"""Offline tests for manager-handshake drift diagnostics."""

from __future__ import annotations

import codecs
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.protocol.capture_metadata import CaptureMetadata, CaptureSelection  # noqa: E402
from qa_mcp.protocol.frames import TAIL_MARKER  # noqa: E402
from qa_mcp.protocol.handshake import classify_manager_handshake_response  # noqa: E402


def _selection() -> CaptureSelection:
    return CaptureSelection(
        capture=CaptureMetadata(
            capture_id="demo10413-nextrow",
            platform_build="8.3.27.2130",
            configuration_name="demo10413",
            capture_dir="src/qa_mcp/_bundled/8.3/captures/nextrow",
        ),
        match="fallback",
        requested_platform_build="8.3.27.2130",
        requested_configuration="Бухгалтерия 3.0",
        exact_config_match=False,
        reason="fallback capture is not config-matched",
    )


def test_manager_handshake_ack_success_records_guid() -> None:
    response = (
        codecs.BOM_UTF8
        + b'{"#",11111111-1111-1111-1111-111111111111,\r\n'
        + b"{22222222-2222-2222-2222-222222222222}\r\n}"
        + TAIL_MARKER
    )

    result = classify_manager_handshake_response(response, selection=_selection())

    assert result.ok is True
    assert result.error is None
    assert result.ack_guid == "22222222-2222-2222-2222-222222222222"
    assert result.to_dict()["capture_selection"]["match"] == "fallback"


def test_manager_handshake_missing_ack_fails_loudly() -> None:
    result = classify_manager_handshake_response(
        codecs.BOM_UTF8 + b'{"unexpected":"shape"}' + TAIL_MARKER,
        selection=_selection(),
    )

    assert result.ok is False
    assert result.error == "manager-handshake-moved"
    assert result.frame_index == 3
    assert "refresh" in result.action_hint.lower()
    payload = result.to_dict()
    assert payload["capture_selection"]["capture"]["capture_id"] == "demo10413-nextrow"
    assert payload["requested"] == {
        "platform_build": "8.3.27.2130",
        "configuration": "Бухгалтерия 3.0",
    }
