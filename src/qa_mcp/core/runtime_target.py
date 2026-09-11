"""Public immutable contract for a declared project runtime target."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from .contracts import TargetIdentity

RUNTIME_TARGET_PROFILE_ENV = "QA_MCP_RUNTIME_TARGET_PROFILE"
RUNTIME_EVIDENCE_ALLOW_ROOT_ENV = "QA_MCP_RUNTIME_EVIDENCE_ALLOW_ROOT"
RUNTIME_OBSERVATIONS_REF = ".ai/runtime-provider-observations.json"
RUNTIME_PROFILE_SCHEMA = "qa-mcp.runtime-target-profile.v1"
RUNTIME_OBSERVATION_SCHEMA = "ai1c.provider-runtime-target-observation.v1"

_BINDING_REF_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,63}$")
_RESOLUTION_VALIDATION_SEAL = object()
_KIND_ALIASES = {
    "file": "file",
    "file-infobase": "file",
    "file_infobase": "file",
    "client-server": "client-server",
    "client-server-infobase": "client-server",
    "client_server": "client-server",
}
_HANDOFF_FIELDS = {
    "AI1C_RUNTIME_TARGET_ID",
    "AI1C_RUNTIME_TARGET_KIND",
    "AI1C_RUNTIME_TARGET_FINGERPRINT",
    "AI1C_RUNTIME_TARGET_FINGERPRINT_ALGORITHM",
    "AI1C_AGENT_PRINCIPAL_ID",
    "AI1C_AGENT_EXPECTED_PRINCIPAL_FINGERPRINT",
    "AI1C_AGENT_EXPECTED_PRINCIPAL_FINGERPRINT_ALGORITHM",
    "AI1C_AGENT_TEST_SECURITY_RECEIPT_ID",
    "AI1C_RUNTIME_TARGET_BINDING_GENERATION",
    "AI1C_RUNTIME_TARGET_OBSERVATIONS",
    "AI1C_RUNTIME_TARGET_BINDING_REF",
}


class RuntimeTargetBindingError(ValueError):
    """Secret-safe target binding failure with a stable diagnostic code."""

    def __init__(self, code: str, field: str, message: str) -> None:
        self.code = code
        self.field = field
        super().__init__(f"{code}: {field}: {message}")


class EvidencePolicy(str, Enum):
    SANITIZED = "sanitized"
    FULL_LOCAL = "full_local"


@dataclass(frozen=True)
class RuntimeFingerprint:
    algorithm: str
    value: str

    @classmethod
    def from_values(cls, algorithm: Any, value: Any, *, field: str) -> "RuntimeFingerprint":
        normalized_algorithm = _required_text(algorithm, f"{field}.algorithm")
        normalized_value = _required_text(value, f"{field}.value")
        if any(char.isspace() for char in normalized_algorithm + normalized_value):
            raise RuntimeTargetBindingError("runtime-target-fingerprint-invalid", field,
                                            "fingerprint must not contain whitespace")
        return cls(normalized_algorithm, normalized_value)

    @classmethod
    def from_mapping(cls, value: Any, *, field: str) -> "RuntimeFingerprint":
        item = _closed_mapping(value, {"algorithm", "value"}, field)
        return cls.from_values(item["algorithm"], item["value"], field=field)

    @property
    def scalar(self) -> str:
        return f"{self.algorithm}:{self.value}"

    def to_dict(self) -> dict[str, str]:
        return {"algorithm": self.algorithm, "value": self.value}


@dataclass(frozen=True)
class RuntimeTargetBinding:
    target: TargetIdentity
    target_kind: str
    declared_target_kind: str
    binding_ref: str
    principal_id: str
    expected_principal_fingerprint: RuntimeFingerprint
    binding_generation: int
    provider_observations_ref: str
    security_receipt_id: str
    evidence_policy: EvidencePolicy
    evidence_root: Path


@dataclass(frozen=True)
class RuntimeTargetObservation:
    target_id: str
    target_kind: str
    target_fingerprint: RuntimeFingerprint
    effective_principal_fingerprint: RuntimeFingerprint
    platform_fingerprint: RuntimeFingerprint
    extension_profile_fingerprint: RuntimeFingerprint
    process_config_fingerprint: RuntimeFingerprint
    security_receipt_id: str
    binding_generation: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": RUNTIME_OBSERVATION_SCHEMA,
            "provider_id": "qa-mcp",
            "target_id": self.target_id,
            "target_kind": self.target_kind,
            "target_fingerprint": self.target_fingerprint.to_dict(),
            "effective_principal_fingerprint": self.effective_principal_fingerprint.to_dict(),
            "platform_fingerprint": self.platform_fingerprint.to_dict(),
            "extension_profile_fingerprint": self.extension_profile_fingerprint.to_dict(),
            "process_config_fingerprint": self.process_config_fingerprint.to_dict(),
            "security_receipt_id": self.security_receipt_id,
            "binding_generation": self.binding_generation,
        }


@dataclass(frozen=True)
class ProviderTargetProfile:
    binding_ref: str
    target_id: str
    target_kind: str
    canonical_target_kind: str
    target_fingerprint: RuntimeFingerprint
    physical_env_file: Path
    evidence_policy: EvidencePolicy
    evidence_root: Path
    observation: RuntimeTargetObservation


@dataclass(frozen=True)
class _ProviderPhysicalConfig:
    """Private, typed physical values admitted with a runtime resolution."""

    infobase_path: str
    connection_string: str
    platform_root: str
    test_client_kind: str
    test_client_user: str
    test_client_password: str
    source_root: str


@dataclass(frozen=True)
class RuntimeTargetResolution:
    binding: RuntimeTargetBinding
    profile: ProviderTargetProfile
    observation: RuntimeTargetObservation
    _physical_config: _ProviderPhysicalConfig = field(repr=False, compare=False)
    _validation_seal: object | None = field(default=None, init=False, repr=False, compare=False)


def validate_runtime_target_resolution(
    resolution: RuntimeTargetResolution,
) -> RuntimeTargetResolution:
    """Admit only values produced after the resolver's full validation chain."""

    if (
        not isinstance(resolution, RuntimeTargetResolution)
        or resolution._validation_seal is not _RESOLUTION_VALIDATION_SEAL
    ):
        raise RuntimeTargetBindingError(
            "runtime-target-mismatch", "resolution", "provider resolution is not validated"
        )
    return resolution


def runtime_target_readiness(
    resolution: RuntimeTargetResolution | None,
) -> dict[str, Any]:
    """Serialize validated target readiness without provider-local values."""

    if resolution is None:
        return {"active": False, "ok": True, "state": "unbound"}
    validated = validate_runtime_target_resolution(resolution)
    binding = validated.binding
    observation = validated.observation
    return {
        "active": True,
        "ok": True,
        "state": "ready",
        "target": {
            "logical_id": binding.target.logical_id,
            "kind": binding.target_kind,
            "fingerprint": binding.target.fingerprint,
            "binding_ref": binding.binding_ref,
            "binding_generation": binding.binding_generation,
        },
        "evidence": {"policy": binding.evidence_policy.value},
        "observation": {
            "status": "matched",
            "effective_principal_fingerprint": (
                observation.effective_principal_fingerprint.scalar
            ),
            "platform_fingerprint": observation.platform_fingerprint.scalar,
            "extension_profile_fingerprint": (
                observation.extension_profile_fingerprint.scalar
            ),
            "process_config_fingerprint": observation.process_config_fingerprint.scalar,
        },
    }


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeTargetBindingError("runtime-target-profile-invalid", field,
                                        "must be a non-empty string")
    return value.strip()


def _closed_mapping(value: Any, keys: set[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise RuntimeTargetBindingError("runtime-target-profile-invalid", field,
                                        "must use the closed provider-profile schema")
    return value


def _canonical_kind(value: Any, *, field: str) -> tuple[str, str]:
    declared = _required_text(value, field)
    canonical = _KIND_ALIASES.get(declared)
    if canonical is None:
        raise RuntimeTargetBindingError("runtime-target-kind-invalid", field,
                                        "target kind is unsupported")
    return declared, canonical


def _positive_generation(value: Any, *, field: str, allow_text: bool = False) -> int:
    generation = None
    if isinstance(value, int) and not isinstance(value, bool):
        generation = value
    elif allow_text and isinstance(value, str) and value.isdecimal():
        try:
            generation = int(value)
        except ValueError:
            pass
    if generation is None or generation < 1:
        raise RuntimeTargetBindingError("runtime-target-generation-invalid", field,
                                        "must be a positive integer")
    return generation


def _local_path(path_value: Any, *, field: str, kind: str = "path",
                code: str = "runtime-target-profile-invalid") -> Path:
    resolved = None
    try:
        path = Path(_required_text(path_value, field)).expanduser().absolute()
        if not any(candidate.is_symlink() for candidate in (path, *path.parents)):
            resolved = path.resolve()
    except (OSError, RuntimeError, ValueError):
        pass
    if resolved is None:
        raise RuntimeTargetBindingError(code, field, "must be a safe local path")
    try:
        valid = kind == "path" or (kind == "file" and resolved.is_file()) or (kind == "dir" and resolved.is_dir())
    except OSError:
        valid = False
    if not valid:
        raise RuntimeTargetBindingError(code, field, f"must reference an existing local {kind}")
    return resolved


def _profile_from_path(path_value: str, allowed_root_value: str) -> ProviderTargetProfile:
    path = _local_path(path_value, field=RUNTIME_TARGET_PROFILE_ENV, kind="file")
    data = None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, RecursionError, json.JSONDecodeError):
        pass
    if data is None:
        raise RuntimeTargetBindingError("runtime-target-profile-invalid",
                                        RUNTIME_TARGET_PROFILE_ENV, "profile is not valid JSON")
    item = _closed_mapping(
        data,
        {"schema", "binding_ref", "target", "physical_config", "evidence", "observation"},
        "profile",
    )
    if item["schema"] != RUNTIME_PROFILE_SCHEMA:
        raise RuntimeTargetBindingError(
            "runtime-target-profile-invalid", "profile.schema", "schema is unsupported"
        )
    binding_ref = _required_text(item["binding_ref"], "profile.binding_ref")
    if not _BINDING_REF_RE.fullmatch(binding_ref):
        raise RuntimeTargetBindingError(
            "runtime-target-profile-invalid", "profile.binding_ref", "must be a logical provider reference"
        )
    target = _closed_mapping(item["target"], {"id", "kind", "fingerprint"}, "profile.target")
    declared_kind, canonical_kind = _canonical_kind(target["kind"], field="profile.target.kind")
    target_id = _required_text(target["id"], "profile.target.id")
    target_fingerprint = RuntimeFingerprint.from_mapping(target["fingerprint"],
                                                         field="profile.target.fingerprint")
    physical = _closed_mapping(item["physical_config"], {"env_file"}, "profile.physical_config")
    physical_env_file = _local_path(physical["env_file"],
                                    field="profile.physical_config.env_file", kind="file")
    evidence = _closed_mapping(item["evidence"], {"policy", "root", "non_production_approved"},
                               "profile.evidence")
    approved = evidence["non_production_approved"]
    if not isinstance(approved, bool):
        raise RuntimeTargetBindingError(
            "runtime-target-evidence-policy-invalid",
            "profile.evidence.non_production_approved",
            "must be a boolean",
        )
    policy_value = _required_text(evidence["policy"], "profile.evidence.policy")
    if policy_value not in EvidencePolicy._value2member_map_:
        raise RuntimeTargetBindingError(
            "runtime-target-evidence-policy-invalid", "profile.evidence.policy", "policy is unsupported"
        )
    policy = EvidencePolicy(policy_value)
    if policy is EvidencePolicy.FULL_LOCAL and not approved:
        raise RuntimeTargetBindingError(
            "runtime-target-evidence-policy-invalid",
            "profile.evidence.non_production_approved",
            "full_local requires explicit non-production approval",
        )
    allowed_root = _local_path(allowed_root_value, field=RUNTIME_EVIDENCE_ALLOW_ROOT_ENV, kind="dir",
                               code="runtime-target-evidence-root-invalid")
    evidence_root = _local_path(evidence["root"], field="profile.evidence.root", kind="dir",
                                code="runtime-target-evidence-root-invalid")
    if evidence_root != allowed_root and allowed_root not in evidence_root.parents:
        raise RuntimeTargetBindingError(
            "runtime-target-evidence-root-invalid",
            "profile.evidence.root",
            "root is outside the configured local allowlist",
        )
    observed = _closed_mapping(
        item["observation"],
        {
            "target_id", "target_kind", "target_fingerprint", "effective_principal_fingerprint",
            "platform_fingerprint", "extension_profile_fingerprint", "process_config_fingerprint",
            "security_receipt_id", "binding_generation",
        },
        "profile.observation",
    )
    observation = RuntimeTargetObservation(
        target_id=_required_text(observed["target_id"], "profile.observation.target_id"),
        target_kind=_required_text(observed["target_kind"], "profile.observation.target_kind"),
        target_fingerprint=RuntimeFingerprint.from_mapping(observed["target_fingerprint"],
                                                           field="profile.observation.target_fingerprint"),
        effective_principal_fingerprint=RuntimeFingerprint.from_mapping(
            observed["effective_principal_fingerprint"],
            field="profile.observation.effective_principal_fingerprint",
        ),
        platform_fingerprint=RuntimeFingerprint.from_mapping(observed["platform_fingerprint"],
                                                             field="profile.observation.platform_fingerprint"),
        extension_profile_fingerprint=RuntimeFingerprint.from_mapping(
            observed["extension_profile_fingerprint"], field="profile.observation.extension_profile_fingerprint"),
        process_config_fingerprint=RuntimeFingerprint.from_mapping(
            observed["process_config_fingerprint"], field="profile.observation.process_config_fingerprint"),
        security_receipt_id=_required_text(observed["security_receipt_id"],
                                           "profile.observation.security_receipt_id"),
        binding_generation=_positive_generation(observed["binding_generation"],
                                                field="profile.observation.binding_generation"),
    )
    return ProviderTargetProfile(
        binding_ref=binding_ref,
        target_id=target_id,
        target_kind=declared_kind,
        canonical_target_kind=canonical_kind,
        target_fingerprint=target_fingerprint,
        physical_env_file=physical_env_file,
        evidence_policy=policy,
        evidence_root=evidence_root,
        observation=observation,
    )


def _frozen_physical_config(path: Path) -> _ProviderPhysicalConfig:
    """Read the declared env file once into the complete consumer allowlist."""

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        raise RuntimeTargetBindingError(
            "runtime-target-profile-invalid", "profile.physical_config.env_file",
            "physical configuration is unreadable",
        ) from None
    values: dict[str, str] = {}
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return _ProviderPhysicalConfig(
        infobase_path=values.get("INFOBASE_PATH", "").strip(),
        connection_string=values.get("CONNECTION_STRING", "").strip(),
        platform_root=values.get("PLATFORM_ROOT", "").strip(),
        test_client_kind=values.get("TEST_CLIENT_KIND", "thick").strip(),
        test_client_user=values.get("TEST_CLIENT_USER", "").strip(),
        test_client_password=values.get("TEST_CLIENT_PASSWORD", ""),
        source_root=values.get("SRC_ROOT", "").strip(),
    )


def resolve_runtime_target(env: Mapping[str, str]) -> RuntimeTargetResolution | None:
    """Resolve one frozen project target without probing or launching TestClient."""
    if not any(name in env for name in _HANDOFF_FIELDS):
        return None
    missing = sorted(name for name in _HANDOFF_FIELDS if not str(env.get(name, "")).strip())
    if missing:
        raise RuntimeTargetBindingError(
            "runtime-target-handoff-incomplete", missing[0], "required logical handoff field is missing"
        )
    declared_kind, canonical_kind = _canonical_kind(env["AI1C_RUNTIME_TARGET_KIND"],
                                                     field="AI1C_RUNTIME_TARGET_KIND")
    binding_ref = _required_text(env["AI1C_RUNTIME_TARGET_BINDING_REF"], "AI1C_RUNTIME_TARGET_BINDING_REF")
    if not _BINDING_REF_RE.fullmatch(binding_ref):
        raise RuntimeTargetBindingError(
            "runtime-target-binding-ref-invalid", "AI1C_RUNTIME_TARGET_BINDING_REF",
            "must be a logical provider reference",
        )
    observations_ref = _required_text(env["AI1C_RUNTIME_TARGET_OBSERVATIONS"],
                                      "AI1C_RUNTIME_TARGET_OBSERVATIONS")
    if observations_ref != RUNTIME_OBSERVATIONS_REF:
        raise RuntimeTargetBindingError(
            "runtime-target-observation-ref-invalid", "AI1C_RUNTIME_TARGET_OBSERVATIONS",
            "reference is unsupported",
        )
    generation = _positive_generation(
        env["AI1C_RUNTIME_TARGET_BINDING_GENERATION"],
        field="AI1C_RUNTIME_TARGET_BINDING_GENERATION",
        allow_text=True,
    )
    target_id = _required_text(env["AI1C_RUNTIME_TARGET_ID"], "AI1C_RUNTIME_TARGET_ID")
    principal_id = _required_text(env["AI1C_AGENT_PRINCIPAL_ID"], "AI1C_AGENT_PRINCIPAL_ID")
    receipt_id = _required_text(
        env["AI1C_AGENT_TEST_SECURITY_RECEIPT_ID"], "AI1C_AGENT_TEST_SECURITY_RECEIPT_ID"
    )
    target_fingerprint = RuntimeFingerprint.from_values(
        env["AI1C_RUNTIME_TARGET_FINGERPRINT_ALGORITHM"],
        env["AI1C_RUNTIME_TARGET_FINGERPRINT"],
        field="AI1C_RUNTIME_TARGET_FINGERPRINT",
    )
    principal_fingerprint = RuntimeFingerprint.from_values(
        env["AI1C_AGENT_EXPECTED_PRINCIPAL_FINGERPRINT_ALGORITHM"],
        env["AI1C_AGENT_EXPECTED_PRINCIPAL_FINGERPRINT"],
        field="AI1C_AGENT_EXPECTED_PRINCIPAL_FINGERPRINT",
    )
    profile_path = str(env.get(RUNTIME_TARGET_PROFILE_ENV, "")).strip()
    allowed_root = str(env.get(RUNTIME_EVIDENCE_ALLOW_ROOT_ENV, "")).strip()
    if not profile_path or not allowed_root:
        missing_field = RUNTIME_TARGET_PROFILE_ENV if not profile_path else RUNTIME_EVIDENCE_ALLOW_ROOT_ENV
        raise RuntimeTargetBindingError(
            "runtime-target-provider-unbound", missing_field, "provider-local binding configuration is missing"
        )
    profile = _profile_from_path(profile_path, allowed_root)
    expected_identity = (target_id, canonical_kind, target_fingerprint, binding_ref)
    if (
        profile.target_id,
        profile.canonical_target_kind,
        profile.target_fingerprint,
        profile.binding_ref,
    ) != expected_identity:
        raise RuntimeTargetBindingError(
            "runtime-target-mismatch", "profile.target", "provider-local identity differs from handoff"
        )
    observed = profile.observation
    observed_identity = (
        observed.target_id,
        _canonical_kind(observed.target_kind, field="profile.observation.target_kind")[1],
        observed.target_fingerprint,
    )
    if observed_identity != expected_identity[:3]:
        raise RuntimeTargetBindingError(
            "runtime-target-mismatch", "profile.observation.target", "observed target differs from handoff"
        )
    if observed.effective_principal_fingerprint != principal_fingerprint:
        raise RuntimeTargetBindingError(
            "runtime-target-principal-mismatch",
            "profile.observation.effective_principal_fingerprint",
            "observed principal differs from handoff",
        )
    if observed.security_receipt_id != receipt_id or observed.binding_generation != generation:
        field = (
            "profile.observation.security_receipt_id"
            if observed.security_receipt_id != receipt_id
            else "profile.observation.binding_generation"
        )
        raise RuntimeTargetBindingError(
            "runtime-target-requalification-required", field, "observation is stale"
        )
    binding = RuntimeTargetBinding(
        target=TargetIdentity(
            logical_id=target_id,
            fingerprint=target_fingerprint.scalar,
            metadata=MappingProxyType({}),
        ),
        target_kind=canonical_kind,
        declared_target_kind=declared_kind,
        binding_ref=binding_ref,
        principal_id=principal_id,
        expected_principal_fingerprint=principal_fingerprint,
        binding_generation=generation,
        provider_observations_ref=observations_ref,
        security_receipt_id=receipt_id,
        evidence_policy=profile.evidence_policy,
        evidence_root=profile.evidence_root,
    )
    resolution = RuntimeTargetResolution(
        binding=binding,
        profile=profile,
        observation=observed,
        _physical_config=_frozen_physical_config(profile.physical_env_file),
    )
    object.__setattr__(resolution, "_validation_seal", _RESOLUTION_VALIDATION_SEAL)
    return resolution
