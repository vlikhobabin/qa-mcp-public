from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "release" / "component_manifest.py"
spec = importlib.util.spec_from_file_location("component_manifest", MODULE_PATH)
assert spec and spec.loader
component_manifest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(component_manifest)


def _write(path: Path, data: bytes) -> Path:
    path.write_bytes(data)
    return path


def _inventory(path: Path) -> Path:
    payload = {"schema": "qa-mcp.open-package-inventory.v1", "source_commit": "a" * 40, "files": {"mcp_server.py": {"kind": "python-source", "sha256": "b" * 64, "size": 1}}}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_build_manifest_records_plaintext_runtime_assets(tmp_path: Path) -> None:
    image = _write(tmp_path / "qa-mcp-thin-v0.2.3.tar.zst", b"image-archive")
    bootstrap = _write(tmp_path / "bootstrap.ps1", b"bootstrap")
    inventory = _inventory(tmp_path / "open-package-inventory.json")

    manifest = component_manifest.build_manifest(
        version="v0.2.3",
        git_commit="abc123",
        image_tag="qa-mcp-thin:v0.2.3",
        image_asset=image,
        package_inventory=inventory,
        assets={"bootstrap.ps1": bootstrap},
        created_at="2026-07-03T10:00:00Z",
    )

    assert manifest["schema"] == "ai1c.component-release.manifest.v1"
    assert manifest["component"] == "qa-mcp"
    assert manifest["image"]["sha256"] == hashlib.sha256(b"image-archive").hexdigest()
    assert manifest["assets"]["bootstrap.ps1"]["sha256"] == hashlib.sha256(b"bootstrap").hexdigest()
    assert manifest["data_assets"] == []
    assert manifest["runtime_assets"] == {
        "path": "qa_mcp/_bundled",
        "representation": "plaintext-package-data",
        "included_in_image": True,
        "separate_data_asset": False,
        "verification": "docker/verify_open_image.py",
        "inventory": json.loads(inventory.read_text(encoding="utf-8")),
    }
    assert "protected_bundled_data" not in json.dumps(manifest)


def test_cli_writes_manifest(tmp_path: Path) -> None:
    image = _write(tmp_path / "qa-mcp-thin-v0.2.3.tar", b"image")
    exe = _write(tmp_path / "qa-mcp-host-agent.exe", b"exe")
    com_worker = _write(tmp_path / "ai-com-worker.exe", b"com-worker")
    output = tmp_path / "manifest.json"
    inventory = _inventory(tmp_path / "open-package-inventory.json")

    completed = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--version",
            "v0.2.3",
            "--git-commit",
            "abc123",
            "--image-tag",
            "qa-mcp-thin:v0.2.3",
            "--image-asset",
            str(image),
            "--package-inventory",
            str(inventory),
            "--asset",
            f"qa-mcp-host-agent.exe={exe}",
            "--asset",
            f"ai-com-worker.exe={com_worker}",
            "--created-at",
            "2026-07-03T10:00:00Z",
            "--output",
            str(output),
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert str(output) in completed.stdout
    manifest = json.loads(output.read_text(encoding="utf-8"))
    assert manifest["image"]["asset"] == "qa-mcp-thin-v0.2.3.tar"
    assert "qa-mcp-host-agent.exe" in manifest["assets"]
    assert manifest["assets"]["ai-com-worker.exe"]["sha256"] == hashlib.sha256(b"com-worker").hexdigest()
    assert manifest["assets"]["ai-com-worker.exe"]["size"] == len(b"com-worker")
