#!/usr/bin/env python3
"""Validate V2 safe-action manifests and emit dry-run phase evidence."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


V2_SAFE_ACTION_SCENARIO = "manager-fixture-v2-safe-action"
VALIDATION_SCHEMA = "qa-mcp.v2-safe-action-manifest-validation.v1"
PHASE_EVENTS_SCHEMA = "qa-mcp.v2-safe-action-phase-events.v1"
MANAGER_MANIFEST_SCHEMA = "qa-mcp.manager-fixture-v2-safe-action.manifest.v1"
MANAGER_RESULT_SCHEMA = "qa-mcp.manager-fixture-v2-safe-action.result.v1"
MANAGER_CATALOG_SCHEMA = "qa-mcp.manager-fixture-v2.safe-action-catalog.v1"
RUNNER_RESULTS_SCHEMA = "qa-mcp.manager-fixture-v2.safe-action-runner-results.v1"
RAW_OUTPUT_POLICY = (
    "raw TCP streams, full event logs, platform logs and generated replay output "
    "stay under ignored runtime/protocol-research paths"
)

ALLOWED_ACTION_FAMILIES = {
    "focus_existing_element",
    "activate_existing_window_or_form",
    "switch_fixture_page",
    "select_local_table_row",
    "expand_or_collapse_menu_or_group",
}

REQUIRED_FIELDS = (
    "action_id",
    "target_id",
    "target_marker",
    "pre_state",
    "action",
    "post_state",
    "recovery_expectation",
    "mutates_business_data",
    "allowed_action_family",
    "expected_action_result_markers",
)

EXECUTABLE_STATUS_HINTS = {
    "",
    "accepted",
    "accepted_for_capture",
    "candidate",
    "ready",
    "reviewed",
}
PENDING_STATUS_HINTS = {"blocked", "deferred", "partial", "pending", "timeout", "unresolved"}
UNSUPPORTED_STATUS_HINTS = {"unsupported"}
REJECTED_STATUS_HINTS = {"rejected"}
SUPPORTED_TARGET_STATUS_HINTS = {"", "accepted", "candidate", "ready", "reviewed", "supported"}
UNSUPPORTED_TARGET_STATUS_HINTS = {"blocked", "deferred", "partial", "pending", "timeout", "unsupported"}
RUNNER_TERMINAL_STATUSES = {"success", "rejected", "blocked", "unsupported", "partial", "timeout"}

TARGET_COLLECTION_KEYS = (
    "safe_action_targets",
    "targets",
    "target_map",
    "fixture_targets",
)
TARGET_MARKER_KEYS = ("target_marker", "marker", "expected_marker")
OWNER_KEYS = ("provider_owner", "owner", "owner_path")
STATUS_REASON_KEYS = (
    "blocked_reason",
    "unsupported_reason",
    "rejection_reason",
    "reason",
    "status_reason",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return True


def manifest_rows(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if not isinstance(data, dict):
        raise ValueError("V2 safe-action manifest must be a JSON object or list")
    for key in ("safe_actions", "actions", "rows", "cases", "commands"):
        value = data.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    raise ValueError("V2 safe-action manifest does not contain safe_actions/actions/rows/cases/commands")


def manifest_targets(data: Any) -> list[dict[str, Any]] | None:
    if not isinstance(data, dict):
        return None
    for key in TARGET_COLLECTION_KEYS:
        value = data.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
        if isinstance(value, dict):
            return [row for row in value.values() if isinstance(row, dict)]
    return None


def target_id_for_row(row: dict[str, Any]) -> str:
    return str(row.get("target_id") or row.get("id") or row.get("case_id") or "").strip()


def target_marker_for_row(row: dict[str, Any]) -> str:
    for key in TARGET_MARKER_KEYS:
        value = row.get(key)
        if has_value(value):
            return str(value).strip()
    return ""


def target_status_for_row(row: dict[str, Any]) -> str:
    for key in ("target_status", "review_status", "status", "availability"):
        value = row.get(key)
        if value is not None:
            return str(value).strip().lower()
    return ""


def target_family_set(row: dict[str, Any]) -> set[str]:
    value = row.get("allowed_action_families") or row.get("allowed_action_family")
    if isinstance(value, list):
        return {str(item).strip() for item in value if str(item).strip()}
    if isinstance(value, str) and value.strip():
        return {value.strip()}
    return set()


def target_index_for_manifest(data: Any) -> dict[str, dict[str, Any]] | None:
    targets = manifest_targets(data)
    if targets is None:
        return None
    index: dict[str, dict[str, Any]] = {}
    for target in targets:
        target_id = target_id_for_row(target)
        if target_id:
            index[target_id] = target
    return index


def first_text_value(row: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = row.get(key)
        if has_value(value):
            return str(value)
    return None


def normalized_row(row: dict[str, Any], index: int) -> dict[str, Any]:
    normalized = dict(row)
    action_id = str(normalized.get("action_id") or normalized.get("case_id") or f"safe-action-{index + 1}")
    normalized.setdefault("action_id", action_id)
    normalized.setdefault("case_id", action_id)
    normalized.setdefault("scenario", V2_SAFE_ACTION_SCENARIO)
    normalized.setdefault("safety_class", "safe_ui_action")
    if "expected_action_result_markers" not in normalized and "action_result_markers" in normalized:
        normalized["expected_action_result_markers"] = normalized["action_result_markers"]
    return normalized


def status_hint_for_row(row: dict[str, Any]) -> str:
    for key in ("tooling_status", "validation_status", "status", "prerequisite_status"):
        value = row.get(key)
        if value is not None:
            return str(value).strip().lower()
    return ""


def validate_target_binding(
    normalized: dict[str, Any],
    status_hint: str,
    target_index: dict[str, dict[str, Any]] | None,
) -> list[str]:
    if target_index is None:
        return []

    errors: list[str] = []
    target_id = str(normalized.get("target_id") or "").strip()
    if not target_id:
        return errors

    target = target_index.get(target_id)
    if target is None:
        errors.append(f"unsupported_target:{target_id}")
        return errors

    expected_marker = target_marker_for_row(target)
    actual_marker = str(normalized.get("target_marker") or "").strip()
    if expected_marker and actual_marker and actual_marker != expected_marker:
        errors.append(f"target_marker_mismatch:{target_id}:{actual_marker}!={expected_marker}")

    family = str(normalized.get("allowed_action_family") or "").strip()
    target_families = target_family_set(target)
    if family and target_families and family not in target_families:
        errors.append(f"target_family_not_allowed:{target_id}:{family}")

    target_status = target_status_for_row(target)
    if (
        target_status in UNSUPPORTED_TARGET_STATUS_HINTS
        and status_hint in EXECUTABLE_STATUS_HINTS
    ):
        errors.append(f"unsupported_target_status:{target_id}:{target_status}")

    return errors


def validate_row(
    row: dict[str, Any],
    index: int = 0,
    target_index: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    normalized = normalized_row(row, index)
    errors: list[str] = []
    warnings: list[str] = []
    owner = first_text_value(normalized, OWNER_KEYS)
    status_reason = first_text_value(normalized, STATUS_REASON_KEYS)
    residual_risk = first_text_value(normalized, ("residual_risk",))

    for field in REQUIRED_FIELDS:
        if not has_value(normalized.get(field)):
            errors.append(f"missing_field:{field}")

    if normalized.get("mutates_business_data") is not False:
        errors.append("mutates_business_data_not_false")

    safety_class = str(normalized.get("safety_class") or "")
    if safety_class != "safe_ui_action":
        errors.append(f"unsupported_safety_class:{safety_class}")

    family = str(normalized.get("allowed_action_family") or "")
    if family and family not in ALLOWED_ACTION_FAMILIES:
        errors.append(f"unsupported_action_family:{family}")

    marker_values = normalized.get("expected_action_result_markers")
    if has_value(marker_values) and not isinstance(marker_values, list):
        errors.append("expected_action_result_markers_not_list")

    status_hint = status_hint_for_row(normalized)
    if status_hint not in (
        EXECUTABLE_STATUS_HINTS
        | PENDING_STATUS_HINTS
        | UNSUPPORTED_STATUS_HINTS
        | REJECTED_STATUS_HINTS
    ):
        errors.append(f"unknown_status:{status_hint}")

    errors.extend(validate_target_binding(normalized, status_hint, target_index))

    if errors:
        validation_status = "rejected"
    elif status_hint in REJECTED_STATUS_HINTS:
        validation_status = "rejected"
    elif status_hint in UNSUPPORTED_STATUS_HINTS:
        validation_status = "unsupported"
    elif status_hint in PENDING_STATUS_HINTS:
        validation_status = status_hint if status_hint in {"blocked", "partial", "timeout"} else "pending"
    else:
        validation_status = "accepted_for_capture"

    executable = validation_status == "accepted_for_capture"
    if not executable and not errors:
        warnings.append(f"non_executable_status:{validation_status}")
    if not executable and not owner:
        warnings.append("missing_non_executable_owner")
    if not executable and not status_reason:
        warnings.append("missing_non_executable_reason")
    if not executable and not residual_risk:
        warnings.append("missing_non_executable_residual_risk")

    return {
        "action_id": normalized["action_id"],
        "case_id": normalized["case_id"],
        "target_id": normalized.get("target_id"),
        "target_marker": normalized.get("target_marker"),
        "allowed_action_family": normalized.get("allowed_action_family"),
        "validation_status": validation_status,
        "executable": executable,
        "owner": owner,
        "status_reason": status_reason,
        "residual_risk": residual_risk,
        "reasons": errors or warnings,
        "row": normalized,
    }


def validate_manifest_data(data: Any, source_manifest: Path | None = None) -> dict[str, Any]:
    rows = manifest_rows(data)
    target_index = target_index_for_manifest(data)
    validated_rows = [
        validate_row(row, index, target_index=target_index) for index, row in enumerate(rows)
    ]
    status_counts = {
        status: sum(1 for row in validated_rows if row["validation_status"] == status)
        for status in sorted({row["validation_status"] for row in validated_rows})
    }
    executable_rows = [row for row in validated_rows if row["executable"]]
    return {
        "schema": VALIDATION_SCHEMA,
        "generated_at": utc_now(),
        "source_manifest": str(source_manifest) if source_manifest else None,
        "scenario": V2_SAFE_ACTION_SCENARIO,
        "row_count": len(validated_rows),
        "executable_count": len(executable_rows),
        "status_counts": status_counts,
        "allowed_action_families": sorted(ALLOWED_ACTION_FAMILIES),
        "required_fields": list(REQUIRED_FIELDS),
        "target_count": len(target_index) if target_index is not None else None,
        "reviewed_target_map_path": data.get("reviewed_target_map_path")
        if isinstance(data, dict)
        else None,
        "raw_output_policy": RAW_OUTPUT_POLICY,
        "rows": validated_rows,
    }


def validate_manifest_path(path: Path) -> dict[str, Any]:
    return validate_manifest_data(read_json(path), path.resolve())


def phase_events_for_validation(validation: dict[str, Any], run_id: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    sequence = 1
    for item in validation.get("rows", []):
        row = item.get("row", {})
        family = row.get("allowed_action_family")
        action_frame_range = row.get("action_frame_range")
        background_frame_ranges = row.get("background_frame_ranges", [])
        recovery_frame_range = row.get("recovery_frame_range")
        recovery_result = recovery_result_for_row(row) if item.get("executable") else None
        common = {
            "schema": PHASE_EVENTS_SCHEMA,
            "run_id": run_id,
            "scenario": V2_SAFE_ACTION_SCENARIO,
            "sequence": None,
            "action_id": item.get("action_id"),
            "case_id": item.get("case_id"),
            "target_id": item.get("target_id"),
            "target_marker": item.get("target_marker"),
            "allowed_action_family": family,
            "validation_status": item.get("validation_status"),
            "tcp_marker_policy": "side_channel_only_no_tcp_markers",
        }
        for phase in (
            "pre_read",
            "action_start",
            "action_end",
            "post_read",
            "recovery",
            "recovery_read",
            "background",
        ):
            is_action_boundary = phase in {"action_start", "action_end"}
            if not item.get("executable"):
                frame_correlation_status = item.get("validation_status")
            elif is_action_boundary and action_frame_range:
                frame_correlation_status = "candidate_action_frame_range"
            elif is_action_boundary:
                frame_correlation_status = "missing_action_frame_range"
            elif phase == "background" and background_frame_ranges:
                frame_correlation_status = "background_frame_ranges_retained"
            elif phase == "recovery" and recovery_frame_range:
                frame_correlation_status = "recovery_frame_range_retained"
            elif phase == "recovery_read" and recovery_result:
                frame_correlation_status = "known_state_recovery"
            else:
                frame_correlation_status = "side_channel_only"
            event = {
                **common,
                "sequence": sequence,
                "phase": phase,
                "event": "phase_planned",
                "status": "planned" if item.get("executable") else "not_executable",
                "action": row.get("action"),
                "pre_state": row.get("pre_state") if phase == "pre_read" else None,
                "post_state": row.get("post_state") if phase == "post_read" else None,
                "recovery_expectation": row.get("recovery_expectation")
                if phase == "recovery"
                else None,
                "recovery_result": recovery_result if phase == "recovery_read" else None,
                "recovery_result_markers": (
                    recovery_result.get("expected_recovery_markers", [])
                    if recovery_result and phase == "recovery_read"
                    else []
                ),
                "known_state_rationale": (
                    recovery_result.get("known_state_rationale")
                    if recovery_result and phase == "recovery_read"
                    else None
                ),
                "action_boundary": is_action_boundary,
                "expected_action_result_markers": row.get("expected_action_result_markers", []),
                "action_result_markers": row.get(
                    "action_result_markers",
                    row.get("expected_action_result_markers", []),
                )
                if phase in {"action_end", "post_read"}
                else [],
                "candidate_action_frame_range": action_frame_range if is_action_boundary else None,
                "action_frame_range": action_frame_range if is_action_boundary else None,
                "background_frame_ranges": background_frame_ranges if phase == "background" else [],
                "recovery_frame_range": recovery_frame_range if phase == "recovery" else None,
                "frame_correlation_status": frame_correlation_status,
                "chunk_correlation": row.get("chunk_correlation", {}),
            }
            events.append(event)
            sequence += 1
    return events


def result_counts(results: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in results:
        status = str(result.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def expected_recovery_markers(row: dict[str, Any]) -> list[str]:
    recovery = row.get("recovery_expectation")
    markers: list[str] = []
    if isinstance(recovery, dict):
        expected_marker = recovery.get("expected_marker")
        if expected_marker:
            markers.append(str(expected_marker))
        expected_markers = recovery.get("expected_markers")
        if isinstance(expected_markers, list):
            markers.extend(str(marker) for marker in expected_markers if marker)
    if not markers and row.get("target_marker"):
        markers.append(str(row["target_marker"]))
    return markers


def recovery_result_for_row(row: dict[str, Any]) -> dict[str, Any]:
    recovery = row.get("recovery_expectation")
    route = recovery.get("route") if isinstance(recovery, dict) else recovery
    markers = expected_recovery_markers(row)
    return {
        "status": "known_state_planned",
        "route": route,
        "expected_recovery_markers": markers,
        "known_state_rationale": (
            "dry-run recovery contract records the expected baseline or known-state markers; "
            "live marker proof is required before acceptance"
        ),
        "live_recovery_executed": False,
    }


def success_phase_results(row: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "phase": "pre_read",
            "status": "success",
            "observed_state": row.get("pre_state"),
        },
        {
            "phase": "action_start",
            "status": "success",
            "action": row.get("action"),
            "allowed_action_family": row.get("allowed_action_family"),
        },
        {
            "phase": "action_end",
            "status": "success",
            "action_result_markers": row.get("expected_action_result_markers", []),
        },
        {
            "phase": "post_read",
            "status": "success",
            "observed_state": row.get("post_state"),
            "action_result_markers": row.get("expected_action_result_markers", []),
        },
        {
            "phase": "recovery",
            "status": "success",
            "recovery_expectation": row.get("recovery_expectation"),
        },
        {
            "phase": "recovery_read",
            "status": "success",
            "recovery_result": recovery_result_for_row(row),
        },
    ]


def safe_action_runner_result(item: dict[str, Any], sequence: int, run_id: str) -> dict[str, Any]:
    row = item.get("row", {})
    validation_status = str(item.get("validation_status") or "rejected")
    action_id = item.get("action_id")
    family = str(row.get("allowed_action_family") or "")
    base = {
        "schema": RUNNER_RESULTS_SCHEMA,
        "run_id": run_id,
        "sequence": sequence,
        "scenario": V2_SAFE_ACTION_SCENARIO,
        "action_id": action_id,
        "case_id": item.get("case_id"),
        "target_id": item.get("target_id"),
        "target_marker": item.get("target_marker"),
        "allowed_action_family": family,
        "validation_status": validation_status,
        "mutates_business_data": row.get("mutates_business_data"),
        "status_reason": item.get("status_reason"),
        "owner": item.get("owner"),
        "residual_risk": item.get("residual_risk"),
        "candidate_only": True,
        "accepted_protocol_mapping": False,
        "live_action_executed": False,
    }
    if validation_status != "accepted_for_capture":
        status = validation_status if validation_status in RUNNER_TERMINAL_STATUSES else "rejected"
        return {
            **base,
            "status": status,
            "status_reason": item.get("status_reason") or ";".join(item.get("reasons") or []),
            "blocked_before_action": True,
            "action_result_markers": [],
            "phase_results": [],
            "reasons": item.get("reasons", []),
        }

    if family not in ALLOWED_ACTION_FAMILIES:
        return {
            **base,
            "status": "unsupported",
            "status_reason": f"no_runner_handler_for_family:{family}",
            "blocked_before_action": True,
            "action_result_markers": [],
            "phase_results": [],
            "reasons": [f"no_runner_handler_for_family:{family}"],
        }

    return {
        **base,
        "status": "success",
        "status_reason": "dry-run dispatcher accepted validated allowlisted row",
        "blocked_before_action": False,
        "action_result_markers": row.get("expected_action_result_markers", []),
        "recovery_result": recovery_result_for_row(row),
        "recovery_frame_range": row.get("recovery_frame_range"),
        "rerun_determinism": {
            "status": "dry_run_repeatable",
            "pre_state": row.get("pre_state"),
            "action_result_markers": row.get("expected_action_result_markers", []),
            "live_rerun_executed": False,
        },
        "phase_results": success_phase_results(row),
        "reasons": [],
    }


def safe_action_runner_results(validation: dict[str, Any], run_id: str) -> list[dict[str, Any]]:
    return [
        safe_action_runner_result(item, index + 1, run_id)
        for index, item in enumerate(validation.get("rows", []))
    ]


def write_dry_run_output(output_dir: Path, validation: dict[str, Any]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = output_dir.name
    validation_path = output_dir / "v2_safe_action_manifest_validation.json"
    phase_events_path = output_dir / "safe_action_phase_events.jsonl"
    manager_manifest_path = output_dir / "manager_harness_manifest.json"
    manager_result_path = output_dir / "manager_harness_result.json"
    runner_results_path = output_dir / "safe_action_runner_results.jsonl"
    dry_run_summary_path = output_dir / "v2_safe_action_dry_run_summary.json"

    events = phase_events_for_validation(validation, run_id)
    runner_results = safe_action_runner_results(validation, run_id)
    runner_counts = result_counts(runner_results)
    executable_rows = [item["row"] for item in validation.get("rows", []) if item.get("executable")]

    manager_manifest = {
        "schema": MANAGER_MANIFEST_SCHEMA,
        "run_id": run_id,
        "scenario": V2_SAFE_ACTION_SCENARIO,
        "source_manifest": validation.get("source_manifest"),
        "dispatcher_mode": "dry_run_fail_closed",
        "supported_action_families": sorted(ALLOWED_ACTION_FAMILIES),
        "command_count": len(executable_rows),
        "commands": executable_rows,
        "raw_outputs_under_runtime": True,
        "tcp_marker_policy": "side_channel_only_no_tcp_markers",
    }
    manager_result = {
        "schema": MANAGER_RESULT_SCHEMA,
        "run_id": run_id,
        "scenario": V2_SAFE_ACTION_SCENARIO,
        "status": "dry_run_ok",
        "status_reason": "phase-aware safe-action dry run wrote side-channel events without starting 1C",
        "command_count": len(executable_rows),
        "completed_count": runner_counts.get("success", 0),
        "result_counts": runner_counts,
        "accepted_protocol_mapping": False,
        "live_action_executed": False,
        "raw_outputs_under_runtime": True,
        "runner_results_path": str(runner_results_path),
        "phase_events_path": str(phase_events_path),
        "manifest_validation_path": str(validation_path),
    }
    dry_run_summary = {
        "schema": "qa-mcp.v2-safe-action-dry-run-summary.v1",
        "generated_at": utc_now(),
        "run_id": run_id,
        "scenario": V2_SAFE_ACTION_SCENARIO,
        "status": "dry_run_ok",
        "row_count": validation["row_count"],
        "executable_count": validation["executable_count"],
        "status_counts": validation["status_counts"],
        "runner_result_counts": runner_counts,
        "phase_event_count": len(events),
        "raw_output_policy": RAW_OUTPUT_POLICY,
        "files": {
            "manifest_validation": str(validation_path),
            "phase_events": str(phase_events_path),
            "runner_results": str(runner_results_path),
            "manager_harness_manifest": str(manager_manifest_path),
            "manager_harness_result": str(manager_result_path),
        },
    }

    write_json(validation_path, validation)
    write_jsonl(phase_events_path, events)
    write_jsonl(output_dir / "case_events.jsonl", events)
    write_jsonl(runner_results_path, runner_results)
    write_json(manager_manifest_path, manager_manifest)
    write_json(manager_result_path, manager_result)
    write_json(dry_run_summary_path, dry_run_summary)

    return {
        "manifest_validation": str(validation_path),
        "phase_events": str(phase_events_path),
        "case_events": str(output_dir / "case_events.jsonl"),
        "runner_results": str(runner_results_path),
        "manager_harness_manifest": str(manager_manifest_path),
        "manager_harness_result": str(manager_result_path),
        "dry_run_summary": str(dry_run_summary_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate",), nargs="?", default="validate")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--write-phase-events", action="store_true")
    parser.add_argument("--require-executable", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validation = validate_manifest_path(args.manifest)
    output_files: dict[str, str] = {}
    if args.output_dir:
        write_json(args.output_dir / "v2_safe_action_manifest_validation.json", validation)
        if args.write_phase_events:
            output_files = write_dry_run_output(args.output_dir, validation)
    result = {
        "status": "ok",
        "validation": validation,
        "output_files": output_files,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"status=ok")
        print(f"row_count={validation['row_count']}")
        print(f"executable_count={validation['executable_count']}")
        print(f"status_counts={validation['status_counts']}")
    if args.require_executable and validation["executable_count"] == 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
