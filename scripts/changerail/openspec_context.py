"""Map one board card to one stock OpenSpec change and its task groups."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from scripts.changerail.contracts import DeliveryError
from scripts.changerail.openspec_adapter import OpenSpecAdapter

_SLUG = r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*"


def _section(card: Path, name: str) -> str:
    matches = re.findall(
        rf"^## {re.escape(name)}\n(.*?)(?=^## |\Z)",
        card.read_text(encoding="utf-8"),
        re.MULTILINE | re.DOTALL,
    )
    if len(matches) > 1:
        raise DeliveryError(f"duplicate card section: {name}")
    return matches[0].strip() if matches else ""


def lifecycle_mode(card: Path) -> str:
    """Return explicit execution mode while preserving unmarked closed history."""

    marker = _section(card, "Lifecycle")
    if not marker:
        if card.parent.name in {"4.done", "5.canceled"}:
            return "board-only-history"
        raise DeliveryError(
            "executable cards require an explicit ## Lifecycle value: "
            "openspec-v1 for native delivery"
        )
    if marker not in {"openspec-v1", "board-only"}:
        raise DeliveryError(f"unsupported card lifecycle: {marker}")
    return marker


def is_native(card: Path) -> bool:
    return lifecycle_mode(card) == "openspec-v1"


def require_owned_artifacts(delivery: Any, extra: set[str], frozen: set[str]) -> None:
    """New artifact trees need a native card; old tree contents cannot grow."""
    if not extra:
        return
    owners: dict[str, Path] = {}
    for card in (Path(delivery.REPO_ROOT) / "openspec/board").glob("*/*.md"):
        if _section(card, "Lifecycle") != "openspec-v1":
            continue
        try:
            identifier = change_id(card)
        except DeliveryError:
            # Planning cards may precede their linked native change. They own
            # no tree until that declaration is valid; accepted cards stay strict.
            if card.parent.name == "1.backlog":
                continue
            raise
        if identifier in owners:
            raise DeliveryError(f"native change has multiple card owners: {identifier}")
        owners[identifier] = card

    def tree(name: str) -> str:
        parts = Path(name).parts
        return "/".join(parts[:4] if parts[2] == "archive" else parts[:3])

    old_trees = {tree(name) for name in frozen}
    for name in sorted(extra):
        scope = tree(name)
        leaf = Path(scope).name
        identifier = (
            re.sub(r"^\d{4}-\d{2}-\d{2}-", "", leaf) if "/archive/" in scope else leaf
        )
        if (
            scope in old_trees
            or identifier not in owners
            or scope == "openspec/changes/archive"
        ):
            raise DeliveryError(
                f"legacy lifecycle contains an unowned addition: {name}"
            )


def change_id(card: Path) -> str:
    if not is_native(card):
        raise DeliveryError("openspec-v1 lifecycle is required")
    match = re.fullmatch(rf"1\. `({_SLUG})`", _section(card, "OpenSpec Changes"))
    if match is None or match.group(1) == "archive":
        raise DeliveryError(
            "openspec-v1 requires exactly one ordered entry in ## OpenSpec Changes: "
            "1. `change-id`"
        )
    return match.group(1)


def adapter(delivery: Any) -> OpenSpecAdapter:
    return OpenSpecAdapter(Path(delivery.REPO_ROOT))


def _archive_receipt(delivery: Any) -> tuple[Path, dict[str, Any]] | None:
    raw = os.environ.get("CHRL_RUN_DIR")
    if not raw:
        return None
    run_dir = Path(raw).resolve(strict=False)
    if not run_dir.is_relative_to(
        Path(delivery.REPO_ROOT) / ".runtime/changerail/runs"
    ):
        raise DeliveryError("native archive receipt run is outside local runtime")
    path = run_dir / "native-archive.json"
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DeliveryError("native archive receipt is malformed") from exc
    if not isinstance(value, dict):
        raise DeliveryError("native archive receipt is malformed")
    return path, value


def carry_archive_receipt(delivery: Any, previous: Path, current: Path) -> bool:
    """Copy an exact predecessor archive receipt into a fresh recovery run."""

    runs = (Path(delivery.REPO_ROOT) / ".runtime/changerail/runs").resolve()
    previous = previous.resolve(strict=False)
    current = current.resolve(strict=False)
    if previous.parent != runs or current.parent != runs or previous == current:
        raise DeliveryError(
            "native recovery runs must be distinct local run directories"
        )
    source = previous / "native-archive.json"
    if not source.is_file():
        return False
    raw = source.read_bytes()
    try:
        receipt = json.loads(raw)
    except ValueError as exc:
        raise DeliveryError("predecessor native archive receipt is malformed") from exc
    if (
        not isinstance(receipt, dict)
        or receipt.get("schema") != "changerail.openspec-archive.v1"
    ):
        raise DeliveryError("predecessor native archive receipt is malformed")
    target = current / "native-archive.json"
    with target.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    if target.read_bytes() != raw:
        raise DeliveryError("native archive recovery receipt copy is incomplete")
    return True


def change_root(delivery: Any, card: Path) -> Path:
    client = adapter(delivery)
    if (
        _archive_receipt(delivery) is not None
        and (Path(delivery.REPO_ROOT) / "openspec/changes" / change_id(card)).exists()
    ):
        raise DeliveryError("archived change cannot also have an active artifact tree")
    try:
        return client.change_root(change_id(card))
    except DeliveryError:
        selected = _archive_receipt(delivery)
        if selected is None:
            raise
        _path, receipt = selected
        if receipt.get("change_id") != change_id(card):
            raise DeliveryError("native archive belongs to a different card")
        relative = receipt.get("destination")
        if not isinstance(relative, str):
            raise DeliveryError("native archive destination is missing")
        root = (Path(delivery.REPO_ROOT) / relative).resolve(strict=True)
        if not root.is_dir() or not root.is_relative_to(
            Path(delivery.REPO_ROOT) / "openspec/changes/archive"
        ):
            raise DeliveryError("native archive destination escapes the repository")
        return root


def task_groups(delivery: Any, card: Path) -> list[tuple[int, str]]:
    text = (change_root(delivery, card) / "tasks.md").read_text(encoding="utf-8")
    groups = [
        (int(number), slug)
        for number, slug in re.findall(
            rf"^## ([1-9][0-9]*)\. ({_SLUG})$", text, re.MULTILINE
        )
    ]
    headings = re.findall(r"^## .+$", text, re.MULTILINE)
    if (
        not groups
        or len(headings) != len(groups)
        or [number for number, _ in groups] != list(range(1, len(groups) + 1))
        or len({slug for _, slug in groups}) != len(groups)
    ):
        raise DeliveryError(
            "OpenSpec tasks.md requires contiguous unique task-group headings: "
            "## 1. group-slug"
        )
    return groups


def _card_contract(card: Path) -> str:
    immutable = re.sub(
        r"^## (?:Status|Result|Log)\n.*?(?=^## |\Z)",
        "",
        card.read_text(encoding="utf-8"),
        flags=re.MULTILINE | re.DOTALL,
    )
    return hashlib.sha256(immutable.encode()).hexdigest()


def plan_identity(delivery: Any, card: Path) -> dict[str, Any]:
    client = adapter(delivery)
    identifier = change_id(card)
    client.inspect_complete_plan(identifier)
    client.validate_change(identifier)
    context = client.apply_context(identifier)
    groups = task_groups(delivery, card)
    # Upstream IDs are flat ordinals; X.Y is retained in its task description.
    numbers = [
        re.match(r"([1-9][0-9]*)\.([1-9][0-9]*)\s", task.description)
        for task in context.tasks
    ]
    if (
        any(match is None for match in numbers)
        or {int(match[1]) for match in numbers if match}
        != {number for number, _ in groups}
        or len({match[0] for match in numbers if match}) != len(numbers)
    ):
        raise DeliveryError(
            "native task descriptions must identify every numbered group uniquely"
        )
    identity = client.identity(identifier)
    identity.update(
        {
            "card_contract_sha256": _card_contract(card),
            "groups": [[number, slug] for number, slug in groups],
            "task_count": len(context.tasks),
        }
    )
    return identity


def require_plan(delivery: Any, card: Path, receipt: Path) -> None:
    path = receipt / "native-plan.json" if receipt.is_dir() else receipt
    try:
        retained = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DeliveryError("accepted native OpenSpec plan receipt is absent") from exc
    client = adapter(delivery)
    try:
        current = plan_identity(delivery, card)
    except DeliveryError:
        selected = _archive_receipt(delivery)
        if selected is None:
            raise
        _path, archive = selected
        root = change_root(delivery, card)
        current = dict(retained)
        current["artifacts"] = client.artifact_identity(root)
        if (
            archive.get("schema") != "changerail.openspec-archive.v1"
            or archive.get("change_id") != change_id(card)
            or archive.get("plan") != retained
            or archive.get("artifacts") != current["artifacts"]
            or archive.get("raw_artifacts")
            != client.artifact_identity(root, normalize_tasks=False)
            or archive.get("tasks_complete") is not True
            or archive.get("card_contract_sha256") != _card_contract(card)
        ):
            raise DeliveryError("native archive receipt is stale")
    if retained != current:
        raise DeliveryError(
            "accepted native OpenSpec plan changed; explicit replan required"
        )


def require_complete(delivery: Any, card: Path) -> None:
    selected = _archive_receipt(delivery)
    if selected is not None:
        _path, receipt = selected
        root = change_root(delivery, card)
        if (
            receipt.get("schema") != "changerail.openspec-archive.v1"
            or receipt.get("change_id") != change_id(card)
            or receipt.get("tasks_complete") is not True
            or receipt.get("card_contract_sha256") != _card_contract(card)
            or receipt.get("artifacts") != adapter(delivery).artifact_identity(root)
            or receipt.get("raw_artifacts")
            != adapter(delivery).artifact_identity(root, normalize_tasks=False)
        ):
            raise DeliveryError("archived OpenSpec tasks lack completion proof")
        return
    context = adapter(delivery).apply_context(change_id(card))
    if not context.tasks_complete:
        raise DeliveryError("OpenSpec tasks are not all complete")


def archive(delivery: Any, card: Path, run_dir: Path) -> dict[str, Any]:
    """Execute stock sync/archive once and retain its exact byte identity."""

    target = run_dir / "native-archive.json"
    if target.exists():
        require_plan(delivery, card, run_dir / "native-plan.json")
        return json.loads(target.read_text(encoding="utf-8"))
    from scripts.changerail.native_workflow import archive_move, require_sync

    client = adapter(delivery)
    active = Path(delivery.REPO_ROOT) / "openspec/changes" / change_id(card)
    if active.exists():
        require_plan(delivery, card, run_dir / "native-plan.json")
        require_complete(delivery, card)
        require_sync(delivery, card, run_dir)
    elif not (run_dir / "native-archive-intent.json").exists():
        raise DeliveryError("missing active change has no retained archive intent")
    plan = json.loads((run_dir / "native-plan.json").read_text(encoding="utf-8"))
    destination = archive_move(delivery, card, run_dir)
    if plan.get("artifacts") != client.artifact_identity(destination) or plan.get(
        "card_contract_sha256"
    ) != _card_contract(card):
        raise DeliveryError("archived artifacts do not match the accepted plan")
    payload = {
        "schema": "changerail.openspec-archive.v1",
        "change_id": change_id(card),
        "destination": destination.relative_to(delivery.REPO_ROOT).as_posix(),
        "artifacts": client.artifact_identity(destination),
        "raw_artifacts": client.artifact_identity(destination, normalize_tasks=False),
        "plan": plan,
        "tasks_complete": True,
        "card_contract_sha256": _card_contract(card),
        "archived_at": delivery.utc_now(),
    }
    delivery.write_json(target, payload)
    require_plan(delivery, card, run_dir / "native-plan.json")
    require_sync(delivery, card, run_dir)
    return payload


def delivery_context(delivery: Any, card: Path) -> dict[str, Any]:
    """Return live stock apply context or exact retained archived context."""
    workflows = {
        name: adapter(delivery).workflow(name) for name in ("apply", "sync", "verify")
    }

    selected = _archive_receipt(delivery)
    if selected is not None:
        _path, receipt = selected
        root = change_root(delivery, card)
        return {
            "schema": "changerail.openspec-context.v1",
            "change_id": change_id(card),
            "state": "archived",
            "workflows": workflows,
            "tasks": [],
            "context_files": [
                path.relative_to(delivery.REPO_ROOT).as_posix()
                for path in sorted(root.rglob("*.md"))
            ],
            "instruction": (
                "The stock change is archived after provisional GO. Do not edit "
                "product code or archived artifacts; refresh card/evidence handoff."
            ),
            "archive": receipt,
        }
    context = adapter(delivery).apply_context(change_id(card))
    return {
        "schema": "changerail.openspec-context.v1",
        "change_id": change_id(card),
        "state": context.state,
        "workflows": workflows,
        "tasks": [task.__dict__ for task in context.tasks],
        "context_files": [
            path.relative_to(delivery.REPO_ROOT).as_posix()
            for path in context.context_files
        ],
        "instruction": context.instruction,
    }
