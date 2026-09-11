"""Offline tests for config-tagged capture metadata and selection."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.protocol.capture_metadata import (  # noqa: E402
    CaptureMetadata,
    load_capture_metadata,
    select_capture_metadata,
    write_capture_metadata,
)


def test_capture_metadata_roundtrip_is_sanitized(tmp_path: Path) -> None:
    metadata = CaptureMetadata(
        capture_id="third-party-config-currencies",
        platform_build="8.3.27.2130",
        configuration_name="Бухгалтерия предприятия",
        configuration_version="3.0",
        configuration_vendor="[redacted third-party configuration]",
        capture_dir="runtime/protocol-research/captures/third-party-config-currencies",
        manager_templates="runtime/protocol-research/templates/third-party-config/manager_frame_templates.json",
        notes="sanitized sidecar only",
    )

    path = tmp_path / "capture-metadata.json"
    write_capture_metadata(path, metadata)
    raw = json.loads(path.read_text(encoding="utf-8"))

    assert raw["schema"] == "qa-mcp.protocol-capture-metadata.v1"
    assert raw["platform_build"] == "8.3.27.2130"
    assert raw["configuration"]["name"] == "Бухгалтерия предприятия"
    assert "payload_b64" not in path.read_text(encoding="utf-8")
    assert load_capture_metadata(path) == metadata


def test_select_capture_metadata_prefers_exact_platform_and_config_match() -> None:
    demo = CaptureMetadata(
        capture_id="demo10413-nextrow",
        platform_build="8.3.27.2130",
        configuration_name="demo10413",
        capture_dir="src/qa_mcp/_bundled/8.3/captures/nextrow",
    )
    bit = CaptureMetadata(
        capture_id="third-party-config-currencies",
        platform_build="8.3.27.2130",
        configuration_name="Бухгалтерия 3.0",
        capture_dir="runtime/protocol-research/captures/third-party-config-currencies",
    )

    selection = select_capture_metadata(
        [demo, bit],
        requested_platform_build="8.3.27.2130",
        requested_configuration="бухгалтерия 3.0",
        fallback_capture_id="demo10413-nextrow",
    )

    assert selection.capture == bit
    assert selection.match == "exact"
    assert selection.exact_config_match is True
    assert selection.to_dict()["requested"]["configuration"] == "бухгалтерия 3.0"


def test_select_capture_metadata_fallback_is_observable() -> None:
    demo = CaptureMetadata(
        capture_id="demo10413-nextrow",
        platform_build="8.3.27.2130",
        configuration_name="demo10413",
        capture_dir="src/qa_mcp/_bundled/8.3/captures/nextrow",
    )

    selection = select_capture_metadata(
        [demo],
        requested_platform_build="8.3.27.2130",
        requested_configuration="Бухгалтерия 3.0",
        fallback_capture_id="demo10413-nextrow",
    )

    assert selection.capture == demo
    assert selection.match == "fallback"
    assert selection.exact_config_match is False
    assert "not config-matched" in selection.reason
    assert selection.to_dict()["requested"] == {
        "platform_build": "8.3.27.2130",
        "configuration": "Бухгалтерия 3.0",
    }
