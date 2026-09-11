from __future__ import annotations

import sys
import json
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools" / "protocol-research"
sys.path.insert(0, str(TOOLS_DIR))

from protocol_corpus_runner import (  # noqa: E402
    FrameRange,
    CorpusCase,
    default_cases,
    load_case_manifest,
    make_case_row,
    normalize_payload,
)


def test_default_cases_cover_readonly_surfaces() -> None:
    case_ids = {case.case_id for case in default_cases()}

    assert "active-window-context" in case_ids
    assert "active-form-context" in case_ids
    assert "form-element-details" in case_ids


def test_expanded_cases_cover_supported_family_and_gaps() -> None:
    cases = default_cases("expanded-readonly")
    by_family = {case.element_family: case for case in cases if case.element_family}
    by_id = {case.case_id: case for case in cases}

    assert by_id["typed-input-field-readonly"].availability == "supported"
    assert by_id["typed-input-field-readonly"].frame_range is not None
    assert by_family["Button"].availability == "unsupported"
    assert by_family["Button"].frame_range is None
    assert by_family["CheckBox"].availability == "unsupported"


def test_normalize_payload_replaces_known_binary_fields() -> None:
    payload = bytearray(range(120))
    payload.extend(bytes.fromhex("6653b2a6"))

    normalized_a = normalize_payload(bytes(payload))
    payload[19] = 200
    payload[68:84] = b"x" * 16
    normalized_b = normalize_payload(bytes(payload))

    assert normalized_a == normalized_b
    assert bytes(range(2, 18)) not in normalized_a


def test_normalize_payload_preserves_operation_token() -> None:
    payload = bytearray(range(120))
    payload.extend(bytes.fromhex("6653b2a6"))

    normalized_a = normalize_payload(bytes(payload))
    payload[51:67] = b"x" * 16
    normalized_b = normalize_payload(bytes(payload))

    assert normalized_a != normalized_b
    assert b"x" * 16 in normalized_b


def test_safe_action_manifest_preserves_action_fields(tmp_path: Path) -> None:
    manifest = tmp_path / "safe-action-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "case_id": "safe-focus-existing-editfield",
                        "action_id": "safe-focus-existing-editfield",
                        "target_id": "tm-v2-editfield-main",
                        "target_marker": "PF_STRING_FIELD",
                        "scenario": "safe-action",
                        "api_call": "TestedForm.ActivateElement",
                        "ui_target": "HomePage.ManagedForm.EditField[0]",
                        "expected_state": "Active form is open and no value edit is in progress.",
                        "safety_class": "safe_ui_action",
                        "replay_expectation": "pending",
                        "mutates_business_data": False,
                        "allowed_action_family": "focus_existing_element",
                        "expected_action_result_markers": ["focused_editfield"],
                        "frame_range": {"manager_to_client": {"from": 10, "to": 12}},
                        "action_frame_range": {"manager_to_client": {"from": 11, "to": 12}},
                        "background_frame_ranges": [
                            {"manager_to_client": {"from": 8, "to": 9}},
                        ],
                        "pre_state": "Focus is on the active form.",
                        "action": "focus_element",
                        "post_state": "Focus is on the selected edit field.",
                        "recovery_expectation": "Return focus to the prior element.",
                        "action_result_markers": ["focused_editfield"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    [case] = load_case_manifest(manifest, "readonly-smoke")

    assert case.safety_class == "safe_ui_action"
    assert case.action_id == "safe-focus-existing-editfield"
    assert case.target_marker == "PF_STRING_FIELD"
    assert case.allowed_action_family == "focus_existing_element"
    assert case.action == "focus_element"
    assert case.pre_state == "Focus is on the active form."
    assert case.expected_action_result_markers == ("focused_editfield",)
    assert case.action_result_markers == ("focused_editfield",)
    assert case.action_frame_range == FrameRange.from_manager(11, 12)
    assert case.background_frame_ranges == (FrameRange.from_manager(8, 9),)


def test_safe_action_row_and_events_include_transition_fields(tmp_path: Path) -> None:
    case = CorpusCase(
        case_id="safe-expand-menu",
        scenario="safe-action",
        api_call="TestedCommandBar.OpenMenu",
        ui_target="Active form command bar menu",
        expected_state="Command bar is visible and no command item is invoked.",
        safety_class="safe_ui_action",
        replay_expectation="pending",
        frame_range=None,
        availability="pending",
        action_id="safe-expand-menu",
        target_id="tm-v2-commandbar-menu",
        target_marker="PF_COMMAND_BAR",
        pre_state="Menu is collapsed.",
        action="expand_menu",
        post_state="Menu is expanded.",
        recovery_expectation="Collapse menu or move focus away without invoking a command.",
        mutates_business_data=False,
        allowed_action_family="expand_or_collapse_menu_or_group",
        expected_action_result_markers=("menu_expanded",),
        action_result_markers=("menu_expanded",),
        background_frame_ranges=(FrameRange.from_manager(20, 21),),
    )

    row, events = make_case_row(
        case,
        capture_dir=tmp_path / "capture",
        evidence_path="docs/protocol-research/evidence/corpus/safe-action-test",
        index={"manager_to_client": {}, "client_to_manager": {}},
        probe_result=None,
        probe_result_path=None,
        repo_root=tmp_path,
    )

    assert row["safety_class"] == "safe_ui_action"
    assert row["pre_state"] == "Menu is collapsed."
    assert row["target_marker"] == "PF_COMMAND_BAR"
    assert row["mutates_business_data"] is False
    assert row["allowed_action_family"] == "expand_or_collapse_menu_or_group"
    assert row["expected_action_result_markers"] == ["menu_expanded"]
    assert row["action"] == "expand_menu"
    assert row["post_state"] == "Menu is expanded."
    assert row["recovery_expectation"].startswith("Collapse menu")
    assert row["action_result_markers"] == ["menu_expanded"]
    assert row["background_frame_ranges"] == [FrameRange.from_manager(20, 21).to_json()]
    assert row["replay_status"] == "pending"
    assert [event["event"] for event in events] == [
        "case_start",
        "action_start",
        "case_step",
        "case_result",
        "action_end",
        "case_end",
    ]
    assert events[1]["action"] == "expand_menu"
    assert events[4]["action_result_markers"] == ["menu_expanded"]
