from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import tarfile
from pathlib import Path

from tests.support.archives import tar_bytes as _tar_bytes


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "docker" / "verify_open_image.py"
spec = importlib.util.spec_from_file_location("verify_open_image", MODULE_PATH)
assert spec and spec.loader
verify_open_image = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_open_image)
SOURCE_COMMIT = "a" * 40


def _write_archive(path: Path, entries: dict[str, bytes], history: str = "COPY source package") -> Path:
    layer = _tar_bytes(entries)
    manifest = json.dumps(
        [{"Config": "config.json", "RepoTags": ["qa-mcp:test"], "Layers": ["layer.tar"]}]
    ).encode()
    config = json.dumps(
        {
            "config": {"Labels": {"org.opencontainers.image.revision": SOURCE_COMMIT}},
            "history": [{"created_by": history}],
        }
    ).encode()
    with tarfile.open(path, mode="w") as archive:
        for name, data in {"manifest.json": manifest, "config.json": config, "layer.tar": layer}.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
    return path


def _component_manifest(path: Path, entries: dict[str, bytes], *, tag: str = "qa-mcp:test") -> Path:
    prefix = "usr/local/lib/python3.12/site-packages/qa_mcp/"
    payloads = {name.removeprefix(prefix): data for name, data in entries.items() if name.startswith(prefix)}
    inventory, errors = verify_open_image.make_inventory(payloads, SOURCE_COMMIT)
    assert errors == []
    manifest = {
        "git_commit": SOURCE_COMMIT,
        "image": {"tag": tag, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()},
        "runtime_assets": {"inventory": inventory},
    }
    target = path.with_suffix(".manifest.json")
    target.write_text(json.dumps(manifest), encoding="utf-8")
    return target


def _valid_entries() -> dict[str, bytes]:
    prefix = "usr/local/lib/python3.12/site-packages/qa_mcp"
    return {
        f"{prefix}/mcp_server.py": b"def main(): pass\n",
        f"{prefix}/protocol/bootstrap.py": b"class CaptureBootstrap: pass\n",
        f"{prefix}/protocol/templates.py": b"class ProtocolTemplates: pass\n",
        f"{prefix}/_bundled/8.3/accepted_mappings.json": b'{"cases": []}',
        f"{prefix}/_bundled/8.3/templates/value.json": b'{"templates": []}',
        f"{prefix}/_bundled/8.3/captures/read/traffic.jsonl": b'{"event": "chunk"}\n',
        f"{prefix}/schemas/qa-mcp-runtime-target-profile.schema.json": b'{"type": "object"}',
    }


def test_archive_scanner_accepts_readable_source_and_plaintext_assets(tmp_path: Path) -> None:
    entries = _valid_entries()
    archive = _write_archive(tmp_path / "open.tar", entries)
    assert verify_open_image.scan_saved_archive(archive, _component_manifest(archive, entries)) == []


def test_archive_scanner_rejects_missing_source_and_encrypted_assets(tmp_path: Path) -> None:
    entries = _valid_entries()
    entries.pop(next(path for path in entries if path.endswith("mcp_server.py")))
    capture = next(path for path in entries if path.endswith("traffic.jsonl"))
    entries[capture] = b"QAMCPENC1\x00ciphertext"
    archive = _write_archive(tmp_path / "closed.tar", entries)

    errors = verify_open_image.scan_saved_archive(archive, _component_manifest(archive, _valid_entries()))

    assert any("missing declared package artifact" in error for error in errors)
    assert any("hash mismatch" in error for error in errors)


def test_archive_scanner_rejects_protection_inputs_in_history(tmp_path: Path) -> None:
    archive = _write_archive(
        tmp_path / "secret-history.tar",
        _valid_entries(),
        history="ARG BUNDLED_DATA_KEY=secret",
    )
    errors = verify_open_image.scan_saved_archive(archive, _component_manifest(archive, _valid_entries()))
    assert any("retired protection input" in error for error in errors)


def test_archive_scanner_requires_manifest_and_rejects_undeclared_private_artifacts(tmp_path: Path) -> None:
    entries = _valid_entries()
    entries["run/secrets/private-signing-key"] = b"private"
    entries["usr/local/lib/python3.12/site-packages/qa_mcp/private.key"] = b"private"
    archive = _write_archive(tmp_path / "private.tar", entries)
    manifest = _component_manifest(archive, _valid_entries())

    assert verify_open_image.scan_saved_archive(archive) == [
        "component manifest is required for saved-image verification"
    ]
    errors = verify_open_image.scan_saved_archive(archive, manifest)
    assert any("undeclared package artifact" in error for error in errors)
    assert any("undeclared private image artifact" in error for error in errors)


def test_archive_scanner_rejects_component_image_or_source_identity_mismatch(tmp_path: Path) -> None:
    entries = _valid_entries()
    archive = _write_archive(tmp_path / "identity.tar", entries)
    manifest = _component_manifest(archive, entries, tag="qa-mcp:wrong")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["git_commit"] = "b" * 40
    manifest.write_text(json.dumps(data), encoding="utf-8")

    errors = verify_open_image.scan_saved_archive(archive, manifest)
    assert any("source revision mismatch" in error for error in errors)
    assert any("image tag mismatch" in error for error in errors)
