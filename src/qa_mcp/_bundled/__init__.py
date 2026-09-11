"""Runtime assets bundled into the package so qa-mcp is self-contained — **per platform version**.

The engine drives 1C by replaying genuine TestClient captures plus manager-frame templates and read-only
operation evidence. Those bytes are faithful to ONE platform protocol version (the family they were captured
on), so the package carries a **separate asset set per version family** under ``_bundled/<version-key>/``:

    _bundled/
      8.3/                      ← populated (captured on 8.3.27.x)
        captures/<name>/traffic.jsonl
        templates/manager_frame_templates.json
        templates/value_read_templates.json
        accepted_mappings.json
      8.5/                      ← declared-supported slot; uses validated 8.3 data until drift requires recapture

``version-key`` is the platform **major-minor family** (``8.3``, ``8.5``); the exact captured ``8.x.y.z`` is
recorded in that set's manifest (``config/protocol-capture-manifest-<key>.json``). A supported family may declare a
protocol-data fallback when live validation proves the wire protocol has not moved. Today ``8.5`` uses the populated
``8.3`` protocol-data set until a validate-first run goes red and an 8.5-specific bundle is needed. In the dev
workspace the raw inputs live under the git-ignored ``runtime/`` tree and ``docs/``; this directory carries exactly
the files the runtime reads, so a fresh clone / wheel / Docker image works standalone.

This module is intentionally **dependency-free** (it only joins paths): the version *policy* — how the active
version is selected from the environment (``QA_MCP_PLATFORM_VERSION`` / ``PLATFORM_ROOT``) and which families
are supported — lives in :mod:`qa_mcp.versioning` (``active_version_key``), which reuses the layout constants
defined here. Callers resolve the active key there and pass it into the path helpers below.

Populate / refresh a version with ``scripts/bundle_runtime_assets.py --version <key>`` (copies only
``traffic.jsonl`` per capture and the template / accepted-mapping JSON, stripping machine-path metadata).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Platform major-minor families this package knows about. A family is *supported* (declared here) independently
# of whether its ``_bundled/<key>/`` slot is populated yet. Unsupported families fail closed in
# ``versioning.active_version_key``. Supported empty families may declare a protocol-data fallback below.
SUPPORTED_VERSION_KEYS: tuple[str, ...] = ("8.3", "8.5")
DEFAULT_VERSION_KEY = "8.3"
PROTOCOL_DATA_FALLBACKS: dict[str, str] = {"8.5": "8.3"}

_VERSION_RE = re.compile(r"(\d+)\.(\d+)")


def version_key(platform_version: str | None) -> str | None:
    """Map a platform version to its major-minor family key.

    ``"8.3.27.2130"`` → ``"8.3"``; ``"8.5.1.1343"`` → ``"8.5"``; ``"8.5"`` → ``"8.5"``. Returns ``None`` when no
    ``<major>.<minor>`` can be read (so callers can fall back to the default / fail closed).
    """
    if not platform_version:
        return None
    m = _VERSION_RE.search(str(platform_version))
    return f"{m.group(1)}.{m.group(2)}" if m else None


def version_root(ver: str = DEFAULT_VERSION_KEY) -> Path:
    """Directory holding the bundled asset set for version family ``ver`` (existence not asserted)."""
    return ROOT / ver


def has_protocol_data(ver: str = DEFAULT_VERSION_KEY) -> bool:
    """Whether ``ver`` has a populated bundled protocol-data set."""
    key = version_key(ver) or ver
    root = version_root(key)
    return (
        any((root / "captures").glob("*/traffic.jsonl"))
        and (root / "templates" / "manager_frame_templates.json").exists()
        and (root / "templates" / "value_read_templates.json").exists()
        and (root / "accepted_mappings.json").exists()
    )


def protocol_data_version_key(ver: str = DEFAULT_VERSION_KEY) -> str:
    """Version family whose bundled protocol data should serve ``ver``."""
    key = version_key(ver) or ver
    if has_protocol_data(key):
        return key
    return PROTOCOL_DATA_FALLBACKS.get(key, key)


def capture_dir(name: str, ver: str = DEFAULT_VERSION_KEY) -> Path | None:
    """Bundled capture directory for ``name`` in version ``ver`` if it carries a ``traffic.jsonl``, else None."""
    candidate = version_root(protocol_data_version_key(ver)) / "captures" / name
    return candidate if (candidate / "traffic.jsonl").exists() else None


def template(name: str, ver: str = DEFAULT_VERSION_KEY) -> Path:
    """Absolute path to a bundled manager-frame template JSON for version ``ver`` (existence not asserted)."""
    return version_root(protocol_data_version_key(ver)) / "templates" / name


def accepted_mappings_path(ver: str = DEFAULT_VERSION_KEY) -> Path:
    """Absolute path to the bundled accepted-mappings evidence for version ``ver`` (existence not asserted)."""
    return version_root(protocol_data_version_key(ver)) / "accepted_mappings.json"
