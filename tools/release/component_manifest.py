#!/usr/bin/env python3
"""Build the qa-mcp self-hosted component release manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "ai1c.component-release.manifest.v1"
COMPONENT = "qa-mcp"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def asset_entry(path: Path) -> dict[str, Any]:
    return {
        "sha256": sha256_file(path),
        "size": path.stat().st_size,
    }


def build_manifest(
    *,
    version: str,
    git_commit: str,
    image_tag: str,
    image_asset: Path,
    package_inventory: Path,
    assets: dict[str, Path],
    created_at: str | None = None,
) -> dict[str, Any]:
    timestamp = created_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    image_info = asset_entry(image_asset)
    manifest_assets = {name: asset_entry(path) for name, path in sorted(assets.items())}
    return {
        "schema": SCHEMA,
        "component": COMPONENT,
        "version": version,
        "git_commit": git_commit,
        "created_at": timestamp,
        "channel": "component-self-hosted",
        "image": {
            "type": "docker-archive",
            "tag": image_tag,
            "asset": image_asset.name,
            "sha256": image_info["sha256"],
            "size": image_info["size"],
        },
        "assets": manifest_assets,
        "data_assets": [],
        "runtime_assets": {
            "path": "qa_mcp/_bundled",
            "representation": "plaintext-package-data",
            "included_in_image": True,
            "separate_data_asset": False,
            "verification": "docker/verify_open_image.py",
            "inventory": json.loads(package_inventory.read_text(encoding="utf-8")),
        },
    }


def parse_asset(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("asset must use name=path")
    name, raw_path = value.split("=", 1)
    if not name:
        raise argparse.ArgumentTypeError("asset name must not be empty")
    path = Path(raw_path)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"asset path does not exist: {path}")
    return name, path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--image-tag", required=True)
    parser.add_argument("--image-asset", required=True, type=Path)
    parser.add_argument("--package-inventory", required=True, type=Path)
    parser.add_argument("--asset", action="append", default=[], type=parse_asset, help="Release asset as name=path")
    parser.add_argument("--created-at", default="")
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.image_asset.is_file():
        raise SystemExit(f"image asset does not exist: {args.image_asset}")
    assets = dict(args.asset)
    manifest = build_manifest(
        version=args.version,
        git_commit=args.git_commit,
        image_tag=args.image_tag,
        image_asset=args.image_asset,
        package_inventory=args.package_inventory,
        assets=assets,
        created_at=args.created_at or None,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
