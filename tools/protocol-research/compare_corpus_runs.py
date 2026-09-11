#!/usr/bin/env python3
"""Compare reviewed protocol corpus rows across repeated captures."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "protocol-corpus-comparison.v1"

PROVIDER_OWNER_BY_REASON = {
    "accepted_reviewed_hash": "project:qa-mcp",
    "ambiguous_operation_join": "project:qa-mcp",
    "incomplete_normalizer_coverage": "project:qa-mcp",
    "missing_action_frame_range": "/opt/vanessa-mcp-stack",
    "missing_action_result_markers": "/opt/vanessa-mcp-stack",
    "missing_safe_action_acceptance_proof": "project:qa-mcp",
    "missing_safe_action_hash": "project:qa-mcp",
    "missing_request_frames": "/opt/vanessa-mcp-stack",
    "pending_action_result": "/opt/vanessa-mcp-stack",
    "replay_or_probe_unavailable": "project:qa-mcp",
    "runtime_unavailable": "/opt/vanessa-mcp-stack",
    "unsupported_fixture_state": "/opt/vanessa-mcp-stack",
}

SAFE_ACTION_STATUSES = {
    "accepted",
    "pending",
    "unsupported",
    "partial",
    "timeout",
    "rejected",
    "blocked",
}

PROBE_CASE_ALIASES = {
    "active-window-context": ["tm-v1-active-window"],
}
GUID_TOKEN_RE = re.compile(r"\[[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\]")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def timestamp_name() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_cases_path(value: str | Path, repo_root: Path) -> Path:
    path = Path(value)
    candidates = [path]
    if not path.is_absolute():
        candidates.append(repo_root / path)
    for candidate in candidates:
        if candidate.is_dir():
            cases_path = candidate / "corpus_cases.jsonl"
            if cases_path.exists():
                return cases_path.resolve()
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError(f"corpus_cases.jsonl input not found: {value}")


def repo_relative_path(path: Path, repo_root: Path) -> str:
    resolved = path.resolve()
    if resolved.is_relative_to(repo_root):
        return str(resolved.relative_to(repo_root)).replace("\\", "/")
    return str(resolved)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as file_obj:
        for line in file_obj:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def json_fingerprint(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def unique_json_values(values: Iterable[Any]) -> list[Any]:
    seen: dict[str, Any] = {}
    for value in values:
        seen.setdefault(json_fingerprint(value), value)
    return [seen[key] for key in sorted(seen)]


def operation_token_values(row: dict[str, Any]) -> list[str]:
    token = row.get("operation_token") or {}
    return sorted(
        {
            value.get("hex", "")
            for value in token.get("values", [])
            if value.get("hex")
        }
    )


def dynamic_field_summary(row: dict[str, Any]) -> list[dict[str, Any]]:
    counters: Counter[tuple[str, str, str, int]] = Counter()
    for field in row.get("dynamic_fields", []):
        counters[
            (
                field.get("name", ""),
                field.get("source", ""),
                field.get("replacement", ""),
                int(field.get("length") or 0),
            )
        ] += 1
    return [
        {
            "name": name,
            "source": source,
            "replacement": replacement,
            "length": length,
            "count": count,
        }
        for (name, source, replacement, length), count in sorted(counters.items())
    ]


def compact_probe_markers(probe_result: dict[str, Any], limit: int = 12) -> list[str]:
    markers: list[str] = []

    def add_marker(value: Any) -> None:
        normalized = str(value).strip()
        if normalized and normalized not in markers:
            markers.append(normalized)

    for frame in probe_result.get("frames", []):
        semantic_guess = frame.get("semantic_guess")
        if semantic_guess:
            add_marker(semantic_guess)
        for value in frame.get("ui_identifiers", []):
            add_marker(value)
        for value in frame.get("ascii_strings", []):
            add_marker(value)
        for value in frame.get("utf16le_strings", []):
            if isinstance(value, dict):
                add_marker(value.get("text"))
            else:
                add_marker(value)
        if len(markers) >= limit:
            return markers[:limit]
    for value in probe_result.get("active_window_markers", []) or []:
        add_marker(value)
    for key in ("active_window_ref", "active_form_name", "active_form_caption", "managed_form_ref"):
        value = probe_result.get(key)
        if value:
            add_marker(value)
    return markers[:limit]


def probe_case_statuses(probe_result: dict[str, Any]) -> dict[str, str]:
    if probe_result.get("status") != "ok":
        return {
            "active-window-context": "rejected",
            "active-form-context": "rejected",
            "form-element-details": "rejected",
            "typed-input-field-readonly": "rejected",
        }
    has_main_frame = any(
        frame.get("semantic_guess") == "main_frame_with_home_page"
        for frame in probe_result.get("frames", [])
    )
    has_active_form = bool(probe_result.get("active_form_name") and probe_result.get("managed_form_ref"))
    has_element_details = int(probe_result.get("element_detail_count") or 0) > 0
    return {
        "active-window-context": "accepted" if has_main_frame else "partial",
        "active-form-context": "accepted" if has_active_form else "partial",
        "form-element-details": "accepted" if has_element_details else "partial",
        "typed-input-field-readonly": "accepted" if has_element_details else "partial",
    }


def load_probe_evidence(paths: Iterable[Path], repo_root: Path) -> dict[str, dict[str, Any]]:
    evidence_by_case: dict[str, dict[str, Any]] = {}
    for path in paths:
        resolved = path.resolve()
        probe_result = read_json(resolved)
        if probe_result.get("schema") == "protocol-case-probe-evidence.v1":
            case_id = str(probe_result.get("case_id") or "")
            if not case_id:
                continue
            evidence_by_case[case_id] = {
                "kind": probe_result.get("kind") or "probe",
                "status": probe_result.get("probe_status") or probe_result.get("status"),
                "query": probe_result.get("query"),
                "case_id": case_id,
                "evidence_path": repo_relative_path(resolved, repo_root),
                "source_capture_id": Path(str(probe_result.get("capture_dir") or "")).name or None,
                "frame_mode": probe_result.get("frame_mode"),
                "response_markers": probe_result.get("response_markers", []),
                "response_marker_count": int(probe_result.get("response_marker_count") or 0),
                "notes": probe_result.get("notes"),
            }
            continue
        markers = compact_probe_markers(probe_result)
        source_capture = probe_result.get("capture_dir")
        source_capture_id = Path(source_capture).name if source_capture else None
        for case_id, status in probe_case_statuses(probe_result).items():
            evidence = {
                "kind": "direct_python_manager",
                "status": status,
                "query": probe_result.get("query") or "form-element-details",
                "case_id": case_id,
                "evidence_path": repo_relative_path(resolved, repo_root),
                "source_capture_id": source_capture_id,
                "frame_mode": probe_result.get("frame_mode"),
                "response_markers": markers,
                "response_marker_count": len(markers),
            }
            evidence_by_case[case_id] = evidence
            for alias_case_id in PROBE_CASE_ALIASES.get(case_id, []):
                evidence_by_case[alias_case_id] = {
                    **evidence,
                    "case_id": alias_case_id,
                    "source_case_id": case_id,
                    "notes": f"Probe evidence mapped from operation-family case {case_id}.",
                }
    return evidence_by_case


def load_request_hash_evidence(paths: Iterable[Path], repo_root: Path) -> dict[str, dict[str, Any]]:
    evidence_by_case: dict[str, dict[str, Any]] = {}
    for path in paths:
        resolved = path.resolve()
        evidence = read_json(resolved)
        for row in evidence.get("rows", []):
            case_id = str(row.get("case_id") or "")
            if not case_id:
                continue
            evidence_by_case[case_id] = {
                **row,
                "kind": "readonly_element_request_hash",
                "evidence_path": repo_relative_path(resolved, repo_root),
            }
    return evidence_by_case


def load_input(path: Path, input_index: int, repo_root: Path) -> dict[str, Any]:
    rows = read_jsonl(path)
    by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_case[row["case_id"]].append(row)
    capture_ids = sorted({str(row.get("capture_id", "")) for row in rows if row.get("capture_id")})
    return {
        "input_index": input_index,
        "cases_path": str(path.relative_to(repo_root)).replace("\\", "/")
        if path.is_relative_to(repo_root)
        else str(path),
        "evidence_dir": str(path.parent.relative_to(repo_root)).replace("\\", "/")
        if path.parent.is_relative_to(repo_root)
        else str(path.parent),
        "capture_ids": capture_ids,
        "rows": rows,
        "rows_by_case": dict(by_case),
    }


def normalize_marker(value: Any) -> str:
    marker = GUID_TOKEN_RE.sub("[<guid>]", str(value).strip().lower())
    return " ".join(marker.split())


def marker_values_match(left: Any, right: Any) -> bool:
    left_marker = normalize_marker(left)
    right_marker = normalize_marker(right)
    if not left_marker or not right_marker:
        return False
    return left_marker == right_marker or left_marker in right_marker or right_marker in left_marker


def any_marker_match(left_values: Iterable[Any], right_values: Iterable[Any]) -> bool:
    left_list = [value for value in left_values if str(value).strip()]
    right_list = [value for value in right_values if str(value).strip()]
    return any(marker_values_match(left, right) for left in left_list for right in right_list)


def expected_markers_observed(row: dict[str, Any]) -> bool:
    expected = row.get("expected_response_markers") or []
    if not expected:
        return True
    return any_marker_match(expected, row.get("response_markers") or [])


def probe_markers_compatible(row: dict[str, Any], probe_evidence: dict[str, Any] | None) -> bool:
    if not probe_evidence:
        return True
    source_case_id = probe_evidence.get("source_case_id")
    if not source_case_id or source_case_id == row.get("case_id"):
        return True
    return any_marker_match(row.get("response_markers") or [], probe_evidence.get("response_markers") or [])


def probe_can_promote_row(row: dict[str, Any], probe_evidence: dict[str, Any] | None) -> bool:
    return expected_markers_observed(row) and probe_markers_compatible(row, probe_evidence)


def effective_replay_status(row: dict[str, Any], probe_evidence: dict[str, Any] | None) -> str | None:
    replay_status = row.get("replay_status")
    if not probe_evidence:
        return replay_status
    if not probe_can_promote_row(row, probe_evidence):
        return replay_status
    probe_status = probe_evidence.get("status")
    if replay_status in {None, "pending", "partial"} and probe_status in {
        "accepted",
        "partial",
        "rejected",
        "timeout",
    }:
        return str(probe_status)
    return replay_status


def unresolved_reasons_for_row(row: dict[str, Any], probe_evidence: dict[str, Any] | None) -> list[str]:
    reasons: list[str] = []
    if probe_evidence and probe_evidence.get("status") == "accepted" and not row.get("normalized_hash"):
        reasons.append("accepted_probe_without_reviewed_request_hash")
    if probe_evidence and not expected_markers_observed(row):
        reasons.append("expected_response_marker_not_observed")
    if probe_evidence and not probe_markers_compatible(row, probe_evidence):
        reasons.append("probe_marker_mismatch")
    if (
        probe_evidence
        and probe_evidence.get("status") == "accepted"
        and row.get("replay_status") == "pending"
        and probe_can_promote_row(row, probe_evidence)
    ):
        reasons.append("row_status_promoted_from_pending_by_probe_evidence")
    return reasons


def safe_action_status(row: dict[str, Any], effective_status: str | None) -> str:
    runtime_result = row.get("action_runtime_result")
    if isinstance(runtime_result, dict):
        runtime_status = str(runtime_result.get("status") or "")
        if runtime_status in SAFE_ACTION_STATUSES:
            return runtime_status
    if effective_status in SAFE_ACTION_STATUSES:
        return str(effective_status)
    replay_status = str(row.get("replay_status") or "")
    if replay_status in SAFE_ACTION_STATUSES:
        return replay_status
    availability = str(row.get("availability") or "")
    if availability == "unsupported":
        return "unsupported"
    return "pending"


def observation_for_row(
    input_info: dict[str, Any],
    row: dict[str, Any],
    probe_evidence_by_case: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    probe_evidence = row.get("probe_evidence")
    if not probe_evidence and probe_evidence_by_case:
        probe_evidence = probe_evidence_by_case.get(str(row.get("case_id")))
    effective_status = effective_replay_status(row, probe_evidence)
    action_status = safe_action_status(row, effective_status)
    return {
        "input_index": input_info["input_index"],
        "capture_id": row.get("capture_id"),
        "evidence_path": row.get("evidence_path"),
        "availability": row.get("availability", "supported"),
        "safety_class": row.get("safety_class"),
        "replay_status": row.get("replay_status"),
        "effective_replay_status": effective_status,
        "probe_evidence": probe_evidence,
        "unresolved_reasons": unresolved_reasons_for_row(row, probe_evidence),
        "pre_normalization_hash": row.get("pre_normalization_hash"),
        "normalized_hash": row.get("normalized_hash"),
        "request_size": row.get("request_size"),
        "response_size": row.get("response_size"),
        "operation_tokens": operation_token_values(row),
        "response_markers": row.get("response_markers", []),
        "response_marker_count": len(row.get("response_markers", [])),
        "dynamic_fields": dynamic_field_summary(row),
        "normalization_replacements": row.get("normalization_replacements", row.get("dynamic_fields", [])),
        "preserved_fields": row.get("preserved_fields", []),
        "ambiguous_fields": row.get("ambiguous_fields", []),
        "frame_range": row.get("frame_range"),
        "element_family": row.get("element_family"),
        "pre_state": row.get("pre_state"),
        "action": row.get("action"),
        "post_state": row.get("post_state"),
        "recovery_expectation": row.get("recovery_expectation"),
        "action_result_markers": row.get("action_result_markers", []),
        "action_frame_range": row.get("action_frame_range"),
        "background_frame_ranges": row.get("background_frame_ranges", []),
        "action_runtime_result": row.get("action_runtime_result"),
        "acceptance_evidence": row.get("acceptance_evidence", []),
        "side_channel_evidence": row.get("side_channel_evidence"),
        "safe_action_status": action_status,
    }


def is_safe_action_observation(item: dict[str, Any]) -> bool:
    return item.get("safety_class") == "safe_ui_action" or bool(
        item.get("action")
        or item.get("pre_state")
        or item.get("post_state")
        or item.get("action_result_markers")
        or item.get("action_frame_range")
    )


def has_accepted_safe_action_evidence(item: dict[str, Any]) -> bool:
    side_channel_evidence = item.get("side_channel_evidence")
    typed_contract_accepted = isinstance(side_channel_evidence, dict) and (
        side_channel_evidence.get("validation_status") == "accepted"
        or side_channel_evidence.get("status") == "accepted"
    )
    probe_evidence = item.get("probe_evidence")
    probe_accepted = isinstance(probe_evidence, dict) and probe_evidence.get("status") == "accepted"
    proof_present = bool(item.get("acceptance_evidence") or probe_accepted or typed_contract_accepted)
    return bool(
        item.get("safe_action_status") == "accepted"
        and item.get("effective_replay_status") == "accepted"
        and proof_present
        and item.get("action_frame_range")
        and item.get("normalized_hash")
        and item.get("request_size")
        and item.get("response_size")
        and item.get("action_result_markers")
    )


def classify_safe_action_case(
    input_count: int,
    missing_inputs: list[int],
    observations: list[dict[str, Any]],
) -> str:
    if missing_inputs or not observations:
        return "blocked"
    if observations and all(item.get("safe_action_status") == "unsupported" for item in observations):
        return "unsupported"

    hashes = [item.get("normalized_hash") for item in observations if item.get("normalized_hash")]
    if (
        all(has_accepted_safe_action_evidence(item) for item in observations)
        and len(hashes) == input_count
        and len(set(hashes)) == 1
    ):
        return "accepted"

    statuses = {str(item.get("safe_action_status") or "pending") for item in observations}
    for status in ("rejected", "timeout", "partial", "pending", "blocked", "unsupported"):
        if status in statuses:
            return status
    return "pending"


def classify_case(input_count: int, missing_inputs: list[int], observations: list[dict[str, Any]]) -> str:
    if any(is_safe_action_observation(item) for item in observations):
        return classify_safe_action_case(input_count, missing_inputs, observations)
    if missing_inputs:
        return "missing_case"
    if observations and all(item.get("availability") == "unsupported" for item in observations):
        return "unsupported_gap"

    hashes = [item.get("normalized_hash") for item in observations if item.get("normalized_hash")]
    replay_statuses = {item.get("effective_replay_status") for item in observations}
    if len(hashes) < input_count:
        return "incomplete_hash"
    if len(set(hashes)) > 1:
        return "divergent_hash"
    if replay_statuses == {"accepted"}:
        return "stable"
    return "non_accepted"


def precise_reasons_for_case(
    classification: str,
    observations: list[dict[str, Any]],
    request_hash_evidence: dict[str, Any] | None = None,
) -> list[str]:
    reasons: set[str] = set()
    if classification in {"stable", "accepted"}:
        reasons.add("accepted_reviewed_hash")
    if classification == "unsupported_gap":
        reasons.add("unsupported_fixture_state")
    if classification == "unsupported" and any(is_safe_action_observation(item) for item in observations):
        reasons.add("unsupported_fixture_state")
    if classification == "missing_case":
        reasons.add("missing_request_frames")
    if classification == "divergent_hash":
        reasons.add("incomplete_normalizer_coverage")

    if any(is_safe_action_observation(item) for item in observations):
        if any(not item.get("action_frame_range") for item in observations):
            reasons.add("missing_action_frame_range")
        if any(not item.get("action_result_markers") for item in observations):
            reasons.add("missing_action_result_markers")
        if any(
            item.get("safe_action_status") == "accepted"
            and not (
                item.get("acceptance_evidence")
                or (
                    isinstance(item.get("probe_evidence"), dict)
                    and item["probe_evidence"].get("status") == "accepted"
                )
                or (
                    isinstance(item.get("side_channel_evidence"), dict)
                    and (
                        item["side_channel_evidence"].get("validation_status") == "accepted"
                        or item["side_channel_evidence"].get("status") == "accepted"
                    )
                )
            )
            for item in observations
        ):
            reasons.add("missing_safe_action_acceptance_proof")
        if any(not item.get("normalized_hash") for item in observations):
            reasons.add("missing_safe_action_hash")
            reasons.add("missing_request_frames")
        if any(item.get("safe_action_status") == "pending" for item in observations):
            reasons.add("pending_action_result")
        if classification != "accepted" and not any(item.get("probe_evidence") for item in observations):
            reasons.add("replay_or_probe_unavailable")
        if classification == "blocked" and not observations:
            reasons.add("missing_request_frames")

    if any(item.get("availability") == "runtime_unavailable" for item in observations):
        reasons.add("runtime_unavailable")

    missing_hash_or_payload = any(
        not item.get("normalized_hash")
        or not item.get("request_size")
        or not item.get("response_size")
        for item in observations
    )
    if classification == "incomplete_hash" and missing_hash_or_payload:
        reasons.add("missing_request_frames")

    if any(item.get("ambiguous_fields") for item in observations):
        reasons.add("incomplete_normalizer_coverage")

    if request_hash_evidence and request_hash_evidence.get("normalized_hash"):
        reasons.add("accepted_reviewed_hash")
        if request_hash_evidence.get("query") != request_hash_evidence.get("case_id"):
            reasons.add("ambiguous_operation_join")
        notes = str(request_hash_evidence.get("notes") or "")
        if "operation join" in notes or "operation-join" in notes:
            reasons.add("ambiguous_operation_join")

    return sorted(reasons)


def provider_owners_for_reasons(reasons: Iterable[str]) -> list[str]:
    return sorted(
        {
            PROVIDER_OWNER_BY_REASON[reason]
            for reason in reasons
            if reason in PROVIDER_OWNER_BY_REASON
        }
    )


def compare_inputs(
    input_paths: list[Path],
    repo_root: Path,
    probe_evidence_by_case: dict[str, dict[str, Any]] | None = None,
    request_hash_evidence_by_case: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    inputs = [load_input(path, index, repo_root) for index, path in enumerate(input_paths)]
    case_ids = sorted({row["case_id"] for input_info in inputs for row in input_info["rows"]})
    cases: list[dict[str, Any]] = []

    for case_id in case_ids:
        observations: list[dict[str, Any]] = []
        missing_inputs: list[int] = []
        duplicate_inputs: list[int] = []

        for input_info in inputs:
            rows = input_info["rows_by_case"].get(case_id, [])
            if not rows:
                missing_inputs.append(input_info["input_index"])
                continue
            if len(rows) > 1:
                duplicate_inputs.append(input_info["input_index"])
            observations.append(observation_for_row(input_info, rows[0], probe_evidence_by_case))

        classification = classify_case(len(inputs), missing_inputs, observations)
        request_hash_evidence = (
            request_hash_evidence_by_case.get(case_id)
            if request_hash_evidence_by_case
            else None
        )
        precise_reasons = precise_reasons_for_case(
            classification,
            observations,
            request_hash_evidence,
        )
        hash_values = unique_json_values(item.get("normalized_hash") for item in observations)
        pre_hash_values = unique_json_values(item.get("pre_normalization_hash") for item in observations)
        request_sizes = unique_json_values(item.get("request_size") for item in observations)
        response_sizes = unique_json_values(item.get("response_size") for item in observations)
        operation_token_sets = unique_json_values(item.get("operation_tokens") for item in observations)
        response_marker_sets = unique_json_values(item.get("response_markers") for item in observations)
        dynamic_field_sets = unique_json_values(item.get("dynamic_fields") for item in observations)
        normalization_replacement_sets = unique_json_values(item.get("normalization_replacements") for item in observations)
        preserved_field_sets = unique_json_values(item.get("preserved_fields") for item in observations)
        ambiguous_field_sets = unique_json_values(item.get("ambiguous_fields") for item in observations)
        safety_classes = sorted(
            {
                str(item.get("safety_class"))
                for item in observations
                if item.get("safety_class")
            }
        )
        safe_action_statuses = sorted(
            {
                str(item.get("safe_action_status"))
                for item in observations
                if is_safe_action_observation(item)
            }
        )
        action_frame_ranges = unique_json_values(item.get("action_frame_range") for item in observations)
        background_frame_range_sets = unique_json_values(
            item.get("background_frame_ranges") for item in observations
        )
        action_result_marker_sets = unique_json_values(
            item.get("action_result_markers") for item in observations
        )
        probe_evidence_paths = sorted(
            {
                item["probe_evidence"]["evidence_path"]
                for item in observations
                if isinstance(item.get("probe_evidence"), dict)
                and item["probe_evidence"].get("evidence_path")
            }
        )
        unresolved_reasons = sorted(
            {
                reason
                for item in observations
                for reason in item.get("unresolved_reasons", [])
            }
        )

        cases.append(
            {
                "case_id": case_id,
                "classification": classification,
                "missing_inputs": missing_inputs,
                "duplicate_inputs": duplicate_inputs,
                "capture_ids": [item.get("capture_id") for item in observations],
                "replay_statuses": sorted({str(item.get("replay_status")) for item in observations}),
                "effective_replay_statuses": sorted(
                    {str(item.get("effective_replay_status")) for item in observations}
                ),
                "availability": sorted({str(item.get("availability", "supported")) for item in observations}),
                "safety_classes": safety_classes,
                "safe_action_statuses": safe_action_statuses,
                "pre_normalization_hash_values": pre_hash_values,
                "hash_values": hash_values,
                "stable_hash": hash_values[0] if classification in {"stable", "accepted"} and len(hash_values) == 1 else None,
                "request_sizes": request_sizes,
                "response_sizes": response_sizes,
                "operation_token_sets": operation_token_sets,
                "response_marker_sets": response_marker_sets,
                "dynamic_field_sets": dynamic_field_sets,
                "normalization_replacement_sets": normalization_replacement_sets,
                "preserved_field_sets": preserved_field_sets,
                "ambiguous_field_sets": ambiguous_field_sets,
                "action_frame_ranges": action_frame_ranges,
                "background_frame_range_sets": background_frame_range_sets,
                "action_result_marker_sets": action_result_marker_sets,
                "probe_evidence_paths": probe_evidence_paths,
                "request_hash_evidence_paths": [request_hash_evidence["evidence_path"]]
                if request_hash_evidence and request_hash_evidence.get("evidence_path")
                else [],
                "unresolved_reasons": unresolved_reasons,
                "precise_reasons": precise_reasons,
                "provider_owners": provider_owners_for_reasons(precise_reasons),
                "observations": observations,
                "normalizer_investigation_candidate": classification == "divergent_hash",
            }
        )

    classification_counts = {
        status: sum(1 for case in cases if case["classification"] == status)
        for status in sorted({case["classification"] for case in cases})
    }
    return {
        "schema": SCHEMA,
        "generated_at": utc_now(),
        "input_count": len(inputs),
        "inputs": [
            {
                "input_index": input_info["input_index"],
                "cases_path": input_info["cases_path"],
                "evidence_dir": input_info["evidence_dir"],
                "capture_ids": input_info["capture_ids"],
                "case_count": len(input_info["rows"]),
            }
            for input_info in inputs
        ],
        "case_count": len(cases),
        "classification_counts": classification_counts,
        "stable_case_ids": [case["case_id"] for case in cases if case["classification"] == "stable"],
        "accepted_case_ids": [
            case["case_id"] for case in cases if case["classification"] in {"stable", "accepted"}
        ],
        "gap_case_ids": [
            case["case_id"]
            for case in cases
            if case["classification"]
            in {
                "missing_case",
                "incomplete_hash",
                "unsupported_gap",
                "pending",
                "unsupported",
                "partial",
                "timeout",
                "rejected",
                "blocked",
            }
        ],
        "normalizer_investigation_case_ids": [
            case["case_id"] for case in cases if case["normalizer_investigation_candidate"]
        ],
        "cases": cases,
    }


def markdown_table(rows: list[list[Any]], headers: list[str]) -> str:
    def cell(value: Any) -> str:
        if isinstance(value, (list, dict)):
            value = json.dumps(value, ensure_ascii=False)
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell(value) for value in row) + " |")
    return "\n".join(lines)


def write_markdown_report(path: Path, comparison: dict[str, Any]) -> None:
    rows = [
        [
            case["case_id"],
            case["classification"],
            case["precise_reasons"],
            case["provider_owners"],
            case["safety_classes"],
            ", ".join(str(capture_id) for capture_id in case["capture_ids"]),
            case["replay_statuses"],
            case["effective_replay_statuses"],
            case["safe_action_statuses"],
            case["probe_evidence_paths"],
            case["request_hash_evidence_paths"],
            case["unresolved_reasons"],
            case["pre_normalization_hash_values"],
            case["hash_values"],
            case["request_sizes"],
            case["response_sizes"],
            case["action_frame_ranges"],
            case["background_frame_range_sets"],
            case["action_result_marker_sets"],
        ]
        for case in comparison["cases"]
    ]
    lines = [
        "# Protocol Corpus Repeatability Report",
        "",
        f"- Generated at: `{comparison['generated_at']}`",
        f"- Input count: `{comparison['input_count']}`",
        f"- Case count: `{comparison['case_count']}`",
        f"- Classification counts: `{json.dumps(comparison['classification_counts'], ensure_ascii=False)}`",
        f"- Stable case ids: `{json.dumps(comparison['stable_case_ids'], ensure_ascii=False)}`",
        f"- Accepted case ids: `{json.dumps(comparison['accepted_case_ids'], ensure_ascii=False)}`",
        f"- Gap case ids: `{json.dumps(comparison['gap_case_ids'], ensure_ascii=False)}`",
        f"- Normalizer investigation candidates: `{json.dumps(comparison['normalizer_investigation_case_ids'], ensure_ascii=False)}`",
        "",
        "## Inputs",
        "",
        markdown_table(
            [
                [
                    item["input_index"],
                    item["capture_ids"],
                    item["case_count"],
                    item["cases_path"],
                ]
                for item in comparison["inputs"]
            ],
            ["index", "capture ids", "cases", "path"],
        ),
        "",
        "## Cases",
        "",
        markdown_table(
            rows,
            [
                "case",
                "classification",
                "precise reasons",
                "provider owners",
                "safety",
                "captures",
                "row replay",
                "effective replay",
                "action status",
                "probe evidence",
                "request hash evidence",
                "unresolved",
                "before hashes",
                "after hashes",
                "request bytes",
                "response bytes",
                "action frames",
                "background frames",
                "action markers",
            ],
        ),
        "",
        "## Notes",
        "",
        "- The report compares reviewed corpus rows only; raw traffic remains under ignored runtime paths.",
        "- `stable` requires the same non-null normalized hash in every input and accepted replay/probe status.",
        "- `effective replay` includes compact direct-probe evidence supplied to the comparison.",
        "- Safe action classifications use `accepted`, `pending`, `unsupported`, `partial`, `timeout`, `rejected` or `blocked`.",
        "- `precise reasons` classify evidence blockers with stable reason values for follow-up planning.",
        "- `incomplete_hash` marks repeated matrix rows whose reviewed evidence exists but one or more inputs lack captured request frames.",
        "- `unsupported_gap` rows are fixture coverage gaps, not protocol mappings.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def replacement_names(replacement_sets: list[Any]) -> list[str]:
    names: set[str] = set()
    for replacement_set in replacement_sets:
        if not isinstance(replacement_set, list):
            continue
        for item in replacement_set:
            if isinstance(item, dict) and item.get("name"):
                names.add(str(item["name"]))
    return sorted(names)


def write_normalizer_report(output_dir: Path, comparison: dict[str, Any]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = []
    for case in comparison["cases"]:
        before_hashes = [value for value in case.get("pre_normalization_hash_values", []) if value]
        after_hashes = [value for value in case.get("hash_values", []) if value]
        replacement_names_for_case = replacement_names(case.get("normalization_replacement_sets", []))
        preserved_names_for_case = replacement_names(case.get("preserved_field_sets", []))
        ambiguous_names_for_case = replacement_names(case.get("ambiguous_field_sets", []))
        cases.append(
            {
                "case_id": case["case_id"],
                "classification": case["classification"],
                "before_hashes": before_hashes,
                "after_hashes": after_hashes,
                "before_hash_count": len(set(before_hashes)),
                "after_hash_count": len(set(after_hashes)),
                "normalization_reduced_hash_set": bool(after_hashes)
                and len(set(after_hashes)) < len(set(before_hashes)),
                "accepted_replacements": replacement_names_for_case,
                "preserved_fields": preserved_names_for_case,
                "ambiguous_fields": ambiguous_names_for_case,
                "normalizer_investigation_candidate": case.get("normalizer_investigation_candidate", False),
            }
        )
    report = {
        "schema": "protocol-normalizer-evidence.v1",
        "generated_at": comparison["generated_at"],
        "comparison_inputs": comparison["inputs"],
        "accepted_replacements": sorted({name for case in cases for name in case["accepted_replacements"]}),
        "preserved_fields": sorted({name for case in cases for name in case["preserved_fields"]}),
        "ambiguous_fields": sorted({name for case in cases for name in case["ambiguous_fields"]}),
        "normalizer_investigation_case_ids": comparison["normalizer_investigation_case_ids"],
        "cases": cases,
    }
    json_path = output_dir / "normalizer_report.json"
    markdown_path = output_dir / "normalizer_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    rows = [
        [
            case["case_id"],
            case["classification"],
            case["before_hash_count"],
            case["after_hash_count"],
            [value[:16] for value in case["before_hashes"]],
            [value[:16] for value in case["after_hashes"]],
            case["accepted_replacements"],
            case["preserved_fields"],
            case["ambiguous_fields"],
        ]
        for case in cases
    ]
    lines = [
        "# Protocol Normalizer Evidence",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Accepted replacements: `{json.dumps(report['accepted_replacements'], ensure_ascii=False)}`",
        f"- Preserved fields: `{json.dumps(report['preserved_fields'], ensure_ascii=False)}`",
        f"- Ambiguous fields: `{json.dumps(report['ambiguous_fields'], ensure_ascii=False)}`",
        f"- Normalizer investigation cases: `{json.dumps(report['normalizer_investigation_case_ids'], ensure_ascii=False)}`",
        "",
        "## Cases",
        "",
        markdown_table(
            rows,
            [
                "case",
                "classification",
                "before hash count",
                "after hash count",
                "before prefixes",
                "after prefixes",
                "accepted replacements",
                "preserved fields",
                "ambiguous fields",
            ],
        ),
        "",
        "## Notes",
        "",
        "- `before_hashes` are calculated after tail stripping and before dynamic replacements.",
        "- `after_hashes` are the normal corpus `normalized_hash` values.",
        "- `operation_token` is preserved as a semantic token and is not replaced by the current normalizer.",
        "",
    ]
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "normalizer_json": str(json_path),
        "normalizer_report": str(markdown_path),
    }


def write_accepted_mappings_report(output_dir: Path, comparison: dict[str, Any]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    accepted_cases = [
        case for case in comparison["cases"] if case["classification"] in {"stable", "accepted"}
    ]
    report = {
        "schema": "protocol-accepted-mappings.v1",
        "generated_at": comparison["generated_at"],
        "comparison_inputs": comparison["inputs"],
        "accepted_case_ids": [case["case_id"] for case in accepted_cases],
        "case_count": len(accepted_cases),
        "cases": [
            {
                "case_id": case["case_id"],
                "classification": case["classification"],
                "safety_classes": case.get("safety_classes", []),
                "normalized_hash": case["stable_hash"],
                "capture_ids": case["capture_ids"],
                "request_sizes": case["request_sizes"],
                "response_sizes": case["response_sizes"],
                "operation_token_sets": case["operation_token_sets"],
                "response_marker_sets": case["response_marker_sets"],
                "action_frame_ranges": case.get("action_frame_ranges", []),
                "background_frame_range_sets": case.get("background_frame_range_sets", []),
                "action_result_marker_sets": case.get("action_result_marker_sets", []),
                "probe_evidence_paths": case["probe_evidence_paths"],
                "observations": [
                    {
                        "capture_id": item.get("capture_id"),
                        "evidence_path": item.get("evidence_path"),
                        "frame_range": item.get("frame_range"),
                        "action_frame_range": item.get("action_frame_range"),
                        "background_frame_ranges": item.get("background_frame_ranges"),
                        "action_result_markers": item.get("action_result_markers"),
                        "acceptance_evidence": item.get("acceptance_evidence", []),
                        "probe_evidence": item.get("probe_evidence"),
                        "side_channel_evidence": item.get("side_channel_evidence"),
                    }
                    for item in case["observations"]
                ],
            }
            for case in accepted_cases
        ],
    }
    json_path = output_dir / "accepted_mappings.json"
    markdown_path = output_dir / "accepted_mappings.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = [
        [
            case["case_id"],
            case["classification"],
            case["stable_hash"],
            case["capture_ids"],
            case["request_sizes"],
            case["response_sizes"],
            case.get("action_frame_ranges", []),
            case["probe_evidence_paths"],
        ]
        for case in accepted_cases
    ]
    lines = [
        "# Protocol Accepted Mapping Evidence",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Accepted case ids: `{json.dumps(report['accepted_case_ids'], ensure_ascii=False)}`",
        "",
        "## Accepted Cases",
        "",
        markdown_table(
            rows,
            [
                "case",
                "classification",
                "normalized hash",
                "captures",
                "request bytes",
                "response bytes",
                "action frames",
                "probe evidence",
            ],
        ),
        "",
        "## Notes",
        "",
        "- Accepted mappings require repeated non-null normalized hashes and accepted replay/probe evidence.",
        "- Safe action mappings additionally require reviewed action-frame evidence and action result markers.",
        "- Raw captures and full probe output remain under ignored runtime paths.",
        "",
    ]
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "accepted_mappings_json": str(json_path),
        "accepted_mappings_report": str(markdown_path),
    }


def write_outputs(output_dir: Path, comparison: dict[str, Any]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "corpus_comparison.json"
    markdown_path = output_dir / "corpus_comparison.md"
    json_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown_report(markdown_path, comparison)
    return {
        "comparison_json": str(json_path),
        "comparison_report": str(markdown_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="Evidence directories or corpus_cases.jsonl files to compare.")
    parser.add_argument("--comparison-id", default=None, help="Output folder name under docs/protocol-research/evidence/corpus-comparison/.")
    parser.add_argument("--output-dir", type=Path, help="Explicit output directory for compact comparison evidence.")
    parser.add_argument("--normalizer-output-dir", type=Path, help="Optional compact normalizer evidence output directory.")
    parser.add_argument("--probe-evidence", action="append", type=Path, default=[], help="Compact python_manager_probe_result.json used to promote supported rows.")
    parser.add_argument("--request-hash-evidence", action="append", type=Path, default=[], help="Compact readonly element request-hash evidence used to refine gap reasons.")
    parser.add_argument("--accepted-output-dir", type=Path, help="Optional compact accepted-mapping evidence output directory.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_script()
    input_paths = [resolve_cases_path(value, repo_root) for value in args.inputs]
    probe_evidence_by_case = load_probe_evidence(args.probe_evidence, repo_root)
    request_hash_evidence_by_case = load_request_hash_evidence(args.request_hash_evidence, repo_root)
    comparison = compare_inputs(input_paths, repo_root, probe_evidence_by_case, request_hash_evidence_by_case)
    output_dir = args.output_dir
    if output_dir is None:
        comparison_id = args.comparison_id or timestamp_name()
        output_dir = repo_root / "docs" / "protocol-research" / "evidence" / "corpus-comparison" / comparison_id
    output_paths = write_outputs(output_dir.resolve(), comparison)
    if args.normalizer_output_dir:
        output_paths.update(write_normalizer_report(args.normalizer_output_dir.resolve(), comparison))
    if args.accepted_output_dir:
        output_paths.update(write_accepted_mappings_report(args.accepted_output_dir.resolve(), comparison))
    result = {
        **output_paths,
        "case_count": comparison["case_count"],
        "classification_counts": comparison["classification_counts"],
        "stable_case_ids": comparison["stable_case_ids"],
        "accepted_case_ids": comparison["accepted_case_ids"],
        "gap_case_ids": comparison["gap_case_ids"],
        "normalizer_investigation_case_ids": comparison["normalizer_investigation_case_ids"],
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"comparison_json={result['comparison_json']}")
        print(f"comparison_report={result['comparison_report']}")
        print(f"classification_counts={result['classification_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
