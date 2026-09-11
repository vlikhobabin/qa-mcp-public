"""Public immutable runtime-target contract and packaged schema."""

from __future__ import annotations

import copy
import json
from dataclasses import FrozenInstanceError
from importlib.resources import files
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from qa_mcp.core import (
    EvidencePolicy,
    ProviderTargetProfile,
    RuntimeFingerprint,
    RuntimeTargetBinding,
    RuntimeTargetBindingError,
    RuntimeTargetObservation,
    TargetIdentity,
)


def _fingerprint(value: str) -> RuntimeFingerprint:
    return RuntimeFingerprint("sha256", value)


def _observation() -> RuntimeTargetObservation:
    return RuntimeTargetObservation(
        target_id="project-demo",
        target_kind="file-infobase",
        target_fingerprint=_fingerprint("target"),
        effective_principal_fingerprint=_fingerprint("principal"),
        platform_fingerprint=_fingerprint("platform"),
        extension_profile_fingerprint=_fingerprint("extensions"),
        process_config_fingerprint=_fingerprint("process"),
        security_receipt_id="receipt-7",
        binding_generation=7,
    )


def test_public_contract_is_immutable_and_provider_neutral(tmp_path: Path) -> None:
    observation = _observation()
    target = TargetIdentity("project-demo", "sha256:target")
    profile = ProviderTargetProfile(
        binding_ref="qa-demo",
        target_id=target.logical_id,
        target_kind="file-infobase",
        canonical_target_kind="file",
        target_fingerprint=_fingerprint("target"),
        physical_env_file=tmp_path / "target.env",
        evidence_policy=EvidencePolicy.SANITIZED,
        evidence_root=tmp_path / "evidence",
        observation=observation,
    )
    binding = RuntimeTargetBinding(
        target=target,
        target_kind="file",
        declared_target_kind="file-infobase",
        binding_ref="qa-demo",
        principal_id="qa-agent",
        expected_principal_fingerprint=_fingerprint("principal"),
        binding_generation=7,
        provider_observations_ref=".ai/runtime-provider-observations.json",
        security_receipt_id="receipt-7",
        evidence_policy=EvidencePolicy.SANITIZED,
        evidence_root=tmp_path / "evidence",
    )
    assert binding.target.logical_id == "project-demo"
    assert profile.evidence_policy is EvidencePolicy.SANITIZED
    assert observation.to_dict()["provider_id"] == "qa-mcp"
    with pytest.raises(FrozenInstanceError):
        binding.binding_generation = 8  # type: ignore[misc]


def test_runtime_fingerprint_normalizes_and_rejects_unsafe_values() -> None:
    fingerprint = RuntimeFingerprint.from_mapping(
        {"algorithm": " sha256 ", "value": " digest "}, field="target"
    )
    assert fingerprint.scalar == "sha256:digest"
    assert fingerprint.to_dict() == {"algorithm": "sha256", "value": "digest"}

    with pytest.raises(RuntimeTargetBindingError) as excinfo:
        RuntimeFingerprint.from_values("sha256", "two words", field="target")
    assert excinfo.value.code == "runtime-target-fingerprint-invalid"


def test_packaged_profile_schema_is_closed_and_complete() -> None:
    schema_path = files("qa_mcp").joinpath(
        "schemas/qa-mcp-runtime-target-profile.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    assert schema["$schema"].endswith("2020-12/schema")
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {
        "schema", "binding_ref", "target", "physical_config", "evidence", "observation"
    }
    assert schema["properties"]["target"]["$ref"] == "#/$defs/target"
    assert schema["properties"]["evidence"]["additionalProperties"] is False
    assert set(schema["properties"]["evidence"]["properties"]["policy"]["enum"]) == {
        "sanitized", "full_local"
    }
    assert schema["properties"]["observation"]["additionalProperties"] is False

    profile = {
        "schema": "qa-mcp.runtime-target-profile.v1",
        "binding_ref": "qa-demo",
        "target": {
            "id": "project-demo",
            "kind": "file-infobase",
            "fingerprint": {"algorithm": "sha256", "value": "target"},
        },
        "physical_config": {"env_file": "/ignored/project-target.env"},
        "evidence": {
            "policy": "sanitized",
            "root": "/ignored/evidence",
            "non_production_approved": True,
        },
        "observation": {
            "target_id": "project-demo",
            "target_kind": "file-infobase",
            "target_fingerprint": {"algorithm": "sha256", "value": "target"},
            "effective_principal_fingerprint": {
                "algorithm": "sha256",
                "value": "principal",
            },
            "platform_fingerprint": {"algorithm": "sha256", "value": "platform"},
            "extension_profile_fingerprint": {
                "algorithm": "sha256",
                "value": "extensions",
            },
            "process_config_fingerprint": {"algorithm": "sha256", "value": "process"},
            "security_receipt_id": "receipt-7",
            "binding_generation": 7,
        },
    }
    validator = Draft202012Validator(schema)
    assert list(validator.iter_errors(profile)) == []

    incomplete = {key: value for key, value in profile.items() if key != "observation"}
    assert any(error.validator == "required" for error in validator.iter_errors(incomplete))

    unknown = {**profile, "connection_string": "must-not-be-accepted"}
    assert any(
        error.validator == "additionalProperties" for error in validator.iter_errors(unknown)
    )

    nested_cases = (
        (["target"], "connection_string", "unexpected", "additionalProperties"),
        (["target"], "fingerprint", None, "required"),
        (["target", "fingerprint"], "secret", "unexpected", "additionalProperties"),
        (["target", "fingerprint"], "value", None, "required"),
        (["physical_config"], "connection_string", "unexpected", "additionalProperties"),
        (["physical_config"], "env_file", None, "required"),
        (["evidence"], "credential", "unexpected", "additionalProperties"),
        (["evidence"], "policy", None, "required"),
        (["observation"], "credential", "unexpected", "additionalProperties"),
        (["observation"], "security_receipt_id", None, "required"),
        (
            ["observation", "target_fingerprint"],
            "secret",
            "unexpected",
            "additionalProperties",
        ),
        (["observation", "target_fingerprint"], "value", None, "required"),
    )
    for object_path, field, replacement, expected_validator in nested_cases:
        invalid = copy.deepcopy(profile)
        nested = invalid
        for segment in object_path:
            nested = nested[segment]
        if replacement is None:
            del nested[field]
        else:
            nested[field] = replacement
        assert any(
            error.validator == expected_validator
            and list(error.absolute_path) == object_path
            for error in validator.iter_errors(invalid)
        ), (object_path, field, expected_validator)
