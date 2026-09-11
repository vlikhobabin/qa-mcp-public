"""Explicit shared-source trust, separate from project evidence confinement."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from scripts.changerail.contracts import DeliveryError

BINDING = ".changerail/source-link.json"
SCHEMA = "changerail.source-link.v1"
RUNTIME_LINKS = frozenset(
    {
        "DISTRIBUTION.md",
        "distribution.py",
        "distribution.json",
        "scripts/__init__.py",
        "scripts/changerail",
        "bin/chrl",
        "bin/chrl-run",
        "bin/chrl-dist",
        "bin/openspec",
        "tools/changerail/LICENSE",
        "tools/changerail/ORIGIN.md",
        "tools/changerail/README.md",
        "tools/changerail/schemas",
        "tools/changerail/skills",
        "tools/changerail/templates",
        "tools/openspec/.gitignore",
        "tools/openspec/README.md",
        "tools/openspec/bootstrap.sh",
        "tools/openspec/check-install.mjs",
        "tools/openspec/workflow-instructions.mjs",
        "tools/openspec/package.json",
        "tools/openspec/package-lock.json",
    }
)
DEVELOPMENT_LINKS = frozenset(
    {
        "tools/changerail/tests",
        "bin/test-changerail",
        "tools/openspec/test-wrapper.mjs",
    }
)


def project_root(source: Path) -> Path:
    explicit = os.environ.get("CHRL_PROJECT_ROOT")
    if explicit:
        root = Path(explicit).resolve(strict=True)
    else:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
        )
        if result.returncode:
            raise DeliveryError("select a project with --project or CHRL_PROJECT_ROOT")
        root = Path(result.stdout.strip()).resolve()
    if root != source.resolve() and not (root / ".changerail/profile.toml").is_file():
        raise DeliveryError("selected project has no ChangeRail profile")
    return root


def _regular(root: Path, relative: str) -> Path:
    if (
        not relative
        or Path(relative).is_absolute()
        or any(p in ("", ".", "..") for p in relative.split("/"))
    ):
        raise DeliveryError("unsafe shared source path")
    path = root
    for part in relative.split("/"):
        path /= part
        if path.is_symlink():
            raise DeliveryError(f"linked path inside shared source: {relative}")
    return path


def _binding_record(root: Path) -> dict[str, Any] | None:
    path = _regular(root, BINDING)
    if not path.exists():
        return None
    value = json.loads(path.read_text())
    if value.get("schema") != SCHEMA or value.get("project_root") != str(
        root.resolve()
    ):
        raise DeliveryError("invalid shared-source project binding")
    source = Path(value.get("source_root", ""))
    if not source.is_absolute() or os.path.normpath(str(source)) != str(source):
        raise DeliveryError("invalid shared-source root")
    mappings = value.get("mappings")
    if not isinstance(mappings, dict) or not mappings:
        raise DeliveryError("missing shared-source mappings")
    if not isinstance(value.get("development"), bool):
        raise DeliveryError("missing shared-source development mode")
    expected_links = RUNTIME_LINKS | (
        DEVELOPMENT_LINKS if value["development"] else frozenset()
    )
    if mappings != {name: name for name in expected_links}:
        raise DeliveryError(
            "shared-source mappings exceed or omit declared tool ownership"
        )
    return value


def recovery_binding(root: Path) -> dict[str, Any] | None:
    """Validate owned consumer links without accessing the source being detached."""
    value = _binding_record(root)
    if value is None:
        return None
    source = Path(value["source_root"])
    for local, target in value["mappings"].items():
        parent = _regular(root, str(Path(local).parent)) if "/" in local else root
        linked = parent / Path(local).name
        if not linked.is_symlink() or os.readlink(linked) != str(source / target):
            raise DeliveryError(f"shared-source link changed: {local}")
    return value


def binding(root: Path) -> dict[str, Any] | None:
    value = _binding_record(root)
    if value is None:
        return None
    source = Path(value["source_root"])
    if source.resolve() != source or not source.is_dir():
        raise DeliveryError("invalid shared-source root")
    for local, target in value["mappings"].items():
        expected = _regular(source, target)
        if expected.is_dir():
            for item in expected.rglob("*"):
                if item.is_symlink():
                    raise DeliveryError(
                        f"linked path inside shared source: {item.relative_to(source)}"
                    )
        # Only the declared leaf may be linked; never accept linked ancestors.
        parent = _regular(root, str(Path(local).parent)) if "/" in local else root
        linked = parent / Path(local).name
        if not linked.is_symlink() or linked.resolve(strict=True) != expected:
            raise DeliveryError(f"shared-source link changed: {local}")
    return value


def trusted_path(root: Path, path: Path) -> Path | None:
    value = binding(root)
    if value is None:
        return None
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError:
        return None
    for local, target in value["mappings"].items():
        if relative == local or relative.startswith(local + "/"):
            suffix = relative[len(local) :].lstrip("/")
            return _regular(
                Path(value["source_root"]), target + ("/" + suffix if suffix else "")
            )
    return None


def read_runtime(root: Path, path: Path, fallback: Any) -> bytes:
    trusted = trusted_path(root, path)
    if trusted is None:
        return fallback(path, 32 * 1024 * 1024)
    if not trusted.is_file() or trusted.stat().st_size > 32 * 1024 * 1024:
        raise DeliveryError("shared runtime file is not bounded and regular")
    return trusted.read_bytes()


def source_info(root: Path) -> dict[str, Any]:
    value = binding(root)
    if value is None:
        return {"mode": "installed", "project_root": str(root)}
    source = Path(value["source_root"])

    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(source), *args], capture_output=True, text=True
        )
        return result.stdout.strip() if result.returncode == 0 else ""

    hashes = {}
    for local, target in value["mappings"].items():
        if local == "bin/test-changerail" or local.startswith("tools/changerail/tests"):
            continue
        path = _regular(source, target)
        files = path.rglob("*") if path.is_dir() else [path]
        for item in files:
            if "__pycache__" in item.parts or item.suffix == ".pyc":
                continue
            if item.is_file():
                safe = _regular(source, item.relative_to(source).as_posix())
                hashes[item.relative_to(source).as_posix()] = hashlib.sha256(
                    safe.read_bytes()
                ).hexdigest()
    return {
        "mode": "shared-source",
        "project_root": str(root),
        "source_root": str(source),
        "revision": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain")),
        "sha256": hashlib.sha256(
            json.dumps(hashes, sort_keys=True).encode()
        ).hexdigest(),
        "files": hashes,
    }
