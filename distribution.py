"""Deterministic native runtime distribution and hash-bound local installation."""

from __future__ import annotations

import argparse
import fcntl
import gzip
import hashlib
import io
import json
import os
import stat
import subprocess
import sys
import tarfile
import tempfile
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, Iterator

SCHEMA = "changerail.distribution.v1"
LOCK = ".changerail/distribution-lock.json"
MANIFEST = "DISTRIBUTION-MANIFEST.json"
MAX_FILE = 32 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
MAX_FILES = 3000
ROOT = Path(__file__).resolve().parent


class DistributionError(ValueError):
    """A source, artifact, or consumer failed an installation boundary."""


def encoded(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_name(name: str) -> str:
    if (
        not isinstance(name, str)
        or not name
        or "\\" in name
        or PurePosixPath(name).is_absolute()
        or any(part in {"", ".", ".."} for part in name.split("/"))
        or any(ord(char) < 32 for char in name)
    ):
        raise DistributionError(f"unsafe path: {name!r}")
    return name


def confined(root: Path, name: str) -> Path:
    path = root
    for part in safe_name(name).split("/"):
        path /= part
        if path.is_symlink():
            raise DistributionError(f"symlink refused: {name}")
    return path


def read_file(root: Path, name: str) -> tuple[bytes, int]:
    path = confined(root, name)
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_FILE:
            raise DistributionError(f"not a bounded regular file: {name}")
        data = stream.read(MAX_FILE + 1)
        if len(data) != info.st_size:
            raise DistributionError(f"source changed while reading: {name}")
    return data, 0o755 if info.st_mode & 0o111 else 0o644


def entry(payload: tuple[bytes, int]) -> dict[str, Any]:
    data, mode = payload
    return {"sha256": digest(data), "size": len(data), "mode": mode}


def allowed_payload(name: str) -> None:
    safe_name(name)
    parts = PurePosixPath(name).parts
    if any(
        part in {".runtime", ".git", ".codex", "node_modules", "__pycache__"}
        or part.startswith(".env")
        for part in parts
    ):
        raise DistributionError(f"private or generated payload path: {name}")
    if not (
        name
        in {
            "distribution.py",
            "distribution.json",
            "DISTRIBUTION.md",
            "scripts/__init__.py",
            "bin/chrl",
            "bin/chrl-run",
            "bin/chrl-dist",
            "bin/test-changerail",
            "bin/openspec",
        }
        or name.startswith(
            ("scripts/changerail/", "tools/changerail/", "tools/openspec/")
        )
    ):
        raise DistributionError(f"path outside distribution ownership: {name}")


def source_payload(root: Path) -> tuple[dict[str, Any], dict[str, tuple[bytes, int]]]:
    config = json.loads(read_file(root, "distribution.json")[0])
    if config.get("schema") != "changerail.distribution-config.v1":
        raise DistributionError("unsupported distribution configuration")
    names = set(config["files"])
    for directory, pattern in config["trees"].items():
        location = confined(root, directory)
        if not location.is_dir():
            raise DistributionError(f"missing source tree: {directory}")
        for path in location.rglob("*"):
            if path.is_symlink():
                raise DistributionError(f"symlink in source tree: {directory}")
        names.update(
            path.relative_to(root).as_posix() for path in location.glob(pattern)
        )
    if len(names) > MAX_FILES:
        raise DistributionError("too many payload files")
    for name in names:
        allowed_payload(name)
    payload = {name: read_file(root, name) for name in sorted(names)}
    if sum(len(data) for data, _mode in payload.values()) > MAX_TOTAL:
        raise DistributionError("payload exceeds size limit")
    return config, payload


def build(root: Path, output: Path) -> dict[str, Any]:
    config, payload = source_payload(root)
    entries = {name: entry(value) for name, value in payload.items()}
    manifest = {
        "schema": SCHEMA,
        "version": config["version"],
        "execution_contract": config["execution_contract"],
        "provenance": config["provenance"],
        "files": entries,
        "payload_sha256": digest(encoded(entries)),
    }
    payload[MANIFEST] = (encoded(manifest), 0o644)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
            with tarfile.open(
                fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT
            ) as archive:
                for name, (data, mode) in sorted(payload.items()):
                    member = tarfile.TarInfo(name)
                    member.size, member.mode, member.mtime = len(data), mode, 0
                    archive.addfile(member, io.BytesIO(data))
    return {"archive": str(output), "sha256": digest(output.read_bytes()), **manifest}


def inspect_archive(
    archive_path: Path,
) -> tuple[dict[str, Any], dict[str, tuple[bytes, int]]]:
    payload: dict[str, tuple[bytes, int]] = {}
    total = 0
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive:
            name = safe_name(member.name)
            if (
                name in payload
                or not member.isfile()
                or member.size > MAX_FILE
                or member.size < 0
            ):
                raise DistributionError(f"unsafe archive member: {name}")
            if member.mode not in {0o644, 0o755}:
                raise DistributionError(f"unsafe file mode: {name}")
            total += member.size
            if total > MAX_TOTAL or len(payload) >= MAX_FILES + 1:
                raise DistributionError("archive exceeds limits")
            stream = archive.extractfile(member)
            if stream is None:
                raise DistributionError(f"unreadable member: {name}")
            data = stream.read(MAX_FILE + 1)
            if len(data) != member.size:
                raise DistributionError(f"truncated member: {name}")
            payload[name] = (data, member.mode)
    if MANIFEST not in payload:
        raise DistributionError("missing distribution manifest")
    manifest = json.loads(payload.pop(MANIFEST)[0])
    if manifest.get("schema") != SCHEMA:
        raise DistributionError("unsupported manifest schema")
    for name in payload:
        allowed_payload(name)
    actual = {name: entry(value) for name, value in sorted(payload.items())}
    if actual != manifest.get("files") or digest(encoded(actual)) != manifest.get(
        "payload_sha256"
    ):
        raise DistributionError("archive hashes or inventory do not match manifest")
    return manifest, payload


def git_root(root: Path) -> Path:
    root = root.resolve()
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode or Path(result.stdout.strip()).resolve() != root:
        raise DistributionError("target must be a Git repository root")
    return root


def run_inventory(root: Path) -> dict[str, dict[str, Any]]:
    result = {}
    total = 0
    for tree in ("runs", "delivery-runs", "ff-runs", "offline-finalizations"):
        runtime = confined(root, f".runtime/changerail/{tree}")
        if not runtime.exists():
            continue
        for path in sorted(runtime.glob("*/run.json")):
            if len(result) >= MAX_FILES:
                raise DistributionError("too many retained runs")
            name = path.relative_to(root).as_posix()
            data, mode = read_file(root, name)
            total += len(data)
            if total > MAX_TOTAL:
                raise DistributionError("retained run inventory exceeds size limit")
            run = json.loads(data)
            result[name] = {
                **entry((data, mode)),
                "execution_contract": run.get("execution_contract"),
            }
    return result


def adoption_inventory(
    root: Path, archive: Path, paths: list[str], *, retain_history: bool = False
) -> dict[str, Any]:
    root = git_root(root)
    manifest, _payload = inspect_archive(archive)
    if confined(root, LOCK).exists():
        raise DistributionError("installed consumer must use ordinary update")
    entries = {}
    for name in sorted(set(paths)):
        # Legacy removal is explicit and hash-bound; never accept configuration,
        # credentials, runtime state, or product source as predecessor ownership.
        safe_name(name)
        if not (
            name.startswith(("scripts/changerail/", "tools/changerail/"))
            or name
            in {
                "scripts/__init__.py",
                "bin/chrl",
                "bin/chrl-run",
                "bin/chrl-ff",
                "bin/chrl-kit",
                "bin/test-changerail",
                "bin/openspec",
                "bin/board-do",
                "bin/board-ff",
                "scripts/board-lib.sh",
                "tests/test_board_helpers.py",
                "tests/test_native_openspec_integration.py",
                "tests/test_native_openspec_lifecycle.py",
            }
            or name.startswith("tools/openspec/")
            or (
                name.startswith("tests/test_")
                and "changerail" in name
                and name.endswith(".py")
            )
        ):
            raise DistributionError(f"not an eligible predecessor path: {name}")
        if any(
            part in {"node_modules", "__pycache__"} or part.startswith(".env")
            for part in PurePosixPath(name).parts
        ):
            raise DistributionError(f"generated predecessor path: {name}")
        entries[name] = entry(read_file(root, name))
    return {
        "schema": "changerail.adoption.v1",
        "target": str(root),
        "candidate_sha256": digest(archive.read_bytes()),
        "payload_sha256": manifest["payload_sha256"],
        "files": entries,
        "retained_read_only_runs": run_inventory(root) if retain_history else {},
    }


def write_atomic(path: Path, data: bytes, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".chrl-dist-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def history_inventory(root: Path, archive: Path) -> dict[str, Any]:
    """Bind explicit retirement of frozen runs to one installed and incoming kit."""
    root = git_root(root)
    inspect_archive(archive)
    lock_data = read_file(root, LOCK)[0]
    if json.loads(lock_data).get("schema") != "changerail.installation.v1":
        raise DistributionError("history retention requires an installed distribution")
    return {
        "schema": "changerail.update-history.v1",
        "target": str(root),
        "candidate_sha256": digest(archive.read_bytes()),
        "installed_lock_sha256": digest(lock_data),
        "retained_read_only_runs": run_inventory(root),
    }


@contextmanager
def delivery_lock(root: Path) -> Iterator[None]:
    """Use the runner's exact lock, also serializing competing installers."""
    path = confined(root, ".runtime/changerail/delivery.lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600
    )
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise DistributionError("delivery lock is not a regular file")
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise DistributionError(
                "delivery writer or another installer holds delivery.lock"
            ) from exc
        restorations = confined(root, ".runtime/changerail/plan-restorations")
        if restorations.exists():
            for transition in restorations.iterdir():
                relative = transition.relative_to(root).as_posix()
                intent = confined(root, relative + "/apply-intent.json")
                applied = confined(root, relative + "/applied.json")
                if intent.exists() and not applied.exists():
                    raise DistributionError(
                        "pending plan restoration requires its exact apply reconciliation"
                    )
        yield
    finally:
        os.close(descriptor)


def install(
    root: Path,
    archive: Path,
    *,
    adoption: Path | None = None,
    history: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    root = git_root(root)
    if (root / ".changerail/source-link.json").exists() or (
        root / ".changerail/source-link.json"
    ).is_symlink():
        raise DistributionError(
            "shared-source consumer must detach before copy installation"
        )
    with delivery_lock(root):
        return _install_locked(
            root, archive, adoption=adoption, history=history, dry_run=dry_run
        )


def _install_locked(
    root: Path,
    archive: Path,
    *,
    adoption: Path | None,
    history: Path | None,
    dry_run: bool,
) -> dict[str, Any]:
    root = git_root(root)
    manifest, payload = inspect_archive(archive)
    archive_hash = digest(archive.read_bytes())
    lock_path = confined(root, LOCK)
    old_lock = json.loads(read_file(root, LOCK)[0]) if lock_path.exists() else None
    if old_lock is not None and old_lock.get("schema") != "changerail.installation.v1":
        raise DistributionError("unsupported installed lock")
    predecessor: dict[str, Any] = {}
    retained = old_lock.get("retained_read_only_runs", {}) if old_lock else {}
    if history is not None:
        if old_lock is None or adoption is not None:
            raise DistributionError(
                "update history requires an existing installation without adoption"
            )
        history_document = json.loads(history.read_bytes())
        if history_document != history_inventory(root, archive):
            raise DistributionError(
                "history allowance does not bind the current runs, lock and candidate"
            )
        additional = history_document["retained_read_only_runs"]
        if any(additional.get(name) != value for name, value in retained.items()):
            raise DistributionError("previously retained history changed")
        retained = additional
    if adoption is not None:
        if old_lock:
            raise DistributionError(
                "adoption is only allowed before the first installation"
            )
        document = json.loads(adoption.read_bytes())
        if (
            document.get("schema") != "changerail.adoption.v1"
            or document.get("target") != str(root)
            or document.get("candidate_sha256") != archive_hash
            or document.get("payload_sha256") != manifest["payload_sha256"]
        ):
            raise DistributionError("adoption does not bind this target and candidate")
        predecessor = document["files"]
        # Revalidate ownership rather than trusting a hand-edited adoption file.
        validated = adoption_inventory(
            root, archive, list(predecessor), retain_history=False
        )
        if predecessor != validated["files"]:
            raise DistributionError("predecessor has local drift")
        retained = document.get("retained_read_only_runs", {})
    owned = old_lock["files"] if old_lock else predecessor
    for name, expected in owned.items():
        if old_lock:
            allowed_payload(name)
        if entry(read_file(root, name)) != expected:
            raise DistributionError(f"installed source has local drift: {name}")
    for name, value in payload.items():
        path = confined(root, name)
        if (
            path.exists()
            and name not in owned
            and entry(read_file(root, name)) != entry(value)
        ):
            raise DistributionError(f"unowned file would be overwritten: {name}")
    changed = (
        old_lock is None or old_lock.get("payload_sha256") != manifest["payload_sha256"]
    )
    runs = run_inventory(root)
    for name, recorded in retained.items():
        if runs.get(name) != recorded:
            raise DistributionError(f"retained historical run changed: {name}")
    for name, recorded in runs.items():
        if name in retained:
            continue
        # A contract marker alone cannot prove frozen process compatibility.
        # Updates with any non-retained run require an exact current payload.
        if changed or recorded["execution_contract"] != manifest["execution_contract"]:
            raise DistributionError(
                f"frozen run blocks source replacement: {name}; retain its exact snapshot explicitly during adoption"
            )
    removed = sorted(set(owned) - set(payload))
    replaced = sorted(
        name
        for name, value in payload.items()
        if confined(root, name).exists()
        and entry(read_file(root, name)) != entry(value)
    )
    created = sorted(name for name in payload if not confined(root, name).exists())
    report = {
        "schema": "changerail.install-report.v1",
        "version": manifest["version"],
        "archive_sha256": archive_hash,
        "payload_sha256": manifest["payload_sha256"],
        "created": created,
        "replaced": replaced,
        "removed": removed,
        "retained_read_only_runs": sorted(retained),
        "dry_run": dry_run,
    }
    if dry_run or (
        not removed
        and not replaced
        and not created
        and old_lock is not None
        and retained == old_lock.get("retained_read_only_runs", {})
    ):
        return report
    # Backups are mandatory and ignored even in a previously empty consumer.
    backup_name = f".runtime/changerail/distribution/{archive_hash}"
    backup = confined(root, backup_name)
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", "--", backup_name + "/audit.json"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if ignored.returncode:
        raise DistributionError("consumer must ignore .runtime/ before installation")
    if backup.exists():
        raise DistributionError(
            "a previous installation attempt already owns this audit directory"
        )
    backup.mkdir(parents=True)
    for name in sorted(set(removed + replaced)):
        data, mode = read_file(root, name)
        write_atomic(confined(backup, "before/" + name), data, mode)
    if old_lock:
        write_atomic(backup / "previous-lock.json", encoded(old_lock))
    if adoption:
        write_atomic(backup / "adoption.json", adoption.read_bytes())
    if history:
        write_atomic(backup / "history.json", history.read_bytes())
    write_atomic(backup / "audit.json", encoded({**report, "state": "prepared"}))
    lock = {
        "schema": "changerail.installation.v1",
        "version": manifest["version"],
        "execution_contract": manifest["execution_contract"],
        "archive_sha256": archive_hash,
        "payload_sha256": manifest["payload_sha256"],
        "provenance": manifest["provenance"],
        "files": manifest["files"],
        "retained_read_only_runs": retained,
    }
    original_lock = read_file(root, LOCK) if old_lock else None
    try:
        for name in sorted(set(created + replaced)):
            data, mode = payload[name]
            write_atomic(confined(root, name), data, mode)
        for name in removed:
            confined(root, name).unlink()
        write_atomic(lock_path, encoded(lock))
        write_atomic(backup / "audit.json", encoded({**report, "state": "installed"}))
    except BaseException as failure:
        rollback_errors = []
        for name in sorted(set(removed + replaced)):
            try:
                data, mode = read_file(backup, "before/" + name)
                write_atomic(confined(root, name), data, mode)
            except OSError as exc:
                rollback_errors.append(f"{name}: {exc}")
        for name in created:
            try:
                confined(root, name).unlink(missing_ok=True)
            except OSError as exc:
                rollback_errors.append(f"{name}: {exc}")
        try:
            if original_lock:
                write_atomic(lock_path, *original_lock)
            else:
                lock_path.unlink(missing_ok=True)
        except OSError as exc:
            rollback_errors.append(f"{LOCK}: {exc}")
        write_atomic(
            backup / "audit.json",
            encoded(
                {
                    **report,
                    "state": "rollback_failed" if rollback_errors else "rolled_back",
                    "failure": str(failure),
                    "rollback_errors": rollback_errors,
                }
            ),
        )
        if rollback_errors:
            raise DistributionError(
                "installation failed; rollback incomplete; inspect retained audit and backup"
            ) from failure
        raise DistributionError(
            "installation failed and previous bytes were restored; inspect retained audit"
        ) from failure
    return report


def install_restoration_locked(
    root: Path, proposal: dict[str, Any], transition_root: Path
) -> dict[str, Any]:
    """Resume an exact restoration install; caller owns lock and plan authority.

    Ordinary installation remains closed to frozen runs. An intent allows
    only old/target file states after interruption, never arbitrary drift.
    """

    def sync_directory(path: Path) -> None:
        descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    root = git_root(root)
    relative = transition_root.relative_to(root).as_posix()
    if (
        confined(root, relative) != transition_root
        or transition_root.parent != root / ".runtime/changerail/plan-restorations"
        or proposal.get("schema") != "changerail.installed-restoration.v1"
        or proposal.get("target") != str(root)
    ):
        raise DistributionError("unsafe restoration installation owner")
    # Only the separately authorized plan operation may use this entry point.
    parent_raw = read_file(transition_root, "proposal.json")[0]
    parent = json.loads(parent_raw)
    authority = json.loads(read_file(transition_root, "apply-intent.json")[0])
    if (
        parent.get("schema") != "changerail.plan-restoration.v1"
        or authority.get("schema") != "changerail.plan-restoration.v1"
        or parent.get("runtime_transition") != proposal
        or parent.get("project") != str(root)
        or parent.get("run_id") != proposal.get("run_id")
        or authority.get("proposal_sha256") != digest(parent_raw)
        or authority.get("authorized") != digest(parent_raw)
    ):
        raise DistributionError("restoration installation lacks exact plan authority")
    archive = Path(proposal["archive"])
    manifest, payload = inspect_archive(archive)
    if (
        digest(archive.read_bytes()) != proposal["archive_sha256"]
        or manifest["files"] != proposal["after_lock"]["files"]
    ):
        raise DistributionError("restoration target archive changed")
    before_lock, after_lock = proposal["before_lock"], proposal["after_lock"]
    if before_lock["retained_read_only_runs"] != after_lock["retained_read_only_runs"]:
        raise DistributionError("restoration cannot remove read-only history")
    if run_inventory(root) != proposal["runs"]:
        raise DistributionError("restoration frozen run inventory changed")
    for name, expected in {**proposal["history"], **proposal["settings"]}.items():
        if entry(read_file(root, name)) != expected:
            raise DistributionError(
                f"restoration history or project setting changed: {name}"
            )
    proof = {
        "schema": proposal["schema"],
        "proposal_sha256": digest(encoded(proposal)),
        "identity": proposal["after_identity"],
    }
    intent_path = confined(transition_root, "runtime-intent.json")
    applied_path = confined(transition_root, "runtime-applied.json")
    interrupted = intent_path.exists()
    if interrupted and read_file(transition_root, "runtime-intent.json")[0] != encoded(
        proof
    ):
        raise DistributionError("restoration installation intent changed")
    if applied_path.exists() and (
        not interrupted
        or read_file(transition_root, "runtime-applied.json")[0] != encoded(proof)
    ):
        raise DistributionError("restoration installation receipt changed")
    old, new = before_lock["files"], manifest["files"]
    all_names = sorted(old.keys() | new.keys())
    for name in all_names:
        allowed_payload(name)
        path = confined(root, name)
        actual = entry(read_file(root, name)) if path.exists() else None
        expected = (old.get(name), new.get(name)) if interrupted else (old.get(name),)
        if actual not in expected:
            raise DistributionError(f"restoration runtime has unexpected bytes: {name}")
    actual_lock = read_file(root, LOCK)[0]
    old_bytes, new_bytes = encoded(before_lock), encoded(after_lock)
    if digest(old_bytes) != proposal["before_lock_sha256"] or actual_lock not in (
        (old_bytes, new_bytes) if interrupted else (old_bytes,)
    ):
        raise DistributionError("restoration installation lock changed")
    if applied_path.exists():
        if (
            actual_lock != new_bytes
            or any(
                entry(read_file(root, name)) != expected
                for name, expected in new.items()
            )
            or any(confined(root, name).exists() for name in old.keys() - new.keys())
        ):
            raise DistributionError("applied restoration runtime changed")
        return proof
    if not interrupted:
        for name in all_names:
            if name in old:
                data, mode = read_file(root, name)
                write_atomic(
                    confined(transition_root, "runtime-before/" + name), data, mode
                )
        with intent_path.open("xb") as stream:
            stream.write(encoded(proof))
            stream.flush()
            os.fsync(stream.fileno())
    sync_directory(transition_root)
    for name in all_names:
        target = confined(root, name)
        if name in payload:
            data, mode = payload[name]
            if not target.exists() or entry(read_file(root, name)) != new[name]:
                write_atomic(target, data, mode)
        elif target.exists():
            target.unlink()
        if target.parent.exists():
            sync_directory(target.parent)
    write_atomic(confined(root, LOCK), new_bytes)
    sync_directory(root / ".changerail")
    with applied_path.open("xb") as stream:
        stream.write(encoded(proof))
        stream.flush()
        os.fsync(stream.fileno())
    sync_directory(transition_root)
    return proof


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    export = commands.add_parser("build")
    export.add_argument("output", type=Path)
    export.add_argument("--source", type=Path, default=ROOT)
    verify = commands.add_parser("verify")
    verify.add_argument("archive", type=Path)
    inventory = commands.add_parser(
        "inventory", help="prepare a reviewable exact predecessor allowance"
    )
    inventory.add_argument("archive", type=Path)
    inventory.add_argument("target", type=Path)
    inventory.add_argument("--paths-file", type=Path, required=True)
    inventory.add_argument("--retain-history-read-only", action="store_true")
    inventory.add_argument("--output", type=Path, required=True)
    retire = commands.add_parser(
        "history", help="explicitly retain installed runs as read-only for one update"
    )
    retire.add_argument("archive", type=Path)
    retire.add_argument("target", type=Path)
    retire.add_argument("--output", type=Path, required=True)
    apply = commands.add_parser("install")
    apply.add_argument("archive", type=Path)
    apply.add_argument("target", type=Path)
    apply.add_argument("--adoption", type=Path)
    apply.add_argument("--history", type=Path)
    apply.add_argument("--dry-run", action="store_true")
    source_inventory = commands.add_parser("attach-inventory")
    source_inventory.add_argument("target", type=Path)
    source_inventory.add_argument("--source", type=Path, default=ROOT)
    source_inventory.add_argument("--development", action="store_true")
    source_inventory.add_argument("--output", type=Path, required=True)
    link = commands.add_parser("attach")
    link.add_argument("target", type=Path)
    link.add_argument("--source", type=Path, default=ROOT)
    link.add_argument("--development", action="store_true")
    link.add_argument("--adoption", type=Path)
    link.add_argument("--dry-run", action="store_true")
    unlink = commands.add_parser("detach")
    unlink.add_argument("target", type=Path)
    unlink.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command in {"attach", "detach", "attach-inventory"}:
            from scripts.changerail import source_install

            if args.command == "attach-inventory":
                with delivery_lock(git_root(args.target)):
                    result = source_install.inventory(
                        args.source, args.target, args.development
                    )
                args.output.parent.mkdir(parents=True, exist_ok=True)
                with args.output.open("xb") as stream:
                    stream.write(encoded(result))
            elif args.command == "attach":
                result = source_install.attach(
                    args.source,
                    args.target,
                    development=args.development,
                    adoption=args.adoption,
                    dry_run=args.dry_run,
                )
            else:
                result = source_install.detach(args.target, dry_run=args.dry_run)
        elif args.command == "build":
            result = build(args.source.resolve(), args.output)
        elif args.command == "verify":
            result, _payload = inspect_archive(args.archive)
        elif args.command in {"inventory", "history"}:
            result = (
                history_inventory(args.target, args.archive)
                if args.command == "history"
                else adoption_inventory(
                    args.target,
                    args.archive,
                    args.paths_file.read_text().splitlines(),
                    retain_history=args.retain_history_read_only,
                )
            )
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("xb") as stream:
                stream.write(encoded(result))
        else:
            result = install(
                args.target,
                args.archive,
                adoption=args.adoption,
                history=args.history,
                dry_run=args.dry_run,
            )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (DistributionError, OSError, ValueError, KeyError, tarfile.TarError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.modules.setdefault("distribution", sys.modules[__name__])
    raise SystemExit(main())
