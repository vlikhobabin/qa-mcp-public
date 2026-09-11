"""Static bootstrap declarations and wiring; these do not execute Windows selection."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_script() -> str:
    return (ROOT / "delivery" / "bootstrap.ps1").read_text(encoding="utf-8-sig")


def _direct_capture_families(script: str) -> set[str]:
    match = re.search(r"\$DirectCaptureFamilies\s*=\s*@\((?P<body>[^)]*)\)", script)
    assert match, "bootstrap.ps1 must declare direct capture families"
    return set(re.findall(r'"([^"]+)"', match.group("body")))


def _protocol_data_fallbacks(script: str) -> dict[str, str]:
    match = re.search(r"\$ProtocolDataFallbacks\s*=\s*@\{(?P<body>[^}]*)\}", script)
    assert match, "bootstrap.ps1 must declare protocol-data fallbacks"
    return dict(re.findall(r'"([^"]+)"\s*=\s*"([^"]+)"', match.group("body")))


def test_bootstrap_declares_only_capture_backed_8_3_as_direct_family() -> None:
    # Independent policy expectation: 8.5 currently reuses the 8.3 capture set.
    assert _direct_capture_families(_bootstrap_script()) == {"8.3"}


def test_bootstrap_source_wires_typed_version_sort_and_direct_capture_preference() -> None:
    script = _bootstrap_script()

    assert "Sort-Object Version -Descending" in script
    assert "[version]$VersionText" in script
    assert "Sort-Object FullName" not in script
    assert "$cand = $candidates | Where-Object { $_.DirectCapture } | Select-Object -First 1" in script
    assert "if (-not $cand) { $cand = $candidates | Select-Object -First 1 }" in script


def test_bootstrap_source_declares_fallback_and_wires_live_version_argument() -> None:
    script = _bootstrap_script()
    fallbacks = _protocol_data_fallbacks(script)

    assert fallbacks["8.5"] == "8.3"
    assert "protocol-data fallback" in script
    assert "-PlatformExe" in script
    assert "-e QA_MCP_PLATFORM_VERSION=$PlatformVersion" in script
