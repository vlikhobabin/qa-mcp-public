"""Offline PE and provenance validation with synthetic files; no Windows process."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "release" / "windows_host_agent_artifact.py"

def _load_tool():
    spec = importlib.util.spec_from_file_location("windows_host_agent_artifact", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_pe_inspection_rejects_malformed_and_missing_capability_markers(tmp_path: Path) -> None:
    tool = _load_tool()
    malformed = tmp_path / "malformed.exe"
    malformed.write_bytes(b"not-a-pe")

    with pytest.raises(tool.ArtifactError, match="DOS header"):
        tool.inspect_pe(malformed)

    valid_shape = tmp_path / "shape-only.exe"
    payload = bytearray(512)
    payload[:2] = b"MZ"
    payload[0x3C:0x40] = (0x80).to_bytes(4, "little")
    payload[0x80:0x84] = b"PE\0\0"
    payload[0x84:0x86] = (0x8664).to_bytes(2, "little")
    payload[0x94:0x96] = (0xF0).to_bytes(2, "little")
    payload[0x98:0x9A] = (0x20B).to_bytes(2, "little")
    payload[0x98 + 68 : 0x98 + 70] = (2).to_bytes(2, "little")
    valid_shape.write_bytes(payload)

    assert tool.inspect_pe(valid_shape) == {
        "machine": "amd64",
        "machine_code": "0x8664",
        "optional_header": "PE32+",
        "subsystem": "windows_gui",
        "subsystem_code": 2,
    }
    with pytest.raises(tool.ArtifactError, match="required capability markers"):
        tool.verify_required_markers(valid_shape, agent_version="test-version")


def test_source_state_refuses_dirty_host_inputs_without_explicit_opt_in(tmp_path: Path) -> None:
    tool = _load_tool()

    with pytest.raises(tool.ArtifactError, match="dirty host-agent build inputs"):
        tool.require_clean_source([" M main.go"], allow_dirty=False)

    tool.require_clean_source([" M main.go"], allow_dirty=True)


def test_vcs_validation_requires_exact_revision_and_modified_state() -> None:
    tool = _load_tool()
    source = {"git_revision": "a" * 40, "git_dirty": False}

    with pytest.raises(tool.ArtifactError, match="VCS revision metadata is missing"):
        tool._validate_vcs({"go_build": {"settings": {}}}, source)
    with pytest.raises(tool.ArtifactError, match="VCS modified metadata is missing"):
        tool._validate_vcs(
            {"go_build": {"settings": {"vcs.revision": source["git_revision"]}}},
            source,
        )
    with pytest.raises(tool.ArtifactError, match="VCS modified state mismatch"):
        tool._validate_vcs(
            {
                "go_build": {
                    "settings": {
                        "vcs.revision": source["git_revision"],
                        "vcs.modified": "true",
                    }
                }
            },
            source,
        )
