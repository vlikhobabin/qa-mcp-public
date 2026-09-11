"""Reviewed installed predecessor bytes and their supported checkpoint semantics.

Only these complete upstream payloads may inherit completed implementation groups.
Version labels and self-consistent installation locks are insufficient authority.
The pre-release candidate is explicitly distinct from the published release tags.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import distribution as dist
from scripts.changerail.contracts import DeliveryError

CHECKPOINT_POLICY = (
    "openspec-v1.exact-groups.checked-tasks.current-focused.shared-two-review.v1"
)
# Reviewed functions: require_group/checkpoint, _card_contract/plan_identity,
# artifact_identity, combined_change_events/validate_change_event_prefix,
# change_checkpoint_statuses and review_budget_usage. Candidate.5 -> rc.1 diffs
# preserve these functions exactly; archive reconciliation differences are outside
# this transition's supported pre-archive boundary. rc.1 -> rc.2 is documentation.
CHECKPOINT_SEMANTICS = {
    "event_schema": "changerail.delivery-phase-event.v1",
    "events": "contiguous numbered group starting/complete prefix",
    "completion": "checked tasks in the assigned group and current focused proof",
    "task_identity": "exact normalized artifact hashes; only checkbox state mutable",
    "card_identity": "all sections except Status/Result/Log frozen, including Next",
    "inherited_evidence": "historical only; obtain fresh payload-bound proofs",
    "review_allowance": "at most two completed independent reviews across lineage",
    "boundary": "stopped implementation or completed NO-GO; no archive/final/publication",
}

REVIEWED_PAYLOADS = {
    "c54a64ecefbe05ec7cd697f677dc7cdcb50669233083de30323fad0bf164b055": {
        "archive_sha256": "e457c000bdb1921c2e5f40c0f4f2b4270e2d271d1dbdf2aea17c2c0fd8071911",
        "checkpoint_policy": "openspec-v1.exact-groups.checked-tasks.current-focused.shared-two-review.v1",
        "critical_sha256": {
            "scripts/changerail/local_delivery.py": "a4d43105b1216706e53bc783adb040bed8e9ac10430f7bb15d4a48c24b6dc5ea",
            "scripts/changerail/native_workflow.py": "34a17701f7aa20f9224576d8003d5d7e683532120ebfc082a48ba356d2ff0466",
            "scripts/changerail/openspec_adapter.py": "94befa609dabfad075291e47d04c2c37fb623450944f1e7783492d5a9b91f137",
            "scripts/changerail/openspec_context.py": "d847ca3748911177253dc89f8c7e2aa13e4231aa14a05e4fb2fd1fdeb1d2e8a1",
        },
        "identity_shape": "installed-legacy",
        "provenance": "reviewed "
        "pre-release "
        "source "
        "candidate; "
        "not a "
        "published "
        "GitHub tag",
        "version": "2.0.0-candidate.5",
    },
    "c609d5f00771258816b80967375d90929d779fcab43e0e69ff41c55ab9228da9": {
        "archive_sha256": "36c80bf34dfe4b85673e2e1ca84f6766b64d6ac3db95b4614624093cb560216e",
        "checkpoint_policy": "openspec-v1.exact-groups.checked-tasks.current-focused.shared-two-review.v1",
        "critical_sha256": {
            "scripts/changerail/local_delivery.py": "e231cce5c3358d344c4c76f5706ba4c9e540ccfd93ae753adf35a1260cde0dbb",
            "scripts/changerail/native_workflow.py": "5231e570832f676a062cfe4408801db3d4a13ef251bfa738cd5c4593e240f647",
            "scripts/changerail/openspec_adapter.py": "651509619bdcd3d8fa1d96efeb340c3195825325b9573cd11a2cb3327543254e",
            "scripts/changerail/openspec_context.py": "d847ca3748911177253dc89f8c7e2aa13e4231aa14a05e4fb2fd1fdeb1d2e8a1",
        },
        "identity_shape": "installed-expanded",
        "provenance": "GitHub release tag v2.0.0-rc.1",
        "version": "2.0.0-rc.1",
    },
    "fce3c4f48295d4fd8d3ec3fc8f86b8cf7e5ace99656001ff2ba1b92f53b1cad5": {
        "archive_sha256": "28aa0d639fa8581cc37c03e8a03b7034123504ac6649f237d8df41ef70a0968a",
        "checkpoint_policy": "openspec-v1.exact-groups.checked-tasks.current-focused.shared-two-review.v1",
        "critical_sha256": {
            "scripts/changerail/local_delivery.py": "e231cce5c3358d344c4c76f5706ba4c9e540ccfd93ae753adf35a1260cde0dbb",
            "scripts/changerail/native_workflow.py": "5231e570832f676a062cfe4408801db3d4a13ef251bfa738cd5c4593e240f647",
            "scripts/changerail/openspec_adapter.py": "651509619bdcd3d8fa1d96efeb340c3195825325b9573cd11a2cb3327543254e",
            "scripts/changerail/openspec_context.py": "d847ca3748911177253dc89f8c7e2aa13e4231aa14a05e4fb2fd1fdeb1d2e8a1",
        },
        "identity_shape": "installed-expanded",
        "provenance": "GitHub release tag v2.0.0-rc.2",
        "version": "2.0.0-rc.2",
    },
}


def require_reviewed_payload(lock: dict[str, Any]) -> dict[str, Any]:
    descriptor = REVIEWED_PAYLOADS.get(lock.get("payload_sha256"))
    if (
        descriptor is None
        or lock.get("schema") != "changerail.installation.v1"
        or lock.get("execution_contract") != "changerail.native.v1"
        or lock.get("version") != descriptor["version"]
        or lock.get("archive_sha256") != descriptor["archive_sha256"]
        or descriptor.get("checkpoint_policy") != CHECKPOINT_POLICY
        or descriptor.get("identity_shape")
        not in {"installed-legacy", "installed-expanded"}
        or dist.digest(dist.encoded(lock.get("files", {})))
        != lock.get("payload_sha256")
        or any(
            lock.get("files", {}).get(name, {}).get("sha256") != digest
            for name, digest in descriptor["critical_sha256"].items()
        )
    ):
        raise DeliveryError(
            "installed compatibility requires an exact reviewed source payload and checkpoint policy"
        )
    return {
        "payload_sha256": lock["payload_sha256"],
        **deepcopy(descriptor),
        "checkpoint_semantics": deepcopy(CHECKPOINT_SEMANTICS),
    }
