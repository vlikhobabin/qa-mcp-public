#!/usr/bin/env python3
"""Publish compact manager fixture V2 safe-action evidence."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

from v2_safe_action_tooling import (
    RAW_OUTPUT_POLICY,
    V2_SAFE_ACTION_SCENARIO,
    validate_manifest_data,
)


REPORT_SCHEMA = "qa-mcp.manager-fixture-v2-safe-action.report.v1"
CASE_ROW_SCHEMA = "protocol-corpus-case-row.v1"
SUMMARY_SCHEMA = "qa-mcp.manager-fixture-v2-safe-action.summary.v1"
MANAGER_TO_CLIENT = "manager_to_client"
CLIENT_TO_MANAGER = "client_to_manager"
DIRECTIONS = (MANAGER_TO_CLIENT, CLIENT_TO_MANAGER)
GUID_RE = re.compile(rb"(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")
SEMANTIC_TOKEN_PATTERNS = [
    re.compile(rb"(?i)\bpf_[a-z0-9_]+\b"),
    re.compile(rb"(?i)\bhomepage(?:\[[0-9a-f-]{36}\])?"),
    re.compile(rb"(?i)\be1cib/[a-z0-9_./-]+"),
    re.compile(rb"(?i)\bprotocol-fixture\.v\d+\b"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_json_optional(path: Path) -> Any | None:
    if not path.exists():
        return None
    return read_json(path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def repo_relative_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def markdown_table(rows: list[list[Any]], headers: list[str]) -> str:
    def cell(value: Any) -> str:
        if isinstance(value, (list, dict)):
            value = json.dumps(value, ensure_ascii=False)
        return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell(value) for value in row) + " |")
    return "\n".join(lines)


def load_validation(run_dir: Path) -> dict[str, Any]:
    validation_path = run_dir / "v2_safe_action_manifest_validation.json"
    if validation_path.exists():
        return read_json(validation_path)
    manager_manifest = read_json_optional(run_dir / "manager_harness_manifest.json")
    if manager_manifest:
        return validate_manifest_data(manager_manifest, run_dir / "manager_harness_manifest.json")
    raise FileNotFoundError(
        f"V2 safe-action validation output not found in {run_dir}; run the capture dry run first"
    )


def event_index(events: list[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    index: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for event in events:
        case_id = str(event.get("case_id") or event.get("action_id") or "")
        phase = str(event.get("phase") or "")
        if not case_id or not phase:
            continue
        index.setdefault(case_id, {}).setdefault(phase, []).append(event)
    return index


def runner_result_index(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for result in results:
        case_id = str(result.get("case_id") or result.get("action_id") or "")
        if case_id:
            index[case_id] = result
    return index


def parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def chunk_events(traffic_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [event for event in traffic_events if event.get("event") == "chunk"]


def first_phase_timestamp(
    phases: dict[str, list[dict[str, Any]]],
    phase: str,
) -> datetime | None:
    for event in phases.get(phase, []):
        timestamp = parse_timestamp(event.get("timestamp") or event.get("ts"))
        if timestamp is not None:
            return timestamp
    return None


def effective_chunk_window(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    if start == end:
        return start, end + timedelta(seconds=1)
    return start, end


def traffic_chunks_in_window(
    chunks: list[dict[str, Any]],
    start: datetime,
    end: datetime,
) -> list[dict[str, Any]]:
    window_start, window_end = effective_chunk_window(start, end)
    selected: list[dict[str, Any]] = []
    for chunk in chunks:
        chunk_ts = parse_timestamp(chunk.get("ts"))
        if chunk_ts is None:
            continue
        if window_start <= chunk_ts <= window_end:
            selected.append(chunk)
    return selected


def chunk_range_for_direction(chunks: list[dict[str, Any]], direction: str) -> dict[str, int] | None:
    numbers = [
        int(chunk["chunk_no"])
        for chunk in chunks
        if chunk.get("direction") == direction and isinstance(chunk.get("chunk_no"), int)
    ]
    if not numbers:
        return None
    return {"from": min(numbers), "to": max(numbers), "count": len(numbers)}


def frame_range_for_chunks(chunks: list[dict[str, Any]]) -> dict[str, dict[str, int]] | None:
    frame_range: dict[str, dict[str, int]] = {}
    for direction in DIRECTIONS:
        range_for_direction = chunk_range_for_direction(chunks, direction)
        if range_for_direction:
            frame_range[direction] = range_for_direction
    return frame_range or None


def byte_count(chunks: list[dict[str, Any]], direction: str) -> int:
    return sum(
        int(chunk.get("byte_count") or 0)
        for chunk in chunks
        if chunk.get("direction") == direction
    )


def raw_hash_for_chunks(chunks: list[dict[str, Any]]) -> str | None:
    digest = hashlib.sha256()
    seen = False
    for chunk in chunks:
        payload_b64 = chunk.get("payload_b64")
        if payload_b64:
            digest.update(base64.b64decode(str(payload_b64)))
            seen = True
        elif chunk.get("sha256"):
            digest.update(str(chunk["sha256"]).encode("ascii", errors="ignore"))
            seen = True
    return digest.hexdigest() if seen else None


def payload_bytes(chunk: dict[str, Any]) -> bytes | None:
    payload_b64 = chunk.get("payload_b64")
    if not payload_b64:
        return None
    return base64.b64decode(str(payload_b64))


def semantic_payload_tokens(payload: bytes) -> list[str]:
    lower_payload = payload.lower()
    tokens: list[str] = []
    seen: set[str] = set()
    for pattern in SEMANTIC_TOKEN_PATTERNS:
        for match in pattern.finditer(lower_payload):
            token = GUID_RE.sub(b"<guid>", match.group(0)).decode("ascii", errors="ignore")
            if token and token not in seen:
                tokens.append(token)
                seen.add(token)
    return tokens


def binary_frame_signature(chunk: dict[str, Any]) -> str | None:
    payload = payload_bytes(chunk)
    if payload is None:
        sha256 = chunk.get("sha256")
        return f"sha256:{sha256}" if sha256 else None

    direction = str(chunk.get("direction") or "unknown")
    frame_kind = payload[:1].hex() if payload else "empty"
    tokens = semantic_payload_tokens(payload)
    token_part = ",".join(tokens) if tokens else "<no-semantic-token>"
    return f"manager-fixture-v2-safe-action-binary-signature|{direction}|kind={frame_kind}|len={len(payload)}|tokens={token_part}"


def normalized_frame_signatures(chunks: list[dict[str, Any]]) -> list[str]:
    signatures = [signature for chunk in chunks if (signature := binary_frame_signature(chunk))]
    return sorted(set(signatures))


def normalized_hash_for_chunks(chunks: list[dict[str, Any]]) -> str | None:
    signatures = normalized_frame_signatures(chunks)
    if not signatures:
        return None

    digest = hashlib.sha256()
    for signature in signatures:
        digest.update(signature.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def dynamic_fields_for_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for chunk in chunks:
        payload = payload_bytes(chunk)
        if payload is None:
            continue
        tokens = semantic_payload_tokens(payload)
        fields.append(
            {
                "name": "binary_frame_dynamic_bytes"
                if tokens
                else "binary_frame_without_semantic_token",
                "source": str(chunk.get("direction") or "unknown"),
                "replacement": "<binary-frame-signature>",
                "length": len(payload),
            }
        )
    duplicate_count = len(chunks) - len(normalized_frame_signatures(chunks))
    if duplicate_count > 0:
        fields.append(
            {
                "name": "safe_action_frame_repeat_dedup",
                "source": "action_window",
                "replacement": "<unique-binary-frame-signature>",
                "length": duplicate_count,
            }
        )
    return fields


def chunk_identity(chunk: dict[str, Any]) -> tuple[str, int] | None:
    direction = str(chunk.get("direction") or "")
    chunk_no = chunk.get("chunk_no")
    if not direction or not isinstance(chunk_no, int):
        return None
    return direction, chunk_no


def background_ranges_for_chunks(
    case_chunks: list[dict[str, Any]],
    excluded_chunks: list[dict[str, Any]],
) -> list[dict[str, dict[str, int]]]:
    excluded = {identity for chunk in excluded_chunks if (identity := chunk_identity(chunk))}
    background = [
        chunk
        for chunk in case_chunks
        if (identity := chunk_identity(chunk)) and identity not in excluded
    ]
    frame_range = frame_range_for_chunks(background)
    return [frame_range] if frame_range else []


def frame_join_for_case(
    phases: dict[str, list[dict[str, Any]]],
    chunks: list[dict[str, Any]],
) -> dict[str, Any]:
    pre_read = first_phase_timestamp(phases, "pre_read")
    action_start = first_phase_timestamp(phases, "action_start")
    action_end = first_phase_timestamp(phases, "action_end")
    recovery = first_phase_timestamp(phases, "recovery")
    recovery_read = first_phase_timestamp(phases, "recovery_read")

    if not action_start or not action_end:
        return {"status": "missing_action_timestamps"}

    action_chunks = traffic_chunks_in_window(chunks, action_start, action_end)
    action_frame_range = frame_range_for_chunks(action_chunks)
    if not action_frame_range:
        return {"status": "missing_action_chunks"}

    recovery_chunks: list[dict[str, Any]] = []
    recovery_frame_range = None
    if recovery and recovery_read:
        recovery_chunks = traffic_chunks_in_window(chunks, recovery, recovery_read)
        recovery_frame_range = frame_range_for_chunks(recovery_chunks)

    background_frame_ranges: list[dict[str, dict[str, int]]] = []
    if pre_read and recovery_read:
        case_chunks = traffic_chunks_in_window(chunks, pre_read, recovery_read)
        background_frame_ranges = background_ranges_for_chunks(
            case_chunks,
            action_chunks + recovery_chunks,
        )

    return {
        "status": "joined",
        "action_frame_range": action_frame_range,
        "background_frame_ranges": background_frame_ranges,
        "recovery_frame_range": recovery_frame_range,
        "request_size": byte_count(action_chunks, MANAGER_TO_CLIENT),
        "response_size": byte_count(action_chunks, CLIENT_TO_MANAGER),
        "dynamic_fields": dynamic_fields_for_chunks(action_chunks),
        "pre_normalization_hash": raw_hash_for_chunks(action_chunks),
        "normalized_hash": normalized_hash_for_chunks(action_chunks),
        "normalization_replacements": dynamic_fields_for_chunks(action_chunks),
        "normalization_strategy": "manager_fixture_v2_safe_action_binary_frame_signature.v1",
        "action_chunk_count": len(action_chunks),
        "recovery_chunk_count": len(recovery_chunks),
    }


def frame_join_index(
    phases_by_case: dict[str, dict[str, list[dict[str, Any]]]],
    traffic_events: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    chunks = chunk_events(traffic_events)
    if not chunks:
        return {}
    return {
        case_id: frame_join_for_case(phases, chunks)
        for case_id, phases in phases_by_case.items()
    }


def proof_present(row: dict[str, Any]) -> bool:
    if row.get("acceptance_evidence"):
        return True
    probe = row.get("probe_evidence")
    if isinstance(probe, dict) and probe.get("status") == "accepted":
        return True
    side_channel = row.get("side_channel_evidence")
    if isinstance(side_channel, dict):
        return side_channel.get("validation_status") == "accepted" or side_channel.get("status") == "accepted"
    return False


def replay_status_for_row(row: dict[str, Any], validation_status: str) -> str:
    replay_status = row.get("replay_status")
    if replay_status == "accepted" and proof_present(row):
        return "accepted"
    if validation_status in {"unsupported", "blocked", "partial", "timeout", "rejected"}:
        return validation_status
    return "pending"


def action_status_for_row(
    row: dict[str, Any],
    validation_status: str,
    replay_status: str,
    runner_result: dict[str, Any] | None = None,
) -> str:
    if replay_status == "accepted":
        return "accepted"
    if runner_result and runner_result.get("status"):
        return str(runner_result["status"])
    runtime = row.get("action_runtime_result")
    if isinstance(runtime, dict) and runtime.get("status"):
        return str(runtime["status"])
    if replay_status == "accepted":
        return "accepted"
    if validation_status == "accepted_for_capture":
        return "candidate"
    return validation_status


def report_row(
    item: dict[str, Any],
    phases_by_case: dict[str, dict[str, list[dict[str, Any]]]],
    runner_by_case: dict[str, dict[str, Any]],
    frame_join_by_case: dict[str, dict[str, Any]],
    evidence_path: str,
    capture_id: str,
) -> dict[str, Any]:
    row = item["row"]
    validation_status = str(item["validation_status"])
    replay_status = replay_status_for_row(row, validation_status)
    action_status = action_status_for_row(row, validation_status, replay_status)
    case_id = str(row.get("case_id") or row.get("action_id"))
    runner_result = runner_by_case.get(case_id)
    frame_join = frame_join_by_case.get(case_id, {})
    action_status = action_status_for_row(row, validation_status, replay_status, runner_result)
    phases = phases_by_case.get(case_id, {})
    phase_names = sorted(phases)
    action_frame_range = row.get("action_frame_range") or frame_join.get("action_frame_range")
    background_frame_ranges = row.get("background_frame_ranges") or frame_join.get(
        "background_frame_ranges",
        [],
    )
    action_result_markers = row.get("action_result_markers") or (
        runner_result.get("action_result_markers") if runner_result else []
    ) or []
    recovery_result = row.get("recovery_result") or (
        runner_result.get("recovery_result") if runner_result else None
    )
    recovery_frame_range = row.get("recovery_frame_range") or (
        runner_result.get("recovery_frame_range") if runner_result else None
    ) or frame_join.get("recovery_frame_range")
    expected_markers = row.get("expected_action_result_markers") or []
    non_accepted_reasons = list(item.get("reasons") or [])
    if replay_status != "accepted":
        if not action_frame_range:
            non_accepted_reasons.append("missing_action_frame_range")
        if not action_result_markers:
            non_accepted_reasons.append("missing_action_result_markers")
        if not recovery_result:
            non_accepted_reasons.append("missing_recovery_result")
        if not recovery_frame_range and not (
            isinstance(recovery_result, dict) and recovery_result.get("known_state_rationale")
        ):
            non_accepted_reasons.append("missing_recovery_frame_range_or_known_state")
        if validation_status == "accepted_for_capture":
            non_accepted_reasons.append("replay_or_probe_unavailable")

    runtime_result = dict(runner_result) if runner_result else {"phase_events": phase_names}
    runtime_result["status"] = action_status
    if frame_join:
        runtime_result["frame_join"] = {
            key: value
            for key, value in frame_join.items()
            if key
            in {
                "status",
                "action_chunk_count",
                "recovery_chunk_count",
            }
        }

    return {
        "schema": CASE_ROW_SCHEMA,
        "case_id": case_id,
        "scenario": row.get("scenario") or V2_SAFE_ACTION_SCENARIO,
        "api_call": row.get("api_call"),
        "ui_target": row.get("ui_target"),
        "expected_state": row.get("expected_state") or row.get("pre_state"),
        "safety_class": "safe_ui_action",
        "action_id": row.get("action_id"),
        "target_id": row.get("target_id"),
        "target_marker": row.get("target_marker"),
        "mutates_business_data": row.get("mutates_business_data"),
        "allowed_action_family": row.get("allowed_action_family"),
        "expected_action_result_markers": expected_markers,
        "pre_state": row.get("pre_state"),
        "action": row.get("action"),
        "post_state": row.get("post_state"),
        "recovery_expectation": row.get("recovery_expectation"),
        "recovery_result": recovery_result,
        "action_frame_range": action_frame_range,
        "background_frame_ranges": background_frame_ranges,
        "recovery_frame_range": recovery_frame_range,
        "action_result_markers": action_result_markers,
        "rerun_determinism": runner_result.get("rerun_determinism") if runner_result else None,
        "action_runtime_result": runtime_result,
        "availability": row.get("availability", "supported"),
        "capture_id": capture_id,
        "frame_range": row.get("frame_range"),
        "request_size": row.get("request_size") or frame_join.get("request_size", 0),
        "response_size": row.get("response_size") or frame_join.get("response_size", 0),
        "dynamic_fields": row.get("dynamic_fields") or frame_join.get("dynamic_fields", []),
        "pre_normalization_hash": row.get("pre_normalization_hash")
        or frame_join.get("pre_normalization_hash"),
        "normalized_hash": row.get("normalized_hash") or frame_join.get("normalized_hash"),
        "normalization_replacements": row.get("normalization_replacements")
        or frame_join.get("normalization_replacements")
        or row.get("dynamic_fields", []),
        "normalization_strategy": row.get("normalization_strategy")
        or frame_join.get("normalization_strategy"),
        "preserved_fields": row.get("preserved_fields", []),
        "ambiguous_fields": row.get("ambiguous_fields", []),
        "operation_token": row.get("operation_token"),
        "response_markers": row.get("response_markers", []),
        "replay_status": replay_status,
        "probe_evidence": row.get("probe_evidence"),
        "side_channel_evidence": row.get("side_channel_evidence"),
        "acceptance_evidence": row.get("acceptance_evidence", []),
        "accepted_protocol_mapping": replay_status == "accepted",
        "validation_status": validation_status,
        "non_accepted_reasons": sorted(set(non_accepted_reasons)),
        "evidence_path": evidence_path,
        "semantic_sources": row.get("semantic_sources", []),
        "notes": row.get("notes", ""),
    }


def write_markdown(path: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    table_rows = [
        [
            row["case_id"],
            row["validation_status"],
            row["action_runtime_result"]["status"],
            row["replay_status"],
            row["action_frame_range"],
            row["background_frame_ranges"],
            row["recovery_frame_range"],
            row["action_result_markers"],
            row["non_accepted_reasons"],
        ]
        for row in rows
    ]
    lines = [
        "# Manager Fixture V2 Safe-Action Report",
        "",
        f"- Generated at: `{summary['generated_at']}`",
        f"- Capture id: `{summary['capture_id']}`",
        f"- Row count: `{summary['row_count']}`",
        f"- Status counts: `{json.dumps(summary['status_counts'], ensure_ascii=False)}`",
        f"- Raw output policy: {summary['raw_output_policy']}",
        "",
        "## Rows",
        "",
        markdown_table(
            table_rows,
            [
                "case",
                "validation",
                "action status",
                "replay",
                "action frames",
                "background frames",
                "recovery frames",
                "result markers",
                "non-accepted reasons",
            ],
        ),
        "",
        "## Notes",
        "",
        "- V2 action rows stay non-accepted until replay/probe or typed contract proof is retained.",
        "- Phase events are side-channel evidence and do not inject markers into TCP traffic.",
        "- Raw captures and generated replay payloads remain under ignored runtime paths.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def generate(run_dir: Path, output_dir: Path) -> dict[str, Any]:
    repo_root = repo_root_from_script()
    validation = load_validation(run_dir)
    events = read_jsonl(run_dir / "safe_action_phase_events.jsonl")
    if not events:
        events = read_jsonl(run_dir / "case_events.jsonl")
    phases_by_case = event_index(events)
    runner_by_case = runner_result_index(read_jsonl(run_dir / "safe_action_runner_results.jsonl"))
    frame_join_by_case = frame_join_index(phases_by_case, read_jsonl(run_dir / "traffic.jsonl"))

    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = repo_relative_path(output_dir, repo_root)
    capture_id = run_dir.name
    rows = [
        report_row(item, phases_by_case, runner_by_case, frame_join_by_case, evidence_path, capture_id)
        for item in validation.get("rows", [])
    ]
    status_counts = {
        status: sum(1 for row in rows if row["action_runtime_result"]["status"] == status)
        for status in sorted({row["action_runtime_result"]["status"] for row in rows})
    }
    summary = {
        "schema": SUMMARY_SCHEMA,
        "generated_at": utc_now(),
        "capture_id": capture_id,
        "run_dir": repo_relative_path(run_dir, repo_root),
        "row_count": len(rows),
        "accepted_count": sum(1 for row in rows if row["accepted_protocol_mapping"]),
        "status_counts": status_counts,
        "validation_status_counts": validation.get("status_counts", {}),
        "raw_output_policy": RAW_OUTPUT_POLICY,
        "phase_event_count": len(events),
        "runner_result_count": len(runner_by_case),
        "frame_join_count": sum(
            1 for joined in frame_join_by_case.values() if joined.get("status") == "joined"
        ),
        "output_files": {
            "safe_action_report_json": repo_relative_path(output_dir / "safe_action_report.json", repo_root),
            "safe_action_report_markdown": repo_relative_path(output_dir / "safe_action_report.md", repo_root),
            "corpus_cases": repo_relative_path(output_dir / "corpus_cases.jsonl", repo_root),
            "runtime_summary": repo_relative_path(output_dir / "runtime_summary.json", repo_root),
        },
    }
    report = {
        "schema": REPORT_SCHEMA,
        "generated_at": summary["generated_at"],
        "capture_id": capture_id,
        "validation": validation,
        "phase_event_count": len(events),
        "rows": rows,
    }

    write_json(output_dir / "safe_action_report.json", report)
    write_markdown(output_dir / "safe_action_report.md", summary, rows)
    write_jsonl(output_dir / "corpus_cases.jsonl", rows)
    write_json(output_dir / "runtime_summary.json", summary)
    write_markdown(output_dir / "runtime_summary.md", summary, rows)
    return {
        "summary": summary,
        "safe_action_report": str(output_dir / "safe_action_report.md"),
        "safe_action_report_json": str(output_dir / "safe_action_report.json"),
        "case_rows_path": str(output_dir / "corpus_cases.jsonl"),
        "summary_path": str(output_dir / "runtime_summary.json"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path, help="Ignored runtime V2 safe-action run directory.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Reviewed evidence output directory.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = generate(args.run_dir.resolve(), args.output_dir.resolve())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"safe_action_report={result['safe_action_report']}")
        print(f"case_rows={result['case_rows_path']}")
        print(f"summary={result['summary_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
