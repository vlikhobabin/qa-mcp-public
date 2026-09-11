from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "qa_mcp"


def test_runtime_source_and_curated_assets_are_readable_plaintext() -> None:
    expected_modules = (
        PACKAGE / "mcp_server.py",
        PACKAGE / "protocol" / "bootstrap.py",
        PACKAGE / "protocol" / "templates.py",
    )
    assert all(path.is_file() for path in expected_modules)
    assert not (PACKAGE / "protocol" / "_bundled_crypto.py").exists()

    schema = PACKAGE / "schemas" / "qa-mcp-runtime-target-profile.schema.json"
    assert schema.is_file()
    assert json.loads(schema.read_text(encoding="utf-8"))["additionalProperties"] is False

    assets = sorted((PACKAGE / "_bundled").glob("*/accepted_mappings.json"))
    assets += sorted((PACKAGE / "_bundled").glob("*/templates/*.json"))
    assets += sorted((PACKAGE / "_bundled").glob("*/captures/*/traffic.jsonl"))
    assert assets
    for path in assets:
        raw = path.read_bytes()
        assert not raw.startswith(b"QAMCPENC1\x00")
        text = raw.decode("utf-8-sig")
        if path.suffix == ".jsonl":
            for line in text.splitlines():
                if line.strip():
                    json.loads(line)
        else:
            json.loads(text)


def test_clean_wheel_contains_readable_modules_and_plaintext_assets(tmp_path: Path) -> None:
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    shutil.copy2(ROOT / "pyproject.toml", checkout / "pyproject.toml")
    shutil.copy2(ROOT / "README.md", checkout / "README.md")
    shutil.copytree(
        ROOT / "src",
        checkout / "src",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.egg-info"),
    )
    output = tmp_path / "dist"
    completed = subprocess.run(
        ["uv", "build", "--wheel", "--sdist", "--out-dir", str(output)],
        cwd=checkout,
        check=False,
        text=True,
        capture_output=True,
    )
    assert completed.returncode == 0, completed.stderr
    wheel = next(output.glob("qa_mcp-*.whl"))
    schema_relative = "schemas/qa-mcp-runtime-target-profile.schema.json"
    expected_schema = (PACKAGE / schema_relative).read_bytes()
    expected_assets = {
        path.relative_to(PACKAGE).as_posix(): path.read_bytes()
        for path in (PACKAGE / "_bundled").rglob("*")
        if path.is_file()
        and (
            path.name == "accepted_mappings.json"
            or (path.parent.name == "templates" and path.suffix == ".json")
            or (path.name == "traffic.jsonl" and path.parent.parent.name == "captures")
        )
    }
    assert len(expected_assets) == 16
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        for relative in (
            "qa_mcp/mcp_server.py",
            "qa_mcp/protocol/bootstrap.py",
            "qa_mcp/protocol/templates.py",
            f"qa_mcp/{schema_relative}",
        ):
            assert relative in names
        assert archive.read(f"qa_mcp/{schema_relative}") == expected_schema
        assets = {
            name.removeprefix("qa_mcp/"): archive.read(name)
            for name in names
            if name.startswith("qa_mcp/_bundled/") and name.endswith((".json", ".jsonl"))
        }
        assert assets == expected_assets
        for payload in assets.values():
            assert not payload.startswith(b"QAMCPENC1\x00")
    sdist = next(output.glob("qa_mcp-*.tar.gz"))
    with tarfile.open(sdist) as archive:
        schema_name = next(
            name for name in archive.getnames() if name.endswith(f"/src/qa_mcp/{schema_relative}")
        )
        assert archive.extractfile(schema_name).read() == expected_schema
        assets = {
            name.split("/src/qa_mcp/", 1)[1]: archive.extractfile(name).read()
            for name in archive.getnames()
            if "/src/qa_mcp/_bundled/" in name and name.endswith((".json", ".jsonl"))
        }
    assert assets == expected_assets


def test_production_loaders_use_normal_package_reads() -> None:
    for relative in (
        "protocol/bootstrap.py",
        "protocol/evidence.py",
        "protocol/native_write.py",
        "protocol/templates.py",
    ):
        source = (PACKAGE / relative).read_text(encoding="utf-8")
        assert "_bundled_crypto" not in source
        assert "read_decrypted" not in source


def test_active_delivery_tree_has_no_confidentiality_stack() -> None:
    removed_paths = (
        "docker/compile_modules.sh",
        "docker/compile_protocol.sh",
        "docker/encrypt_bundled.py",
        "docker/strip_source.py",
        "docker/verify_protected_image.py",
        "src/qa_mcp/protocol/_bundled_crypto.py",
        "tests/test_bundled_crypto.py",
        "tests/test_bundled_crypto_runtime_key.py",
        "tests/test_verify_protected_image_archive.py",
    )
    assert not [path for path in removed_paths if (ROOT / path).exists()]

    scanned = [
        ROOT / ".dockerignore",
        ROOT / "pyproject.toml",
        ROOT / ".github" / "workflows" / "release.yml",
        ROOT / "docs" / "self-hosted-release-delivery-plan.md",
    ]
    for directory in ("docker", "delivery", "src", "tools/release"):
        scanned.extend(path for path in (ROOT / directory).rglob("*") if path.is_file())
    prohibited = (
        "BUNDLED_DATA_KEY",
        "BundledDataKey",
        "_bundled_crypto",
        "verify_protected_image",
        "encrypt_bundled.py",
        "strip_source.py",
        "compile_modules.sh",
        "compile_protocol.sh",
        "nuitka",
    )
    violations: list[str] = []
    for path in scanned:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (UnicodeDecodeError, OSError):
            continue
        for token in prohibited:
            if token.lower() in text.lower():
                violations.append(f"{path.relative_to(ROOT)}: {token}")
    assert violations == []


def test_release_manifest_declares_plaintext_runtime_assets(tmp_path: Path) -> None:
    module_path = ROOT / "tools" / "release" / "component_manifest.py"
    spec = importlib.util.spec_from_file_location("component_manifest_open", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    image = tmp_path / "qa-mcp.tar"
    image.write_bytes(b"image")
    bootstrap = tmp_path / "bootstrap.ps1"
    bootstrap.write_bytes(b"bootstrap")
    inventory = tmp_path / "inventory.json"
    inventory.write_text(
        json.dumps({"schema": "qa-mcp.open-package-inventory.v1", "source_commit": "a" * 40, "files": {"mcp_server.py": {"kind": "python-source", "sha256": "b" * 64, "size": 1}}}),
        encoding="utf-8",
    )

    manifest = module.build_manifest(
        version="v1.0.0",
        git_commit="abcdef0",
        image_tag="qa-mcp:v1.0.0",
        image_asset=image,
        package_inventory=inventory,
        assets={"bootstrap.ps1": bootstrap},
        created_at="2026-08-24T00:00:00Z",
    )

    assert "protected_bundled_data" not in manifest
    assert manifest["runtime_assets"] == {
        "path": "qa_mcp/_bundled",
        "representation": "plaintext-package-data",
        "included_in_image": True,
        "separate_data_asset": False,
        "verification": "docker/verify_open_image.py",
        "inventory": json.loads(inventory.read_text(encoding="utf-8")),
    }


def test_standalone_bootstrap_and_renderer_have_no_data_key_contract() -> None:
    for relative in (
        "delivery/bootstrap.ps1",
        "tools/release/render_standalone_bootstrap.py",
        "tools/release/verify_standalone_bootstrap.ps1",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8-sig")
        assert "BUNDLED_DATA_KEY" not in text
        assert "BundledDataKey" not in text
