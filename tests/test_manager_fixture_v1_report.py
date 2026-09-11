from __future__ import annotations

import base64
import json
import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools" / "protocol-research"
sys.path.insert(0, str(TOOLS_DIR))

from report_manager_fixture_v1 import generate  # noqa: E402


def write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def command(case_id: str = "tm-v1-active-window") -> dict[str, object]:
    return {
        "case_id": case_id,
        "command_id": "active_window",
        "command_kind": "active_window",
        "target_fixture_path": "DataProcessor.ФикстураПротоколаTestClient.Form.Форма",
        "target_marker": "PF_FORM_MAIN",
        "expected_marker": "QA MCP Protocol Fixture V1",
        "element_family": "ApplicationWindow",
        "safety_class": "read_only",
    }


def write_runtime(run_dir: Path, commands: list[dict[str, object]], events: list[dict[str, object]], traffic: list[dict[str, object]]) -> None:
    run_dir.mkdir()
    write_json(
        run_dir / "manager_harness_manifest.json",
        {
            "schema": "qa-mcp.manager-fixture-v1.manifest.v1",
            "run_id": run_dir.name,
            "fixture_version": "protocol-fixture.v1",
            "manager_harness": "DataProcessor.ProtocolFixtureTestManager.Form.ManagerHarness",
            "target_fixture_path": "DataProcessor.ФикстураПротоколаTestClient.Form.Форма",
            "proxy_testclient_port": 15382,
            "commands": commands,
        },
    )
    write_json(
        run_dir / "manager_harness_result.json",
        {
            "schema": "qa-mcp.manager-fixture-v1.result.v1",
            "run_id": run_dir.name,
            "scenario": "manager-fixture-v1-readonly",
            "status": "ok",
            "status_reason": "test fixture",
            "command_count": len(commands),
            "completed_count": len(commands),
            "failed_count": 0,
            "accepted_protocol_mapping": False,
        },
    )
    write_jsonl(run_dir / "case_events.jsonl", events)
    write_jsonl(run_dir / "traffic.jsonl", traffic)


def event(case_id: str, phase: str, timestamp: str) -> dict[str, object]:
    return {
        "schema": "manager_case_event.v1",
        "run_id": "test-run",
        "case_id": case_id,
        "command_id": "active_window",
        "command_kind": "active_window",
        "phase": phase,
        "status": "started" if phase == "before" else "ok",
        "timestamp": timestamp,
        "target_marker": "PF_FORM_MAIN",
        "expected_marker": "QA MCP Protocol Fixture V1",
    }


def chunk(direction: str, chunk_no: int, timestamp: str, byte_count: int = 4, payload: bytes | None = None) -> dict[str, object]:
    if payload is not None:
        return {
            "ts": timestamp,
            "event": "chunk",
            "connection_id": 1,
            "direction": direction,
            "chunk_no": chunk_no,
            "byte_count": len(payload),
            "sha256": f"{chunk_no:064x}",
            "payload_b64": base64.b64encode(payload).decode("ascii"),
        }
    return {
        "ts": timestamp,
        "event": "chunk",
        "connection_id": 1,
        "direction": direction,
        "chunk_no": chunk_no,
        "byte_count": byte_count,
        "sha256": f"{chunk_no:064x}",
    }


def load_frame_report(output_dir: Path) -> dict[str, object]:
    return json.loads((output_dir / "frame_join_report.json").read_text(encoding="utf-8"))


def load_corpus_rows(output_dir: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in (output_dir / "corpus_cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_joined_case_events_map_to_directional_chunk_ranges(tmp_path: Path) -> None:
    run_dir = tmp_path / "joined-run"
    output_dir = tmp_path / "joined-evidence"
    write_runtime(
        run_dir,
        [command()],
        [
            event("tm-v1-active-window", "before", "2026-06-05T00:00:01Z"),
            event("tm-v1-active-window", "after", "2026-06-05T00:00:05Z"),
        ],
        [
            chunk("manager_to_client", 10, "2026-06-05T00:00:02Z", 7),
            chunk("client_to_manager", 20, "2026-06-05T00:00:03Z", 9),
        ],
    )

    generate(run_dir, output_dir)

    [case] = load_frame_report(output_dir)["cases"]
    assert case["join_status"] == "joined"
    assert case["manager_chunk_range"] == {"from": 10, "to": 10, "count": 1}
    assert case["client_chunk_range"] == {"from": 20, "to": 20, "count": 1}
    [row] = load_corpus_rows(output_dir)
    assert row["replay_status"] == "pending"
    assert row["accepted_protocol_mapping"] is False
    assert row["request_size"] == 7
    assert row["response_size"] == 9


def test_missing_event_is_reported_with_precise_reason(tmp_path: Path) -> None:
    run_dir = tmp_path / "missing-event-run"
    output_dir = tmp_path / "missing-event-evidence"
    write_runtime(run_dir, [command()], [], [chunk("manager_to_client", 1, "2026-06-05T00:00:02Z")])

    generate(run_dir, output_dir)

    [case] = load_frame_report(output_dir)["cases"]
    assert case["join_status"] == "unresolved"
    assert case["unresolved_reason"] == "no_before_event"


def test_missing_traffic_is_reported_with_precise_reason(tmp_path: Path) -> None:
    run_dir = tmp_path / "missing-traffic-run"
    output_dir = tmp_path / "missing-traffic-evidence"
    write_runtime(
        run_dir,
        [command()],
        [
            event("tm-v1-active-window", "before", "2026-06-05T00:00:01Z"),
            event("tm-v1-active-window", "after", "2026-06-05T00:00:05Z"),
        ],
        [],
    )

    generate(run_dir, output_dir)

    [case] = load_frame_report(output_dir)["cases"]
    assert case["join_status"] == "unresolved"
    assert case["unresolved_reason"] == "no_proxy_chunks"


def test_zero_width_event_window_expands_for_chunk_join(tmp_path: Path) -> None:
    run_dir = tmp_path / "zero-width-run"
    output_dir = tmp_path / "zero-width-evidence"
    write_runtime(
        run_dir,
        [command()],
        [
            event("tm-v1-active-window", "before", "2026-06-05T00:00:01Z"),
            event("tm-v1-active-window", "after", "2026-06-05T00:00:01Z"),
        ],
        [
            chunk("manager_to_client", 10, "2026-06-05T00:00:01.500Z", 7),
            chunk("client_to_manager", 20, "2026-06-05T00:00:01.700Z", 9),
        ],
    )

    generate(run_dir, output_dir)

    [case] = load_frame_report(output_dir)["cases"]
    assert case["join_status"] == "joined"
    assert case["timestamp_window_adjustment"] == "zero_width_expanded_to_1s"
    assert case["manager_chunk_range"] == {"from": 10, "to": 10, "count": 1}
    assert case["client_chunk_range"] == {"from": 20, "to": 20, "count": 1}


def test_binary_frame_signature_normalizes_dynamic_bytes_and_repeat_count(tmp_path: Path) -> None:
    rows: list[dict[str, object]] = []
    for index, repeat_count in enumerate([1, 3]):
        run_dir = tmp_path / f"binary-run-{index}"
        output_dir = tmp_path / f"binary-evidence-{index}"
        traffic = []
        for repeat in range(repeat_count):
            traffic.extend(
                [
                    chunk(
                        "manager_to_client",
                        10 + repeat,
                        "2026-06-05T00:00:02Z",
                        payload=b"A" + bytes([index + repeat + 1]) * 16 + b"pf_form_main" + b"\x00",
                    ),
                    chunk(
                        "client_to_manager",
                        20 + repeat,
                        "2026-06-05T00:00:03Z",
                        payload=b"B" + bytes([index + repeat + 5]) * 16 + b"pf_form_main" + b"\x00",
                    ),
                ]
            )
        write_runtime(
            run_dir,
            [command()],
            [
                event("tm-v1-active-window", "before", "2026-06-05T00:00:01Z"),
                event("tm-v1-active-window", "after", "2026-06-05T00:00:05Z"),
            ],
            traffic,
        )

        generate(run_dir, output_dir)
        [row] = load_corpus_rows(output_dir)
        rows.append(row)

    assert rows[0]["pre_normalization_hash"] != rows[1]["pre_normalization_hash"]
    assert rows[0]["normalized_hash"] == rows[1]["normalized_hash"]
    assert rows[0]["normalization_strategy"] == "manager_fixture_v1_binary_frame_signature.v1"
    assert rows[0]["normalized_frame_signature_count"] == 2
    assert rows[1]["normalized_frame_signature_count"] == 2
    assert rows[0]["response_markers"] == ["PF_FORM_MAIN"]
    assert rows[0]["preserved_fields"] == [
        {"name": "semantic_payload_token", "source": "payload_ascii", "value": "pf_form_main", "count": 2}
    ]


def test_response_markers_fall_back_to_binary_semantic_tokens(tmp_path: Path) -> None:
    run_dir = tmp_path / "semantic-token-run"
    output_dir = tmp_path / "semantic-token-evidence"
    active_window_command = command()
    active_window_command["target_marker"] = "MISSING_TARGET"
    active_window_command["expected_marker"] = "MISSING_EXPECTED"
    write_runtime(
        run_dir,
        [active_window_command],
        [
            event("tm-v1-active-window", "before", "2026-06-05T00:00:01Z"),
            event("tm-v1-active-window", "after", "2026-06-05T00:00:05Z"),
        ],
        [
            chunk(
                "client_to_manager",
                20,
                "2026-06-05T00:00:03Z",
                payload=b"B" + b"\x01" * 16 + b"HomePage[6ca75e50-62a3-4842-b6cd-b429f7591ef2]\x00",
            ),
        ],
    )

    generate(run_dir, output_dir)

    [row] = load_corpus_rows(output_dir)
    assert row["response_markers"] == ["homepage[<guid>]"]


def test_overlapping_event_windows_remain_unaccepted(tmp_path: Path) -> None:
    run_dir = tmp_path / "overlap-run"
    output_dir = tmp_path / "overlap-evidence"
    write_runtime(
        run_dir,
        [command("tm-v1-active-window"), command("tm-v1-active-form")],
        [
            event("tm-v1-active-window", "before", "2026-06-05T00:00:01Z"),
            event("tm-v1-active-form", "before", "2026-06-05T00:00:02Z"),
            event("tm-v1-active-window", "after", "2026-06-05T00:00:05Z"),
            event("tm-v1-active-form", "after", "2026-06-05T00:00:06Z"),
        ],
        [chunk("manager_to_client", 1, "2026-06-05T00:00:03Z")],
    )

    generate(run_dir, output_dir)

    cases = load_frame_report(output_dir)["cases"]
    assert {case["unresolved_reason"] for case in cases} == {"overlapping_case_window"}
    assert all(case["accepted_protocol_mapping"] is False for case in cases)


def test_missing_manager_result_is_synthesized_as_incomplete_runtime(tmp_path: Path) -> None:
    run_dir = tmp_path / "missing-result-run"
    output_dir = tmp_path / "missing-result-evidence"
    run_dir.mkdir()
    write_json(
        run_dir / "manager_harness_manifest.json",
        {
            "schema": "qa-mcp.manager-fixture-v1.manifest.v1",
            "run_id": run_dir.name,
            "fixture_version": "protocol-fixture.v1",
            "manager_harness": "DataProcessor.ProtocolFixtureTestManager.Form.ManagerHarness",
            "target_fixture_path": "DataProcessor.ProtocolFixtureTestClient.Form.Main",
            "proxy_testclient_port": 15382,
            "commands": [command()],
        },
    )
    write_json(
        run_dir / "manager_harness_invocation.json",
        {
            "schema": "qa-mcp.manager-fixture-v1.invocation.v1",
            "run_id": run_dir.name,
            "scenario": "manager-fixture-v1-readonly",
            "status": "invoking",
        },
    )
    write_jsonl(run_dir / "traffic.jsonl", [chunk("manager_to_client", 1, "2026-06-05T00:00:02Z")])

    generate(run_dir, output_dir)

    [case] = load_frame_report(output_dir)["cases"]
    assert case["join_status"] == "unresolved"
    assert case["unresolved_reason"] == "no_before_event"
    summary = json.loads((output_dir / "runtime_summary.json").read_text(encoding="utf-8"))
    assert summary["run_status"] == "harness_no_result"
    assert summary["unresolved_gaps"][0]["gap"] == "harness_no_result"


def test_pretty_json_case_event_file_is_tolerated(tmp_path: Path) -> None:
    run_dir = tmp_path / "pretty-event-run"
    output_dir = tmp_path / "pretty-event-evidence"
    run_dir.mkdir()
    write_json(
        run_dir / "manager_harness_manifest.json",
        {
            "schema": "qa-mcp.manager-fixture-v1.manifest.v1",
            "run_id": run_dir.name,
            "fixture_version": "protocol-fixture.v1",
            "manager_harness": "inline_generated_manager_fixture_v1",
            "target_fixture_path": "DataProcessor.ProtocolFixtureTestClient.Form.Main",
            "proxy_testclient_port": 15382,
            "commands": [command()],
        },
    )
    write_json(
        run_dir / "manager_harness_result.json",
        {
            "schema": "qa-mcp.manager-fixture-v1.result.v1",
            "run_id": run_dir.name,
            "scenario": "manager-fixture-v1-readonly",
            "status": "partial",
            "status_reason": "test fixture",
            "command_count": 1,
            "completed_count": 0,
            "failed_count": 1,
            "accepted_protocol_mapping": False,
        },
    )
    (run_dir / "case_events.jsonl").write_text(
        json.dumps(event("tm-v1-active-window", "before", "2026-06-05T00:00:01Z"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_jsonl(run_dir / "traffic.jsonl", [chunk("manager_to_client", 1, "2026-06-05T00:00:02Z")])

    generate(run_dir, output_dir)

    summary = json.loads((output_dir / "runtime_summary.json").read_text(encoding="utf-8"))
    assert summary["event_count"] == 1


def test_replay_probe_summary_promotes_matching_joined_case(tmp_path: Path) -> None:
    run_dir = tmp_path / "replay-run"
    pending_output_dir = tmp_path / "pending-evidence"
    accepted_output_dir = tmp_path / "accepted-evidence"
    case_id = "tm-v1-field-version"
    replay_command = command(case_id)
    replay_command["expected_marker"] = "protocol-fixture.v1"
    write_runtime(
        run_dir,
        [replay_command],
        [
            event(case_id, "before", "2026-06-05T00:00:01Z"),
            event(case_id, "after", "2026-06-05T00:00:03Z"),
        ],
        [
            chunk("manager_to_client", 120, "2026-06-05T00:00:02Z", payload=b"A" + b"\x01" * 16 + b"pf_fixture_version"),
            chunk("client_to_manager", 121, "2026-06-05T00:00:02.500Z", payload=b"B" + b"\x02" * 16 + b"protocol-fixture.v1"),
        ],
    )

    generate(run_dir, pending_output_dir)
    [pending_case] = load_frame_report(pending_output_dir)["cases"]
    [pending_row] = load_corpus_rows(pending_output_dir)
    assert pending_case["replay_status"] == "pending"
    assert pending_row["accepted_protocol_mapping"] is False

    replay_summary_path = tmp_path / "replay-summary.json"
    write_json(
        replay_summary_path,
        {
            "schema": "qa-mcp.manager-fixture-v1.replay-probe-summary.v1",
            "source_capture": "runtime/protocol-research/captures/test-run",
            "successful_replay_dir": "runtime/protocol-research/replay-probe/test-run",
            "transport_status": "ok",
            "no_response_frames": [],
            "observed_dynamic_fields": {"ack_guid_after_send_3": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"},
            "adaptation": {"ui_path_guids": True},
            "accepted_probe_cases": [
                {
                    "case_id": case_id,
                    "manager_frame_range": {"from": 120, "to": 120},
                    "response_after_send": 120,
                    "response_size": 128,
                    "expected_marker": "protocol-fixture.v1",
                    "normalized_hash": pending_case["normalized_hash"],
                    "replay_status": "accepted_probe",
                }
            ],
        },
    )

    generate(run_dir, accepted_output_dir, [replay_summary_path])

    [accepted_case] = load_frame_report(accepted_output_dir)["cases"]
    assert accepted_case["replay_status"] == "accepted_probe"
    assert accepted_case["accepted_protocol_mapping"] is True
    assert accepted_case["replay_evidence"]["validation_status"] == "accepted"
    assert accepted_case["replay_evidence"]["response_after_send"] == 120

    [accepted_row] = load_corpus_rows(accepted_output_dir)
    assert accepted_row["availability"] == "available"
    assert accepted_row["probe_status"] == "accepted"
    assert accepted_row["accepted_protocol_mapping"] is True
    assert accepted_row["acceptance_evidence"] == [
        "replay_probe_status=accepted_probe",
        f"replay_probe_summary={replay_summary_path}",
        "response_after_send=120",
    ]

    summary = json.loads((accepted_output_dir / "runtime_summary.json").read_text(encoding="utf-8"))
    assert summary["accepted_protocol_mapping"] is True
    assert summary["accepted_case_ids"] == [case_id]


def test_side_channel_result_preview_contract_promotes_joined_case(tmp_path: Path) -> None:
    run_dir = tmp_path / "side-channel-run"
    output_dir = tmp_path / "side-channel-evidence"
    case_id = "tm-v1-diag-window-children"
    count_command = command(case_id)
    count_command["command_id"] = "diagnostic_window_children"
    count_command["command_kind"] = "diagnostic_window_children"
    count_command["expected_marker"] = "window_children_count="
    count_command["acceptance_contract"] = {
        "kind": "manager_result_preview_contains",
        "expected_result_preview_marker": "window_children_count=",
        "evidence_source": "manager_case_event.after.result_preview",
    }
    before = event(case_id, "before", "2026-06-05T00:00:01Z")
    after = event(case_id, "after", "2026-06-05T00:00:03Z")
    after["result_preview"] = "window_children_count=1"
    write_runtime(
        run_dir,
        [count_command],
        [before, after],
        [
            chunk("manager_to_client", 20, "2026-06-05T00:00:02Z", payload=b"A" + b"\x01" * 16 + b"homepage"),
            chunk("client_to_manager", 21, "2026-06-05T00:00:02.500Z", payload=b"B" + b"\x02" * 16 + b"homepage"),
        ],
    )

    generate(run_dir, output_dir)

    [case] = load_frame_report(output_dir)["cases"]
    assert case["accepted_protocol_mapping"] is True
    assert case["replay_status"] == "accepted_side_channel"
    assert case["side_channel_evidence"]["validation_status"] == "accepted"
    assert case["side_channel_evidence"]["observed_result_preview"] == "window_children_count=1"

    [row] = load_corpus_rows(output_dir)
    assert row["availability"] == "available"
    assert row["probe_status"] == "accepted"
    assert row["acceptance_evidence"] == [
        "side_channel_contract_status=accepted",
        "side_channel_contract_kind=manager_result_preview_contains",
        "result_preview_marker=window_children_count=",
    ]

    summary_md = (output_dir / "runtime_summary.md").read_text(encoding="utf-8")
    assert "typed side-channel evidence" in summary_md
    frame_md = (output_dir / "frame_join_report.md").read_text(encoding="utf-8")
    assert "`accepted_side_channel` means" in frame_md


def test_side_channel_result_preview_contract_requires_marker(tmp_path: Path) -> None:
    run_dir = tmp_path / "side-channel-mismatch-run"
    output_dir = tmp_path / "side-channel-mismatch-evidence"
    case_id = "tm-v1-diag-window-children"
    count_command = command(case_id)
    count_command["expected_marker"] = "window_children_count="
    count_command["acceptance_contract"] = {
        "kind": "manager_result_preview_contains",
        "expected_result_preview_marker": "window_children_count=",
    }
    before = event(case_id, "before", "2026-06-05T00:00:01Z")
    after = event(case_id, "after", "2026-06-05T00:00:03Z")
    after["result_preview"] = "window_title=QA MCP Protocol Fixture V1"
    write_runtime(
        run_dir,
        [count_command],
        [before, after],
        [
            chunk("manager_to_client", 20, "2026-06-05T00:00:02Z", payload=b"A" + b"\x01" * 16 + b"homepage"),
            chunk("client_to_manager", 21, "2026-06-05T00:00:02.500Z", payload=b"B" + b"\x02" * 16 + b"homepage"),
        ],
    )

    generate(run_dir, output_dir)

    [case] = load_frame_report(output_dir)["cases"]
    assert case["accepted_protocol_mapping"] is False
    assert case["direct_probe_status"] == "side_channel_mismatch"
    assert case["side_channel_evidence"]["validation_mismatches"] == ["result_preview_marker_missing"]

    [row] = load_corpus_rows(output_dir)
    assert row["availability"] == "pending"
    assert row["accepted_protocol_mapping"] is False
