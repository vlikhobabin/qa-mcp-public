"""Sanitized metadata for protocol captures and config-matched selection."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "qa-mcp.protocol-capture-metadata.v1"
SIDECAR_NAMES = ("capture-metadata.json", "capture.metadata.json", "metadata.json")


def normalize_tag(value: str | None) -> str:
    """Normalize a platform/configuration tag for matching without losing the original label."""
    text = " ".join(str(value or "").strip().split())
    return text.replace("ё", "е").replace("Ё", "Е").casefold()


@dataclass(frozen=True)
class CaptureMetadata:
    capture_id: str
    platform_build: str = ""
    configuration_name: str = ""
    configuration_version: str = ""
    configuration_vendor: str = ""
    capture_dir: str = ""
    manager_templates: str = ""
    generated_at: str = ""
    notes: str = ""
    schema: str = SCHEMA

    @property
    def configuration_tags(self) -> set[str]:
        tags = {
            normalize_tag(self.configuration_name),
            normalize_tag(self.configuration_version),
            normalize_tag(self.configuration_vendor),
            normalize_tag(f"{self.configuration_name} {self.configuration_version}"),
            normalize_tag(f"{self.configuration_vendor} {self.configuration_name}"),
            normalize_tag(f"{self.configuration_vendor} {self.configuration_version}"),
        }
        return {tag for tag in tags if tag}

    def platform_matches(self, requested_platform_build: str | None) -> bool:
        if not requested_platform_build:
            return True
        return normalize_tag(self.platform_build) == normalize_tag(requested_platform_build)

    def configuration_matches(self, requested_configuration: str | None) -> bool:
        if not requested_configuration:
            return True
        requested = normalize_tag(requested_configuration)
        return requested in self.configuration_tags

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "capture_id": self.capture_id,
            "platform_build": self.platform_build,
            "configuration": {
                "name": self.configuration_name,
                "version": self.configuration_version,
                "vendor": self.configuration_vendor,
            },
            "capture_dir": self.capture_dir,
            "manager_templates": self.manager_templates,
            "generated_at": self.generated_at,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CaptureMetadata":
        config = data.get("configuration") if isinstance(data.get("configuration"), dict) else {}
        return cls(
            schema=str(data.get("schema") or SCHEMA),
            capture_id=str(data.get("capture_id") or data.get("id") or ""),
            platform_build=str(data.get("platform_build") or data.get("platform_version") or ""),
            configuration_name=str(config.get("name") or data.get("configuration_name") or ""),
            configuration_version=str(config.get("version") or data.get("configuration_version") or ""),
            configuration_vendor=str(config.get("vendor") or data.get("configuration_vendor") or ""),
            capture_dir=str(data.get("capture_dir") or ""),
            manager_templates=str(data.get("manager_templates") or ""),
            generated_at=str(data.get("generated_at") or ""),
            notes=str(data.get("notes") or ""),
        )


@dataclass(frozen=True)
class CaptureSelection:
    capture: CaptureMetadata | None
    match: str
    requested_platform_build: str | None = None
    requested_configuration: str | None = None
    exact_config_match: bool = False
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "match": self.match,
            "exact_config_match": self.exact_config_match,
            "reason": self.reason,
            "requested": {
                "platform_build": self.requested_platform_build,
                "configuration": self.requested_configuration,
            },
            "capture": self.capture.to_dict() if self.capture is not None else None,
        }


def _metadata_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_dir():
        for name in SIDECAR_NAMES:
            sidecar = candidate / name
            if sidecar.exists():
                return sidecar
    return candidate


def load_capture_metadata(path: str | Path) -> CaptureMetadata:
    sidecar = _metadata_path(path)
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    metadata = CaptureMetadata.from_dict(data)
    if not metadata.capture_id:
        raise ValueError(f"capture metadata missing capture_id: {sidecar}")
    return metadata


def write_capture_metadata(path: str | Path, metadata: CaptureMetadata) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(metadata.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_available_capture_metadata(paths: Iterable[str | Path]) -> list[CaptureMetadata]:
    loaded: list[CaptureMetadata] = []
    for path in paths:
        try:
            loaded.append(load_capture_metadata(path))
        except FileNotFoundError:
            continue
    return loaded


def select_capture_metadata(
    candidates: Iterable[CaptureMetadata],
    *,
    requested_platform_build: str | None = None,
    requested_configuration: str | None = None,
    fallback_capture_id: str | None = None,
) -> CaptureSelection:
    items = list(candidates)
    platform_matches = [item for item in items if item.platform_matches(requested_platform_build)]
    for item in platform_matches:
        if item.configuration_matches(requested_configuration):
            return CaptureSelection(
                capture=item,
                match="exact",
                requested_platform_build=requested_platform_build,
                requested_configuration=requested_configuration,
                exact_config_match=bool(requested_configuration),
                reason="capture metadata matches requested platform/configuration tags",
            )

    fallback = None
    if fallback_capture_id:
        fallback = next((item for item in items if item.capture_id == fallback_capture_id), None)
    if fallback is None:
        fallback = (platform_matches or items or [None])[0]
    if fallback is None:
        return CaptureSelection(
            capture=None,
            match="none",
            requested_platform_build=requested_platform_build,
            requested_configuration=requested_configuration,
            exact_config_match=False,
            reason="no capture metadata candidates were available",
        )
    return CaptureSelection(
        capture=fallback,
        match="fallback",
        requested_platform_build=requested_platform_build,
        requested_configuration=requested_configuration,
        exact_config_match=False,
        reason=(
            "fallback capture is not config-matched; requested platform/configuration "
            "remain unproven until a matching capture is refreshed"
        ),
    )
