"""Small project-local delivery runner for controlled ChangeRail experiments."""

from __future__ import annotations
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import math
import os
import re
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import threading
import time
import tomllib
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Mapping, NamedTuple, Protocol, Sequence

_SOURCE_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_SOURCE_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_SOURCE_REPO_ROOT))
from scripts.changerail.contracts import DeliveryError
from scripts.changerail import openspec_context as native
from scripts.changerail.adapters.results import validate_selected_nodes, receipt_nodes
from scripts.changerail.targeted_checks import select_targeted_commands

from scripts.changerail import source_binding

REPO_ROOT = source_binding.project_root(_SOURCE_REPO_ROOT)
BOARD_ROOT = REPO_ROOT / "openspec" / "board"
BOARD_COLUMNS = ("1.backlog", "2.todo", "3.inprogress", "4.done", "5.canceled")


def execution_identity() -> dict[str, str]:
    """Freeze local code, schemas, skills, profile and launcher bytes for execution."""
    launcher = (
        profile().get("adapters", {}).get("codex", {}).get("launcher", "bin/codex")
    )
    paths = [
        PROFILE_PATH,
        REPO_ROOT / "bin/chrl",
        REPO_ROOT / "bin/chrl-run",
        REPO_ROOT / "bin/openspec",
        REPO_ROOT / "scripts/__init__.py",
        REPO_ROOT / "tools/openspec/workflow-instructions.mjs",
        REPO_ROOT / "tools/openspec/check-install.mjs",
        REPO_ROOT / "tools/openspec/package.json",
        REPO_ROOT / "tools/openspec/package-lock.json",
        REPO_ROOT / "tools/openspec/bootstrap.sh",
        REPO_ROOT / _safe_path(launcher),
        REPO_ROOT / ".changerail/distribution-lock.json",
        REPO_ROOT / ".changerail/source-link.json",
    ]
    for directory in (
        "scripts/changerail",
        "tools/changerail/schemas",
        "tools/changerail/skills",
        ".changerail/adapters",
    ):
        paths.extend(
            (
                path
                for path in (REPO_ROOT / directory).rglob("*")
                if path.is_file() and "__pycache__" not in path.parts
            )
        )
    return {
        path.relative_to(REPO_ROOT).as_posix(): hashlib.sha256(
            source_binding.read_runtime(REPO_ROOT, path, _check_bytes)
        ).hexdigest()
        for path in sorted(set(paths))
        if path.is_file()
    }


def recovery_ancestors(run_dir: Path) -> list[Path]:
    ancestors = []
    seen = {run_dir.name}
    current = run_dir
    while True:
        metadata = require_current_execution(current)
        previous = metadata.get("recovery_of")
        if previous is None:
            return ancestors
        if (
            not isinstance(previous, str)
            or not re.fullmatch("[A-Za-z0-9][A-Za-z0-9._-]*", previous)
            or previous in seen
        ):
            raise DeliveryError("invalid recovery ancestry")
        current = RUNTIME_ROOT / "runs" / previous
        if current.resolve() != current:
            raise DeliveryError("linked recovery ancestor")
        seen.add(previous)
        ancestors.append(current)


def _publication_route() -> dict[str, str]:
    branch = git("branch", "--show-current").stdout.strip()
    remote = git("config", "--get", f"branch.{branch}.remote").stdout.strip()
    ref = git("config", "--get", f"branch.{branch}.merge").stdout.strip()
    if not remote or not ref.startswith("refs/heads/"):
        raise DeliveryError("publication requires an exact configured upstream")
    urls = git("remote", "get-url", "--push", "--all", remote).stdout.splitlines()
    if len(urls) != 1:
        raise DeliveryError("publication push destination must be unique")
    return {
        "branch": branch,
        "remote": remote,
        "ref": ref,
        "url_sha256": hashlib.sha256(urls[0].encode()).hexdigest(),
    }


def resume_publication(run_dir: Path) -> int:
    """Only push the exact retained committed result; never create a new commit."""
    require_frozen_execution(run_dir)
    receipt = _check_json(run_dir / "publication.json")
    if receipt.get("schema") != "changerail.publication.v1" or receipt.get(
        "state"
    ) not in {"committed", "pushed"}:
        raise DeliveryError("publication has no proven committed receipt")
    commit = git("rev-parse", "HEAD").stdout.strip()
    if (
        commit != receipt.get("commit")
        or changed_paths()
        or git("rev-parse", "HEAD^{tree}").stdout.strip() != receipt.get("tree")
        or (git("rev-parse", "HEAD^").stdout.strip() != receipt.get("parent"))
        or (_publication_route() != receipt.get("destination"))
    ):
        raise DeliveryError(
            "publication receipt no longer matches exact HEAD, tree or destination"
        )
    for relative, digest in receipt.get("evidence", {}).items():
        if (
            hashlib.sha256(
                _check_bytes(REPO_ROOT / _safe_path(relative), 32 * 1024 * 1024)
            ).hexdigest()
            != digest
        ):
            raise DeliveryError("publication evidence changed after commit")
    if not receipt.get("evidence"):
        raise DeliveryError("publication evidence is absent")
    if receipt["state"] == "pushed":
        return 0
    destination = receipt["destination"]
    result = git(
        "push", destination["remote"], f"{commit}:{destination['ref']}", check=False
    )
    if result.returncode == 0:
        receipt.update(state="pushed", pushed_at=utc_now())
        write_json(run_dir / "publication.json", receipt)
    return result.returncode


def require_frozen_execution(run_dir: Path) -> dict[str, Any]:
    metadata = require_current_execution(run_dir)
    from scripts.changerail.runtime_repair import effective_identity
    from scripts.changerail import plan_restoration

    identity = plan_restoration.effective_identity(runner_module(), run_dir, metadata)
    if identity is None:
        identity = effective_identity(runner_module(), run_dir, metadata)
    if identity != execution_identity():
        raise DeliveryError(
            "frozen execution process changed; ordinary recovery cannot adopt new code or profile"
        )
    return metadata


def require_current_execution(run_dir: Path) -> dict[str, Any]:
    lock_path = REPO_ROOT / ".changerail/distribution-lock.json"
    if lock_path.exists() or lock_path.is_symlink():
        try:
            lock = _check_json(lock_path)
            retained = lock.get("retained_read_only_runs")
            if lock.get("schema") != "changerail.installation.v1" or not isinstance(
                retained, dict
            ):
                raise ValueError("invalid distribution installation lock")
            if repo_relative(run_dir / "run.json") in retained:
                raise DeliveryError(
                    "historical adopted run is read-only under the distribution lock"
                )
        except (OSError, ValueError) as exc:
            raise DeliveryError(
                f"unsafe distribution installation lock: {exc}"
            ) from exc
    try:
        metadata = _check_json(run_dir / "run.json")
    except (OSError, ValueError, RecursionError) as exc:
        raise DeliveryError(f"unsafe current execution owner: {exc}") from exc
    if (
        metadata.get("execution_contract") != "changerail.native.v1"
        or metadata.get("mode") != "delivery"
        or metadata.get("lifecycle_mode") != "openspec-v1"
    ):
        raise DeliveryError(
            "historical run is read-only; a current native execution contract is required"
        )
    return metadata


PROFILE_PATH = REPO_ROOT / ".changerail" / "profile.toml"
VERDICT_SCHEMA_PATH = (
    REPO_ROOT / "tools" / "changerail" / "schemas" / "review-verdict.schema.json"
)
CARD_EVIDENCE_SCHEMA_PATH = (
    REPO_ROOT / "tools" / "changerail" / "schemas" / "card-evidence.schema.json"
)
CHECK_RESULT_SCHEMA_PATH = (
    REPO_ROOT / "tools/changerail/schemas/check-result.schema.json"
)
CARD_PROOF_SCHEMA_PATH = REPO_ROOT / "tools/changerail/schemas/card-proof.schema.json"
VERDICT_V2_SCHEMA_PATH = (
    REPO_ROOT / "tools/changerail/schemas/review-verdict-v2.schema.json"
)
RUNTIME_ROOT = REPO_ROOT / ".runtime" / "changerail"
EXCLUDED_PREFIXES = (
    ".runtime/",
    "runtime/",
    ".ai/",
    ".ai1c/",
    ".codex/auth.json",
    ".codex/auth.toml",
    ".codex/sessions/",
    ".codex/.tmp/",
    ".codex/tmp/",
    "artifacts/",
)
TOKEN_USAGE_KEYS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)


def runner_module() -> Any:
    """Return this loaded runner, including importlib-loaded test instances."""
    return sys.modules.get(__name__) or SimpleNamespace(**globals())


REVIEW_BUDGET_KEYS = ("semantic_cycles",)
BOARD_REFERENCE_PATTERN = re.compile(
    "openspec/board/(?:1\\.backlog|2\\.todo|3\\.inprogress|4\\.done|5\\.canceled)/[A-Za-z0-9._-]+\\.md"
)
LOG_TIMESTAMP_PATTERN = re.compile("\\b\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z\\b")


class _Digest(Protocol):
    def update(self, value: bytes) -> None: ...


class _SessionCommandBudget:
    """Track the reactive shell-command ceiling for one streamed Codex session."""

    def __init__(
        self,
        role: str,
        budgets: dict[str, Any],
        *,
        require_first_file_change: bool = True,
        inherited_investigative_commands: int = 0,
    ) -> None:
        self.role = role
        self.enforced = budget_limits_enforced({"budgets": budgets})
        self.command_count = inherited_investigative_commands
        self.inherited_command_count = inherited_investigative_commands
        self.session_command_count = 0
        self.file_change_started = False
        self.metric: str | None
        self.limit: int
        self.verdict_only_limit: int
        self.hard_stop_limit: int
        self.verdict_only_started_at: int | None = None
        if role == "implementation" and require_first_file_change:
            self.metric = "investigative_commands_before_first_file_change"
            self.limit = int(budgets.get("first_edit_discovery_commands", 8))
            self.verdict_only_limit = self.limit
            self.hard_stop_limit = int(
                budgets.get("first_edit_hard_stop_commands", self.limit)
            )
            if not 0 <= self.limit <= self.hard_stop_limit:
                raise DeliveryError(
                    "implementation command budgets must satisfy target <= hard-stop"
                )
        elif role == "review":
            self.metric = "review_investigative_command_count"
            self.limit = int(budgets.get("review_commands", 12))
            configured_hard_stop = int(
                budgets.get("review_hard_stop_commands", max(self.limit, 20))
            )
            self.verdict_only_limit = int(
                budgets.get(
                    "review_verdict_only_commands",
                    min(configured_hard_stop, max(self.limit, 20)),
                )
            )
            self.hard_stop_limit = configured_hard_stop
            if not self.limit <= self.verdict_only_limit <= self.hard_stop_limit:
                raise DeliveryError(
                    "review command budgets must satisfy target <= verdict-only <= hard-stop"
                )
        else:
            self.metric = None
            self.limit = 0
            self.verdict_only_limit = 0
            self.hard_stop_limit = 0

    def observe(self, event: dict[str, Any]) -> dict[str, Any] | None:
        """Return violation details when a streamed command crosses the limit."""
        if event.get("type") != "item.started":
            return None
        item_value = event.get("item")
        item: dict[str, Any] = item_value if isinstance(item_value, dict) else {}
        if item.get("type") == "file_change":
            self.file_change_started = True
            return None
        if item.get("type") != "command_execution" or self.metric is None:
            return None
        if self.role == "implementation" and self.file_change_started:
            return None
        command = str(item.get("command", "") or "")
        if self.role == "implementation" and is_delivery_protocol_command(command):
            return None
        if self.role == "review" and is_review_protocol_command(command):
            return None
        self.command_count += 1
        self.session_command_count += 1
        if not self.enforced:
            return None
        if (
            self.role == "review"
            and self.verdict_only_started_at is None
            and (self.command_count >= self.verdict_only_limit)
        ):
            self.verdict_only_started_at = self.command_count
        if self.command_count <= self.hard_stop_limit:
            return None
        return {
            "schema": "changerail.command-budget-violation.v1",
            "role": self.role,
            "metric": self.metric,
            "budget": self.limit,
            "hard_stop_budget": self.hard_stop_limit,
            "observed": self.command_count,
            "command_id": str(item.get("id") or "unknown"),
            "item_type": "command_execution",
        }

    def snapshot(self) -> dict[str, Any]:
        """Return the final command-budget state without command contents."""
        return {
            "metric": self.metric,
            "enforced": self.enforced,
            "target": self.limit,
            "verdict_only_at": self.verdict_only_limit
            if self.role == "review"
            else None,
            "hard_stop": self.hard_stop_limit,
            "observed": self.command_count,
            "inherited": self.inherited_command_count,
            "session_observed": self.session_command_count,
            "target_exceeded": self.command_count > self.limit,
            "verdict_only_entered": self.verdict_only_started_at is not None,
            "hard_stop_exceeded": self.command_count > self.hard_stop_limit,
        }


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DeliveryError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise DeliveryError(f"expected JSON object in {path}")
    return payload


def profile() -> dict[str, Any]:
    try:
        configured = tomllib.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise DeliveryError(f"cannot read local delivery profile: {exc}") from exc
    if configured.get("schema") != "changerail.local-delivery.v1":
        raise DeliveryError("profile schema must be changerail.local-delivery.v1")
    cycles = configured.get("max_review_cycles", 2)
    if type(cycles) is not int or cycles != 2:
        raise DeliveryError("max_review_cycles must be exactly 2")
    retired = {
        "max_terminal_semantic_repair_reviews",
        "max_post_verification_repair_reviews",
        "offline_finalization",
    }
    if retired.intersection(configured):
        raise DeliveryError(
            "retired review allowances or offline finalization in profile"
        )
    models = configured.get("models", {})
    if not isinstance(models, dict) or set(models) - {"implementation", "review"}:
        raise DeliveryError("profile models permit only implementation and review")
    if not isinstance(configured.get("budgets", {}), dict):
        raise DeliveryError("profile budgets must be a table")
    budget_limits_enforced(configured)
    return configured


def budget_limits_enforced(current_profile: Mapping[str, Any] | None = None) -> bool:
    """Numerical ceilings are optional; measurements and authority gates are not."""
    configured = profile() if current_profile is None else current_profile
    value = configured.get("budgets", {}).get("enforce_limits", True)
    if type(value) is not bool:
        raise DeliveryError("budgets.enforce_limits must be a boolean")
    return value


def git(
    *args: str, check: bool = True, text: bool = True
) -> subprocess.CompletedProcess[Any]:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=text,
        check=False,
    )
    if check and result.returncode:
        stderr = result.stderr if text else result.stderr.decode(errors="replace")
        stdout = result.stdout if text else result.stdout.decode(errors="replace")
        raise DeliveryError(
            stderr.strip() or stdout.strip() or f"git {' '.join(args)} failed"
        )
    return result


def repo_relative(path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise DeliveryError(f"path is outside repository: {path}") from exc


def resolve_card(value: str | Path) -> Path:
    requested = Path(value)
    direct = requested if requested.is_absolute() else REPO_ROOT / requested
    if direct.is_file():
        resolved = direct.resolve()
        if not resolved.is_relative_to(BOARD_ROOT.resolve()):
            raise DeliveryError(f"card is outside the board: {value}")
        return resolved
    matches = sorted(BOARD_ROOT.glob(f"*/{requested.name}"))
    if len(matches) != 1:
        raise DeliveryError(
            f"card resolution expected one match for {value}, found {len(matches)}"
        )
    return matches[0].resolve()


def card_id(path: Path) -> str:
    return path.stem


def checked_frozen_records() -> dict[Path, str]:
    """Validate project-owned frozen history without embedding project identities."""
    configured = profile().get("history", {}).get("manifest")
    if configured is None:
        return {}
    manifest = load_json(REPO_ROOT / _safe_path(configured))
    if manifest.get("schema") != "changerail.project-history.v1":
        raise DeliveryError("unsupported project history manifest")
    records = {}
    for relative, record in manifest.get("board_records", {}).items():
        try:
            path = REPO_ROOT / _safe_path(relative)
            if not relative.startswith("openspec/board/") or record.get(
                "disposition"
            ) not in {"superseded-no-go", "suspended-not-verifiable"}:
                raise DeliveryError("invalid frozen board record")
            if hashlib.sha256(
                _check_bytes(path, 32 * 1024 * 1024)
            ).hexdigest() != record.get("sha256"):
                raise DeliveryError(
                    f"frozen board integrity: changed bytes: {relative}"
                )
        except (OSError, ValueError, DeliveryError) as exc:
            raise DeliveryError(f"frozen board integrity: {relative}: {exc}") from exc
        records[path] = record["disposition"]
    return records


def require_deliverable_card(card: Path) -> None:
    disposition = checked_frozen_records().get(card.resolve(strict=False))
    if disposition:
        raise DeliveryError(
            f"frozen board record is non-deliverable ({disposition}): {repo_relative(card)}"
        )
    if native.lifecycle_mode(card) != "openspec-v1":
        raise DeliveryError("only openspec-v1 cards are executable")


def resolve_deliverable_card(value: str | Path) -> Path:
    checked_frozen_records()
    card = resolve_card(value)
    require_deliverable_card(card)
    return card


def board_activity() -> dict[str, list[Path]]:
    frozen = checked_frozen_records()
    activity: dict[str, list[Path]] = {
        "active": [],
        "superseded-no-go": [],
        "suspended-not-verifiable": [],
    }
    for path in sorted((BOARD_ROOT / "3.inprogress").glob("*.md")):
        activity[frozen.get(path, "active")].append(path)
    return activity


def board_guard(card_value: str, *, start: bool = False) -> None:
    """Read-only shell adapter; dependency validation remains with the caller."""
    resolve_deliverable_card(card_value)
    if start:
        activity = board_activity()
        if activity["active"]:
            raise DeliveryError(
                "3.inprogress is occupied by another card: "
                + ", ".join((repo_relative(path) for path in activity["active"]))
            )
        print(
            "active lane empty; retained history: "
            + ", ".join(
                (
                    f"{name}={len(paths)}"
                    for name, paths in activity.items()
                    if name != "active"
                )
            )
        )


def section_body(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    marker = f"## {heading}"
    try:
        start = lines.index(marker) + 1
    except ValueError:
        return []
    end = next(
        (index for index in range(start, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    return lines[start:end]


def require_substantive_result_and_log(card: Path) -> None:
    """Reject template Result/Log sections before running the repository floor."""
    text = card.read_text(encoding="utf-8")
    provisional = {
        "",
        "implementation in progress",
        "in progress",
        "pending",
        "placeholder",
        "tbd",
        "todo",
    }
    for heading in ("Result", "Log"):
        content = "\n".join(
            (line.strip() for line in section_body(text, heading))
        ).strip()
        normalized = content.casefold().lstrip("- ").strip()
        if normalized in provisional:
            raise DeliveryError(
                f"preverification requires substantive {heading} content"
            )


def require_delivery_card_structure(card: Path) -> None:
    """Reject missing lifecycle sections before any verification command runs."""
    text = card.read_text(encoding="utf-8")
    required = ("Status", "Acceptance", "Depends On", "Result", "Next", "Log")
    missing = [
        heading for heading in required if f"## {heading}" not in text.splitlines()
    ]
    if missing:
        rendered = ", ".join((f"## {heading}" for heading in missing))
        raise DeliveryError(
            f"preverification requires preserved card sections: {rendered}"
        )


def require_non_future_log_timestamps(
    card: Path, *, now: datetime | None = None
) -> None:
    """Reject card log events that claim to have happened in the future."""
    current = now or datetime.now(timezone.utc)
    log = "\n".join(section_body(card.read_text(encoding="utf-8"), "Log"))
    future = [
        value
        for value in LOG_TIMESTAMP_PATTERN.findall(log)
        if datetime.fromisoformat(value.replace("Z", "+00:00")) > current
    ]
    if future:
        raise DeliveryError(
            "preverification rejects future card Log timestamps: "
            + ", ".join(sorted(set(future)))
        )


def replace_section(text: str, heading: str, replacement: Sequence[str]) -> str:
    lines = text.splitlines()
    marker = f"## {heading}"
    try:
        marker_index = lines.index(marker)
    except ValueError as exc:
        raise DeliveryError(f"card is missing {marker}") from exc
    start = marker_index + 1
    end = next(
        (index for index in range(start, len(lines)) if lines[index].startswith("## ")),
        len(lines),
    )
    updated = [*lines[:start], *replacement, "", *lines[end:]]
    while len(updated) > 1 and (not updated[-1]):
        updated.pop()
    return "\n".join(updated) + "\n"


def acceptance_criteria(card: Path) -> list[str]:
    """Return stable semantic-review units from the card acceptance contract.

    Structured OpenSpec acceptance is reviewed per complete scenario rather
    than per wrapped ``WHEN``/``THEN``/``AND`` Markdown line. Compact cards
    without scenario headings retain their top-level bullet criteria.
    """
    body = section_body(card.read_text(encoding="utf-8"), "Acceptance")
    requirement: str | None = None
    scenarios: list[str] = []
    for line in body:
        if line.startswith("### Requirement:"):
            requirement = line.removeprefix("### Requirement:").strip()
        elif line.startswith("#### Scenario:"):
            scenario = line.removeprefix("#### Scenario:").strip()
            scenarios.append(
                f"Requirement: {requirement} / Scenario: {scenario}"
                if requirement
                else f"Scenario: {scenario}"
            )
    if scenarios:
        return scenarios
    criteria: list[str] = []
    current: list[str] = []
    for line in body:
        if line.startswith("- "):
            if current:
                criteria.append(" ".join(current))
            current = [line[2:].strip()]
        elif current and line.strip() and (not line.startswith("#")):
            current.append(line.strip())
    if current:
        criteria.append(" ".join(current))
    if not criteria:
        raise DeliveryError("card has no observable acceptance criteria")
    return criteria


def admission_acceptance_criteria(card: Path) -> list[str]:
    """Return requirement-level obligations used by right-size admission.

    Semantic review uses complete scenarios, while admission measures their
    stable top-level obligations: structured OpenSpec acceptance uses its
    Requirement headings, while compact cards use their flat bullet list. A
    specs-stage formatting expansion must not make the same behavior appear
    larger merely because one requirement contains several scenarios.
    """
    body = section_body(card.read_text(encoding="utf-8"), "Acceptance")
    requirements = [
        line.removeprefix("### Requirement:").strip()
        for line in body
        if line.startswith("### Requirement:")
    ]
    if requirements:
        return requirements
    return acceptance_criteria(card)


_CONDITION_ID_PATTERN = re.compile("^- \\[(C[1-9][0-9]*)\\] \\S")
_TOP_LEVEL_BULLET_PATTERN = re.compile("^(?:- |\\* |\\+ )")
_SAFE_EVIDENCE_TARGET = re.compile("^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$")
_SAFE_EVIDENCE_SELECTOR = re.compile("^[A-Za-z0-9_.-]+$")
_EVIDENCE_RISK_KINDS = frozenset(
    {
        "input_safety",
        "mutation",
        "restart",
        "concurrency",
        "publication",
        "external_effects",
    }
)
_OBSERVED_PROOF_CONTRACT = "changerail.observed-proof.v1"
_LEGACY_OBSERVED_PROOF_CONTINUATION = "changerail.observed-proof-continuation.v1"
_REVIEW_VERDICT_V2 = "changerail.review-verdict.v2"
_PROOF_STAGES = frozenset({"implementation", "review", "final"})
_PROOF_ROLES = {
    "implementation": frozenset({"implementation"}),
    "review": frozenset({"review"}),
    "final": frozenset({"outer"}),
}
FIXTURE_PROOF_SOURCE_SETS: dict[str, dict[str, Any]] = {}


def _single_section_body(text: str, heading: str) -> list[str]:
    if len(re.findall(f"^## {re.escape(heading)}$", text, flags=re.MULTILINE)) != 1:
        raise DeliveryError(f"evidence plan requires exactly one ## {heading} section")
    return section_body(text, heading)


def acceptance_condition_ids_text(text: str) -> list[str]:
    """Return IDs on every top-level Acceptance bullet from one card read."""
    ids: list[str] = []
    for line in _single_section_body(text, "Acceptance"):
        if not _TOP_LEVEL_BULLET_PATTERN.match(line):
            continue
        match = _CONDITION_ID_PATTERN.match(line)
        if match is None:
            raise DeliveryError(
                "every top-level Acceptance bullet requires a [C<number>] condition ID"
            )
        ids.append(match.group(1))
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        raise DeliveryError(
            "duplicate Acceptance condition IDs: " + ", ".join(duplicates)
        )
    if not ids:
        raise DeliveryError(
            "fresh admission requires [C<number>] IDs on top-level Acceptance bullets"
        )
    return ids


def acceptance_condition_ids(card: Path) -> list[str]:
    """Path wrapper for specs-stage validation."""
    return acceptance_condition_ids_text(card.read_text(encoding="utf-8"))


def _evidence_plan_json(text: str) -> dict[str, Any]:
    """Extract one JSON contract from Verify without touching its locators."""
    body = section_body(text, "Verify")
    rendered = "\n".join(body)
    starts = list(re.finditer("^```json[ \\t]*$", rendered, flags=re.MULTILINE))
    if len(starts) != 1:
        raise DeliveryError(
            "evidence plan requires exactly one fenced json block in ## Verify"
        )
    start = starts[0].end()
    close = re.search("^```[ \\t]*$", rendered[start:], flags=re.MULTILINE)
    if close is None:
        raise DeliveryError("evidence plan JSON block is unclosed")
    blocks = [rendered[start : start + close.start()].strip()]

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise DeliveryError(f"evidence plan has duplicate JSON key: {key}")
            result[key] = value
        return result

    try:
        payload = json.loads(blocks[0], object_pairs_hook=reject_duplicate_keys)
    except (json.JSONDecodeError, DeliveryError) as exc:
        if isinstance(exc, DeliveryError):
            raise
        raise DeliveryError(f"evidence plan JSON is malformed: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise DeliveryError("evidence plan JSON must be an object")
    return payload


def validate_evidence_plan_text(
    text: str, schema: Mapping[str, Any], *, phase: str = "admission"
) -> dict[str, Any]:
    """Pure structural validation of a once-read card and loaded schema."""
    if phase not in {"specs", "design", "tasks", "admission"}:
        raise DeliveryError(f"unknown evidence-plan phase: {phase}")
    expected = acceptance_condition_ids_text(text)
    if phase == "specs":
        return {"conditions": expected}
    design = _single_section_body(text, "Design")
    if not any((line.strip() for line in design)):
        raise DeliveryError("evidence plan requires a nonempty ## Design section")
    _single_section_body(text, "Verify")
    try:
        import jsonschema
    except ImportError as exc:
        raise DeliveryError(
            "jsonschema is required to validate evidence plans"
        ) from exc
    payload = _evidence_plan_json(text)
    try:
        jsonschema.validate(payload, schema)
    except jsonschema.ValidationError as exc:
        location = ".".join((str(part) for part in exc.absolute_path))
        raise DeliveryError(
            f"evidence plan schema validation failed{(f' at {location}' if location else '')}: {exc.message}"
        ) from exc
    condition_ids = [entry["condition"] for entry in payload["conditions"]]
    duplicates = sorted(
        {value for value in condition_ids if condition_ids.count(value) > 1}
    )
    if duplicates:
        raise DeliveryError(
            "duplicate evidence-plan condition rows: " + ", ".join(duplicates)
        )
    foreign_rows = sorted(set(condition_ids) - set(expected))
    if foreign_rows:
        raise DeliveryError(
            "evidence-plan condition rows reference foreign Acceptance IDs: "
            + ", ".join(foreign_rows)
        )
    if phase != "design" and (
        set(condition_ids) != set(expected) or len(condition_ids) != len(expected)
    ):
        raise DeliveryError(
            f"evidence-plan condition rows must exactly match Acceptance IDs; expected={expected}, observed={condition_ids}"
        )
    risk_kinds: list[str] = []
    for risk in payload["risks"]:
        risk_kinds.extend(risk["kinds"])
        references = risk["conditions"]
        foreign = sorted(set(references) - set(expected))
        if foreign:
            raise DeliveryError(
                "evidence-plan risk references foreign conditions: "
                + ", ".join(foreign)
            )
        if risk["applies"] and (not references):
            raise DeliveryError(
                "applicable evidence-plan risk requires condition references"
            )
        if not risk["applies"] and references:
            raise DeliveryError(
                "non-applicable evidence-plan risk must use conditions: []"
            )
    duplicated_risks = sorted(
        {value for value in risk_kinds if risk_kinds.count(value) > 1}
    )
    if duplicated_risks:
        raise DeliveryError(
            "duplicate evidence-plan risk kinds: " + ", ".join(duplicated_risks)
        )
    if set(risk_kinds) != _EVIDENCE_RISK_KINDS:
        raise DeliveryError(
            "evidence-plan risks must cover exactly: "
            + ", ".join(sorted(_EVIDENCE_RISK_KINDS))
        )
    for entry in payload["conditions"]:
        target = entry["method"]["target"]
        path, separator, selector = target.partition("::")
        if (
            target.count("::") > 1
            or not _SAFE_EVIDENCE_TARGET.fullmatch(path)
            or any((part in {".", ".."} for part in path.split("/")))
            or (separator and (not _SAFE_EVIDENCE_SELECTOR.fullmatch(selector)))
        ):
            raise DeliveryError(
                f"evidence-plan method target is not an inert relative locator: {target}"
            )
    return payload


def validate_evidence_plan(card: Path, *, phase: str = "admission") -> dict[str, Any]:
    """Read a candidate and schema once, then run the pure declaration core."""
    return validate_evidence_plan_text(
        card.read_text(encoding="utf-8"),
        load_json(CARD_EVIDENCE_SCHEMA_PATH),
        phase=phase,
    )


def _acceptance_scenarios_text(text: str) -> dict[str, str]:
    """Bind every condition to one complete scenario from the same card bytes."""
    scenario: str | None = None
    requirement: str | None = None
    result: dict[str, str] = {}
    requirements: set[str] = set()
    scenarios: set[tuple[str, str]] = set()
    form: str | None = None
    for line in _single_section_body(text, "Acceptance"):
        if line.startswith("### Requirement:"):
            requirement = line.removeprefix("### Requirement:").strip()
            if not requirement or requirement in requirements:
                raise DeliveryError(
                    "Acceptance Requirement heading is empty or duplicate"
                )
            requirements.add(requirement)
            scenario = None
        elif line.startswith("#### Scenario:"):
            name = line.removeprefix("#### Scenario:").strip()
            if form == "flat" or requirement is None or (not name):
                raise DeliveryError("Acceptance Scenario heading is orphaned or mixed")
            identity = (requirement, name)
            if identity in scenarios:
                raise DeliveryError("Acceptance Scenario heading is duplicate")
            scenarios.add(identity)
            form = "structured"
            scenario = f"Requirement: {requirement} / Scenario: {name}"
        elif (match := _CONDITION_ID_PATTERN.match(line)) is not None:
            condition = match.group(1)
            if condition in result:
                raise DeliveryError(f"duplicate Acceptance condition ID: {condition}")
            if requirement is not None or scenario is not None:
                if form == "flat" or scenario is None:
                    raise DeliveryError(
                        "Acceptance condition has no unambiguous Scenario owner"
                    )
                form = "structured"
                result[condition] = scenario
            else:
                if form == "structured":
                    raise DeliveryError(
                        "Acceptance flat condition is mixed with structured scenarios"
                    )
                form = "flat"
                result[condition] = f"Condition: {condition}"
    if form == "structured" and any(
        (
            requirement not in {item[0] for item in scenarios}
            for requirement in requirements
        )
    ):
        raise DeliveryError("Acceptance Requirement has no Scenario owner")
    return result


def _derive_proof_inventory_from_checked_sources(
    sources: Sequence[tuple[Path, bytes]],
) -> dict[str, Any]:
    """Derive one inventory from source bytes already admitted by this decision.

    This is deliberately private: its callers have used the component-wise
    no-follow reader and retain the bytes that established each source hash.
    Keeping parsing here avoids a capability admission validating one version of
    an extra source and the inventory reopening a different version.
    """
    if len({repo_relative(source) for source, _ in sources}) != len(sources):
        raise DeliveryError("duplicate proof inventory source")
    rows: list[dict[str, Any]] = []
    for source, data in sources:
        relative = repo_relative(source)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise DeliveryError("proof inventory source is not UTF-8") from exc
        plan = validate_evidence_plan_text(
            text, load_json(CARD_EVIDENCE_SCHEMA_PATH), phase="admission"
        )
        scenarios = _acceptance_scenarios_text(text)
        source_hash = hashlib.sha256(data).hexdigest()
        for condition in plan["conditions"]:
            condition_id = condition["condition"]
            if condition_id not in scenarios:
                raise DeliveryError(
                    f"proof inventory has orphan condition: {condition_id}"
                )
            rows.append(
                {
                    "identity": f"{relative}@sha256:{source_hash}:{condition_id}",
                    "source": {"path": relative, "sha256": source_hash},
                    "condition": condition_id,
                    "scenario": f"{relative}@sha256:{source_hash} / {scenarios[condition_id]}",
                    "method": condition["method"],
                    "stage": condition["stage"],
                }
            )
        unplanned = sorted(
            set(scenarios) - {item["condition"] for item in plan["conditions"]}
        )
        if unplanned:
            raise DeliveryError(
                "proof inventory has Acceptance conditions absent from the evidence plan: "
                + ", ".join(unplanned)
            )
    identities = [row["identity"] for row in rows]
    if len(identities) != len(set(identities)):
        raise DeliveryError("duplicate proof inventory identity")
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema": "changerail.proof-inventory.v1",
        "conditions": rows,
        "digest": "sha256:" + hashlib.sha256(canonical).hexdigest(),
    }


def derive_proof_inventory(
    card: Path, *, additional_sources: Sequence[Path] = ()
) -> dict[str, Any]:
    """Derive one namespaced, hash-bound condition inventory from checked bytes.

    ``additional_sources`` is deliberately an internal checked interface: no run
    metadata or request flag is consulted.  Production callers pass nothing;
    isolated fixtures may exercise composition without gaining adoption authority.
    """
    sources = (card, *additional_sources)
    if len({repo_relative(source) for source in sources}) != len(sources):
        raise DeliveryError("duplicate proof inventory source")
    checked: list[tuple[Path, bytes]] = []
    for source in sources:
        relative = repo_relative(source)
        data = _check_bytes(REPO_ROOT / relative, 2 * 1024 * 1024)
        checked.append((REPO_ROOT / relative, data))
    return _derive_proof_inventory_from_checked_sources(checked)


def _run_observed_contract(run_dir: Path) -> dict[str, Any] | None:
    """Load only an independently retained v2 selection or an explicit v1 anchor.

    Version absence is deliberately not a legacy selector: a damaged new run may
    not become weaker merely by deleting one field.
    """
    require_current_execution(run_dir)
    try:
        run_bytes = _check_bytes(run_dir / "run.json")
        run = _check_json_bytes(run_bytes)
    except (OSError, ValueError) as exc:
        raise DeliveryError("observed proof run metadata is missing or unsafe") from exc
    selected = run.get("observed_proof_contract")
    if run.get("schema") != "changerail.delivery-run.v2":
        raise DeliveryError("observed proof run metadata cannot be downgraded")
    if not isinstance(selected, dict) or set(selected) != {
        "schema",
        "required_stages",
        "selection",
    }:
        raise DeliveryError("observed proof contract selection is malformed")
    if selected["schema"] != _OBSERVED_PROOF_CONTRACT or selected[
        "required_stages"
    ] != ["implementation", "review", "final"]:
        raise DeliveryError("observed proof contract selection cannot be downgraded")
    reference = selected["selection"]
    if not isinstance(reference, dict) or set(reference) != {"path", "sha256"}:
        raise DeliveryError("observed proof creation selection is malformed")
    path = reference["path"]
    if (
        not isinstance(path, str)
        or Path(path).is_absolute()
        or ".." in Path(path).parts
    ):
        raise DeliveryError("observed proof creation selection is unsafe")
    expected_path = repo_relative(run_dir / "observed-proof-selection.json")
    if path != expected_path:
        raise DeliveryError("observed proof creation selection is foreign")
    data = _check_bytes(REPO_ROOT / path)
    if (
        not isinstance(reference["sha256"], str)
        or not re.fullmatch("[0-9a-f]{64}", reference["sha256"])
        or (not data)
        or (hashlib.sha256(data).hexdigest() != reference["sha256"])
    ):
        raise DeliveryError("observed proof creation selection is stale")
    try:
        creation = _check_json_bytes(data)
    except ValueError as exc:
        raise DeliveryError("observed proof creation selection is malformed") from exc
    if set(creation) != {"schema", "root", "owner", "required_stages"}:
        raise DeliveryError("observed proof creation selection is malformed")
    root = creation["root"]
    owner = creation["owner"]
    if (
        creation["schema"] != "changerail.observed-proof-selection.v1"
        or root != repo_relative(run_dir)
        or (not isinstance(owner, dict))
        or (set(owner) != {"run_id", "card"})
        or (owner.get("run_id") != run_dir.name)
        or (not isinstance(owner.get("card"), str))
        or Path(owner["card"]).is_absolute()
        or (".." in Path(owner["card"]).parts)
        or (owner["card"] != Path(owner["card"]).as_posix())
    ):
        raise DeliveryError("observed proof creation selection does not bind this run")
    original = owner["card"]
    current = run.get("card")
    if (
        run.get("run_id") != run_dir.name
        or not isinstance(current, str)
        or Path(current).is_absolute()
        or (".." in Path(current).parts)
        or (current != Path(current).as_posix())
        or (Path(original).name != Path(current).name)
    ):
        raise DeliveryError("observed proof creation selection does not bind this run")
    legal_move = (
        isinstance(original, str)
        and isinstance(current, str)
        and (Path(original).name == Path(current).name)
        and original.startswith("openspec/board/2.todo/")
        and current.startswith("openspec/board/3.inprogress/")
    )
    if creation["required_stages"] != ["implementation", "review", "final"] or (
        current != original and (not legal_move)
    ):
        raise DeliveryError("observed proof creation selection does not bind this run")
    return selected


def _current_proof_inventory(card: Path, run_dir: Path) -> dict[str, Any] | None:
    contract = _run_observed_contract(run_dir)
    if contract is None or contract["schema"] != _OBSERVED_PROOF_CONTRACT:
        return None
    try:
        _check_json(run_dir / "run.json")
    except (OSError, ValueError) as exc:
        raise DeliveryError("proof inventory owning run is unsafe") from exc
    capability = FIXTURE_PROOF_SOURCE_SETS.get(run_dir.name)
    if capability is None:
        return derive_proof_inventory(card)
    owner = _check_owner(run_dir)
    if set(capability) != {"run", "payload", "caller", "sources"}:
        raise DeliveryError("proof source-set capability is malformed")
    if capability["run"] != owner or capability["payload"] != payload_fingerprint():
        raise DeliveryError("proof source-set capability is stale or foreign")
    if not isinstance(capability["caller"], str) or not capability["caller"]:
        raise DeliveryError("proof source-set capability caller is missing")
    sources = capability["sources"]
    if not isinstance(sources, list) or not sources:
        raise DeliveryError("proof source-set capability sources are malformed")
    checked_sources: list[tuple[Path, bytes]] = []
    for source in sources:
        if not isinstance(source, dict) or set(source) != {"path", "sha256"}:
            raise DeliveryError("proof source-set capability source is malformed")
        path = _safe_reference_path(
            source["path"], root=REPO_ROOT, label="proof source-set"
        )
        try:
            data = _check_bytes(path, 2 * 1024 * 1024)
        except (OSError, ValueError) as exc:
            raise DeliveryError("proof source-set capability source is unsafe") from exc
        if hashlib.sha256(data).hexdigest() != source["sha256"]:
            raise DeliveryError("proof source-set capability source is stale")
        checked_sources.append((path, data))
    card_relative = repo_relative(card)
    card_bytes = _check_bytes(REPO_ROOT / card_relative, 2 * 1024 * 1024)
    return _derive_proof_inventory_from_checked_sources(
        [(REPO_ROOT / card_relative, card_bytes), *checked_sources]
    )


_PROOF_INDEX_SCHEMA = "changerail.proof-index.v2"
_PROOF_RECORD_POST_RETENTION_HOOK: Any | None = None


def _proof_index_path(run_dir: Path) -> Path:
    return run_dir / "proof-index.json"


def _open_safe_directory(path: Path) -> int:
    """Open a repository directory component-by-component without following it."""
    relative = path.relative_to(REPO_ROOT)
    if not relative.parts or any((part in ("", ".", "..") for part in relative.parts)):
        raise ValueError("unsafe proof directory")
    directory = os.open(REPO_ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in relative.parts:
            child = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
            )
            os.close(directory)
            directory = child
        return directory
    except BaseException:
        os.close(directory)
        raise


def _safe_proof_directory(run_dir: Path, name: str, *, create: bool) -> int:
    """Return a no-follow descriptor for one owned proof subdirectory."""
    run_fd = _open_safe_directory(run_dir)
    try:
        if create:
            try:
                os.mkdir(name, 448, dir_fd=run_fd)
            except FileExistsError:
                pass
        child = os.open(
            name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=run_fd
        )
        return child
    finally:
        os.close(run_fd)


def _write_json_at(
    directory_fd: int, name: str, payload: Mapping[str, Any], *, replace: bool
) -> None:
    """Durably create or atomically replace a closed run-local JSON leaf."""
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    temporary = f".{name}.{uuid.uuid4().hex}.tmp"
    fd = os.open(
        temporary,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        384,
        dir_fd=directory_fd,
    )
    try:
        with os.fdopen(fd, "wb", closefd=True) as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        if replace:
            os.rename(temporary, name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        else:
            os.link(
                temporary,
                name,
                src_dir_fd=directory_fd,
                dst_dir_fd=directory_fd,
                follow_symlinks=False,
            )
            os.unlink(temporary, dir_fd=directory_fd)
        os.fsync(directory_fd)
    except BaseException:
        try:
            os.unlink(temporary, dir_fd=directory_fd)
        except FileNotFoundError:
            pass
        raise


def _caller_proof_role(*, outer: bool = False) -> str:
    """Use the actual session role; proof data and API parameters cannot grant it."""
    role = os.environ.get("CHRL_SESSION_ROLE")
    allowed = {"implementation", "review"}
    if outer:
        allowed = {"outer"}
    if role not in allowed:
        expected = "outer" if outer else "implementation or review"
        raise DeliveryError(f"proof recording requires actual {expected} session role")
    return role


def _decode_closed_json(data: bytes, *, label: str) -> dict[str, Any]:
    """Decode one retained JSON object, refusing duplicate keys and non-finite values."""

    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value = dict(pairs)
        if len(value) != len(pairs):
            raise ValueError("duplicate key")
        return value

    def finite(raw: str) -> float:
        value = float(raw)
        if not math.isfinite(value):
            raise ValueError("nonfinite number")
        return value

    try:
        value = json.loads(
            data, object_pairs_hook=unique, parse_float=finite, parse_constant=finite
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        RecursionError,
        ValueError,
    ) as exc:
        raise DeliveryError(f"{label} is not closed JSON") from exc
    if not isinstance(value, dict):
        raise DeliveryError(f"{label} must be a JSON object")
    return value


def _is_utc_observed_at(value: object) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        return (
            datetime.fromisoformat(value.removesuffix("Z") + "+00:00").tzinfo
            is not None
        )
    except ValueError:
        return False


def _safe_reference_path(value: object, *, root: Path, label: str) -> Path:
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or ("\x00" in value)
        or Path(value).is_absolute()
        or any((part in ("", ".", "..") for part in Path(value).parts))
    ):
        raise DeliveryError(f"{label} path is unsafe")
    path = REPO_ROOT / value
    try:
        if not path.is_relative_to(root):
            raise DeliveryError(f"{label} is outside its owning root")
    except ValueError as exc:
        raise DeliveryError(f"{label} path is unsafe") from exc
    return path


def _validate_reference_shape(reference: Any, *, label: str) -> Mapping[str, Any]:
    """Reject an untyped reference before resolving or reading its locator."""
    if (
        not isinstance(reference, Mapping)
        or set(reference) != {"path", "size", "sha256"}
        or (not isinstance(reference.get("path"), str))
        or (not isinstance(reference.get("size"), int))
        or isinstance(reference.get("size"), bool)
        or (reference["size"] < 0)
        or (not isinstance(reference.get("sha256"), str))
        or (not re.fullmatch("[0-9a-f]{64}", reference["sha256"]))
    ):
        raise DeliveryError(f"{label} reference is not closed")
    return reference


def _reference_bytes(
    reference: Mapping[str, Any],
    *,
    root: Path,
    label: str,
    limit: int = 32 * 1024 * 1024,
) -> tuple[Path, bytes]:
    """Read one typed reference exactly once through the no-follow reader."""
    reference = _validate_reference_shape(reference, label=label)
    path = _safe_reference_path(reference["path"], root=root, label=label)
    try:
        data = _check_bytes(path, limit)
    except (OSError, ValueError) as exc:
        raise DeliveryError(f"{label} cannot be safely read") from exc
    if (
        reference["size"] != len(data)
        or reference["sha256"] != hashlib.sha256(data).hexdigest()
    ):
        raise DeliveryError(f"{label} integrity failed")
    return (path, data)


def _proof_artifact(path: Path, run_dir: Path, reference: Mapping[str, Any]) -> bytes:
    artifact, data = _reference_bytes(reference, root=run_dir, label="proof artifact")
    if artifact != path:
        raise DeliveryError("proof artifact path does not match its reference")
    return data


def _fragment_bytes(
    reference: Mapping[str, Any], *, run_dir: Path, label: str
) -> bytes:
    expected = {"path", "size", "sha256", "start", "end", "fragment_sha256"}
    if set(reference) != expected:
        raise DeliveryError(f"{label} fragment reference is not closed")
    _, data = _reference_bytes(
        {key: reference[key] for key in ("path", "size", "sha256")},
        root=run_dir,
        label=label,
    )
    start, end = (reference["start"], reference["end"])
    if (
        not isinstance(start, int)
        or isinstance(start, bool)
        or (not isinstance(end, int))
        or isinstance(end, bool)
        or (start < 0)
        or (end <= start)
        or (end > len(data))
    ):
        raise DeliveryError(f"{label} fragment offsets are invalid")
    fragment = data[start:end]
    if hashlib.sha256(fragment).hexdigest() != reference["fragment_sha256"]:
        raise DeliveryError(f"{label} fragment identity failed")
    return fragment


def _validate_fragments(fragments: Mapping[str, Any], *, run_dir: Path) -> None:
    if set(fragments) != {"before", "action", "after"}:
        raise DeliveryError("observed fragments are not closed")
    for name in ("before", "action", "after"):
        _fragment_bytes(fragments[name], run_dir=run_dir, label=f"{name} observation")


def _validate_source_reference(
    reference: Mapping[str, Any], *, validated: tuple[Path, bytes] | None = None
) -> None:
    """Validate an inspectable repository reference without reopening supplied bytes."""
    if validated is None:
        path, data = _reference_bytes(
            reference, root=REPO_ROOT, label="inspected source", limit=2 * 1024 * 1024
        )
    else:
        path, data = validated
        reference = _validate_reference_shape(reference, label="inspected source")
        if path != _safe_reference_path(
            reference.get("path"), root=REPO_ROOT, label="inspected source"
        ):
            raise DeliveryError(
                "inspected source locator does not match its validated bytes"
            )
    if path.is_relative_to(RUNTIME_ROOT) or not data:
        raise DeliveryError("inspected source locator is not a repository source")


def _validate_test_assertion_support(support: Mapping[str, Any], target: str) -> None:
    """Require state assertions from the declared test source, never its log."""
    if set(support) != {"source", "fragments"}:
        raise DeliveryError("test assertion support is not closed")
    source, source_bytes = _reference_bytes(
        support["source"],
        root=REPO_ROOT,
        label="test assertion source",
        limit=2 * 1024 * 1024,
    )
    _validate_source_reference(support["source"], validated=(source, source_bytes))
    declared_file = target.partition("::")[0]
    if repo_relative(source) != declared_file:
        raise DeliveryError("test assertion support does not bind its declared source")
    fragments = support["fragments"]
    if set(fragments) != {"before", "action", "after"}:
        raise DeliveryError("test assertion support fragments are not closed")
    reference = support["source"]
    for name in ("before", "action", "after"):
        fragment = fragments[name]
        expected = {"path", "size", "sha256", "start", "end", "fragment_sha256"}
        if (
            not isinstance(fragment, Mapping)
            or set(fragment) != expected
            or {key: fragment[key] for key in ("path", "size", "sha256")} != reference
        ):
            raise DeliveryError(
                "test assertion fragment is not from its declared source"
            )
        start, end = (fragment["start"], fragment["end"])
        if (
            type(start) is not int
            or type(end) is not int
            or start < 0
            or (end <= start)
            or (end > len(source_bytes))
        ):
            raise DeliveryError("test assertion fragment offsets are invalid")
        if (
            hashlib.sha256(source_bytes[start:end]).hexdigest()
            != fragment["fragment_sha256"]
        ):
            raise DeliveryError("test assertion fragment identity failed")


def _validate_runtime_reference(
    reference: Mapping[str, Any],
    *,
    run_dir: Path,
    owner: Mapping[str, str],
    expected_kind: str,
    target: Mapping[str, Any],
    session: Mapping[str, Any],
    fixture_only: bool,
) -> None:
    """Validate one exact runtime provenance record against the observed scope.

    These records deliberately attest only retained fixture inputs.  They do
    not launch or authorize a native runtime; a fixture target must say so in
    both its observation and each referenced provenance record.
    """
    _, data = _reference_bytes(
        reference, root=run_dir, label=f"runtime {expected_kind}"
    )
    record = _decode_closed_json(data, label=f"runtime {expected_kind} reference")
    expected_outcomes = {
        "authorization": {"authorized"},
        "preflight": {"passed"},
        "recovery": {"recovered", "rerun_passed"},
        "not_applicable": {"not_applicable"},
    }
    expected = {
        "schema",
        "run",
        "kind",
        "outcome",
        "scope",
        "fixture_only",
        "observed_at",
    }
    if expected_kind in {"recovery", "not_applicable"}:
        expected.add("resolution")
    if (
        set(record) != expected
        or record.get("schema") != "changerail.runtime-reference.v1"
        or record.get("run") != dict(owner)
        or (record.get("kind") != expected_kind)
        or (record.get("outcome") not in expected_outcomes.get(expected_kind, set()))
        or (not isinstance(record.get("scope"), dict))
        or (set(record["scope"]) != {"target", "session"})
        or (record["scope"]["target"] != dict(target))
        or (record["scope"]["session"] != dict(session))
        or (type(record.get("fixture_only")) is not bool)
        or (record["fixture_only"] != fixture_only)
        or (target.get("kind") == "fixture" and (not record["fixture_only"]))
        or (not _is_utc_observed_at(record.get("observed_at")))
    ):
        raise DeliveryError(f"runtime {expected_kind} reference identity is foreign")
    if expected_kind == "not_applicable":
        resolution = record["resolution"]
        if (
            not isinstance(resolution, dict)
            or set(resolution) != {"kind", "reason"}
            or resolution.get("kind") != "not_applicable"
            or (not isinstance(resolution.get("reason"), str))
            or (not resolution["reason"].strip())
        ):
            raise DeliveryError("runtime not_applicable reference is not concrete")
    elif expected_kind == "recovery":
        resolution = record["resolution"]
        if (
            not isinstance(resolution, dict)
            or set(resolution) != {"kind", "reference"}
            or resolution.get("kind") not in {"recovery", "rerun"}
            or (not isinstance(resolution.get("reference"), str))
            or (not resolution["reference"].strip())
        ):
            raise DeliveryError("runtime recovery reference is not concrete")


def _validate_observed_proof(
    proof: Mapping[str, Any],
    *,
    card: Path,
    run_dir: Path,
    inventory: Mapping[str, Any],
    role: str | None = None,
) -> dict[str, Any]:
    """Validate a closed observation against current inventory and retained bytes."""
    from jsonschema import Draft202012Validator, FormatChecker

    try:
        Draft202012Validator(
            load_json(CARD_PROOF_SCHEMA_PATH), format_checker=FormatChecker()
        ).validate(proof)
    except Exception as exc:
        raise DeliveryError(f"observed proof schema validation failed: {exc}") from exc
    owner = _check_owner(run_dir)
    if proof["run"] != owner or proof["inventory_digest"] != inventory["digest"]:
        raise DeliveryError("observed proof ownership or inventory is foreign")
    expected_payload = payload_fingerprint()
    if proof["payload"] != expected_payload:
        raise DeliveryError("observed proof payload is stale")
    rows = {row["identity"]: row for row in inventory["conditions"]}
    row = rows.get(proof["condition"])
    if (
        row is None
        or proof["method"] != row["method"]
        or proof["stage"] != row["stage"]
    ):
        raise DeliveryError("observed proof condition, method, or stage is foreign")
    if proof["kind"] != row["method"]["kind"]:
        raise DeliveryError("observed proof kind does not match the declared method")
    if role is not None and proof["recorder_role"] != role:
        raise DeliveryError("observed proof recorder role is forged")
    if proof["recorder_role"] not in _PROOF_ROLES[proof["stage"]]:
        raise DeliveryError("observed proof role cannot record this stage")
    if proof["outcome"] != "pass":
        raise DeliveryError("observed proof outcome is not terminal pass")
    artifact = proof["artifact"]
    artifact_path = _safe_reference_path(
        artifact["path"], root=run_dir, label="proof artifact"
    )
    data = _proof_artifact(artifact_path, run_dir, artifact)
    if proof["kind"] == "test":
        item, log, current = read_check_result(
            artifact_path,
            run_dir,
            proof["lane"],
            proof["command_identity"],
            record_data=data,
            expected_record=artifact,
        )
        if (
            not current
            or not log
            or (not proof["selected_nodes"])
            or (item["attempt_id"] != proof["attempt_id"])
        ):
            raise DeliveryError("test proof has no current selected-node receipt")
        target = str(row["method"]["target"])
        identity = item["command_identity"]
        if item["command_identity"] != proof["command_identity"]:
            raise DeliveryError("test proof has no declared pytest selector")
        _validate_test_assertion_support(proof["assertion_support"], target)
        if proof["fragments"] != proof["assertion_support"]["fragments"]:
            raise DeliveryError(
                "test proof fragments do not retain its assertion support"
            )
        passed = validate_selected_nodes(
            REPO_ROOT,
            profile(),
            log,
            identity,
            target,
            proof["selected_nodes"],
            label="test proof",
        )
        if item["lane"] != proof["lane"] or len(passed) == 0:
            raise DeliveryError("test proof receipt lane is foreign")
    else:
        _validate_fragments(proof["fragments"], run_dir=run_dir)
        observed = _decode_closed_json(data, label="typed proof artifact")
        expected = {
            "schema",
            "observer",
            "role",
            "observed_at",
            "condition",
            "inspected_sources",
            "fragments",
            "conclusion",
            "mocked_seams",
            "residual_risks",
        }
        if proof["kind"] == "runtime":
            expected.add("runtime")
        if (
            set(observed) != expected
            or observed.get("schema") != f"changerail.{proof['kind']}-observation.v1"
        ):
            raise DeliveryError(
                "typed proof artifact has an unresolved observation shape"
            )
        if (
            not all(
                (
                    isinstance(observed.get(key), str) and observed[key]
                    for key in ("observer", "role", "condition", "conclusion")
                )
            )
            or not _is_utc_observed_at(observed.get("observed_at"))
            or observed["role"] != proof["recorder_role"]
            or (observed["condition"] != proof["condition"])
            or (observed["fragments"] != proof["fragments"])
            or any(
                (
                    not isinstance(observed.get(key), list)
                    for key in ("inspected_sources", "mocked_seams", "residual_risks")
                )
            )
            or any(
                (
                    not isinstance(item, str) or not item.strip()
                    for key in ("mocked_seams", "residual_risks")
                    for item in observed[key]
                )
            )
        ):
            raise DeliveryError("typed proof artifact has invalid observation fields")
        _validate_fragments(observed["fragments"], run_dir=run_dir)
        if proof["kind"] == "inspection":
            if not observed["inspected_sources"]:
                raise DeliveryError("inspection proof has no inspected sources")
            for source in observed["inspected_sources"]:
                _validate_source_reference(source)
            if str(row["method"]["target"]) not in {
                source["path"] for source in observed["inspected_sources"]
            }:
                raise DeliveryError(
                    "inspection proof does not bind its declared source"
                )
        else:
            if observed["inspected_sources"]:
                raise DeliveryError("runtime proof does not support inspected sources")
            runtime = observed.get("runtime")
            if runtime != proof["runtime"]:
                raise DeliveryError("runtime proof does not bind its observation")
            if runtime["target"]["identity"] != row["method"]["target"]:
                raise DeliveryError("runtime proof does not bind its declared target")
            if type(runtime.get("fixture_only")) is not bool or (
                runtime["target"].get("kind") == "fixture"
                and (not runtime["fixture_only"])
            ):
                raise DeliveryError("runtime fixture provenance is not explicit")
            for key in ("authorization", "preflight"):
                _validate_runtime_reference(
                    runtime[key],
                    run_dir=run_dir,
                    owner=owner,
                    expected_kind=key,
                    target=runtime["target"],
                    session=runtime["session"],
                    fixture_only=runtime["fixture_only"],
                )
            recovery = runtime["recovery"]
            _validate_runtime_reference(
                recovery["reference"],
                run_dir=run_dir,
                owner=owner,
                expected_kind=recovery["kind"],
                target=runtime["target"],
                session=runtime["session"],
                fixture_only=runtime["fixture_only"],
            )
    return dict(proof)


def _validated_index_records(
    index: Mapping[str, Any], *, card: Path, run_dir: Path, inventory: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """Read every current index reference and its exact immutable record bytes."""
    owner = _check_owner(run_dir)
    expected = {"schema", "run", "inventory_digest", "payload", "generation", "records"}
    if set(index) != expected or index.get("schema") != _PROOF_INDEX_SCHEMA:
        raise DeliveryError("observed proof index is stale or malformed")
    if (
        index.get("run") != owner
        or index.get("inventory_digest") != inventory["digest"]
        or index.get("payload") != payload_fingerprint()
        or (not isinstance(index.get("generation"), str))
        or (not index["generation"])
    ):
        raise DeliveryError("observed proof index is stale or foreign")
    rows = index.get("records")
    if not isinstance(rows, list):
        raise DeliveryError("observed proof index records are malformed")
    seen_refs: set[str] = set()
    seen_observations: set[str] = set()
    records: list[dict[str, Any]] = []
    root = run_dir / "proof-records"
    for reference in rows:
        path, data = _reference_bytes(reference, root=run_dir, label="proof record")
        if path.parent != root or path.name.startswith("."):
            raise DeliveryError("observed proof record is foreign")
        relative = reference["path"]
        if relative in seen_refs:
            raise DeliveryError("observed proof index has duplicate references")
        seen_refs.add(relative)
        record = _decode_closed_json(data, label="proof record")
        checked = _validate_observed_proof(
            record, card=card, run_dir=run_dir, inventory=inventory
        )
        if checked["observation_id"] in seen_observations:
            raise DeliveryError(
                "observed proof index has duplicate observation identities"
            )
        seen_observations.add(checked["observation_id"])
        records.append(checked)
    return records


def _record_index_reference(path: Path) -> dict[str, Any]:
    data = _check_bytes(path, 2 * 1024 * 1024)
    return {
        "path": repo_relative(path),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _record_observed_proof_with_ownership(
    run_dir: Path,
    proof: Mapping[str, Any],
    *,
    actual_role: str,
    ownership: _VerificationLockOwnership,
) -> Path:
    """Record one proof while the caller's existing 03C lock is still held."""
    owner = _check_owner(run_dir)
    card = REPO_ROOT / owner["card"]
    _require_verification_attempt_ownership(ownership, run_dir, card)
    inventory = _current_proof_inventory(card, run_dir)
    if inventory is None:
        raise DeliveryError("legacy run has no observed-proof recording authority")
    checked = _validate_observed_proof(
        proof, card=card, run_dir=run_dir, inventory=inventory, role=actual_role
    )
    index_path = _proof_index_path(run_dir)
    prior: list[dict[str, Any]] = []
    prior_refs: list[dict[str, Any]] = []
    try:
        index_stat = os.lstat(index_path)
    except FileNotFoundError:
        index_stat = None
    if index_stat is not None and (not stat.S_ISREG(index_stat.st_mode)):
        raise DeliveryError("observed proof index leaf is unsafe")
    if index_stat is not None:
        try:
            raw_index = _check_json(index_path)
            expected_index = {
                "schema",
                "run",
                "inventory_digest",
                "payload",
                "generation",
                "records",
            }
            if (
                set(raw_index) != expected_index
                or raw_index.get("schema") != _PROOF_INDEX_SCHEMA
                or raw_index.get("run") != owner
                or (not isinstance(raw_index.get("records"), list))
            ):
                raise DeliveryError("observed proof index is stale or malformed")
            for reference in raw_index["records"]:
                path, _ = _reference_bytes(
                    reference, root=run_dir, label="proof record"
                )
                if path.parent != run_dir / "proof-records":
                    raise DeliveryError("observed proof record is foreign")
            if (
                raw_index.get("inventory_digest") == inventory["digest"]
                and raw_index.get("payload") == payload_fingerprint()
            ):
                prior = _validated_index_records(
                    raw_index, card=card, run_dir=run_dir, inventory=inventory
                )
                prior_refs = list(raw_index["records"])
        except (OSError, ValueError) as exc:
            raise DeliveryError("observed proof index cannot be safely read") from exc
    if any((item["observation_id"] == checked["observation_id"] for item in prior)):
        raise DeliveryError("observed proof duplicate observation identity")
    run_fd = _open_safe_directory(run_dir)
    records_fd = -1
    try:
        try:
            existing_index = os.stat(
                "proof-index.json", dir_fd=run_fd, follow_symlinks=False
            )
        except FileNotFoundError:
            existing_index = None
        if existing_index is not None and (not stat.S_ISREG(existing_index.st_mode)):
            raise DeliveryError("observed proof index leaf is unsafe")
        try:
            os.mkdir("proof-records", 448, dir_fd=run_fd)
        except FileExistsError:
            pass
        records_fd = os.open(
            "proof-records", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=run_fd
        )
        destination = run_dir / "proof-records" / f"proof-{uuid.uuid4().hex}.json"
        _write_json_at(records_fd, destination.name, checked, replace=False)
        if _PROOF_RECORD_POST_RETENTION_HOOK is not None:
            _PROOF_RECORD_POST_RETENTION_HOOK()
        entries = list(prior_refs)
        entries.append(_record_index_reference(destination))
        index = {
            "schema": _PROOF_INDEX_SCHEMA,
            "run": owner,
            "inventory_digest": inventory["digest"],
            "payload": payload_fingerprint(),
            "generation": uuid.uuid4().hex,
            "records": entries,
        }
        _write_json_at(run_fd, "proof-index.json", index, replace=True)
        return destination
    except OSError as exc:
        raise DeliveryError("proof record retention failed") from exc
    finally:
        if records_fd >= 0:
            os.close(records_fd)
        os.close(run_fd)


def record_observed_proof(
    run_dir: Path, proof: Mapping[str, Any], *, outer: bool = False
) -> Path:
    """Retain an immutable observation through one freshly acquired run lock."""
    actual_role = _caller_proof_role(outer=outer)
    try:
        preliminary = _check_owner(run_dir)
        preliminary_card = REPO_ROOT / preliminary["card"]
    except (OSError, ValueError) as exc:
        raise DeliveryError("proof recording has unsafe owning metadata") from exc
    with verification_attempt_lock(run_dir, preliminary_card, "focused") as ownership:
        if _check_owner(run_dir)["card"] != preliminary["card"]:
            raise DeliveryError("proof recording owner changed while waiting")
        return _record_observed_proof_with_ownership(
            run_dir, proof, actual_role=actual_role, ownership=ownership
        )


def _unresolved_proof_run_dir() -> Path:
    """Return the lexical CHRL run path so no symlink is normalized away."""
    raw = os.environ.get("CHRL_RUN_DIR")
    if not raw:
        raise DeliveryError("proof recording requires CHRL_RUN_DIR")
    path = Path(os.path.abspath(raw))
    roots = (Path(os.path.abspath(RUNTIME_ROOT / "runs")),)
    if not any((path.is_relative_to(root) for root in roots)):
        raise DeliveryError("proof recording run is outside the local runtime root")
    return path


def record_observed_proof_artifact(
    run_dir: Path, artifact: Path, *, outer: bool = False
) -> Path:
    """Read a bounded closed proof input; it is data, never a command locator."""
    if not artifact.is_absolute():
        artifact = REPO_ROOT / artifact
    try:
        relative = artifact.relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise DeliveryError("proof input is outside the repository") from exc
    path = _safe_reference_path(relative, root=run_dir, label="proof input")
    try:
        data = _check_bytes(path, 2 * 1024 * 1024)
    except (OSError, ValueError) as exc:
        raise DeliveryError("proof input cannot be safely read") from exc
    proof = _decode_closed_json(data, label="proof input")
    return record_observed_proof(run_dir, proof, outer=outer)


def record_outer_observed_proof(run_dir: Path, proof: Mapping[str, Any]) -> Path:
    """Explicit final-stage path for the runner's actual `outer` session."""
    return record_observed_proof(run_dir, proof, outer=True)


def _require_final_test_receipt_membership(
    observations: Sequence[Mapping[str, Any]], verification: Any
) -> None:
    """Bind retained final test proofs to this exact validated final set.

    ``_validated_index_records`` has already authenticated each proof artifact.
    Compare its retained reference with bytes and identities carried by the sole
    ``_verified_command_set`` reader; do not reopen a receipt here.
    """
    if (
        not isinstance(verification, _VerifiedCommandSet)
        or verification.lane != "final"
    ):
        raise DeliveryError("final test proof requires the current final command set")
    receipts: set[tuple[str, str, str, str, str]] = set()
    for entry, (item, _log, record_data) in zip(
        verification.payload["commands"], verification.receipts, strict=True
    ):
        command = item["command_identity"]
        record_path = entry["record"]
        receipts.add(
            (
                item["attempt_id"],
                json.dumps(command, sort_keys=True, separators=(",", ":")),
                record_path,
                str(len(record_data)),
                hashlib.sha256(record_data).hexdigest(),
            )
        )
    for proof in observations:
        if proof["stage"] != "final" or proof["kind"] != "test":
            continue
        artifact = proof["artifact"]
        reference = (
            proof["attempt_id"],
            json.dumps(
                proof["command_identity"], sort_keys=True, separators=(",", ":")
            ),
            artifact["path"],
            str(artifact["size"]),
            artifact["sha256"],
        )
        if proof["lane"] != "final" or reference not in receipts:
            raise DeliveryError(
                "final test proof receipt is outside the current configured final set"
            )


def require_current_stage_proofs(
    card: Path, run_dir: Path, stages: Sequence[str], *, final_verification: Any = None
) -> list[dict[str, Any]]:
    """Return current, revalidated observations for each due condition."""
    inventory = _current_proof_inventory(card, run_dir)
    if inventory is None:
        return []
    if not set(stages) <= _PROOF_STAGES:
        raise DeliveryError("unknown observed-proof stage")
    due = {row["identity"] for row in inventory["conditions"] if row["stage"] in stages}
    try:
        observations = _validated_index_records(
            _check_json(_proof_index_path(run_dir)),
            card=card,
            run_dir=run_dir,
            inventory=inventory,
        )
    except FileNotFoundError:
        if due:
            raise DeliveryError(
                f"observed proof coverage mismatch: missing={sorted(due)}, duplicates=[], foreign=[]"
            )
        return []
    except (OSError, ValueError) as exc:
        raise DeliveryError("observed proof index cannot be safely read") from exc
    found = [proof["condition"] for proof in observations if proof["stage"] in stages]
    missing = sorted(due - set(found))
    foreign = sorted(set(found) - due)
    duplicates = sorted(
        {condition for condition in found if found.count(condition) > 1}
    )
    if missing or duplicates or foreign:
        raise DeliveryError(
            f"observed proof coverage mismatch: missing={missing}, duplicates={duplicates}, foreign={foreign}"
        )
    if "final" in stages and final_verification is not None:
        _require_final_test_receipt_membership(observations, final_verification)
    return observations


def planned_changes(card: Path) -> list[tuple[int, str]]:
    """Return ordered Change sections declared by one board card."""
    if native.is_native(card):
        return native.task_groups(runner_module(), card)
    return [
        (int(number), slug)
        for number, slug in re.findall(
            "^## Change ([0-9]+): `([^`]+)`$",
            card.read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        )
    ]


def change_plan_reasons(changes: Sequence[tuple[int, str]]) -> list[str]:
    """Validate a non-empty, contiguous and uniquely named change sequence."""
    if not changes:
        return ["one board card must contain at least one executable `## Change 1`"]
    reasons: list[str] = []
    observed_numbers = [number for number, _ in changes]
    expected_numbers = list(range(1, len(changes) + 1))
    if observed_numbers != expected_numbers:
        reasons.append(
            f"board-card Change sections must be ordered and contiguous from 1; observed={observed_numbers}"
        )
    slugs = [slug for _, slug in changes]
    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        reasons.append(
            "board-card Change slugs must be unique: " + ", ".join(duplicates)
        )
    return reasons


def _delivery_budget(card: Path) -> tuple[dict[str, int | str], list[str]]:
    """Parse the small, explicit delivery estimate from a board card."""
    required = {
        "primary_invariant",
        "expected_wall_minutes",
        "production_owners",
        "runtime_contours",
        "estimated_product_files",
        "estimated_production_loc",
    }
    values: dict[str, int | str] = {}
    reasons: list[str] = []
    for line in section_body(card.read_text(encoding="utf-8"), "Delivery Budget"):
        if not line:
            continue
        match = re.fullmatch("- ([a-z_]+): (.+)", line)
        if match is None:
            reasons.append(f"malformed Delivery Budget entry: {line}")
            continue
        key, raw = match.groups()
        if key in values:
            reasons.append(f"duplicate Delivery Budget field: {key}")
            continue
        if key == "primary_invariant":
            values[key] = raw.strip()
            continue
        try:
            value = int(raw)
        except ValueError:
            reasons.append(f"Delivery Budget field {key} must be an integer")
            continue
        if value < 0:
            reasons.append(f"Delivery Budget field {key} must be non-negative")
            continue
        values[key] = value
    missing = sorted(required - values.keys())
    if missing:
        reasons.append(f"missing Delivery Budget fields: {', '.join(missing)}")
    if values.get("primary_invariant") == "":
        reasons.append("primary_invariant must not be empty")
    return (values, reasons)


def admission_report(card: Path) -> dict[str, Any]:
    """Decide whether one card is small enough for one measured delivery."""
    require_deliverable_card(card)
    validate_evidence_plan(card)
    card.read_text(encoding="utf-8")
    reasons: list[str] = []
    changes = planned_changes(card)
    reasons.extend(change_plan_reasons(changes))
    try:
        criteria_count = len(admission_acceptance_criteria(card))
    except DeliveryError as exc:
        criteria_count = 0
        reasons.append(str(exc))
    budget, budget_reasons = _delivery_budget(card)
    reasons.extend(budget_reasons)
    configured = profile().get("admission", {})
    limits = {
        "expected_wall_minutes": "max_expected_wall_minutes",
        "production_owners": "max_production_owners",
        "runtime_contours": "max_runtime_contours",
        "estimated_product_files": "max_estimated_product_files",
        "estimated_production_loc": "max_estimated_production_loc",
    }
    for field, limit_key in limits.items():
        value = budget.get(field)
        limit = configured.get(limit_key)
        if not isinstance(limit, int) or limit < 0:
            raise DeliveryError(f"invalid admission profile limit: {limit_key}")
        if budget_limits_enforced() and isinstance(value, int) and (value > limit):
            reasons.append(f"{field}={value} exceeds {limit_key}={limit}")
    acceptance_limit = configured.get("max_acceptance_criteria")
    if not isinstance(acceptance_limit, int) or acceptance_limit < 1:
        raise DeliveryError("invalid admission profile limit: max_acceptance_criteria")
    if budget_limits_enforced() and criteria_count > acceptance_limit:
        reasons.append(
            f"acceptance_criteria={criteria_count} exceeds max_acceptance_criteria={acceptance_limit}"
        )
    return {
        "schema": "changerail.delivery-admission.v1",
        "card": repo_relative(card),
        "status": "SPLIT_REQUIRED" if reasons else "READY",
        "change_count": len(changes),
        "acceptance_criteria": criteria_count,
        "budget": budget,
        "limits": configured,
        "budget_limits_enforced": budget_limits_enforced(),
        "reasons": reasons,
        "lifecycle": native.lifecycle_mode(card),
    }


def dependencies(card: Path) -> list[str]:
    body = section_body(card.read_text(encoding="utf-8"), "Depends On")
    if [line for line in body if line] == ["- none"]:
        return []
    return [
        match.group(1) for line in body if (match := re.fullmatch("- `([^`]+)`", line))
    ]


def changed_paths() -> list[str]:
    tracked = git(
        "diff", "--name-only", "--no-renames", "-z", "HEAD", text=False
    ).stdout.split(b"\x00")
    staged = git(
        "diff", "--cached", "--name-only", "--no-renames", "-z", "HEAD", text=False
    ).stdout.split(b"\x00")
    untracked = git(
        "ls-files", "--others", "--exclude-standard", "-z", text=False
    ).stdout.split(b"\x00")
    paths = {os.fsdecode(item) for item in [*tracked, *staged, *untracked] if item}
    return sorted(
        (
            path
            for path in paths
            if not any(
                (
                    path == prefix.rstrip("/") or path.startswith(prefix)
                    for prefix in EXCLUDED_PREFIXES
                )
            )
        )
    )


def live_board_reference_sources(paths: Sequence[str] | None = None) -> list[str]:
    """Return payload and live-board files whose exact card links must resolve."""
    frozen = checked_frozen_records()
    selected = set(paths if paths is not None else changed_paths())
    for column in ("1.backlog", "2.todo", "3.inprogress"):
        selected.update(
            (repo_relative(path) for path in (BOARD_ROOT / column).glob("*.md"))
        )
    return sorted(
        (
            relative
            for relative in selected
            if not relative.startswith("openspec/board/4.done/")
            and (not relative.startswith("openspec/board/5.canceled/"))
            and ((REPO_ROOT / relative).resolve(strict=False) not in frozen)
        )
    )


def dangling_live_board_references(
    paths: Sequence[str] | None = None,
) -> list[dict[str, str]]:
    """Find stale exact board paths in the current payload and live board."""
    active_names = {path.name for path in board_activity()["active"]}
    findings: list[dict[str, str]] = []
    for relative in live_board_reference_sources(paths):
        source = REPO_ROOT / relative
        if not source.is_file():
            continue
        try:
            text = source.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for reference in sorted(set(BOARD_REFERENCE_PATTERN.findall(text))):
            target = REPO_ROOT / reference
            if target.is_file():
                continue
            target_path = Path(reference)
            if target_path.parent.name == "2.todo" and target_path.name in active_names:
                continue
            findings.append({"source": relative, "reference": reference})
    return findings


def require_live_board_references(paths: Sequence[str] | None = None) -> None:
    """Fail closed when a live payload names a board card that does not exist."""
    findings = dangling_live_board_references(paths)
    if findings:
        rendered = "; ".join(
            (f"{item['source']} -> {item['reference']}" for item in findings)
        )
        raise DeliveryError(f"dangling live board references: {rendered}")


def staged_paths() -> list[str]:
    staged = git(
        "diff", "--cached", "--name-only", "--no-renames", "-z", "HEAD", text=False
    ).stdout.split(b"\x00")
    return sorted((os.fsdecode(item) for item in staged if item))


def _update_path_digest(digest: _Digest, relative: str) -> None:
    digest.update(f"path\x00{relative}\x00".encode())
    absolute = REPO_ROOT / relative
    try:
        stat = absolute.lstat()
    except FileNotFoundError:
        digest.update(b"deleted\x00")
        return
    digest.update(f"mode\x00{stat.st_mode:o}\x00".encode())
    if absolute.is_symlink():
        digest.update(b"symlink\x00")
        digest.update(os.fsencode(os.readlink(absolute)))
    elif absolute.is_file():
        digest.update(b"file\x00")
        with absolute.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    elif absolute.is_dir():
        digest.update(b"replaced-by-directory\x00")
    else:
        raise DeliveryError(f"changed path is not a regular file: {relative}")
    digest.update(b"\x00")


def path_fingerprints(paths: Sequence[str]) -> dict[str, str]:
    fingerprints: dict[str, str] = {}
    for relative in sorted(paths):
        digest = hashlib.sha256()
        _update_path_digest(digest, relative)
        fingerprints[relative] = f"sha256:{digest.hexdigest()}"
    return fingerprints


def payload_fingerprint(paths: Sequence[str] | None = None) -> dict[str, str]:
    selected = sorted(paths if paths is not None else changed_paths())
    head = git("rev-parse", "HEAD").stdout.strip()
    digest = hashlib.sha256()
    digest.update(f"head\x00{head}\x00".encode())
    for relative in selected:
        _update_path_digest(digest, relative)
    return {"head_commit": head, "payload_fingerprint": f"sha256:{digest.hexdigest()}"}


def execution_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    if extra:
        env.update(extra)
    return env


def require_legacy_history() -> None:
    """Preserve project-configured historical artifacts and enforce new ownership."""
    configured = profile().get("history", {}).get("manifest")
    history = load_json(REPO_ROOT / _safe_path(configured)) if configured else {}
    expected = history.get("files", {})
    if not isinstance(expected, dict):
        raise DeliveryError("history files must be an object")
    root = REPO_ROOT / "openspec/changes"
    observed = {}
    if root.is_symlink():
        raise DeliveryError("legacy lifecycle root must not be a symlink")
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise DeliveryError("legacy lifecycle must not contain symlinks")
        if path.is_file():
            observed[repo_relative(path)] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    if any((observed.get(name) != digest for name, digest in expected.items())):
        raise DeliveryError(
            "legacy lifecycle changed; frozen artifacts must remain exact"
        )
    native.require_owned_artifacts(
        runner_module(), set(observed) - set(expected), set(expected)
    )


def external_changerail_symlinks() -> list[str]:
    owned = (
        "scripts/changerail",
        "tools/changerail",
        "bin/chrl",
        "bin/chrl-run",
        "bin/chrl-kit",
    )
    found = []
    for relative in owned:
        root = REPO_ROOT / relative
        for path in (root, *root.rglob("*")):
            if path.is_symlink() and (
                not path.resolve(strict=False).is_relative_to(REPO_ROOT)
            ):
                if source_binding.trusted_path(REPO_ROOT, path) is None:
                    found.append(repo_relative(path))
    return sorted(found)


def install_local_hooks() -> dict[str, str]:
    configured = profile().get("project", {}).get("hooks_path", "")
    if not configured:
        return {"status": "not-configured"}
    hooks = REPO_ROOT / _safe_path(configured)
    pre_commit = hooks / "pre-commit"
    if (
        not pre_commit.is_file()
        or pre_commit.is_symlink()
        or (not os.access(pre_commit, os.X_OK))
    ):
        raise DeliveryError(f"local pre-commit hook is unavailable: {pre_commit}")
    git("config", "core.hooksPath", configured)
    return {"status": "installed", "core.hooksPath": configured}


def wiring_report() -> dict[str, Any]:
    """Check local installation without running agents, delivery or runtime tools."""
    errors: list[str] = []
    for relative in ("bin/chrl", "bin/chrl-run", "bin/openspec"):
        path = REPO_ROOT / relative
        try:
            trusted = source_binding.trusted_path(REPO_ROOT, path)
            if (
                (path.is_symlink() and trusted is None)
                or not path.is_file()
                or not os.access(path, os.X_OK)
            ):
                errors.append(f"missing local executable: {relative}")
        except DeliveryError as exc:
            errors.append(str(exc))
    for role in ("chrl-native-deliver", "chrl-native-review"):
        path = REPO_ROOT / "tools/changerail/skills" / role / "SKILL.md"
        if not path.is_file():
            errors.append(f"missing local skill: {role}")
    try:
        errors.extend(
            f"external workflow link: {name}" for name in external_changerail_symlinks()
        )
        source = source_binding.source_info(REPO_ROOT)
    except (DeliveryError, OSError, ValueError) as exc:
        errors.append(str(exc))
        source = {"mode": "invalid"}
    try:
        require_legacy_history()
        checked_frozen_records()
        import jsonschema

        for path in (REPO_ROOT / "tools/changerail/schemas").glob("*.json"):
            jsonschema.Draft202012Validator.check_schema(load_json(path))
        for role in ("implementation", "review"):
            model_route(profile(), role)
        native.adapter(runner_module())
    except (DeliveryError, ImportError, ValueError) as exc:
        errors.append(str(exc))
    hooks = git("config", "--get", "core.hooksPath", check=False).stdout.strip()
    configured_hooks = profile().get("project", {}).get("hooks_path", "")
    if configured_hooks and (
        hooks != configured_hooks
        or not (REPO_ROOT / _safe_path(configured_hooks) / "pre-commit").is_file()
    ):
        errors.append("local hook is not installed; run ./bin/chrl install")
    return {
        "schema": "changerail.local-wiring.v1",
        "ok": not errors,
        "errors": errors,
        "source": source,
    }


def _safe_path(value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or ("\x00" in value)
        or Path(value).is_absolute()
    ):
        raise DeliveryError("payload path must be a non-absolute repository path")
    candidate = Path(value)
    if any((part in {"", ".", ".."} for part in candidate.parts)):
        raise DeliveryError("payload path escapes the repository")
    absolute = REPO_ROOT / candidate
    if any(
        (
            part.is_symlink()
            for part in (absolute, *absolute.parents)
            if part.is_relative_to(REPO_ROOT)
        )
    ):
        raise DeliveryError("payload does not accept symlinked payload paths")
    try:
        absolute.resolve(strict=False).relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise DeliveryError("payload path escapes the repository") from exc
    if candidate.as_posix() != value:
        raise DeliveryError("payload path is not canonical")
    return value


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _path_state(relative: str) -> dict[str, Any]:
    """Return one exact path state; absent is distinct from an unreadable path."""
    _safe_path(relative)
    path = REPO_ROOT / relative
    try:
        item = path.lstat()
    except FileNotFoundError:
        return {
            "kind": "deleted",
            "mode": 0,
            "digest": path_fingerprints([relative])[relative],
        }
    if stat.S_ISLNK(item.st_mode) or not stat.S_ISREG(item.st_mode):
        raise DeliveryError("payload paths must be regular files or deleted")
    _check_bytes(path, 32 * 1024 * 1024)
    return {
        "kind": "file",
        "mode": stat.S_IMODE(item.st_mode),
        "digest": path_fingerprints([relative])[relative],
    }


def _deleted_digest(relative: str) -> str:
    digest = hashlib.sha256()
    digest.update(f"path\x00{relative}\x00".encode())
    digest.update(b"deleted\x00")
    return f"sha256:{digest.hexdigest()}"


def _manifest_for_run(card: Path, run_dir: Path) -> Path:
    try:
        if _check_owner(run_dir)["card"] != repo_relative(card):
            raise ValueError("foreign manifest owning card")
    except (OSError, ValueError) as exc:
        raise DeliveryError(f"unsafe manifest owning metadata: {exc}") from exc
    return manifest_path(card_id(card))


def _write_review_json(run_dir: Path, path: Path, payload: Mapping[str, Any]) -> None:
    write_json(path, payload)


@contextmanager
def _review_setup_lock(run_dir: Path):
    (run_dir / "reviews").mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        run_dir / "review.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 384
    )
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise DeliveryError("review lock is not a regular file")
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        os.close(descriptor)


def _safe_recovery_path(relative: object) -> bool:
    """Accept one repository-relative payload path without following ancestors."""
    if (
        not isinstance(relative, str)
        or not relative
        or "\\" in relative
        or ("\x00" in relative)
    ):
        return False
    candidate = Path(relative)
    if candidate.is_absolute() or candidate.as_posix() != relative:
        return False
    current = REPO_ROOT
    for part in candidate.parts[:-1]:
        if part in ("", ".", ".."):
            return False
        current /= part
        try:
            if current.is_symlink():
                return False
        except OSError:
            return False
    return all((part not in ("", ".", "..") for part in candidate.parts))


def _safe_recovery_manifest(path: Path, runs_root: Path) -> bool:
    """Only read a regular run-local manifest whose ancestry is not linked."""
    try:
        relative = path.relative_to(REPO_ROOT)
    except ValueError:
        return False
    current = REPO_ROOT
    try:
        for part in relative.parts:
            current /= part
            if current.is_symlink():
                return False
        return path.is_file() and path.parent.parent == runs_root
    except OSError:
        return False


def _load_recovery_manifest(path: Path) -> dict[str, Any]:
    """Read one retained manifest while refusing ambiguous JSON object keys."""

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for key, value in pairs:
            if key in payload:
                raise ValueError(f"duplicate JSON key {key!r}")
            payload[key] = value
        return payload

    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=unique_object
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise DeliveryError(f"cannot read recovery JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise DeliveryError(f"expected JSON object in {path}")
    return payload


def recovery_source(
    card: Path, dirty: Sequence[str], *, required_run_id: str | None = None
) -> tuple[bool, str, dict[str, Any] | None]:
    require_deliverable_card(card)
    if not dirty:
        return (False, "recovery requires a retained product payload", None)
    actual_paths = changed_paths()
    if sorted(dirty) != actual_paths:
        return (False, "recovery dirty paths do not match the current worktree", None)
    if not all((_safe_recovery_path(item) for item in actual_paths)):
        return (
            False,
            "recovery payload contains an unsafe repository-relative path",
            None,
        )
    expected_card = {"id": card_id(card), "path": repo_relative(card)}
    runs_root = RUNTIME_ROOT / "runs"
    try:
        candidates = sorted(runs_root.iterdir(), reverse=True)
    except OSError:
        candidates = []
    mismatch: tuple[list[str], dict[str, Any]] | None = None
    invalid_proof = False
    for previous_run in candidates:
        run_id = previous_run.name
        if required_run_id is not None and run_id != required_run_id:
            continue
        path = previous_run / "manifest.json"
        if (
            not re.fullmatch("[A-Za-z0-9][A-Za-z0-9._-]*", run_id)
            or previous_run.is_symlink()
            or (not _safe_recovery_manifest(path, runs_root))
        ):
            continue
        try:
            require_current_execution(previous_run)
            from scripts.changerail import plan_restoration

            manifest = plan_restoration.effective_manifest(
                runner_module(), previous_run
            )
            if manifest is None:
                manifest = _load_recovery_manifest(path)
        except (DeliveryError, UnicodeDecodeError, OSError, ValueError):
            invalid_proof = True
            continue
        if manifest.get("card") != expected_card:
            continue
        expected_paths = manifest.get("paths")
        if (
            manifest.get("run_id") != run_id
            or manifest.get("schema") != "changerail.delivery-manifest.v1"
        ):
            invalid_proof = True
            continue
        if (
            not isinstance(expected_paths, list)
            or not all((isinstance(item, str) for item in expected_paths))
            or len(expected_paths) != len(set(expected_paths))
            or (not all((_safe_recovery_path(item) for item in expected_paths)))
        ):
            invalid_proof = True
            continue
        if sorted(expected_paths) != actual_paths:
            mismatch = (expected_paths, manifest)
            continue
        fingerprint = manifest.get("fingerprint")
        path_hashes = manifest.get("path_fingerprints")
        if (
            manifest.get("baseline_head") != git("rev-parse", "HEAD").stdout.strip()
            or fingerprint != payload_fingerprint(actual_paths)
            or path_hashes != path_fingerprints(actual_paths)
        ):
            invalid_proof = True
            continue
        return (True, f"exact payload from {run_id}", manifest)
    if mismatch is not None:
        expected_paths, manifest = mismatch
        return (
            False,
            f"dirty paths differ from previous manifest: expected={sorted(expected_paths)} actual={sorted(dirty)}",
            manifest,
        )
    if invalid_proof:
        return (False, "previous delivery manifest lacks exact fingerprint proof", None)
    return (False, "previous delivery manifest is unavailable", None)


def doctor(
    card_value: str,
    *,
    check_remote: bool = True,
    recovery: bool = False,
    required_run_id: str | None = None,
) -> dict[str, Any]:
    card = resolve_deliverable_card(card_value)
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append(
            {"name": name, "status": "pass" if passed else "fail", "detail": detail}
        )

    current_profile = profile()
    try:
        model_route(current_profile, "implementation")
        model_route(current_profile, "review")
        _SessionCommandBudget("implementation", current_profile.get("budgets", {}))
        _SessionCommandBudget("review", current_profile.get("budgets", {}))
        profile_ok = True
        profile_detail = "native-only; shared review limit=2; time is advisory"
    except (DeliveryError, KeyError, TypeError, ValueError) as exc:
        profile_ok = False
        profile_detail = str(exc)
    add("measured-profile", profile_ok, profile_detail)
    dirty = changed_paths()
    recovery_manifest: dict[str, Any] | None = None
    if recovery:
        recovery_ok, recovery_detail, recovery_manifest = recovery_source(
            card, dirty, required_run_id=required_run_id
        )
        add("recovery-payload", recovery_ok, recovery_detail)
        objective = os.environ.get("CHRL_RECOVERY_OBJECTIVE", "").strip()
        add(
            "recovery-objective",
            0 < len(objective) <= 1000,
            "bounded objective supplied"
            if 0 < len(objective) <= 1000
            else "set CHRL_RECOVERY_OBJECTIVE to 1..1000 characters",
        )
        staged = staged_paths()
        add(
            "clean-index",
            not staged,
            "clean" if not staged else f"pre-staged paths: {staged[:10]}",
        )
    else:
        add(
            "clean-start",
            not dirty,
            "clean" if not dirty else f"changed paths: {dirty[:10]}",
        )
    branch = git("branch", "--show-current").stdout.strip()
    add("branch", branch == "main", f"branch={branch or 'detached'}")
    upstream = git(
        "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", check=False
    )
    add(
        "upstream",
        upstream.returncode == 0,
        upstream.stdout.strip() or upstream.stderr.strip(),
    )
    if (
        check_remote
        and current_profile.get("require_push", True)
        and (upstream.returncode == 0)
    ):
        remote, remote_branch = upstream.stdout.strip().split("/", maxsplit=1)
        remote_check = subprocess.run(
            ["git", "ls-remote", "--exit-code", remote, f"refs/heads/{remote_branch}"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
        add("remote", remote_check.returncode == 0, f"{remote}/{remote_branch}")
    add(
        "card-state",
        card.parent.name == ("3.inprogress" if recovery else "2.todo"),
        f"card={repo_relative(card)}",
    )
    if not recovery:
        admission = admission_report(card)
        add(
            "right-size-admission",
            admission["status"] == "READY",
            "READY"
            if admission["status"] == "READY"
            else "SPLIT_REQUIRED: " + "; ".join(admission["reasons"]),
        )
    if native.is_native(card):
        if recovery:
            receipt = RUNTIME_ROOT / "native-plans" / card.stem / "native-plan.json"
            add(
                "native-accepted-plan",
                receipt.is_file(),
                "accepted plan receipt retained for exact recovery"
                if receipt.is_file()
                else "accepted native plan receipt is missing",
            )
        else:
            try:
                from scripts.changerail.openspec_board import require_accepted

                require_accepted(runner_module(), card)
                add(
                    "native-accepted-plan",
                    True,
                    "accepted local OpenSpec artifacts match the card contract",
                )
            except DeliveryError as exc:
                add("native-accepted-plan", False, str(exc))
    activity = board_activity()
    active = activity["active"]
    for disposition in ("superseded-no-go", "suspended-not-verifiable"):
        add(
            disposition,
            True,
            ", ".join((repo_relative(path) for path in activity[disposition]))
            or "none",
        )
    add(
        "single-active-card",
        active == [card] if recovery else not active,
        repo_relative(card)
        if recovery and active == [card]
        else "empty"
        if not active
        else ", ".join((repo_relative(item) for item in active)),
    )
    dependency_errors: list[str] = []
    for dependency in dependencies(card):
        target = REPO_ROOT / dependency
        if not target.is_file() or target.parent.name != "4.done":
            dependency_errors.append(dependency)
    add(
        "dependencies",
        not dependency_errors,
        "satisfied" if not dependency_errors else f"not done: {dependency_errors}",
    )
    try:
        require_legacy_history()
        add("legacy-history", True, "unchanged migration snapshot")
    except DeliveryError as exc:
        add("legacy-history", False, str(exc))
    skills = REPO_ROOT / "tools" / "changerail" / "skills"
    deliver_skill = "chrl-native-deliver"
    required_skills = (
        skills / deliver_skill / "SKILL.md",
        skills
        / ("chrl-native-review" if native.is_native(card) else "chrl-review")
        / "SKILL.md",
    )
    add("local-skills", all((path.is_file() for path in required_skills)), str(skills))
    linked = external_changerail_symlinks()
    add(
        "local-authority",
        not linked,
        "local" if not linked else f"external symlinks: {linked}",
    )
    hooks_path = git("config", "--get", "core.hooksPath", check=False).stdout.strip()
    configured_hooks = profile().get("project", {}).get("hooks_path", "")
    hook = (
        REPO_ROOT / _safe_path(configured_hooks) / "pre-commit"
        if configured_hooks
        else None
    )
    add(
        "local-hooks",
        not configured_hooks
        or (
            hooks_path == configured_hooks
            and hook.is_file()
            and not hook.is_symlink()
            and os.access(hook, os.X_OK)
        ),
        f"core.hooksPath={hooks_path or 'unset'}",
    )
    payload = {
        "schema": "changerail.delivery-doctor.v1",
        "checked_at": utc_now(),
        "ok": all((check["status"] == "pass" for check in checks)),
        "card": repo_relative(card),
        "mode": "delivery",
        "checks": checks,
    }
    if recovery_manifest is not None:
        payload["recovery_of"] = recovery_manifest.get("run_id")
    return payload


def current_run_dir(required: bool = True) -> Path | None:
    raw = os.environ.get("CHRL_RUN_DIR")
    if raw:
        path = Path(os.path.abspath(raw))
        if path.resolve(strict=False) != path:
            raise DeliveryError(
                "unsafe current execution owner: CHRL_RUN_DIR contains symlinks"
            )
        allowed_roots = ((RUNTIME_ROOT / "runs").resolve(strict=False),)
        if not any((path.is_relative_to(expected) for expected in allowed_roots)):
            raise DeliveryError("CHRL_RUN_DIR is outside the local runtime root")
        require_current_execution(path)
        return path
    if required:
        raise DeliveryError("this command must run inside ./bin/chrl-run")
    return None


def manifest_path(identifier: str) -> Path:
    return RUNTIME_ROOT / "delivery-manifests" / f"{identifier}.json"


def read_phase_events(run_dir: Path) -> list[dict[str, Any]]:
    """Read validated phase events retained for one measured run."""
    path = run_dir / "phase-events.jsonl"
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DeliveryError(
                f"invalid phase event at {repo_relative(path)}:{line_number}"
            ) from exc
        if not isinstance(event, dict):
            raise DeliveryError(
                f"phase event must be an object at {repo_relative(path)}:{line_number}"
            )
        events.append(event)
    return events


def declared_change_plan(run_dir: Path) -> list[tuple[int, str]] | None:
    """Return the immutable Change plan captured by a delivery run."""
    path = run_dir / "run.json"
    if not path.exists():
        return None
    raw = _check_json(path).get("change_plan")
    if raw is None:
        return None
    if not isinstance(raw, list):
        raise DeliveryError("delivery run change_plan must be a list")
    plan: list[tuple[int, str]] = []
    for item in raw:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("number"), int)
            or (not isinstance(item.get("slug"), str))
        ):
            raise DeliveryError("delivery run change_plan contains an invalid entry")
        plan.append((item["number"], item["slug"]))
    if plan:
        reasons = change_plan_reasons(plan)
        if reasons:
            raise DeliveryError(
                "invalid delivery run change_plan: " + "; ".join(reasons)
            )
    return plan


def _change_event_pairs(events: Sequence[dict[str, Any]]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for event in events:
        phase = str(event.get("phase") or "")
        if not phase.startswith("change-"):
            continue
        stage = str(event.get("stage") or "")
        if re.fullmatch("change-[1-9][0-9]*", phase) is None or stage not in {
            "starting",
            "complete",
        }:
            raise DeliveryError(f"invalid Change checkpoint event: {phase} {stage}")
        pairs.append((phase, stage))
    return pairs


def _expected_change_event_pairs(
    plan: Sequence[tuple[int, str]],
) -> list[tuple[str, str]]:
    return [
        event
        for number, _slug in plan
        for event in (
            (f"change-{number}", "starting"),
            (f"change-{number}", "complete"),
        )
    ]


def _inherited_change_events(run_dir: Path) -> list[dict[str, Any]]:
    path = run_dir / "run.json"
    if not path.exists():
        return []
    raw = _check_json(path).get("inherited_change_events", [])
    if not isinstance(raw, list) or not all((isinstance(item, dict) for item in raw)):
        raise DeliveryError(
            "delivery run inherited_change_events must be object records"
        )
    return [dict(item) for item in raw]


def combined_change_events(run_dir: Path) -> list[dict[str, Any]]:
    """Return inherited and current Change events as one logical prefix."""
    return [*_inherited_change_events(run_dir), *read_phase_events(run_dir)]


def validate_change_event_prefix(
    plan: Sequence[tuple[int, str]], events: Sequence[dict[str, Any]]
) -> list[tuple[str, str]]:
    """Require Change events to be a non-repeating prefix of the card plan."""
    observed = _change_event_pairs(events)
    expected = _expected_change_event_pairs(plan)
    if observed != expected[: len(observed)]:
        next_expected = (
            expected[len(observed)] if len(observed) < len(expected) else None
        )
        raise DeliveryError(
            f"Change checkpoint order violation: observed={observed}, next_expected={next_expected}"
        )
    if len(observed) > len(expected):
        raise DeliveryError("Change checkpoint events exceed the declared plan")
    return observed


def change_checkpoint_statuses(
    plan: Sequence[tuple[int, str]], events: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Summarize completion and timing for every declared Change checkpoint."""
    validate_change_event_prefix(plan, events)
    change_events = [
        event for event in events if str(event.get("phase") or "").startswith("change-")
    ]
    summaries: list[dict[str, Any]] = []
    for number, slug in plan:
        phase = f"change-{number}"
        started = next(
            (
                str(event.get("at") or "")
                for event in change_events
                if event.get("phase") == phase and event.get("stage") == "starting"
            ),
            None,
        )
        completed = next(
            (
                str(event.get("at") or "")
                for event in change_events
                if event.get("phase") == phase and event.get("stage") == "complete"
            ),
            None,
        )
        duration: float | None = None
        if started and completed:
            try:
                began_at = datetime.fromisoformat(started.replace("Z", "+00:00"))
                ended_at = datetime.fromisoformat(completed.replace("Z", "+00:00"))
                duration = round(max(0.0, (ended_at - began_at).total_seconds()), 3)
            except ValueError:
                duration = None
        summaries.append(
            {
                "number": number,
                "slug": slug,
                "status": "complete"
                if completed
                else "started"
                if started
                else "pending",
                "started_at": started,
                "completed_at": completed,
                "duration_seconds": duration,
            }
        )
    return summaries


def require_completed_change_plan(card: Path, run_dir: Path) -> None:
    """Block pre-review work until every captured Change is narrowly green."""
    require_run_lifecycle(card, run_dir)
    if native.is_native(card):
        native.require_plan(runner_module(), card, run_dir / "native-plan.json")
        native.require_complete(runner_module(), card)
    plan = declared_change_plan(run_dir)
    if not plan:
        return
    current_plan = planned_changes(card)
    if current_plan != plan:
        raise DeliveryError(
            f"card Change plan differs from delivery baseline: {current_plan} != {plan}"
        )
    events = combined_change_events(run_dir)
    observed = validate_change_event_prefix(plan, events)
    expected = _expected_change_event_pairs(plan)
    if observed != expected:
        raise DeliveryError(
            f"preverification requires every Change checkpoint to be complete; next_expected={expected[len(observed)]}"
        )


def require_run_lifecycle(card: Path, run_dir: Path) -> None:
    require_current_execution(run_dir)
    if native.lifecycle_mode(card) != "openspec-v1":
        raise DeliveryError("only openspec-v1 cards are executable")


def emit_event(phase: str, stage: str) -> None:
    run_dir = current_run_dir()
    assert run_dir is not None
    if phase.startswith("change-"):
        if _check_json(run_dir / "run.json").get("lifecycle_mode") == "openspec-v1":
            card = REPO_ROOT / _check_owner(run_dir)["card"]
            from scripts.changerail.native_workflow import checkpoint

            checkpoint(runner_module(), card, run_dir, phase, stage)
        plan = declared_change_plan(run_dir)
        if not plan:
            raise DeliveryError(
                "Change checkpoint event requires a declared change_plan"
            )
        prospective = {
            "schema": "changerail.delivery-phase-event.v1",
            "at": utc_now(),
            "phase": phase,
            "stage": stage,
        }
        validate_change_event_prefix(
            plan, [*combined_change_events(run_dir), prospective]
        )
    path = run_dir / "phase-events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "schema": "changerail.delivery-phase-event.v1",
        "at": utc_now(),
        "phase": phase,
        "stage": stage,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def concise_event(event: dict[str, Any]) -> str | None:
    event_type = event.get("type")
    item_value = event.get("item")
    item: dict[str, Any] = item_value if isinstance(item_value, dict) else {}
    if event_type == "item.completed" and item.get("type") == "agent_message":
        return str(item.get("text") or "")
    if event_type == "item.started" and item.get("type") == "command_execution":
        return f"[command] {item.get('id') or 'unknown'}"
    if event_type == "item.completed" and item.get("type") == "command_execution":
        return f"[command exit={item.get('exit_code')}]"
    return None


def is_review_protocol_command(command: str) -> bool:
    """Return whether a command is an allowlisted verdict protocol operation."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False
    if (
        len(tokens) == 3
        and tokens[0] in {"bash", "/bin/bash", "/usr/bin/bash"}
        and (tokens[1] == "-lc")
    ):
        try:
            tokens = shlex.split(tokens[2])
        except ValueError:
            return False
    return (
        len(tokens) == 4
        and tokens[0] == "./bin/chrl"
        and (tokens[1] == "verdict")
        and (tokens[2] in {"template", "validate"})
        and bool(tokens[3])
    )


def is_delivery_protocol_command(command: str) -> bool:
    """Return whether an exact command advances deterministic delivery state."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False
    if (
        len(tokens) == 3
        and tokens[0] in {"bash", "/bin/bash", "/usr/bin/bash"}
        and (tokens[1] == "-lc")
    ):
        try:
            tokens = shlex.split(tokens[2])
        except ValueError:
            return False
    if len(tokens) == 2 and tokens[0] == "./bin/board-do" and tokens[1]:
        return True
    if len(tokens) == 4 and tokens[:2] == ["./bin/chrl", "event"]:
        return bool(tokens[2] and tokens[3])
    return (
        len(tokens) == 3 and tokens[:2] == ["./bin/chrl", "handoff"] and bool(tokens[2])
    )


def is_review_wrapper_command(command: str) -> bool:
    """Return whether a command synchronously owns one semantic review call."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False
    if (
        len(tokens) == 3
        and tokens[0] in {"bash", "/bin/bash", "/usr/bin/bash"}
        and (tokens[1] == "-lc")
    ):
        try:
            tokens = shlex.split(tokens[2])
        except ValueError:
            return False
    return (
        len(tokens) == 3
        and tokens[0] == "./bin/chrl"
        and (tokens[1] == "review")
        and bool(tokens[2])
    )


def is_ff_protocol_command(command: str) -> bool:
    """Return whether a command is an allowlisted FF planning operation."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False
    if (
        len(tokens) == 3
        and tokens[0] in {"bash", "/bin/bash", "/usr/bin/bash"}
        and (tokens[1] == "-lc")
    ):
        try:
            tokens = shlex.split(tokens[2])
        except ValueError:
            return False
    if tokens == ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]:
        return True
    return (
        len(tokens) == 5
        and tokens[0] == "./bin/chrl-ff"
        and (tokens[1] == "verdict")
        and (tokens[2] in {"template", "validate"})
        and (
            tokens[3]
            in {
                "proposal",
                "specs",
                "design",
                "tasks",
                "$CHRL_FF_STAGE",
                "${CHRL_FF_STAGE}",
            }
        )
        and bool(tokens[4])
    )


def _command_traits(command: str) -> dict[str, bool]:
    return {
        "pytest": is_pytest_command(command),
        "full_pytest": is_full_pytest_command(command),
        "deterministic_wrapper": is_deterministic_wrapper(command),
        "review_protocol": is_review_protocol_command(command),
        "review_wrapper": is_review_wrapper_command(command),
        "ff_protocol": is_ff_protocol_command(command),
        "delivery_protocol": is_delivery_protocol_command(command),
    }


def sanitize_stream_event(event: dict[str, Any]) -> dict[str, Any]:
    """Remove command text and command output before persisting telemetry."""
    sanitized = dict(event)
    item_value = event.get("item")
    if (
        not isinstance(item_value, dict)
        or item_value.get("type") != "command_execution"
    ):
        if event.get("type") == "unparsed" and "text" in sanitized:
            sanitized["text_length"] = len(str(sanitized.pop("text")))
        return sanitized
    item = dict(item_value)
    command = str(item.pop("command", "") or "")
    output = str(item.pop("aggregated_output", "") or "")
    item["command_fingerprint"] = (
        "sha256:" + hashlib.sha256(command.encode("utf-8")).hexdigest()
    )
    item["command_traits"] = _command_traits(command)
    item["aggregated_output_length"] = len(output)
    sanitized["item"] = item
    return sanitized


def codex_session_command(
    *,
    model: str,
    reasoning: str,
    last_message: Path,
    prompt: str,
    resume_thread_id: str | None = None,
) -> list[str]:
    from scripts.changerail.adapters.codex import session_command

    return session_command(
        REPO_ROOT,
        profile(),
        model=model,
        reasoning=reasoning,
        last_message=last_message,
        prompt=prompt,
        resume_thread_id=resume_thread_id,
    )


def model_route(current_profile: dict[str, Any], role: str) -> tuple[str, str]:
    """Resolve an explicit model and reasoning effort for one session role."""
    route = current_profile.get("models", {}).get(role)
    if not isinstance(route, dict):
        raise DeliveryError(f"missing model route for role: {role}")
    model = route.get("model")
    reasoning = route.get("reasoning_effort")
    if not isinstance(model, str) or not model:
        raise DeliveryError(f"invalid model route for role: {role}")
    if not isinstance(reasoning, str) or not reasoning:
        raise DeliveryError(f"invalid reasoning effort for role: {role}")
    if model == "gpt-6-astra" and reasoning in {"none", "minimal"}:
        raise DeliveryError("Astra requires low or higher reasoning effort")
    return (model, reasoning)


def terminate_process_group(process: subprocess.Popen[str]) -> None:
    """Ask the isolated Codex process group to terminate."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except OSError:
        pass


def kill_process_group(process: subprocess.Popen[str]) -> None:
    """Kill the isolated Codex process group after graceful shutdown expires."""
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except OSError:
        pass


def launch_codex(
    *,
    role: str,
    prompt: str,
    model: str,
    reasoning: str,
    run_dir: Path,
    timeout_minutes: float | None,
    session_env: dict[str, str] | None = None,
    expected_artifact: Path | None = None,
    resume_thread_id: str | None = None,
    require_first_file_change: bool | None = None,
    inherited_investigative_commands: int = 0,
    on_session_started: Callable[[Path], None] | None = None,
) -> int:
    if role not in {"implementation", "review"}:
        raise DeliveryError("only implementation and review sessions are executable")
    sessions = run_dir / "sessions"
    sessions.mkdir(parents=True, exist_ok=True)
    if role == "implementation":
        initial = sessions / role
        if not initial.exists():
            name = role
        else:
            name = f"{role}-{len(list(sessions.glob(f'{role}-*'))) + 2:02d}"
    else:
        existing = sorted(sessions.glob(f"{role}-*"))
        name = f"{role}-{len(existing) + 1:02d}"
    session_dir = sessions / name
    session_dir.mkdir(parents=True, exist_ok=False)

    def retain_session_json(name: str, payload: Mapping[str, Any]) -> None:
        write_json(session_dir / name, payload)

    def open_stream(name: str):
        return (session_dir / name).open("w", encoding="utf-8")

    session_dir / "stdout.jsonl"
    session_dir / "events.jsonl"
    session_dir / "stderr.log"
    last_message = session_dir / "last-message.md"
    command = codex_session_command(
        model=model,
        reasoning=reasoning,
        last_message=last_message,
        prompt=prompt,
        resume_thread_id=resume_thread_id,
    )
    started_at = utc_now()
    started = time.monotonic()
    recovery = bool((session_env or {}).get("CHRL_RECOVERY_RUN"))
    if require_first_file_change is None:
        require_first_file_change = not (role == "implementation" and recovery)
    parent_session = os.environ.get("CHRL_SESSION_NAME", "").strip() or None
    metadata: dict[str, Any] = {
        "schema": "changerail.delivery-session.v1",
        "session": name,
        "role": role,
        "model": model,
        "reasoning_effort": reasoning,
        "model_evidence": {
            "model": model,
            "reasoning_effort": reasoning,
            "source": "explicit_codex_cli_arguments",
        },
        "recovery": recovery,
        "inherited_investigative_commands": inherited_investigative_commands,
        "started_at": started_at,
        "command": command,
    }
    if resume_thread_id:
        metadata["resumed_thread_id"] = resume_thread_id
    if parent_session:
        metadata["parent_session"] = parent_session
    review_reason = (session_env or {}).get("CHRL_REVIEW_REASON")
    if role == "review" and review_reason:
        metadata["review_reason"] = review_reason
    retain_session_json("session.json", metadata)
    if on_session_started is not None:
        on_session_started(session_dir)
    codex_env = {
        "CHRL_RUN_DIR": str(run_dir),
        "CHRL_SESSION_ROLE": role,
        "CHRL_SESSION_NAME": name,
        **(session_env or {}),
    }
    try:
        process = subprocess.Popen(
            command,
            cwd=REPO_ROOT,
            env=execution_env(codex_env),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            start_new_session=True,
        )
    except OSError as exc:
        metadata.update(
            {
                "finished_at": utc_now(),
                "duration_seconds": round(time.monotonic() - started, 3),
                "exit_code": None,
                "timed_out": False,
                "interrupted": False,
                "budget_violation": None,
                "stop_reason": "launch_error",
                "completed": False,
            }
        )
        retain_session_json("session.json", metadata)
        raise DeliveryError(f"cannot launch {role} Codex session: {exc}") from exc
    lock = threading.Lock()
    budget_lock = threading.Lock()
    command_budget = _SessionCommandBudget(
        role,
        profile().get("budgets", {}),
        require_first_file_change=require_first_file_change,
        inherited_investigative_commands=inherited_investigative_commands,
    )
    budget_violation: dict[str, Any] | None = None
    verdict_only_notice: dict[str, Any] | None = None

    def pump_stdout() -> None:
        nonlocal budget_violation, verdict_only_notice
        assert process.stdout is not None
        with (
            open_stream("stdout.jsonl") as raw,
            open_stream("events.jsonl") as observed,
        ):
            for line in process.stdout:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    event = {"type": "unparsed", "text": line.rstrip("\n")}
                violation = command_budget.observe(event)
                safe_event = sanitize_stream_event(event)
                raw.write(json.dumps(safe_event, ensure_ascii=False) + "\n")
                raw.flush()
                envelope = {
                    "observed_at": utc_now(),
                    "observed_elapsed_seconds": round(time.monotonic() - started, 3),
                    "event": safe_event,
                }
                observed.write(json.dumps(envelope, ensure_ascii=False) + "\n")
                observed.flush()
                if (
                    role == "review"
                    and command_budget.verdict_only_started_at is not None
                    and (verdict_only_notice is None)
                ):
                    verdict_only_notice = {
                        "schema": "changerail.review-verdict-only.v1",
                        "observed_at": envelope["observed_at"],
                        "observed_investigative_commands": command_budget.verdict_only_started_at,
                        "target": command_budget.limit,
                        "verdict_only_at": command_budget.verdict_only_limit,
                        "hard_stop": command_budget.hard_stop_limit,
                    }
                    retain_session_json("verdict-only.json", verdict_only_notice)
                    with lock:
                        print(
                            "[review] verdict-only threshold reached; waiting for verdict protocol",
                            flush=True,
                        )
                if violation is not None:
                    violation = {**violation, "observed_at": envelope["observed_at"]}
                    with budget_lock:
                        if budget_violation is None:
                            budget_violation = violation
                            retain_session_json("budget-violation.json", violation)
                            kill_process_group(process)
                rendered = concise_event(safe_event)
                if rendered:
                    with lock:
                        print(rendered, flush=True)

    def pump_stderr() -> None:
        assert process.stderr is not None
        with open_stream("stderr.log") as handle:
            for line in process.stderr:
                handle.write(line)
                handle.flush()

    stream_errors: list[BaseException] = []

    def guarded_pump(pump: Callable[[], None]) -> None:
        try:
            pump()
        except BaseException as exc:
            stream_errors.append(exc)

    stdout_thread = threading.Thread(target=pump_stdout, daemon=True)
    stderr_thread = threading.Thread(target=pump_stderr, daemon=True)
    stdout_thread.start()
    stderr_thread.start()
    timed_out = False
    interrupted = False
    try:
        return_code = process.wait()
    except subprocess.TimeoutExpired:
        timed_out = True
        terminate_process_group(process)
        try:
            return_code = process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            kill_process_group(process)
            return_code = process.wait()
    except KeyboardInterrupt:
        interrupted = True
        terminate_process_group(process)
        try:
            return_code = process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            kill_process_group(process)
            return_code = process.wait()
    stdout_thread.join(timeout=5)
    stderr_thread.join(timeout=5)
    if budget_violation is not None:
        stop_reason = "command_safety_stop"
    elif timed_out:
        stop_reason = "timeout"
    elif interrupted:
        stop_reason = "operator_interrupt"
    elif return_code != 0:
        stop_reason = "nonzero_exit"
    elif expected_artifact is not None and (not expected_artifact.is_file()):
        stop_reason = (
            "incomplete_review_no_verdict"
            if role == "review"
            else "incomplete_session_no_artifact"
        )
    else:
        stop_reason = "completed"
    metadata.update(
        {
            "finished_at": utc_now(),
            "duration_seconds": round(time.monotonic() - started, 3),
            "exit_code": return_code,
            "timed_out": timed_out,
            "interrupted": interrupted,
            "budget_violation": budget_violation,
            "command_budget": command_budget.snapshot(),
            "verdict_only_notice": verdict_only_notice,
            "stop_reason": stop_reason,
            "completed": stop_reason == "completed",
        }
    )
    retain_session_json("session.json", metadata)
    if budget_violation is not None:
        raise DeliveryError(
            f"{role} shell command budget exceeded: {budget_violation['observed']} > {budget_violation['hard_stop_budget']} hard stop (target {budget_violation['budget']}) for {budget_violation['metric']}"
        )
    if interrupted:
        raise DeliveryError(f"{role} Codex session interrupted")
    return return_code


def capture_manifest(card_value: str) -> dict[str, Any]:
    card = resolve_deliverable_card(card_value)
    run_dir = current_run_dir()
    assert run_dir is not None
    identifier = card_id(card)
    path = manifest_path(identifier)
    existing = load_json(path)
    if existing.get("baseline_head") != git("rev-parse", "HEAD").stdout.strip():
        raise DeliveryError("delivery baseline HEAD changed during the run")
    paths = changed_paths()
    if repo_relative(card) not in paths:
        raise DeliveryError("active board card is not part of the delivery payload")
    existing.update(
        {
            "updated_at": utc_now(),
            "card": {"id": identifier, "path": repo_relative(card)},
            "paths": paths,
            "fingerprint": payload_fingerprint(paths),
            "path_fingerprints": path_fingerprints(paths),
            "path_states": {path: _path_state(path) for path in paths},
        }
    )
    inventory = _current_proof_inventory(card, run_dir)
    if inventory is not None:
        existing["observed_proof"] = {
            "schema": _OBSERVED_PROOF_CONTRACT,
            "inventory_digest": inventory["digest"],
            "selection": _run_observed_contract(run_dir)["selection"],
        }
    write_json(path, existing)
    write_json(run_dir / "manifest.json", existing)
    return existing


def handoff_path(run_dir: Path) -> Path:
    """Return the current fingerprint-bound implementation handoff path."""
    return run_dir / "implementation-handoff.json"


def implementation_handoff(card_value: str) -> int:
    """Freeze a completed implementation payload for runner-owned review."""
    card = resolve_deliverable_card(card_value)
    run_dir = current_run_dir()
    assert run_dir is not None
    if os.environ.get("CHRL_SESSION_ROLE") != "implementation":
        raise DeliveryError("implementation handoff requires implementation role")
    if native.is_native(card) and os.environ.get("CHRL_DELIVERY_STAGE") == "change":
        raise DeliveryError(
            "task-group sessions must finish their group, not hand off the card"
        )
    if preverify(str(card)) != 0:
        repaired = run_safe_handoff_repair(run_dir)
        repaired_preverification = repaired and preverify(str(card)) == 0
        if repaired_preverification:
            status = "deterministic_repair_applied"
            action = "refresh focused evidence invalidated by the import-only edit, then rerun chrl handoff in this session; do not report success yet"
        else:
            status = "failed"
            action = "repair the reported preverification failure in this session and rerun chrl handoff; do not report success"
        print(
            json.dumps(
                {
                    "schema": "changerail.implementation-handoff-status.v1",
                    "status": status,
                    "artifact_written": False,
                    "action": action,
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1
    inventory = _current_proof_inventory(card, run_dir)
    if inventory is not None:
        require_current_stage_proofs(card, run_dir, ["implementation"])
    manifest = capture_manifest(str(card))
    fingerprint = payload_fingerprint()
    if manifest.get("fingerprint") != fingerprint:
        raise DeliveryError("implementation handoff manifest is stale")
    payload = {
        "schema": "changerail.implementation-handoff.v1",
        "card": {"id": card_id(card), "path": repo_relative(card)},
        "fingerprint": fingerprint,
        "manifest": repo_relative(manifest_path(card_id(card))),
        "preverification": repo_relative(run_dir / "preverification.json"),
        "kind": "repair" if os.environ.get("CHRL_REPAIR_CONTEXT") else "implementation",
        "completed_at": utc_now(),
    }
    if inventory is not None:
        payload["observed_proof"] = {
            "inventory_digest": inventory["digest"],
            "stages": ["implementation"],
            "selection": _run_observed_contract(run_dir)["selection"],
        }
    current = handoff_path(run_dir)
    if current.is_file():
        retained = load_json(current)
        stable_keys = (
            "schema",
            "card",
            "fingerprint",
            "manifest",
            "preverification",
            "kind",
        )
        if all((retained.get(key) == payload.get(key) for key in stable_keys)):
            print(json.dumps({**retained, "reused": True}, ensure_ascii=False))
            return 0
    history = run_dir / "implementation-handoffs"
    history.mkdir(parents=True, exist_ok=True)
    destination = (
        history / f"handoff-{len(list(history.glob('handoff-*.json'))) + 1:02d}.json"
    )
    write_json(destination, payload)
    write_json(current, payload)
    print(json.dumps({**payload, "reused": False}, ensure_ascii=False))
    return 0


def require_current_implementation_handoff(card: Path, run_dir: Path) -> dict[str, Any]:
    """Validate that the implementation session froze the current payload."""
    path = handoff_path(run_dir)
    if not path.is_file():
        raise DeliveryError("implementation session exited without a handoff")
    payload = load_json(path)
    expected_card = {"id": card_id(card), "path": repo_relative(card)}
    if payload.get("schema") != "changerail.implementation-handoff.v1":
        raise DeliveryError("implementation handoff schema is invalid")
    if payload.get("card") != expected_card:
        raise DeliveryError("implementation handoff card identity is stale")
    fingerprint = payload_fingerprint()
    if payload.get("fingerprint") != fingerprint:
        raise DeliveryError("implementation handoff fingerprint is stale")
    manifest = load_json(manifest_path(card_id(card)))
    if (
        manifest.get("fingerprint") != fingerprint
        or manifest.get("paths") != changed_paths()
    ):
        raise DeliveryError("implementation handoff manifest is stale")
    require_current_successful_preverification(card, run_dir, stage="handoff")
    inventory = _current_proof_inventory(card, run_dir)
    if inventory is not None:
        if payload.get("observed_proof") != {
            "inventory_digest": inventory["digest"],
            "stages": ["implementation"],
            "selection": _run_observed_contract(run_dir)["selection"],
        }:
            raise DeliveryError(
                "implementation handoff observed-proof binding is stale"
            )
        require_current_stage_proofs(card, run_dir, ["implementation"])
    return payload


def _check_bytes(path: Path, limit: int = 262144) -> bytes:
    """Read bounded regular bytes without following any component below the repo."""
    relative = path.relative_to(REPO_ROOT)
    if not relative.parts or ".." in relative.parts:
        raise ValueError("unsafe check path")
    directory = os.open(REPO_ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
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
            if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
                raise ValueError("nonregular or oversized check artifact")
            data = stream.read(limit + 1)
            after = os.fstat(stream.fileno())
            if (
                len(data) > limit
                or len(data) != before.st_size
                or before.st_mtime_ns != after.st_mtime_ns
            ):
                raise ValueError("check artifact changed during read")
            return data
    finally:
        os.close(directory)


def _check_json(path: Path) -> dict[str, Any]:
    return _check_json_bytes(_check_bytes(path))


def _check_json_bytes(data: bytes) -> dict[str, Any]:
    """Decode one already-authenticated bounded JSON object exactly once."""

    def unique(pairs):
        value = dict(pairs)
        if len(value) != len(pairs):
            raise ValueError("duplicate check key")
        return value

    def finite(raw):
        value = float(raw)
        if not math.isfinite(value):
            raise ValueError("nonfinite check number")
        return value

    try:
        value = json.loads(
            data, object_pairs_hook=unique, parse_float=finite, parse_constant=finite
        )
    except RecursionError as exc:
        raise ValueError("check JSON exceeds decoder depth") from exc
    if not isinstance(value, dict):
        raise ValueError("check JSON must be an object")
    return value


def _check_owner(run_dir: Path) -> dict[str, str]:
    owner = _check_json(run_dir / "run.json")
    card = owner.get("card")
    if (
        owner.get("run_id") != run_dir.name
        or not isinstance(card, str)
        or (not card)
        or Path(card).is_absolute()
        or (".." in Path(card).parts)
    ):
        raise ValueError("missing check owning identity")
    path = REPO_ROOT / card
    if path.is_file():
        _check_bytes(path)
    else:
        _check_bytes(path)
    return {"run_id": owner["run_id"], "card": card}


def read_check_result(
    path: Path,
    run_dir: Path,
    lane: str,
    command: Mapping[str, Any] | None = None,
    *,
    record_data: bytes | None = None,
    expected_record: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bytes, bool]:
    """The sole schema/identity/log validator; failed proof is never a cache hit."""
    from jsonschema import Draft202012Validator, FormatChecker

    if not path.is_relative_to(run_dir):
        raise ValueError("foreign check record")
    if record_data is None:
        item = _check_json(path)
    else:
        if expected_record is None:
            raise ValueError("validated check bytes require their receipt reference")
        if set(expected_record) != {"path", "size", "sha256"}:
            raise ValueError("invalid expected receipt reference")
        if (
            expected_record["size"] != len(record_data)
            or expected_record["sha256"] != hashlib.sha256(record_data).hexdigest()
        ):
            raise ValueError("validated receipt bytes do not match their reference")
        try:
            item = _decode_closed_json(record_data, label="check result")
        except DeliveryError as exc:
            raise ValueError("invalid validated check JSON") from exc
    if item.get("schema") == "changerail.dependency-reuse.v1":
        if lane != "focused":
            raise ValueError("only focused checks allow dependency reuse")
        from scripts.changerail.evidence_dependencies import validate_reuse_receipt

        result = validate_reuse_receipt(
            REPO_ROOT,
            run_dir,
            path,
            item,
            profile=profile(),
            command=command,
            environment=execution_env(),
            read_source=lambda source: read_check_result(source, run_dir, "focused"),
            fingerprint=payload_fingerprint(),
        )
        if any(
            (
                result[0].get(key) != value
                for key, value in _check_owner(run_dir).items()
            )
        ):
            raise ValueError("foreign reused check owner")
        return result
    Draft202012Validator(
        load_json(CHECK_RESULT_SCHEMA_PATH), format_checker=FormatChecker()
    ).validate(item)
    owner = _check_owner(run_dir)
    if (
        not path.is_relative_to(run_dir)
        or item["attempt_id"] != path.stem
        or any((item[k] != v for k, v in owner.items()))
        or (item["lane"] != lane)
    ):
        raise ValueError("foreign check identity")
    identity = item["command_identity"]
    display = (
        shlex.join(identity["argv"])
        if identity["kind"] == "argv"
        else identity["shell_text"]
    )
    if item["command"] != display or (command is not None and identity != command):
        raise ValueError("foreign check command")
    if item.get("observed_at", item["started_at"]) < item["started_at"]:
        raise ValueError("check finish precedes start")
    data = b""
    if "log" in item:
        if Path(item["log"]).is_absolute() or ".." in Path(item["log"]).parts:
            raise ValueError("unsafe check log reference")
        log = REPO_ROOT / item["log"]
        if log != path.with_suffix(".log"):
            raise ValueError("foreign check log")
        data = _check_bytes(log, 32 * 1024 * 1024)
        if len(data) != item.get("log_size") or hashlib.sha256(
            data
        ).hexdigest() != item.get("log_sha256"):
            raise ValueError("check log integrity failed")
    fingerprint = payload_fingerprint()
    current = (
        item.get("verdict") == "verified"
        and item["before"] == item.get("fingerprint") == fingerprint
    )
    return (item, data, current)


def start_check_result(
    run_dir: Path,
    lane: str,
    label: str,
    command: Mapping[str, Any],
    *,
    destination: Path | None = None,
) -> tuple[Path, dict[str, Any]]:
    owner = _check_owner(run_dir)
    attempt = uuid.uuid4().hex
    directory = destination if destination is not None else run_dir / "focused-evidence"
    if not directory.is_relative_to(run_dir) or ".." in directory.parts:
        raise ValueError("foreign check directory")
    directory.mkdir(exist_ok=True)
    if directory.is_symlink():
        raise ValueError("unsafe check directory")
    path = directory / f"{attempt}.json"
    item = {
        "schema": "changerail.check-result.v1",
        "state": "running",
        "attempt_id": attempt,
        **owner,
        "lane": lane,
        "command_identity": dict(command),
        "label": label,
        "command": shlex.join(command["argv"])
        if command["kind"] == "argv"
        else command["shell_text"],
        "started_at": utc_now(),
        "before": payload_fingerprint(),
    }
    if lane == "focused":
        from scripts.changerail.evidence_dependencies import (
            selected_dependencies,
            capture_dependency_snapshot,
        )

        dependencies = selected_dependencies(profile(), command)
        if dependencies is not None:
            item["dependency_snapshot"] = capture_dependency_snapshot(
                REPO_ROOT,
                dependencies,
                command=command["argv"],
                environment=execution_env(),
            )
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(item) + "\n")
    _start_verification_attempt_intent(run_dir, path, item)
    return (path, item)


def finish_check_result(path: Path, item: dict[str, Any], output: bytes) -> None:
    """Retain the entire log before atomic terminal publication; propagate faults."""
    log = path.with_suffix(".log")
    with log.open("xb") as stream:
        stream.write(output)
    item.update(
        log=repo_relative(log),
        log_size=len(output),
        log_sha256=hashlib.sha256(output).hexdigest(),
    )
    write_json(path, item)
    _finish_verification_attempt_intent(path, item)


def run_evidence(label: str, command: Sequence[str]) -> int:
    if not command:
        raise DeliveryError("focused evidence command is empty")
    run_dir = current_run_dir()
    assert run_dir is not None
    safe_label = re.sub("[^a-z0-9._-]+", "-", label.lower()).strip("-")
    if not safe_label:
        raise DeliveryError("focused evidence label is empty after normalization")
    run_dir = Path(os.environ["CHRL_RUN_DIR"])
    identity = {"kind": "argv", "argv": list(command)}
    try:
        card = REPO_ROOT / _check_owner(run_dir)["card"]
    except (ValueError, OSError) as exc:
        raise DeliveryError(f"cannot start focused proof: {exc}") from exc
    with verification_attempt_lock(run_dir, card, "focused") as ownership:
        return _run_evidence_locked(
            run_dir, safe_label, identity, card=card, ownership=ownership
        )


def _run_evidence_locked(
    run_dir: Path,
    safe_label: str,
    identity: dict[str, Any],
    *,
    card: Path | None = None,
    ownership: _VerificationLockOwnership | None = None,
) -> int:
    """Execute focused evidence while its caller owns the run-wide check lock."""
    from jsonschema.exceptions import ValidationError

    if ownership is None:
        try:
            card = REPO_ROOT / _check_owner(run_dir)["card"]
        except (ValueError, OSError) as exc:
            raise DeliveryError(f"cannot start focused proof: {exc}") from exc
        with verification_attempt_lock(run_dir, card, "focused") as acquired:
            return _run_evidence_locked(
                run_dir, safe_label, identity, card=card, ownership=acquired
            )
    if card is None:
        raise DeliveryError("focused proof requires current lock ownership")
    _require_verification_attempt_ownership(ownership, run_dir, card)
    for existing in focused_evidence_summaries(run_dir):
        if (
            existing.get("proof_status") == "current"
            and existing.get("command_identity") == identity
        ):
            raise DeliveryError(
                f"unchanged successful focused evidence must not be repeated: {existing['record']}"
            )
    from scripts.changerail.evidence_dependencies import (
        selected_dependencies,
        create_reuse_receipt,
    )

    if selected_dependencies(profile(), identity) is not None:
        for source in sorted((run_dir / "focused-evidence").glob("*.json")):
            receipt_id = uuid.uuid4().hex
            destination = source.parent / f"{receipt_id}.json"
            try:
                receipt = create_reuse_receipt(
                    REPO_ROOT,
                    run_dir,
                    source,
                    profile=profile(),
                    command=identity,
                    environment=execution_env(),
                    read_source=lambda path: read_check_result(
                        path, run_dir, "focused"
                    ),
                    fingerprint=payload_fingerprint(),
                    receipt_id=receipt_id,
                    observed_at=utc_now(),
                )
            except (ValueError, OSError, DeliveryError, ValidationError):
                continue
            with destination.open("x", encoding="utf-8") as stream:
                stream.write(json.dumps(receipt) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            read_check_result(destination, run_dir, "focused", identity)
            print(
                json.dumps(
                    {
                        "reused": repo_relative(destination),
                        "source": repo_relative(source),
                    }
                )
            )
            return 0
    try:
        path, item = start_check_result(run_dir, "focused", safe_label, identity)
    except (ValueError, OSError) as exc:
        raise DeliveryError(f"cannot start focused proof: {exc}") from exc
    started = time.monotonic()
    output, code, outcome = (b"", None, "unknown")
    try:
        result = subprocess.run(
            identity["argv"],
            cwd=REPO_ROOT,
            env=execution_env(),
            capture_output=True,
            check=False,
        )
        output, code, outcome = (
            result.stdout + result.stderr,
            result.returncode,
            "exit",
        )
    except OSError as exc:
        output, outcome = (str(exc).encode(), "spawn_failure")
    except KeyboardInterrupt:
        outcome = "interrupted"
    after = payload_fingerprint()
    verified = outcome == "exit" and code == 0 and (item["before"] == after)
    if "dependency_snapshot" in item:
        from scripts.changerail.evidence_dependencies import (
            validate_dependency_snapshot,
        )

        try:
            validate_dependency_snapshot(
                REPO_ROOT,
                item["dependency_snapshot"],
                command=identity["argv"],
                environment=execution_env(),
            )
        except (ValueError, OSError):
            verified = False
    item.update(
        state="terminal",
        observed_at=utc_now(),
        duration_seconds=round(time.monotonic() - started, 3),
        fingerprint=after,
        exit_code=code,
        outcome=outcome,
        verdict="verified" if verified else "unconfirmed",
        reason="stable" if verified else "process_failure_or_payload_drift",
    )
    try:
        finish_check_result(path, item, output)
        _, _, verified = read_check_result(path, run_dir, "focused", identity)
    except (
        OSError,
        ValueError,
        DeliveryError,
        ValidationError,
        KeyboardInterrupt,
    ) as exc:
        verified = False
        item.update(verdict="unconfirmed", reason="retention_failure")
        try:
            write_json(path, item)
        except (OSError, KeyboardInterrupt):
            pass
        print(
            f"focused retention failed; observed exit={code!r}: {exc}", file=sys.stderr
        )
    print(output.decode("utf-8", errors="replace"), end="")
    return 0 if verified else code if code not in (0, None) else 1


def focused_evidence_summaries(run_dir: Path) -> list[dict[str, Any]]:
    from jsonschema.exceptions import ValidationError

    summaries: list[dict[str, Any]] = []
    for path in sorted((run_dir / "focused-evidence").glob("*.json")):
        item, status = ({}, "unconfirmed")
        try:
            item = _check_json(path)
            if item.get("schema") in {
                "changerail.check-result.v1",
                "changerail.dependency-reuse.v1",
            }:
                item, _, current = read_check_result(path, run_dir, "focused")
                status = "current" if current else "unconfirmed"
            elif item.get("schema") in (None, "changerail.focused-evidence.v1"):
                status = "historical/unconfirmed"
            else:
                item = {}
        except (ValueError, OSError, DeliveryError):
            pass
        except ValidationError:
            item = {}
        summaries.append(
            {
                "record": path.relative_to(REPO_ROOT).as_posix(),
                "proof_status": status,
                "command_identity": item.get("command_identity"),
                "observed_at": item.get("observed_at"),
                "label": item.get("label"),
                "command": item.get("command")
                if isinstance(item.get("command"), str)
                else None,
                "exit_code": item.get("exit_code")
                if type(item.get("exit_code")) is int
                else None,
                "duration_seconds": item.get("duration_seconds")
                if type(item.get("duration_seconds")) in (int, float)
                else None,
                "fingerprint": item.get("fingerprint"),
                "log": item.get("log"),
            }
        )
    return summaries


def _empty_review_budget_usage() -> dict[str, int]:
    return {key: 0 for key in REVIEW_BUDGET_KEYS}


def _review_budget_key(review_reason: str) -> str:
    return "semantic_cycles"


def review_budget_usage(run_dir: Path) -> dict[str, int]:
    """Count inherited and local completed reviews by their budget lane."""
    usage = _empty_review_budget_usage()
    metadata_path = run_dir / "run.json"
    metadata = _check_json(metadata_path) if metadata_path.exists() else {}
    if metadata.get("recovery_of"):
        ancestors = recovery_ancestors(run_dir)
        inherited = sum(
            len(_completed_review_verdicts(path / "reviews")) for path in ancestors
        )
        context = _check_json(run_dir / "recovery-context.json")
        if context.get("inherited_review_budget") != {"semantic_cycles": inherited}:
            raise DeliveryError(
                "inherited review allowance differs from retained predecessor reviews"
            )
    recovery_path = run_dir / "recovery-context.json"
    if recovery_path.exists():
        inherited = _check_json(recovery_path).get("inherited_review_budget", {})
        if not isinstance(inherited, dict):
            raise DeliveryError("inherited review budget must be an object")
        for key in REVIEW_BUDGET_KEYS:
            value = inherited.get(key, 0)
            if not isinstance(value, int) or value < 0:
                raise DeliveryError(f"inherited review budget {key} is invalid")
            usage[key] = value
    history = run_dir / "reviews"
    for verdict_file in _completed_review_verdicts(history):
        context_file = verdict_file.with_name(f"{verdict_file.stem}-context.json")
        review_reason = "semantic"
        if context_file.is_file():
            raw_reason = load_json(context_file).get("review_reason")
            if isinstance(raw_reason, str):
                review_reason = raw_reason
        usage[_review_budget_key(review_reason)] += 1
    return usage


def failed_final_floors(run_dir: Path) -> list[dict[str, Any]]:
    """Index retained failed final floors without changing their receipts."""
    fingerprint = payload_fingerprint()
    failures = []
    for origin in (run_dir, *recovery_ancestors(run_dir)):
        path = origin / "verification.json"
        if not path.exists():
            continue
        retained = _check_json(path)
        if retained.get("ok") is False:
            failures.append(
                {
                    "run_id": origin.name,
                    "receipt": repo_relative(path),
                    "fingerprint": retained.get("fingerprint"),
                    "matches_current_payload": retained.get("fingerprint")
                    == fingerprint,
                    "commands": retained.get("commands", []),
                }
            )
    return failures


def require_repaired_final_payload(run_dir: Path) -> None:
    if any(item["matches_current_payload"] for item in failed_final_floors(run_dir)):
        raise DeliveryError(
            "unchanged failed final floor requires repair before another review or verification"
        )


def build_recovery_context(
    *, run_dir: Path, previous_run: Path, objective: str
) -> Path:
    current_fingerprint = payload_fingerprint()
    plan = declared_change_plan(run_dir) or []
    previous_plan = declared_change_plan(previous_run)
    if previous_plan is not None and previous_plan != plan:
        raise DeliveryError(
            f"recovery Change plan differs from previous run: {plan} != {previous_plan}"
        )
    inherited_change_events = combined_change_events(previous_run) if plan else []
    observed_change_events = validate_change_event_prefix(plan, inherited_change_events)
    expected_change_events = _expected_change_event_pairs(plan)
    next_change_event = (
        {
            "phase": expected_change_events[len(observed_change_events)][0],
            "stage": expected_change_events[len(observed_change_events)][1],
        }
        if len(observed_change_events) < len(expected_change_events)
        else None
    )
    completed_reviews: list[tuple[int, Path, Path, dict[str, Any]]] = []
    reviews = previous_run / "reviews"
    for verdict_file in sorted(reviews.glob("cycle-[0-9][0-9].json")):
        match = re.fullmatch("cycle-(\\d{2})\\.json", verdict_file.name)
        if match is None or int(match.group(1)) < 1:
            continue
        cycle = int(match.group(1))
        review_manifest = reviews / f"cycle-{cycle:02d}-manifest.json"
        if not review_manifest.is_file():
            continue
        verdict = load_json(verdict_file)
        retained_manifest = load_json(review_manifest)
        if verdict.get("workspace") != retained_manifest.get("fingerprint"):
            continue
        completed_reviews.append((cycle, verdict_file, review_manifest, verdict))
    previous_recovery_path = previous_run / "recovery-context.json"
    previous_recovery = (
        _check_json(previous_recovery_path) if previous_recovery_path.exists() else {}
    )
    previous_review: dict[str, Any] | None = None
    if completed_reviews:
        cycle, verdict_file, review_manifest, verdict = completed_reviews[-1]
        review_context = reviews / f"cycle-{cycle:02d}-context.json"
        review_reason = "semantic"
        if review_context.is_file():
            raw_reason = load_json(review_context).get("review_reason")
            if isinstance(raw_reason, str):
                review_reason = raw_reason
        previous_review = {
            "cycle": cycle,
            "run_id": previous_run.name,
            "result": verdict.get("result"),
            "review_reason": review_reason,
            "verdict": repo_relative(verdict_file),
            "manifest": repo_relative(review_manifest),
            "matches_current_payload": verdict.get("workspace") == current_fingerprint,
        }
    elif isinstance(previous_recovery.get("previous_completed_review"), dict):
        inherited_review = dict(previous_recovery["previous_completed_review"])
        verdict_value = inherited_review.get("verdict")
        manifest_value = inherited_review.get("manifest")
        if isinstance(verdict_value, str) and isinstance(manifest_value, str):
            verdict_file = REPO_ROOT / verdict_value
            review_manifest = REPO_ROOT / manifest_value
            if verdict_file.is_file() and review_manifest.is_file():
                verdict = load_json(verdict_file)
                retained_manifest = load_json(review_manifest)
                if verdict.get("workspace") == retained_manifest.get("fingerprint"):
                    inherited_review["matches_current_payload"] = (
                        verdict.get("workspace") == current_fingerprint
                    )
                    previous_review = inherited_review
    retained_evidence = focused_evidence_summaries(previous_run)
    for item in retained_evidence:
        item["proof_status"] = "historical/unconfirmed"
        item["matches_current_payload"] = item.get("fingerprint") == current_fingerprint
    source_thread_id = latest_implementation_thread(previous_run)
    inherited_review_budget = review_budget_usage(previous_run)
    profile()
    resume_strategy = "resume_retained_thread"
    context = {
        "schema": "changerail.recovery-context.v1",
        "run_id": run_dir.name,
        "recovery_of": previous_run.name,
        "objective": objective,
        "current_fingerprint": current_fingerprint,
        "payload_paths": changed_paths(),
        "change_checkpoints": change_checkpoint_statuses(plan, inherited_change_events),
        "inherited_change_events": inherited_change_events,
        "next_change_event": next_change_event,
        "source_thread_id": source_thread_id,
        "resumed_thread_id": source_thread_id,
        "resume_strategy": resume_strategy,
        "previous_completed_review": previous_review,
        "failed_final_floors": failed_final_floors(previous_run),
        "inherited_review_budget": inherited_review_budget,
        "retained_focused_evidence": retained_evidence,
        "instruction": "Use this summary as the sole index of the previous run. A null previous_completed_review means no completed verdict exists. Only evidence with matches_current_payload=true may be carried forward. Do not repeat complete Change checkpoints; continue from next_change_event. Inspect failed_final_floors command results and retained logs, repair the failed payload and retain current focused/pre-review evidence before using the remaining shared review allowance. An unchanged failed payload cannot spend a new review or repeat the final floor.",
    }
    # Context readers also support historical owner-less unit inputs. Ordinary
    # native execution still requires its pinned owner in _run_observed_contract.
    metadata_path = run_dir / "run.json"
    restoration = (
        _check_json(metadata_path).get("plan_restoration")
        if metadata_path.exists()
        else None
    )
    if restoration:
        context["plan_restoration"] = restoration
        context["instruction"] += (
            " The accepted Next bytes were restored through an explicit transition. "
            "All predecessor evidence is historical; re-execute required checks and "
            "record current observed proof before handoff. Preserve completed task "
            "groups, finalize/sync normally, and never edit frozen Next."
        )
        for item in retained_evidence:
            item["matches_current_payload"] = False
    contract = _run_observed_contract(run_dir)
    if contract is not None:
        key = (
            "observed_proof_selection"
            if contract["schema"] == _OBSERVED_PROOF_CONTRACT
            else "legacy_observed_proof_continuation"
        )
        context[key] = contract["selection"]
    path = run_dir / "recovery-context.json"
    write_json(path, context)
    return path


def _write_review_payload_diff(
    *, manifest: dict[str, Any], selected_paths: Sequence[str], destination: Path
) -> dict[str, Any] | None:
    tracked: list[str] = []
    untracked: list[str] = []
    for relative in selected_paths:
        probe = git("ls-files", "--error-unmatch", "--", relative, check=False)
        (tracked if probe.returncode == 0 else untracked).append(relative)
    chunks: list[str] = []
    if tracked:
        result = git(
            "diff",
            "--no-ext-diff",
            "--no-color",
            "--unified=16",
            str(manifest["baseline_head"]),
            "--",
            *tracked,
            check=False,
        )
        if result.returncode:
            raise DeliveryError(result.stderr.strip() or "cannot build review diff")
        chunks.append(result.stdout)
    for relative in untracked:
        absolute = REPO_ROOT / relative
        if not absolute.is_file():
            continue
        result = subprocess.run(
            [
                "git",
                "diff",
                "--no-index",
                "--no-ext-diff",
                "--no-color",
                "--unified=16",
                "--",
                "/dev/null",
                str(absolute),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode not in (0, 1):
            raise DeliveryError(result.stderr.strip() or "cannot build untracked diff")
        chunks.append(result.stdout)
    destination.write_text("\n".join(chunks), encoding="utf-8")


def _write_review_payload_diffs(
    *,
    manifest: dict[str, Any],
    selected_paths: Sequence[str],
    history: Path,
    cycle: int,
) -> list[dict[str, Any]]:
    """Write one bounded diff artifact per selected payload path."""
    artifacts: list[dict[str, Any]] = []
    for index, relative in enumerate(selected_paths, start=1):
        destination = history / f"cycle-{cycle:02d}-payload-{index:02d}.diff"
        _write_review_payload_diff(
            manifest=manifest, selected_paths=[relative], destination=destination
        )
        artifact = {"path": relative, "diff": repo_relative(destination)}
        artifact["size_bytes"] = destination.stat().st_size
        artifacts.append(artifact)
    return artifacts


def _cross_run_previous_cycle(
    *, run_dir: Path, manifest: dict[str, Any]
) -> tuple[dict[str, Any] | None, list[str] | None]:
    """Return the retained recovery verdict and its current changed-path delta."""
    context_path = run_dir / "recovery-context.json"
    if not context_path.exists():
        return (None, None)
    recovery = _check_json(context_path)
    previous = recovery.get("previous_completed_review")
    if not isinstance(previous, dict):
        return (None, None)
    verdict_value = previous.get("verdict")
    manifest_value = previous.get("manifest")
    if not isinstance(verdict_value, str) or not isinstance(manifest_value, str):
        raise DeliveryError("recovery review continuity paths are invalid")
    verdict_path = REPO_ROOT / verdict_value
    manifest_path_value = REPO_ROOT / manifest_value
    verdict = load_json(verdict_path)
    previous_manifest = load_json(manifest_path_value)
    if verdict.get("workspace") != previous_manifest.get("fingerprint"):
        raise DeliveryError("recovery review verdict is not bound to its manifest")
    previous_hashes = previous_manifest.get("path_fingerprints", {})
    current_hashes = manifest.get("path_fingerprints", {})
    if not isinstance(previous_hashes, dict) or not isinstance(current_hashes, dict):
        raise DeliveryError("recovery review path fingerprints are invalid")
    selected_paths = sorted(
        (
            path
            for path in set(previous_hashes) | set(current_hashes)
            if previous_hashes.get(path) != current_hashes.get(path)
        )
    )
    return (
        {
            "cycle": previous.get("cycle"),
            "run_id": previous.get("run_id") or recovery.get("recovery_of"),
            "result": verdict.get("result"),
            "verdict": verdict_value,
            "manifest": manifest_value,
            "changed_paths": selected_paths,
            "cross_run": True,
        },
        selected_paths,
    )


def build_review_context(
    *,
    card: Path,
    run_dir: Path,
    cycle: int,
    manifest: dict[str, Any],
    review_reason: str = "semantic",
) -> Path:
    run = _check_json(run_dir / "run.json") if (run_dir / "run.json").exists() else {}
    budgets = profile()["budgets"]
    review_target = int(budgets.get("review_commands", 12))
    review_hard_stop = int(
        budgets.get("review_hard_stop_commands", max(review_target, 20))
    )
    review_verdict_only = int(
        budgets.get(
            "review_verdict_only_commands",
            min(review_hard_stop, max(review_target, 20)),
        )
    )
    inventory = _current_proof_inventory(card, run_dir)
    bootstrap_acceptance: list[str] = []
    if "bootstrap_plan" in run:
        raise DeliveryError(
            "unadmitted bootstrap plan is historical and cannot execute"
        )
    history = run_dir / "reviews"
    previous_cycle: dict[str, Any] | None = None
    selected_paths = list(manifest["paths"])
    if cycle > 1:
        previous_verdict_path = history / f"cycle-{cycle - 1:02d}.json"
        previous_manifest_path = history / f"cycle-{cycle - 1:02d}-manifest.json"
        if not previous_verdict_path.is_file() or not previous_manifest_path.is_file():
            raise DeliveryError("previous review cycle context is incomplete")
        previous_verdict = load_json(previous_verdict_path)
        previous_manifest = load_json(previous_manifest_path)
        if previous_verdict.get("workspace") != previous_manifest.get("fingerprint"):
            raise DeliveryError("previous review verdict is not bound to its manifest")
        previous_hashes = previous_manifest.get("path_fingerprints", {})
        current_hashes = manifest.get("path_fingerprints", {})
        selected_paths = sorted(
            (
                path
                for path in set(previous_hashes) | set(current_hashes)
                if previous_hashes.get(path) != current_hashes.get(path)
            )
        )
        previous_cycle = {
            "cycle": cycle - 1,
            "result": previous_verdict.get("result"),
            "verdict": repo_relative(previous_verdict_path),
            "manifest": repo_relative(previous_manifest_path),
            "changed_paths": selected_paths,
        }
    else:
        previous_cycle, recovery_paths = _cross_run_previous_cycle(
            run_dir=run_dir, manifest=manifest
        )
        if recovery_paths is not None:
            selected_paths = recovery_paths
    payload_diffs = _write_review_payload_diffs(
        manifest=manifest, selected_paths=selected_paths, history=history, cycle=cycle
    )
    carried_evidence: list[dict[str, Any]] = []
    recovery_context_path = run_dir / "recovery-context.json"
    if recovery_context_path.exists():
        recovery_context = _check_json(recovery_context_path)
        for item in recovery_context.get("retained_focused_evidence", []):
            if not isinstance(item, dict):
                continue
            current_item = {
                **item,
                "proof_status": "historical/unconfirmed",
                "matches_current_payload": item.get("fingerprint")
                == manifest.get("fingerprint"),
            }
            if current_item["matches_current_payload"]:
                carried_evidence.append(current_item)
    context = {
        "schema": "changerail.review-context.v1",
        "cycle": cycle,
        "review_reason": review_reason,
        "card": repo_relative(card),
        "manifest": repo_relative(history / f"cycle-{cycle:02d}-manifest.json"),
        "verdict_schema": repo_relative(
            VERDICT_V2_SCHEMA_PATH if inventory is not None else VERDICT_SCHEMA_PATH
        ),
        "payload_diffs": payload_diffs,
        "diff_context_lines": 16,
        "selected_paths": selected_paths,
        "previous_cycle": previous_cycle,
        "focused_evidence": focused_evidence_summaries(run_dir),
        "carried_focused_evidence": carried_evidence,
        "bootstrap_acceptance": bootstrap_acceptance,
        "shell_command_budget": review_target,
        "shell_command_verdict_only": review_verdict_only,
        "shell_command_hard_stop": review_hard_stop,
        "budget_limits_enforced": budget_limits_enforced(),
    }
    if inventory is not None:
        context["proof_inventory"] = inventory
        context["observed_proof_selection"] = _run_observed_contract(run_dir)[
            "selection"
        ]
        context["reviewer_obligations"] = (
            "Assess complete scenarios, before/action/after assertions, selected tests, risk N/A and mocked seams; references do not decide semantic adequacy."
        )
    path = history / f"cycle-{cycle:02d}-context.json"
    _write_review_json(run_dir, path, context)
    return path


def verdict_path(identifier: str) -> Path:
    run_dir = current_run_dir(required=False)
    if run_dir is not None:
        run_dir = Path(os.environ["CHRL_RUN_DIR"])
    if run_dir is not None and (run_dir / "run.json").exists():
        try:
            _check_json(run_dir / "run.json")
        except (ValueError, OSError) as exc:
            raise DeliveryError(f"unsafe verdict owning metadata: {exc}") from exc
    return RUNTIME_ROOT / "reviews" / f"{identifier}.json"


def _v2_decision_groups(
    inventory: Mapping[str, Any],
) -> list[tuple[str, list[dict[str, Any]]]]:
    """Group all clauses of one complete Requirement/Scenario together."""
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in inventory["conditions"]:
        groups.setdefault(row["scenario"], []).append(row)
    return [(scenario, rows) for scenario, rows in groups.items()]


def _v2_verdict_template(card: Path, inventory: Mapping[str, Any]) -> dict[str, Any]:
    current_profile = profile()
    review_model, review_reasoning = model_route(current_profile, "review")
    decisions = []
    for scenario, rows in _v2_decision_groups(inventory):
        conditions = [row["identity"] for row in rows]
        decisions.append(
            {
                "scenario": scenario,
                "conditions": conditions,
                "disposition": "pending_final"
                if all((row["stage"] == "final" for row in rows))
                else "pass",
                "observation_ids": [],
                "condition_refs": [
                    {
                        "condition": row["identity"],
                        "stage": row["stage"],
                        "disposition": "pending_final"
                        if row["stage"] == "final"
                        else "pass",
                        "observation_ids": [],
                    }
                    for row in rows
                ],
                "assessment": "Reviewer must assess real assertions, relevance, risks, and mocked seams.",
            }
        )
    return {
        "schema": _REVIEW_VERDICT_V2,
        "card": {"id": card_id(card), "path": repo_relative(card)},
        "workspace": payload_fingerprint(),
        "inventory_digest": inventory["digest"],
        "reviewer": {
            "model": review_model,
            "reasoning_effort": review_reasoning,
            "fresh_context": True,
            "did_not_implement": True,
        },
        "result": "go",
        "decisions": decisions,
        "findings": [],
        "reviewed_at": utc_now(),
    }


def _validate_v2_verdict(
    card: Path, run_dir: Path, payload: dict[str, Any]
) -> dict[str, Any]:
    import jsonschema

    inventory = _current_proof_inventory(card, run_dir)
    assert inventory is not None
    try:
        jsonschema.validate(
            payload,
            load_json(VERDICT_V2_SCHEMA_PATH),
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.ValidationError as exc:
        raise DeliveryError(
            f"review v2 verdict schema validation failed: {exc.message}"
        ) from exc
    expected_payload = payload_fingerprint()
    if payload["workspace"] != expected_payload or payload["card"] != {
        "id": card_id(card),
        "path": repo_relative(card),
    }:
        raise DeliveryError("review v2 verdict is stale")
    if payload["inventory_digest"] != inventory["digest"]:
        raise DeliveryError("review v2 verdict inventory is stale")
    expected = {
        (scenario, frozenset((row["identity"] for row in rows)))
        for scenario, rows in _v2_decision_groups(inventory)
    }
    observed: set[tuple[str, frozenset[str]]] = set()
    duplicates: list[str] = []
    for decision in payload["decisions"]:
        identity = (decision["scenario"], frozenset(decision["conditions"]))
        if identity in observed:
            duplicates.append(decision["scenario"])
        observed.add(identity)
    missing = sorted((repr(item) for item in expected - observed))
    foreign = sorted((repr(item) for item in observed - expected))
    if missing or duplicates or foreign:
        raise DeliveryError(
            f"review v2 decision coverage mismatch: missing={missing}, duplicates={duplicates}, foreign={foreign}"
        )
    stage_by_condition = {
        row["identity"]: row["stage"] for row in inventory["conditions"]
    }
    try:
        current_observations = _validated_index_records(
            _check_json(_proof_index_path(run_dir)),
            card=card,
            run_dir=run_dir,
            inventory=inventory,
        )
    except FileNotFoundError:
        current_observations = []
    except (OSError, ValueError) as exc:
        raise DeliveryError("observed proof index cannot be safely read") from exc
    valid_ids = {
        proof["observation_id"]: proof["condition"] for proof in current_observations
    }
    assessment_placeholder = (
        "Reviewer must assess real assertions, relevance, risks, and mocked seams."
    )
    all_ref_ids: list[str] = []
    for decision in payload["decisions"]:
        conditions = decision["conditions"]
        refs = decision["condition_refs"]
        assessment = decision["assessment"].strip()
        if (
            not assessment
            or assessment.casefold() == "unassessed"
            or assessment == assessment_placeholder
        ):
            raise DeliveryError(
                "review v2 decision assessment is still the template placeholder"
            )
        if len(conditions) != len(set(conditions)):
            raise DeliveryError("review v2 decision conditions are duplicate")
        if (
            {item["condition"] for item in refs} != set(conditions)
            or len({item["condition"] for item in refs}) != len(refs)
            or any(
                (
                    item["stage"] != stage_by_condition.get(item["condition"])
                    for item in refs
                )
            )
        ):
            raise DeliveryError(
                "review v2 decision condition references are incomplete"
            )
        ref_ids: list[str] = []
        for item in refs:
            ids = item["observation_ids"]
            if len(ids) != len(set(ids)):
                raise DeliveryError("review v2 condition references are duplicate")
            if item["stage"] == "final":
                if item["disposition"] != "pending_final" or ids:
                    raise DeliveryError("final condition must remain pending_final")
                continue
            if item["disposition"] == "pending_final":
                raise DeliveryError("non-final condition cannot be pending_final")
            if set(ids) - set(valid_ids) or (
                ids and {valid_ids[value] for value in ids} != {item["condition"]}
            ):
                raise DeliveryError(
                    "review v2 condition references are foreign or stale"
                )
            if item["disposition"] == "pass" and (not ids):
                raise DeliveryError(
                    "passing v2 condition lacks its current observations"
                )
            ref_ids.extend(ids)
        decision_ids = decision["observation_ids"]
        if (
            len(decision_ids) != len(set(decision_ids))
            or len(ref_ids) != len(set(ref_ids))
            or set(decision_ids) != set(ref_ids)
        ):
            raise DeliveryError(
                "review v2 decision references are swapped or duplicate"
            )
        all_ref_ids.extend(ref_ids)
    if len(all_ref_ids) != len(set(all_ref_ids)):
        raise DeliveryError(
            "review v2 condition references are duplicated across decisions"
        )
    blockers = any(
        (finding["severity"] == "blocker" for finding in payload["findings"])
    )
    failed = any((item["disposition"] == "fail" for item in payload["decisions"]))
    if payload["result"] == "go" and (blockers or failed):
        raise DeliveryError("GO v2 verdict contains a blocker or failed decision")
    if payload["result"] == "no-go" and (not (blockers or failed)):
        raise DeliveryError("NO-GO v2 verdict requires a blocker or failed decision")
    if payload["result"] == "go":
        require_current_stage_proofs(card, run_dir, ["implementation", "review"])
        for decision in payload["decisions"]:
            refs = decision["condition_refs"]
            for item in refs:
                if item["stage"] == "final":
                    continue
                if item["disposition"] != "pass":
                    raise DeliveryError("GO v2 condition does not pass")
    return payload


def verdict_template(card_value: str) -> dict[str, Any]:
    card = resolve_deliverable_card(card_value)
    run_dir = current_run_dir(required=False)
    inventory = _current_proof_inventory(card, run_dir) if run_dir is not None else None
    if inventory is not None:
        template = _v2_verdict_template(card, inventory)
        return {
            "verdict_path": repo_relative(verdict_path(card_id(card))),
            "template": template,
        }
    current_profile = profile()
    fingerprint = payload_fingerprint()
    review_model, review_reasoning = model_route(current_profile, "review")
    template = {
        "schema": "changerail.review-verdict.v1",
        "card": {"id": card_id(card), "path": repo_relative(card)},
        "workspace": fingerprint,
        "reviewer": {
            "model": review_model,
            "reasoning_effort": review_reasoning,
            "fresh_context": True,
            "did_not_implement": True,
        },
        "result": "go",
        "acceptance": [
            {"criterion": criterion, "result": "pass", "evidence": []}
            for criterion in acceptance_criteria(card)
        ],
        "findings": [],
        "reviewed_at": utc_now(),
    }
    return {
        "verdict_path": repo_relative(verdict_path(card_id(card))),
        "template": template,
    }


def validate_verdict(card_value: str) -> dict[str, Any]:
    card = resolve_deliverable_card(card_value)
    run_dir = current_run_dir(required=False)
    if run_dir is not None:
        candidate = load_json(verdict_path(card_id(card)))
        inventory = _current_proof_inventory(card, run_dir)
        if inventory is not None:
            if candidate.get("schema") != _REVIEW_VERDICT_V2:
                raise DeliveryError(
                    "pinned observed-proof run requires a v2 review verdict"
                )
            return _validate_v2_verdict(card, run_dir, candidate)
        if candidate.get("schema") == _REVIEW_VERDICT_V2:
            raise DeliveryError("v2 verdict lacks a pinned observed-proof run contract")
    try:
        import jsonschema
    except ImportError as exc:
        raise DeliveryError(
            "jsonschema is required to validate review verdicts"
        ) from exc
    path = verdict_path(card_id(card))
    payload = load_json(path)
    schema = load_json(VERDICT_SCHEMA_PATH)
    try:
        jsonschema.validate(payload, schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as exc:
        raise DeliveryError(
            f"review verdict schema validation failed: {exc.message}"
        ) from exc
    current = payload_fingerprint()
    if payload["workspace"] != current:
        raise DeliveryError("review verdict is stale for the current payload")
    if payload["card"] != {"id": card_id(card), "path": repo_relative(card)}:
        raise DeliveryError("review verdict card identity is stale")
    expected_criteria = acceptance_criteria(card)
    observed_criteria = [item["criterion"] for item in payload["acceptance"]]
    observed_counts = Counter(observed_criteria)
    missing = [
        criterion for criterion in expected_criteria if not observed_counts[criterion]
    ]
    duplicates = sorted(
        (
            criterion
            for criterion, count in observed_counts.items()
            if count > 1 and criterion in expected_criteria
        )
    )
    foreign = [
        criterion
        for criterion in observed_criteria
        if criterion not in expected_criteria
    ]
    if missing or duplicates or foreign:
        raise DeliveryError(
            f"review verdict acceptance coverage mismatch: missing={missing}, duplicates={duplicates}, foreign={foreign}"
        )
    blocker = any((finding["severity"] == "blocker" for finding in payload["findings"]))
    failed = any((item["result"] == "fail" for item in payload["acceptance"]))
    if payload["result"] == "go" and (blocker or failed):
        raise DeliveryError("GO verdict contains a blocker or failed acceptance")
    if payload["result"] == "no-go" and (not (blocker or failed)):
        raise DeliveryError("NO-GO verdict requires a blocker or failed acceptance")
    return payload


def _completed_review_verdicts(history: Path) -> list[Path]:
    return sorted(history.glob("cycle-[0-9][0-9].json"))


def _matching_retained_verdict(
    card: Path, history: Path
) -> tuple[int, dict[str, Any]] | None:
    """Return a current verdict already retained by this run, if any."""
    existing = verdict_path(card_id(card))
    if not existing.is_file():
        return None
    try:
        verdict = validate_verdict(str(card))
    except DeliveryError:
        return None
    for path in reversed(_completed_review_verdicts(history)):
        retained = load_json(path)
        if retained == verdict:
            return (int(path.stem.removeprefix("cycle-")), verdict)
    return None


def _is_post_verification_repair(
    *, card: Path, run_dir: Path, previous_verdict: dict[str, Any] | None
) -> bool:
    """Prove that the current payload repairs a failed floor after a GO."""
    if not previous_verdict or previous_verdict.get("result") != "go":
        return False
    verification_path = run_dir / "verification.json"
    if not verification_path.is_file():
        return False
    verification = load_json(verification_path)
    previous_fingerprint = previous_verdict.get("workspace")
    return (
        verification.get("ok") is False
        and verification.get("card")
        == {"id": card_id(card), "path": repo_relative(card)}
        and (verification.get("fingerprint") == previous_fingerprint)
        and (payload_fingerprint() != previous_fingerprint)
    )


def run_review(card_value: str) -> int:
    if os.environ.get("CHRL_SESSION_ROLE") == "implementation":
        raise DeliveryError(
            "implementation sessions must hand off; the delivery runner owns review"
        )
    card = resolve_deliverable_card(card_value)
    run_dir = current_run_dir()
    assert run_dir is not None
    current_profile = profile()
    history = run_dir / "reviews"
    with _review_setup_lock(run_dir):
        require_repaired_final_payload(run_dir)
        require_current_successful_preverification(card, run_dir, stage="review")
        manifest = load_json(_manifest_for_run(card, run_dir))
        if manifest.get("paths") != changed_paths():
            raise DeliveryError("manifest scope is stale before review")
        native_mode = native.is_native(card)
        continuation = None
        if native_mode:
            from scripts.changerail.native_workflow import require_sync, pending_review

            require_sync(runner_module(), card, run_dir)
            continuation = pending_review(runner_module(), card, run_dir)
            if continuation and (not (run_dir / "native-archive.json").exists()):
                if continuation["before"] != payload_fingerprint():
                    raise DeliveryError(
                        "native provisional review payload changed before archive"
                    )
                return 0
        retained = _matching_retained_verdict(card, history)
        if retained is not None:
            cycle, verdict = retained
            print(
                json.dumps(
                    {"cycle": cycle, "result": verdict["result"], "reused": True},
                    ensure_ascii=False,
                )
            )
            return 0 if verdict["result"] == "go" else 3
        completed_cycles = _completed_review_verdicts(history)
        cycle = continuation["cycle"] if continuation else len(completed_cycles) + 1
        previous_verdict = load_json(completed_cycles[-1]) if completed_cycles else None
        budget_usage = review_budget_usage(run_dir)
        review_reason = (
            "post_verification_repair"
            if _is_post_verification_repair(
                card=card, run_dir=run_dir, previous_verdict=previous_verdict
            )
            else "semantic"
        )
        if not continuation and budget_usage["semantic_cycles"] >= 2:
            raise DeliveryError("shared two-review budget exhausted")
        before = payload_fingerprint()
        existing = verdict_path(card_id(card))
        if existing.is_file():
            existing.unlink()
        _write_review_json(
            run_dir, history / f"cycle-{cycle:02d}-manifest.json", manifest
        )
        review_context = build_review_context(
            card=card,
            run_dir=run_dir,
            cycle=cycle,
            manifest=manifest,
            review_reason=review_reason,
        )
        review_model, review_reasoning = model_route(current_profile, "review")
        actual_review_session: Path | None = None

        def retain_actual_review_allocation(session_dir: Path) -> None:
            nonlocal actual_review_session
            actual_review_session = session_dir

        native_env = {}
        if native_mode:
            context_path = run_dir / "native-context.json"
            write_json(context_path, native.delivery_context(runner_module(), card))
            native_env = {
                "CHRL_NATIVE_CONTEXT": str(context_path),
                "CHRL_NATIVE_REVIEW_PHASE": "final" if continuation else "active",
            }
            if continuation:
                native_env["CHRL_NATIVE_PRELIMINARY_REVIEW"] = str(
                    run_dir / "native-review-continuation.json"
                )
        code = launch_codex(
            role="review",
            prompt=f"${('chrl-native-review' if native_mode else 'chrl-review')} {repo_relative(card)}",
            model=review_model,
            reasoning=review_reasoning,
            run_dir=run_dir,
            timeout_minutes=int(current_profile["max_wall_minutes"]),
            session_env={
                "CHRL_REVIEW_CYCLE": str(cycle),
                "CHRL_REVIEW_CONTEXT": str(review_context),
                "CHRL_REVIEW_REASON": review_reason,
                **native_env,
            },
            resume_thread_id=continuation["thread_id"] if continuation else None,
            inherited_investigative_commands=continuation["commands"]
            if continuation
            else 0,
            expected_artifact=existing,
            on_session_started=retain_actual_review_allocation,
        )
        if payload_fingerprint() != before:
            raise DeliveryError("reviewer modified the tracked payload")
        if code:
            raise DeliveryError(f"review Codex session exited with {code}")
        verdict = validate_verdict(str(card))
        if (
            native_mode
            and (not (run_dir / "native-archive.json").exists())
            and (verdict["result"] == "go")
        ):
            from scripts.changerail.native_workflow import retain_provisional

            if actual_review_session is None:
                raise DeliveryError("native review lacks its actual session identity")
            retain_provisional(
                runner_module(), card, run_dir, cycle, existing, actual_review_session
            )
        else:
            shutil.copy2(existing, history / f"cycle-{cycle:02d}.json")
            if native_mode and (run_dir / "native-archive.json").exists():
                state_path = run_dir / "native-review-continuation.json"
                completed = continuation or _check_json(state_path)
                if not continuation:
                    write_json(
                        history / f"cycle-{completed['cycle']:02d}-continuation.json",
                        completed,
                    )
                completed.update(
                    complete=True,
                    final=payload_fingerprint(),
                    result=verdict["result"],
                    cycle=cycle,
                    final_verdict_sha256=hashlib.sha256(
                        existing.read_bytes()
                    ).hexdigest(),
                )
                write_json(state_path, completed)
        print(
            json.dumps(
                {"cycle": cycle, "result": verdict["result"], "reused": False},
                ensure_ascii=False,
            )
        )
        return 0 if verdict["result"] == "go" else 3


def run_shell_verification(
    command: str, log: Path, *, proof: tuple[Path, str] | None = None
) -> dict[str, Any]:
    from jsonschema.exceptions import ValidationError

    if proof is not None:
        run_dir, lane = proof
        identity = {
            "kind": "shell",
            "argv": ["bash", "-lc", command],
            "shell_text": command,
        }
        path, item = start_check_result(
            run_dir, lane, log.stem, identity, destination=log.parent
        )
    started = time.monotonic()
    output, code, outcome = (b"", None, "unknown")
    try:
        result = subprocess.run(
            ["bash", "-lc", command],
            cwd=REPO_ROOT,
            env=execution_env(),
            capture_output=True,
            check=False,
        )
        output, code, outcome = (
            result.stdout + result.stderr,
            result.returncode,
            "exit",
        )
    except OSError as exc:
        if proof is None:
            raise
        output, outcome = (str(exc).encode(), "spawn_failure")
    except KeyboardInterrupt:
        if proof is None:
            raise
        outcome = "interrupted"
    duration = round(time.monotonic() - started, 3)
    if proof is not None:
        after = payload_fingerprint()
        verified = outcome == "exit" and code == 0 and (item["before"] == after)
        item.update(
            state="terminal",
            observed_at=utc_now(),
            duration_seconds=duration,
            fingerprint=after,
            exit_code=code,
            outcome=outcome,
            verdict="verified" if verified else "unconfirmed",
            reason="stable" if verified else "process_failure_or_payload_drift",
        )
        try:
            finish_check_result(path, item, output)
            _, _, verified = read_check_result(path, run_dir, lane, identity)
        except (
            OSError,
            ValueError,
            DeliveryError,
            ValidationError,
            KeyboardInterrupt,
        ) as exc:
            verified = False
            item.update(verdict="unconfirmed", reason="retention_failure")
            try:
                write_json(path, item)
            except (OSError, KeyboardInterrupt):
                pass
            print(
                f"configured retention failed; observed exit={code!r}: {exc}",
                file=sys.stderr,
            )
        return {
            "command": command,
            "exit_code": code,
            "duration_seconds": duration,
            "record": repo_relative(path),
            "log": repo_relative(path.with_suffix(".log")),
            "verified": verified,
        }
    log.write_text(output.decode("utf-8"), encoding="utf-8")
    return {
        "command": command,
        "exit_code": code,
        "duration_seconds": duration,
        "log": repo_relative(log),
    }


def verification_commands(lane: str) -> list[str]:
    """Return the configured deterministic checks for one verification lane."""
    keys = {"pre_review": "pre_review_commands", "final": "final_commands"}
    try:
        key = keys[lane]
    except KeyError as exc:
        raise DeliveryError(f"unknown verification lane: {lane}") from exc
    current_profile = profile()
    commands = current_profile.get("verification", {}).get(key)
    if (
        not isinstance(commands, list)
        or not commands
        or (not all((isinstance(command, str) and command for command in commands)))
    ):
        raise DeliveryError(
            f"verification {lane} command set must be a non-empty string list"
        )
    if lane == "pre_review" and "targeted" in current_profile:
        return list(
            dict.fromkeys(
                [*commands, *select_targeted_commands(current_profile, changed_paths())]
            )
        )
    return commands


def _preverification_commands(run_dir: Path) -> list[str]:
    """Select the owning pre-review receipt lane from authenticated run mode."""
    try:
        _check_json(run_dir / "run.json")
    except (OSError, ValueError) as exc:
        raise DeliveryError("preverification owning run is unsafe") from exc
    return verification_commands("pre_review")


def _is_ruff_check_command(command: str) -> bool:
    """Recognize the configured Ruff lint contour without executing shell text."""
    try:
        arguments = shlex.split(command)
    except ValueError:
        return False
    return arguments[:4] == ["uv", "run", "ruff", "check"] or arguments[:2] == [
        "ruff",
        "check",
    ]


def run_safe_handoff_repair(run_dir: Path) -> bool:
    """Apply Ruff's safe import sorter to changed Python paths after its failure."""
    preverification_path = run_dir / "preverification.json"
    if not preverification_path.is_file():
        return False
    try:
        preverification = _check_json(preverification_path)
    except (ValueError, OSError):
        return False
    failed_commands = [
        item
        for item in (
            preverification.get("commands")
            if isinstance(preverification.get("commands"), list)
            else []
        )
        if isinstance(item, dict) and item.get("exit_code") not in (0, None)
    ]
    if len(failed_commands) != 1 or not _is_ruff_check_command(
        str(failed_commands[0].get("command") or "")
    ):
        return False
    python_paths = [
        path
        for path in changed_paths()
        if path.endswith(".py")
        and path.startswith(("src/", "tests/"))
        and (REPO_ROOT / path).is_file()
    ]
    if not python_paths:
        return False
    repair_root = run_dir / "deterministic-repairs"
    cycle_dir = _next_verification_cycle(repair_root)
    command = shlex.join(
        ["uv", "run", "ruff", "check", "--fix", "--select", "I", "--", *python_paths]
    )
    before = payload_fingerprint()
    result = run_shell_verification(command, cycle_dir / "01.log")
    after = payload_fingerprint()
    payload = {
        "schema": "changerail.deterministic-handoff-repair.v1",
        "kind": "safe_import_sorting",
        "paths": python_paths,
        "before_fingerprint": before,
        "after_fingerprint": after,
        "changed_payload": after != before,
        "command": result,
        "repaired_at": utc_now(),
    }
    write_json(cycle_dir / "repair.json", payload)
    write_json(run_dir / "deterministic-repair.json", payload)
    print(
        f"[{result['exit_code']}] {command} ({result['duration_seconds']}s)", flush=True
    )
    return result["exit_code"] == 0 and after != before


def _next_verification_cycle(root: Path) -> Path:
    cycle = len(list(root.glob("cycle-*"))) + 1 if root.exists() else 1
    cycle_dir = root / f"cycle-{cycle:02d}"
    cycle_dir.mkdir(parents=True, exist_ok=False)
    return cycle_dir


_VERIFICATION_CYCLE_NAME = re.compile("cycle-(?:0[1-9]|[1-9][0-9]+)")


def _is_verification_cycle_name(name: str) -> bool:
    """Accept exactly the positive, minimum-width names emitted by the allocator."""
    return _VERIFICATION_CYCLE_NAME.fullmatch(name) is not None


def _open_run_local_verification_lock(run_dir: Path) -> int:
    """Open the one regular no-follow lock file owned by a retained run."""
    try:
        relative = run_dir.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValueError("verification run is outside the repository") from exc
    if not relative.parts or ".." in relative.parts:
        raise ValueError("unsafe verification run path")
    directory = os.open(REPO_ROOT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in relative.parts:
            child = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
            )
            os.close(directory)
            directory = child
        fd = os.open(
            ".verification.lock",
            os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW,
            384,
            dir_fd=directory,
        )
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            os.close(fd)
            raise ValueError("verification lock is not regular")
        return fd
    finally:
        os.close(directory)


class _VerificationLockOwnership(NamedTuple):
    """An in-process capability yielded only while this run's flock is held."""

    token: str
    fd: int
    pid: int
    run_dir: Path
    card: Path


_ACTIVE_VERIFICATION_LOCKS: dict[str, _VerificationLockOwnership] = {}


def _require_verification_attempt_ownership(
    ownership: _VerificationLockOwnership, run_dir: Path, card: Path
) -> None:
    """Reject a forged/stale helper capability without taking a nested flock."""
    if not isinstance(ownership, _VerificationLockOwnership):
        raise DeliveryError("verification helper requires current lock ownership")
    current = _ACTIVE_VERIFICATION_LOCKS.get(ownership.token)
    if (
        current != ownership
        or ownership.pid != os.getpid()
        or ownership.run_dir != run_dir
        or (ownership.card != card)
    ):
        raise DeliveryError("verification helper requires current lock ownership")
    try:
        if not stat.S_ISREG(os.fstat(ownership.fd).st_mode):
            raise OSError("verification lock descriptor is not regular")
        fcntl.fcntl(ownership.fd, fcntl.F_GETFD)
    except OSError as exc:
        raise DeliveryError(
            "verification helper requires current lock ownership"
        ) from exc


def _verification_attempt_intent_path(run_dir: Path, attempt_id: str) -> Path:
    if not re.fullmatch("[a-f0-9]{32}", attempt_id):
        raise ValueError("unsafe verification attempt identity")
    return run_dir / "verification-attempts" / f"{attempt_id}.json"


def _start_verification_attempt_intent(
    run_dir: Path, record: Path, item: Mapping[str, Any]
) -> None:
    """Durably retain start ownership separately from mutable receipt proof."""
    if not record.is_relative_to(run_dir):
        raise ValueError("foreign verification attempt record")
    intent = _verification_attempt_intent_path(run_dir, str(item["attempt_id"]))
    payload = {
        "schema": "changerail.verification-attempt-intent.v1",
        "attempt_id": item["attempt_id"],
        "run_id": item["run_id"],
        "card": item["card"],
        "lane": item["lane"],
        "record": repo_relative(record),
        "state": "started",
    }
    intent.parent.mkdir(exist_ok=True)
    if intent.parent.is_symlink():
        raise ValueError("unsafe verification attempt directory")
    with intent.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _finish_verification_attempt_intent(path: Path, item: Mapping[str, Any]) -> None:
    """Only observed exit/spawn outcomes release durable start ownership."""
    if item.get("state") != "terminal" or item.get("outcome") not in {
        "exit",
        "spawn_failure",
    }:
        return
    try:
        run_dir = RUNTIME_ROOT / "runs" / str(item["run_id"])
        if not path.is_relative_to(run_dir):
            raise ValueError("foreign verification attempt intent")
        intent = _verification_attempt_intent_path(run_dir, str(item["attempt_id"]))
        payload = _check_json(intent)
        if (
            payload.get("state") != "started"
            or any(
                (
                    payload.get(key) != item.get(key)
                    for key in ("attempt_id", "run_id", "card", "lane")
                )
            )
            or payload.get("record") != repo_relative(path)
        ):
            raise ValueError("verification attempt intent identity changed")
        payload.update(
            state="observed_terminal",
            outcome=item["outcome"],
            exit_code=item.get("exit_code"),
            finished_at=item.get("observed_at"),
        )
        write_json(intent, payload)
    except (ValueError, OSError, DeliveryError) as exc:
        raise OSError(f"cannot retain verification attempt outcome: {exc}") from exc


def _intent_is_unresolved(run_dir: Path, path: Path) -> bool:
    """Interpret the ownership ledger; it is not verification proof or a log format."""
    try:
        payload = _check_json(path)
        started = {"schema", "attempt_id", "run_id", "card", "lane", "record", "state"}
        terminal = started | {"outcome", "exit_code", "finished_at"}
        if not isinstance(payload, dict) or set(payload) not in (started, terminal):
            return True
        if (
            payload.get("schema") != "changerail.verification-attempt-intent.v1"
            or not all(
                (
                    isinstance(payload.get(key), str) and payload[key]
                    for key in (
                        "attempt_id",
                        "run_id",
                        "card",
                        "lane",
                        "record",
                        "state",
                    )
                )
            )
            or payload.get("run_id") != run_dir.name
            or (payload.get("lane") not in {"focused", "pre_review", "final"})
            or Path(payload["card"]).is_absolute()
            or (".." in Path(payload["card"]).parts)
            or Path(payload["record"]).is_absolute()
            or (".." in Path(payload["record"]).parts)
            or (
                _verification_attempt_intent_path(run_dir, payload["attempt_id"])
                != path
            )
            or (payload["card"] != _check_owner(run_dir)["card"])
        ):
            return True
        record = REPO_ROOT / payload["record"]
        root = (
            run_dir
            / {
                "focused": "focused-evidence",
                "pre_review": "preverification",
                "final": "verification",
            }[payload["lane"]]
        )
        if (
            not record.is_relative_to(root)
            or record.stem != payload["attempt_id"]
            or record.suffix != ".json"
            or (payload["lane"] == "focused" and record.parent != root)
            or (
                payload["lane"] != "focused"
                and (
                    record.parent.parent != root
                    or not _is_verification_cycle_name(record.parent.name)
                )
            )
        ):
            return True
        if payload["state"] == "started":
            return True
        if payload["state"] != "observed_terminal" or set(payload) != terminal:
            return True
        if payload.get("outcome") not in {"exit", "spawn_failure"}:
            return True
        if not isinstance(payload.get("finished_at"), str):
            return True
        datetime.strptime(payload["finished_at"], "%Y-%m-%dT%H:%M:%SZ")
        if payload["outcome"] == "exit":
            return type(payload.get("exit_code")) is not int
        return payload.get("exit_code") is not None
    except (ValueError, OSError, DeliveryError, TypeError, KeyError):
        return True


def _unresolved_verification_attempt(run_dir: Path) -> str | None:
    """Return a safely decoded started attempt; terminal corruption is never reuse."""
    from jsonschema.exceptions import ValidationError

    intent_root = run_dir / "verification-attempts"
    if intent_root.exists():
        if intent_root.is_symlink() or not intent_root.is_dir():
            return repo_relative(intent_root)
        for path in sorted(intent_root.glob("*.json")):
            if _intent_is_unresolved(run_dir, path):
                return repo_relative(path)
    roots = {
        "focused": run_dir / "focused-evidence",
        "pre_review": run_dir / "preverification",
        "final": run_dir / "verification",
    }
    for record_lane, root in roots.items():
        patterns = ("*.json",) if record_lane == "focused" else ("cycle-*/*.json",)
        for pattern in patterns:
            for path in sorted(root.glob(pattern)):
                try:
                    item = _check_json(path)
                    if item.get("schema") != "changerail.check-result.v1":
                        continue
                    if item.get("state") == "terminal" and item.get("outcome") in {
                        "exit",
                        "spawn_failure",
                    }:
                        continue
                    read_check_result(path, run_dir, record_lane)
                except (ValueError, OSError, DeliveryError, ValidationError):
                    continue
                return repo_relative(path)
    return None


@contextmanager
def verification_attempt_lock(run_dir: Path, card: Path, lane: str):
    """Serialize every check decision through terminal index publication per run."""
    if lane not in {"focused", "pre_review", "final"}:
        raise ValueError("unknown verification lock lane")
    try:
        owner = _check_owner(run_dir)
        if owner["card"] != repo_relative(card):
            raise ValueError("foreign verification owner")
        fd = _open_run_local_verification_lock(run_dir)
    except (ValueError, OSError) as exc:
        raise DeliveryError(f"unsafe verification lock: {exc}") from exc
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise DeliveryError(
                "verification attempt is already running for this run"
            ) from exc
        if _check_owner(run_dir)["card"] != repo_relative(card):
            raise DeliveryError("foreign verification owner")
        unresolved = _unresolved_verification_attempt(run_dir)
        if unresolved is not None:
            raise DeliveryError(
                f"verification attempt remains unresolved after owner interruption: {unresolved}"
            )
        ownership = _VerificationLockOwnership(
            token=uuid.uuid4().hex, fd=fd, pid=os.getpid(), run_dir=run_dir, card=card
        )
        _ACTIVE_VERIFICATION_LOCKS[ownership.token] = ownership
        try:
            yield ownership
        finally:
            _ACTIVE_VERIFICATION_LOCKS.pop(ownership.token, None)
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def _successful_verification_matches(
    path: Path,
    *,
    card: Path,
    fingerprint: dict[str, str],
    commands: Sequence[str],
    run_dir: Path,
    lane: str,
) -> bool:
    return (
        _verified_command_set(path, run_dir, card, fingerprint, commands, lane)
        is not None
    )


class _VerifiedCommandSet(NamedTuple):
    """Internal result of the sole set decision, including the exact log bytes."""

    payload: dict[str, Any]
    receipts: list[tuple[dict[str, Any], bytes, bytes]]
    run_dir: Path
    lane: str


def _validated_final_test_proof_input(
    raw: Mapping[str, Any], *, run_dir: Path, inventory: Mapping[str, Any]
) -> tuple[str, dict[str, Any]]:
    """Validate one inert, current final assertion draft."""
    owner = _check_owner(run_dir)
    rows = {row["identity"]: row for row in inventory["conditions"]}
    if set(raw) != {
        "schema",
        "run",
        "payload",
        "inventory_digest",
        "condition",
        "assertion_support",
    }:
        raise DeliveryError("final test proof input is not closed")
    condition = raw.get("condition")
    row = rows.get(condition)
    if (
        raw.get("schema") != "changerail.final-test-proof-input.v1"
        or raw.get("run") != owner
        or raw.get("payload") != payload_fingerprint()
        or (raw.get("inventory_digest") != inventory["digest"])
        or (row is None)
        or (row["stage"] != "final")
        or (row["method"]["kind"] != "test")
    ):
        raise DeliveryError("final test proof input is stale or foreign")
    _validate_test_assertion_support(
        raw["assertion_support"], str(row["method"]["target"])
    )
    return (condition, dict(raw["assertion_support"]))


def _final_test_proof_inputs(
    card: Path, run_dir: Path, inventory: Mapping[str, Any]
) -> dict[str, dict[str, Any]]:
    """Read current inert drafts while retaining stale history as inert history."""
    root = run_dir / "final-test-proof-inputs"
    if not root.exists():
        return {}
    if root.is_symlink() or not root.is_dir():
        raise DeliveryError("final test proof input root is unsafe")
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob("*.json")):
        raw = _check_json(path)
        if (
            not isinstance(raw, dict)
            or set(raw)
            != {
                "schema",
                "run",
                "payload",
                "inventory_digest",
                "condition",
                "assertion_support",
            }
            or raw.get("schema") != "changerail.final-test-proof-input.v1"
        ):
            raise DeliveryError("final test proof input is not closed")
        if (
            raw.get("payload") != payload_fingerprint()
            or raw.get("inventory_digest") != inventory["digest"]
        ):
            continue
        condition, support = _validated_final_test_proof_input(
            raw, run_dir=run_dir, inventory=inventory
        )
        if condition in result:
            raise DeliveryError("final test proof input is duplicate")
        result[condition] = support
    return result


def retain_final_test_proof_input(run_dir: Path, artifact: Path) -> Path:
    """Retain an implementation/review draft; it has no execution authority."""
    _caller_proof_role()
    owner = _check_owner(run_dir)
    card = REPO_ROOT / owner["card"]
    inventory = _current_proof_inventory(card, run_dir)
    if inventory is None:
        raise DeliveryError("legacy run has no final proof-input authority")
    if not artifact.is_absolute():
        artifact = REPO_ROOT / artifact
    source = _safe_reference_path(
        repo_relative(artifact), root=run_dir, label="final proof input"
    )
    raw = _decode_closed_json(
        _check_bytes(source, 2 * 1024 * 1024), label="final proof input"
    )
    with verification_attempt_lock(run_dir, card, "final"):
        inventory = _current_proof_inventory(card, run_dir)
        if inventory is None:
            raise DeliveryError("legacy run has no final proof-input authority")
        condition, _support = _validated_final_test_proof_input(
            raw, run_dir=run_dir, inventory=inventory
        )
        directory_fd = _safe_proof_directory(
            run_dir, "final-test-proof-inputs", create=True
        )
        try:
            encoded = json.dumps(
                raw, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode()
            name = hashlib.sha256(encoded).hexdigest() + ".json"
            destination = run_dir / "final-test-proof-inputs" / name
            try:
                _write_json_at(directory_fd, name, raw, replace=False)
            except FileExistsError:
                if (
                    _check_bytes(destination, 2 * 1024 * 1024)
                    != (json.dumps(raw, ensure_ascii=False, indent=2) + "\n").encode()
                ):
                    raise DeliveryError("final test proof input history conflicts")
            return destination
        finally:
            os.close(directory_fd)


def _final_test_proof_supplies(
    run_dir: Path, inventory: Mapping[str, Any], existing: Sequence[Mapping[str, Any]]
) -> dict[str, Mapping[str, Any]]:
    """Return current completed supplies and refuse lost accepted history."""
    root = run_dir / "final-test-proof-supplies"
    if not root.exists():
        return {}
    if root.is_symlink() or not root.is_dir():
        raise DeliveryError("final test proof supply root is unsafe")
    owner = _check_owner(run_dir)
    present = {
        (proof["condition"], proof["observation_id"]): proof for proof in existing
    }
    result: dict[str, Mapping[str, Any]] = {}
    for path in sorted(root.glob("*.json")):
        marker = _check_json(path)
        if set(marker) != {
            "schema",
            "run",
            "payload",
            "inventory_digest",
            "condition",
            "observation_id",
            "record",
        }:
            raise DeliveryError("final test proof supply is not closed")
        if (
            marker.get("schema") != "changerail.final-test-proof-supply.v1"
            or marker.get("run") != owner
            or marker.get("payload") != payload_fingerprint()
            or (marker.get("inventory_digest") != inventory["digest"])
        ):
            continue
        condition = marker.get("condition")
        observation_id = marker.get("observation_id")
        if (
            not isinstance(condition, str)
            or not isinstance(observation_id, str)
            or condition in result
        ):
            raise DeliveryError("final test proof supply is malformed")
        proof = present.get((condition, observation_id))
        if proof is None or proof.get("stage") != "final":
            raise DeliveryError("accepted final test proof is missing or corrupt")
        reference = marker.get("record")
        try:
            record_path, record_bytes = _reference_bytes(
                reference, root=run_dir, label="final test proof supply record"
            )
            record = _decode_closed_json(
                record_bytes, label="final test proof supply record"
            )
        except (OSError, ValueError) as exc:
            raise DeliveryError(
                "accepted final test proof is missing or corrupt"
            ) from exc
        if (
            record_path.parent != run_dir / "proof-records"
            or record.get("condition") != condition
            or record.get("observation_id") != observation_id
        ):
            raise DeliveryError("accepted final test proof is missing or corrupt")
        result[condition] = marker
    return result


def _supply_final_test_proofs(
    card: Path,
    run_dir: Path,
    verification: _VerifiedCommandSet,
    ownership: _VerificationLockOwnership,
) -> None:
    """Publish only receipt-backed final test observations under the held lock.

    Inspection/runtime rows deliberately have no synthetic route: their separately
    supplied typed artifacts remain necessary.  This function never executes a
    card locator; it maps a declared locator to terminal nodes in the configured
    final command set that has already been validated byte-for-byte.
    """
    _require_verification_attempt_ownership(ownership, run_dir, card)
    if verification.run_dir != run_dir or verification.lane != "final":
        raise DeliveryError("final proof supply requires the current final command set")
    inventory = _current_proof_inventory(card, run_dir)
    if inventory is None:
        return
    try:
        existing = _validated_index_records(
            _check_json(_proof_index_path(run_dir)),
            card=card,
            run_dir=run_dir,
            inventory=inventory,
        )
    except FileNotFoundError:
        existing = []
    except (OSError, ValueError) as exc:
        raise DeliveryError("observed proof index cannot be safely read") from exc
    _final_test_proof_supplies(run_dir, inventory, existing)
    covered = {proof["condition"] for proof in existing if proof["stage"] == "final"}
    inputs = _final_test_proof_inputs(card, run_dir, inventory)
    receipts = list(verification.receipts)
    for row in inventory["conditions"]:
        if (
            row["stage"] != "final"
            or row["method"]["kind"] != "test"
            or row["identity"] in covered
        ):
            continue
        assertion_support = inputs.get(row["identity"])
        if assertion_support is None:
            continue
        target = str(row["method"]["target"])
        for receipt_index, (item, data, record_data) in enumerate(receipts):
            nodes = receipt_nodes(REPO_ROOT, profile(), item, data, target)
            if not nodes:
                continue
            entry = verification.payload["commands"][receipt_index]
            record_path = _safe_reference_path(
                entry["record"], root=run_dir, label="final receipt"
            )
            proof = {
                "schema": "changerail.card-proof.v1",
                "run": _check_owner(run_dir),
                "inventory_digest": inventory["digest"],
                "payload": payload_fingerprint(),
                "condition": row["identity"],
                "method": row["method"],
                "stage": "final",
                "observation_id": "outer-final-"
                + hashlib.sha256(row["identity"].encode()).hexdigest()[:16],
                "recorder_role": "outer",
                "kind": "test",
                "outcome": "pass",
                "artifact": {
                    "path": repo_relative(record_path),
                    "size": len(record_data),
                    "sha256": hashlib.sha256(record_data).hexdigest(),
                },
                "fragments": assertion_support["fragments"],
                "assertion_support": assertion_support,
                "lane": "final",
                "attempt_id": item["attempt_id"],
                "command_identity": item["command_identity"],
                "selected_nodes": nodes,
            }
            record_path = _record_observed_proof_with_ownership(
                run_dir, proof, actual_role="outer", ownership=ownership
            )
            marker = {
                "schema": "changerail.final-test-proof-supply.v1",
                "run": _check_owner(run_dir),
                "payload": payload_fingerprint(),
                "inventory_digest": inventory["digest"],
                "condition": row["identity"],
                "observation_id": proof["observation_id"],
                "record": _record_index_reference(record_path),
            }
            directory_fd = _safe_proof_directory(
                run_dir, "final-test-proof-supplies", create=True
            )
            try:
                marker_name = (
                    hashlib.sha256(
                        (
                            row["identity"]
                            + "\x00"
                            + inventory["digest"]
                            + "\x00"
                            + payload_fingerprint()["payload_fingerprint"]
                        ).encode()
                    ).hexdigest()
                    + ".json"
                )
                _write_json_at(directory_fd, marker_name, marker, replace=False)
            except FileExistsError as exc:
                raise DeliveryError(
                    "final test proof supply history conflicts"
                ) from exc
            finally:
                os.close(directory_fd)
            covered.add(row["identity"])
            break


def _verified_command_set(path, run_dir, card, fingerprint, commands, lane):
    """Read one owning ordered set once; return its validated records and bytes."""
    from jsonschema.exceptions import ValidationError

    try:
        owner = _check_owner(run_dir)
        if owner["card"] != repo_relative(card) or not path.is_relative_to(run_dir):
            return None
        payload = _check_json(path)
        expected_schema = {
            "pre_review": "changerail.pre-review-verification.v1",
            "final": "changerail.final-verification.v1",
        }.get(lane)
        if expected_schema is None or payload.get("schema") != expected_schema:
            return None
        datetime.strptime(payload["verified_at"], "%Y-%m-%dT%H:%M:%SZ")
        results = payload.get("commands")
        if not (
            payload.get("ok") is True
            and payload.get("card")
            == {"id": card_id(card), "path": repo_relative(card)}
            and (payload.get("fingerprint") == fingerprint)
            and (payload.get("configured_commands") == list(commands))
            and isinstance(results, list)
            and (len(results) == len(commands))
            and all(
                (
                    isinstance(row, dict)
                    and row.get("command") == command
                    and (type(row.get("exit_code")) is int)
                    and (row["exit_code"] == 0)
                    for row, command in zip(results, commands, strict=True)
                )
            )
        ):
            return None
        receipts, seen = ([], set())
        for row, command in zip(payload["commands"], commands, strict=True):
            reference = row.get("record")
            if (
                not isinstance(reference, str)
                or Path(reference).is_absolute()
                or ".." in Path(reference).parts
            ):
                return None
            reference = REPO_ROOT / reference
            if reference in seen:
                return None
            seen.add(reference)
            record_data = _check_bytes(reference)
            record_ref = {
                "path": repo_relative(reference),
                "size": len(record_data),
                "sha256": hashlib.sha256(record_data).hexdigest(),
            }
            identity = {
                "kind": "shell",
                "argv": ["bash", "-lc", command],
                "shell_text": command,
            }
            item, data, current = read_check_result(
                reference,
                run_dir,
                lane,
                identity,
                record_data=record_data,
                expected_record=record_ref,
            )
            if not current or item["fingerprint"] != fingerprint:
                return None
            receipts.append((item, data, record_data))
        return _VerifiedCommandSet(payload, receipts, run_dir, lane)
    except (
        ValueError,
        OSError,
        DeliveryError,
        ValidationError,
        TypeError,
        AttributeError,
        KeyError,
    ):
        return None


def require_current_successful_preverification(
    card: Path, run_dir: Path, *, stage: str
) -> dict[str, Any]:
    """Load a green preverification bound to the current payload and floor."""
    path = run_dir / "preverification.json"
    if not path.exists():
        raise DeliveryError(f"{stage} requires successful preverification")
    if os.environ.get("CHRL_RUN_DIR") and Path(os.environ["CHRL_RUN_DIR"]) != run_dir:
        raise DeliveryError(
            f"{stage} requires the original non-aliased owning run path"
        )
    result = _verified_command_set(
        path,
        run_dir,
        card,
        payload_fingerprint(),
        _preverification_commands(run_dir),
        "pre_review",
    )
    if result is None:
        raise DeliveryError(
            f"{stage} requires current successful preverification with the configured command set"
        )
    return result[0]


def _run_full_floor(
    card: Path,
    *,
    commands: Sequence[str],
    root_name: str,
    result_name: str,
    schema: str,
    event_stage: str,
    proof_lane: str,
    ownership: _VerificationLockOwnership | None = None,
) -> dict[str, Any]:
    run_dir = current_run_dir()
    assert run_dir is not None
    run_dir = Path(os.environ["CHRL_RUN_DIR"])
    if ownership is None:
        with verification_attempt_lock(run_dir, card, proof_lane) as acquired:
            return _run_full_floor(
                card,
                commands=commands,
                root_name=root_name,
                result_name=result_name,
                schema=schema,
                event_stage=event_stage,
                proof_lane=proof_lane,
                ownership=acquired,
            )
    _require_verification_attempt_ownership(ownership, run_dir, card)
    if _check_owner(run_dir)["card"] != repo_relative(card):
        raise DeliveryError("foreign verification owner")
    fingerprint = payload_fingerprint()
    configured = (
        _preverification_commands(run_dir)
        if proof_lane == "pre_review"
        else verification_commands(proof_lane)
    )
    if list(commands) != configured:
        raise DeliveryError("configured verification commands changed before execution")
    existing = run_dir / result_name
    if _successful_verification_matches(
        existing,
        run_dir=run_dir,
        lane=proof_lane,
        card=card,
        fingerprint=fingerprint,
        commands=configured,
    ):
        return _check_json(existing)
    if proof_lane == "final":
        require_repaired_final_payload(run_dir)
    cycle_dir = _next_verification_cycle(run_dir / root_name)
    emit_event("do", event_stage)
    results: list[dict[str, Any]] = []
    for index, command in enumerate(commands, start=1):
        item = run_shell_verification(
            command, cycle_dir / f"{index:02d}.log", proof=(run_dir, proof_lane)
        )
        results.append(item)
        print(
            f"[{item['exit_code']}] {command} ({item['duration_seconds']}s)", flush=True
        )
        if item["exit_code"] or not item["verified"]:
            break
    payload = {
        "schema": schema,
        "card": {"id": card_id(card), "path": repo_relative(card)},
        "verified_at": utc_now(),
        "ok": len(results) == len(commands)
        and all((item["exit_code"] == 0 for item in results))
        and all((item["verified"] for item in results))
        and (payload_fingerprint() == fingerprint),
        "fingerprint": fingerprint,
        "configured_commands": configured,
        "commands": results,
    }
    write_json(cycle_dir / result_name, payload)
    write_json(run_dir / result_name, payload)
    return payload


def preverify(card_value: str) -> int:
    card = resolve_deliverable_card(card_value)
    require_legacy_history()
    run_dir = current_run_dir()
    assert run_dir is not None
    run_dir = Path(os.environ["CHRL_RUN_DIR"])
    with verification_attempt_lock(run_dir, card, "pre_review") as ownership:
        try:
            if _check_owner(run_dir)["card"] != repo_relative(card):
                raise ValueError("foreign preverification owner")
            _check_json(run_dir / "run.json")
        except (ValueError, OSError) as exc:
            raise DeliveryError(f"unsafe preverification owner: {exc}") from exc
        require_delivery_card_structure(card)
        require_completed_change_plan(card, run_dir)
        if native.is_native(card):
            from scripts.changerail.native_workflow import require_sync

            require_sync(runner_module(), card, run_dir)
        require_substantive_result_and_log(card)
        require_non_future_log_timestamps(card)
        require_live_board_references()
        commands = _preverification_commands(run_dir)
        existing = run_dir / "preverification.json"
        if _successful_verification_matches(
            existing,
            run_dir=run_dir,
            lane="pre_review",
            card=card,
            fingerprint=payload_fingerprint(),
            commands=commands,
        ):
            emit_event("do", "preverification-reused")
            return 0
        payload = _run_full_floor(
            card,
            commands=commands,
            root_name="preverification",
            result_name="preverification.json",
            schema="changerail.pre-review-verification.v1",
            event_stage="preverification",
            proof_lane="pre_review",
            ownership=ownership,
        )
        return 0 if payload["ok"] else 1


def verify(card_value: str) -> int:
    if os.environ.get("CHRL_SESSION_ROLE") == "implementation":
        raise DeliveryError(
            "implementation sessions must hand off; the delivery runner owns verification"
        )
    card = resolve_deliverable_card(card_value)
    run_dir = current_run_dir()
    assert run_dir is not None
    run_dir = Path(os.environ["CHRL_RUN_DIR"])
    if native.is_native(card):
        from scripts.changerail.native_workflow import require_final_review

        require_final_review(runner_module(), card, run_dir)
    with verification_attempt_lock(run_dir, card, "final") as ownership:
        verdict = validate_verdict(str(card))
        if verdict["result"] != "go":
            raise DeliveryError("final verification requires a fresh GO verdict")
        manifest = load_json(_manifest_for_run(card, run_dir))
        if manifest.get("paths") != changed_paths():
            raise DeliveryError("manifest scope is stale before verification")
        require_current_successful_preverification(
            card, run_dir, stage="final verification"
        )
        commands = verification_commands("final")
        existing = run_dir / "verification.json"
        if _successful_verification_matches(
            existing,
            run_dir=run_dir,
            lane="final",
            card=card,
            fingerprint=payload_fingerprint(),
            commands=commands,
        ):
            if verdict.get("schema") == _REVIEW_VERDICT_V2:
                require_current_stage_proofs(
                    card, run_dir, ["implementation", "review"]
                )
                verification = _verified_command_set(
                    existing, run_dir, card, payload_fingerprint(), commands, "final"
                )
                if verification is None:
                    raise DeliveryError(
                        "final verification receipts cannot supply observed proof"
                    )
                try:
                    require_current_stage_proofs(
                        card, run_dir, ["final"], final_verification=verification
                    )
                except DeliveryError:
                    _caller_proof_role(outer=True)
                    _supply_final_test_proofs(card, run_dir, verification, ownership)
                    require_current_stage_proofs(
                        card, run_dir, ["final"], final_verification=verification
                    )
            emit_event("do", "verification-reused")
            return 0
        payload = _run_full_floor(
            card,
            commands=commands,
            root_name="verification",
            result_name="verification.json",
            schema="changerail.final-verification.v1",
            event_stage="verification",
            proof_lane="final",
            ownership=ownership,
        )
        if payload["ok"] and verdict.get("schema") == _REVIEW_VERDICT_V2:
            _caller_proof_role(outer=True)
            verification = _verified_command_set(
                run_dir / "verification.json",
                run_dir,
                card,
                payload_fingerprint(),
                commands,
                "final",
            )
            if verification is None:
                raise DeliveryError(
                    "final verification receipts cannot supply observed proof"
                )
            _supply_final_test_proofs(card, run_dir, verification, ownership)
            require_current_stage_proofs(
                card,
                run_dir,
                ["implementation", "review", "final"],
                final_verification=verification,
            )
        return 0 if payload["ok"] else 1


def pytest_summary_from_verification(
    verification: _VerifiedCommandSet, *, run_dir: Path
) -> str | None:
    """Parse the bytes issued by the complete final-set decision; never reopen."""
    if (
        not isinstance(verification, _VerifiedCommandSet)
        or verification.lane != "final"
        or verification.run_dir != run_dir
        or (verification.payload["fingerprint"] != payload_fingerprint())
        or (
            verification.payload["configured_commands"]
            != verification_commands("final")
        )
    ):
        raise DeliveryError("summary requires a current validated final command set")
    for item, data, _record_data in verification.receipts:
        if not is_full_pytest_command(item["command"]):
            continue
        for line in reversed(data.decode("utf-8", errors="replace").splitlines()):
            summary = line.strip().strip("=").strip()
            if re.search("\\b\\d+ passed\\b", summary) and re.search(
                "\\bin \\d", summary
            ):
                return summary
    return None


def delivery_receipt_lines(
    *,
    verdict: dict[str, Any],
    verification: _VerifiedCommandSet | None,
    run_dir: Path,
    finalized_at: str,
) -> list[str]:
    """Build a deterministic final receipt from retained machine evidence."""
    pytest_summary = pytest_summary_from_verification(verification, run_dir=run_dir)
    commands = verification.payload["commands"]
    passed = sum(
        (isinstance(item, dict) and item.get("exit_code") == 0 for item in commands)
    )
    lines = [
        "## Delivery Receipt",
        "",
        f"- Independent review: `GO` at `{verdict['reviewed_at']}`.",
        f"- Final repository verification: `passed` at `{verification.payload['verified_at']}`; {passed}/{len(commands)} configured commands succeeded.",
    ]
    has_full_pytest = any(
        (
            isinstance(item, dict)
            and is_full_pytest_command(str(item.get("command") or ""))
            for item in commands
        )
    )
    if has_full_pytest and (not pytest_summary):
        raise DeliveryError("cannot derive pytest summary from final verification log")
    if pytest_summary:
        lines.append(f"- Pytest: `{pytest_summary}`.")
    lines.append(
        f"- Deterministic done transition recorded at `{finalized_at}` for publish."
    )
    return lines


def finalize_card(card: Path, *, receipt: Sequence[str] = ()) -> Path:
    require_deliverable_card(card)
    text = _finalized_card_text(card.read_text(encoding="utf-8"), receipt)
    destination = BOARD_ROOT / "4.done" / card.name
    if destination.exists():
        raise DeliveryError(f"done-card destination already exists: {destination}")
    card.write_text(text, encoding="utf-8")
    card.replace(destination)
    return destination


def _finalized_card_text(text: str, receipt: Sequence[str]) -> str:
    """Derive the exact done-card bytes without changing the live board."""
    text = replace_section(text, "Status", ["4.done"])
    text = replace_section(
        text, "Next", ["- continue with the next dependency-ready epic card"]
    )
    if receipt:
        if "## Delivery Receipt" in text:
            raise DeliveryError("card already contains a delivery receipt")
        text = text.rstrip() + "\n\n" + "\n".join(receipt) + "\n"
    return text


def rewrite_active_board_references(card_name: str, destination: str) -> list[str]:
    """Move exact live-board links alongside a deterministic card transition."""
    sources = (
        f"openspec/board/1.backlog/{card_name}",
        f"openspec/board/2.todo/{card_name}",
        f"openspec/board/3.inprogress/{card_name}",
    )
    changed: list[str] = []
    for relative in live_board_reference_sources():
        path = REPO_ROOT / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if not any((source in text for source in sources)):
            continue
        for source in sources:
            text = text.replace(source, destination)
        path.write_text(text, encoding="utf-8")
        changed.append(relative)
    return changed


def _publish_continuation(
    card: Path,
    run_dir: Path,
    manifest_file: Path,
    manifest: dict[str, Any],
    verdict: dict[str, Any],
    verification: _VerifiedCommandSet,
    message: str | None,
) -> int:
    """Perform the irreversible deterministic continuation after all gates.

    Keeping this boundary separate makes the already-validated publisher
    decision testable without granting a test any way to bypass its evidence,
    manifest, index, or active-card checks.
    """
    _check_json(run_dir / "run.json")
    run_dir / "publication-journal.json"
    active_relative = repo_relative(card)
    finalized_at = utc_now()
    destination = finalize_card(
        card,
        receipt=delivery_receipt_lines(
            verdict=verdict,
            verification=verification,
            run_dir=run_dir,
            finalized_at=finalized_at,
        ),
    )
    destination_relative = repo_relative(destination)
    reference_paths = rewrite_active_board_references(
        destination.name, destination_relative
    )
    expected = set(manifest["paths"])
    if (
        git(
            "ls-files", "--error-unmatch", "--", active_relative, check=False
        ).returncode
        == 0
    ):
        expected.add(active_relative)
    else:
        expected.discard(active_relative)
    expected.add(destination_relative)
    expected.update(reference_paths)
    actual = set(changed_paths())
    if actual != expected:
        raise DeliveryError(
            f"deterministic finalization changed unexpected scope: expected={sorted(expected)} actual={sorted(actual)}"
        )
    git("add", "--", *sorted(actual))
    staged_check = git("diff", "--cached", "--check", check=False)
    if staged_check.returncode:
        raise DeliveryError(staged_check.stdout + staged_check.stderr)
    title = destination.read_text(encoding="utf-8").splitlines()[0].removeprefix("# ")
    commit_message = message or title
    evidence_paths = [run_dir / "verification.json", verdict_path(card_id(card))]
    for command in verification.payload["commands"]:
        for key in ("record", "log"):
            relative = command.get(key)
            if isinstance(relative, str):
                evidence_paths.append(REPO_ROOT / _safe_path(relative))
    receipt = {
        "schema": "changerail.publication.v1",
        "state": "prepared",
        "parent": git("rev-parse", "HEAD").stdout.strip(),
        "tree": git("write-tree").stdout.strip(),
        "destination": _publication_route(),
        "card": destination_relative,
        "evidence": {
            repo_relative(path): hashlib.sha256(
                _check_bytes(path, 32 * 1024 * 1024)
            ).hexdigest()
            for path in evidence_paths
        },
    }
    write_json(run_dir / "publication.json", receipt)
    git("commit", "-m", commit_message)
    commit = git("rev-parse", "HEAD").stdout.strip()
    if (
        git("rev-parse", "HEAD^{tree}").stdout.strip() != receipt["tree"]
        or git("rev-parse", "HEAD^").stdout.strip() != receipt["parent"]
    ):
        raise DeliveryError("commit differs from the approved publication tree")
    receipt.update(state="committed", commit=commit, committed_at=utc_now())
    write_json(run_dir / "publication.json", receipt)
    target = receipt["destination"]
    push = git("push", target["remote"], f"{commit}:{target['ref']}", check=False)
    if push.returncode == 0:
        receipt.update(state="pushed", pushed_at=utc_now())
        write_json(run_dir / "publication.json", receipt)
    status = "pushed" if push.returncode == 0 else "failed"
    manifest["card"] = {"id": card_id(destination), "path": repo_relative(destination)}
    manifest["publish"] = {
        "status": status,
        "commit": commit,
        "remote": "origin",
        "branch": git("branch", "--show-current").stdout.strip(),
        "finished_at": utc_now(),
    }
    write_json(manifest_file, manifest)
    write_json(run_dir / "manifest.json", manifest)
    if push.returncode:
        print(push.stdout + push.stderr, file=sys.stderr)
        return push.returncode
    emit_event("publish", "complete")
    print(json.dumps(manifest["publish"], ensure_ascii=False))
    return 0


def publish(card_value: str, message: str | None = None) -> int:
    if os.environ.get("CHRL_SESSION_ROLE") == "implementation":
        raise DeliveryError(
            "implementation sessions must hand off; the delivery runner owns publish"
        )
    card = resolve_deliverable_card(card_value)
    require_legacy_history()
    run_dir = current_run_dir()
    assert run_dir is not None
    run_dir = Path(os.environ["CHRL_RUN_DIR"])
    if card.parent.name != "3.inprogress":
        raise DeliveryError("publish expects the active card in 3.inprogress")
    if native.is_native(card):
        from scripts.changerail.native_workflow import require_final_review

        require_final_review(runner_module(), card, run_dir)
    verdict = validate_verdict(str(card))
    if verdict["result"] != "go":
        raise DeliveryError("publish requires GO")
    verification = _verified_command_set(
        run_dir / "verification.json",
        run_dir,
        card,
        payload_fingerprint(),
        verification_commands("final"),
        "final",
    )
    if verification is None:
        raise DeliveryError("final verification is missing, failed, or stale")
    if verdict.get("schema") == _REVIEW_VERDICT_V2:
        require_current_stage_proofs(
            card,
            run_dir,
            ["implementation", "review", "final"],
            final_verification=verification,
        )
    manifest_file = _manifest_for_run(card, run_dir)
    manifest = load_json(manifest_file)
    if manifest.get("paths") != changed_paths():
        raise DeliveryError("manifest scope is stale before publish")
    if git("diff", "--cached", "--quiet", check=False).returncode:
        raise DeliveryError("index contains pre-staged changes")
    return _publish_continuation(
        card, run_dir, manifest_file, manifest, verdict, verification, message
    )


def parse_session_metrics(session_dir: Path) -> dict[str, Any]:
    metadata = load_json(session_dir / "session.json")
    exact_usage = {key: 0 for key in TOKEN_USAGE_KEYS}
    partial_usage: dict[str, int | None] = {key: None for key in TOKEN_USAGE_KEYS}
    commands: list[dict[str, Any]] = []
    started: dict[str, tuple[str, float | None, str, dict[str, bool]]] = {}
    thread_id: str | None = None
    usage_complete = False
    usage_snapshot_count = 0
    usage_sources: set[str] = set()
    first_file_change_at: str | None = None
    commands_before_first_file_change: int | None = None
    investigative_commands_before_first_file_change: int | None = None
    command_start_count = 0
    investigative_command_start_count = int(
        metadata.get("inherited_investigative_commands") or 0
    )
    last_observed_at: str | None = None
    last_observed_elapsed: float | None = None

    def elapsed_between(
        began_at: str,
        finished_at: str,
        began_elapsed: float | None,
        finished_elapsed: float | None,
    ) -> float:
        if began_elapsed is not None and finished_elapsed is not None:
            return round(max(0.0, finished_elapsed - began_elapsed), 3)
        try:
            began = datetime.fromisoformat(began_at.replace("Z", "+00:00"))
            finished = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
        except ValueError:
            return 0.0
        return round(max(0.0, (finished - began).total_seconds()), 3)

    events_file = session_dir / "events.jsonl"
    if events_file.is_file():
        for line in events_file.read_text(encoding="utf-8").splitlines():
            envelope = json.loads(line)
            observed_at = str(envelope["observed_at"])
            observed_elapsed_value = envelope.get("observed_elapsed_seconds")
            observed_elapsed = (
                float(observed_elapsed_value)
                if isinstance(observed_elapsed_value, (int, float))
                else None
            )
            last_observed_at = observed_at
            last_observed_elapsed = observed_elapsed
            event = envelope["event"]
            if event.get("type") == "thread.started":
                thread_id = str(event.get("thread_id") or "") or None
            usage_value = event.get("usage")
            if isinstance(usage_value, dict) and any(
                (key in usage_value for key in TOKEN_USAGE_KEYS)
            ):
                usage_snapshot_count += 1
                event_type = str(event.get("type") or "unknown")
                usage_sources.add(event_type)
                if event_type == "turn.completed":
                    usage_complete = True
                    for key in TOKEN_USAGE_KEYS:
                        exact_usage[key] += int(usage_value.get(key, 0) or 0)
                elif not usage_complete:
                    for key in TOKEN_USAGE_KEYS:
                        value = usage_value.get(key)
                        if isinstance(value, int):
                            previous = partial_usage[key]
                            partial_usage[key] = max(previous or 0, value)
            item = event.get("item") if isinstance(event.get("item"), dict) else {}
            if (
                event.get("type") == "item.started"
                and item.get("type") == "command_execution"
            ):
                command_start_count += 1
                traits = dict(item.get("command_traits") or {})
                if "delivery_protocol" not in traits:
                    traits["delivery_protocol"] = is_delivery_protocol_command(
                        str(item.get("command") or "")
                    )
                if not traits.get("delivery_protocol", False):
                    investigative_command_start_count += 1
                started[str(item.get("id"))] = (
                    observed_at,
                    observed_elapsed,
                    str(item.get("command_fingerprint") or item.get("command") or ""),
                    dict(item.get("command_traits") or {}),
                )
            if (
                event.get("type") == "item.completed"
                and item.get("type") == "command_execution"
            ):
                item_id = str(item.get("id"))
                began, began_elapsed, command, traits = started.pop(
                    item_id,
                    (
                        observed_at,
                        observed_elapsed,
                        str(
                            item.get("command_fingerprint") or item.get("command") or ""
                        ),
                        dict(item.get("command_traits") or {}),
                    ),
                )
                commands.append(
                    {
                        "command": command,
                        "command_traits": traits,
                        "started_at": began,
                        "finished_at": observed_at,
                        "duration_seconds": elapsed_between(
                            began, observed_at, began_elapsed, observed_elapsed
                        ),
                        "exit_code": item.get("exit_code"),
                        "completed": True,
                    }
                )
            if (
                event.get("type") == "item.completed"
                and item.get("type") == "file_change"
                and (first_file_change_at is None)
            ):
                first_file_change_at = observed_at
                commands_before_first_file_change = command_start_count
                investigative_commands_before_first_file_change = (
                    investigative_command_start_count
                )
    unfinished_at = str(metadata.get("finished_at") or last_observed_at or "")
    session_duration = float(metadata.get("duration_seconds") or 0.0)
    unfinished_elapsed = session_duration if session_duration else last_observed_elapsed
    for began, began_elapsed, command, traits in started.values():
        commands.append(
            {
                "command": command,
                "command_traits": traits,
                "started_at": began,
                "finished_at": unfinished_at or None,
                "duration_seconds": elapsed_between(
                    began, unfinished_at or began, began_elapsed, unfinished_elapsed
                ),
                "exit_code": None,
                "completed": False,
            }
        )
    commands.sort(key=lambda item: str(item["started_at"]))
    if usage_complete:
        usage: dict[str, int | None] = dict(exact_usage)
        usage_status = "complete"
    elif usage_snapshot_count:
        usage = dict(partial_usage)
        usage_status = "partial"
    else:
        usage = {key: None for key in TOKEN_USAGE_KEYS}
        usage_status = "unknown"
    input_tokens = usage["input_tokens"]
    cached_tokens = usage["cached_input_tokens"]
    usage["uncached_input_tokens"] = (
        max(0, input_tokens - cached_tokens)
        if isinstance(input_tokens, int) and isinstance(cached_tokens, int)
        else None
    )
    pytest_commands = [item for item in commands if command_has_trait(item, "pytest")]
    full_pytest = [
        item for item in pytest_commands if command_has_trait(item, "full_pytest")
    ]
    review_protocol_commands = [
        item for item in commands if command_has_trait(item, "review_protocol")
    ]
    ff_protocol_commands = [
        item for item in commands if command_has_trait(item, "ff_protocol")
    ]
    delivery_protocol_commands = [
        item for item in commands if command_has_trait(item, "delivery_protocol")
    ]
    shell_command_seconds = round(
        sum((float(item["duration_seconds"]) for item in commands)), 3
    )
    session_wall_seconds = float(metadata.get("duration_seconds") or 0.0)
    stop_reason = metadata.get("stop_reason")
    if not isinstance(stop_reason, str) or not stop_reason:
        if metadata.get("budget_violation"):
            stop_reason = "command_safety_stop"
        elif metadata.get("timed_out"):
            stop_reason = "timeout"
        elif metadata.get("interrupted"):
            stop_reason = "operator_interrupt"
        elif metadata.get("exit_code") not in (0, None):
            stop_reason = "nonzero_exit"
        elif metadata.get("exit_code") is None:
            stop_reason = "incomplete_session"
        else:
            stop_reason = "completed"
    return {
        **metadata,
        "session": metadata.get("session") or session_dir.name,
        "stop_reason": stop_reason,
        "thread_id": thread_id,
        "first_file_change_at": first_file_change_at,
        "commands_before_first_file_change": commands_before_first_file_change,
        "investigative_commands_before_first_file_change": investigative_commands_before_first_file_change,
        "usage": usage,
        "usage_complete": usage_complete,
        "usage_status": usage_status,
        "usage_snapshot_count": usage_snapshot_count,
        "usage_sources": sorted(usage_sources),
        "command_count": len(commands),
        "review_investigative_command_count": len(commands)
        - len(review_protocol_commands),
        "review_protocol_command_count": len(review_protocol_commands),
        "ff_stage_investigative_command_count": len(commands)
        - len(ff_protocol_commands),
        "ff_protocol_command_count": len(ff_protocol_commands),
        "implementation_investigative_command_count": int(
            metadata.get("inherited_investigative_commands") or 0
        )
        + len(commands)
        - len(delivery_protocol_commands),
        "delivery_protocol_command_count": len(delivery_protocol_commands),
        "failed_command_count": sum(
            (item["exit_code"] not in (0, None) for item in commands)
        ),
        "pytest_command_count": len(pytest_commands),
        "full_pytest_command_count": len(full_pytest),
        "timing": {
            "session_wall_seconds": round(session_wall_seconds, 3),
            "shell_command_seconds": shell_command_seconds,
            "model_api_non_command_seconds": round(
                max(0.0, session_wall_seconds - shell_command_seconds), 3
            ),
        },
        "commands": commands,
    }


def configured_command_observations(
    run_dir: Path, path: Path, lane: str
) -> list[dict[str, Any]]:
    """Typed display-only rows survive broken proof; never certify a command set."""
    from jsonschema.exceptions import ValidationError

    try:
        owner = _check_owner(run_dir)
        rows = _check_json(path).get("commands")
    except (ValueError, OSError, DeliveryError):
        return []
    observations = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        if isinstance(row.get("record"), str):
            record, row = (REPO_ROOT / row["record"], {})
            if not record.is_relative_to(run_dir):
                continue
            try:
                row = _check_json(record)
                if (
                    row.get("lane") != lane
                    or row.get("attempt_id") != record.stem
                    or any((row.get(key) != value for key, value in owner.items()))
                ):
                    continue
                read_check_result(record, run_dir, lane)
            except ValidationError:
                row = {}
            except (ValueError, OSError, DeliveryError):
                pass
        duration = row.get("duration_seconds")
        try:
            duration = float(duration) if type(duration) in (int, float) else None
        except OverflowError:
            duration = None
        if duration is not None and (not math.isfinite(duration) or duration < 0):
            duration = None
        observations.append(
            {
                "proof_status": "unconfirmed",
                "command": row.get("command")
                if isinstance(row.get("command"), str)
                else None,
                "exit_code": row.get("exit_code")
                if type(row.get("exit_code")) is int
                else None,
                "duration_seconds": duration,
                "finished_at": row.get("observed_at")
                if isinstance(row.get("observed_at"), str)
                else None,
            }
        )
    return observations


def deterministic_commands(run_dir: Path) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    for item in focused_evidence_summaries(run_dir):
        try:
            if (
                _check_json(REPO_ROOT / item["record"]).get("schema")
                == "changerail.dependency-reuse.v1"
            ):
                continue
        except (ValueError, OSError):
            pass
        commands.append(
            {
                "source": "focused-evidence",
                "proof_status": item["proof_status"],
                "command": item["command"],
                "exit_code": item["exit_code"],
                "duration_seconds": item["duration_seconds"],
                "finished_at": item["observed_at"],
            }
        )
    for path in sorted((run_dir / "deterministic-repairs").glob("cycle-*/repair.json")):
        repair = load_json(path)
        item = repair.get("command")
        if isinstance(item, dict):
            commands.append({"source": "deterministic-handoff-repair", **item})
    for path in sorted(
        (run_dir / "preverification").glob("cycle-*/preverification.json")
    ):
        commands.extend(
            (
                {"source": "pre-review-verification", **row}
                for row in configured_command_observations(run_dir, path, "pre_review")
            )
        )
    for path in sorted((run_dir / "verification").glob("cycle-*/verification.json")):
        commands.extend(
            (
                {"source": "final-verification", **row}
                for row in configured_command_observations(run_dir, path, "final")
            )
        )
    return commands


def is_pytest_command(command: str) -> bool:
    return re.search("(?:^|\\s)pytest(?:\\s|$)", command) is not None


def is_full_pytest_command(command: str) -> bool:
    """Classify an untargeted pytest invocation without project-specific flags."""
    try:
        argv = shlex.split(command)
    except ValueError:
        return False
    if argv[:2] == ["uv", "run"]:
        argv = argv[2:]
    if (
        argv
        and Path(argv[0]).name.startswith("python")
        and (argv[1:3] == ["-m", "pytest"])
    ):
        argv = argv[2:]
    if not argv or Path(argv[0]).name != "pytest":
        return False
    takes_value = {
        "-m",
        "--maxfail",
        "--cov",
        "--cov-report",
        "--cov-fail-under",
        "--junitxml",
        "--rootdir",
        "-o",
        "--override-ini",
    }
    waiting = False
    for token in argv[1:]:
        if waiting:
            waiting = False
        elif token in takes_value:
            waiting = True
        elif not token.startswith("-") or token in {
            "-k",
            "--lf",
            "--last-failed",
            "--ff",
            "--failed-first",
        }:
            return False
    return not waiting


def is_deterministic_wrapper(command: str) -> bool:
    return any(
        (
            wrapper in command
            for wrapper in (
                "bin/chrl evidence",
                "bin/chrl handoff",
                "bin/chrl preverify",
                "bin/chrl verify",
            )
        )
    )


def command_has_trait(item: dict[str, Any], trait: str) -> bool:
    traits = item.get("command_traits")
    if isinstance(traits, dict) and trait in traits:
        return bool(traits[trait])
    command = str(item.get("command") or "")
    if trait == "pytest":
        return is_pytest_command(command)
    if trait == "full_pytest":
        return is_full_pytest_command(command)
    if trait == "deterministic_wrapper":
        return is_deterministic_wrapper(command)
    if trait == "review_protocol":
        return is_review_protocol_command(command)
    if trait == "review_wrapper":
        return is_review_wrapper_command(command)
    if trait == "ff_protocol":
        return is_ff_protocol_command(command)
    if trait == "delivery_protocol":
        return is_delivery_protocol_command(command)
    return False


def _union_timed_seconds(items: Sequence[dict[str, Any]]) -> float:
    """Measure elapsed coverage once when timed items overlap or nest."""
    intervals: list[tuple[float, float]] = []
    for item in items:
        started_at = item.get("started_at")
        duration = item.get("duration_seconds")
        if not isinstance(started_at, str) or not isinstance(duration, (int, float)):
            continue
        try:
            start = datetime.fromisoformat(
                started_at.replace("Z", "+00:00")
            ).timestamp()
        except ValueError:
            continue
        intervals.append((start, start + max(0.0, float(duration))))
    merged: list[tuple[float, float]] = []
    for start, finish in sorted(intervals):
        if finish <= start:
            continue
        if not merged or start > merged[-1][1]:
            merged.append((start, finish))
            continue
        merged[-1] = (merged[-1][0], max(merged[-1][1], finish))
    return sum((finish - start for start, finish in merged))


def _calculate_metrics(run_dir: Path) -> dict[str, Any]:
    """Calculate retained metrics without refreshing any run-local record."""
    run = _check_json(run_dir / "run.json")
    if any(
        (
            not isinstance(run.get(key), str) or not run[key]
            for key in ("run_id", "card", "started_at")
        )
    ):
        raise DeliveryError("metrics owning metadata is incomplete")
    current_profile = profile()
    sessions = [
        parse_session_metrics(path)
        for path in sorted((run_dir / "sessions").glob("*"))
        if path.is_dir()
    ]
    process_budgets = current_profile.get("budgets", {})
    budget_observations: list[dict[str, Any]] = []
    for session in sessions:
        role = session.get("role")
        verdict_only_budget: int | None = None
        hard_stop_budget: int | None = None
        if role == "implementation":
            command_budget = session.get("command_budget")
            if (
                isinstance(command_budget, dict)
                and command_budget.get("metric") is None
            ):
                continue
            budget = int(process_budgets.get("first_edit_discovery_commands", 8))
            hard_stop_budget = int(
                process_budgets.get("first_edit_hard_stop_commands", budget)
            )
            observed = session.get("investigative_commands_before_first_file_change")
            metric = "investigative_commands_before_first_file_change"
            if not isinstance(observed, int):
                observed = session.get("implementation_investigative_command_count")
        elif role == "review":
            budget = int(process_budgets.get("review_commands", 12))
            hard_stop_budget = int(
                process_budgets.get("review_hard_stop_commands", max(budget, 20))
            )
            verdict_only_budget = int(
                process_budgets.get(
                    "review_verdict_only_commands",
                    min(hard_stop_budget, max(budget, 20)),
                )
            )
            observed = session.get("review_investigative_command_count")
            metric = "review_investigative_command_count"
        elif isinstance(role, str) and role.startswith("ff-"):
            budget = int(process_budgets.get("ff_stage_discovery_commands", 6))
            hard_stop_budget = int(
                process_budgets.get("ff_stage_hard_stop_commands", max(budget, 8))
            )
            observed = session.get("ff_stage_investigative_command_count")
            metric = "ff_stage_investigative_command_count"
        else:
            continue
        violation = session.get("budget_violation")
        if isinstance(violation, dict):
            budget = int(violation.get("budget", budget))
            observed = violation.get("observed")
            metric = str(violation.get("metric", metric))
        budget_observations.append(
            {
                "role": role,
                "metric": metric,
                "budget": budget,
                "observed": observed,
                "exceeded": isinstance(violation, dict)
                or (isinstance(observed, int) and observed > budget),
                "verdict_only_budget": verdict_only_budget,
                "verdict_only_entered": isinstance(observed, int)
                and verdict_only_budget is not None
                and (observed >= verdict_only_budget),
                "hard_stop_budget": hard_stop_budget,
                "hard_stop_exceeded": isinstance(observed, int)
                and hard_stop_budget is not None
                and (observed > hard_stop_budget),
                **(
                    {"enforced": False}
                    if (session.get("command_budget") or {}).get("enforced") is False
                    else {}
                ),
            }
        )
    usage_keys = (*TOKEN_USAGE_KEYS, "uncached_input_tokens")
    usage_lower_bound = {
        key: sum(
            (
                value
                for session in sessions
                if isinstance((value := session["usage"][key]), int)
            )
        )
        for key in usage_keys
    }
    usage_complete = bool(sessions) and all(
        (session["usage_complete"] for session in sessions)
    )
    usage_observed = any((session["usage_status"] != "unknown" for session in sessions))
    if usage_complete:
        totals: dict[str, int | None] = dict(usage_lower_bound)
        usage_status = "complete"
    else:
        totals = {key: None for key in usage_keys}
        usage_status = "partial" if usage_observed else "unknown"
    agent_commands = [item for session in sessions for item in session["commands"]]
    measured_commands = deterministic_commands(run_dir)
    command_observations = [*agent_commands, *measured_commands]
    execution_commands = [
        item
        for item in agent_commands
        if not command_has_trait(item, "deterministic_wrapper")
    ]
    execution_commands.extend(measured_commands)
    frequencies: dict[str, int] = {}
    for item in execution_commands:
        frequencies[item["command"]] = frequencies.get(item["command"], 0) + 1
    phase_events = read_phase_events(run_dir)
    phase_durations: list[dict[str, Any]] = []
    for current, following in zip(phase_events, phase_events[1:], strict=False):
        start = datetime.fromisoformat(current["at"].replace("Z", "+00:00"))
        finish = datetime.fromisoformat(following["at"].replace("Z", "+00:00"))
        phase_durations.append(
            {
                "phase": current["phase"],
                "stage": current["stage"],
                "duration_seconds": round((finish - start).total_seconds(), 3),
            }
        )
    pytest_commands = [
        item for item in execution_commands if command_has_trait(item, "pytest")
    ]
    full_pytest = [
        item for item in pytest_commands if command_has_trait(item, "full_pytest")
    ]
    agent_failures = sum(
        (item["exit_code"] not in (0, None) for item in agent_commands)
    )
    deterministic_failures = sum(
        (item["exit_code"] not in (0, None) for item in measured_commands)
    )
    run_finished_at = str(
        run.get("finished_at")
        or next(
            (
                session.get("finished_at")
                for session in reversed(sessions)
                if session.get("finished_at")
            ),
            utc_now(),
        )
    )
    recorded_run_duration = run.get("duration_seconds")
    if isinstance(recorded_run_duration, (int, float)):
        run_wall_seconds = max(0.0, float(recorded_run_duration))
    else:
        try:
            run_started = datetime.fromisoformat(
                str(run["started_at"]).replace("Z", "+00:00")
            )
            run_finished = datetime.fromisoformat(
                run_finished_at.replace("Z", "+00:00")
            )
            run_wall_seconds = max(0.0, (run_finished - run_started).total_seconds())
        except ValueError:
            run_wall_seconds = sum(
                (
                    float(session["timing"]["session_wall_seconds"])
                    for session in sessions
                )
            )
    raw_session_wall_seconds = sum(
        (float(session["timing"]["session_wall_seconds"]) for session in sessions)
    )
    timed_sessions = [
        {
            "started_at": session.get("started_at"),
            "duration_seconds": session["timing"]["session_wall_seconds"],
        }
        for session in sessions
    ]
    timed_session_seconds = _union_timed_seconds(timed_sessions)
    session_wall_seconds = timed_session_seconds or raw_session_wall_seconds
    review_wrapper_commands = [
        item for item in agent_commands if command_has_trait(item, "review_wrapper")
    ]
    shell_commands = [
        item for item in agent_commands if not command_has_trait(item, "review_wrapper")
    ]
    shell_command_seconds = _union_timed_seconds(shell_commands)
    model_api_non_command_seconds = max(
        0.0, session_wall_seconds - shell_command_seconds
    )
    deterministic_check_seconds = sum(
        (float(item.get("duration_seconds") or 0.0) for item in measured_commands)
    )
    stop_reason_counts = Counter(
        (str(session.get("stop_reason") or "unknown") for session in sessions)
    )
    payload = {
        "schema": "changerail.delivery-metrics.v1",
        "run_id": run["run_id"],
        "card": run["card"],
        "started_at": run["started_at"],
        "finished_at": run_finished_at,
        "sessions": sessions,
        "usage": totals,
        "usage_observed_lower_bound": usage_lower_bound,
        "usage_status": usage_status,
        "usage_complete": usage_complete,
        "usage_incomplete_session_count": sum(
            (not session["usage_complete"] for session in sessions)
        ),
        "model_routes": [
            {
                "session": session.get("session"),
                "role": session.get("role"),
                "model": session.get("model"),
                "reasoning_effort": session.get("reasoning_effort"),
                "review_reason": session.get("review_reason"),
                "source": (session.get("model_evidence") or {}).get("source"),
            }
            for session in sessions
        ],
        "command_count": len(agent_commands),
        "agent_command_count": len(agent_commands),
        "deterministic_command_count": len(measured_commands),
        "command_observation_count": len(command_observations),
        "execution_command_count": len(execution_commands),
        "failed_command_count": agent_failures,
        "deterministic_failed_command_count": deterministic_failures,
        "failed_command_observation_count": agent_failures + deterministic_failures,
        "repeated_commands": [
            {"command": command, "count": count}
            for command, count in sorted(
                frequencies.items(), key=lambda pair: pair[0] or ""
            )
            if count > 1
        ],
        "pytest_command_count": len(pytest_commands),
        "full_pytest_command_count": len(full_pytest),
        "review_attempt_count": sum(
            (session["role"] == "review" for session in sessions)
        ),
        "review_cycle_count": len(
            list((run_dir / "reviews").glob("cycle-[0-9][0-9].json"))
        ),
        "stop_reason_counts": dict(sorted(stop_reason_counts.items())),
        "process_budgets": process_budgets,
        "budget_observations": budget_observations,
        "phase_events": phase_events,
        "phase_durations": phase_durations,
        "change_checkpoints": change_checkpoint_statuses(
            declared_change_plan(run_dir) or [], combined_change_events(run_dir)
        ),
        "timing": {
            "run_wall_seconds": round(run_wall_seconds, 3),
            "session_wall_seconds": round(session_wall_seconds, 3),
            "raw_session_wall_seconds": round(raw_session_wall_seconds, 3),
            "overlapping_session_seconds": round(
                max(0.0, raw_session_wall_seconds - session_wall_seconds), 3
            ),
            "agent_shell_command_seconds": round(shell_command_seconds, 3),
            "deterministic_check_seconds": round(deterministic_check_seconds, 3),
            "model_api_non_command_seconds": round(model_api_non_command_seconds, 3),
            "review_wrapper_wait_seconds": round(
                _union_timed_seconds(review_wrapper_commands), 3
            ),
            "orchestration_outside_sessions_seconds": round(
                max(0.0, run_wall_seconds - session_wall_seconds), 3
            ),
            "deterministic_check_seconds_are_nested_in_session_wall": True,
        },
        "duplicate_review_invocation_count": max(
            0,
            sum((command_has_trait(item, "review_wrapper") for item in agent_commands))
            - sum((session["role"] == "review" for session in sessions)),
        ),
    }
    return payload


def build_metrics(run_dir: Path, *, persist: bool = False) -> dict[str, Any]:
    """Read retained history without modifying receipts; only the runner persists."""
    payload = _calculate_metrics(run_dir)
    if persist:
        require_current_execution(run_dir)
        write_json(run_dir / "metrics.json", payload)
    return payload


def retain_recovery_manifest(
    *, card_name: str, run_dir: Path, manifest: dict[str, Any]
) -> dict[str, Any]:
    """Retain an exact dirty payload after a bounded session stops early."""
    paths = changed_paths()
    if not paths:
        return manifest
    current_head = git("rev-parse", "HEAD").stdout.strip()
    if manifest.get("baseline_head") != current_head:
        raise DeliveryError(
            "cannot retain recovery payload after baseline HEAD changed"
        )
    card = resolve_deliverable_card(card_name)
    manifest.update(
        {
            "updated_at": utc_now(),
            "card": {"id": card_id(card), "path": repo_relative(card)},
            "paths": paths,
            "fingerprint": payload_fingerprint(paths),
            "path_fingerprints": path_fingerprints(paths),
        }
    )
    write_json(manifest_path(card_id(card)), manifest)
    write_json(run_dir / "manifest.json", manifest)
    return manifest


def implementation_session_dirs(run_dir: Path) -> list[Path]:
    """Return implementation sessions in launch order."""
    sessions: list[tuple[str, Path]] = []
    for path in (run_dir / "sessions").glob("*"):
        metadata_path = path / "session.json"
        if not metadata_path.is_file():
            continue
        metadata = load_json(metadata_path)
        if metadata.get("role") == "implementation":
            sessions.append((str(metadata.get("started_at") or ""), path))
    return [path for _started_at, path in sorted(sessions)]


def latest_implementation_thread(run_dir: Path) -> str | None:
    """Return the newest retained implementation thread identifier."""
    for path in reversed(implementation_session_dirs(run_dir)):
        thread_id = parse_session_metrics(path).get("thread_id")
        if isinstance(thread_id, str) and thread_id:
            return thread_id
    return None


def _manifest_has_product_payload(manifest: dict[str, Any]) -> bool:
    paths = manifest.get("paths", [])
    return isinstance(paths, list) and any(
        (
            isinstance(path, str) and (not path.startswith("openspec/board/"))
            for path in paths
        )
    )


def recovery_implementation_state(
    previous_run: Path, manifest: dict[str, Any]
) -> tuple[str | None, bool, int]:
    """Return thread, first-edit requirement, and inherited discovery count."""
    thread_id = latest_implementation_thread(previous_run)
    require_first_edit = not _manifest_has_product_payload(manifest)
    inherited = 0
    sessions = implementation_session_dirs(previous_run)
    if require_first_edit and sessions:
        metrics = parse_session_metrics(sessions[-1])
        observed = metrics.get("investigative_commands_before_first_file_change")
        if not isinstance(observed, int):
            violation = metrics.get("budget_violation")
            if isinstance(violation, dict):
                observed = violation.get("observed")
        if not isinstance(observed, int):
            observed = metrics.get("implementation_investigative_command_count")
        if isinstance(observed, int):
            inherited = observed
    return (thread_id, require_first_edit, inherited)


def start_delivery_card(card: Path, manifest: dict[str, Any]) -> Path:
    """Move one accepted card into progress under deterministic runner control."""
    require_deliverable_card(card)
    emit_event("do", "starting")
    if card.parent.name != "2.todo":
        raise DeliveryError("native start requires an accepted todo card")
    target = BOARD_ROOT / "3.inprogress" / card.name
    if target.exists() or board_activity()["active"]:
        raise DeliveryError("native start requires an empty active-card lane")
    text = replace_section(card.read_text(encoding="utf-8"), "Status", ["3.inprogress"])
    text = replace_section(text, "Result", ["implementation in progress"])
    log = section_body(text, "Log")
    text = replace_section(
        text, "Log", [*log, f"- {utc_now()} started native OpenSpec delivery"]
    )
    card.write_text(text, encoding="utf-8")
    card.rename(target)
    manifest["card"] = {"id": card_id(target), "path": repo_relative(target)}
    write_json(manifest_path(card_id(target)), manifest)
    return target


def build_repair_context(*, card: Path, run_dir: Path, reason: str) -> Path:
    """Create the bounded finding or floor context for one repair turn."""
    reviews = _completed_review_verdicts(run_dir / "reviews")
    verdict = load_json(reviews[-1]) if reviews else None
    verification_path = run_dir / "verification.json"
    verification = load_json(verification_path) if verification_path.is_file() else None
    failed_commands = []
    if isinstance(verification, dict) and verification.get("ok") is False:
        failed_commands = [
            item
            for item in verification.get("commands", [])
            if isinstance(item, dict) and item.get("exit_code") != 0
        ]
    payload = {
        "schema": "changerail.repair-context.v1",
        "card": {"id": card_id(card), "path": repo_relative(card)},
        "reason": reason,
        "current_fingerprint": payload_fingerprint(),
        "review_verdict": repo_relative(reviews[-1]) if reviews else None,
        "findings": verdict.get("findings", []) if isinstance(verdict, dict) else [],
        "failed_verification_commands": failed_commands,
        "instruction": "Repair only the recorded root-cause findings or failed final-floor command. Do not repeat completed Change checkpoints or broad discovery. Refresh affected evidence, Result/Log, and finish with chrl handoff.",
    }
    root = run_dir / "repair-contexts"
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"repair-{len(list(root.glob('repair-*.json'))) + 1:02d}.json"
    write_json(path, payload)
    return path


def launch_implementation_stage(
    *,
    card: Path,
    run_dir: Path,
    current_profile: dict[str, Any],
    resume_thread_id: str | None = None,
    recovery_context: Path | None = None,
    repair_context: Path | None = None,
    require_first_file_change: bool = True,
    inherited_investigative_commands: int = 0,
) -> str | None:
    """Run one implementation or repair turn through a validated handoff."""
    current_handoff = handoff_path(run_dir)
    current_handoff.unlink(missing_ok=True)
    session_env: dict[str, str] = {}
    if recovery_context is not None:
        session_env.update(
            {"CHRL_RECOVERY_RUN": "1", "CHRL_RECOVERY_CONTEXT": str(recovery_context)}
        )
    if repair_context is not None:
        session_env["CHRL_REPAIR_CONTEXT"] = str(repair_context)
    native_mode = native.is_native(card)
    if native_mode:
        context_path = run_dir / "native-context.json"
        write_json(context_path, native.delivery_context(runner_module(), card))
        session_env["CHRL_NATIVE_CONTEXT"] = str(context_path)
        session_env["CHRL_DELIVERY_STAGE"] = (
            "archive-refresh"
            if repair_context
            and repair_context.name == "native-archive-finalization.json"
            else "repair"
            if repair_context
            else "finalize"
        )
    implementation_model, implementation_reasoning = model_route(
        current_profile, "implementation"
    )
    code = launch_codex(
        role="implementation",
        prompt=f"$chrl-native-deliver {repo_relative(card)}",
        model=implementation_model,
        reasoning=implementation_reasoning,
        run_dir=run_dir,
        timeout_minutes=int(current_profile["max_wall_minutes"]),
        session_env=session_env or None,
        expected_artifact=current_handoff,
        resume_thread_id=resume_thread_id,
        require_first_file_change=require_first_file_change,
        inherited_investigative_commands=inherited_investigative_commands,
    )
    if code:
        raise DeliveryError(f"implementation Codex session exited with {code}")
    require_current_implementation_handoff(card, run_dir)
    return latest_implementation_thread(run_dir) or resume_thread_id


def orchestrate_delivery(
    *,
    card: Path,
    run_dir: Path,
    current_profile: dict[str, Any],
    resume_thread_id: str | None,
    recovery_context: Path | None,
    require_first_file_change: bool,
    inherited_investigative_commands: int,
) -> int:
    """Own review, repair, verification, and publish outside the LLM."""
    if native.is_native(card) and (not (run_dir / "native-archive.json").exists()):
        from scripts.changerail.native_workflow import launch_groups

        launch_groups(
            runner_module(),
            card=card,
            run_dir=run_dir,
            current_profile=current_profile,
            recovery_context=recovery_context,
        )
        resume_thread_id = None
        require_first_file_change = False
    thread_id = launch_implementation_stage(
        card=card,
        run_dir=run_dir,
        current_profile=current_profile,
        resume_thread_id=resume_thread_id,
        recovery_context=recovery_context,
        require_first_file_change=require_first_file_change,
        inherited_investigative_commands=inherited_investigative_commands,
    )
    while True:
        require_frozen_execution(run_dir)
        emit_event("review", "waiting")
        review_code = run_review(str(card))
        if review_code == 3:
            if review_budget_usage(run_dir)["semantic_cycles"] >= 2:
                raise DeliveryError("shared two-review budget exhausted after NO-GO")
            repair_reason = "semantic_review"
            repair_thread_id = thread_id
            repair = build_repair_context(
                card=card, run_dir=run_dir, reason=repair_reason
            )
            thread_id = launch_implementation_stage(
                card=card,
                run_dir=run_dir,
                current_profile=current_profile,
                resume_thread_id=repair_thread_id,
                repair_context=repair,
                require_first_file_change=False,
            )
            continue
        if review_code:
            raise DeliveryError(f"review failed with exit code {review_code}")
        if native.is_native(card) and (not (run_dir / "native-archive.json").is_file()):
            archive_receipt = native.archive(runner_module(), card, run_dir)
            archive_context = run_dir / "native-archive-finalization.json"
            write_json(
                archive_context,
                {
                    "schema": "changerail.native-archive-finalization.v1",
                    "reason": "stock_sync_archive_after_provisional_go",
                    "archive": archive_receipt,
                    "instruction": "Do not alter product code or archived OpenSpec artifacts. Refresh Result/Log and current evidence for the archived payload, then produce a new handoff for final review.",
                },
            )
            before_refresh = path_fingerprints(
                [p for p in changed_paths() if p != repo_relative(card)]
            )
            thread_id = launch_implementation_stage(
                card=card,
                run_dir=run_dir,
                current_profile=current_profile,
                resume_thread_id=None,
                repair_context=archive_context,
                require_first_file_change=False,
            )
            if before_refresh != path_fingerprints(
                [p for p in changed_paths() if p != repo_relative(card)]
            ):
                raise DeliveryError(
                    "archive evidence refresh changed product or artifact payload"
                )
            continue
        verification_code = verify_as_outer_dispatch(str(card))
        if verification_code == 0:
            emit_event("publish", "finalizing")
            return publish(str(card))
        if review_budget_usage(run_dir)["semantic_cycles"] >= 2:
            raise DeliveryError(
                "shared two-review budget exhausted after failed final verification"
            )
        repair = build_repair_context(
            card=card, run_dir=run_dir, reason="final_verification"
        )
        thread_id = launch_implementation_stage(
            card=card,
            run_dir=run_dir,
            current_profile=current_profile,
            resume_thread_id=thread_id,
            repair_context=repair,
            require_first_file_change=False,
        )


def verify_as_outer_dispatch(card_value: str) -> int:
    """Runner-owned outer dispatch; direct callers never gain an implicit role."""
    prior = os.environ.get("CHRL_SESSION_ROLE")
    os.environ["CHRL_SESSION_ROLE"] = "outer"
    try:
        return verify(card_value)
    finally:
        if prior is None:
            os.environ.pop("CHRL_SESSION_ROLE", None)
        else:
            os.environ["CHRL_SESSION_ROLE"] = prior


@contextmanager
def delivery_lock(*, restoration_reconcile: bool = False):
    """Serialize checkout writers; never follow a substituted lock file."""
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    path = RUNTIME_ROOT / "delivery.lock"
    if RUNTIME_ROOT.resolve() != RUNTIME_ROOT.absolute():
        raise DeliveryError("delivery lock directory must not contain symlinks")
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 384)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise DeliveryError("delivery lock must be a regular file")
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise DeliveryError("another delivery runner holds the checkout") from exc
        if not restoration_reconcile:
            from scripts.changerail import plan_restoration

            plan_restoration.ensure_no_pending(runner_module())
        yield
    finally:
        os.close(descriptor)


def run_delivery(
    card_value: str, *, recovery: bool = False, required_run_id: str | None = None
) -> int:
    with delivery_lock():
        from scripts.changerail import plan_restoration

        plan_restoration.ensure_no_pending(runner_module())
        return _run_delivery(
            card_value, recovery=recovery, required_run_id=required_run_id
        )


def _run_delivery(
    card_value: str, *, recovery: bool = False, required_run_id: str | None = None
) -> int:
    health = doctor(card_value, recovery=recovery, required_run_id=required_run_id)
    print(json.dumps(health, ensure_ascii=False, indent=2))
    if not health["ok"]:
        return 2
    card = resolve_deliverable_card(card_value)
    current_profile = profile()
    run_started_monotonic = time.monotonic()
    previous_run_id = str(health.get("recovery_of") or "")
    previous_run = RUNTIME_ROOT / "runs" / previous_run_id
    recovery_compatibility: str | None = None
    if recovery:
        require_frozen_execution(previous_run)
        _run_observed_contract(previous_run)
        for origin in (previous_run, *recovery_ancestors(previous_run)):
            if _unresolved_verification_attempt(origin):
                raise DeliveryError(
                    "interrupted verification attempt cannot restart through ordinary recovery"
                )
    if recovery and native.is_native(card):
        changes = declared_change_plan(previous_run)
        from scripts.changerail import plan_restoration

        retained_plan = plan_restoration.accepted_plan(runner_module(), previous_run)
        if retained_plan is None:
            retained_plan = _check_json(previous_run / "native-plan.json")
        if not changes or retained_plan.get("groups") != [
            list(group) for group in changes
        ]:
            raise DeliveryError(
                "native recovery checkpoint plan differs from accepted predecessor"
            )
    else:
        changes = planned_changes(card)
    from scripts.changerail import plan_restoration

    prepared = (
        plan_restoration.create_successor(
            runner_module(),
            previous_run,
            card,
            changes,
            os.environ["CHRL_RECOVERY_OBJECTIVE"].strip(),
        )
        if recovery
        else None
    )
    if prepared is not None:
        run_dir = prepared["run_dir"]
        run = prepared["run"]
        manifest = prepared["manifest"]
        recovery_context = prepared["recovery_context"]
        resume_thread_id = run["resume_thread_id"]
        inherited_investigative_commands = run["inherited_investigative_commands"]
        require_first_file_change = run["restoration_require_first_file_change"]
        write_json(manifest_path(card_id(card)), manifest)
    else:
        run_id = (
            f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{card_id(card)}"
        )
        run_dir = RUNTIME_ROOT / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        creation_selection = {
            "schema": "changerail.observed-proof-selection.v1",
            "root": repo_relative(run_dir),
            "owner": {"run_id": run_id, "card": repo_relative(card)},
            "required_stages": ["implementation", "review", "final"],
        }
        creation_path = run_dir / "observed-proof-selection.json"
        write_json(creation_path, creation_selection)
        creation_bytes = _check_bytes(creation_path)
        creation_reference = {
            "path": repo_relative(creation_path),
            "sha256": hashlib.sha256(creation_bytes).hexdigest(),
        }
        run = {
            "schema": "changerail.delivery-run.v2",
            "run_id": run_id,
            "card": repo_relative(card),
            "started_at": utc_now(),
            "baseline_head": git("rev-parse", "HEAD").stdout.strip(),
            "profile": repo_relative(PROFILE_PATH),
            "mode": "delivery",
            "lifecycle_mode": native.lifecycle_mode(card),
            "change_plan": [
                {"number": number, "slug": slug} for number, slug in changes
            ],
        }
        run["execution_contract"] = "changerail.native.v1"
        run["process_identity"] = execution_identity()
        run["observed_proof_contract"] = {
            "schema": _OBSERVED_PROOF_CONTRACT,
            "required_stages": ["implementation", "review", "final"],
            "selection": creation_reference,
        }
        resume_thread_id: str | None = None
        require_first_file_change = True
        inherited_investigative_commands = 0
        if recovery:
            run["recovery_of"] = previous_run_id
            run["recovery_compatibility"] = recovery_compatibility
            run["recovery_objective"] = os.environ["CHRL_RECOVERY_OBJECTIVE"].strip()
            previous_manifest = load_json(previous_run / "manifest.json")
            (
                resume_thread_id,
                require_first_file_change,
                inherited_investigative_commands,
            ) = recovery_implementation_state(previous_run, previous_manifest)
            run["resume_thread_id"] = resume_thread_id
            run["inherited_investigative_commands"] = inherited_investigative_commands
        write_json(run_dir / "run.json", run)
        if recovery:
            from scripts.changerail import plan_restoration

            restoration = plan_restoration.consume(
                runner_module(), previous_run, run_dir
            )
            if restoration is not None:
                run["plan_restoration"] = restoration
                write_json(run_dir / "run.json", run)
        if recovery and native.is_native(card):
            carried = native.carry_archive_receipt(
                runner_module(), previous_run, run_dir
            )
            intent = previous_run / "native-archive-intent.json"
            if carried or intent.exists():
                from scripts.changerail.native_workflow import inherit_archived_context

                for source in (previous_run / "native-plan.json", intent):
                    if source.exists():
                        with (run_dir / source.name).open("xb") as stream:
                            stream.write(_check_bytes(source))
                            stream.flush()
                            os.fsync(stream.fileno())
                inherit_archived_context(runner_module(), previous_run, run_dir)
                run["native_archive_recovery_source"] = repo_relative(
                    previous_run / "native-archive.json" if carried else intent
                )
                write_json(run_dir / "run.json", run)
        manifest = {
            "schema": "changerail.delivery-manifest.v1",
            "run_id": run_id,
            "baseline_head": run["baseline_head"],
            "created_at": utc_now(),
            "card": {"id": card_id(card), "path": repo_relative(card)},
            "paths": [],
        }
        manifest["observed_proof_selection"] = creation_reference
        write_json(manifest_path(card_id(card)), manifest)
        write_json(run_dir / "manifest.json", manifest)
        recovery_context: Path | None = None
        if recovery:
            recovery_context = build_recovery_context(
                run_dir=run_dir,
                previous_run=previous_run,
                objective=str(run["recovery_objective"]),
            )
            recovery_payload = load_json(recovery_context)
            run["resume_thread_id"] = resume_thread_id
            run["recovery_session_strategy"] = recovery_payload.get("resume_strategy")
            run["inherited_change_events"] = recovery_payload["inherited_change_events"]
            write_json(run_dir / "run.json", run)
    emit_environment = {"CHRL_RUN_DIR": str(run_dir)}
    original = os.environ.get("CHRL_RUN_DIR")
    os.environ.update(emit_environment)
    code = 2
    try:
        emit_event("preflight", "complete")
        try:
            if native.is_native(card):
                from scripts.changerail.openspec_board import import_accepted

                if (run_dir / "native-archive-intent.json").exists() and (
                    not (run_dir / "native-archive.json").exists()
                ):
                    native.archive(runner_module(), card, run_dir)
                import_accepted(runner_module(), card, run_dir)
                if planned_changes(card) != changes:
                    raise DeliveryError(
                        "native recovery artifacts changed checkpoint plan"
                    )
            if not recovery:
                card = start_delivery_card(card, manifest)
                run["card"] = repo_relative(card)
                write_json(run_dir / "run.json", run)
                write_json(run_dir / "manifest.json", manifest)
            code = orchestrate_delivery(
                card=card,
                run_dir=run_dir,
                current_profile=current_profile,
                resume_thread_id=resume_thread_id,
                recovery_context=recovery_context,
                require_first_file_change=require_first_file_change,
                inherited_investigative_commands=inherited_investigative_commands,
            )
            final_matches = sorted((BOARD_ROOT / "4.done").glob(card.name))
            if code == 0 and (len(final_matches) != 1 or changed_paths()):
                code = 2
                run["terminal_reason"] = (
                    "session exited without a clean published done card"
                )
        except DeliveryError as exc:
            code = 2
            run["terminal_reason"] = str(exc)
            try:
                retain_recovery_manifest(
                    card_name=card.name, run_dir=run_dir, manifest=manifest
                )
            except DeliveryError as manifest_exc:
                run["recovery_manifest_error"] = str(manifest_exc)
            print(f"local ChangeRail: {exc}", file=sys.stderr)
        finally:
            run.update(
                {
                    "finished_at": utc_now(),
                    "duration_seconds": round(
                        time.monotonic() - run_started_monotonic, 3
                    ),
                    "exit_code": code,
                }
            )
            write_json(run_dir / "run.json", run)
            metrics = build_metrics(run_dir, persist=True)
            print(
                json.dumps(
                    {"run_dir": repo_relative(run_dir), "metrics": metrics["usage"]},
                    ensure_ascii=False,
                )
            )
        return code
    finally:
        if original is None:
            os.environ.pop("CHRL_RUN_DIR", None)
        else:
            os.environ["CHRL_RUN_DIR"] = original


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("card")
    doctor_parser.add_argument("--no-remote", action="store_true")
    doctor_parser.add_argument("--recovery", action="store_true")
    subparsers.add_parser("install")
    subparsers.add_parser("wiring")
    repair_prepare = subparsers.add_parser("runtime-repair-prepare")
    repair_prepare.add_argument("run_dir", type=Path)
    repair_prepare.add_argument("--test", dest="tests", action="append", required=True)
    repair_prepare.add_argument("--reason", required=True)
    repair_apply = subparsers.add_parser("runtime-repair-apply")
    repair_apply.add_argument("run_dir", type=Path)
    repair_apply.add_argument("--proposal", type=Path, required=True)
    restore_prepare = subparsers.add_parser("plan-restore-prepare")
    restore_prepare.add_argument("run_dir", type=Path)
    restore_prepare.add_argument("--reason", required=True)
    restore_prepare.add_argument("--dry-run", action="store_true")
    restore_prepare.add_argument("--runtime-archive", type=Path)
    restore_apply = subparsers.add_parser("plan-restore-apply")
    restore_apply.add_argument("run_dir", type=Path)
    restore_apply.add_argument("--proposal", type=Path, required=True)
    restore_apply.add_argument("--authorize", required=True)
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("run_dir", type=Path)
    resume_parser = subparsers.add_parser("resume")
    resume_parser.add_argument("run_dir", type=Path)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("card")
    run_parser.add_argument("--recovery", action="store_true")
    event_parser = subparsers.add_parser("event")
    event_parser.add_argument("phase")
    event_parser.add_argument("stage")
    evidence_parser = subparsers.add_parser("evidence")
    evidence_parser.add_argument("--label", required=True)
    evidence_parser.add_argument("evidence_command", nargs=argparse.REMAINDER)
    proof_parser = subparsers.add_parser("proof")
    proof_parser.add_argument("action", choices=("record", "prepare-final"))
    proof_parser.add_argument("artifact", type=Path)
    proof_parser.add_argument("--outer", action="store_true")
    manifest_parser = subparsers.add_parser("manifest")
    manifest_parser.add_argument("card")
    handoff_parser = subparsers.add_parser("handoff")
    handoff_parser.add_argument("card")
    review_parser = subparsers.add_parser("review")
    review_parser.add_argument("card")
    verdict_parser = subparsers.add_parser("verdict")
    verdict_parser.add_argument(
        "action", choices=("fingerprint", "template", "validate")
    )
    verdict_parser.add_argument("card")
    preverify_parser = subparsers.add_parser("preverify")
    preverify_parser.add_argument("card")
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("card")
    publish_parser = subparsers.add_parser("publish")
    publish_parser.add_argument("card")
    publish_parser.add_argument("--message")
    metrics_parser = subparsers.add_parser("metrics")
    metrics_parser.add_argument("run_dir", type=Path)
    admission_parser = subparsers.add_parser("admission")
    admission_parser.add_argument("card")
    native_accept_parser = subparsers.add_parser("native-accept")
    native_accept_parser.add_argument("card")
    native_accept_parser.add_argument("--dry-run", action="store_true")
    native_sync_parser = subparsers.add_parser("native-sync")
    native_sync_parser.add_argument("card")
    native_sync_parser.add_argument("--report", required=True, type=Path)
    guard_parser = subparsers.add_parser("board-guard")
    guard_parser.add_argument("card")
    guard_parser.add_argument("--start", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        # Session commands share the runner's lock; reject pending restoration
        # before any child writer dispatch, including stale CHRL_RUN_DIR callers.
        if args.command not in {
            "plan-restore-apply",
            "status",
            "metrics",
            "doctor",
            "wiring",
            "admission",
            "verdict",
            "board-guard",
        }:
            from scripts.changerail import plan_restoration

            plan_restoration.ensure_no_pending(runner_module())
        if args.command in {"plan-restore-prepare", "plan-restore-apply"}:
            from scripts.changerail import plan_restoration
            from scripts.changerail.native_workflow import retained_run

            run_dir, _metadata = retained_run(runner_module(), args.run_dir)
            if args.command == "plan-restore-prepare":
                result = plan_restoration.prepare(
                    runner_module(),
                    run_dir,
                    reason=args.reason,
                    dry_run=args.dry_run,
                    runtime_archive=args.runtime_archive,
                )
            else:
                result = plan_restoration.apply(
                    runner_module(),
                    run_dir,
                    args.proposal,
                    args.authorize,
                )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command in {"runtime-repair-prepare", "runtime-repair-apply"}:
            from scripts.changerail import runtime_repair
            from scripts.changerail.native_workflow import retained_run

            run_dir, _metadata = retained_run(runner_module(), args.run_dir)
            if args.command == "runtime-repair-prepare":
                result = runtime_repair.prepare(
                    runner_module(), run_dir, tests=args.tests, reason=args.reason
                )
            else:
                result = runtime_repair.apply(runner_module(), run_dir, args.proposal)
            print(
                json.dumps(
                    result if isinstance(result, dict) else {"proposal": str(result)},
                    ensure_ascii=False,
                )
            )
            return 0
        if args.command == "board-guard":
            board_guard(args.card, start=args.start)
            return 0
        if args.command == "wiring":
            payload = wiring_report()
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0 if payload["ok"] else 1
        if args.command == "status":
            from scripts.changerail.native_workflow import status

            observation = status(runner_module(), args.run_dir)
            try:
                observation["source"] = source_binding.source_info(REPO_ROOT)
            except (DeliveryError, OSError, ValueError) as exc:
                observation["source"] = {"mode": "invalid", "error": str(exc)}
            print(json.dumps(observation, ensure_ascii=False, indent=2))
            return 0
        if args.command == "resume":
            from scripts.changerail.native_workflow import retained_run

            run_dir, metadata = retained_run(runner_module(), args.run_dir)
            require_frozen_execution(run_dir)
            if (run_dir / "publication.json").is_file():
                return resume_publication(run_dir)
            card = resolve_deliverable_card(metadata["card"])
            ok, detail, manifest = recovery_source(
                card, changed_paths(), required_run_id=run_dir.name
            )
            if not ok or not manifest or manifest.get("run_id") != run_dir.name:
                raise DeliveryError(
                    "resume requires the selected exact predecessor: " + detail
                )
            previous_objective = os.environ.get("CHRL_RECOVERY_OBJECTIVE")
            os.environ["CHRL_RECOVERY_OBJECTIVE"] = (
                previous_objective
                or "Continue the remaining accepted native groups, review and finalization."
            )
            try:
                return run_delivery(
                    str(card), recovery=True, required_run_id=run_dir.name
                )
            finally:
                if previous_objective is None:
                    os.environ.pop("CHRL_RECOVERY_OBJECTIVE", None)
                else:
                    os.environ["CHRL_RECOVERY_OBJECTIVE"] = previous_objective
        if args.command == "doctor":
            payload = doctor(
                args.card, check_remote=not args.no_remote, recovery=args.recovery
            )
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0 if payload["ok"] else 1
        if args.command == "install":
            print(json.dumps(install_local_hooks(), ensure_ascii=False, indent=2))
            return 0
        if args.command == "run":
            return run_delivery(args.card, recovery=args.recovery)
        if args.command == "native-accept":
            from scripts.changerail.openspec_board import accept_card

            if os.environ.get("CHRL_SESSION_ROLE"):
                raise DeliveryError("native-accept must run before delivery")
            with delivery_lock():
                if git("branch", "--show-current").stdout.strip() != "main":
                    raise DeliveryError("native acceptance requires main")
                payload = accept_card(
                    runner_module(), resolve_card(args.card), dry_run=args.dry_run
                )
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 0
        if args.command == "native-sync":
            from scripts.changerail.native_workflow import record_sync

            record_sync(
                runner_module(),
                resolve_deliverable_card(args.card),
                current_run_dir(),
                args.report,
            )
            return 0
        if args.command == "event":
            emit_event(args.phase, args.stage)
            return 0
        if args.command == "evidence":
            command = list(args.evidence_command)
            if command[:1] == ["--"]:
                command = command[1:]
            return run_evidence(args.label, command)
        if args.command == "proof":
            run_dir = _unresolved_proof_run_dir()
            if args.action == "prepare-final":
                destination = retain_final_test_proof_input(run_dir, args.artifact)
                print(
                    json.dumps(
                        {"input": repo_relative(destination)}, ensure_ascii=False
                    )
                )
                return 0
            destination = record_observed_proof_artifact(
                run_dir, args.artifact, outer=args.outer
            )
            print(
                json.dumps({"record": repo_relative(destination)}, ensure_ascii=False)
            )
            return 0
        if args.command == "manifest":
            print(json.dumps(capture_manifest(args.card), ensure_ascii=False, indent=2))
            return 0
        if args.command == "handoff":
            return implementation_handoff(args.card)
        if args.command == "review":
            return run_review(args.card)
        if args.command == "verdict":
            if args.action == "fingerprint":
                print(json.dumps(payload_fingerprint(), ensure_ascii=False, indent=2))
            elif args.action == "template":
                print(
                    json.dumps(
                        verdict_template(args.card), ensure_ascii=False, indent=2
                    )
                )
            else:
                print(
                    json.dumps(
                        validate_verdict(args.card), ensure_ascii=False, indent=2
                    )
                )
            return 0
        if args.command == "preverify":
            return preverify(args.card)
        if args.command == "verify":
            return verify(args.card)
        if args.command == "publish":
            return publish(args.card, args.message)
        if args.command == "metrics":
            from scripts.changerail.native_workflow import retained_run

            run_dir, _metadata = retained_run(
                runner_module(), args.run_dir, read_only=True
            )
            print(json.dumps(build_metrics(run_dir), ensure_ascii=False, indent=2))
            return 0
        if args.command == "admission":
            report = admission_report(resolve_card(args.card))
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["status"] == "READY" else 3
    except (DeliveryError, OSError, subprocess.SubprocessError) as exc:
        print(f"local ChangeRail: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
