from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools" / "protocol-research"
sys.path.insert(0, str(TOOLS_DIR))

from v2_safe_action_live_runner import build_runner  # noqa: E402
from v2_safe_action_tooling import validate_manifest_data, write_json  # noqa: E402


def focused_manifest() -> dict[str, object]:
    return {
        "safe_action_targets": [
            {
                "target_id": "tm-v2-pages-main",
                "target_marker": "PF_PAGES_MAIN",
                "target_status": "reviewed",
                "allowed_action_families": ["switch_fixture_page"],
            },
            {
                "target_id": "tm-v2-edit-string",
                "target_marker": "PF_EDIT_STRING",
                "target_status": "reviewed",
                "allowed_action_families": ["focus_existing_element"],
            },
        ],
        "actions": [
            {
                "action_id": "safe-switch-fixture-page-b",
                "target_id": "tm-v2-pages-main",
                "target_marker": "PF_PAGES_MAIN",
                "pre_state": {"selected_page": "PF_PAGE_A"},
                "action": {"family": "switch_fixture_page"},
                "post_state": {"selected_page": "PF_PAGE_B"},
                "recovery_expectation": {"route": "select_page_a", "expected_marker": "PF_PAGE_A"},
                "mutates_business_data": False,
                "allowed_action_family": "switch_fixture_page",
                "expected_action_result_markers": ["PF_PAGES_MAIN", "PF_PAGE_B"],
                "safety_class": "safe_ui_action",
            },
            {
                "action_id": "safe-focus-existing-edit-string",
                "target_id": "tm-v2-edit-string",
                "target_marker": "PF_EDIT_STRING",
                "pre_state": {"focus_marker": "PF_FORM_MAIN"},
                "action": {"family": "focus_existing_element"},
                "post_state": {"focus_marker": "PF_EDIT_STRING"},
                "recovery_expectation": {"route": "focus_form_shell", "expected_marker": "PF_FORM_MAIN"},
                "mutates_business_data": False,
                "allowed_action_family": "focus_existing_element",
                "expected_action_result_markers": ["PF_EDIT_STRING", "PF_EDIT_STRING_VALUE"],
                "safety_class": "safe_ui_action",
            },
        ],
    }


def test_live_runner_builds_only_focused_manifest_gated_step(tmp_path: Path) -> None:
    validation = validate_manifest_data(focused_manifest())
    validation_path = tmp_path / "validation.json"
    output_dir = tmp_path / "run"
    write_json(validation_path, validation)

    result = build_runner(validation_path, output_dir, "test-run", 15382)

    manifest = json.loads(Path(result["manager_harness_manifest"]).read_text(encoding="utf-8"))
    assert manifest["dispatcher_mode"] == "live_manifest_gated_focused_rows"
    assert manifest["command_count"] == 2
    assert manifest["supported_action_ids"] == [
        "safe-focus-existing-edit-string",
        "safe-switch-fixture-page-b",
    ]
    step_text = Path(result["manager_harness_step"]).read_text(encoding="utf-8")
    for phase in ("pre_read", "action_start", "action_end", "post_read", "recovery", "recovery_read"):
        assert phase in step_text


def test_live_runner_rejects_non_focused_executable_row(tmp_path: Path) -> None:
    data = focused_manifest()
    actions = data["actions"]
    assert isinstance(actions, list)
    actions.append(
        {
            "action_id": "safe-select-local-row-002",
            "target_id": "tm-v2-edit-string",
            "target_marker": "PF_EDIT_STRING",
            "pre_state": {"focus_marker": "PF_FORM_MAIN"},
            "action": {"family": "focus_existing_element"},
            "post_state": {"focus_marker": "PF_EDIT_STRING"},
            "recovery_expectation": {"route": "focus_form_shell", "expected_marker": "PF_FORM_MAIN"},
            "mutates_business_data": False,
            "allowed_action_family": "focus_existing_element",
            "expected_action_result_markers": ["PF_EDIT_STRING"],
            "safety_class": "safe_ui_action",
        }
    )
    validation = validate_manifest_data(data)
    validation_path = tmp_path / "validation.json"
    write_json(validation_path, validation)

    with pytest.raises(ValueError, match="live_runner_action_not_allowlisted:safe-select-local-row-002"):
        build_runner(validation_path, tmp_path / "run", "test-run", 15382)
