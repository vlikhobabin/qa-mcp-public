from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "release" / "windows_host_agent_artifact.py"
LAUNCHER = ROOT / "bin" / "ai-build-windows-host-agent"


def test_windows_host_agent_builder_has_standalone_cli_contract() -> None:
    assert TOOL.is_file()
    assert LAUNCHER.is_file()

    completed = subprocess.run(
        [str(LAUNCHER), "--help"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert completed.returncode == 0
    assert "build" in completed.stdout
    assert "verify" in completed.stdout


@pytest.mark.slow
def test_two_fixed_setting_builds_are_byte_identical_and_verify(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    for output in (first, second):
        completed = subprocess.run(
            [str(LAUNCHER), "build", "--output-dir", str(output), "--allow-dirty"],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        assert completed.returncode == 0, completed.stderr

    first_manifest = json.loads((first / "qa-mcp-host-agent.manifest.json").read_text(encoding="utf-8"))
    second_manifest = json.loads((second / "qa-mcp-host-agent.manifest.json").read_text(encoding="utf-8"))
    assert first_manifest["artifact"]["sha256"] == second_manifest["artifact"]["sha256"]
    assert (first / "qa-mcp-host-agent.exe").read_bytes() == (second / "qa-mcp-host-agent.exe").read_bytes()

    verified = subprocess.run(
        [str(LAUNCHER), "verify", "--bundle-dir", str(first), "--allow-dirty"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert verified.returncode == 0, verified.stderr
    assert "verified" in verified.stdout
