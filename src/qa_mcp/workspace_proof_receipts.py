from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "ai1c.qa-mcp.workspace-proof-receipt.v1"
PROVIDER = "qa-mcp"

_SAFE_SOURCE_IDENTITY_KEYS = {
    "workspace_id",
    "user_id",
    "project_id",
    "repository_id",
    "remote_identity",
    "issue_id",
    "pull_request_id",
    "branch",
    "ref_policy",
    "project_profile_id",
    "commit_sha",
    "tree_sha",
    "source_scope",
    "source_generation_id",
    "source_snapshot_id",
}
_SAFE_PROOF_KEYS = {
    "scenario_ref",
    "evidence_ref",
    "commit_sha",
    "tree_sha",
    "source_generation_id",
    "source_snapshot_id",
}
_SOURCE_TRANSPORT_KEYS = {
    "workspace_path",
    "mutable_workspace_path",
    "server_ssh_workspace_path",
    "source_path",
    "source_root",
    "source_dir",
    "local_path",
    "absolute_path",
    "host_bind_path",
    "network_share_path",
    "mcp_file_payload",
    "host_bridge_payload",
    "host_bridge_source_body",
    "source_body",
    "source_text",
    "xml_source",
    "xml_body",
    "bsl_source",
    "bsl_body",
    "raw_source",
}
_RAW_EVIDENCE_KEYS = {
    "screenshot",
    "screenshot_path",
    "screenshot_base64",
    "raw_protocol_log",
    "protocol_log",
    "protocol_trace",
    "customer_data",
    "infobase_dump",
    "source_body",
    "source_text",
    "xml_source",
    "xml_body",
    "bsl_source",
    "bsl_body",
    "raw_source",
}


def build_workspace_qa_proof_receipt(
    *,
    source_identity: Mapping[str, Any],
    policy: Mapping[str, Any] | None = None,
    proof: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a secret-safe server SSH workspace QA proof receipt."""

    policy = policy or {}
    proof = proof or {}
    required = _policy_requires_qa_proof(policy)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "provider": PROVIDER,
        "source_identity": _select_safe_source_identity(source_identity),
        "qa_proof": {
            "required": required,
        },
        "diagnostics": [],
    }
    policy_ref = _string_or_none(policy.get("policy_ref") or policy.get("card_ref"))
    if policy_ref:
        receipt["qa_proof"]["policy_ref"] = policy_ref

    forbidden = _first_forbidden_input(source_identity, prefix="source_identity")
    if forbidden is None:
        forbidden = _first_forbidden_input(proof, prefix="proof", source_transport_only=True)
    if forbidden is not None:
        receipt["qa_proof"].update({"status": "unavailable", "freshness": "unavailable"})
        receipt["diagnostics"].append(forbidden)
        return receipt

    if not required:
        receipt["qa_proof"].update({"status": "not-required", "freshness": "not-required"})
        return receipt

    missing_source_field = _missing_source_identity_field(source_identity)
    if missing_source_field is not None:
        receipt["qa_proof"].update({"status": "unavailable", "freshness": "unavailable"})
        receipt["diagnostics"].append(
            {
                "code": "missing-source-identity",
                "field": f"source_identity.{missing_source_field}",
                "message": "QA proof freshness requires project/repository identity, source scope, selected commit/tree and source generation or snapshot identity.",
            }
        )
        return receipt

    evidence_ref = _string_or_none(proof.get("evidence_ref"))
    if evidence_ref is None:
        receipt["qa_proof"].update({"status": "missing", "freshness": "missing"})
        receipt["diagnostics"].append(
            {
                "code": "missing-qa-proof",
                "field": "proof.evidence_ref",
                "message": "QA proof is required by policy but no scenario evidence reference was provided.",
            }
        )
        return receipt

    receipt["qa_proof"].update(_select_safe_proof_fields(proof))
    stale_field = _stale_identity_field(source_identity, proof)
    if stale_field is not None:
        receipt["qa_proof"].update({"status": "stale", "freshness": "stale"})
        receipt["diagnostics"].append(
            {
                "code": "stale-qa-proof",
                "field": stale_field,
                "message": f"QA proof {stale_field} does not match the selected workspace source identity.",
            }
        )
        return receipt

    receipt["qa_proof"].update({"status": "current", "freshness": "current"})
    return receipt


def _policy_requires_qa_proof(policy: Mapping[str, Any]) -> bool:
    for key in ("qa_proof_required", "required", "requires_qa_proof"):
        value = policy.get(key)
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().lower() in {"1", "true", "yes", "on", "required"}:
            return True
    return False


def _select_safe_source_identity(source_identity: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in _SAFE_SOURCE_IDENTITY_KEYS:
        if key not in source_identity:
            continue
        value = source_identity[key]
        if key == "source_scope":
            scope = _safe_source_scope_list(value)
            if scope:
                result[key] = scope
        else:
            safe_value = _string_or_none(value)
            if safe_value is not None:
                result[key] = safe_value
    return result


def _select_safe_proof_fields(proof: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in _SAFE_PROOF_KEYS:
        safe_value = _string_or_none(proof.get(key))
        if safe_value is not None:
            result[key] = safe_value
    return result


def _safe_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        candidates: Sequence[Any] = [value]
    elif isinstance(value, Sequence) and not isinstance(value, bytes | bytearray):
        candidates = value
    else:
        return []
    result: list[str] = []
    for item in candidates:
        safe_value = _string_or_none(item)
        if safe_value is not None:
            result.append(safe_value)
    return result


def _safe_source_scope_list(value: Any) -> list[str]:
    return [item for item in _safe_string_list(value) if not _looks_like_absolute_or_escape_path(item)]


def _first_forbidden_input(
    payload: Mapping[str, Any],
    *,
    prefix: str,
    source_transport_only: bool = False,
) -> dict[str, str] | None:
    for path, value in _walk_mapping(payload, prefix=prefix):
        key = path.rsplit(".", 1)[-1].lower()
        if key in _SOURCE_TRANSPORT_KEYS:
            return _forbidden_route_diagnostic(path)
        if source_transport_only:
            continue
        if key in _RAW_EVIDENCE_KEYS:
            continue
        if _path_value_is_forbidden(path, value):
            return _forbidden_route_diagnostic(path)
    return None


def _walk_mapping(payload: Mapping[str, Any], *, prefix: str) -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = []
    for key, value in payload.items():
        path = f"{prefix}.{key}"
        items.append((path, value))
        if isinstance(value, Mapping):
            items.extend(_walk_mapping(value, prefix=path))
    return items


def _path_value_is_forbidden(path: str, value: Any) -> bool:
    key = path.rsplit(".", 1)[-1].lower()
    if key == "source_scope":
        return any(_looks_like_absolute_or_escape_path(item) for item in _safe_string_list(value))
    if not _is_path_shaped_key(key):
        return False
    string_value = _string_or_none(value)
    return string_value is not None and _looks_like_absolute_or_escape_path(string_value)


def _is_path_shaped_key(key: str) -> bool:
    return key in {"path", "paths"} or key.endswith("_path") or key.endswith("_paths")


def _looks_like_absolute_or_escape_path(value: str) -> bool:
    normalized = value.strip()
    if not normalized:
        return False
    lowered = normalized.lower()
    normalized_for_parts = normalized.replace("\\", "/")
    has_windows_drive = len(normalized) >= 3 and normalized[1] == ":" and normalized[2] in {"/", "\\"}
    return (
        normalized.startswith("/")
        or normalized.startswith("\\")
        or normalized.startswith("//")
        or normalized.startswith("\\\\")
        or normalized.startswith("~")
        or lowered.startswith("file:")
        or "://" in lowered
        or has_windows_drive
        or "\\" in normalized
        or ".." in normalized_for_parts.split("/")
    )


def _forbidden_route_diagnostic(path: str) -> dict[str, str]:
    return {
        "code": "forbidden-source-route",
        "field": path,
        "message": "Mutable workspace paths and source-body transport are not valid QA proof receipt inputs.",
    }


def _missing_source_identity_field(source_identity: Mapping[str, Any]) -> str | None:
    for field in ("project_id", "repository_id"):
        if not _string_or_none(source_identity.get(field)):
            return field
    if not _safe_source_scope_list(source_identity.get("source_scope")):
        return "source_scope"
    for field in ("commit_sha", "tree_sha"):
        if not _string_or_none(source_identity.get(field)):
            return field
    if not _string_or_none(source_identity.get("source_generation_id")) and not _string_or_none(
        source_identity.get("source_snapshot_id")
    ):
        return "source_generation_id"
    return None


def _stale_identity_field(source_identity: Mapping[str, Any], proof: Mapping[str, Any]) -> str | None:
    for field in ("commit_sha", "tree_sha"):
        expected = _string_or_none(source_identity.get(field))
        observed = _string_or_none(proof.get(field))
        if observed is None:
            return field
        if expected != observed:
            return field
    return None


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


__all__ = ["SCHEMA", "build_workspace_qa_proof_receipt"]
