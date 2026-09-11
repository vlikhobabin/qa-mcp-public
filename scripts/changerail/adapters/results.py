"""Project-owned result parsers behind shared retained-node proof checks.

The default adapter understands pytest. A project may configure
``[adapters.tests] module = '.changerail/adapters/test_results.py'``. That trusted
module must expose ``parse_results(log, command_identity, target)`` and return
actual terminal passing nodes mapped to complete-line byte spans. It owns the
test runner's command grammar and terminal status semantics. This wrapper owns
path confinement, output shape, selected-node identity and retained byte bounds;
the delivery kernel still owns receipt provenance and source assertions.
"""

from __future__ import annotations

import hashlib
import os
import stat
import types
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from scripts.changerail.adapters.pytest import (
    _final_receipt_nodes,
    _validate_pytest_selected_nodes,
)
from scripts.changerail.contracts import DeliveryError

MAX_ADAPTER_BYTES = 1024 * 1024
MAX_RESULT_NODES = 20000


def _module_source(root: Path, relative: object) -> tuple[Path, bytes]:
    if not isinstance(relative, str):
        raise DeliveryError("test result adapter module must be a repository path")
    path = Path(relative)
    if (
        path.is_absolute()
        or ".." in path.parts
        or path.suffix != ".py"
        or len(path.parts) < 3
        or path.parts[:2] != (".changerail", "adapters")
    ):
        raise DeliveryError(
            "test result adapter must reside under .changerail/adapters"
        )
    directory = -1
    try:
        directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        for part in path.parts[:-1]:
            child = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
            )
            os.close(directory)
            directory = child
        fd = os.open(
            path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_ADAPTER_BYTES:
                raise DeliveryError(
                    "test result adapter source is nonregular or oversized"
                )
            source = stream.read(MAX_ADAPTER_BYTES + 1)
            after = os.fstat(stream.fileno())
            attrs = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
            if (
                len(source) != before.st_size
                or len(source) > MAX_ADAPTER_BYTES
                or any(getattr(before, key) != getattr(after, key) for key in attrs)
            ):
                raise DeliveryError("test result adapter changed during read")
    except OSError as exc:
        raise DeliveryError(
            "test result adapter source is unsafe or unavailable"
        ) from exc
    finally:
        if directory >= 0:
            os.close(directory)
    return root / path, source


def _configured_module(profile: Mapping[str, Any]) -> object:
    adapters = profile.get("adapters", {})
    if not isinstance(adapters, Mapping):
        raise DeliveryError("adapters configuration must be a mapping")
    tests = adapters.get("tests", {})
    if not isinstance(tests, Mapping):
        raise DeliveryError("test adapter configuration must be a mapping")
    return tests.get("module")


def _matches_target(node: str, target: str) -> bool:
    return (
        node == target
        or node.startswith(target + "[")
        or ("::" not in target and node.startswith(target + "::"))
    )


def _custom_results(
    root: Path,
    module_path: object,
    log: bytes,
    identity: object,
    target: str,
) -> dict[str, tuple[int, int]]:
    if not isinstance(log, bytes) or not isinstance(target, str) or not target.strip():
        raise DeliveryError("test result adapter requires retained bytes and a target")
    if (
        not isinstance(identity, Mapping)
        or identity.get("kind") not in {"argv", "shell"}
        or not isinstance(identity.get("argv"), list)
        or not identity["argv"]
        or any(not isinstance(arg, str) or not arg for arg in identity["argv"])
    ):
        raise DeliveryError("test result adapter requires a command identity")
    path, source = _module_source(root, module_path)
    module = types.ModuleType(
        "changerail_project_results_" + hashlib.sha256(source).hexdigest()
    )
    module.__file__ = str(path)
    try:
        exec(compile(source, str(path), "exec"), module.__dict__)
        parser = getattr(module, "parse_results", None)
        if not callable(parser):
            raise DeliveryError("test result adapter has no parse_results callable")
        results = parser(log, identity, target)
    except DeliveryError:
        raise
    except Exception as exc:
        raise DeliveryError(
            "test result adapter failed to parse retained results"
        ) from exc
    if not isinstance(results, Mapping) or len(results) > MAX_RESULT_NODES:
        raise DeliveryError("test result adapter returned a malformed node mapping")
    checked: dict[str, tuple[int, int]] = {}
    for node, span in results.items():
        if (
            not isinstance(node, str)
            or not node.strip()
            or "\n" in node
            or "\r" in node
            or not isinstance(span, (tuple, list))
            or len(span) != 2
            or any(type(offset) is not int for offset in span)
        ):
            raise DeliveryError("test result adapter returned a malformed node span")
        start, end = span
        if (
            not 0 <= start < end <= len(log)
            or (start > 0 and log[start - 1 : start] != b"\n")
            or (end < len(log) and log[end : end + 1] not in {b"\r", b"\n"})
            or b"\n" in log[start:end]
            or b"\r" in log[start:end]
            or node.encode("utf-8") not in log[start:end]
        ):
            raise DeliveryError(
                "test result adapter node span does not bind a retained terminal line"
            )
        if _matches_target(node, target):
            checked[node] = (start, end)
    return checked


def validate_selected_nodes(
    root: Path,
    profile: Mapping[str, Any],
    log: bytes,
    identity: object,
    target: str,
    selected_nodes: object,
    label: str,
) -> dict[str, tuple[int, int]]:
    """Validate selected actual PASS nodes; aggregate/empty results cannot pass."""
    module = _configured_module(profile)
    if module is None:
        return _validate_pytest_selected_nodes(
            log, identity, target, selected_nodes, label=label
        )
    results = _custom_results(root, module, log, identity, target)
    if not isinstance(selected_nodes, list) or not selected_nodes or not results:
        raise DeliveryError(f"{label} has no current selected-node receipt")
    seen: set[str] = set()
    for row in selected_nodes:
        if (
            not isinstance(row, Mapping)
            or set(row) != {"node", "start", "end"}
            or not isinstance(row.get("node"), str)
            or type(row.get("start")) is not int
            or type(row.get("end")) is not int
        ):
            raise DeliveryError(f"{label} selected node is malformed")
        node = row["node"]
        if node in seen or results.get(node) != (row["start"], row["end"]):
            raise DeliveryError(f"{label} selected node is outside declared selector")
        seen.add(node)
    return results


def receipt_nodes(
    root: Path,
    profile: Mapping[str, Any],
    item: Mapping[str, Any],
    data: bytes,
    target: str,
) -> list[dict[str, Any]]:
    """Derive selected nodes only from terminal successful check observations."""
    if (
        item.get("state") != "terminal"
        or item.get("verdict") != "verified"
        or item.get("outcome") != "exit"
        or type(item.get("exit_code")) is not int
        or item["exit_code"] != 0
    ):
        return []
    module = _configured_module(profile)
    identity = item.get("command_identity")
    if module is None:
        nodes = _final_receipt_nodes(item, data, target)
        if nodes:
            _validate_pytest_selected_nodes(
                data, identity, target, nodes, label="test receipt"
            )
        return nodes
    return [
        {"node": node, "start": start, "end": end}
        for node, (start, end) in _custom_results(
            root, module, data, identity, target
        ).items()
    ]
