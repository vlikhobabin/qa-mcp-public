from __future__ import annotations

import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools" / "protocol-research"
sys.path.insert(0, str(TOOLS_DIR))

from compare_corpus_runs import compare_inputs, load_probe_evidence, load_request_hash_evidence  # noqa: E402


def write_cases(path: Path, rows: list[dict[str, object]]) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def row(
    case_id: str,
    capture_id: str,
    normalized_hash: str | None,
    replay_status: str = "accepted",
    availability: str = "supported",
    ambiguous_fields: list[dict[str, object]] | None = None,
    response_markers: list[str] | None = None,
    expected_response_markers: list[str] | None = None,
) -> dict[str, object]:
    return {
        "case_id": case_id,
        "capture_id": capture_id,
        "evidence_path": f"docs/protocol-research/evidence/corpus/{capture_id}",
        "availability": availability,
        "replay_status": replay_status,
        "normalized_hash": normalized_hash,
        "request_size": 100 if normalized_hash else 0,
        "response_size": 200 if normalized_hash else 0,
        "operation_token": {"values": [{"hex": "aa"}]} if normalized_hash else None,
        "response_markers": response_markers if response_markers is not None else ["HomePage"] if normalized_hash else [],
        "expected_response_markers": expected_response_markers or [],
        "dynamic_fields": [],
        "ambiguous_fields": ambiguous_fields or [],
        "frame_range": None if normalized_hash is None else {"manager_to_client": {"from": 1, "to": 1}},
    }


def safe_action_row(
    case_id: str,
    capture_id: str,
    normalized_hash: str | None,
    replay_status: str = "pending",
    action_status: str = "pending",
    action_frame_range: dict[str, object] | None = None,
    acceptance_evidence: list[str] | None = None,
) -> dict[str, object]:
    value = row(case_id, capture_id, normalized_hash, replay_status)
    value.update(
        {
            "safety_class": "safe_ui_action",
            "api_call": "activate_window",
            "pre_state": {"kind": "active_window"},
            "action": "activate_window",
            "post_state": {"kind": "active_window"},
            "recovery_expectation": {"kind": "reactivate_original_window"},
            "action_result_markers": [f"status={action_status}", "window_title_observed"],
            "action_frame_range": action_frame_range,
            "background_frame_ranges": [],
            "action_runtime_result": {"status": action_status},
            "acceptance_evidence": acceptance_evidence or [],
        }
    )
    return value


def write_request_hash_evidence(path: Path) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema": "readonly-element-request-hashes.v1",
                "rows": [
                    {
                        "case_id": "typed-input-field-readonly",
                        "query": "form-element-details",
                        "normalized_hash": "hash-extracted",
                        "replay_status": "accepted",
                        "notes": "Typed input needs operation join review.",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_compare_inputs_classifies_stable_and_incomplete(tmp_path: Path) -> None:
    left = tmp_path / "left" / "corpus_cases.jsonl"
    right = tmp_path / "right" / "corpus_cases.jsonl"
    write_cases(left, [row("active-window-context", "run-a", "hash-a"), row("typed-input-field-readonly", "run-a", "hash-b")])
    write_cases(right, [row("active-window-context", "run-b", "hash-a"), row("typed-input-field-readonly", "run-b", None, "pending")])

    comparison = compare_inputs([left, right], tmp_path)
    by_case = {case["case_id"]: case for case in comparison["cases"]}

    assert by_case["active-window-context"]["classification"] == "stable"
    assert by_case["active-window-context"]["precise_reasons"] == ["accepted_reviewed_hash"]
    assert by_case["typed-input-field-readonly"]["classification"] == "incomplete_hash"
    assert by_case["typed-input-field-readonly"]["precise_reasons"] == ["missing_request_frames"]
    assert comparison["classification_counts"] == {"incomplete_hash": 1, "stable": 1}


def test_compare_inputs_detects_missing_cases(tmp_path: Path) -> None:
    left = tmp_path / "left" / "corpus_cases.jsonl"
    right = tmp_path / "right" / "corpus_cases.jsonl"
    write_cases(left, [row("active-window-context", "run-a", "hash-a"), row("active-form-context", "run-a", "hash-b")])
    write_cases(right, [row("active-window-context", "run-b", "hash-a")])

    comparison = compare_inputs([left, right], tmp_path)
    by_case = {case["case_id"]: case for case in comparison["cases"]}

    assert by_case["active-form-context"]["classification"] == "missing_case"
    assert by_case["active-form-context"]["missing_inputs"] == [1]
    assert by_case["active-form-context"]["precise_reasons"] == ["missing_request_frames"]


def test_probe_evidence_promotes_repeated_pending_rows(tmp_path: Path) -> None:
    left = tmp_path / "left" / "corpus_cases.jsonl"
    right = tmp_path / "right" / "corpus_cases.jsonl"
    write_cases(left, [row("active-window-context", "run-a", "hash-a", "pending")])
    write_cases(right, [row("active-window-context", "run-b", "hash-a", "pending")])
    probe_path = tmp_path / "probe" / "python_manager_probe_result.json"
    probe_path.parent.mkdir(parents=True)
    probe_path.write_text(
        """
        {
          "status": "ok",
          "query": "form-element-details",
          "capture_dir": "runtime/protocol-research/captures/20260602-084433",
          "frames": [{"semantic_guess": "main_frame_with_home_page", "ui_identifiers": ["MainFrame"]}],
          "active_form_name": "Report.Form",
          "managed_form_ref": "ManagedForm",
          "element_detail_count": 2,
          "frame_mode": "short"
        }
        """,
        encoding="utf-8",
    )

    comparison = compare_inputs([left, right], tmp_path, load_probe_evidence([probe_path], tmp_path))
    by_case = {case["case_id"]: case for case in comparison["cases"]}

    assert by_case["active-window-context"]["classification"] == "stable"
    assert by_case["active-window-context"]["effective_replay_statuses"] == ["accepted"]
    assert by_case["active-window-context"]["probe_evidence_paths"] == [
        "probe/python_manager_probe_result.json"
    ]


def test_probe_evidence_alias_promotes_manager_fixture_active_window(tmp_path: Path) -> None:
    left = tmp_path / "left" / "corpus_cases.jsonl"
    right = tmp_path / "right" / "corpus_cases.jsonl"
    manager_row_a = row(
        "tm-v1-active-window",
        "run-a",
        "hash-a",
        "pending",
        response_markers=["QA MCP Protocol Fixture V1"],
        expected_response_markers=["QA MCP Protocol Fixture V1"],
    )
    manager_row_b = row(
        "tm-v1-active-window",
        "run-b",
        "hash-a",
        "pending",
        response_markers=["QA MCP Protocol Fixture V1"],
        expected_response_markers=["QA MCP Protocol Fixture V1"],
    )
    write_cases(left, [manager_row_a])
    write_cases(right, [manager_row_b])
    probe_path = tmp_path / "probe" / "python_manager_probe_result.json"
    probe_path.parent.mkdir(parents=True)
    probe_path.write_text(
        """
        {
          "status": "ok",
          "query": "active-window-context",
          "capture_dir": "runtime/protocol-research/captures/20260602-084433",
          "frames": [
            {
              "semantic_guess": "main_frame_with_home_page",
              "ui_identifiers": ["e1cib/app/Обработка.ФикстураПротоколаTestClient"],
              "ascii_strings": ["QA MCP Protocol Fixture V1"]
            }
          ],
          "active_window_markers": ["e1cib/app/Обработка.ФикстураПротоколаTestClient"]
        }
        """,
        encoding="utf-8",
    )

    comparison = compare_inputs([left, right], tmp_path, load_probe_evidence([probe_path], tmp_path))
    by_case = {case["case_id"]: case for case in comparison["cases"]}
    observations = by_case["tm-v1-active-window"]["observations"]

    assert by_case["tm-v1-active-window"]["classification"] == "stable"
    assert by_case["tm-v1-active-window"]["effective_replay_statuses"] == ["accepted"]
    assert observations[0]["probe_evidence"]["source_case_id"] == "active-window-context"
    assert "QA MCP Protocol Fixture V1" in observations[0]["probe_evidence"]["response_markers"]


def test_probe_evidence_alias_does_not_promote_when_expected_marker_missing(tmp_path: Path) -> None:
    left = tmp_path / "left" / "corpus_cases.jsonl"
    right = tmp_path / "right" / "corpus_cases.jsonl"
    manager_row_a = row(
        "tm-v1-active-window",
        "run-a",
        "hash-a",
        "pending",
        response_markers=["homepage[<guid>]", "e1cib/navigationpoint/startpage"],
        expected_response_markers=["QA MCP Protocol Fixture V1"],
    )
    manager_row_b = {
        **manager_row_a,
        "capture_id": "run-b",
        "evidence_path": "docs/protocol-research/evidence/corpus/run-b",
    }
    write_cases(left, [manager_row_a])
    write_cases(right, [manager_row_b])
    probe_path = tmp_path / "probe" / "python_manager_probe_result.json"
    probe_path.parent.mkdir(parents=True)
    probe_path.write_text(
        """
        {
          "status": "ok",
          "query": "active-window-context",
          "capture_dir": "runtime/protocol-research/captures/20260602-084433",
          "frames": [
            {
              "semantic_guess": "main_frame_with_home_page",
              "ui_identifiers": ["e1cib/app/РћР±СЂР°Р±РѕС‚РєР°.Р¤РёРєСЃС‚СѓСЂР°РџСЂРѕС‚РѕРєРѕР»Р°TestClient"],
              "ascii_strings": ["QA MCP Protocol Fixture V1"]
            }
          ],
          "active_window_markers": ["e1cib/app/РћР±СЂР°Р±РѕС‚РєР°.Р¤РёРєСЃС‚СѓСЂР°РџСЂРѕС‚РѕРєРѕР»Р°TestClient"]
        }
        """,
        encoding="utf-8",
    )

    comparison = compare_inputs([left, right], tmp_path, load_probe_evidence([probe_path], tmp_path))
    by_case = {case["case_id"]: case for case in comparison["cases"]}

    assert by_case["tm-v1-active-window"]["classification"] == "non_accepted"
    assert by_case["tm-v1-active-window"]["effective_replay_statuses"] == ["pending"]
    assert by_case["tm-v1-active-window"]["unresolved_reasons"] == [
        "expected_response_marker_not_observed",
        "probe_marker_mismatch",
    ]


def test_generic_case_probe_evidence_promotes_matching_manager_marker_row(tmp_path: Path) -> None:
    left = tmp_path / "left" / "corpus_cases.jsonl"
    right = tmp_path / "right" / "corpus_cases.jsonl"
    write_cases(
        left,
        [
            row(
                "tm-v1-active-form",
                "run-a",
                "hash-a",
                "pending",
                response_markers=["PF_FORM_MAIN"],
                expected_response_markers=["PF_FORM_MAIN"],
            )
        ],
    )
    write_cases(
        right,
        [
            row(
                "tm-v1-active-form",
                "run-b",
                "hash-a",
                "pending",
                response_markers=["PF_FORM_MAIN"],
                expected_response_markers=["PF_FORM_MAIN"],
            )
        ],
    )
    probe_path = tmp_path / "probe" / "manager_fixture_marker_probe_result.json"
    probe_path.parent.mkdir(parents=True)
    probe_path.write_text(
        """
        {
          "schema": "protocol-case-probe-evidence.v1",
          "kind": "direct_python_manager_marker_replay",
          "status": "ok",
          "probe_status": "accepted",
          "case_id": "tm-v1-active-form",
          "query": "manager-fixture-marker",
          "capture_dir": "runtime/protocol-research/captures/run-a",
          "response_markers": ["PF_FORM_MAIN"],
          "response_marker_count": 1
        }
        """,
        encoding="utf-8",
    )

    comparison = compare_inputs([left, right], tmp_path, load_probe_evidence([probe_path], tmp_path))
    by_case = {case["case_id"]: case for case in comparison["cases"]}

    assert by_case["tm-v1-active-form"]["classification"] == "stable"
    assert by_case["tm-v1-active-form"]["effective_replay_statuses"] == ["accepted"]
    assert by_case["tm-v1-active-form"]["probe_evidence_paths"] == [
        "probe/manager_fixture_marker_probe_result.json"
    ]


def test_rejected_generic_probe_evidence_does_not_report_promotion(tmp_path: Path) -> None:
    left = tmp_path / "left" / "corpus_cases.jsonl"
    right = tmp_path / "right" / "corpus_cases.jsonl"
    write_cases(
        left,
        [
            row(
                "tm-v1-form-summary",
                "run-a",
                "hash-a",
                "pending",
                response_markers=["PF_FORM_MAIN"],
                expected_response_markers=["PF_FORM_MAIN", "PF_FIXTURE_VERSION"],
            )
        ],
    )
    write_cases(
        right,
        [
            row(
                "tm-v1-form-summary",
                "run-b",
                "hash-a",
                "pending",
                response_markers=["PF_FORM_MAIN"],
                expected_response_markers=["PF_FORM_MAIN", "PF_FIXTURE_VERSION"],
            )
        ],
    )
    probe_path = tmp_path / "probe" / "manager_fixture_marker_probe_result.json"
    probe_path.parent.mkdir(parents=True)
    probe_path.write_text(
        """
        {
          "schema": "protocol-case-probe-evidence.v1",
          "kind": "direct_python_manager_marker_replay",
          "status": "ok",
          "probe_status": "rejected",
          "case_id": "tm-v1-form-summary",
          "query": "manager-fixture-marker",
          "capture_dir": "runtime/protocol-research/captures/run-a",
          "expected_marker": "PF_FIXTURE_VERSION",
          "response_markers": ["PF_FORM_MAIN"],
          "response_marker_count": 1
        }
        """,
        encoding="utf-8",
    )

    comparison = compare_inputs([left, right], tmp_path, load_probe_evidence([probe_path], tmp_path))
    by_case = {case["case_id"]: case for case in comparison["cases"]}

    assert by_case["tm-v1-form-summary"]["classification"] == "non_accepted"
    assert by_case["tm-v1-form-summary"]["effective_replay_statuses"] == ["rejected"]
    assert by_case["tm-v1-form-summary"]["unresolved_reasons"] == []


def test_probe_evidence_does_not_accept_incomplete_hash_rows(tmp_path: Path) -> None:
    left = tmp_path / "left" / "corpus_cases.jsonl"
    right = tmp_path / "right" / "corpus_cases.jsonl"
    write_cases(left, [row("typed-input-field-readonly", "run-a", None, "pending")])
    write_cases(right, [row("typed-input-field-readonly", "run-b", None, "pending")])
    probe_path = tmp_path / "probe" / "python_manager_probe_result.json"
    probe_path.parent.mkdir(parents=True)
    probe_path.write_text(
        """
        {
          "status": "ok",
          "query": "form-element-details",
          "capture_dir": "runtime/protocol-research/captures/20260602-084433",
          "frames": [{"semantic_guess": "main_frame_with_home_page"}],
          "active_form_name": "Report.Form",
          "managed_form_ref": "ManagedForm",
          "element_detail_count": 2,
          "frame_mode": "short"
        }
        """,
        encoding="utf-8",
    )

    comparison = compare_inputs([left, right], tmp_path, load_probe_evidence([probe_path], tmp_path))
    by_case = {case["case_id"]: case for case in comparison["cases"]}

    assert by_case["typed-input-field-readonly"]["classification"] == "incomplete_hash"
    assert by_case["typed-input-field-readonly"]["effective_replay_statuses"] == ["accepted"]
    assert by_case["typed-input-field-readonly"]["unresolved_reasons"] == [
        "accepted_probe_without_reviewed_request_hash",
        "row_status_promoted_from_pending_by_probe_evidence",
    ]


def test_request_hash_evidence_refines_incomplete_element_reason(tmp_path: Path) -> None:
    left = tmp_path / "left" / "corpus_cases.jsonl"
    right = tmp_path / "right" / "corpus_cases.jsonl"
    write_cases(left, [row("typed-input-field-readonly", "run-a", None, "pending")])
    write_cases(right, [row("typed-input-field-readonly", "run-b", None, "pending")])
    request_hash_path = tmp_path / "request-hashes" / "request_hashes.json"
    write_request_hash_evidence(request_hash_path)

    comparison = compare_inputs(
        [left, right],
        tmp_path,
        request_hash_evidence_by_case=load_request_hash_evidence([request_hash_path], tmp_path),
    )
    by_case = {case["case_id"]: case for case in comparison["cases"]}

    assert by_case["typed-input-field-readonly"]["classification"] == "incomplete_hash"
    assert by_case["typed-input-field-readonly"]["precise_reasons"] == [
        "accepted_reviewed_hash",
        "ambiguous_operation_join",
        "missing_request_frames",
    ]
    assert by_case["typed-input-field-readonly"]["provider_owners"] == [
        "/opt/vanessa-mcp-stack",
        "project:qa-mcp",
    ]
    assert by_case["typed-input-field-readonly"]["request_hash_evidence_paths"] == [
        "request-hashes/request_hashes.json"
    ]


def test_precise_reasons_cover_unsupported_fixture_state(tmp_path: Path) -> None:
    left = tmp_path / "left" / "corpus_cases.jsonl"
    right = tmp_path / "right" / "corpus_cases.jsonl"
    write_cases(left, [row("fixture-button-readonly", "run-a", None, "unsupported", "unsupported")])
    write_cases(right, [row("fixture-button-readonly", "run-b", None, "unsupported", "unsupported")])

    comparison = compare_inputs([left, right], tmp_path)
    by_case = {case["case_id"]: case for case in comparison["cases"]}

    assert by_case["fixture-button-readonly"]["classification"] == "unsupported_gap"
    assert by_case["fixture-button-readonly"]["precise_reasons"] == ["unsupported_fixture_state"]


def test_precise_reasons_cover_incomplete_normalizer_coverage(tmp_path: Path) -> None:
    left = tmp_path / "left" / "corpus_cases.jsonl"
    right = tmp_path / "right" / "corpus_cases.jsonl"
    write_cases(
        left,
        [row("form-element-details", "run-a", "hash-a", ambiguous_fields=[{"name": "opaque"}])],
    )
    write_cases(right, [row("form-element-details", "run-b", "hash-b")])

    comparison = compare_inputs([left, right], tmp_path)
    by_case = {case["case_id"]: case for case in comparison["cases"]}

    assert by_case["form-element-details"]["classification"] == "divergent_hash"
    assert by_case["form-element-details"]["precise_reasons"] == [
        "incomplete_normalizer_coverage"
    ]


def test_safe_action_pending_row_stays_non_accepted(tmp_path: Path) -> None:
    cases = tmp_path / "safe-action" / "corpus_cases.jsonl"
    write_cases(
        cases,
        [
            safe_action_row(
                "safe-activate-existing-window",
                "run-a",
                None,
                "pending",
                "pending",
            )
        ],
    )

    comparison = compare_inputs([cases], tmp_path)
    by_case = {case["case_id"]: case for case in comparison["cases"]}

    action_case = by_case["safe-activate-existing-window"]
    assert action_case["classification"] == "pending"
    assert action_case["safe_action_statuses"] == ["pending"]
    assert comparison["accepted_case_ids"] == []
    assert comparison["gap_case_ids"] == ["safe-activate-existing-window"]
    assert action_case["precise_reasons"] == [
        "missing_action_frame_range",
        "missing_request_frames",
        "missing_safe_action_hash",
        "pending_action_result",
        "replay_or_probe_unavailable",
    ]


def test_safe_action_requires_action_frame_and_hash_for_acceptance(tmp_path: Path) -> None:
    cases = tmp_path / "safe-action" / "corpus_cases.jsonl"
    write_cases(
        cases,
        [
            safe_action_row(
                "safe-activate-existing-window",
                "run-a",
                "hash-a",
                "accepted",
                "accepted",
                {"manager_to_client": {"from": 10, "to": 11}},
                ["docs/protocol-research/evidence/probe/accepted-summary.json"],
            )
        ],
    )

    comparison = compare_inputs([cases], tmp_path)
    by_case = {case["case_id"]: case for case in comparison["cases"]}

    action_case = by_case["safe-activate-existing-window"]
    assert action_case["classification"] == "accepted"
    assert action_case["precise_reasons"] == ["accepted_reviewed_hash"]
    assert comparison["accepted_case_ids"] == ["safe-activate-existing-window"]


def test_safe_action_accepted_status_without_proof_stays_non_accepted(tmp_path: Path) -> None:
    cases = tmp_path / "safe-action" / "corpus_cases.jsonl"
    write_cases(
        cases,
        [
            safe_action_row(
                "safe-activate-existing-window",
                "run-a",
                "hash-a",
                "accepted",
                "accepted",
                {"manager_to_client": {"from": 10, "to": 11}},
            )
        ],
    )

    comparison = compare_inputs([cases], tmp_path)
    by_case = {case["case_id"]: case for case in comparison["cases"]}

    action_case = by_case["safe-activate-existing-window"]
    assert action_case["classification"] == "pending"
    assert action_case["precise_reasons"] == [
        "missing_safe_action_acceptance_proof",
        "replay_or_probe_unavailable",
    ]
    assert comparison["accepted_case_ids"] == []
