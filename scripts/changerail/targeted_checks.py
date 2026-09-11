"""Select additive project regression commands from changed repository paths."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from fnmatch import fnmatchcase
from typing import Any

from scripts.changerail.contracts import DeliveryError

MAX_TARGETED_RULES = 1000
MAX_RULE_VALUES = 1000
MAX_CHANGED_PATHS = 100000


def _relative_path(value: object, *, label: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or "\x00" in value
        or value.startswith("/")
        or "\\" in value
        or any(part in {"", ".", ".."} for part in value.split("/"))
    ):
        raise DeliveryError(f"{label} must be a normalized repository-relative path")
    return value


def select_targeted_commands(
    profile: Mapping[str, Any],
    changed_paths: Sequence[str],
) -> list[str]:
    """Return matching commands in profile order, with exact duplicates removed.

    Each ``[[targeted]]`` rule has nonempty ``paths`` glob and ``commands`` lists.
    Any changed path matching any pattern selects every command in that rule.
    Matching uses case-sensitive fnmatch semantics (``*`` can span ``/``).
    Paths need not exist: callers supply additions, modifications, deletions and
    both rename endpoints. The result is additive to mandatory verification;
    this function neither executes commands nor replaces the repository floor.
    Every rule is validated, including currently unmatched rules.
    """
    if not isinstance(profile, Mapping):
        raise DeliveryError("targeted command profile must be a mapping")
    if (
        not isinstance(changed_paths, Sequence)
        or isinstance(changed_paths, (str, bytes))
        or len(changed_paths) > MAX_CHANGED_PATHS
    ):
        raise DeliveryError("changed paths must be a bounded sequence")
    changed = sorted(
        {_relative_path(path, label="changed path") for path in changed_paths}
    )
    rules = profile.get("targeted", [])
    if not isinstance(rules, list) or len(rules) > MAX_TARGETED_RULES:
        raise DeliveryError("targeted configuration must be a bounded list of rules")
    selected: list[str] = []
    seen: set[str] = set()
    for rule in rules:
        if not isinstance(rule, Mapping) or set(rule) != {"paths", "commands"}:
            raise DeliveryError("targeted rule requires only paths and commands")
        patterns, commands = rule["paths"], rule["commands"]
        if (
            not isinstance(patterns, list)
            or not patterns
            or len(patterns) > MAX_RULE_VALUES
            or not isinstance(commands, list)
            or not commands
            or len(commands) > MAX_RULE_VALUES
        ):
            raise DeliveryError(
                "targeted rule paths and commands must be nonempty bounded lists"
            )
        for pattern in patterns:
            _relative_path(pattern, label="targeted pattern")
        if any(
            not isinstance(command, str) or not command.strip() or "\x00" in command
            for command in commands
        ):
            raise DeliveryError(
                "targeted commands must be nonempty shell command strings"
            )
        if any(fnmatchcase(path, pattern) for path in changed for pattern in patterns):
            for command in commands:
                if command not in seen:
                    selected.append(command)
                    seen.add(command)
    return selected
