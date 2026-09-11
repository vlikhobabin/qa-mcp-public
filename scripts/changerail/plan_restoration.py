"""Append-only, explicitly authorized restoration of the accepted Next byte span.

Old run directories are never written. Receipt lookup checks retained history,
not the subsequently evolving product tree. Resume owns fresh payload checking.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import stat
import subprocess
import uuid
from pathlib import Path
from typing import Any

from scripts.changerail import openspec_context as native
from scripts.changerail.contracts import DeliveryError

SCHEMA = "changerail.plan-restoration.v1"
LIMIT = 32 * 1024 * 1024


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sync(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write(path: Path, value: dict[str, Any]) -> None:
    # Publish an already-fsynced complete record with exclusive link creation.
    # A killed writer cannot leave a partially written authoritative JSON file.
    temporary = path.with_name("." + path.name + ".pending-" + uuid.uuid4().hex)
    try:
        with temporary.open("xb") as stream:
            stream.write((json.dumps(value, sort_keys=True, indent=2) + "\n").encode())
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path, follow_symlinks=False)
        _sync(path.parent)
    finally:
        temporary.unlink(missing_ok=True)
        _sync(path.parent)


def _safe(delivery: Any, path: Path) -> Path:
    path = path.absolute()
    if path.resolve() != path or not path.is_relative_to(delivery.REPO_ROOT):
        raise DeliveryError("plan restoration path must be local without symlinks")
    return path


def _root(delivery: Any) -> Path:
    return _safe(delivery, delivery.RUNTIME_ROOT / "plan-restorations")


def _run(delivery: Any, path: Path) -> Path:
    path = _safe(delivery, path)
    if path.parent != delivery.RUNTIME_ROOT / "runs" or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._-]*", path.name
    ):
        raise DeliveryError("plan restoration requires an exact run directory")
    return path


def _inventory(delivery: Any, run: Path) -> dict[str, Any]:
    result = {}
    for path in sorted(run.rglob("*")):
        _safe(delivery, path)
        mode = stat.S_IMODE(path.stat().st_mode)
        key = path.relative_to(run).as_posix()
        if path.is_dir():
            result[key] = {"directory": True, "mode": mode}
        else:
            result[key] = {
                "sha256": _digest(delivery._check_bytes(path, LIMIT)),
                "mode": mode,
            }
        if len(result) > 100000:
            raise DeliveryError("plan restoration history inventory exceeds limit")
    return result


def _lineage(delivery: Any, run: Path) -> list[tuple[Path, dict[str, Any]]]:
    found = []
    seen = set()
    owner = None
    while True:
        run = _run(delivery, run)
        if run.name in seen or len(seen) >= 1000:
            raise DeliveryError("invalid cyclic recovery ancestry")
        seen.add(run.name)
        metadata = delivery.require_current_execution(run)
        if (
            metadata.get("run_id") != run.name
            or not metadata.get("finished_at")
            or metadata.get("exit_code") in (None, 0)
        ):
            raise DeliveryError("plan restoration requires a stopped failed native run")
        card = metadata.get("card")
        if not isinstance(card, str) or (owner is not None and card != owner):
            raise DeliveryError("foreign recovery ancestor card owner")
        owner = card
        found.append((run, metadata))
        previous = metadata.get("recovery_of")
        if previous is None:
            return found
        if not isinstance(previous, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._-]*", previous
        ):
            raise DeliveryError("invalid recovery ancestor")
        run = delivery.RUNTIME_ROOT / "runs" / previous


def _next(data: bytes) -> tuple[int, int]:
    headings = list(re.finditer(rb"^## ([^\r\n]+)\r?\n", data, re.MULTILINE))
    names = [match[1] for match in headings]
    if len(names) != len(set(names)) or names.count(b"Next") != 1:
        raise DeliveryError(
            "restoration requires exactly one Next and no duplicate sections"
        )
    index = names.index(b"Next")
    return headings[index].end(), headings[index + 1].start() if index + 1 < len(
        headings
    ) else len(data)


def _contract(data: bytes) -> str:
    text = data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(
        r"^## (?:Status|Result|Log)\n.*?(?=^## |\Z)",
        "",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return _digest(text.encode())


def _boundary(
    delivery: Any, lineage: list, *, check_identity: bool = True
) -> tuple[dict, Path, dict]:
    plan = None
    origin = None
    review_count = 0
    for run, metadata in lineage:
        reason = str(metadata.get("terminal_reason", ""))
        if not re.search(
            r"accepted.*plan.*changed|accepted.*plan.*receipt.*absent|recovery.*(?:payload|manifest|fingerprint)|frozen execution process changed",
            reason,
            re.IGNORECASE,
        ):
            raise DeliveryError(
                "unsupported terminal stage: restoration requires accepted-plan drift or pre-import recovery failure"
            )
        if metadata.get("stop_reason") == "operator_interrupt" or metadata.get(
            "exit_code"
        ) in (130, -2):
            raise DeliveryError("operator-stopped execution cannot be restored")
        prohibited = (
            "native-archive.json",
            "native-archive-intent.json",
            "native-review-continuation.json",
            "verification.json",
            "publication.json",
            "publication-journal.json",
            "final-test-proof-inputs",
        )
        if any((run / name).exists() for name in prohibited):
            raise DeliveryError(
                "plan restoration cannot cross pending review, archive, floor or publication"
            )
        if delivery._unresolved_verification_attempt(run):
            raise DeliveryError(
                "plan restoration cannot restart an interrupted verification attempt"
            )
        for path in (run / "verification-attempts").glob("*.json"):
            if delivery._check_json(path).get("lane") == "final":
                raise DeliveryError(
                    "plan restoration cannot cross a final floor attempt"
                )
        if (
            check_identity
            and metadata.get("process_identity") != delivery.execution_identity()
        ):
            raise DeliveryError(
                "frozen execution identity changed; an explicit supported installed runtime transition is required"
            )
        for session in run.rglob("session.json"):
            retained_session = delivery._check_json(session)
            if retained_session.get(
                "stop_reason"
            ) == "operator_interrupt" or not retained_session.get("finished_at"):
                raise DeliveryError(
                    "unfinished or operator-stopped session cannot be restored"
                )
        if any(
            event.get("phase") in {"verify", "publish", "preverify"}
            for event in delivery.read_phase_events(run)
        ):
            raise DeliveryError(
                "plan restoration cannot cross final floor or publication events"
            )
        reviews = delivery._completed_review_verdicts(run / "reviews")
        review_count += len(reviews)
        for verdict in reviews:
            if delivery._check_json(verdict).get("result") != "no-go":
                raise DeliveryError(
                    "restoration cannot reuse or cross a completed GO review"
                )
        path = run / "native-plan.json"
        if path.exists():
            candidate = delivery._check_json(path)
            if plan is not None and candidate != plan:
                raise DeliveryError("ancestor accepted plans differ")
            if plan is None:
                plan, origin = candidate, run
        elif (
            not metadata.get("recovery_of")
            or any(
                (run / name).exists()
                for name in (
                    "reviews",
                    "focused-evidence",
                    "implementation-handoff.json",
                )
            )
            or any(
                str(e.get("phase", "")).startswith("change-")
                for e in delivery.read_phase_events(run)
            )
        ):
            raise DeliveryError(
                "missing native plan is only allowed for a proven pre-import recovery child"
            )
    if review_count >= 2:
        raise DeliveryError(
            "two independent reviews already consumed; restoration cannot grant a third review"
        )
    if plan is None or origin is None:
        raise DeliveryError("accepted plan origin is absent")
    admission = (
        delivery.RUNTIME_ROOT
        / "native-plans"
        / Path(lineage[0][1]["card"]).stem
        / "native-plan.json"
    )
    if delivery._check_json(admission) != plan:
        raise DeliveryError("accepted plan origin differs from admission receipt")
    for index, (run, metadata) in enumerate(lineage):
        events = delivery.combined_change_events(run)
        delivery.validate_change_event_prefix(
            [tuple(g) for g in plan["groups"]], events
        )
        if metadata.get("recovery_of"):
            predecessor = lineage[index + 1][0]
            if metadata.get(
                "inherited_change_events", []
            ) != delivery.combined_change_events(predecessor):
                raise DeliveryError(
                    "inherited checkpoint events differ from retained ancestor"
                )
    if delivery.review_budget_usage(lineage[0][0]) != {"semantic_cycles": review_count}:
        raise DeliveryError("retained review accounting differs from complete ancestry")
    return plan, origin, {"semantic_cycles": review_count}


def _exact_payload(delivery: Any, manifest: dict) -> None:
    paths = delivery.changed_paths()
    if (
        delivery.staged_paths()
        or manifest.get("baseline_head")
        != delivery.git("rev-parse", "HEAD").stdout.strip()
        or manifest.get("paths") != paths
        or manifest.get("fingerprint") != delivery.payload_fingerprint(paths)
        or manifest.get("path_fingerprints") != delivery.path_fingerprints(paths)
    ):
        raise DeliveryError(
            "plan restoration requires the exact retained HEAD, index and payload manifest"
        )
    for relative in paths:
        delivery._safe_path(relative)
        delivery._path_state(relative)


def _snapshot_source(delivery: Any, card: Path, plan: dict) -> tuple[bytes, str]:
    root = delivery.RUNTIME_ROOT / "native-plans" / card.stem
    path = _safe(delivery, root / "accepted-card.md")
    descriptor_path = _safe(delivery, root / "accepted-card.json")
    if not path.is_file() or not descriptor_path.is_file():
        raise DeliveryError(
            "accepted Git blob unavailable and no authenticated admission snapshot exists"
        )
    descriptor = delivery._check_json(descriptor_path)
    data = delivery._check_bytes(path, LIMIT)
    source = descriptor.get("source")
    if not isinstance(source, str):
        raise DeliveryError("accepted snapshot source owner is absent")
    owner = delivery.REPO_ROOT / delivery._safe_path(source)
    if (
        descriptor.get("schema") != "changerail.accepted-card.v1"
        or descriptor.get("sha256") != _digest(data)
        or descriptor.get("card_contract_sha256") != plan.get("card_contract_sha256")
        or _contract(data) != plan.get("card_contract_sha256")
        or owner.parent.parent != delivery.BOARD_ROOT
        or owner.parent.name not in {"1.backlog", "2.todo"}
        or owner.name != card.name
    ):
        raise DeliveryError("accepted snapshot source or full contract changed")
    _next(data)
    return data, delivery.repo_relative(path)


def _source(delivery: Any, commit: str, card: Path, plan: dict) -> tuple[bytes, str]:
    path = (
        (card.parent.parent / "2.todo" / card.name)
        .relative_to(delivery.REPO_ROOT)
        .as_posix()
    )
    tree = delivery.git(
        "ls-tree", "-r", "--name-only", commit, "--", "openspec/board"
    ).stdout.splitlines()
    matches = [p for p in tree if Path(p).name == card.name]
    if not matches:
        return _snapshot_source(delivery, card, plan)
    if matches != [path]:
        raise DeliveryError("accepted baseline must contain exactly one todo card")
    entry = delivery.git("ls-tree", commit, "--", path).stdout.split()
    if len(entry) != 4 or entry[0] not in {"100644", "100755"} or entry[1] != "blob":
        raise DeliveryError("accepted source must be a regular Git blob")
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=delivery.REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        return _snapshot_source(delivery, card, plan)
    if len(result.stdout) > LIMIT:
        raise DeliveryError("accepted Git card blob exceeds limit")
    data = result.stdout
    _next(data)
    if _contract(data) != plan.get("card_contract_sha256"):
        raise DeliveryError(
            "accepted Git source does not match the complete accepted card contract"
        )
    return data, path


def _projected_manifest(
    delivery: Any,
    manifest: dict,
    card: Path,
    after: bytes,
    *,
    runtime_transition: dict | None = None,
) -> dict:
    """Project exact path inventory and bytes before either mutation is allowed."""
    relative = delivery.repo_relative(card)
    overrides: dict[str, tuple[bytes, int] | None] = {
        relative: (after, stat.S_IMODE(card.stat().st_mode)),
    }
    if runtime_transition is not None:
        import distribution as dist

        archive = Path(runtime_transition["archive"])
        target, payload = dist.inspect_archive(archive)
        if (
            _digest(archive.read_bytes()) != runtime_transition["archive_sha256"]
            or target["files"] != runtime_transition["after_lock"]["files"]
        ):
            raise DeliveryError("projection target archive changed")
        for name in runtime_transition["before_lock"]["files"].keys() - payload.keys():
            overrides[name] = None
        overrides.update(payload)
        overrides[dist.LOCK] = (dist.encoded(runtime_transition["after_lock"]), 0o644)
    tree = delivery.git("ls-tree", "-rz", manifest["baseline_head"], text=False).stdout
    baseline = {}
    for entry in tree.split(b"\x00"):
        if entry:
            meta, path = entry.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            baseline[os.fsdecode(path)] = (mode, kind, oid)
    paths = set(manifest["paths"])
    for name, item in overrides.items():
        delivery._safe_path(name)
        if any(
            name == p.rstrip("/") or name.startswith(p)
            for p in delivery.EXCLUDED_PREFIXES
        ):
            paths.discard(name)
            continue
        retained = baseline.get(name)
        if retained is None:
            ignored = (
                delivery.git(
                    "check-ignore", "--quiet", "--no-index", "--", name, check=False
                ).returncode
                == 0
            )
            changed = item is not None and not ignored
        elif item is None:
            changed = True
        else:
            data, mode = item
            oid = (
                subprocess.run(
                    ["git", "hash-object", "--path=" + name, "--stdin"],
                    cwd=delivery.REPO_ROOT,
                    input=data,
                    capture_output=True,
                    check=True,
                )
                .stdout.decode()
                .strip()
            )
            executable = "100755" if mode & 0o111 else "100644"
            filemode = (
                delivery.git(
                    "config", "--bool", "core.filemode", check=False
                ).stdout.strip()
                != "false"
            )
            changed = (
                retained[1] != "blob"
                or retained[2] != oid
                or (filemode and retained[0] != executable)
            )
        if changed:
            paths.add(name)
        else:
            paths.discard(name)
    aggregate = hashlib.sha256()
    aggregate.update(f"head\x00{manifest['baseline_head']}\x00".encode())
    hashes, states = {}, {}
    for name in sorted(paths):
        path_hash = hashlib.sha256()
        if name in overrides:
            item = overrides[name]
            encoded = f"path\x00{name}\x00".encode()
            if item is None:
                encoded += b"deleted\x00"
                state = {"kind": "deleted", "mode": 0}
            else:
                data, mode = item
                encoded += (
                    f"mode\x00{stat.S_IFREG | mode:o}\x00".encode()
                    + b"file\x00"
                    + data
                    + b"\x00"
                )
                state = {"kind": "file", "mode": mode}
            aggregate.update(encoded)
            path_hash.update(encoded)
        else:
            delivery._update_path_digest(aggregate, name)
            delivery._update_path_digest(path_hash, name)
            state = delivery._path_state(name)
        hashes[name] = "sha256:" + path_hash.hexdigest()
        states[name] = {**state, "digest": hashes[name]}
    return {
        **manifest,
        "paths": sorted(paths),
        "path_fingerprints": hashes,
        "path_states": states,
        "fingerprint": {
            "head_commit": manifest["baseline_head"],
            "payload_fingerprint": "sha256:" + aggregate.hexdigest(),
        },
    }


def prepare(
    delivery: Any,
    run_dir: Path,
    reason: str,
    dry_run: bool = False,
    accepted_commit: str | None = None,
    runtime_archive: Path | None = None,
) -> dict[str, Any]:
    if os.environ.get("CHRL_SESSION_ROLE") or not reason.strip() or len(reason) > 1000:
        raise DeliveryError(
            "plan restoration requires a bounded operator reason outside delivery"
        )
    with delivery.delivery_lock():
        ensure_no_pending(delivery)
        run_dir = _run(delivery, run_dir)
        lineage = _lineage(delivery, run_dir)
        plan, origin, usage = _boundary(
            delivery, lineage, check_identity=runtime_archive is None
        )
        manifest = delivery._check_json(run_dir / "manifest.json")
        metadata = lineage[0][1]
        card = _safe(
            delivery, delivery.REPO_ROOT / delivery._safe_path(metadata["card"])
        )
        if (
            card.parent != delivery.BOARD_ROOT / "3.inprogress"
            or manifest.get("run_id") != run_dir.name
            or manifest.get("schema") != "changerail.delivery-manifest.v1"
            or manifest.get("card")
            != {"id": delivery.card_id(card), "path": delivery.repo_relative(card)}
        ):
            raise DeliveryError(
                "manifest/card owner is not the exact inprogress predecessor"
            )
        if list(delivery.BOARD_ROOT.glob(f"*/{card.name}")) != [card]:
            raise DeliveryError("restoration card is duplicated across board columns")
        _exact_payload(delivery, manifest)
        commit = manifest["baseline_head"]
        if accepted_commit is not None and accepted_commit != commit:
            raise DeliveryError("accepted commit must equal the proven run baseline")
        accepted, source_path = _source(delivery, commit, card, plan)
        before = delivery._check_bytes(card, LIMIT)
        start, end = _next(before)
        astart, aend = _next(accepted)
        after = before[:start] + accepted[astart:aend] + before[end:]
        if before == after:
            raise DeliveryError(
                "Next already matches the accepted source; no restoration is applicable"
            )
        current = native.plan_identity(delivery, card)
        current["card_contract_sha256"] = _contract(after)
        if current != plan:
            raise DeliveryError(
                "restoring Next would not restore the complete accepted plan identity"
            )
        transition = None
        if runtime_archive is not None:
            from scripts.changerail import installed_restoration

            transition = installed_restoration.prepare_transition(
                delivery, run_dir, runtime_archive
            )
        proposal = {
            "schema": SCHEMA,
            "project": str(delivery.REPO_ROOT),
            "run_id": run_dir.name,
            "origin": origin.name,
            "reason": reason.strip(),
            "created_at": delivery.utc_now(),
            "card": delivery.repo_relative(card),
            "mode": stat.S_IMODE(card.stat().st_mode),
            "accepted_commit": commit,
            "accepted_path": source_path,
            "accepted_blob_sha256": _digest(accepted),
            "before_sha256": _digest(before),
            "after_sha256": _digest(after),
            "before_hex": before.hex(),
            "after_hex": after.hex(),
            "accepted_hex": accepted.hex(),
            "plan": plan,
            "review_budget": usage,
            "manifest": manifest,
            "identity": metadata["process_identity"],
            "coordinator_identity": delivery.execution_identity(),
            "history": {run.name: _inventory(delivery, run) for run, _ in lineage},
            "diff": "".join(
                difflib.unified_diff(
                    before.decode().splitlines(True),
                    after.decode().splitlines(True),
                    fromfile="before/" + card.name,
                    tofile="after/" + card.name,
                )
            ),
            "runtime_transition": transition,
            "projected_manifest": _projected_manifest(
                delivery, manifest, card, after, runtime_transition=transition
            ),
        }
        if dry_run:
            return {"dry_run": True, "status": "READY", "candidate": proposal}
        root = _root(delivery)
        root.mkdir(parents=True, exist_ok=True)
        directory = root / uuid.uuid4().hex
        directory.mkdir()
        path = directory / "proposal.json"
        _write(path, proposal)
        return {
            "proposal": str(path),
            "proposal_sha256": _digest(delivery._check_bytes(path, LIMIT * 8)),
            "status": "READY",
        }


def _proposal(delivery: Any, run_dir: Path, path: Path) -> dict:
    path = _safe(delivery, path)
    if (
        path.name != "proposal.json"
        or path.parent.parent != _root(delivery)
        or not re.fullmatch(r"[0-9a-f]{32}", path.parent.name)
    ):
        raise DeliveryError(
            "proposal must belong to the selected restoration transaction"
        )
    value = delivery._check_json_bytes(delivery._check_bytes(path, LIMIT * 8))
    if (
        value.get("schema") != SCHEMA
        or value.get("project") != str(delivery.REPO_ROOT)
        or value.get("run_id") != run_dir.name
    ):
        raise DeliveryError("invalid plan restoration proposal owner")
    for key in ("before", "after", "accepted"):
        try:
            data = bytes.fromhex(value[key + "_hex"])
        except (KeyError, TypeError, ValueError) as exc:
            raise DeliveryError("invalid restoration snapshot") from exc
        expected = (
            value["accepted_blob_sha256"]
            if key == "accepted"
            else value[key + "_sha256"]
        )
        if len(data) > LIMIT or _digest(data) != expected:
            raise DeliveryError("restoration snapshot changed")
    before, after, accepted = (
        bytes.fromhex(value[key + "_hex"]) for key in ("before", "after", "accepted")
    )
    a, b = _next(before)
    c, e = _next(accepted)
    if (
        before[:a] + accepted[c:e] + before[b:] != after
        or _contract(after) != value["plan"].get("card_contract_sha256")
        or _contract(accepted) != _contract(after)
    ):
        raise DeliveryError("proposal is not an exact accepted Next restoration")
    for name, inventory in value["history"].items():
        if (
            _inventory(delivery, _run(delivery, delivery.RUNTIME_ROOT / "runs" / name))
            != inventory
        ):
            raise DeliveryError("retained restoration history changed")
    return value


def _atomic_card(path: Path, data: bytes, mode: int) -> None:
    temporary = path.with_name("." + path.name + ".restore-" + uuid.uuid4().hex)
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        _sync(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def apply(
    delivery: Any, run_dir: Path, proposal: Path, authorize: str
) -> dict[str, Any]:
    if os.environ.get("CHRL_SESSION_ROLE"):
        raise DeliveryError(
            "plan restoration apply requires an operator outside delivery"
        )
    with delivery.delivery_lock(restoration_reconcile=True):
        run_dir = _run(delivery, run_dir)
        proposal = Path(proposal).absolute()
        value = _proposal(delivery, run_dir, proposal)
        digest = _digest(delivery._check_bytes(proposal, LIMIT * 8))
        if authorize != digest:
            raise DeliveryError("explicit proposal SHA256 authority does not match")
        directory = proposal.parent
        receipt_path = directory / "applied.json"
        if receipt_path.exists():
            return _receipt(delivery, run_dir, directory)
        intent_path = directory / "apply-intent.json"
        card = _safe(delivery, delivery.REPO_ROOT / delivery._safe_path(value["card"]))
        before = bytes.fromhex(value["before_hex"])
        after = bytes.fromhex(value["after_hex"])
        data = delivery._check_bytes(card, LIMIT)
        if (
            data not in (before, after)
            or stat.S_IMODE(card.stat().st_mode) != value["mode"]
        ):
            raise DeliveryError(
                "restoration card is neither exact before nor after state"
            )
        if not intent_path.exists():
            ensure_no_pending(delivery)
            if data != before:
                raise DeliveryError("card changed before durable restoration intent")
            _boundary(
                delivery,
                _lineage(delivery, run_dir),
                check_identity=value["runtime_transition"] is None,
            )
            _exact_payload(delivery, value["manifest"])
            if delivery.execution_identity() != value["coordinator_identity"]:
                raise DeliveryError("coordinator execution changed after preparation")
            _write(
                intent_path,
                {
                    "schema": SCHEMA,
                    "proposal_sha256": digest,
                    "authorized": authorize,
                    "created_at": delivery.utc_now(),
                },
            )
        intent = delivery._check_json(intent_path)
        if (
            intent.get("proposal_sha256") != digest
            or intent.get("authorized") != authorize
        ):
            raise DeliveryError("restoration durable authority changed")
        # Reconciliation may only alter Next, never resample unrelated paths.
        paths = delivery.changed_paths()
        manifest = value["manifest"]
        hashes = delivery.path_fingerprints(paths)
        runtime_paths = set()
        if value["runtime_transition"] is not None:
            bridge = value["runtime_transition"]
            runtime_paths = (
                set(bridge["before_lock"]["files"])
                | set(bridge["after_lock"]["files"])
                | {".changerail/distribution-lock.json"}
            )
        if (
            delivery.staged_paths()
            or set(paths) - runtime_paths != set(manifest["paths"]) - runtime_paths
            or delivery.git("rev-parse", "HEAD").stdout.strip()
            != manifest["baseline_head"]
            or any(
                hashes.get(p) != h
                for p, h in manifest["path_fingerprints"].items()
                if p != value["card"] and p not in runtime_paths
            )
        ):
            raise DeliveryError("restoration payload changed after durable intent")
        if value["runtime_transition"] is not None:
            from scripts.changerail import installed_restoration

            installed_restoration.apply_transition(
                delivery, value["runtime_transition"], directory
            )
        elif delivery.execution_identity() != value["coordinator_identity"]:
            raise DeliveryError("restoration execution identity changed")
        if data == before:
            _atomic_card(card, after, value["mode"])
        paths = delivery.changed_paths()
        effective = dict(manifest)
        effective.update(
            paths=paths,
            fingerprint=delivery.payload_fingerprint(paths),
            path_fingerprints=delivery.path_fingerprints(paths),
            path_states={p: delivery._path_state(p) for p in paths},
        )
        if effective != value["projected_manifest"]:
            raise DeliveryError(
                "applied payload differs from authorized projection; reconcile exact intent"
            )
        receipt = {
            "schema": SCHEMA,
            "run_id": run_dir.name,
            "proposal_sha256": digest,
            "applied_at": delivery.utc_now(),
            "effective_manifest": effective,
            "identity": delivery.execution_identity(),
            "receipt": str(receipt_path),
            "next": "ordinary resume; refresh payload-bound evidence before handoff",
        }
        _write(receipt_path, receipt)
        return receipt


def _receipt(delivery: Any, run_dir: Path, directory: Path) -> dict:
    value = _proposal(delivery, run_dir, directory / "proposal.json")
    receipt = delivery._check_json_bytes(
        delivery._check_bytes(directory / "applied.json", LIMIT * 8)
    )
    intent = delivery._check_json(directory / "apply-intent.json")
    digest = _digest(delivery._check_bytes(directory / "proposal.json", LIMIT * 8))
    if (
        receipt.get("schema") != SCHEMA
        or receipt.get("run_id") != run_dir.name
        or receipt.get("receipt") != str(directory / "applied.json")
        or receipt.get("proposal_sha256") != digest
        or intent.get("proposal_sha256") != digest
        or intent.get("authorized") != digest
    ):
        raise DeliveryError("restoration receipt authority changed")
    if receipt.get("effective_manifest") != value["projected_manifest"]:
        raise DeliveryError(
            "restoration effective manifest differs from authorized projection"
        )
    if value["runtime_transition"] is not None:
        from scripts.changerail import installed_restoration

        identity = installed_restoration.effective_identity(
            delivery, value["runtime_transition"], directory
        )
        if receipt.get("identity") != identity:
            raise DeliveryError(
                "installed restoration receipt execution identity changed"
            )
    if (
        value["runtime_transition"] is None
        and receipt.get("identity") != value["identity"]
    ):
        raise DeliveryError("restoration receipt execution identity changed")
    return receipt


def _applied(delivery: Any, run_dir: Path) -> tuple[dict, dict] | None:
    run_dir = _run(delivery, run_dir)
    root = _root(delivery)
    if not root.exists():
        return None
    found = []
    for directory in sorted(root.iterdir()):
        _safe(delivery, directory)
        path = directory / "applied.json"
        if (
            path.exists()
            and delivery._check_json_bytes(delivery._check_bytes(path, LIMIT * 8)).get(
                "run_id"
            )
            == run_dir.name
        ):
            receipt = _receipt(delivery, run_dir, directory)
            found.append(
                (
                    delivery._check_json_bytes(
                        delivery._check_bytes(directory / "proposal.json", LIMIT * 8)
                    ),
                    receipt,
                )
            )
    if len(found) > 1:
        raise DeliveryError("multiple restorations claim the same predecessor")
    return found[0] if found else None


def effective_manifest(delivery: Any, run_dir: Path) -> dict | None:
    selected = _applied(delivery, run_dir)
    return selected[1]["effective_manifest"] if selected else None


def effective_identity(delivery: Any, run_dir: Path, metadata: dict) -> dict | None:
    selected = _applied(delivery, run_dir)
    if selected:
        return selected[1]["identity"]
    # A restored failed child proves the same transition for every immutable
    # ancestor in its lineage, so ordinary accounting can inspect them too.
    root = _root(delivery)
    found = []
    if root.exists():
        for directory in sorted(root.iterdir()):
            _safe(delivery, directory)
            if not (directory / "applied.json").exists():
                continue
            proposal = delivery._check_json_bytes(
                delivery._check_bytes(directory / "proposal.json", LIMIT * 8)
            )
            if run_dir.name in proposal.get("history", {}):
                owner = _run(
                    delivery, delivery.RUNTIME_ROOT / "runs" / proposal["run_id"]
                )
                found.append(_receipt(delivery, owner, directory)["identity"])
    if any(identity != found[0] for identity in found):
        raise DeliveryError("conflicting restoration ancestor identities")
    return found[0] if found else None


def accepted_plan(delivery: Any, run_dir: Path) -> dict | None:
    selected = _applied(delivery, run_dir)
    return selected[0]["plan"] if selected else None


def ensure_no_pending(delivery: Any) -> None:
    root = _root(delivery)
    if root.exists():
        for directory in root.iterdir():
            _safe(delivery, directory)
            if (directory / "apply-intent.json").exists() and not (
                directory / "applied.json"
            ).exists():
                raise DeliveryError(
                    f"pending plan restoration requires reconcile: {directory / 'proposal.json'}"
                )


def consume(delivery: Any, previous_run: Path, new_run: Path) -> dict | None:
    """Bind a single successor without adding files to any predecessor run.

    Called under the runner's existing writer lock after creating its run.json.
    The reference deliberately does not hash mutable successor metadata.
    """
    selected = _applied(delivery, previous_run)
    if selected is None:
        return None
    proposal, receipt = selected
    directory = Path(receipt["receipt"]).parent
    new_run = _run(delivery, new_run)
    metadata = delivery.require_current_execution(new_run)
    if (
        metadata.get("run_id") != new_run.name
        or metadata.get("recovery_of") != previous_run.name
        or metadata.get("process_identity") != receipt["identity"]
    ):
        raise DeliveryError("restoration successor identity or predecessor differs")
    path = directory / "consumed.json"
    value = {
        "schema": SCHEMA,
        "proposal_sha256": receipt["proposal_sha256"],
        "predecessor": previous_run.name,
        "successor": new_run.name,
        "origin": proposal["origin"],
        "receipt": delivery.repo_relative(directory / "applied.json"),
        "refresh_evidence": True,
    }
    if path.exists():
        if delivery._check_json(path) != value:
            raise DeliveryError(
                "restoration was already consumed by another successor; resume that successor"
            )
    else:
        _ready_successor(delivery, previous_run, new_run, receipt)
        _write(path, value)
    return value


def _creation_reference(
    delivery: Any, proposal: dict, receipt: dict, previous: Path, successor: Path
) -> dict:
    return {
        "schema": SCHEMA,
        "proposal_sha256": receipt["proposal_sha256"],
        "predecessor": previous.name,
        "successor": successor.name,
        "origin": proposal["origin"],
        "receipt": delivery.repo_relative(Path(receipt["receipt"])),
        "refresh_evidence": True,
    }


def _ready_successor(
    delivery: Any, previous: Path, successor: Path, receipt: dict
) -> None:
    required = (
        "run.json",
        "manifest.json",
        "native-plan.json",
        "recovery-context.json",
        "observed-proof-selection.json",
    )
    if any(not (successor / name).is_file() for name in required):
        raise DeliveryError("consumption requires a complete recoverable successor")
    metadata = delivery.require_current_execution(successor)
    manifest = delivery._check_json(successor / "manifest.json")
    context = delivery._check_json(successor / "recovery-context.json")
    if (
        metadata.get("recovery_of") != previous.name
        or metadata.get("run_id") != successor.name
        or manifest.get("run_id") != successor.name
        or context.get("recovery_of") != previous.name
        or manifest.get("fingerprint") != receipt["effective_manifest"]["fingerprint"]
    ):
        raise DeliveryError("complete restoration successor owner or payload differs")
    plan = accepted_plan(delivery, previous)
    if delivery._check_json(
        successor / "native-plan.json"
    ) != plan or delivery.declared_change_plan(successor) != [
        tuple(group) for group in plan["groups"]
    ]:
        raise DeliveryError("complete restoration successor accepted plan differs")
    if metadata.get("inherited_change_events") != delivery.combined_change_events(
        previous
    ) or context.get("inherited_change_events") != metadata.get(
        "inherited_change_events"
    ):
        raise DeliveryError(
            "complete restoration successor checkpoint ancestry differs"
        )
    delivery._run_observed_contract(successor)
    delivery.review_budget_usage(successor)


def _publish_successor(
    delivery: Any, previous: Path, directory: Path, receipt: dict
) -> Path:
    intent = delivery._check_json_bytes(
        delivery._check_bytes(directory / "successor-intent.json", LIMIT * 8)
    )
    if (
        intent.get("schema") != SCHEMA
        or intent.get("proposal_sha256") != receipt["proposal_sha256"]
    ):
        raise DeliveryError("restoration successor intent authority changed")
    successor = _run(delivery, delivery.RUNTIME_ROOT / "runs" / intent["successor"])
    staged = _safe(delivery, directory / delivery._safe_path(intent["staged"]))
    if not staged.is_relative_to(directory / "successor-preparations"):
        raise DeliveryError("unsafe successor staging owner")
    _exact_payload(delivery, receipt["effective_manifest"])
    if successor.exists():
        if staged.exists() or _inventory(delivery, successor) != intent["inventory"]:
            raise DeliveryError(
                f"restoration successor already started or changed; resume {successor}"
            )
    else:
        if _inventory(delivery, staged) != intent["inventory"]:
            raise DeliveryError("restoration successor staging changed")
        _exact_payload(delivery, receipt["effective_manifest"])
        successor.parent.mkdir(parents=True, exist_ok=True)
        os.rename(staged, successor)
        _sync(successor.parent)
        _sync(staged.parent)
    _ready_successor(delivery, previous, successor, receipt)
    consume(delivery, previous, successor)
    return successor


def create_successor(
    delivery: Any, previous: Path, card: Path, changes: list, objective: str
) -> dict | None:
    """Build off-run, authorize exact files, atomically publish, then consume.

    A pre-intent interruption only leaves an unowned preparation. A post-intent
    retry finishes the same publication. Once execution changes the published
    run, ordinary resume uses that fully initialized successor instead.
    """
    selected = _applied(delivery, previous)
    if selected is None:
        return None
    proposal, receipt = selected
    directory = Path(receipt["receipt"]).parent
    intent_path = directory / "successor-intent.json"
    if intent_path.exists():
        successor = _publish_successor(delivery, previous, directory, receipt)
    else:
        if (directory / "consumed.json").exists():
            consumed = delivery._check_json(directory / "consumed.json")
            raise DeliveryError(
                f"restoration already consumed; resume {consumed.get('successor')}"
            )
        _exact_payload(delivery, receipt["effective_manifest"])
        run_id = f"{delivery.utc_now().replace('-', '').replace(':', '')}-{card.stem}-{uuid.uuid4().hex[:8]}"
        successor = _run(delivery, delivery.RUNTIME_ROOT / "runs" / run_id)
        staged = directory / "successor-preparations" / uuid.uuid4().hex / run_id
        staged.mkdir(parents=True)
        selection = {
            "schema": "changerail.observed-proof-selection.v1",
            "root": delivery.repo_relative(staged),
            "owner": {"run_id": run_id, "card": delivery.repo_relative(card)},
            "required_stages": ["implementation", "review", "final"],
        }
        _write(staged / "observed-proof-selection.json", selection)
        reference = {
            "path": delivery.repo_relative(staged / "observed-proof-selection.json"),
            "sha256": _digest(
                delivery._check_bytes(staged / "observed-proof-selection.json")
            ),
        }
        thread, first_change, investigative = delivery.recovery_implementation_state(
            previous, receipt["effective_manifest"]
        )
        metadata = {
            "schema": "changerail.delivery-run.v2",
            "run_id": run_id,
            "card": delivery.repo_relative(card),
            "started_at": delivery.utc_now(),
            "baseline_head": receipt["effective_manifest"]["baseline_head"],
            "profile": delivery.repo_relative(delivery.PROFILE_PATH),
            "mode": "delivery",
            "lifecycle_mode": "openspec-v1",
            "change_plan": [
                {"number": number, "slug": slug} for number, slug in changes
            ],
            "execution_contract": "changerail.native.v1",
            "process_identity": delivery.execution_identity(),
            "observed_proof_contract": {
                "schema": delivery._OBSERVED_PROOF_CONTRACT,
                "required_stages": ["implementation", "review", "final"],
                "selection": reference,
            },
            "recovery_of": previous.name,
            "recovery_compatibility": None,
            "recovery_objective": objective,
            "resume_thread_id": thread,
            "inherited_investigative_commands": investigative,
            "restoration_require_first_file_change": first_change,
            "plan_restoration": _creation_reference(
                delivery, proposal, receipt, previous, successor
            ),
        }
        _write(staged / "run.json", metadata)
        context_path = delivery.build_recovery_context(
            run_dir=staged, previous_run=previous, objective=objective
        )
        context = delivery._check_json(context_path)
        metadata.update(
            recovery_session_strategy=context.get("resume_strategy"),
            inherited_change_events=context["inherited_change_events"],
        )
        final_selection = {**selection, "root": delivery.repo_relative(successor)}
        # Finish references before recording the exact publication inventory.
        selection_bytes = (
            json.dumps(final_selection, sort_keys=True, indent=2) + "\n"
        ).encode()
        final_reference = {
            "path": delivery.repo_relative(successor / "observed-proof-selection.json"),
            "sha256": _digest(selection_bytes),
        }
        metadata["observed_proof_contract"]["selection"] = final_reference
        context["observed_proof_selection"] = final_reference
        manifest = {
            **receipt["effective_manifest"],
            "run_id": run_id,
            "created_at": delivery.utc_now(),
            "observed_proof_selection": final_reference,
        }
        for name, value in (
            ("run.json", metadata),
            ("recovery-context.json", context),
            ("observed-proof-selection.json", final_selection),
        ):
            delivery.write_json(staged / name, value)
        # Canonical serialization must match the bound observed-selection hash.
        (staged / "observed-proof-selection.json").write_bytes(selection_bytes)
        _write(staged / "manifest.json", manifest)
        _write(staged / "native-plan.json", proposal["plan"])
        admission = (
            delivery.RUNTIME_ROOT / "native-plans" / card.stem / "native-plan.json"
        )
        accepted_bytes = delivery._check_bytes(admission)
        if delivery._check_json_bytes(accepted_bytes) != proposal["plan"]:
            raise DeliveryError("admission changed during successor preparation")
        (staged / "native-plan.json").write_bytes(accepted_bytes)
        for path in staged.iterdir():
            descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        _sync(staged)
        _sync(staged.parent)
        _write(
            intent_path,
            {
                "schema": SCHEMA,
                "proposal_sha256": receipt["proposal_sha256"],
                "successor": run_id,
                "staged": staged.relative_to(directory).as_posix(),
                "inventory": _inventory(delivery, staged),
            },
        )
        successor = _publish_successor(delivery, previous, directory, receipt)
    metadata = delivery._check_json(successor / "run.json")
    return {
        "run_dir": successor,
        "run": metadata,
        "manifest": delivery._check_json(successor / "manifest.json"),
        "recovery_context": successor / "recovery-context.json",
    }
