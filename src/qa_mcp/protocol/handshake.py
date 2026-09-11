"""Manager-handshake drift diagnostics for TestClient protocol captures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .capture_metadata import CaptureSelection
from .frames import extract_client_ack_guid, preview_hex, sha256_hex

MANAGER_HANDSHAKE_MOVED = "manager-handshake-moved"
ACK_MISSING_DETAIL = "client ACK GUID not found in response after manager frame 3"


@dataclass(frozen=True)
class ManagerHandshakePreflightResult:
    ok: bool
    frame_index: int = 3
    ack_guid: str | None = None
    error: str | None = None
    detail: str = ""
    action_hint: str = ""
    response_byte_count: int = 0
    response_sha256: str = ""
    response_head_hex: str = ""
    selection: CaptureSelection | None = None
    requested_platform_build: str | None = None
    requested_configuration: str | None = None

    def to_dict(self) -> dict[str, Any]:
        requested = {
            "platform_build": self.requested_platform_build,
            "configuration": self.requested_configuration,
        }
        if self.selection is not None:
            requested = self.selection.to_dict()["requested"]
        payload: dict[str, Any] = {
            "ok": self.ok,
            "frame_index": self.frame_index,
            "ack_guid": self.ack_guid,
            "error": self.error,
            "detail": self.detail,
            "action_hint": self.action_hint,
            "response_byte_count": self.response_byte_count,
            "response_sha256": self.response_sha256,
            "response_head_hex": self.response_head_hex,
            "requested": requested,
        }
        if self.selection is not None:
            payload["capture_selection"] = self.selection.to_dict()
        return payload


def _refresh_action_hint(selection: CaptureSelection | None = None) -> str:
    target = ""
    if selection is not None:
        req = selection.to_dict()["requested"]
        parts = [part for part in (req.get("platform_build"), req.get("configuration")) if part]
        target = f" for {' / '.join(parts)}" if parts else ""
    return (
        "Manager handshake moved or the selected capture is not compatible; "
        f"refresh the protocol capture{target} using docs/capture-refresh-runbook.md."
    )


def classify_manager_handshake_response(
    response: bytes,
    *,
    selection: CaptureSelection | None = None,
    requested_platform_build: str | None = None,
    requested_configuration: str | None = None,
    frame_index: int = 3,
) -> ManagerHandshakePreflightResult:
    try:
        ack_guid = extract_client_ack_guid(response)
    except ValueError as exc:
        return ManagerHandshakePreflightResult(
            ok=False,
            frame_index=frame_index,
            error=MANAGER_HANDSHAKE_MOVED,
            detail=str(exc),
            action_hint=_refresh_action_hint(selection),
            response_byte_count=len(response),
            response_sha256=sha256_hex(response) if response else "",
            response_head_hex=preview_hex(response),
            selection=selection,
            requested_platform_build=requested_platform_build,
            requested_configuration=requested_configuration,
        )
    return ManagerHandshakePreflightResult(
        ok=True,
        frame_index=frame_index,
        ack_guid=ack_guid,
        response_byte_count=len(response),
        response_sha256=sha256_hex(response) if response else "",
        response_head_hex=preview_hex(response),
        selection=selection,
        requested_platform_build=requested_platform_build,
        requested_configuration=requested_configuration,
    )


def is_manager_handshake_drift_error(exc: BaseException) -> bool:
    current: BaseException | None = exc
    while current is not None:
        if ACK_MISSING_DETAIL in str(current) or MANAGER_HANDSHAKE_MOVED in str(current):
            return True
        current = current.__cause__ or current.__context__
    return False


def manager_handshake_drift_diagnostic(
    exc: BaseException,
    *,
    selection: CaptureSelection | None = None,
    requested_platform_build: str | None = None,
    requested_configuration: str | None = None,
) -> dict[str, Any]:
    return ManagerHandshakePreflightResult(
        ok=False,
        error=MANAGER_HANDSHAKE_MOVED,
        detail=f"{type(exc).__name__}: {exc}",
        action_hint=_refresh_action_hint(selection),
        selection=selection,
        requested_platform_build=requested_platform_build,
        requested_configuration=requested_configuration,
    ).to_dict()
