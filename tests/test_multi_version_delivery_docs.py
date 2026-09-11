"""Focused contract checks for the active multi-version delivery guidance."""

from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_DELIVERY_DOCS = (
    "delivery/README.md",
    "delivery/windows-agent-runbook.md",
    "docker/README.md",
    "docs/self-hosted-release-delivery-plan.md",
)


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_active_delivery_urls_use_canonical_mcp_path() -> None:
    stale: list[str] = []
    for relative_path in ACTIVE_DELIVERY_DOCS:
        for line_number, line in enumerate(_read(relative_path).splitlines(), start=1):
            if re.search(r"https?://\S+/mcp/", line):
                stale.append(f"{relative_path}:{line_number}")

    assert stale == [], f"trailing-slash MCP URLs remain in active docs: {stale}"


def test_docker_guidance_names_capture_baselines_and_runtime_configuration() -> None:
    guidance = _read("docker/README.md")

    # Explicit baseline manifests, not a glob over bundles: a bundle's presence
    # does not qualify another build for live support. This only checks docs.
    for manifest_path in (
        "config/protocol-capture-manifest-8.3.json",
        "config/protocol-capture-manifest-8.5.json",
    ):
        version = json.loads(_read(manifest_path))["platform_version"]
        assert version in guidance, f"Docker guidance omits baseline {version} from {manifest_path}"
    assert "QA_MCP_PLATFORM_VERSION" in guidance
    assert "PLATFORM_ROOT" in guidance
    assert "_bundled/8.5" in guidance
