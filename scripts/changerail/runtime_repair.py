"""Explicit, receipt-proven source repair before any delivery proof is accepted.

This deliberately narrow boundary keeps all retained run metadata immutable. It
does not thaw historical runs, replay a completed checkpoint, reuse an old proof,
or add review/floor allowances. Later-stage repairs need a separate contract.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Sequence

from scripts.changerail import source_binding
from scripts.changerail.contracts import DeliveryError

SCHEMA = "changerail.runtime-repair.v1"


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write(path: Path, value: dict[str, Any]) -> None:
    with path.open("xb") as stream:
        stream.write((json.dumps(value, sort_keys=True, indent=2) + "\n").encode())
        stream.flush()
        os.fsync(stream.fileno())


def _code_key(key: str) -> bool:
    return key.startswith("scripts/changerail/") and key.endswith(".py")


def _changed(before: dict[str, str], after: dict[str, str]) -> list[str]:
    changed = sorted(
        key for key in before.keys() | after.keys() if before.get(key) != after.get(key)
    )
    if not changed or any(not _code_key(key) for key in changed):
        raise DeliveryError(
            "runtime repair permits Python core changes only; project, launcher, schemas and skills remain frozen"
        )
    return changed


def _root(delivery: Any, run_dir: Path) -> Path:
    run_dir = run_dir.absolute()
    if run_dir.resolve() != run_dir or run_dir.parent != delivery.RUNTIME_ROOT / "runs":
        raise DeliveryError(
            "runtime repair requires an exact local current run directory"
        )
    root = run_dir / "runtime-repairs"
    if root.is_symlink():
        raise DeliveryError("linked runtime repair directory")
    return root


def _run_snapshot(delivery: Any, run_dir: Path) -> dict[str, str]:
    return {
        path.relative_to(run_dir).as_posix(): _digest(
            delivery._check_bytes(path, 32 * 1024 * 1024)
        )
        for path in sorted(run_dir.rglob("*"))
        if "runtime-repairs" not in path.relative_to(run_dir).parts
        and (path.is_file() or path.is_symlink())
    }


def _boundary(delivery: Any, run_dir: Path) -> dict[str, Any]:
    metadata = delivery.require_current_execution(run_dir)
    if not metadata.get("finished_at") or metadata.get("recovery_of"):
        raise DeliveryError(
            "runtime repair requires a stopped original run, without recovery ancestry"
        )
    prohibited = (
        "reviews",
        "verification-attempts",
        "focused-evidence",
        "proof-index.json",
        "proof-records",
        "observed-proofs",
        "final-test-proof-inputs",
        "preverification",
        "preverification.json",
        "verification.json",
        "implementation-handoff.json",
        "native-archive.json",
        "native-archive-intent.json",
        "publication.json",
        "publication-journal.json",
    )
    if any(
        (run_dir / name).exists() or (run_dir / name).is_symlink()
        for name in prohibited
    ):
        raise DeliveryError(
            "runtime repair boundary is before evidence, handoff, review, archive or floor"
        )
    if any(delivery.review_budget_usage(run_dir).values()):
        raise DeliveryError("runtime repair cannot replenish consumed review allowance")
    for event in delivery.combined_change_events(run_dir):
        phase = str(event.get("phase", ""))
        if phase in {"review", "verify", "publish", "preverify"} or (
            phase.startswith("change-") and event.get("stage") == "complete"
        ):
            raise DeliveryError(
                "runtime repair cannot adopt accepted checkpoints or later stages"
            )
    manifest = delivery._check_json(run_dir / "manifest.json")
    if manifest.get("run_id") != run_dir.name or not manifest.get("path_fingerprints"):
        raise DeliveryError(
            "runtime repair requires the retained interrupted implementation payload"
        )
    card = delivery.resolve_deliverable_card(metadata["card"])
    ok, detail, current_manifest = delivery.recovery_source(
        card, delivery.changed_paths()
    )
    if not ok or not current_manifest or current_manifest.get("run_id") != run_dir.name:
        raise DeliveryError(
            "runtime repair requires an exact recoverable payload: " + detail
        )
    return metadata


def _proposal(delivery: Any, run_dir: Path, path: Path) -> dict[str, Any]:
    root = _root(delivery, run_dir)
    if (
        path.name != "proposal.json"
        or path.parent.parent != root
        or not re.fullmatch(r"[0-9a-f]{32}", path.parent.name)
    ):
        raise DeliveryError("repair proposal must be retained in the selected run")
    value = delivery._check_json(path)
    if value.get("schema") != SCHEMA or value.get("run_id") != run_dir.name:
        raise DeliveryError("invalid runtime repair proposal owner")
    if value.get("run_sha256") != _digest(delivery._check_bytes(run_dir / "run.json")):
        raise DeliveryError("runtime repair original run metadata changed")
    before, after = value.get("before"), value.get("after")
    if (
        not isinstance(before, dict)
        or not isinstance(after, dict)
        or _changed(before, after) != value.get("changed")
    ):
        raise DeliveryError("invalid runtime repair identity transition")
    check = value.get("check", {})
    log = delivery._check_bytes(path.parent / "check.log", 32 * 1024 * 1024)
    if check.get("returncode") != 0 or check.get("log_sha256") != _digest(log):
        raise DeliveryError("runtime repair check evidence changed or failed")
    if not re.search(rb"\b[1-9][0-9]* passed\b", log):
        raise DeliveryError("runtime repair needs actual passing pytest assertions")
    snapshot = value.get("snapshot")
    if not isinstance(snapshot, dict) or not snapshot:
        raise DeliveryError("runtime repair source snapshot is missing")
    for relative, digest in snapshot.items():
        safe = delivery._safe_path(relative)
        if (
            _digest(
                delivery._check_bytes(path.parent / "source" / safe, 32 * 1024 * 1024)
            )
            != digest
        ):
            raise DeliveryError("runtime repair source snapshot changed")
    for relative, digest in after.items():
        if _code_key(relative) and snapshot.get(relative) != digest:
            raise DeliveryError(
                "runtime repair snapshot differs from new core identity"
            )
    selectors = check.get("tests", [])
    if not selectors or any(
        str(selector).split("::")[0] not in snapshot for selector in selectors
    ):
        raise DeliveryError("runtime repair lacks retained test sources")
    return value


def effective_identity(
    delivery: Any, run_dir: Path, metadata: dict[str, Any]
) -> dict[str, str]:
    """Validate append-only repair receipts without rewriting original identity."""
    identity = metadata.get("process_identity")
    if not isinstance(identity, dict):
        raise DeliveryError("missing frozen execution identity")
    root = _root(delivery, run_dir)
    applied = root / "applied"
    if not applied.exists() and not applied.is_symlink():
        return identity
    if applied.is_symlink():
        raise DeliveryError("linked runtime repair chain")
    previous = None
    for number, path in enumerate(sorted(applied.iterdir()), 1):
        if path.name != f"{number:06d}.json":
            raise DeliveryError("runtime repair receipt chain is incomplete")
        raw = delivery._check_bytes(path)
        receipt = delivery._check_json(path)
        if (
            receipt.get("schema") != SCHEMA
            or receipt.get("previous_sha256") != previous
        ):
            raise DeliveryError("runtime repair receipt chain changed")
        proposal_path = root / delivery._safe_path(receipt.get("proposal"))
        if _digest(delivery._check_bytes(proposal_path)) != receipt.get(
            "proposal_sha256"
        ):
            raise DeliveryError("runtime repair proposal changed after apply")
        proposal = _proposal(delivery, run_dir, proposal_path)
        if proposal["before"] != identity:
            raise DeliveryError(
                "runtime repair does not extend the frozen source identity"
            )
        identity = proposal["after"]
        previous = _digest(raw)
    return identity


def prepare(
    delivery: Any, run_dir: Path, *, tests: Sequence[str], reason: str
) -> dict[str, Any]:
    """Run operator-selected scoped pytest checks and retain an immutable proposal."""
    if os.environ.get("CHRL_SESSION_ROLE") or not reason.strip():
        raise DeliveryError(
            "runtime repair preparation requires an operator reason outside delivery"
        )
    with delivery.delivery_lock():
        return _prepare(delivery, run_dir.absolute(), tests=tests, reason=reason)


def _prepare(
    delivery: Any, run_dir: Path, *, tests: Sequence[str], reason: str
) -> dict[str, Any]:
    metadata = _boundary(delivery, run_dir)
    linked = source_binding.binding(delivery.REPO_ROOT)
    if linked is None:
        raise DeliveryError("runtime repair requires an explicit shared-source binding")
    source = Path(linked["source_root"])
    before = effective_identity(delivery, run_dir, metadata)
    after = delivery.execution_identity()
    changed = _changed(before, after)
    if any(
        source_binding.trusted_path(delivery.REPO_ROOT, delivery.REPO_ROOT / relative)
        is None
        for relative in changed
    ):
        raise DeliveryError("runtime repair only adopts explicitly linked shared code")
    if not tests:
        raise DeliveryError(
            "runtime repair requires explicit focused pytest test files or nodes"
        )
    selected = []
    for selector in tests:
        relative = delivery._safe_path(selector.split("::")[0])
        path = source / relative
        if (
            not relative.startswith("tools/changerail/tests/test_")
            or not relative.endswith(".py")
            or path.resolve() != path
            or not path.is_file()
        ):
            raise DeliveryError(
                "runtime repair checks must select shared ChangeRail test files or nodes"
            )
        selected.append(relative)
    retained = _run_snapshot(delivery, run_dir)
    project_payload = delivery.payload_fingerprint()
    root = _root(delivery, run_dir)
    root.mkdir(exist_ok=True)
    directory = root / uuid.uuid4().hex
    directory.mkdir()
    snapshots = {}
    for relative in sorted({key for key in after if _code_key(key)} | set(selected)):
        if _code_key(relative):
            data = source_binding.read_runtime(
                delivery.REPO_ROOT, delivery.REPO_ROOT / relative, delivery._check_bytes
            )
        else:
            data = (source / relative).read_bytes()
        target = directory / "source" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        snapshots[relative] = _digest(data)
    command = [sys.executable, "-m", "pytest", *tests, "-q"]
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("CHRL_")
        and key not in {"PYTEST_ADDOPTS", "PYTEST_PLUGINS", "PYTHONPATH"}
    }
    environment["PYTHONPATH"] = str(source)
    environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    with (directory / "check.log").open("xb") as log:
        result = subprocess.run(
            command,
            cwd=source,
            env=environment,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    output = (directory / "check.log").read_bytes()
    if result.returncode or not re.search(rb"\b[1-9][0-9]* passed\b", output):
        raise DeliveryError(
            f"runtime repair focused tests did not pass; retained log: {directory / 'check.log'}"
        )
    if (
        delivery.execution_identity() != after
        or _run_snapshot(delivery, run_dir) != retained
        or delivery.payload_fingerprint() != project_payload
    ):
        raise DeliveryError(
            "source or project changed during runtime repair verification"
        )
    if any(
        _digest((source / relative).read_bytes()) != snapshots[relative]
        for relative in selected
    ):
        raise DeliveryError("runtime repair test sources changed during verification")
    proposal = {
        "schema": SCHEMA,
        "run_id": run_dir.name,
        "reason": reason.strip(),
        "created_at": delivery.utc_now(),
        "boundary": "before-first-accepted-proof",
        "run_sha256": retained["run.json"],
        "run_snapshot": retained,
        "project_payload": project_payload,
        "before": before,
        "after": after,
        "changed": changed,
        "snapshot": snapshots,
        "check": {
            "command": command,
            "tests": list(tests),
            "returncode": result.returncode,
            "log_sha256": _digest(output),
        },
    }
    path = directory / "proposal.json"
    _write(path, proposal)
    _proposal(delivery, run_dir, path)
    return {"proposal": str(path), "changed": changed, "boundary": proposal["boundary"]}


def apply(delivery: Any, run_dir: Path, proposal_path: Path) -> dict[str, Any]:
    """Adopt only the proven core revision; continue through ordinary resume."""
    if os.environ.get("CHRL_SESSION_ROLE"):
        raise DeliveryError(
            "runtime repair apply requires an operator outside delivery"
        )
    run_dir = run_dir.absolute()
    with delivery.delivery_lock():
        metadata = _boundary(delivery, run_dir)
        if source_binding.binding(delivery.REPO_ROOT) is None:
            raise DeliveryError(
                "runtime repair requires an explicit shared-source binding"
            )
        value = _proposal(delivery, run_dir, proposal_path.absolute())
        if (
            effective_identity(delivery, run_dir, metadata) != value["before"]
            or delivery.execution_identity() != value["after"]
        ):
            raise DeliveryError(
                "runtime repair source identity changed after preparation"
            )
        if (
            _run_snapshot(delivery, run_dir) != value["run_snapshot"]
            or delivery.payload_fingerprint() != value["project_payload"]
        ):
            raise DeliveryError(
                "runtime repair project or retained payload changed after preparation"
            )
        root = _root(delivery, run_dir)
        applied = root / "applied"
        applied.mkdir(exist_ok=True)
        chain = sorted(applied.iterdir())
        receipt = {
            "schema": SCHEMA,
            "applied_at": delivery.utc_now(),
            "proposal": proposal_path.absolute().relative_to(root).as_posix(),
            "proposal_sha256": _digest(delivery._check_bytes(proposal_path.absolute())),
            "previous_sha256": _digest(delivery._check_bytes(chain[-1]))
            if chain
            else None,
        }
        path = applied / f"{len(chain) + 1:06d}.json"
        _write(path, receipt)
        return {
            "receipt": str(path),
            "next": "ordinary resume; all delivery proof and review gates remain mandatory",
        }
