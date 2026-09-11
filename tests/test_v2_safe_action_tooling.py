from __future__ import annotations

import json
import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools" / "protocol-research"
sys.path.insert(0, str(TOOLS_DIR))

from v2_safe_action_tooling import (  # noqa: E402
    validate_manifest_data,
    validate_manifest_path,
    write_dry_run_output,
)


def valid_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "action_id": "safe-activate-existing-window",
        "target_id": "tm-v2-window-main",
        "target_marker": "PF_FORM_MAIN",
        "pre_state": {"active_window": "fixture-main"},
        "action": "activate existing fixture window",
        "post_state": {"active_window": "fixture-main"},
        "recovery_expectation": "reactivate original fixture window",
        "mutates_business_data": False,
        "allowed_action_family": "activate_existing_window_or_form",
        "expected_action_result_markers": ["PF_FORM_MAIN", "active_window_changed"],
        "safety_class": "safe_ui_action",
        "provider_owner": "project:qa-mcp",
        "status_reason": "reviewed catalog row",
        "residual_risk": "candidate only until live proof is retained",
    }
    row.update(overrides)
    return row


def target_map() -> list[dict[str, object]]:
    return [
        {
            "target_id": "tm-v2-window-main",
            "target_marker": "PF_FORM_MAIN",
            "target_status": "reviewed",
            "allowed_action_families": ["activate_existing_window_or_form"],
        },
        {
            "target_id": "tm-v2-popup-child",
            "target_marker": "PF_COMMAND_POPUP_CHILD",
            "target_status": "unsupported",
            "allowed_action_families": ["expand_or_collapse_menu_or_group"],
        },
    ]


def test_manifest_validation_accepts_complete_safe_action_row() -> None:
    validation = validate_manifest_data({"actions": [valid_row()]})
    [row] = validation["rows"]

    assert validation["executable_count"] == 1
    assert row["validation_status"] == "accepted_for_capture"
    assert row["executable"] is True


def test_manifest_validation_rejects_mutating_or_unsupported_rows() -> None:
    validation = validate_manifest_data(
        {
            "actions": [
                valid_row(action_id="bad-toggle", mutates_business_data=True),
                valid_row(action_id="bad-family", allowed_action_family="toggle_checkbox"),
            ]
        }
    )

    by_action = {row["action_id"]: row for row in validation["rows"]}
    assert by_action["bad-toggle"]["validation_status"] == "rejected"
    assert "mutates_business_data_not_false" in by_action["bad-toggle"]["reasons"]
    assert by_action["bad-family"]["validation_status"] == "rejected"
    assert "unsupported_action_family:toggle_checkbox" in by_action["bad-family"]["reasons"]


def test_manifest_validation_checks_reviewed_target_bindings() -> None:
    validation = validate_manifest_data(
        {
            "safe_action_targets": target_map(),
            "actions": [
                valid_row(action_id="target-ok"),
                valid_row(action_id="missing-target", target_id="tm-v2-missing"),
                valid_row(action_id="bad-marker", target_marker="PF_WRONG"),
                valid_row(
                    action_id="blocked-target",
                    target_id="tm-v2-popup-child",
                    target_marker="PF_COMMAND_POPUP_CHILD",
                    allowed_action_family="expand_or_collapse_menu_or_group",
                ),
            ],
        }
    )

    by_action = {row["action_id"]: row for row in validation["rows"]}
    assert validation["target_count"] == 2
    assert by_action["target-ok"]["validation_status"] == "accepted_for_capture"
    assert by_action["missing-target"]["validation_status"] == "rejected"
    assert "unsupported_target:tm-v2-missing" in by_action["missing-target"]["reasons"]
    assert by_action["bad-marker"]["validation_status"] == "rejected"
    assert "target_marker_mismatch:tm-v2-window-main:PF_WRONG!=PF_FORM_MAIN" in by_action[
        "bad-marker"
    ]["reasons"]
    assert by_action["blocked-target"]["validation_status"] == "rejected"
    assert "unsupported_target_status:tm-v2-popup-child:unsupported" in by_action[
        "blocked-target"
    ]["reasons"]


def test_manifest_validation_retains_non_executable_pending_and_unsupported_rows() -> None:
    validation = validate_manifest_data(
        {
            "safe_action_targets": target_map(),
            "actions": [
                valid_row(action_id="pending-target", prerequisite_status="pending"),
                valid_row(
                    action_id="unsupported-target",
                    target_id="tm-v2-popup-child",
                    target_marker="PF_COMMAND_POPUP_CHILD",
                    allowed_action_family="expand_or_collapse_menu_or_group",
                    prerequisite_status="unsupported",
                    unsupported_reason="popup child is not reviewed for V2 execution",
                    residual_risk="popup action may invoke a command if target identity drifts",
                ),
            ]
        }
    )

    by_action = {row["action_id"]: row for row in validation["rows"]}
    assert by_action["pending-target"]["validation_status"] == "pending"
    assert by_action["pending-target"]["executable"] is False
    assert by_action["unsupported-target"]["validation_status"] == "unsupported"
    assert by_action["unsupported-target"]["owner"] == "project:qa-mcp"
    assert by_action["unsupported-target"]["residual_risk"].startswith("popup action may")
    assert by_action["unsupported-target"]["status_reason"].startswith("popup child")
    assert validation["executable_count"] == 0


def test_dry_run_output_writes_phase_events_and_manager_manifest(tmp_path: Path) -> None:
    validation = validate_manifest_data({"actions": [valid_row()]})
    output_files = write_dry_run_output(tmp_path / "dry-run", validation)
    phase_events = [
        json.loads(line)
        for line in Path(output_files["phase_events"]).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    manager_manifest = json.loads(
        Path(output_files["manager_harness_manifest"]).read_text(encoding="utf-8")
    )
    manager_result = json.loads(
        Path(output_files["manager_harness_result"]).read_text(encoding="utf-8")
    )
    runner_results = [
        json.loads(line)
        for line in Path(output_files["runner_results"]).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert {event["phase"] for event in phase_events} == {
        "pre_read",
        "action_start",
        "action_end",
        "post_read",
        "recovery",
        "recovery_read",
        "background",
    }
    by_phase = {event["phase"]: event for event in phase_events}
    assert all(event["tcp_marker_policy"] == "side_channel_only_no_tcp_markers" for event in phase_events)
    assert by_phase["action_start"]["action_boundary"] is True
    assert by_phase["action_end"]["frame_correlation_status"] == "missing_action_frame_range"
    assert by_phase["action_end"]["action_result_markers"] == [
        "PF_FORM_MAIN",
        "active_window_changed",
    ]
    assert by_phase["recovery_read"]["recovery_result"]["status"] == "known_state_planned"
    assert by_phase["recovery_read"]["known_state_rationale"].startswith("dry-run recovery")
    assert by_phase["background"]["background_frame_ranges"] == []
    assert manager_manifest["command_count"] == 1
    assert manager_manifest["dispatcher_mode"] == "dry_run_fail_closed"
    assert manager_result["result_counts"] == {"success": 1}
    assert manager_result["live_action_executed"] is False
    assert runner_results[0]["status"] == "success"
    assert [phase["phase"] for phase in runner_results[0]["phase_results"]] == [
        "pre_read",
        "action_start",
        "action_end",
        "post_read",
        "recovery",
        "recovery_read",
    ]
    assert runner_results[0]["recovery_result"]["status"] == "known_state_planned"
    assert runner_results[0]["rerun_determinism"]["status"] == "dry_run_repeatable"
    assert runner_results[0]["action_result_markers"] == ["PF_FORM_MAIN", "active_window_changed"]


def test_dry_run_runner_results_preserve_typed_non_executable_statuses(tmp_path: Path) -> None:
    validation = validate_manifest_data(
        {
            "actions": [
                valid_row(action_id="blocked-row", prerequisite_status="blocked"),
                valid_row(action_id="unsupported-row", prerequisite_status="unsupported"),
                valid_row(action_id="partial-row", prerequisite_status="partial"),
                valid_row(action_id="timeout-row", prerequisite_status="timeout"),
                valid_row(action_id="rejected-row", allowed_action_family="business_command_click"),
            ]
        }
    )

    output_files = write_dry_run_output(tmp_path / "dry-run", validation)

    runner_results = [
        json.loads(line)
        for line in Path(output_files["runner_results"]).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    manager_result = json.loads(
        Path(output_files["manager_harness_result"]).read_text(encoding="utf-8")
    )

    statuses = {result["action_id"]: result["status"] for result in runner_results}
    assert statuses == {
        "blocked-row": "blocked",
        "unsupported-row": "unsupported",
        "partial-row": "partial",
        "timeout-row": "timeout",
        "rejected-row": "rejected",
    }
    assert manager_result["result_counts"] == {
        "blocked": 1,
        "partial": 1,
        "rejected": 1,
        "timeout": 1,
        "unsupported": 1,
    }


def test_validate_manifest_path_reads_cases_shape(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"cases": [valid_row()]}), encoding="utf-8")

    validation = validate_manifest_path(manifest)

    assert validation["row_count"] == 1
    assert validation["rows"][0]["case_id"] == "safe-activate-existing-window"
