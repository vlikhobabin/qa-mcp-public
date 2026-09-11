#!/usr/bin/env python3
"""Validate the qa-mcp self-hosted component release manifest."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "ai1c.component-release.manifest.v1"
CHANNEL = "component-self-hosted"
COMPONENT_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
RELEASE_LINK_ID_PATTERN = re.compile(r"^r-[0-9]{8}-[0-9a-f]{16,}$")
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")
    return data


def write(path: str | None, payload: dict[str, Any]) -> None:
    if not path:
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value)


def is_nonnegative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def is_relative_path(value: object) -> bool:
    return is_non_empty_string(value) and not str(value).startswith("/")


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and bool(SHA256_PATTERN.fullmatch(value))


def validate_datetime(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def add_unknown_key_errors(
    errors: list[str],
    path: str,
    value: dict[str, Any],
    allowed: set[str],
) -> None:
    for key in sorted(set(value) - allowed):
        errors.append(f"{path}: additional property is not allowed: {key}")


def validate_hash_size(errors: list[str], path: str, value: object) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path}: must be an object")
        return
    add_unknown_key_errors(errors, path, value, {"sha256", "size"})
    for key in ("sha256", "size"):
        if key not in value:
            errors.append(f"{path}: missing required property: {key}")
    if "sha256" in value and not is_sha256(value["sha256"]):
        errors.append(f"{path}.sha256: must be a lowercase SHA-256 hex digest")
    if "size" in value and not is_nonnegative_int(value["size"]):
        errors.append(f"{path}.size: must be a non-negative integer")


def validate_image(errors: list[str], value: object) -> None:
    path = "image"
    if not isinstance(value, dict):
        errors.append(f"{path}: must be an object")
        return
    allowed = {"type", "tag", "asset", "sha256", "size"}
    add_unknown_key_errors(errors, path, value, allowed)
    for key in sorted(allowed):
        if key not in value:
            errors.append(f"{path}: missing required property: {key}")
    if value.get("type") != "docker-archive":
        errors.append(f"{path}.type: must be docker-archive")
    if "tag" in value and not is_non_empty_string(value["tag"]):
        errors.append(f"{path}.tag: must be a non-empty string")
    if "asset" in value and not is_relative_path(value["asset"]):
        errors.append(f"{path}.asset: must be a relative non-empty path")
    if "sha256" in value and not is_sha256(value["sha256"]):
        errors.append(f"{path}.sha256: must be a lowercase SHA-256 hex digest")
    if "size" in value and not is_nonnegative_int(value["size"]):
        errors.append(f"{path}.size: must be a non-negative integer")


def validate_data_asset(errors: list[str], path: str, value: object) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path}: must be an object")
        return
    allowed = {"asset", "sha256", "size"}
    add_unknown_key_errors(errors, path, value, allowed)
    for key in sorted(allowed):
        if key not in value:
            errors.append(f"{path}: missing required property: {key}")
    if "asset" in value and not is_relative_path(value["asset"]):
        errors.append(f"{path}.asset: must be a relative non-empty path")
    if "sha256" in value and not is_sha256(value["sha256"]):
        errors.append(f"{path}.sha256: must be a lowercase SHA-256 hex digest")
    if "size" in value and not is_nonnegative_int(value["size"]):
        errors.append(f"{path}.size: must be a non-negative integer")


def validate_string_list(errors: list[str], path: str, value: object) -> None:
    if not isinstance(value, list):
        errors.append(f"{path}: must be an array")
        return
    seen: set[str] = set()
    for index, item in enumerate(value):
        item_path = f"{path}.{index}"
        if not is_non_empty_string(item):
            errors.append(f"{item_path}: must be a non-empty string")
            continue
        if item in seen:
            errors.append(f"{item_path}: duplicate item")
        seen.add(item)


def validate_runtime_assets(errors: list[str], value: object) -> None:
    path = "runtime_assets"
    if not isinstance(value, dict):
        errors.append(f"{path}: must be an object")
        return
    allowed = {
        "path",
        "representation",
        "included_in_image",
        "separate_data_asset",
        "verification",
        "inventory",
    }
    add_unknown_key_errors(errors, path, value, allowed)
    for key in sorted(allowed):
        if key not in value:
            errors.append(f"{path}: missing required property: {key}")
    for key in ("included_in_image", "separate_data_asset"):
        if key in value and not isinstance(value[key], bool):
            errors.append(f"{path}.{key}: must be a boolean")
    for key in ("path", "representation", "verification"):
        if key in value and not is_non_empty_string(value[key]):
            errors.append(f"{path}.{key}: must be a non-empty string")
    if value.get("representation") != "plaintext-package-data":
        errors.append(f"{path}.representation: must be plaintext-package-data")
    if value.get("included_in_image") is not True:
        errors.append(f"{path}.included_in_image: must be true")
    inventory = value.get("inventory")
    if not isinstance(inventory, dict) or inventory.get("schema") != "qa-mcp.open-package-inventory.v1":
        errors.append(f"{path}.inventory: must be a qa-mcp open-package inventory")
    elif not isinstance(inventory.get("files"), dict) or not inventory["files"]:
        errors.append(f"{path}.inventory.files: must be a non-empty object")


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema",
        "component",
        "version",
        "git_commit",
        "created_at",
        "channel",
        "image",
        "assets",
        "data_assets",
        "runtime_assets",
    }
    allowed = required | {"compatibility_contracts", "notes", "release_link_id"}
    add_unknown_key_errors(errors, "<root>", manifest, allowed)
    for key in sorted(required):
        if key not in manifest:
            errors.append(f"<root>: missing required property: {key}")

    if manifest.get("schema") != SCHEMA:
        errors.append(f"schema: must be {SCHEMA}")
    component = manifest.get("component")
    if not isinstance(component, str) or not COMPONENT_PATTERN.fullmatch(component):
        errors.append("component: must match ^[a-z0-9][a-z0-9-]*$")
    if "version" in manifest and not is_non_empty_string(manifest["version"]):
        errors.append("version: must be a non-empty string")
    if "git_commit" in manifest:
        git_commit = manifest["git_commit"]
        if not isinstance(git_commit, str) or len(git_commit) < 7:
            errors.append("git_commit: must be a string with at least 7 characters")
    if "created_at" in manifest and not validate_datetime(manifest["created_at"]):
        errors.append("created_at: must be an RFC 3339 date-time string")
    if manifest.get("channel") != CHANNEL:
        errors.append(f"channel: must be {CHANNEL}")
    if "release_link_id" in manifest:
        release_link_id = manifest["release_link_id"]
        if not isinstance(release_link_id, str) or not RELEASE_LINK_ID_PATTERN.fullmatch(release_link_id):
            errors.append("release_link_id: must match ^r-[0-9]{8}-[0-9a-f]{16,}$")

    if "image" in manifest:
        validate_image(errors, manifest["image"])

    assets = manifest.get("assets")
    if isinstance(assets, dict):
        if not assets:
            errors.append("assets: must contain at least one asset")
        for name, value in sorted(assets.items()):
            validate_hash_size(errors, f"assets.{name}", value)
    elif "assets" in manifest:
        errors.append("assets: must be an object")

    data_assets = manifest.get("data_assets")
    if isinstance(data_assets, list):
        for index, value in enumerate(data_assets):
            validate_data_asset(errors, f"data_assets.{index}", value)
    elif "data_assets" in manifest:
        errors.append("data_assets: must be an array")

    if "runtime_assets" in manifest:
        validate_runtime_assets(errors, manifest["runtime_assets"])
    if "compatibility_contracts" in manifest:
        validate_string_list(errors, "compatibility_contracts", manifest["compatibility_contracts"])
    if "notes" in manifest:
        validate_string_list(errors, "notes", manifest["notes"])
    return errors


def validate_component_manifest(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    manifest = read_json(manifest_path)
    errors = validate_manifest(manifest)
    payload = {
        "schema": "ai1c.release-hardening-check.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check": "validate-component-manifest",
        "status": "ok" if not errors else "fail",
        "manifest": str(manifest_path),
        "schema_path": args.schema or "<qa-mcp-bundled-validator>",
        "contract": manifest.get("schema"),
        "component": manifest.get("component"),
        "version": manifest.get("version"),
        "errors": errors,
    }
    write(args.evidence, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    component = sub.add_parser("validate-component-manifest")
    component.add_argument("manifest")
    component.add_argument("--schema")
    component.add_argument("--evidence")
    component.set_defaults(func=validate_component_manifest)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
