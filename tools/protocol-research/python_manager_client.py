#!/usr/bin/env python3
"""Compatibility facade for package-owned direct TestClient protocol APIs."""

from __future__ import annotations

import sys
from pathlib import Path


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


_REPO_ROOT = repo_root_from_script()
_SRC_PATH = _REPO_ROOT / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

from qa_mcp.protocol import (  # noqa: E402
    CLIENT_TO_MANAGER,
    MANAGER_TO_CLIENT,
    TAIL_MARKER,
    ActiveFormContext,
    ActiveWindowContext,
    BootstrapFrameRenderer,
    CaptureBootstrap,
    FormElementDetailsContext,
    FormSummaryContext,
    InitialUiContext,
    OperationDescriptor,
    ProtocolTemplates,
    RenderedFrame,
    TestClientSession,
    adapt_manager_header_guid,
    extract_client_ack_guid,
    extract_managed_form_guid,
    manager_frame_sequence,
    payload_summary,
    read_available,
    resolve_capture_dir as _resolve_capture_dir,
    sha256_hex,
    split_tail_marker,
    strip_tail,
    timestamp_name,
    utc_now,
)
from qa_mcp.protocol.bootstrap import captures_root, payload_from_record  # noqa: E402
from qa_mcp.protocol.frames import decode_utf8_frame_text, find_positions, preview_hex, replace_body_ranges  # noqa: E402
from qa_mcp.protocol.responses import (  # noqa: E402
    ascii_strings,
    extract_active_form_fields,
    extract_active_window_fields,
    extract_element_details,
    extract_form_elements,
    response_summary,
    semantic_guess,
    ui_identifiers,
    utf16le_strings,
)


def resolve_capture_dir(value: str, repo_root: Path) -> Path:
    return _resolve_capture_dir(value, repo_root)


__all__ = [
    "CLIENT_TO_MANAGER",
    "MANAGER_TO_CLIENT",
    "TAIL_MARKER",
    "ActiveFormContext",
    "ActiveWindowContext",
    "BootstrapFrameRenderer",
    "CaptureBootstrap",
    "FormElementDetailsContext",
    "FormSummaryContext",
    "InitialUiContext",
    "OperationDescriptor",
    "ProtocolTemplates",
    "RenderedFrame",
    "TestClientSession",
    "adapt_manager_header_guid",
    "ascii_strings",
    "captures_root",
    "decode_utf8_frame_text",
    "extract_active_form_fields",
    "extract_active_window_fields",
    "extract_client_ack_guid",
    "extract_element_details",
    "extract_form_elements",
    "extract_managed_form_guid",
    "find_positions",
    "manager_frame_sequence",
    "payload_from_record",
    "payload_summary",
    "preview_hex",
    "read_available",
    "replace_body_ranges",
    "repo_root_from_script",
    "resolve_capture_dir",
    "response_summary",
    "semantic_guess",
    "sha256_hex",
    "split_tail_marker",
    "strip_tail",
    "timestamp_name",
    "ui_identifiers",
    "utc_now",
    "utf16le_strings",
]
