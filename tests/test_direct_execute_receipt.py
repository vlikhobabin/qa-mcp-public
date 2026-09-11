from __future__ import annotations

from copy import deepcopy
import json
from threading import Barrier, Thread
from time import sleep

import pytest

from qa_mcp.direct_execute_receipt import CleanupIdentity, ReceiptError, ReceiptLease


HASHES = {char: char * 64 for char in "abcdef1239"}


def _payload(*, prompt: bool = False) -> tuple[dict, CleanupIdentity]:
    identity = CleanupIdentity(HASHES["a"], HASHES["b"], HASHES["c"], 15473, 11, 12, 12)
    observation = {
        "schema": "qa-mcp.hidden-direct-execute-observation.v1",
        "status": "exact_marker_topology_observed",
        "main_identity_hash": HASHES["a"],
        "expected_marker_hash": HASHES["b"],
        "topology_hash": HASHES["c"],
        "marker_match_count": 1,
        "control_count": 3,
        "action_count": 0,
        "raw_ui_retained": False,
    }
    prompt_receipt = None
    status = "exact_direct_execute_observed"
    if prompt:
        status = "exact_direct_execute_prompt_confirmed"
        prompt_receipt = {
            "Schema": "qa-mcp.hidden-prompt-admission-action.v1",
            "Status": "exact_prompt_confirmed_post_state_observed",
            "MainIdentityHash": HASHES["a"],
            "PromptIdentityHash": HASHES["d"],
            "PatternHash": HASHES["e"],
            "TopologyHash": HASHES["f"],
            "ActionPathHash": "2b6dd675bc3690a7d39c8d61adccb37aee8615934da718c8263f1b4d5286fe5f",
            "RootGeometryHash": HASHES["1"],
            "ActionGeometryHash": HASHES["2"],
            "ControlCount": 3,
            "InvokeCount": 1,
            "ValueCount": 0,
            "ActionAttempts": 1,
            "FocusCalls": 1,
            "KeyMessages": 2,
            "PromptClosed": True,
            "RawUIRetained": False,
        }
    return {
        "schema": "qa-mcp.internal-hidden-direct-execute-receipt.v1",
        "status": status,
        "cleanup": identity.as_dict(),
        "cleanup_identity_hash": identity.binding_hash(),
        "observation": observation,
        "prompt": prompt_receipt,
    }, identity


@pytest.mark.parametrize("prompt", [False, True])
def test_receipt_lease_binds_exact_prompt_outcomes(prompt: bool) -> None:
    payload, identity = _payload(prompt=prompt)
    lease = ReceiptLease.bind(payload, identity, set())
    calls: list[str] = []
    lease.stop(payload, lambda: calls.append("cleanup"))
    assert calls == ["cleanup"]


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("schema",), "changed"),
        (("status",), "changed"),
        (("cleanup_identity_hash",), "bad"),
        (("observation", "schema"), "changed"),
        (("observation", "status"), "changed"),
        (("observation", "control_count"), 0),
        (("observation", "control_count"), True),
        (("observation", "topology_hash"), "bad"),
        (("prompt", "Status"), "changed"),
        (("prompt", "ActionAttempts"), 0),
        (("prompt", "MainIdentityHash"), HASHES["9"]),
    ],
)
def test_receipt_rejects_malformed_schema_status_hash_count_and_type(path: tuple[str, ...], value: object) -> None:
    payload, identity = _payload(prompt=True)
    target = payload
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ReceiptError):
        ReceiptLease.bind(payload, identity, set())


def test_receipt_rejects_unknown_missing_and_foreign_cleanup_identity() -> None:
    payload, identity = _payload()
    unknown = deepcopy(payload)
    unknown["unexpected"] = 1
    missing = deepcopy(payload)
    del missing["cleanup"]["port"]
    foreign = CleanupIdentity(HASHES["9"], identity.worker_token_hash, identity.desktop_hash,
                              identity.port, identity.worker_pid, identity.child_pid, identity.listener_pid)
    for candidate, expected in [(unknown, identity), (missing, identity), (payload, foreign)]:
        with pytest.raises(ReceiptError):
            ReceiptLease.bind(candidate, expected, set())


def test_receipt_rejects_post_bind_mutation_and_shared_ledger_replay() -> None:
    payload, identity = _payload()
    consumed: set[str] = set()
    first = ReceiptLease.bind(payload, identity, consumed)
    second = ReceiptLease.bind(payload, identity, consumed)
    mutated = deepcopy(payload)
    mutated["observation"]["control_count"] += 1
    calls: list[str] = []
    with pytest.raises(ReceiptError):
        first.stop(mutated, lambda: calls.append("mutated"))
    first.stop(payload, lambda: calls.append("first"))
    with pytest.raises(ReceiptError):
        first.stop(payload, lambda: calls.append("repeat"))
    with pytest.raises(ReceiptError):
        second.stop(payload, lambda: calls.append("replay"))
    assert calls == ["first"]


def test_failed_cleanup_is_consumed_without_retry() -> None:
    payload, identity = _payload(prompt=True)
    lease = ReceiptLease.bind(payload, identity, set())
    calls: list[str] = []

    def fail() -> None:
        calls.append("failed")
        raise RuntimeError("typed cleanup failure")

    with pytest.raises(RuntimeError):
        lease.stop(payload, fail)
    with pytest.raises(ReceiptError):
        lease.stop(payload, lambda: calls.append("retry"))
    assert calls == ["failed"]


def test_cleanup_identity_uses_cross_language_canonical_hash() -> None:
    identity = CleanupIdentity(HASHES["a"], HASHES["b"], HASHES["c"], 15473, 11, 12, 12)
    assert identity.binding_hash() == "3ae48845756209ad1c84ab79906a090c4bd94126f7913731818ff320e6e5e79b"


@pytest.mark.parametrize("field", ["worker_pid", "child_pid", "listener_pid"])
@pytest.mark.parametrize("value", [0, True, 4294967296])
def test_cleanup_pid_rejects_values_outside_exact_go_uint32(field: str, value: object) -> None:
    payload, _ = _payload()
    payload["cleanup"][field] = value
    callbacks: list[str] = []
    rejected = False
    try:
        identity = CleanupIdentity.parse(payload["cleanup"])
        payload["cleanup_identity_hash"] = identity.binding_hash()
        ReceiptLease.bind(payload, identity, set()).stop(payload, lambda: callbacks.append("cleanup"))
    except ReceiptError:
        rejected = True
    assert rejected
    assert callbacks == []


def test_full_go_serialized_receipt_accepts_uint32_maximum_once() -> None:
    payload, _ = _payload()
    payload["cleanup"].update(worker_pid=4294967295, child_pid=4294967294, listener_pid=4294967294)
    identity = CleanupIdentity.parse(payload["cleanup"])
    payload["cleanup_identity_hash"] = identity.binding_hash()
    serialized = json.loads(json.dumps(payload))
    callbacks: list[str] = []
    ReceiptLease.bind(serialized, identity, set()).stop(serialized, lambda: callbacks.append("cleanup"))
    assert callbacks == ["cleanup"]


def test_concurrent_shared_ledger_invokes_cleanup_once() -> None:
    class SlowSet(set[str]):
        def __contains__(self, item: object) -> bool:
            present = super().__contains__(item)
            sleep(0.01)
            return present

    payload, identity = _payload()
    consumed: set[str] = SlowSet()
    leases = [ReceiptLease.bind(payload, identity, consumed) for _ in range(2)]
    start = Barrier(3)
    callbacks: list[str] = []

    def stop(lease: ReceiptLease) -> None:
        start.wait()
        try:
            lease.stop(payload, lambda: callbacks.append("cleanup"))
        except ReceiptError:
            pass

    threads = [Thread(target=stop, args=(lease,)) for lease in leases]
    for thread in threads:
        thread.start()
    start.wait()
    for thread in threads:
        thread.join()
    assert callbacks == ["cleanup"]
