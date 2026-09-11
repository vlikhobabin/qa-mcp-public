"""Guard the aliasing risk introduced by sharing mutable profile builders."""

from pathlib import Path

from tests.support.runtime_targets import TargetProfileInputs


def test_profile_mutation_cannot_repair_its_observation_or_leak_to_next_case(tmp_path: Path) -> None:
    inputs = TargetProfileInputs(tmp_path, fingerprint="declared-target")
    profile = inputs.profile()
    profile["target"]["fingerprint"]["value"] = "foreign-target"
    profile["evidence"]["non_production_approved"] = True
    env = inputs.handoff_env()
    env["AI1C_RUNTIME_TARGET_FINGERPRINT"] = "foreign-target"

    assert profile["observation"]["target_fingerprint"]["value"] == "declared-target"
    fresh = inputs.profile()
    assert fresh["target"]["fingerprint"]["value"] == "declared-target"
    assert fresh["evidence"]["non_production_approved"] is False
    assert inputs.handoff_env()["AI1C_RUNTIME_TARGET_FINGERPRINT"] == "declared-target"
