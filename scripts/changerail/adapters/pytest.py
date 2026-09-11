"""Validate pytest command identities and retained terminal node evidence."""

from __future__ import annotations

import re
import shlex
from pathlib import Path
from typing import Any, Mapping

from scripts.changerail.contracts import DeliveryError


def _is_pytest_command_identity(identity: object) -> bool:
    """Recognize a supported pytest invocation without executing it.

    This is deliberately a small command grammar, not executable
    authentication: a same-user binary named ``pytest`` is outside the proof
    this structural reader can make. It does prevent a receipt whose command
    merely *mentions* pytest from turning arbitrary printed text into a test
    observation.
    """

    if not isinstance(identity, Mapping):
        return False
    kind = identity.get("kind")
    if kind == "argv":
        if set(identity) != {"kind", "argv"} or not isinstance(
            identity.get("argv"), list
        ):
            return False
        argv = identity["argv"]
    elif kind == "shell":
        if set(identity) != {"kind", "argv", "shell_text"} or not isinstance(
            identity.get("shell_text"), str
        ):
            return False
        supplied_argv = identity.get("argv")
        if not isinstance(supplied_argv, list) or not all(
            isinstance(value, str) and value for value in supplied_argv
        ):
            return False
        shell_text = identity["shell_text"]
        # Shell grammar (pipes, redirects, substitutions, expansions, command
        # lists) cannot identify one executed pytest process. Refuse it rather
        # than treating a later token as an invocation.
        if not shell_text or re.search(r"[\n\r;|&<>$`]", shell_text):
            return False
        if supplied_argv != ["bash", "-lc", shell_text]:
            return False
        try:
            argv = shlex.split(shell_text)
        except ValueError:
            return False
    else:
        return False
    if not argv or not all(isinstance(value, str) and value for value in argv):
        return False
    executable = Path(argv[0]).name
    if re.fullmatch(r"pytest(?:-[0-9]+(?:\.[0-9]+)*)?", executable):
        return True
    if re.fullmatch(r"python(?:[0-9]+(?:\.[0-9]+)*)?", executable):
        return len(argv) >= 3 and argv[1:3] == ["-m", "pytest"]
    if executable == "uv" and len(argv) >= 3 and argv[1] == "run":
        nested = argv[2:]
        nested_executable = Path(nested[0]).name
        return re.fullmatch(
            r"pytest(?:-[0-9]+(?:\.[0-9]+)*)?", nested_executable
        ) is not None or (
            re.fullmatch(r"python(?:[0-9]+(?:\.[0-9]+)*)?", nested_executable)
            is not None
            and len(nested) >= 3
            and nested[1:3] == ["-m", "pytest"]
        )
    return False


def _validate_pytest_selected_nodes(
    log: bytes,
    command_identity: object,
    target: str,
    selected_nodes: object,
    *,
    label: str,
) -> dict[str, tuple[int, int]]:
    """Bind selected pytest terminal lines to one declared test locator.

    Both measured receipts and ordinary offline reports use this parser.  It
    validates retained bytes only; it never launches a command or treats an
    exit code/aggregate summary as a selected-node observation.
    """

    declared_file, separator, _selector = target.partition("::")
    if not declared_file.endswith(".py") or not _is_pytest_command_identity(
        command_identity
    ):
        raise DeliveryError(f"{label} has no declared pytest selector")
    if not isinstance(selected_nodes, list) or not selected_nodes:
        raise DeliveryError(f"{label} has no current selected-node receipt")
    passed = _final_receipt_node_spans(log)
    seen: set[str] = set()
    for selected in selected_nodes:
        if (
            not isinstance(selected, Mapping)
            or set(selected) != {"node", "start", "end"}
            or not isinstance(selected.get("node"), str)
            or not selected["node"]
            or type(selected.get("start")) is not int
            or type(selected.get("end")) is not int
        ):
            raise DeliveryError(f"{label} selected node is malformed")
        node, start, end = selected["node"], selected["start"], selected["end"]
        if (
            node in seen
            or not _node_matches_target(node, declared_file, separator, target)
            or (start, end) != passed.get(node)
        ):
            raise DeliveryError(f"{label} selected node is outside declared selector")
        seen.add(node)
    return passed


def _node_matches_target(
    node: str, declared_file: str, separator: str, target: str
) -> bool:
    return (
        (node == declared_file or node.startswith(declared_file + "::"))
        if not separator
        else (node == target or node.startswith(target + "["))
    )


def _final_receipt_node_spans(data: bytes) -> dict[str, tuple[int, int]]:
    """Parse terminal pytest lines in byte coordinates, including Unicode ids."""

    passed: dict[str, tuple[int, int]] = {}
    for match in re.finditer(
        rb"(?m)^(?P<node>.+?)[ \t]+PASSED(?:[ \t]+\[[^\r\n]*\])?[ \t]*$", data
    ):
        try:
            node = match.group("node").decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise DeliveryError("final pytest node is not UTF-8") from exc
        if ".py" in node:
            passed[node] = (match.start(), match.end())
    return passed


def _final_receipt_nodes(
    item: Mapping[str, Any], data: bytes, target: str
) -> list[dict[str, Any]]:
    """Return only terminal PASS lines genuinely selected by a declared test locator."""

    declared_file, separator, _selector = target.partition("::")
    if not declared_file.endswith(".py"):
        return []
    matches: list[dict[str, Any]] = []
    for node, (start, end) in _final_receipt_node_spans(data).items():
        allowed = _node_matches_target(node, declared_file, separator, target)
        if allowed:
            matches.append({"node": node, "start": start, "end": end})
    return matches
