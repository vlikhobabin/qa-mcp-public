from pathlib import Path

import pytest

from qa_mcp import mcp_server


ROOT = Path(__file__).resolve().parents[1]


def test_model_a_compose_defaults_to_loopback_without_unsafe_bind() -> None:
    compose = (ROOT / "docker" / "docker-compose.yml").read_text(encoding="utf-8")

    assert "network_mode: host" in compose
    assert 'QA_MCP_HTTP_HOST: "${QA_MCP_HTTP_HOST:-127.0.0.1}"' in compose
    assert "QA_MCP_HTTP_ALLOW_UNSAFE_BIND" not in compose


def test_http_bind_rejects_non_loopback_without_bearer_token() -> None:
    with pytest.raises(ValueError, match="QA_MCP_BEARER_TOKEN"):
        mcp_server._resolve_http_bind({"QA_MCP_HTTP_HOST": "192.168.0.10"})


def test_http_bind_allows_non_loopback_with_bearer_token() -> None:
    assert mcp_server._resolve_http_bind({
        "QA_MCP_HTTP_HOST": "192.168.0.10",
        "QA_MCP_BEARER_TOKEN": "secret",
    }) == ("192.168.0.10", 8000)
