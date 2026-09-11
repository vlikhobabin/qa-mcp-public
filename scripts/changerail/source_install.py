"""Transactional attachment of an explicitly inventoried consumer to shared source."""

from __future__ import annotations

import json
import os
import subprocess
import uuid
from pathlib import Path
from typing import Any

from scripts.changerail.source_binding import BINDING, SCHEMA, recovery_binding


def mappings(source: Path, development: bool) -> dict[str, str]:
    import distribution as dist

    _config, payload = dist.source_payload(source)
    grouped = [
        "scripts/changerail",
        "tools/changerail/schemas",
        "tools/changerail/skills",
        "tools/changerail/templates",
    ]
    result = {name: name for name in grouped}
    for name in payload:
        if not any(name.startswith(directory + "/") for directory in grouped):
            result[name] = name
    if development:
        result.update(
            {
                "tools/changerail/tests": "tools/changerail/tests",
                "bin/test-changerail": "bin/test-changerail",
                "tools/openspec/test-wrapper.mjs": "tools/openspec/test-wrapper.mjs",
            }
        )
    return dict(sorted(result.items()))


def inventory(source: Path, target: Path, development: bool) -> dict[str, Any]:
    import distribution as dist

    source, target = source.resolve(strict=True), dist.git_root(target)
    if source == target:
        raise dist.DistributionError("cannot attach source to itself")
    links = mappings(source, development)
    source_files = {}
    previous = {}
    for local, relative in links.items():
        src = dist.confined(source, relative)
        if not src.exists():
            raise dist.DistributionError(f"missing shared source entry: {relative}")
        files = src.rglob("*") if src.is_dir() else [src]
        for path in files:
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            if path.is_file() or path.is_symlink():
                name = path.relative_to(source).as_posix()
                source_files[name] = dist.entry(dist.read_file(source, name))
        dst = dist.confined(target, local)
        files = dst.rglob("*") if dst.is_dir() else [dst]
        for path in files:
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            if path.is_file() or path.is_symlink():
                name = path.relative_to(target).as_posix()
                previous[name] = dist.entry(dist.read_file(target, name))
    lock_path = dist.confined(target, dist.LOCK)
    lock = (
        json.loads(dist.read_file(target, dist.LOCK)[0]) if lock_path.exists() else None
    )
    retained = dist.run_inventory(target)
    if lock:
        for name, expected in lock.get("retained_read_only_runs", {}).items():
            if retained.get(name) != expected:
                raise dist.DistributionError(f"retained historical run changed: {name}")
        for name, expected in lock["files"].items():
            if dist.entry(dist.read_file(target, name)) != expected:
                raise dist.DistributionError(
                    f"installed source has local drift: {name}"
                )
    return {
        "schema": "changerail.source-adoption.v1",
        "source_root": str(source),
        "project_root": str(target),
        "development": development,
        "mappings": links,
        "source_files": source_files,
        "previous_files": previous,
        "previous_lock_sha256": dist.digest(dist.read_file(target, dist.LOCK)[0])
        if lock
        else None,
        "retained_runs": retained,
    }


def attach(
    source: Path,
    target: Path,
    *,
    development: bool = False,
    adoption: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    import distribution as dist

    target = dist.git_root(target)
    # Match copy-install's Git ignore contract before even creating delivery.lock.
    backup_rel = ".runtime/changerail/source-bindings/" + uuid.uuid4().hex
    for relative in (".runtime/changerail/delivery.lock", backup_rel + "/audit.json"):
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", "--", relative],
            cwd=target,
            capture_output=True,
            check=False,
        )
        if ignored.returncode:
            raise dist.DistributionError(
                "consumer must ignore .runtime/ before attachment"
            )
    with dist.delivery_lock(target):
        if (target / BINDING).exists() or (target / BINDING).is_symlink():
            raise dist.DistributionError(
                "consumer already has a shared-source binding; detach first"
            )
        current = inventory(source, target, development)
        if adoption is None and (current["previous_files"] or current["retained_runs"]):
            raise dist.DistributionError(
                "existing consumer requires exact attach-inventory --adoption"
            )
        if adoption is not None and json.loads(adoption.read_bytes()) != current:
            raise dist.DistributionError(
                "source, consumer or history changed since attach inventory"
            )
        report = {
            "schema": SCHEMA,
            "source_root": current["source_root"],
            "project_root": str(target),
            "development": development,
            "mappings": current["mappings"],
            "dry_run": dry_run,
        }
        if dry_run:
            return report
        backup = dist.confined(target, backup_rel)
        backup.mkdir(parents=True)
        dist.write_atomic(backup / "inventory.json", dist.encoded(current))
        old_lock = (
            dist.read_file(target, dist.LOCK) if (target / dist.LOCK).exists() else None
        )
        if old_lock:
            dist.write_atomic(backup / "previous-lock.json", old_lock[0], old_lock[1])
        applied = []
        try:
            for local, relative in current["mappings"].items():
                dst = dist.confined(target, local)
                saved = backup / "before" / local
                saved.parent.mkdir(parents=True, exist_ok=True)
                had_previous = dst.exists()
                if had_previous:
                    os.replace(dst, saved)
                applied.append((local, had_previous))
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.symlink_to(
                    Path(current["source_root"]) / relative,
                    target_is_directory=(
                        Path(current["source_root"]) / relative
                    ).is_dir(),
                )
            # Exact previous execution records remain read-only after changing process identity.
            lock = (
                json.loads(old_lock[0])
                if old_lock
                else {"schema": "changerail.installation.v1", "files": {}}
            )
            lock["retained_read_only_runs"] = current["retained_runs"]
            dist.write_atomic(target / dist.LOCK, dist.encoded(lock))
            report.update(
                backup=backup_rel,
                source_files=current["source_files"],
                inventory_sha256=dist.digest(dist.encoded(current)),
            )
            dist.write_atomic(target / BINDING, dist.encoded(report))
            dist.write_atomic(
                backup / "audit.json", dist.encoded({"state": "attached", **report})
            )
        except BaseException:
            (target / BINDING).unlink(missing_ok=True)
            for local, had_previous in reversed(applied):
                dst = target / local
                if dst.is_symlink():
                    dst.unlink()
                if had_previous:
                    os.replace(backup / "before" / local, dst)
            if old_lock:
                dist.write_atomic(target / dist.LOCK, old_lock[0], old_lock[1])
            else:
                (target / dist.LOCK).unlink(missing_ok=True)
            dist.write_atomic(
                backup / "audit.json", dist.encoded({"state": "rolled-back"})
            )
            raise
        return report


def detach(target: Path, *, dry_run: bool = False) -> dict[str, Any]:
    """Restore the exact pre-attachment consumer, retaining all source edits."""
    import distribution as dist

    target = dist.git_root(target)
    with dist.delivery_lock(target):
        value = recovery_binding(target)
        if value is None:
            raise dist.DistributionError("consumer has no shared-source binding")
        backup_name = dist.safe_name(value["backup"])
        if (
            not backup_name.startswith(".runtime/changerail/source-bindings/")
            or len(Path(backup_name).parts) != 4
        ):
            raise dist.DistributionError("invalid attachment backup path")
        backup = dist.confined(target, backup_name)
        inventory_bytes = dist.read_file(backup, "inventory.json")[0]
        previous = json.loads(inventory_bytes)
        audit = json.loads(dist.read_file(backup, "audit.json")[0])
        if audit != {"state": "attached", **value}:
            raise dist.DistributionError("attachment audit changed")
        if (
            previous.get("schema") != "changerail.source-adoption.v1"
            or any(
                previous.get(key) != value[key]
                for key in (
                    "source_root",
                    "project_root",
                    "development",
                    "mappings",
                    "source_files",
                )
            )
            or (
                "inventory_sha256" in value
                and dist.digest(inventory_bytes) != value["inventory_sha256"]
            )
        ):
            raise dist.DistributionError("attachment backup inventory changed")
        if dist.run_inventory(target) != previous["retained_runs"]:
            raise dist.DistributionError(
                "runs changed since attach; detach requires reconciliation"
            )
        observed = {}
        before = dist.confined(backup, "before")
        for path in before.rglob("*"):
            if path.is_symlink():
                raise dist.DistributionError("attachment backup contains a link")
            if (
                path.is_file()
                and "__pycache__" not in path.parts
                and path.suffix != ".pyc"
            ):
                name = path.relative_to(backup / "before").as_posix()
                observed[name] = dist.entry(dist.read_file(backup, "before/" + name))
        if observed != previous["previous_files"]:
            raise dist.DistributionError("attachment backup inventory changed")
        prior_lock = None
        if previous["previous_lock_sha256"] is not None:
            prior_lock = dist.read_file(backup, "previous-lock.json")
            if dist.digest(prior_lock[0]) != previous["previous_lock_sha256"]:
                raise dist.DistributionError("attachment previous lock changed")
        elif (backup / "previous-lock.json").exists() or (
            backup / "previous-lock.json"
        ).is_symlink():
            raise dist.DistributionError("unexpected attachment previous lock")
        for name, expected in previous["previous_files"].items():
            if dist.entry(dist.read_file(backup, "before/" + name)) != expected:
                raise dist.DistributionError("attachment backup changed")
        report = {"state": "detached", "project_root": str(target), "dry_run": dry_run}
        if dry_run:
            return report
        # Prevalidate all saved bytes before touching any link; record each step for rollback.
        restored = []
        current_lock = dist.read_file(target, dist.LOCK)
        current_binding = dist.read_file(target, BINDING)
        try:
            for local in value["mappings"]:
                dst = target / local
                saved = backup / "before" / local
                dst.unlink()
                restored.append(local)
                if saved.exists():
                    os.replace(saved, dst)
            if prior_lock is not None:
                dist.write_atomic(target / dist.LOCK, prior_lock[0], prior_lock[1])
            else:
                (target / dist.LOCK).unlink(missing_ok=True)
            (target / BINDING).unlink()
        except BaseException:
            for local in reversed(restored):
                dst = target / local
                saved = backup / "before" / local
                if dst.exists() and not dst.is_symlink():
                    os.replace(dst, saved)
                dst.symlink_to(Path(value["source_root"]) / value["mappings"][local])
            dist.write_atomic(target / dist.LOCK, current_lock[0], current_lock[1])
            dist.write_atomic(target / BINDING, current_binding[0], current_binding[1])
            raise
        dist.write_atomic(backup / "detach.json", dist.encoded(report))
        return report
