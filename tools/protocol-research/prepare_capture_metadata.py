#!/usr/bin/env python3
"""Prepare sanitized metadata sidecars for refreshed protocol captures."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.protocol.capture_metadata import CaptureMetadata, load_capture_metadata, write_capture_metadata  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Write or validate a raw-data-free capture-metadata sidecar for a "
            "platform/configuration-specific protocol refresh."
        )
    )
    parser.add_argument("--output", required=True, help="Sidecar JSON path to write or validate.")
    parser.add_argument("--capture-id", required=True, help="Stable capture id, e.g. third-party-config-currencies.")
    parser.add_argument("--platform-build", required=True, help="Full 1C platform build, e.g. 8.3.27.2130.")
    parser.add_argument("--configuration-name", required=True, help="Configuration label, e.g. Бухгалтерия 3.0.")
    parser.add_argument("--configuration-version", default="", help="Optional configuration version.")
    parser.add_argument("--configuration-vendor", default="", help="Optional vendor/project label.")
    parser.add_argument("--capture-dir", required=True, help="Repo-relative or runtime capture directory.")
    parser.add_argument("--manager-templates", default="", help="Manager-frame template path produced by refresh.")
    parser.add_argument("--notes", default="", help="Short sanitized operator notes.")
    parser.add_argument("--check", action="store_true", help="Validate the resulting sidecar can be loaded.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    metadata = CaptureMetadata(
        capture_id=args.capture_id,
        platform_build=args.platform_build,
        configuration_name=args.configuration_name,
        configuration_version=args.configuration_version,
        configuration_vendor=args.configuration_vendor,
        capture_dir=args.capture_dir,
        manager_templates=args.manager_templates,
        notes=args.notes,
    )
    output = Path(args.output)
    write_capture_metadata(output, metadata)
    if args.check:
        loaded = load_capture_metadata(output)
        if loaded != metadata:
            print(f"metadata validation failed: {output}", file=sys.stderr)
            return 1
    print(f"wrote sanitized capture metadata: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
