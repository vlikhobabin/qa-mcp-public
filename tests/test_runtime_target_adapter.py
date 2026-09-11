"""Closed, side-effect-free runtime-target profile resolution."""

from __future__ import annotations

import ast
import json
import traceback
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from qa_mcp import doctor, mcp_server
from qa_mcp.core import (
    EvidencePolicy,
    RuntimeTargetBindingError,
    TargetIdentity,
    activate_application_context,
    resolve_runtime_target,
)
from qa_mcp.config import Settings


def _fingerprint(value: str) -> dict[str, str]:
    return {"algorithm": "sha256", "value": value}


def _write_profile(
    tmp_path: Path,
    *,
    target_kind: str = "file-infobase",
    policy: str = "sanitized",
    approved: bool = False,
    mutation: tuple[tuple[str, ...], object] | None = None,
) -> tuple[Path, Path, Path]:
    allowed_root = tmp_path / "ignored-evidence"
    allowed_root.mkdir(parents=True)
    (allowed_root / "qa").mkdir()
    physical = tmp_path / "target.env"
    physical.write_text(
        "INFOBASE_PATH=/secret/local/base\nTEST_CLIENT_PASSWORD=sentinel-password\n",
        encoding="utf-8",
    )
    profile: dict[str, object] = {
        "schema": "qa-mcp.runtime-target-profile.v1",
        "binding_ref": "qa-demo",
        "target": {
            "id": "project-demo",
            "kind": target_kind,
            "fingerprint": _fingerprint("target-observed"),
        },
        "physical_config": {"env_file": str(physical)},
        "evidence": {
            "policy": policy,
            "root": str(allowed_root / "qa"),
            "non_production_approved": approved,
        },
        "observation": {
            "target_id": "project-demo",
            "target_kind": target_kind,
            "target_fingerprint": _fingerprint("target-observed"),
            "effective_principal_fingerprint": _fingerprint("principal-observed"),
            "platform_fingerprint": _fingerprint("platform-observed"),
            "extension_profile_fingerprint": _fingerprint("extensions-observed"),
            "process_config_fingerprint": _fingerprint("process-observed"),
            "security_receipt_id": "receipt-7",
            "binding_generation": 7,
        },
    }
    if mutation is not None:
        path, value = mutation
        target = profile
        for segment in path[:-1]:
            target = target[segment]  # type: ignore[assignment,index]
        if value is _DELETE:
            del target[path[-1]]  # type: ignore[arg-type]
        else:
            target[path[-1]] = value  # type: ignore[index]
    profile_path = tmp_path / "qa-target.json"
    profile_path.write_text(json.dumps(profile), encoding="utf-8")
    return profile_path, allowed_root, physical


_DELETE = object()


def _assert_exception_graph_is_secret_safe(exc: BaseException, sentinel: str) -> None:
    assert exc.__cause__ is None
    assert exc.__context__ is None
    assert sentinel not in str(exc)
    assert sentinel not in repr(vars(exc))
    assert sentinel not in "".join(traceback.format_exception(exc))


def _env(profile: Path, allowed_root: Path, *, kind: str = "file-infobase") -> dict[str, str]:
    return {
        "AI1C_RUNTIME_TARGET_ID": "project-demo",
        "AI1C_RUNTIME_TARGET_KIND": kind,
        "AI1C_RUNTIME_TARGET_FINGERPRINT": "target-observed",
        "AI1C_RUNTIME_TARGET_FINGERPRINT_ALGORITHM": "sha256",
        "AI1C_AGENT_PRINCIPAL_ID": "qa-agent",
        "AI1C_AGENT_EXPECTED_PRINCIPAL_FINGERPRINT": "principal-observed",
        "AI1C_AGENT_EXPECTED_PRINCIPAL_FINGERPRINT_ALGORITHM": "sha256",
        "AI1C_RUNTIME_TARGET_BINDING_GENERATION": "7",
        "AI1C_RUNTIME_TARGET_OBSERVATIONS": ".ai/runtime-provider-observations.json",
        "AI1C_RUNTIME_TARGET_BINDING_REF": "qa-demo",
        "AI1C_AGENT_TEST_SECURITY_RECEIPT_ID": "receipt-7",
        "QA_MCP_RUNTIME_TARGET_PROFILE": str(profile),
        "QA_MCP_RUNTIME_EVIDENCE_ALLOW_ROOT": str(allowed_root),
    }


@pytest.mark.parametrize(
    ("declared_kind", "canonical_kind"),
    [
        ("file", "file"),
        ("file-infobase", "file"),
        ("file_infobase", "file"),
        ("client-server", "client-server"),
        ("client-server-infobase", "client-server"),
        ("client_server", "client-server"),
    ],
)
def test_complete_handoff_resolves_one_immutable_target(
    tmp_path: Path, declared_kind: str, canonical_kind: str
) -> None:
    profile, allowed_root, physical = _write_profile(tmp_path, target_kind=declared_kind)

    resolution = resolve_runtime_target(_env(profile, allowed_root, kind=declared_kind))

    assert resolution is not None
    assert resolution.binding.target.logical_id == "project-demo"
    assert resolution.binding.target.fingerprint == "sha256:target-observed"
    assert resolution.binding.target_kind == canonical_kind
    assert resolution.binding.declared_target_kind == declared_kind
    assert resolution.binding.principal_id == "qa-agent"
    assert resolution.binding.security_receipt_id == "receipt-7"
    assert resolution.binding.binding_generation == 7
    assert resolution.binding.binding_ref == "qa-demo"
    assert resolution.profile.physical_env_file == physical.resolve()
    assert resolution.observation is resolution.profile.observation
    with pytest.raises(FrozenInstanceError):
        resolution.binding.binding_generation = 8  # type: ignore[misc]


def test_application_composes_explicit_configured_and_unbound_targets_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    env = _env(profile, allowed_root)
    resolution = resolve_runtime_target(env)
    assert resolution is not None
    observed: list[dict[str, str]] = []

    def resolve_once(values: dict[str, str]):
        observed.append(values)
        return resolution

    monkeypatch.setattr(mcp_server, "resolve_runtime_target", resolve_once)
    explicit = mcp_server.create_mcp_server(
        settings=Settings.from_env({
            "QA_MCP_CLIENT_HOST": "203.0.113.8",
            "QA_MCP_CLIENT_PORT": "15444",
        }),
        runtime_target=resolution,
    )
    configured = mcp_server.create_mcp_server(
        settings=Settings.from_env({
            "QA_MCP_CLIENT_HOST": "198.51.100.9",
            "QA_MCP_CLIENT_PORT": "25444",
        }),
        runtime_target_env=env,
    )
    unbound = mcp_server.create_mcp_server(settings=Settings.from_env({}))

    explicit_context = mcp_server.application_context(explicit)
    configured_context = mcp_server.application_context(configured)
    unbound_context = mcp_server.application_context(unbound)
    assert observed == [env]
    assert explicit_context.runtime_target is resolution
    assert configured_context.runtime_target is resolution
    assert explicit_context.target == configured_context.target == resolution.binding.target
    assert configured_context.settings.client_host == "198.51.100.9"
    assert unbound_context.runtime_target is None
    assert unbound_context.target is None
    assert len({id(explicit_context), id(configured_context), id(unbound_context)}) == 3


def test_application_rejects_contradictory_explicit_resolution(tmp_path: Path) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    resolution = resolve_runtime_target(_env(profile, allowed_root))
    assert resolution is not None
    contradictory = replace(
        resolution,
        binding=replace(
            resolution.binding,
            target=TargetIdentity(logical_id="other-project", fingerprint="sha256:other"),
        ),
    )

    with pytest.raises(RuntimeTargetBindingError) as caught:
        mcp_server.create_mcp_server(runtime_target=contradictory)

    assert caught.value.code == "runtime-target-mismatch"


@pytest.mark.parametrize("field", ["binding_ref", "evidence_policy"])
def test_application_rejects_self_consistent_forged_resolution_secret_safe(
    tmp_path: Path, field: str
) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    resolution = resolve_runtime_target(_env(profile, allowed_root))
    assert resolution is not None
    sentinel = "../sentinel-private-value" if field == "binding_ref" else "sentinel-private-value"
    if field == "binding_ref":
        forged = replace(
            resolution,
            binding=replace(resolution.binding, binding_ref=sentinel),
            profile=replace(resolution.profile, binding_ref=sentinel),
        )
    else:
        forged = replace(
            resolution,
            binding=replace(resolution.binding, evidence_policy=sentinel),  # type: ignore[arg-type]
            profile=replace(resolution.profile, evidence_policy=sentinel),  # type: ignore[arg-type]
        )

    with pytest.raises(RuntimeTargetBindingError) as caught:
        mcp_server.create_mcp_server(runtime_target=forged)

    assert caught.value.code == "runtime-target-mismatch"
    _assert_exception_graph_is_secret_safe(caught.value, sentinel)


def test_application_runtime_target_cannot_change_after_composition(tmp_path: Path) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    resolution = resolve_runtime_target(_env(profile, allowed_root))
    assert resolution is not None
    context = mcp_server.application_context(
        mcp_server.create_mcp_server(runtime_target=resolution)
    )

    with pytest.raises(FrozenInstanceError):
        context.runtime_target = None
    with pytest.raises(FrozenInstanceError):
        del context.runtime_target

    assert context.runtime_target is resolution


def test_only_resolver_produced_resolution_is_admitted_and_deeply_immutable(
    tmp_path: Path,
) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    resolution = resolve_runtime_target(_env(profile, allowed_root))
    assert resolution is not None

    with pytest.raises(RuntimeTargetBindingError) as caught:
        mcp_server.create_mcp_server(runtime_target=replace(resolution))
    assert caught.value.code == "runtime-target-mismatch"

    with pytest.raises(TypeError):
        resolution.binding.target.metadata["forged"] = "value"
    assert dict(resolution.binding.target.metadata) == {}


def test_doctor_reports_bound_target_first_without_physical_values(tmp_path: Path) -> None:
    profile, allowed_root, physical = _write_profile(tmp_path)
    env = _env(profile, allowed_root)

    result = doctor.run_doctor(
        env=env,
        require_bearer_token=False,
        standalone=True,
        probes=doctor.DoctorProbes(port_is_listening=lambda host, port, timeout: False),
    )

    binding = result["checks"][0]
    assert binding == {
        "name": "runtime_target_binding",
        "status": "pass",
        "ok": True,
        "required": True,
        "code": "runtime-target-ready",
        "data": {
            "state": "ready",
            "target": {
                "logical_id": "project-demo",
                "kind": "file",
                "fingerprint": "sha256:target-observed",
                "binding_ref": "qa-demo",
                "binding_generation": 7,
            },
            "evidence": {"policy": "sanitized"},
            "observation": {
                "status": "matched",
                "effective_principal_fingerprint": "sha256:principal-observed",
                "platform_fingerprint": "sha256:platform-observed",
                "extension_profile_fingerprint": "sha256:extensions-observed",
                "process_config_fingerprint": "sha256:process-observed",
            },
        },
    }
    payload = json.dumps(result, ensure_ascii=False)
    for secret in (str(profile), str(physical), str(allowed_root), "sentinel-password", "receipt-7", "qa-agent"):
        assert secret not in payload


def test_doctor_invalid_binding_fails_before_runtime_probes(tmp_path: Path) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    env = _env(profile, allowed_root)
    env["AI1C_RUNTIME_TARGET_ID"] = ""
    probe_calls: list[str] = []

    result = doctor.run_doctor(
        env=env,
        probes=doctor.DoctorProbes(
            port_is_listening=lambda host, port, timeout: probe_calls.append("listener") or True,
            proxy_auth_probe=lambda settings: probe_calls.append("auth") or {"ok": True},
        ),
    )

    assert result["ok"] is False
    assert result["checks"] == [{
        "name": "runtime_target_binding",
        "status": "fail",
        "ok": False,
        "required": True,
        "code": "runtime-target-handoff-incomplete",
        "hint": "Resolve the declared provider-local target binding before runtime probes.",
        "data": {"state": "invalid", "field": "AI1C_RUNTIME_TARGET_ID"},
    }]
    assert probe_calls == []


def test_bound_mcp_doctor_uses_frozen_application_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    resolution = resolve_runtime_target(_env(profile, allowed_root))
    assert resolution is not None
    observed: dict[str, object] = {}
    monkeypatch.setattr(
        mcp_server,
        "run_qa_mcp_doctor",
        lambda **kwargs: observed.update(kwargs) or {"ok": True, "checks": []},
    )
    server = mcp_server.create_mcp_server(runtime_target=resolution)

    with activate_application_context(mcp_server.application_context(server)):
        mcp_server.qa_mcp_doctor(require_bearer_token=False)

    assert observed["runtime_target"] is resolution
    assert observed["resolve_configured_target"] is False


def test_no_frozen_handoff_is_unbound_even_if_provider_profile_is_present(tmp_path: Path) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)

    assert resolve_runtime_target({}) is None
    assert resolve_runtime_target(
        {
            "QA_MCP_RUNTIME_TARGET_PROFILE": str(profile),
            "QA_MCP_RUNTIME_EVIDENCE_ALLOW_ROOT": str(allowed_root),
        }
    ) is None


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        ({"AI1C_RUNTIME_TARGET_ID": ""}, "runtime-target-handoff-incomplete"),
        ({"AI1C_AGENT_TEST_SECURITY_RECEIPT_ID": ""}, "runtime-target-handoff-incomplete"),
        ({"AI1C_RUNTIME_TARGET_BINDING_GENERATION": "0"}, "runtime-target-generation-invalid"),
        ({"AI1C_RUNTIME_TARGET_BINDING_GENERATION": "true"}, "runtime-target-generation-invalid"),
        ({"AI1C_RUNTIME_TARGET_OBSERVATIONS": "elsewhere.json"}, "runtime-target-observation-ref-invalid"),
        ({"AI1C_RUNTIME_TARGET_BINDING_REF": "../raw/path"}, "runtime-target-binding-ref-invalid"),
        ({"QA_MCP_RUNTIME_TARGET_PROFILE": ""}, "runtime-target-provider-unbound"),
        ({"QA_MCP_RUNTIME_EVIDENCE_ALLOW_ROOT": ""}, "runtime-target-provider-unbound"),
    ],
)
def test_partial_or_malformed_handoff_fails_secret_safe(
    tmp_path: Path, mutation: dict[str, str], code: str
) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    env = _env(profile, allowed_root)
    env.update(mutation)
    env["UNRELATED_SECRET"] = "sentinel-password"

    with pytest.raises(RuntimeTargetBindingError) as excinfo:
        resolve_runtime_target(env)

    assert excinfo.value.code == code
    assert "sentinel-password" not in str(excinfo.value)
    assert str(profile) not in str(excinfo.value)


@pytest.mark.parametrize(
    ("profile_mutation", "replacement", "code"),
    [
        (("target", "id"), "other", "runtime-target-mismatch"),
        (("target", "fingerprint", "value"), "other", "runtime-target-mismatch"),
        (("observation", "target_kind"), "client-server", "runtime-target-mismatch"),
        (("observation", "target_fingerprint", "value"), "other", "runtime-target-mismatch"),
        (("observation", "effective_principal_fingerprint", "value"), "other", "runtime-target-principal-mismatch"),
        (("observation", "security_receipt_id"), "old", "runtime-target-requalification-required"),
        (("observation", "binding_generation"), 6, "runtime-target-requalification-required"),
        (("binding_ref",), "other-ref", "runtime-target-mismatch"),
    ],
)
def test_profile_or_observation_mismatch_fails_closed(
    tmp_path: Path,
    profile_mutation: tuple[str, ...],
    replacement: object,
    code: str,
) -> None:
    profile, allowed_root, _ = _write_profile(
        tmp_path, mutation=(profile_mutation, replacement)
    )
    env = _env(profile, allowed_root)

    with pytest.raises(RuntimeTargetBindingError) as excinfo:
        resolve_runtime_target(env)

    assert excinfo.value.code == code


@pytest.mark.parametrize(
    ("policy", "approved", "expected"),
    [
        ("sanitized", False, EvidencePolicy.SANITIZED),
        ("full_local", True, EvidencePolicy.FULL_LOCAL),
    ],
)
def test_evidence_policies_require_explicit_local_approval(
    tmp_path: Path, policy: str, approved: bool, expected: EvidencePolicy
) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path, policy=policy, approved=approved)

    resolution = resolve_runtime_target(_env(profile, allowed_root))

    assert resolution is not None
    assert resolution.binding.evidence_policy is expected
    assert resolution.binding.evidence_root == (allowed_root / "qa").resolve()


@pytest.mark.parametrize(("policy", "approved"), [("full_local", False), ("sentinel-policy-secret", True)])
def test_unapproved_or_unknown_evidence_policy_fails_closed(
    tmp_path: Path, policy: str, approved: bool
) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path, policy=policy, approved=approved)

    with pytest.raises(RuntimeTargetBindingError) as excinfo:
        resolve_runtime_target(_env(profile, allowed_root))

    assert excinfo.value.code == "runtime-target-evidence-policy-invalid"
    assert excinfo.value.__cause__ is None
    assert excinfo.value.__context__ is None
    if policy == "sentinel-policy-secret":
        _assert_exception_graph_is_secret_safe(excinfo.value, policy)


def test_profile_generation_must_be_json_integer(tmp_path: Path) -> None:
    profile, allowed_root, _ = _write_profile(
        tmp_path, mutation=(("observation", "binding_generation"), "7")
    )

    with pytest.raises(RuntimeTargetBindingError) as excinfo:
        resolve_runtime_target(_env(profile, allowed_root))

    assert excinfo.value.code == "runtime-target-generation-invalid"


def test_missing_declared_evidence_directory_fails_closed(tmp_path: Path) -> None:
    profile, allowed_root, _ = _write_profile(
        tmp_path, mutation=(("evidence", "root"), str(tmp_path / "ignored-evidence" / "missing"))
    )

    with pytest.raises(RuntimeTargetBindingError) as excinfo:
        resolve_runtime_target(_env(profile, allowed_root))

    assert excinfo.value.code == "runtime-target-evidence-root-invalid"


def test_malformed_profile_inputs_do_not_survive_in_exception_graph(tmp_path: Path) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    for payload, sentinel in (
        (b'{"sentinel-json-secret":', "sentinel-json-secret"),
        (b"\xffsentinel-utf8-secret", "sentinel-utf8-secret"),
    ):
        profile.write_bytes(payload)
        with pytest.raises(RuntimeTargetBindingError) as excinfo:
            resolve_runtime_target(_env(profile, allowed_root))
        _assert_exception_graph_is_secret_safe(excinfo.value, sentinel)


def test_invalid_path_is_typed_without_retaining_input(tmp_path: Path) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    env = _env(profile, allowed_root)
    env["QA_MCP_RUNTIME_TARGET_PROFILE"] = "\x00sentinel-path-secret"

    with pytest.raises(RuntimeTargetBindingError) as excinfo:
        resolve_runtime_target(env)

    _assert_exception_graph_is_secret_safe(excinfo.value, "sentinel-path-secret")


def test_oversized_generations_are_typed_without_retaining_input(tmp_path: Path) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    oversized = "9" * 5000
    env = _env(profile, allowed_root)
    env["AI1C_RUNTIME_TARGET_BINDING_GENERATION"] = oversized
    with pytest.raises(RuntimeTargetBindingError) as excinfo:
        resolve_runtime_target(env)
    _assert_exception_graph_is_secret_safe(excinfo.value, oversized)

    payload = profile.read_text(encoding="utf-8").replace(
        '"binding_generation": 7', f'"binding_generation": {oversized}'
    )
    profile.write_text(payload, encoding="utf-8")
    with pytest.raises(RuntimeTargetBindingError) as excinfo:
        resolve_runtime_target(_env(profile, allowed_root))
    _assert_exception_graph_is_secret_safe(excinfo.value, oversized)


def test_deeply_nested_json_is_typed_without_retaining_input(tmp_path: Path) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    sentinel = "sentinel-deep-json-secret"
    profile.write_text("[" * 2000 + f'"{sentinel}"' + "]" * 2000, encoding="utf-8")

    with pytest.raises(RuntimeTargetBindingError) as excinfo:
        resolve_runtime_target(_env(profile, allowed_root))

    assert excinfo.value.code == "runtime-target-profile-invalid"
    _assert_exception_graph_is_secret_safe(excinfo.value, sentinel)


def test_profile_and_physical_symlinks_are_rejected(tmp_path: Path) -> None:
    profile, allowed_root, physical = _write_profile(tmp_path)
    profile_link = tmp_path / "profile-link.json"
    profile_link.symlink_to(profile)
    with pytest.raises(RuntimeTargetBindingError):
        resolve_runtime_target(_env(profile_link, allowed_root))

    physical_link = tmp_path / "physical-link.env"
    physical_link.symlink_to(physical)
    payload = json.loads(profile.read_text(encoding="utf-8"))
    payload["physical_config"]["env_file"] = str(physical_link)
    profile.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuntimeTargetBindingError):
        resolve_runtime_target(_env(profile, allowed_root))


@pytest.mark.parametrize("payload", ["{broken", '{"schema":"qa-mcp.runtime-target-profile.v1","extra":true}'])
def test_malformed_or_open_profile_fails_closed(tmp_path: Path, payload: str) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    profile.write_text(payload, encoding="utf-8")

    with pytest.raises(RuntimeTargetBindingError) as excinfo:
        resolve_runtime_target(_env(profile, allowed_root))

    assert excinfo.value.code == "runtime-target-profile-invalid"


def test_evidence_root_escape_and_symlink_chain_are_rejected(tmp_path: Path) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    payload = json.loads(profile.read_text(encoding="utf-8"))
    payload["evidence"]["root"] = str(tmp_path / "outside")
    profile.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuntimeTargetBindingError) as excinfo:
        resolve_runtime_target(_env(profile, allowed_root))
    assert excinfo.value.code == "runtime-target-evidence-root-invalid"

    real_root = tmp_path / "real-evidence"
    real_root.mkdir()
    linked_root = tmp_path / "linked-evidence"
    linked_root.symlink_to(real_root, target_is_directory=True)
    profile, _, _ = _write_profile(tmp_path / "second")
    with pytest.raises(RuntimeTargetBindingError) as excinfo:
        resolve_runtime_target(_env(profile, linked_root))
    assert excinfo.value.code == "runtime-target-evidence-root-invalid"


def test_resolution_reads_only_declared_files_and_creates_no_runtime_resources(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profile, allowed_root, _ = _write_profile(tmp_path)
    before = {
        path.relative_to(tmp_path).as_posix(): (path.stat().st_mtime_ns, path.read_bytes())
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    monkeypatch.setattr(Path, "write_text", lambda *_args, **_kwargs: pytest.fail("write"))
    monkeypatch.setattr(Path, "write_bytes", lambda *_args, **_kwargs: pytest.fail("write"))
    monkeypatch.setattr(Path, "mkdir", lambda *_args, **_kwargs: pytest.fail("mkdir"))

    resolution = resolve_runtime_target(_env(profile, allowed_root))

    assert resolution is not None
    after = {
        path.relative_to(tmp_path).as_posix(): (path.stat().st_mtime_ns, path.read_bytes())
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert after == before


def test_resolver_module_has_no_process_network_or_lifecycle_dependency() -> None:
    source = Path("src/qa_mcp/core/runtime_target.py").read_text(encoding="utf-8")
    imports = {
        node.names[0].name.split(".")[0]
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Import)
    }
    from_imports = {
        (node.module or "").split(".")[0]
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom)
    }

    assert not ({"subprocess", "socket", "asyncio"} & imports)
    assert not ({"application", "executors", "lifecycle", "mcp_server"} & from_imports)
