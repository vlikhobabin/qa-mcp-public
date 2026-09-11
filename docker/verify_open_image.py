#!/usr/bin/env python3
"""Verify exact source/package inventory and component identity for open images."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import io
import json
import re
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any
INVENTORY_SCHEMA = "qa-mcp.open-package-inventory.v1"
REQUIRED_MODULES = ("mcp_server.py", "protocol/bootstrap.py", "protocol/templates.py")
ASSET_PATTERNS = (
    "_bundled/*/accepted_mappings.json",
    "_bundled/*/templates/*.json",
    "_bundled/*/captures/*/traffic.jsonl",
    "protocol/*.json",
    "protocol/assets/*.png",
    "schemas/*.json",
)
SOURCE_ONLY_PATTERNS = ("_bundled/*/README.md", "_bundled/*/captures/*/capture-metadata.json")
RETIRED_HISTORY_TOKENS = ("bundled" + "_data_key", "nuit" + "ka", "protected" + "-package")
ENCRYPTED_ASSET_MAGIC = b"QAMCP" + b"ENC1\x00"
SOURCE_REVISION = re.compile(r"^[0-9a-f]{40}$")
PRIVATE_SUFFIXES = (".key", ".pfx", ".p12")
def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
def file_kind(relative: str) -> str | None:
    if relative.endswith(".py"):
        return "python-source"
    if any(fnmatch.fnmatchcase(relative, pattern) for pattern in ASSET_PATTERNS):
        return "runtime-asset"
    return None
def make_inventory(payloads: dict[str, bytes], source_commit: str) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    if not SOURCE_REVISION.fullmatch(source_commit):
        errors.append("source commit must be a full lowercase Git SHA")
    files: dict[str, Any] = {}
    for relative, payload in sorted(payloads.items()):
        if any(fnmatch.fnmatchcase(relative, pattern) for pattern in SOURCE_ONLY_PATTERNS):
            continue
        kind = file_kind(relative)
        if kind is None:
            errors.append(f"undeclared package artifact: {relative}")
            continue
        files[relative] = {
            "kind": kind,
            "sha256": sha256_bytes(payload),
            "size": len(payload),
            "provenance": f"git:{source_commit}:src/qa_mcp/{relative}",
        }
    return {"schema": INVENTORY_SCHEMA, "source_commit": source_commit, "files": files}, errors
def source_payloads(package_root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(package_root).as_posix(): path.read_bytes()
        for path in package_root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
def validate_payloads(payloads: dict[str, bytes], inventory: dict[str, Any]) -> list[str]:
    expected = inventory.get("files")
    source_commit = inventory.get("source_commit")
    if inventory.get("schema") != INVENTORY_SCHEMA or not SOURCE_REVISION.fullmatch(
        source_commit or ""
    ) or not isinstance(expected, dict):
        return ["invalid open-package inventory"]
    errors: list[str] = []
    actual = set(payloads)
    declared = set(expected)
    for relative in sorted(declared - actual):
        errors.append(f"missing declared package artifact: {relative}")
    for relative in sorted(actual - declared):
        errors.append(f"undeclared package artifact: {relative}")
    for relative in sorted(actual & declared):
        entry = expected[relative]
        if not isinstance(entry, dict) or entry.get("sha256") != sha256_bytes(payloads[relative]):
            errors.append(f"package artifact hash mismatch: {relative}")
            continue
        if entry.get("size") != len(payloads[relative]) or entry.get("kind") != file_kind(relative):
            errors.append(f"package artifact metadata mismatch: {relative}")
        if entry.get("provenance") != f"git:{source_commit}:src/qa_mcp/{relative}":
            errors.append(f"package artifact provenance mismatch: {relative}")
        if entry.get("kind") == "runtime-asset":
            validate_asset(relative, payloads[relative], errors)
    for relative in REQUIRED_MODULES:
        if relative not in declared:
            errors.append(f"missing readable module declaration: {relative}")
    return errors
def validate_asset(path: str, payload: bytes, errors: list[str]) -> None:
    if payload.startswith(ENCRYPTED_ASSET_MAGIC):
        errors.append(f"encrypted bundled asset: {path}")
        return
    try:
        if path.endswith(".png"):
            if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError("invalid PNG signature")
        else:
            text = payload.decode("utf-8-sig")
            values = text.splitlines() if path.endswith(".jsonl") else (text,)
            for value in values:
                if value.strip():
                    json.loads(value)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"unreadable runtime asset {path}: {exc}")
def outer_member(archive: tarfile.TarFile, name: str) -> bytes:
    stream = archive.extractfile(name)
    if stream is None:
        raise ValueError(f"Docker archive member is not a file: {name}")
    return stream.read()
def apply_layer(files: dict[str, bytes], payload: bytes) -> None:
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:*") as layer:
        for member in layer:
            name = member.name.removeprefix("./").lstrip("/")
            path = PurePosixPath(name)
            if path.name == ".wh..wh..opq":
                prefix = "" if str(path.parent) == "." else f"{path.parent}/"
                for existing in tuple(files):
                    if existing.startswith(prefix):
                        files.pop(existing, None)
            elif path.name.startswith(".wh."):
                removed = str(path.with_name(path.name[4:]))
                for existing in tuple(files):
                    if existing == removed or existing.startswith(f"{removed}/"):
                        files.pop(existing, None)
            elif member.isfile() and (stream := layer.extractfile(member)) is not None:
                files[name] = stream.read()
def package_payloads(files: dict[str, bytes]) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    marker = "/site-packages/qa_mcp/"
    for name, payload in files.items():
        normalized = f"/{name}"
        if marker in normalized:
            result[normalized.split(marker, 1)[1]] = payload
    return result
def scan_saved_archive(path: Path | str, component_manifest: Path | str | None = None) -> list[str]:
    if component_manifest is None:
        return ["component manifest is required for saved-image verification"]
    archive_path = Path(path)
    try:
        component = json.loads(Path(component_manifest).read_text(encoding="utf-8"))
        inventory = component["runtime_assets"]["inventory"]
        if component.get("image", {}).get("sha256") != sha256_file(archive_path):
            return ["component manifest image SHA-256 mismatch"]
        files: dict[str, bytes] = {}
        with tarfile.open(archive_path, mode="r:*") as archive:
            docker_manifest = json.loads(outer_member(archive, "manifest.json"))
            if not isinstance(docker_manifest, list) or len(docker_manifest) != 1:
                return ["Docker archive must contain exactly one image manifest"]
            entry = docker_manifest[0]
            config = json.loads(outer_member(archive, entry["Config"]))
            for layer_name in entry.get("Layers") or []:
                apply_layer(files, outer_member(archive, layer_name))
        errors = validate_payloads(package_payloads(files), inventory)
        revision = (config.get("config", {}).get("Labels") or {}).get("org.opencontainers.image.revision")
        if revision != inventory.get("source_commit") or revision != component.get("git_commit"):
            errors.append("source revision mismatch across image, inventory and component manifest")
        if component.get("image", {}).get("tag") not in (entry.get("RepoTags") or []):
            errors.append("component manifest image tag mismatch")
        config_text = json.dumps(config, sort_keys=True).lower()
        for token in RETIRED_HISTORY_TOKENS:
            if token in config_text:
                errors.append(f"retired protection input in image config/history: {token}")
        sensitive = sorted(name for name, payload in files.items()
            if "/run/secrets/" in f"/{name}" or "/.ssh/" in f"/{name}"
            or PurePosixPath(name).suffix.lower() in PRIVATE_SUFFIXES
            or (not name.endswith(".py") and payload.lstrip().startswith(
                (b"-----BEGIN PRIVATE KEY-----", b"-----BEGIN OPENSSH PRIVATE KEY-----"))))
        if sensitive:
            errors.append(f"undeclared private image artifact: {sensitive[0]}")
        return errors
    except (KeyError, OSError, tarfile.TarError, ValueError, json.JSONDecodeError) as exc:
        return [f"cannot inspect Docker archive and component manifest: {exc}"]
def verify_installed_package(inventory_path: Path) -> list[str]:
    import qa_mcp

    package = Path(qa_mcp.__file__).resolve().parent
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    return validate_payloads(source_payloads(package), inventory)
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--component-manifest", type=Path)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--package-root", type=Path)
    parser.add_argument("--source-commit", default="")
    parser.add_argument("--write-inventory", type=Path)
    args = parser.parse_args()
    if args.write_inventory:
        inventory, errors = make_inventory(source_payloads(args.package_root), args.source_commit)
        if not errors:
            args.write_inventory.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif args.archive:
        errors = scan_saved_archive(args.archive, args.component_manifest)
    elif args.inventory:
        errors = verify_installed_package(args.inventory)
    else:
        errors = ["choose --write-inventory, --archive, or --inventory"]
    if errors:
        print("open-image verification FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("open-image verification OK: exact source and runtime-asset inventory matched")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
