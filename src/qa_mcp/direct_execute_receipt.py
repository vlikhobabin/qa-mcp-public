"""Dormant internal typed receipt and single-use cleanup binding for S6."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from threading import Lock
from typing import Any, Callable, MutableSet

_SCHEMA = "qa-mcp.internal-hidden-direct-execute-receipt.v1"
_OBSERVED = "exact_direct_execute_observed"
_PROMPT_CONFIRMED = "exact_direct_execute_prompt_confirmed"
_ACTION_PATH = "2b6dd675bc3690a7d39c8d61adccb37aee8615934da718c8263f1b4d5286fe5f"
_CONSUMED_LOCK = Lock()


class ReceiptError(ValueError):
    """The internal receipt is not exact, current-run bound, or unused."""


def _hash(value: Any) -> bool:
    return type(value) is str and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _integer(value: Any, minimum: int = 0, maximum: int | None = None) -> bool:
    return type(value) is int and value >= minimum and (maximum is None or value <= maximum)


def _exact(value: Any, keys: set[str]) -> dict[str, Any]:
    if type(value) is not dict or set(value) != keys:
        raise ReceiptError("receipt shape is invalid")
    return value


@dataclass(frozen=True)
class CleanupIdentity:
    run_id_hash: str
    worker_token_hash: str
    desktop_hash: str
    port: int
    worker_pid: int
    child_pid: int
    listener_pid: int

    def __post_init__(self) -> None:
        if not all(_hash(value) for value in (self.run_id_hash, self.worker_token_hash, self.desktop_hash)) or not (
            _integer(self.port, 1, 65535) and _integer(self.worker_pid, 1, 4294967295)
            and _integer(self.child_pid, 1, 4294967295) and _integer(self.listener_pid, 1, 4294967295)
            and self.worker_pid != self.child_pid
        ):
            raise ReceiptError("cleanup identity is invalid")

    def as_dict(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}

    def binding_hash(self) -> str:
        fields = (self.run_id_hash, self.worker_token_hash, self.desktop_hash, self.port,
                  self.worker_pid, self.child_pid, self.listener_pid)
        return hashlib.sha256("|".join(map(str, fields)).encode()).hexdigest()

    @classmethod
    def parse(cls, value: Any) -> CleanupIdentity:
        data = _exact(value, set(cls.__dataclass_fields__))
        try:
            return cls(**data)
        except TypeError as exc:
            raise ReceiptError("cleanup identity fields are invalid") from exc


def _validate_observation(value: Any) -> str:
    data = _exact(value, {"schema", "status", "main_identity_hash", "expected_marker_hash", "topology_hash",
                          "marker_match_count", "control_count", "action_count", "raw_ui_retained"})
    valid = (
        data["schema"] == "qa-mcp.hidden-direct-execute-observation.v1"
        and data["status"] == "exact_marker_topology_observed"
        and all(_hash(data[name]) for name in ("main_identity_hash", "expected_marker_hash", "topology_hash"))
        and data["marker_match_count"] == 1 and _integer(data["marker_match_count"], 1, 1)
        and _integer(data["control_count"], 1, 512) and _integer(data["action_count"], 0, 0)
        and type(data["raw_ui_retained"]) is bool and not data["raw_ui_retained"]
    )
    if not valid:
        raise ReceiptError("observation receipt is invalid")
    return data["main_identity_hash"]


def _validate_prompt(value: Any, main_hash: str) -> None:
    keys = {"Schema", "Status", "MainIdentityHash", "PromptIdentityHash", "PatternHash", "TopologyHash",
            "ActionPathHash", "RootGeometryHash", "ActionGeometryHash", "ControlCount", "InvokeCount",
            "ValueCount", "ActionAttempts", "FocusCalls", "KeyMessages", "PromptClosed", "RawUIRetained"}
    data = _exact(value, keys)
    hashes = ("MainIdentityHash", "PromptIdentityHash", "PatternHash", "TopologyHash", "ActionPathHash",
              "RootGeometryHash", "ActionGeometryHash")
    valid = (
        data["Schema"] == "qa-mcp.hidden-prompt-admission-action.v1"
        and data["Status"] == "exact_prompt_confirmed_post_state_observed"
        and all(_hash(data[name]) for name in hashes) and data["MainIdentityHash"] == main_hash
        and data["ActionPathHash"] == _ACTION_PATH and _integer(data["ControlCount"], 1, 128)
        and _integer(data["InvokeCount"], 1, data["ControlCount"])
        and _integer(data["ValueCount"], 0, data["ControlCount"])
        and all(_integer(data[name], wanted, wanted) for name, wanted in
                (("ActionAttempts", 1), ("FocusCalls", 1), ("KeyMessages", 2)))
        and type(data["PromptClosed"]) is bool and data["PromptClosed"]
        and type(data["RawUIRetained"]) is bool and not data["RawUIRetained"]
    )
    if not valid:
        raise ReceiptError("prompt receipt is invalid")


def _admit(value: Any, expected: CleanupIdentity) -> str:
    data = _exact(value, {"schema", "status", "cleanup", "cleanup_identity_hash", "observation", "prompt"})
    cleanup = CleanupIdentity.parse(data["cleanup"])
    if data["schema"] != _SCHEMA or cleanup != expected or data["cleanup_identity_hash"] != expected.binding_hash():
        raise ReceiptError("receipt cleanup identity is stale or foreign")
    main_hash = _validate_observation(data["observation"])
    if data["prompt"] is None:
        if data["status"] != _OBSERVED:
            raise ReceiptError("prompt-free receipt status is invalid")
    else:
        if data["status"] != _PROMPT_CONFIRMED:
            raise ReceiptError("prompt receipt status is invalid")
        _validate_prompt(data["prompt"], main_hash)
    return data["cleanup_identity_hash"]


def _fingerprint(value: Any) -> str:
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise ReceiptError("receipt is not canonical JSON") from exc
    return hashlib.sha256(encoded.encode()).hexdigest()


class ReceiptLease:
    def __init__(self, expected: CleanupIdentity, binding: str, fingerprint: str, consumed: MutableSet[str]) -> None:
        self._expected, self._binding, self._fingerprint, self._consumed = expected, binding, fingerprint, consumed

    @classmethod
    def bind(cls, value: Any, expected: CleanupIdentity, consumed: MutableSet[str]) -> ReceiptLease:
        if not isinstance(consumed, MutableSet):
            raise ReceiptError("consumed-binding ledger is unavailable")
        binding = _admit(value, expected)
        with _CONSUMED_LOCK:
            if binding in consumed:
                raise ReceiptError("cleanup identity was already consumed")
        return cls(expected, binding, _fingerprint(value), consumed)

    def stop(self, value: Any, cleanup: Callable[[], Any]) -> Any:
        if not callable(cleanup) or _fingerprint(value) != self._fingerprint or _admit(value, self._expected) != self._binding:
            raise ReceiptError("stop receipt is stale or changed")
        with _CONSUMED_LOCK:
            if self._binding in self._consumed:
                raise ReceiptError("cleanup identity was already consumed")
            self._consumed.add(self._binding)
        return cleanup()
