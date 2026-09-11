"""Capture bootstrap loading for direct TestClient protocol sessions."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from ..versioning import active_version_key
from .frames import CLIENT_TO_MANAGER, MANAGER_TO_CLIENT


def repo_root_from_package() -> Path:
    return Path(__file__).resolve().parents[3]


def captures_root(repo_root: Path) -> Path:
    return repo_root / "runtime" / "protocol-research" / "captures"


def resolve_capture_dir(value: str | Path, repo_root: Path | None = None, *, version: str | None = None) -> Path:
    """Resolve a capture by explicit path, then the bundled per-version package copy, then the dev ``runtime/`` tree.

    The bundled copy is selected by active platform family, then mapped through the bundled protocol-data policy:
    direct-covered families use their own data, while 8.5 uses the validated 8.3 corpus until a dedicated 8.5
    bundle is populated.
    """
    path = Path(value)
    if path.exists():
        return path.resolve()
    from .._bundled import capture_dir as bundled_capture_dir  # local import: _bundled has no deps

    if version is None:
        version = active_version_key()
    bundled = bundled_capture_dir(str(value), version)
    if bundled is not None:
        return bundled.resolve()
    root = repo_root or repo_root_from_package()
    candidate = captures_root(root) / str(value)
    if candidate.exists():
        return candidate.resolve()
    raise FileNotFoundError(f"Capture directory not found: {value}")


def payload_from_record(record: dict[str, Any]) -> bytes:
    payload_b64 = record.get("payload_b64")
    if payload_b64:
        return base64.b64decode(payload_b64)

    aggregate_path = Path(record["aggregate_path"])
    offset = int(record["aggregate_offset"])
    byte_count = int(record["byte_count"])
    with aggregate_path.open("rb") as file_obj:
        file_obj.seek(offset)
        return file_obj.read(byte_count)


class CaptureBootstrap:
    """Captured bootstrap manager frames needed before generated UI queries."""

    def __init__(self, capture_dir: Path, manager_frames: list[bytes], client_frames: list[bytes]) -> None:
        self.capture_dir = capture_dir
        self.manager_frames = manager_frames
        self.client_frames = client_frames

    @classmethod
    def load(cls, capture_dir: Path) -> "CaptureBootstrap":
        traffic_path = capture_dir / "traffic.jsonl"
        if not traffic_path.exists():
            raise FileNotFoundError(f"traffic.jsonl not found: {traffic_path}")

        manager_frames: list[bytes] = []
        client_frames: list[bytes] = []
        for line in traffic_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                record = json.loads(line)
                if record.get("event") != "chunk":
                    continue
                payload = payload_from_record(record)
                if record.get("direction") == MANAGER_TO_CLIENT:
                    manager_frames.append(payload)
                elif record.get("direction") == CLIENT_TO_MANAGER:
                    client_frames.append(payload)

        if len(manager_frames) < 10:
            raise RuntimeError(f"Capture {capture_dir.name} does not contain manager frames 1..10")
        return cls(capture_dir=capture_dir, manager_frames=manager_frames, client_frames=client_frames)

    def captured_frame(self, frame_index: int) -> bytes:
        return self.manager_frames[frame_index - 1]
