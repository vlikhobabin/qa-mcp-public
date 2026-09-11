from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from qa_mcp.protocol import display_backend


ROOT = Path(__file__).resolve().parents[1]


class StubBridge(display_backend.RemoteAgentBackend):
    response: dict[str, Any]

    def _json(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        assert (method, path) == ("GET", "/v1/capabilities")
        return dict(self.response)


def _bridge(response: dict[str, Any]) -> StubBridge:
    bridge = StubBridge(address="bridge.invalid", token="token")
    bridge.response = response
    return bridge


def _compatible_response() -> dict[str, Any]:
    return {
        "ok": True,
        "api": display_backend.HOST_BRIDGE_API,
        "api_major": display_backend.HOST_BRIDGE_API_MAJOR,
        "version": display_backend.HOST_AGENT_VERSION,
        "sha256": "a" * 64,
        "capabilities": sorted(display_backend.HOST_BRIDGE_REQUIRED_CAPABILITIES),
    }


def test_supported_standalone_handshake_is_accepted() -> None:
    result = _bridge(_compatible_response()).handshake()
    assert result["api_major"] == display_backend.HOST_BRIDGE_API_MAJOR
    assert set(result["capabilities"]) == display_backend.HOST_BRIDGE_REQUIRED_CAPABILITIES


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        ({"api_major": 2}, "host-agent-api-major-incompatible"),
        ({"api_major": True}, "host-agent-capability-document-invalid"),
        ({"api_major": 1.0}, "host-agent-capability-document-invalid"),
        ({"api_major": "1"}, "host-agent-capability-document-invalid"),
        ({"api_major": None}, "host-agent-capability-document-invalid"),
        ({"capabilities": ["health"]}, "host-agent-capability-missing"),
    ],
)
def test_standalone_handshake_fails_closed(
    mutation: dict[str, Any], code: str
) -> None:
    response = _compatible_response()
    response.update(mutation)
    with pytest.raises(display_backend.DisplayBackendError) as raised:
        _bridge(response).handshake()
    assert raised.value.code == code


def test_installer_contains_only_standalone_inputs() -> None:
    script = (ROOT / "host-agent" / "install-windows-host-agent.ps1").read_text(
        encoding="utf-8-sig"
    )
    for forbidden in (
        "AgentCli",
        "BslAgent",
        "ComWorker",
        "Onboarding",
        "Registry",
    ):
        assert forbidden not in script
    assert "TestClientRelayAddress" in script
    assert "TokenFile" in script
