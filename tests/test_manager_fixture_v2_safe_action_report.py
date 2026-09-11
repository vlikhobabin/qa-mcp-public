from __future__ import annotations

import json
import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools" / "protocol-research"
sys.path.insert(0, str(TOOLS_DIR))

from report_manager_fixture_v2_safe_action import generate  # noqa: E402
from v2_safe_action_tooling import validate_manifest_data, write_dry_run_output  # noqa: E402


def safe_action_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "action_id": "safe-focus-existing-editfield",
        "target_id": "tm-v2-editfield-main",
        "target_marker": "PF_STRING_FIELD",
        "pre_state": {"focus": "form"},
        "action": "focus existing edit field",
        "post_state": {"focus": "PF_STRING_FIELD"},
        "recovery_expectation": "return focus to the form",
        "mutates_business_data": False,
        "allowed_action_family": "focus_existing_element",
        "expected_action_result_markers": ["PF_STRING_FIELD", "focus_changed"],
        "action_frame_range": {"manager_to_client": {"from": 20, "to": 21}},
        "background_frame_ranges": [{"manager_to_client": {"from": 18, "to": 19}}],
        "recovery_frame_range": {"manager_to_client": {"from": 25, "to": 25}},
        "safety_class": "safe_ui_action",
        "api_call": "TestedForm.ActivateElement",
        "ui_target": "ProtocolFixture.Form.PF_STRING_FIELD",
    }
    row.update(overrides)
    return row


def read_rows(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def chunk(direction: str, chunk_no: int, timestamp: str, byte_count: int = 4) -> dict[str, object]:
    return {
        "ts": timestamp,
        "event": "chunk",
        "direction": direction,
        "chunk_no": chunk_no,
        "byte_count": byte_count,
        "sha256": f"{chunk_no:064x}",
    }


def test_v2_safe_action_report_publishes_candidate_rows_with_separated_ranges(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    output_dir = tmp_path / "evidence"
    validation = validate_manifest_data({"actions": [safe_action_row()]})
    write_dry_run_output(run_dir, validation)

    result = generate(run_dir, output_dir)

    [row] = read_rows(Path(result["case_rows_path"]))
    assert row["safety_class"] == "safe_ui_action"
    assert row["validation_status"] == "accepted_for_capture"
    assert row["replay_status"] == "pending"
    assert row["accepted_protocol_mapping"] is False
    assert row["action_frame_range"] == {"manager_to_client": {"from": 20, "to": 21}}
    assert row["background_frame_ranges"] == [{"manager_to_client": {"from": 18, "to": 19}}]
    assert row["recovery_frame_range"] == {"manager_to_client": {"from": 25, "to": 25}}
    assert row["action_runtime_result"]["status"] == "success"
    assert row["recovery_result"]["status"] == "known_state_planned"
    assert row["rerun_determinism"]["status"] == "dry_run_repeatable"
    assert row["action_result_markers"] == ["PF_STRING_FIELD", "focus_changed"]
    assert "missing_action_result_markers" not in row["non_accepted_reasons"]
    assert "missing_recovery_result" not in row["non_accepted_reasons"]
    assert "replay_or_probe_unavailable" in row["non_accepted_reasons"]


def test_v2_safe_action_report_reads_runner_results(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    output_dir = tmp_path / "evidence"
    validation = validate_manifest_data({"actions": [safe_action_row()]})
    write_dry_run_output(run_dir, validation)

    result = generate(run_dir, output_dir)

    [row] = read_rows(Path(result["case_rows_path"]))
    assert row["action_runtime_result"]["status"] == "success"
    assert row["action_runtime_result"]["live_action_executed"] is False
    assert row["action_result_markers"] == ["PF_STRING_FIELD", "focus_changed"]
    assert row["recovery_result"]["known_state_rationale"].startswith("dry-run recovery")
    assert row["accepted_protocol_mapping"] is False


def test_v2_safe_action_report_joins_live_phase_events_to_traffic(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    output_dir = tmp_path / "evidence"
    validation = validate_manifest_data(
        {
            "actions": [
                safe_action_row(
                    action_frame_range=None,
                    background_frame_ranges=[],
                    recovery_frame_range=None,
                    request_size=0,
                    response_size=0,
                )
            ]
        }
    )
    write_dry_run_output(run_dir, validation)

    case_id = "safe-focus-existing-editfield"
    phase_rows = [
        {"case_id": case_id, "action_id": case_id, "phase": "pre_read", "timestamp": "2026-06-07T10:00:00Z"},
        {"case_id": case_id, "action_id": case_id, "phase": "action_start", "timestamp": "2026-06-07T10:00:02Z"},
        {"case_id": case_id, "action_id": case_id, "phase": "action_end", "timestamp": "2026-06-07T10:00:02Z"},
        {"case_id": case_id, "action_id": case_id, "phase": "post_read", "timestamp": "2026-06-07T10:00:04Z"},
        {"case_id": case_id, "action_id": case_id, "phase": "recovery", "timestamp": "2026-06-07T10:00:05Z"},
        {"case_id": case_id, "action_id": case_id, "phase": "recovery_read", "timestamp": "2026-06-07T10:00:05Z"},
    ]
    write_jsonl(run_dir / "safe_action_phase_events.jsonl", phase_rows)
    write_jsonl(run_dir / "case_events.jsonl", phase_rows)
    write_jsonl(
        run_dir / "traffic.jsonl",
        [
            chunk("manager_to_client", 18, "2026-06-07T10:00:01Z", byte_count=3),
            chunk("manager_to_client", 20, "2026-06-07T10:00:02Z", byte_count=7),
            chunk("client_to_manager", 21, "2026-06-07T10:00:03Z", byte_count=11),
            chunk("manager_to_client", 22, "2026-06-07T10:00:04Z", byte_count=5),
            chunk("manager_to_client", 25, "2026-06-07T10:00:05Z", byte_count=13),
            chunk("client_to_manager", 26, "2026-06-07T10:00:06Z", byte_count=17),
        ],
    )
    write_jsonl(
        run_dir / "safe_action_runner_results.jsonl",
        [
            {
                "case_id": case_id,
                "action_id": case_id,
                "status": "success",
                "live_action_executed": True,
                "action_result_markers": ["PF_STRING_FIELD", "focus_changed"],
                "recovery_result": {
                    "status": "known_state_restored",
                    "expected_recovery_markers": ["PF_FORM_MAIN"],
                    "live_recovery_executed": True,
                    "known_state_rationale": "live recovery read returned the fixture shell marker",
                },
            }
        ],
    )

    result = generate(run_dir, output_dir)

    [row] = read_rows(Path(result["case_rows_path"]))
    assert row["action_frame_range"] == {
        "manager_to_client": {"from": 20, "to": 20, "count": 1},
        "client_to_manager": {"from": 21, "to": 21, "count": 1},
    }
    assert row["background_frame_ranges"] == [
        {"manager_to_client": {"from": 18, "to": 22, "count": 2}}
    ]
    assert row["recovery_frame_range"] == {
        "manager_to_client": {"from": 25, "to": 25, "count": 1},
        "client_to_manager": {"from": 26, "to": 26, "count": 1},
    }
    assert row["request_size"] == 7
    assert row["response_size"] == 11
    assert row["normalized_hash"]
    assert row["pre_normalization_hash"]
    assert row["action_runtime_result"]["live_action_executed"] is True
    assert row["action_runtime_result"]["frame_join"]["status"] == "joined"
    assert "missing_action_frame_range" not in row["non_accepted_reasons"]


def test_v2_safe_action_report_can_publish_accepted_row_with_compact_proof(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    output_dir = tmp_path / "evidence"
    validation = validate_manifest_data(
        {
            "actions": [
                safe_action_row(
                    replay_status="accepted",
                    action_result_markers=["PF_STRING_FIELD", "focus_changed"],
                    normalized_hash="a" * 64,
                    request_size=10,
                    response_size=12,
                    acceptance_evidence=["docs/protocol-research/evidence/probe/focus-summary.json"],
                )
            ]
        }
    )
    write_dry_run_output(run_dir, validation)

    result = generate(run_dir, output_dir)

    [row] = read_rows(Path(result["case_rows_path"]))
    assert row["replay_status"] == "accepted"
    assert row["accepted_protocol_mapping"] is True
    assert row["action_runtime_result"]["status"] == "accepted"
