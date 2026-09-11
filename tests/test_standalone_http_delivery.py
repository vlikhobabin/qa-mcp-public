from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_BASE = (
    "ghcr.io/astral-sh/uv:0.11.14-python3.12-trixie-slim"
    "@sha256:13b5883729ec534af5863facf5c40ac0869f2c124ad5620c9ed36fe7c03fa87d"
)


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_standalone_dockerfile_uses_public_pinned_direct_runtime() -> None:
    dockerfile = _text("docker/Dockerfile.thin")

    assert f"ARG PUBLIC_BASE_IMAGE={PUBLIC_BASE}\nFROM ${{PUBLIC_BASE_IMAGE}}" in dockerfile
    assert 'org.opencontainers.image.source="https://github.com/vlikhobabin/qa-mcp"' in dockerfile
    assert 'QA_MCP_TRANSPORT="streamable-http"' in dockerfile
    assert 'QA_MCP_HTTP_HOST="0.0.0.0"' in dockerfile
    assert 'CMD ["qa-native-mcp"]' in dockerfile
    assert "USER qa-mcp" in dockerfile
    assert "verify_open_image.py" in dockerfile
    assert "ai-suite-base" not in dockerfile
    assert "ai-mcp-proxy" not in dockerfile


def test_compose_and_bootstrap_use_project_bearer_and_loopback_publish() -> None:
    compose = _text("docker/docker-compose.thin.yml")
    bootstrap = _text("delivery/bootstrap.ps1")
    native_dockerfile = _text("Dockerfile")

    assert '"127.0.0.1:8000:8080"' in compose
    assert 'QA_MCP_BEARER_TOKEN: "${QA_MCP_BEARER_TOKEN:?' in compose
    assert "-e QA_MCP_BEARER_TOKEN=$McpToken" in bootstrap
    assert "--entrypoint sh" not in bootstrap
    assert "ai-mcp-proxy" not in compose + bootstrap
    assert "AI1C_MCP_PROXY_HTTP_TOKEN" not in compose + bootstrap
    assert "QA_MCP_HTTP_ALLOW_UNSAFE_BIND" not in native_dockerfile
    assert "QA_MCP_BEARER_TOKEN" in native_dockerfile


def test_release_paths_validate_same_public_base_and_keep_inventory_gate() -> None:
    workflow = _text(".github/workflows/release.yml")
    publisher = _text("tools/release/publish_self_hosted.sh")

    for payload in (workflow, publisher):
        assert PUBLIC_BASE in payload
        assert "PUBLIC_BASE_IMAGE" in payload
        assert "verify_open_image.py" in payload
        assert "open-package-inventory.json" in payload
        assert "SUITE_BASE_IMAGE" not in payload
        assert not re.search(r"(?:ai-suite-base|ai-mcp-proxy)", payload)


def test_release_paths_run_the_direct_authenticated_image_smoke() -> None:
    workflow = _text(".github/workflows/release.yml")
    publisher = _text("tools/release/publish_self_hosted.sh")
    smoke = _text("tools/release/smoke_standalone_image.py")

    assert "smoke_standalone_image.py" in workflow
    assert "smoke_standalone_image.py" in publisher
    assert "qa-mcp.owned=standalone-smoke" in smoke
    assert '"unauthorized": unauthorized == 401' in smoke
    assert '"authorized_initialize": authorized == 200' in smoke
    assert '"non_root": bool(user' in smoke
    assert 'docker("rm", "-f", args.name, check=False)' in smoke
