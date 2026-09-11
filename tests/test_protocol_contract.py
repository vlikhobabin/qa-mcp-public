from __future__ import annotations

import json
from pathlib import Path

from qa_mcp.protocol import AcceptanceStatus, list_readonly_operation_descriptors, load_accepted_mappings


REPO_ROOT = Path(__file__).resolve().parents[1]
ACCEPTED_EVIDENCE = (
    REPO_ROOT
    / "docs"
    / "protocol-research"
    / "evidence"
    / "accepted-mappings"
    / "expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted"
    / "accepted_mappings.json"
)
RESOLUTION_EVIDENCE = (
    REPO_ROOT
    / "docs"
    / "protocol-research"
    / "evidence"
    / "readonly-element-hash-resolution"
    / "20260603-incomplete-hash-with-extracted-request-evidence"
    / "resolution.json"
)


def test_readonly_descriptors_preserve_accepted_mapping_evidence() -> None:
    accepted = load_accepted_mappings(ACCEPTED_EVIDENCE)
    descriptors = {item.case_id: item for item in list_readonly_operation_descriptors(REPO_ROOT)}

    assert descriptors["active-window-context"].acceptance_status == AcceptanceStatus.ACCEPTED
    assert descriptors["active-form-context"].acceptance_status == AcceptanceStatus.ACCEPTED
    assert (
        descriptors["active-window-context"].accepted_normalized_hash
        == accepted["active-window-context"]["normalized_hash"]
    )
    assert (
        descriptors["active-form-context"].accepted_normalized_hash
        == accepted["active-form-context"]["normalized_hash"]
    )
    assert descriptors["active-window-context"].probe_evidence_paths
    assert descriptors["active-form-context"].source_capture_ids == ("20260602-193802", "20260602-195407")


def test_unresolved_probe_paths_are_not_accepted() -> None:
    descriptors = {item.case_id: item for item in list_readonly_operation_descriptors(REPO_ROOT)}

    assert descriptors["initial-ui"].acceptance_status == AcceptanceStatus.PARTIAL
    assert descriptors["form-summary"].acceptance_status == AcceptanceStatus.PARTIAL
    assert descriptors["form-element-details"].acceptance_status == AcceptanceStatus.INCOMPLETE_HASH
    assert descriptors["typed-input-field-readonly"].acceptance_status == AcceptanceStatus.INCOMPLETE_HASH
    assert descriptors["form-element-details"].accepted_normalized_hash is None
    assert descriptors["typed-input-field-readonly"].unresolved_reason == "accepted_probe_without_reviewed_request_hash"


def test_readonly_element_resolution_preserves_descriptor_boundary() -> None:
    descriptors = {item.case_id: item for item in list_readonly_operation_descriptors(REPO_ROOT)}
    resolution = json.loads(RESOLUTION_EVIDENCE.read_text(encoding="utf-8"))
    rows = {row["case_id"]: row for row in resolution["rows"]}

    assert resolution["outcome"] == "unresolved"
    assert resolution["accepted_case_ids"] == []
    assert descriptors["form-element-details"].acceptance_status == AcceptanceStatus.INCOMPLETE_HASH
    assert descriptors["typed-input-field-readonly"].acceptance_status == AcceptanceStatus.INCOMPLETE_HASH
    assert rows["form-element-details"]["published_status"] == "incomplete_hash"
    assert rows["typed-input-field-readonly"]["published_status"] == "incomplete_hash"
    assert rows["form-element-details"]["precise_reasons"] == [
        "accepted_reviewed_hash",
        "missing_request_frames",
    ]
    assert rows["typed-input-field-readonly"]["precise_reasons"] == [
        "accepted_reviewed_hash",
        "ambiguous_operation_join",
        "missing_request_frames",
    ]
    assert resolution["safe_action_boundary"]["safe_actions_unblocked"] is False
