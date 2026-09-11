"""Evidence adapter for the native OpenSpec delivery sequence.

Stock OpenSpec owns artifact interpretation. This module only binds semantic
sync, the exact archive move, and runner-assigned group sessions. It never
imports a historical finalization exception or grants publication authority.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.changerail import openspec_context as native
from scripts.changerail.contracts import DeliveryError


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _specs(delivery: Any) -> dict[str, str]:
    root = Path(delivery.REPO_ROOT) / "openspec/specs"
    if root.is_symlink() or any(p.is_symlink() for p in root.rglob("*")):
        raise DeliveryError("canonical specs must not contain symlinks")
    return {
        p.relative_to(root).as_posix(): _hash(p)
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def _sync_identity(delivery: Any, card: Path, report: Path) -> dict[str, Any]:
    raw = delivery._check_bytes(report)
    if not raw.strip():
        raise DeliveryError("semantic sync report is empty")
    return {
        "schema": "changerail.native-sync.v1",
        "change_id": native.change_id(card),
        "card_contract_sha256": native._card_contract(card),
        "artifacts": native.adapter(delivery).artifact_identity(
            native.change_root(delivery, card)
        ),
        "specs": _specs(delivery),
        "report": delivery.repo_relative(report),
        "report_sha256": hashlib.sha256(raw).hexdigest(),
    }


def record_sync(delivery: Any, card: Path, run_dir: Path, report: Path) -> None:
    if os.environ.get("CHRL_SESSION_ROLE") != "implementation":
        raise DeliveryError("native-sync requires the implementation role")
    if os.environ.get("CHRL_DELIVERY_STAGE") == "change":
        raise DeliveryError("semantic sync belongs to aggregate finalization")
    delivery.require_run_lifecycle(card, run_dir)
    native.require_plan(delivery, card, run_dir / "native-plan.json")
    native.require_complete(delivery, card)
    if (run_dir / "native-archive.json").exists():
        raise DeliveryError("archived semantic sync cannot be rewritten")
    report = report if report.is_absolute() else Path(delivery.REPO_ROOT) / report
    if not report.is_relative_to(run_dir) or report.resolve() != report:
        raise DeliveryError(
            "sync report must belong to the current run without symlinks"
        )
    native.adapter(delivery).validate_specs()
    identity = _sync_identity(delivery, card, report)
    target = run_dir / "native-sync.json"
    if target.exists():
        previous = delivery._check_json(target)
        if previous == identity:
            return
        history = run_dir / "native-sync-history"
        history.mkdir(exist_ok=True)
        delivery.write_json(
            history / f"{len(list(history.glob('*.json'))) + 1:03d}.json", previous
        )
    delivery.write_json(target, identity)


def require_sync(delivery: Any, card: Path, run_dir: Path) -> None:
    receipt = delivery._check_json(run_dir / "native-sync.json")
    report = Path(delivery.REPO_ROOT) / receipt["report"]
    if not report.is_relative_to(run_dir) or report.resolve() != report:
        raise DeliveryError("native sync report belongs to another run")
    if receipt != _sync_identity(delivery, card, report):
        raise DeliveryError("native semantic sync evidence is stale")


def _outside(delivery: Any, source: str, destination: str) -> dict[str, str]:
    return delivery.path_fingerprints(
        [
            p
            for p in delivery.changed_paths()
            if not p.startswith((source + "/", destination + "/"))
        ]
    )


def _archive_intents(delivery: Any, run_dir: Path) -> list[tuple[Path, dict[str, Any]]]:
    """Validate an append-only chain; successors may change only the UTC date."""
    initial = run_dir / "native-archive-intent.json"
    rows = [(initial, delivery._check_json(initial))]
    history = run_dir / "native-archive-intent-successors"
    if history.is_symlink():
        raise DeliveryError("linked archive intent history")
    for number, path in enumerate(sorted(history.glob("*.json")), 1):
        previous_path, previous = rows[-1]
        current = delivery._check_json(path)
        destination = current.get("destination", "")
        if not isinstance(destination, str):
            raise DeliveryError("archive intent successor destination is malformed")
        prefix = "openspec/changes/archive/"
        suffix = "-" + str(previous.get("change_id", ""))
        date = destination.removeprefix(prefix).removesuffix(suffix)
        try:
            valid_date = datetime.strptime(date, "%Y-%m-%d").date().isoformat() == date
        except ValueError:
            valid_date = False
        expected = {
            **previous,
            "destination": destination,
            "predecessor_sha256": hashlib.sha256(
                delivery._check_bytes(previous_path)
            ).hexdigest(),
        }
        old_target = Path(delivery.REPO_ROOT) / previous["destination"]
        if (
            path.name != f"{number:03d}.json"
            or current != expected
            or not valid_date
            or destination != prefix + date + suffix
            or destination <= previous["destination"]
            or old_target.exists()
            or old_target.is_symlink()
        ):
            raise DeliveryError(
                "archive intent successor does not match retained history"
            )
        rows.append((path, current))
    return rows


def archive_move(delivery: Any, card: Path, run_dir: Path) -> Path:
    """Retain intent before stock archive; interrupted exact moves can reconcile."""
    client = native.adapter(delivery)
    identifier = native.change_id(card)
    source = f"openspec/changes/{identifier}"
    intent_path = run_dir / "native-archive-intent.json"
    if intent_path.exists():
        intent = delivery._check_json(intent_path)
    else:
        date = datetime.now(timezone.utc).date().isoformat()
        destination = f"openspec/changes/archive/{date}-{identifier}"
        intent = {
            "schema": "changerail.native-archive-intent.v1",
            "change_id": identifier,
            "source": source,
            "destination": destination,
            "head": delivery.git("rev-parse", "HEAD").stdout.strip(),
            "artifacts": client.artifact_identity(Path(delivery.REPO_ROOT) / source),
            "raw_artifacts": client.artifact_identity(
                Path(delivery.REPO_ROOT) / source, normalize_tasks=False
            ),
            "tasks_complete": client.apply_context(identifier).tasks_complete,
            "outside": _outside(delivery, source, destination),
        }
        delivery.write_json(intent_path, intent)
    history = _archive_intents(delivery, run_dir)
    intent_path, intent = history[-1]
    destination = intent["destination"]
    target = Path(delivery.REPO_ROOT) / destination
    if (
        intent.get("change_id") != identifier
        or intent.get("source") != source
        or intent.get("tasks_complete") is not True
        or target.resolve() != target
        or target.parent != Path(delivery.REPO_ROOT) / "openspec/changes/archive"
        or intent["head"] != delivery.git("rev-parse", "HEAD").stdout.strip()
        or intent["outside"] != _outside(delivery, source, destination)
    ):
        raise DeliveryError("native archive intent does not match the current payload")
    active = Path(delivery.REPO_ROOT) / source
    if active.exists():
        if (
            client.artifact_identity(active, normalize_tasks=False)
            != intent["raw_artifacts"]
        ):
            raise DeliveryError("active artifacts changed after archive intent")
        date = datetime.now(timezone.utc).date().isoformat()
        if target.exists() or target.is_symlink():
            raise DeliveryError("archive destination exists alongside active artifacts")
        if target.name != f"{date}-{identifier}":
            successor_destination = f"openspec/changes/archive/{date}-{identifier}"
            successor_target = Path(delivery.REPO_ROOT) / successor_destination
            if (
                successor_destination <= destination
                or successor_target.resolve() != successor_target
                or successor_target.exists()
                or successor_target.is_symlink()
                or intent["outside"]
                != _outside(delivery, source, successor_destination)
            ):
                raise DeliveryError(
                    "archive date successor conflicts with retained payload"
                )
            successor = {
                **intent,
                "destination": successor_destination,
                "predecessor_sha256": hashlib.sha256(
                    delivery._check_bytes(intent_path)
                ).hexdigest(),
            }
            successor_path = (
                run_dir
                / "native-archive-intent-successors"
                / f"{len(history):03d}.json"
            )
            delivery.write_json(successor_path, successor)
            destination, target, intent = (
                successor_destination,
                successor_target,
                successor,
            )
        if client.archive(identifier) != target:
            raise DeliveryError("stock archive returned a foreign destination")
    if (
        not target.is_dir()
        or client.artifact_identity(target, normalize_tasks=False)
        != intent["raw_artifacts"]
        or intent["outside"] != _outside(delivery, source, destination)
    ):
        raise DeliveryError("archive changed more than the exact artifact move")
    return target


def inherit_archived_context(delivery: Any, previous: Path, current: Path) -> None:
    """Carry byte-proven methodology/history, never old execution proof as current."""
    if (previous / "native-archive-intent.json").exists():
        for source, _intent in _archive_intents(delivery, previous)[1:]:
            target = current / source.relative_to(previous)
            target.parent.mkdir(exist_ok=True)
            with target.open("xb") as stream:
                stream.write(delivery._check_bytes(source))
                stream.flush()
                os.fsync(stream.fileno())
    sync = delivery._check_json(previous / "native-sync.json")
    report = Path(delivery.REPO_ROOT) / sync["report"]
    if not report.is_relative_to(previous):
        raise DeliveryError("predecessor sync report is foreign")
    raw = delivery._check_bytes(report)
    if hashlib.sha256(raw).hexdigest() != sync["report_sha256"]:
        raise DeliveryError("predecessor sync report changed")
    target = current / "inherited-sync-report.md"
    target.write_bytes(raw)
    sync["report"] = delivery.repo_relative(target)
    delivery.write_json(current / "native-sync.json", sync)
    review = delivery._check_json(previous / "native-review-continuation.json")
    source = Path(delivery.REPO_ROOT) / review["preliminary"]
    if not source.is_relative_to(previous):
        raise DeliveryError("predecessor preliminary review is foreign")
    raw = delivery._check_bytes(source)
    if hashlib.sha256(raw).hexdigest() != review["preliminary_sha256"]:
        raise DeliveryError("predecessor preliminary review changed")
    target = current / "inherited-preliminary-review.json"
    target.write_bytes(raw)
    review["preliminary"] = delivery.repo_relative(target)
    review["origin"] = delivery.repo_relative(previous)
    delivery.write_json(current / "native-review-continuation.json", review)


def require_group(delivery: Any, card: Path, number: int) -> None:
    context = native.adapter(delivery).apply_context(native.change_id(card))
    tasks = [
        task for task in context.tasks if task.description.startswith(f"{number}.")
    ]
    if not tasks or any(not task.done for task in tasks):
        raise DeliveryError(f"native task group {number} is not complete")


def launch_groups(
    delivery: Any,
    *,
    card: Path,
    run_dir: Path,
    current_profile: dict[str, Any],
    recovery_context: Path | None,
) -> None:
    plan = delivery.declared_change_plan(run_dir)
    if not plan:
        raise DeliveryError("native group sessions require a frozen task plan")
    for number, _slug in plan:
        states = delivery.change_checkpoint_statuses(
            plan, delivery.combined_change_events(run_dir)
        )
        state = next(row for row in states if row["number"] == number)
        if state["status"] == "complete":
            require_group(delivery, card, number)
            continue
        native.require_plan(delivery, card, run_dir / "native-plan.json")
        before_tasks = (
            native.adapter(delivery).apply_context(native.change_id(card)).tasks
        )
        context_path = run_dir / "native-context.json"
        delivery.write_json(context_path, native.delivery_context(delivery, card))
        model, reasoning = delivery.model_route(current_profile, "implementation")
        env = {
            "CHRL_NATIVE_CONTEXT": str(context_path),
            "CHRL_DELIVERY_STAGE": "change",
            "CHRL_CHANGE_NUMBER": str(number),
            "CHRL_CHANGE_NEXT_EVENT": "complete"
            if state["status"] == "started"
            else "starting",
        }
        if recovery_context:
            env.update(
                CHRL_RECOVERY_RUN="1", CHRL_RECOVERY_CONTEXT=str(recovery_context)
            )
        code = delivery.launch_codex(
            role="implementation",
            prompt=f"$chrl-native-deliver {delivery.repo_relative(card)}",
            model=model,
            reasoning=reasoning,
            run_dir=run_dir,
            timeout_minutes=int(current_profile["max_wall_minutes"]),
            session_env=env,
            resume_thread_id=None,
            require_first_file_change=state["status"] == "pending",
        )
        if code:
            raise DeliveryError(f"native group {number} session exited with {code}")
        native.require_plan(delivery, card, run_dir / "native-plan.json")
        after_tasks = (
            native.adapter(delivery).apply_context(native.change_id(card)).tasks
        )
        outside_before = {
            task.id: task.done
            for task in before_tasks
            if not task.description.startswith(f"{number}.")
        }
        outside_after = {
            task.id: task.done
            for task in after_tasks
            if not task.description.startswith(f"{number}.")
        }
        if outside_before != outside_after:
            raise DeliveryError("native session changed another task group's progress")
        require_group(delivery, card, number)
        states = delivery.change_checkpoint_statuses(
            plan, delivery.combined_change_events(run_dir)
        )
        if (
            next(row for row in states if row["number"] == number)["status"]
            != "complete"
        ):
            raise DeliveryError(f"native group {number} lacks its completion event")


def checkpoint(
    delivery: Any, card: Path, run_dir: Path, phase: str, stage: str
) -> None:
    """A completion event needs checked tasks and validated current QA evidence."""
    assigned = os.environ.get("CHRL_CHANGE_NUMBER")
    if (
        os.environ.get("CHRL_DELIVERY_STAGE") == "change"
        and phase != f"change-{assigned}"
    ):
        raise DeliveryError("session attempted another task group's checkpoint")
    if stage == "complete":
        require_group(delivery, card, int(phase.split("-")[1]))
        if not any(
            row.get("proof_status") == "current"
            for row in delivery.focused_evidence_summaries(run_dir)
        ):
            raise DeliveryError(
                "native checkpoint requires validated current focused evidence"
            )


def retain_provisional(
    delivery: Any, card: Path, run_dir: Path, cycle: int, verdict: Path, session: Path
) -> None:
    metrics = delivery.parse_session_metrics(session)
    thread = metrics.get("thread_id")
    if not isinstance(thread, str) or not thread:
        raise DeliveryError(
            "native provisional review did not retain a reviewer thread"
        )
    history = run_dir / "reviews"
    destination = history / f"cycle-{cycle:02d}-provisional.json"
    if destination.exists() and destination.read_bytes() != verdict.read_bytes():
        raise DeliveryError("native preliminary verdict history conflicts")
    destination.write_bytes(verdict.read_bytes())
    for suffix in ("context", "manifest"):
        source = history / f"cycle-{cycle:02d}-{suffix}.json"
        (history / f"cycle-{cycle:02d}-provisional-{suffix}.json").write_bytes(
            source.read_bytes()
        )
    state = {
        "schema": "changerail.native-review-continuation.v1",
        "card": delivery.repo_relative(card),
        "cycle": cycle,
        "thread_id": thread,
        "before": delivery.payload_fingerprint(),
        "commands": metrics.get("review_investigative_command_count", 0),
        "preliminary": delivery.repo_relative(destination),
        "preliminary_sha256": _hash(destination),
        "complete": False,
    }
    previous = run_dir / "native-review-continuation.json"
    if previous.exists():
        old = delivery._check_json(previous)
        if not old.get("complete"):
            raise DeliveryError("another native review continuation is pending")
        delivery.write_json(
            history / f"cycle-{old['cycle']:02d}-continuation.json", old
        )
    delivery.write_json(previous, state)


def pending_review(delivery: Any, card: Path, run_dir: Path) -> dict[str, Any] | None:
    path = run_dir / "native-review-continuation.json"
    if not path.exists():
        return None
    state = delivery._check_json(path)
    if state.get("card") != delivery.repo_relative(card):
        raise DeliveryError("native review continuation belongs to another card")
    source = Path(delivery.REPO_ROOT) / state["preliminary"]
    if not source.is_relative_to(run_dir):
        raise DeliveryError("native preliminary review is outside its run")
    raw = delivery._check_bytes(source)
    if hashlib.sha256(raw).hexdigest() != state["preliminary_sha256"]:
        raise DeliveryError("native preliminary verdict changed")
    verdict = json.loads(raw)
    if verdict.get("result") != "go" or verdict.get("workspace") != state["before"]:
        raise DeliveryError("native preliminary verdict is not its recorded GO")
    return None if state.get("complete") else state


def require_final_review(delivery: Any, card: Path, run_dir: Path) -> None:
    native.require_plan(delivery, card, run_dir / "native-plan.json")
    require_sync(delivery, card, run_dir)
    state = delivery._check_json(run_dir / "native-review-continuation.json")
    current = delivery.verdict_path(delivery.card_id(card))
    if (
        not (run_dir / "native-archive.json").is_file()
        or state.get("complete") is not True
        or state.get("card") != delivery.repo_relative(card)
        or state.get("result") != "go"
        or state.get("final") != delivery.payload_fingerprint()
        or state.get("final_verdict_sha256") != _hash(current)
    ):
        raise DeliveryError(
            "native final floor requires the completed post-archive review"
        )


def retained_run(
    delivery: Any, value: Path, *, read_only: bool = False
) -> tuple[Path, dict[str, Any]]:
    path = value if value.is_absolute() else Path(delivery.REPO_ROOT) / value
    roots = {delivery.RUNTIME_ROOT / "runs"}
    if read_only:
        roots.update(
            delivery.RUNTIME_ROOT / name
            for name in ("delivery-runs", "ff-runs", "offline-finalizations")
        )
    if path.parent not in roots or path.resolve() != path:
        raise DeliveryError(
            "select an exact local retained run directory without symlinks"
        )
    return path, delivery._check_json(path / "run.json")


def status(delivery: Any, value: Path) -> dict[str, Any]:
    run_dir, metadata = retained_run(delivery, value, read_only=True)
    plan = delivery.declared_change_plan(run_dir) or []
    events = delivery.combined_change_events(run_dir)
    return {
        "schema": "changerail.native-run-status.v1",
        "run": delivery.repo_relative(run_dir),
        "card": metadata.get("card"),
        "lifecycle": metadata.get("lifecycle_mode", "board-only"),
        "checkpoints": delivery.change_checkpoint_statuses(plan, events),
        "last_event": events[-1] if events else None,
        "archived": (run_dir / "native-archive.json").is_file(),
        "note": "Retained history only; status does not authorize or prove recovery.",
    }
