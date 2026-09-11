"""Cycle-free platform version selection helpers."""

from __future__ import annotations

import os
import re
from pathlib import Path

from ._bundled import DEFAULT_VERSION_KEY, SUPPORTED_VERSION_KEYS, version_key

DEFAULT_PLATFORM_ROOT = "/opt/1cv8/x86_64/8.3.27.2130"
PLATFORM_VERSION_ENV = "QA_MCP_PLATFORM_VERSION"

_VERSION_RE = re.compile(r"(\d+\.\d+\.\d+\.\d+)")


def load_env_file(path: str | os.PathLike[str] | None) -> dict[str, str]:
    """Parse a small UTF-8 KEY=VALUE env file."""
    env: dict[str, str] = {}
    if not path:
        return env
    p = Path(path)
    if not p.is_file():
        return env
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        env[key.strip()] = value
    return env


def platform_version_from_root(platform_root: str | None) -> str | None:
    """Extract a full platform version from a platform-root path."""
    if not platform_root:
        return None
    m = _VERSION_RE.search(str(platform_root))
    return m.group(1) if m else None


def detect_live_platform_version(*, platform_root: str | None = None, env_file: str | None = None) -> str | None:
    """Live platform version by priority: explicit root, env-file PLATFORM_ROOT, default root."""
    if platform_root:
        return platform_version_from_root(platform_root)
    if env_file:
        root = (load_env_file(env_file) or {}).get("PLATFORM_ROOT")
        if root:
            return platform_version_from_root(root)
    return platform_version_from_root(DEFAULT_PLATFORM_ROOT)


def active_version_key(
    *,
    platform_root: str | None = None,
    env_file: str | None = None,
    env: dict[str, str] | None = None,
) -> str:
    """Resolve the active bundled-asset version family and fail closed if unsupported."""
    environ = os.environ if env is None else env
    override = environ.get(PLATFORM_VERSION_ENV)
    key: str | None = None
    if override:
        key = version_key(override)
        if key is None:
            raise ValueError(
                f"{PLATFORM_VERSION_ENV}={override!r} is not a recognizable platform version "
                f"(expected e.g. '8.3' or '8.5.1.1343').")
    if key is None:
        key = version_key(detect_live_platform_version(platform_root=platform_root, env_file=env_file)) \
            or DEFAULT_VERSION_KEY
    if key not in SUPPORTED_VERSION_KEYS:
        raise ValueError(
            f"no protocol assets bundled for platform {key} — supported: {', '.join(SUPPORTED_VERSION_KEYS)}; "
            f"capture per docs/capture-refresh-runbook.md")
    return key
