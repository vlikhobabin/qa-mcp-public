"""Hash-bound installed native identity bridge for exact plan restoration.

The caller owns the project lock and the plan restoration authority/intent.
This module never grants an old run permission independently of that transition.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import distribution as dist
from scripts.changerail.contracts import DeliveryError
from scripts.changerail import installed_compatibility

SCHEMA = "changerail.installed-restoration.v1"
_RUNTIME_PREFIXES = (
    "scripts/changerail/",
    "tools/changerail/schemas/",
    "tools/changerail/skills/",
)
_FIXED = {
    "bin/chrl",
    "bin/chrl-run",
    "bin/openspec",
    ".changerail/profile.toml",
    dist.LOCK,
}
_EXPANDED = {
    "scripts/__init__.py",
    "tools/openspec/workflow-instructions.mjs",
    "tools/openspec/check-install.mjs",
    "tools/openspec/package.json",
    "tools/openspec/package-lock.json",
    "tools/openspec/bootstrap.sh",
}


def _read(root: Path, name: str) -> bytes:
    return dist.read_file(root, name)[0]


def _lineage(delivery: Any, run_dir: Path) -> list[Path]:
    root = Path(delivery.REPO_ROOT)
    runs = root / ".runtime/changerail/runs"
    result = []
    while True:
        if run_dir.parent != runs or run_dir.resolve() != run_dir or run_dir in result:
            raise DeliveryError("installed restoration has unsafe or cyclic lineage")
        value = json.loads(
            _read(root, (run_dir / "run.json").relative_to(root).as_posix())
        )
        if (
            value.get("run_id") != run_dir.name
            or not value.get("finished_at")
            or value.get("schema") != "changerail.delivery-run.v2"
            or value.get("execution_contract") != "changerail.native.v1"
            or value.get("lifecycle_mode") != "openspec-v1"
            or value.get("mode") != "delivery"
        ):
            raise DeliveryError("installed restoration requires stopped native lineage")
        result.append(run_dir)
        previous = value.get("recovery_of")
        if previous is None:
            return result
        if (
            not isinstance(previous, str)
            or dist.safe_name(previous) != Path(previous).name
        ):
            raise DeliveryError("installed restoration has unsafe predecessor")
        run_dir = runs / previous


def _history(root: Path, lineage: list[Path]) -> dict[str, dict[str, Any]]:
    result = {}
    for run in lineage:
        for path in sorted(run.rglob("*")):
            if path.is_symlink():
                raise DeliveryError("linked installed restoration history")
            if path.is_file():
                name = path.relative_to(root).as_posix()
                result[name] = dist.entry(dist.read_file(root, name))
    return result


def _identity_keys(
    root: Path, files: dict[str, Any], launcher: str, *, expanded: bool
) -> set[str]:
    keys = (
        _FIXED
        | {launcher}
        | {name for name in files if name.startswith(_RUNTIME_PREFIXES)}
    )
    adapters = root / ".changerail/adapters"
    for path in adapters.rglob("*"):
        if path.is_symlink():
            raise DeliveryError("linked project adapter")
        if path.is_file():
            keys.add(path.relative_to(root).as_posix())
    return keys | (_EXPANDED if expanded else set())


def prepare_transition(
    delivery: Any, run_dir: Path, target_archive: Path
) -> dict[str, Any]:
    root = Path(delivery.REPO_ROOT)
    if (root / ".changerail/source-link.json").exists():
        raise DeliveryError("installed restoration does not adopt shared source")
    lock_raw = _read(root, dist.LOCK)
    lock = json.loads(lock_raw)
    compatibility = installed_compatibility.require_reviewed_payload(lock)
    lineage = _lineage(delivery, run_dir)
    inventory = dist.run_inventory(root)
    names = {(path / "run.json").relative_to(root).as_posix() for path in lineage}
    retained = lock.get("retained_read_only_runs")
    if not isinstance(retained, dict) or names & retained.keys():
        raise DeliveryError("read-only installed lineage cannot be restored")
    if set(inventory) - retained.keys() != names:
        raise DeliveryError("unrelated frozen run blocks installed restoration")
    if any(inventory.get(name) != value for name, value in retained.items()):
        raise DeliveryError("retained read-only history changed")
    files = lock.get("files", {})
    if not files or dist.digest(dist.encoded(files)) != lock.get("payload_sha256"):
        raise DeliveryError("installed lock lacks complete payload proof")
    for name, expected in files.items():
        dist.allowed_payload(name)
        if dist.entry(dist.read_file(root, name)) != expected:
            raise DeliveryError(f"installed source has local drift: {name}")
    for directory in _RUNTIME_PREFIXES:
        for path in (root / directory).rglob("*"):
            if path.is_symlink():
                raise DeliveryError("linked installed runtime")
            if (
                path.is_file()
                and "__pycache__" not in path.parts
                and path.relative_to(root).as_posix() not in files
            ):
                raise DeliveryError("unowned installed runtime file")
    launcher = (
        delivery.profile()
        .get("adapters", {})
        .get("codex", {})
        .get("launcher", "bin/codex")
    )
    keys = _identity_keys(
        root,
        files,
        launcher,
        expanded=compatibility["identity_shape"] == "installed-expanded",
    )
    before = {name: dist.digest(_read(root, name)) for name in sorted(keys)}
    for path in lineage:
        metadata = json.loads(
            _read(root, (path / "run.json").relative_to(root).as_posix())
        )
        if metadata.get("process_identity") != before:
            raise DeliveryError(
                "installed predecessor identity differs from frozen lock/profile/launcher"
            )
    manifest, payload = dist.inspect_archive(target_archive)
    if manifest.get("execution_contract") != "changerail.native.v1":
        raise DeliveryError("incompatible target native execution contract")
    # The coordinator must be exactly the target tool, never an arbitrary archive.
    source = Path(__file__).resolve().parents[2]
    _config, executing = dist.source_payload(source)
    if {name: dist.entry(value) for name, value in executing.items()} != manifest[
        "files"
    ]:
        raise DeliveryError(
            "target archive differs from the executing restoration runtime"
        )
    new_lock = {
        "schema": "changerail.installation.v1",
        "version": manifest["version"],
        "execution_contract": manifest["execution_contract"],
        "archive_sha256": dist.digest(target_archive.read_bytes()),
        "payload_sha256": manifest["payload_sha256"],
        "provenance": manifest["provenance"],
        "files": manifest["files"],
        "retained_read_only_runs": retained,
    }
    after_keys = _identity_keys(root, manifest["files"], launcher, expanded=True)
    after = {
        name: dist.digest(dist.encoded(new_lock))
        if name == dist.LOCK
        else dist.digest(payload[name][0])
        if name in payload
        else dist.digest(_read(root, name))
        for name in sorted(after_keys)
    }
    settings = {
        name: dist.entry(dist.read_file(root, name))
        for name in keys - files.keys() - {dist.LOCK}
    }
    return {
        "schema": SCHEMA,
        "target": str(root),
        "run_id": run_dir.name,
        "archive": str(target_archive.absolute()),
        "archive_sha256": new_lock["archive_sha256"],
        "compatibility": compatibility,
        "before_lock": lock,
        "before_lock_sha256": dist.digest(lock_raw),
        "after_lock": new_lock,
        "before_identity": before,
        "after_identity": after,
        "settings": settings,
        "runs": inventory,
        "history": _history(root, lineage),
    }


def apply_transition(
    delivery: Any, proposal: dict[str, Any], transition_root: Path
) -> dict[str, Any]:
    if proposal.get("schema") != SCHEMA or proposal.get("target") != str(
        delivery.REPO_ROOT
    ):
        raise DeliveryError("foreign installed restoration proposal")
    if proposal.get(
        "compatibility"
    ) != installed_compatibility.require_reviewed_payload(proposal["before_lock"]):
        raise DeliveryError("installed restoration compatibility changed")
    lineage = _lineage(
        delivery,
        Path(delivery.REPO_ROOT) / ".runtime/changerail/runs" / proposal["run_id"],
    )
    if _history(Path(delivery.REPO_ROOT), lineage) != proposal["history"]:
        raise DeliveryError("installed predecessor history inventory changed")
    if not (transition_root / "runtime-intent.json").exists():
        if (
            prepare_transition(delivery, lineage[0], Path(proposal["archive"]))
            != proposal
        ):
            raise DeliveryError(
                "installed restoration proposal no longer matches verified inputs"
            )
    return dist.install_restoration_locked(
        Path(delivery.REPO_ROOT), proposal, transition_root
    )


def effective_identity(
    delivery: Any, proposal: dict[str, Any], transition_root: Path
) -> dict[str, str]:
    if proposal.get(
        "compatibility"
    ) != installed_compatibility.require_reviewed_payload(proposal["before_lock"]):
        raise DeliveryError("installed restoration compatibility changed")
    root = Path(delivery.REPO_ROOT)
    receipt = json.loads(
        _read(
            root,
            (transition_root / "runtime-applied.json").relative_to(root).as_posix(),
        )
    )
    if receipt != {
        "schema": SCHEMA,
        "proposal_sha256": dist.digest(dist.encoded(proposal)),
        "identity": proposal["after_identity"],
    }:
        raise DeliveryError("installed restoration receipt changed")
    lineage = _lineage(delivery, root / ".runtime/changerail/runs" / proposal["run_id"])
    if _history(root, lineage) != proposal["history"]:
        raise DeliveryError("installed predecessor history inventory changed")
    for name, expected in proposal["history"].items():
        if dist.entry(dist.read_file(root, name)) != expected:
            raise DeliveryError("installed predecessor history changed")
    if delivery.execution_identity() != proposal["after_identity"]:
        raise DeliveryError("installed restoration effective identity changed")
    return proposal["after_identity"]
