from __future__ import annotations

import subprocess
from typing import Any

import pytest

from qa_mcp import mcp_server


def test_main_ignores_legacy_product_license_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_calls: list[dict[str, Any]] = []
    factory_calls: list[dict[str, Any]] = []

    def unexpected_subprocess(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("qa-mcp startup must not launch a product-license broker")

    monkeypatch.setenv("QA_MCP_TRANSPORT", "stdio")
    monkeypatch.setenv("QA_MCP_LICENSE_GATE", "1")
    monkeypatch.setenv("QA_MCP_LICENSE_BROKER", "/missing/ai1c-license")
    monkeypatch.setenv("QA_MCP_LICENSE_TIMEOUT", "not-a-number")
    monkeypatch.setattr(subprocess, "run", unexpected_subprocess)
    class ComposedServer:
        def run(self, **kwargs: Any) -> None:
            run_calls.append(kwargs)

    def fake_factory(**kwargs: Any) -> ComposedServer:
        factory_calls.append(kwargs)
        return ComposedServer()

    monkeypatch.setattr(mcp_server, "create_mcp_server", fake_factory)

    mcp_server.main()

    assert run_calls == [{"show_banner": False}]
    assert factory_calls[0]["tool_profile"] == "standalone"
    assert factory_calls[0]["settings"].http_transport == "stdio"
