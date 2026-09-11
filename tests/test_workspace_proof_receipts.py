from __future__ import annotations

import json

import pytest

from qa_mcp.workspace_proof_receipts import build_workspace_qa_proof_receipt


SOURCE_IDENTITY = {
    "workspace_id": "ws-acme-42",
    "project_id": "acme-accounting",
    "repository_id": "acme-main",
    "commit_sha": "6f33f7e6e4644d37268d75e61cbdd4b941b12c6a",
    "tree_sha": "85d3a9f742d04a24a88f96f2d8e9ab8726d0f413",
    "source_scope": ["configuration", "extensions"],
    "source_generation_id": "gen-acme-20260804-0001",
}


def test_optional_missing_qa_proof_is_not_required() -> None:
    receipt = build_workspace_qa_proof_receipt(source_identity=SOURCE_IDENTITY, policy={})

    assert receipt["schema"] == "ai1c.qa-mcp.workspace-proof-receipt.v1"
    assert receipt["provider"] == "qa-mcp"
    assert receipt["source_identity"]["workspace_id"] == "ws-acme-42"
    assert receipt["qa_proof"]["required"] is False
    assert receipt["qa_proof"]["status"] == "not-required"
    assert receipt["qa_proof"]["freshness"] == "not-required"
    assert "scenario_ref" not in receipt["qa_proof"]
    assert receipt["diagnostics"] == []


def test_required_missing_qa_proof_reports_gap() -> None:
    receipt = build_workspace_qa_proof_receipt(
        source_identity=SOURCE_IDENTITY,
        policy={"qa_proof_required": True, "policy_ref": "policy:workspace-qa-required"},
    )

    assert receipt["qa_proof"]["required"] is True
    assert receipt["qa_proof"]["policy_ref"] == "policy:workspace-qa-required"
    assert receipt["qa_proof"]["status"] == "missing"
    assert receipt["qa_proof"]["freshness"] == "missing"
    assert receipt["diagnostics"] == [
        {
            "code": "missing-qa-proof",
            "field": "proof.evidence_ref",
            "message": "QA proof is required by policy but no scenario evidence reference was provided.",
        }
    ]


def test_required_matching_qa_proof_is_current_and_secret_safe() -> None:
    receipt = build_workspace_qa_proof_receipt(
        source_identity=SOURCE_IDENTITY,
        policy={"qa_proof_required": True},
        proof={
            "scenario_ref": "scenario:smoke/read-document-list",
            "evidence_ref": "evidence:qa/workspace-42/smoke",
            "commit_sha": SOURCE_IDENTITY["commit_sha"],
            "tree_sha": SOURCE_IDENTITY["tree_sha"],
            "source_generation_id": SOURCE_IDENTITY["source_generation_id"],
            "raw_protocol_log": "REQUEST source text and protocol bytes",
            "screenshot_base64": "not-retained",
            "customer_data": {"name": "ACME"},
        },
    )

    assert receipt["qa_proof"]["status"] == "current"
    assert receipt["qa_proof"]["freshness"] == "current"
    assert receipt["qa_proof"]["scenario_ref"] == "scenario:smoke/read-document-list"
    assert receipt["qa_proof"]["evidence_ref"] == "evidence:qa/workspace-42/smoke"
    assert receipt["qa_proof"]["commit_sha"] == SOURCE_IDENTITY["commit_sha"]
    assert receipt["qa_proof"]["tree_sha"] == SOURCE_IDENTITY["tree_sha"]
    assert receipt["qa_proof"]["source_generation_id"] == SOURCE_IDENTITY["source_generation_id"]
    payload = json.dumps(receipt, ensure_ascii=False)
    assert "REQUEST source text" not in payload
    assert "not-retained" not in payload
    assert "ACME" not in payload


@pytest.mark.parametrize("missing_field", ["project_id", "repository_id", "source_scope"])
def test_required_qa_proof_needs_full_source_identity(missing_field: str) -> None:
    source_identity = dict(SOURCE_IDENTITY)
    source_identity.pop(missing_field)

    receipt = build_workspace_qa_proof_receipt(
        source_identity=source_identity,
        policy={"qa_proof_required": True},
        proof={
            "scenario_ref": "scenario:smoke/read-document-list",
            "evidence_ref": "evidence:qa/workspace-42/smoke",
            "commit_sha": SOURCE_IDENTITY["commit_sha"],
            "tree_sha": SOURCE_IDENTITY["tree_sha"],
        },
    )

    assert receipt["qa_proof"]["status"] == "unavailable"
    assert receipt["qa_proof"]["freshness"] == "unavailable"
    assert receipt["diagnostics"] == [
        {
            "code": "missing-source-identity",
            "field": f"source_identity.{missing_field}",
            "message": "QA proof freshness requires project/repository identity, source scope, selected commit/tree and source generation or snapshot identity.",
        }
    ]


@pytest.mark.parametrize("unsafe_scope", ["ssh://host/srv/workspace", "C:/work/source", r"..\workspace"])
def test_source_scope_rejects_mutable_or_absolute_routes(unsafe_scope: str) -> None:
    receipt = build_workspace_qa_proof_receipt(
        source_identity={**SOURCE_IDENTITY, "source_scope": [unsafe_scope]},
        policy={"qa_proof_required": True},
        proof={
            "scenario_ref": "scenario:smoke/read-document-list",
            "evidence_ref": "evidence:qa/workspace-42/smoke",
            "commit_sha": SOURCE_IDENTITY["commit_sha"],
            "tree_sha": SOURCE_IDENTITY["tree_sha"],
        },
    )

    assert receipt["qa_proof"]["status"] == "unavailable"
    assert receipt["qa_proof"]["freshness"] == "unavailable"
    assert receipt["diagnostics"] == [
        {
            "code": "forbidden-source-route",
            "field": "source_identity.source_scope",
            "message": "Mutable workspace paths and source-body transport are not valid QA proof receipt inputs.",
        }
    ]
    assert unsafe_scope not in json.dumps(receipt, ensure_ascii=False)


def test_required_qa_proof_with_mismatched_tree_is_stale() -> None:
    receipt = build_workspace_qa_proof_receipt(
        source_identity=SOURCE_IDENTITY,
        policy={"qa_proof_required": True},
        proof={
            "scenario_ref": "scenario:smoke/read-document-list",
            "evidence_ref": "evidence:qa/workspace-42/smoke",
            "commit_sha": SOURCE_IDENTITY["commit_sha"],
            "tree_sha": "0000000000000000000000000000000000000000",
        },
    )

    assert receipt["qa_proof"]["status"] == "stale"
    assert receipt["qa_proof"]["freshness"] == "stale"
    assert receipt["diagnostics"] == [
        {
            "code": "stale-qa-proof",
            "field": "tree_sha",
            "message": "QA proof tree_sha does not match the selected workspace source identity.",
        }
    ]


def test_forbidden_mutable_source_route_is_unavailable_without_retaining_value() -> None:
    receipt = build_workspace_qa_proof_receipt(
        source_identity={**SOURCE_IDENTITY, "workspace_path": "/srv/ssh-workspaces/acme/ws-42"},
        policy={"qa_proof_required": True},
        proof={"evidence_ref": "evidence:qa/workspace-42/smoke"},
    )

    assert receipt["qa_proof"]["status"] == "unavailable"
    assert receipt["qa_proof"]["freshness"] == "unavailable"
    assert receipt["diagnostics"] == [
        {
            "code": "forbidden-source-route",
            "field": "source_identity.workspace_path",
            "message": "Mutable workspace paths and source-body transport are not valid QA proof receipt inputs.",
        }
    ]
    assert "/srv/ssh-workspaces" not in json.dumps(receipt, ensure_ascii=False)
