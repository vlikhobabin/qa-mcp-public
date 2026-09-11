"""Explicit local-content reuse of immutable focused check observations.

The default is execution. A project may allowlist a command and its complete
local dependency set; this is a claim about dependency completeness, not a way
to cache mutable runtime observations or the final repository floor.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

SNAPSHOT_SCHEMA = "changerail.evidence-dependencies.v1"
REUSE_SCHEMA = "changerail.dependency-reuse.v1"
SHARED_INPUTS = (
    "conftest.py",
    "tests/conftest.py",
    "pyproject.toml",
    "uv.lock",
    "pytest.ini",
    "setup.cfg",
    "tox.ini",
    ".env",
    ".changerail/profile.toml",
    "scripts/changerail",
    "tools/changerail/schemas",
    "bin/chrl",
    "bin/openspec",
    "tools/openspec/package.json",
    "tools/openspec/package-lock.json",
)
MAX_INVENTORY_ENTRIES = 20000
MAX_RECEIPT_BYTES = 262144


def _receipt_bytes(root: Path, path: Path) -> bytes:
    """Read bounded regular receipt bytes without following any path component."""
    relative = path.relative_to(root)
    if not relative.parts or ".." in relative.parts:
        raise ValueError("unsafe original observation path")
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in relative.parts[:-1]:
            child = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
            )
            os.close(directory)
            directory = child
        fd = os.open(
            relative.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_RECEIPT_BYTES:
                raise ValueError("nonregular or oversized original observation")
            data = stream.read(MAX_RECEIPT_BYTES + 1)
            after = os.fstat(stream.fileno())
            attributes = (
                "st_dev",
                "st_ino",
                "st_mode",
                "st_size",
                "st_mtime_ns",
                "st_ctime_ns",
            )
            if (
                len(data) > MAX_RECEIPT_BYTES
                or len(data) != before.st_size
                or any(
                    getattr(before, key) != getattr(after, key) for key in attributes
                )
            ):
                raise ValueError("original observation changed during read")
            return data
    finally:
        os.close(directory)


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _path(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path == Path("."):
        raise ValueError("dependency path must be bounded and repository-relative")
    candidate = root / path
    for part in (candidate, *candidate.parents):
        if part == root:
            break
        if part.is_symlink():
            raise ValueError("symlink evidence dependency is unsupported")
    if not candidate.resolve().is_relative_to(root):
        raise ValueError("external evidence dependency")
    return candidate


def selected_dependencies(
    profile: Mapping[str, Any],
    command: Mapping[str, Any],
    *,
    kind: str = "test",
) -> list[str] | None:
    """Return a profile-owned local allowlist, or None to execute normally.

    Configuration shape: evidence.reuse='dependencies' and evidence.checks rows
    with argv, dependencies, kind='local', external_state=false. Only focused
    argv checks are eligible; runtime, shell and final checks always execute.
    """
    policy = profile.get("evidence", {})
    if policy.get("reuse", "rerun") == "rerun":
        return None
    if policy.get("reuse") != "dependencies":
        raise ValueError("unsupported evidence reuse policy")
    if kind != "test" or command.get("kind") != "argv":
        return None
    matches = [
        row
        for row in policy.get("checks", [])
        if row.get("argv") == command.get("argv")
    ]
    if not matches:
        return None
    if len(matches) != 1:
        raise ValueError("duplicate evidence command allowlist")
    row = matches[0]
    if row.get("kind") != "local" or row.get("external_state") is not False:
        raise ValueError("reuse requires an explicit local-only dependency contract")
    deps = row.get("dependencies")
    if (
        not isinstance(deps, list)
        or not deps
        or any(not isinstance(p, str) or not p for p in deps)
    ):
        raise ValueError("reuse requires explicit local dependencies")
    return list(deps)


def capture_dependency_snapshot(
    root: Path,
    dependencies: Sequence[str],
    *,
    command: Sequence[str],
    environment: Mapping[str, str],
) -> dict[str, Any]:
    """Capture files, additions/deletions, harness, argv and hashed full env.

    Generated Python bytecode is excluded; real files or symlinks hidden inside
    cache directories still participate. Environment contents are never stored.
    """
    root = root.resolve()
    if (
        not dependencies
        or not command
        or any(not isinstance(v, str) or not v for v in [*dependencies, *command])
    ):
        raise ValueError("reuse requires dependencies and argv")
    declared = sorted(
        {str(_path(root, value).relative_to(root)) for value in dependencies}
    )
    inputs = set(declared) | set(SHARED_INPUTS)
    for value in declared:
        for parent in _path(root, value).parents:
            if parent == root:
                break
            inputs.add(str((parent / "conftest.py").relative_to(root)))
    inventory: dict[str, Any] = {}
    visited = 0

    def visit(path: Path) -> None:
        nonlocal visited
        relative = str(path.relative_to(root))
        if relative in inventory:
            return
        visited += 1
        if visited > MAX_INVENTORY_ENTRIES:
            raise ValueError("dependency inventory exceeds bounded limit")
        _path(root, relative)
        if not path.exists():
            inventory[relative] = {"kind": "missing"}
        elif path.is_file():
            if (
                relative not in inputs
                and path.parent.name == "__pycache__"
                and str(path.parent.relative_to(root)) not in inputs
                and path.suffix in {".pyc", ".pyo"}
            ):
                return
            inventory[relative] = {
                "kind": "file",
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "mode": path.stat().st_mode & 0o777,
            }
        elif path.is_dir():
            if path.name != "__pycache__" or relative in inputs:
                inventory[relative] = {"kind": "directory"}
            for child in sorted(path.iterdir()):
                visit(child)
        else:
            raise ValueError("unsupported dependency file")

    for value in sorted(inputs):
        visit(_path(root, value))
    search_path = os.pathsep.join(
        str((root / entry).resolve())
        for entry in environment.get("PATH", os.defpath).split(os.pathsep)
    )
    executable_name = str(root / command[0]) if "/" in command[0] else command[0]
    executable = shutil.which(executable_name, path=search_path)
    if not executable:
        raise ValueError("reuse command executable cannot be resolved")
    binaries = {}
    for name, filename in (("command", executable), ("observer", sys.executable)):
        binary = Path(filename).resolve()
        binaries[name] = {
            "path": str(binary),
            "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        }
    value = {
        "schema": SNAPSHOT_SCHEMA,
        "dependencies": declared,
        "command": list(command),
        "environment_sha256": _digest(dict(environment)),
        "inventory": inventory,
        "binaries": binaries,
        "python_version": sys.version,
    }
    return {**value, "sha256": _digest(value)}


def validate_dependency_snapshot(
    root: Path,
    snapshot: Any,
    *,
    command: Sequence[str],
    environment: Mapping[str, str],
) -> dict[str, Any]:
    if not isinstance(snapshot, dict) or not isinstance(
        snapshot.get("dependencies"), list
    ):
        raise ValueError("check has no explicit dependency snapshot")
    current = capture_dependency_snapshot(
        root, snapshot["dependencies"], command=command, environment=environment
    )
    if current != snapshot:
        raise ValueError("evidence dependencies, command or environment changed")
    return current


SourceReader = Callable[[Path], tuple[dict[str, Any], bytes, bool]]


def _validated_source(
    root: Path,
    run_dir: Path,
    source_path: Path,
    *,
    profile: Mapping[str, Any],
    command: Mapping[str, Any],
    environment: Mapping[str, str],
    read_source: SourceReader,
) -> tuple[dict[str, Any], bytes, bytes]:
    source_path = _path(root, str(source_path.relative_to(root)))
    if source_path.parent != run_dir / "focused-evidence":
        raise ValueError("reuse source must belong to this run's focused observations")
    before = _receipt_bytes(root, source_path)
    decoded = json.loads(before)
    if (
        not isinstance(decoded, dict)
        or decoded.get("schema") != "changerail.check-result.v1"
    ):
        raise ValueError("reuse needs an immutable successful original check")
    source, log, _ = read_source(source_path)
    if _receipt_bytes(root, source_path) != before or decoded != source:
        raise ValueError("original observation changed during validation")
    if (
        source.get("schema") != "changerail.check-result.v1"
        or source.get("lane") != "focused"
        or source.get("run_id") != run_dir.name
        or source.get("state") != "terminal"
        or source.get("verdict") != "verified"
        or source.get("outcome") != "exit"
        or type(source.get("exit_code")) is not int
        or source["exit_code"] != 0
        or source.get("before") != source.get("fingerprint")
        or not source.get("fingerprint")
        or source.get("command_identity") != command
    ):
        raise ValueError("reuse needs an immutable successful original check")
    dependencies = selected_dependencies(profile, command)
    snapshot = source.get("dependency_snapshot")
    if (
        dependencies is None
        or not isinstance(snapshot, dict)
        or sorted(set(dependencies)) != snapshot.get("dependencies")
    ):
        raise ValueError("source dependencies are not currently allowlisted")
    validate_dependency_snapshot(
        root, snapshot, command=command["argv"], environment=environment
    )
    if (
        not log
        or source.get("log_size") != len(log)
        or source.get("log_sha256") != hashlib.sha256(log).hexdigest()
    ):
        raise ValueError("reuse source log integrity failed")
    return source, log, before


def create_reuse_receipt(
    root: Path,
    run_dir: Path,
    source_path: Path,
    *,
    profile: Mapping[str, Any],
    command: Mapping[str, Any],
    environment: Mapping[str, str],
    read_source: SourceReader,
    fingerprint: Mapping[str, str],
    receipt_id: str,
    observed_at: str,
) -> dict[str, Any]:
    """Prepare a new link, without copying/fabricating an execution or its log."""
    source, _, source_bytes = _validated_source(
        root,
        run_dir,
        source_path,
        profile=profile,
        command=command,
        environment=environment,
        read_source=read_source,
    )
    return {
        "schema": REUSE_SCHEMA,
        "receipt_id": receipt_id,
        "run_id": run_dir.name,
        "card": source["card"],
        "lane": "focused",
        "fingerprint": dict(fingerprint),
        "validated_at": observed_at,
        "command_identity": dict(command),
        "source": {
            "path": str(source_path.relative_to(root)),
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
            "attempt_id": source["attempt_id"],
            "fingerprint": source["fingerprint"],
            "dependency_sha256": source["dependency_snapshot"]["sha256"],
        },
    }


def validate_reuse_receipt(
    root: Path,
    run_dir: Path,
    path: Path,
    receipt: Mapping[str, Any],
    *,
    profile: Mapping[str, Any],
    command: Mapping[str, Any] | None,
    environment: Mapping[str, str],
    read_source: SourceReader,
    fingerprint: Mapping[str, str],
) -> tuple[dict[str, Any], bytes, bool]:
    """Read-validate every reuse consumer; return ORIGINAL execution fields/log.

    Callers still validate condition-level pytest selectors/assertions against
    this actual log. A reuse receipt alone is never a semantic acceptance proof.
    """
    keys = {
        "schema",
        "receipt_id",
        "run_id",
        "card",
        "lane",
        "fingerprint",
        "validated_at",
        "command_identity",
        "source",
    }
    if (
        set(receipt) != keys
        or receipt.get("schema") != REUSE_SCHEMA
        or receipt.get("receipt_id") != path.stem
        or path.parent != run_dir / "focused-evidence"
        or receipt.get("run_id") != run_dir.name
        or receipt.get("lane") != "focused"
        or receipt.get("fingerprint") != fingerprint
    ):
        raise ValueError("foreign or stale dependency reuse receipt")
    identity = receipt["command_identity"]
    if command is not None and identity != command:
        raise ValueError("foreign reuse command")
    reference = receipt["source"]
    if not isinstance(reference, dict) or set(reference) != {
        "path",
        "sha256",
        "attempt_id",
        "fingerprint",
        "dependency_sha256",
    }:
        raise ValueError("invalid original observation reference")
    source_path = _path(root, reference["path"])
    if source_path == path:
        raise ValueError("original observation record changed")
    source, log, source_bytes = _validated_source(
        root,
        run_dir,
        source_path,
        profile=profile,
        command=identity,
        environment=environment,
        read_source=read_source,
    )
    if hashlib.sha256(source_bytes).hexdigest() != reference["sha256"]:
        raise ValueError("original observation record changed")
    if (
        source["attempt_id"] != reference["attempt_id"]
        or source["fingerprint"] != reference["fingerprint"]
        or source["dependency_snapshot"]["sha256"] != reference["dependency_sha256"]
        or source["card"] != receipt["card"]
    ):
        raise ValueError("reuse observation lineage changed")
    return source, log, True
