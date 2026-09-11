from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from json import JSONDecodeError
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


MANAGER_TO_CLIENT = "manager_to_client"
CLIENT_TO_MANAGER = "client_to_manager"
GUID_RE = re.compile(rb"(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")
SEMANTIC_TOKEN_PATTERNS = [
    re.compile(rb"(?i)\bpf_[a-z0-9_]+\b"),
    re.compile(rb"(?i)\bhomepage(?:\[[0-9a-f-]{36}\])?"),
    re.compile(rb"(?i)\be1cib/[a-z0-9_./-]+"),
    re.compile(rb"(?i)\bprotocol-fixture\.v\d+\b"),
]
RAW_OUTPUT_POLICY = (
    "raw TCP streams, full event logs, platform logs and generated replay "
    "output stay under ignored runtime/protocol-research paths"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_json_optional(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return read_json(path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8-sig")
    rows: list[dict[str, Any]] = []
    try:
        for line in text.splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows
    except JSONDecodeError:
        return read_json_objects(text, path)


def read_json_objects(text: str, path: Path) -> list[dict[str, Any]]:
    decoder = json.JSONDecoder()
    rows: list[dict[str, Any]] = []
    index = 0
    while index < len(text):
        while index < len(text) and text[index].isspace():
            index += 1
        if index >= len(text):
            break
        try:
            value, end = decoder.raw_decode(text, index)
        except JSONDecodeError as exc:
            raise JSONDecodeError(f"{exc.msg} while reading {path}", exc.doc, exc.pos) from exc
        if isinstance(value, dict):
            rows.append(value)
        elif isinstance(value, list):
            rows.extend(item for item in value if isinstance(item, dict))
        index = end
    return rows


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
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
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(format_cell(value) for value in row) + " |")
    return "\n".join(lines)


def format_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False)
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def count_proxy_chunks(traffic_events: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    chunks: dict[str, list[int]] = {}
    for event in traffic_events:
        if event.get("event") != "chunk":
            continue
        direction = str(event.get("direction") or "unknown")
        chunk_no = event.get("chunk_no")
        if isinstance(chunk_no, int):
            chunks.setdefault(direction, []).append(chunk_no)

    return {
        direction: {
            "first_chunk": min(numbers),
            "last_chunk": max(numbers),
            "chunk_count": len(numbers),
        }
        for direction, numbers in sorted(chunks.items())
        if numbers
    }


def parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def chunk_events(traffic_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [event for event in traffic_events if event.get("event") == "chunk"]


def event_pairs_by_case(events: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    by_case: dict[str, dict[str, dict[str, Any]]] = {}
    for event in events:
        case_id = event.get("case_id")
        if not case_id:
            continue
        phase = str(event.get("phase") or "")
        if phase not in {"before", "after"}:
            phase = "legacy"
        by_case.setdefault(str(case_id), {})[phase] = event
    return by_case


def traffic_chunks_in_window(
    chunks: list[dict[str, Any]],
    before_ts: datetime,
    after_ts: datetime,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for chunk in chunks:
        chunk_ts = parse_timestamp(chunk.get("ts"))
        if chunk_ts is None:
            continue
        if before_ts <= chunk_ts <= after_ts:
            selected.append(chunk)
    return selected


def effective_chunk_window(before_ts: datetime, after_ts: datetime) -> tuple[datetime, datetime, str | None]:
    if before_ts == after_ts:
        return before_ts, after_ts + timedelta(seconds=1), "zero_width_expanded_to_1s"
    return before_ts, after_ts, None


def chunk_range_for_direction(chunks: list[dict[str, Any]], direction: str) -> dict[str, int] | None:
    numbers = [
        int(chunk["chunk_no"])
        for chunk in chunks
        if chunk.get("direction") == direction and isinstance(chunk.get("chunk_no"), int)
    ]
    if not numbers:
        return None
    return {"from": min(numbers), "to": max(numbers), "count": len(numbers)}


def byte_count(chunks: list[dict[str, Any]], direction: str) -> int:
    return sum(int(chunk.get("byte_count") or 0) for chunk in chunks if chunk.get("direction") == direction)


def raw_hash_for_chunks(chunks: list[dict[str, Any]]) -> str | None:
    digest = hashlib.sha256()
    seen = False
    for chunk in chunks:
        payload_b64 = chunk.get("payload_b64")
        if payload_b64:
            payload = base64.b64decode(str(payload_b64))
            digest.update(payload)
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
    return f"manager-fixture-v1-binary-signature|{direction}|kind={frame_kind}|len={len(payload)}|tokens={token_part}"


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
        if tokens:
            fields.append(
                {
                    "name": "binary_frame_dynamic_bytes",
                    "source": str(chunk.get("direction") or "unknown"),
                    "replacement": "<binary-dynamic-prefix-and-nonce>",
                    "length": len(payload),
                }
            )
        else:
            fields.append(
                {
                    "name": "binary_frame_without_semantic_token",
                    "source": str(chunk.get("direction") or "unknown"),
                    "replacement": "<binary-frame-signature>",
                    "length": len(payload),
                }
            )
    duplicate_count = len(chunks) - len(normalized_frame_signatures(chunks))
    if duplicate_count > 0:
        fields.append(
            {
                "name": "polling_frame_repeat_dedup",
                "source": "selected_case_window",
                "replacement": "<unique-binary-frame-signature>",
                "length": duplicate_count,
            }
        )
    return fields


def preserved_fields_for_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counters: Counter[str] = Counter()
    for chunk in chunks:
        payload = payload_bytes(chunk)
        if payload is None:
            continue
        counters.update(semantic_payload_tokens(payload))
    return [
        {
            "name": "semantic_payload_token",
            "source": "payload_ascii",
            "value": token,
            "count": count,
        }
        for token, count in sorted(counters.items())
    ]


def ambiguous_fields_for_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not chunks:
        return []
    semantic_chunk_count = 0
    for chunk in chunks:
        payload = payload_bytes(chunk)
        if payload is not None and semantic_payload_tokens(payload):
            semantic_chunk_count += 1
    if semantic_chunk_count:
        return []
    return [
        {
            "name": "semantic_payload_token",
            "source": "selected_case_window",
            "reason": "no whitelisted binary semantic tokens were found; normalized hash is envelope-only",
        }
    ]


def response_markers(chunks: list[dict[str, Any]], command: dict[str, Any]) -> list[str]:
    markers: list[str] = []
    raw_values = [str(command.get("expected_marker") or ""), str(command.get("target_marker") or "")]
    decoded_payloads: list[str] = []
    raw_payloads: list[bytes] = []
    fallback_tokens: list[str] = []
    for chunk in chunks:
        payload = payload_bytes(chunk)
        if payload is None:
            continue
        raw_payloads.append(payload.lower())
        for token in semantic_payload_tokens(payload):
            if token not in fallback_tokens:
                fallback_tokens.append(token)
        decoded_payloads.append(payload.decode("utf-8", errors="ignore"))
        decoded_payloads.append(payload.decode("utf-16-le", errors="ignore"))
    joined_payload = "\n".join(decoded_payloads)
    for marker in raw_values:
        marker_bytes = marker.encode("utf-8", errors="ignore").lower()
        if marker and marker in joined_payload and marker not in markers:
            markers.append(marker)
        elif marker_bytes and any(marker_bytes in payload for payload in raw_payloads) and marker not in markers:
            markers.append(marker)
    if not markers:
        markers.extend(fallback_tokens[:8])
    return markers


def command_windows(event_pairs: dict[str, dict[str, dict[str, Any]]]) -> dict[str, tuple[datetime, datetime]]:
    windows: dict[str, tuple[datetime, datetime]] = {}
    for case_id, pair in event_pairs.items():
        before_ts = parse_timestamp(pair.get("before", {}).get("timestamp"))
        after_ts = parse_timestamp(pair.get("after", {}).get("timestamp"))
        if before_ts and after_ts and before_ts <= after_ts:
            windows[case_id] = (before_ts, after_ts)
    return windows


def overlaps_other(case_id: str, before_ts: datetime, after_ts: datetime, windows: dict[str, tuple[datetime, datetime]]) -> bool:
    for other_case_id, (other_before, other_after) in windows.items():
        if other_case_id == case_id:
            continue
        if before_ts < other_after and other_before < after_ts:
            return True
    return False


def load_replay_probe_evidence(paths: list[Path], repo_root: Path) -> dict[str, dict[str, Any]]:
    evidence_by_case: dict[str, dict[str, Any]] = {}
    for path in paths:
        data = read_json(path)
        if data.get("schema") != "qa-mcp.manager-fixture-v1.replay-probe-summary.v1":
            raise ValueError(f"Unsupported replay probe summary schema in {path}: {data.get('schema')}")
        if data.get("transport_status") != "ok" or data.get("no_response_frames"):
            continue

        for case in data.get("accepted_probe_cases") or []:
            case_id = str(case.get("case_id") or "")
            if not case_id:
                continue
            if case_id in evidence_by_case:
                raise ValueError(f"Duplicate replay probe evidence for case_id={case_id}")
            evidence_by_case[case_id] = {
                "schema": "qa-mcp.manager-fixture-v1.case-replay-evidence.v1",
                "status": str(case.get("replay_status") or "accepted_probe"),
                "case_id": case_id,
                "evidence_path": repo_relative_path(path, repo_root),
                "source_capture": data.get("source_capture"),
                "successful_replay_dir": data.get("successful_replay_dir"),
                "manager_frame_range": case.get("manager_frame_range"),
                "response_after_send": case.get("response_after_send"),
                "response_size": case.get("response_size"),
                "expected_marker": case.get("expected_marker"),
                "normalized_hash": case.get("normalized_hash"),
                "observed_dynamic_fields": data.get("observed_dynamic_fields") or {},
                "adaptation": data.get("adaptation") or {},
            }
    return evidence_by_case


def evaluate_replay_evidence(case: dict[str, Any], evidence_by_case: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    evidence = evidence_by_case.get(str(case.get("case_id") or ""))
    if evidence is None:
        return None

    mismatches: list[str] = []
    if case.get("join_status") != "joined":
        mismatches.append("case_not_joined")

    expected_range = evidence.get("manager_frame_range") or {}
    actual_range = case.get("manager_chunk_range") or {}
    for key in ("from", "to"):
        if expected_range.get(key) != actual_range.get(key):
            mismatches.append(f"manager_frame_{key}_mismatch")

    expected_hash = evidence.get("normalized_hash")
    actual_hash = case.get("normalized_hash")
    if expected_hash and actual_hash and expected_hash != actual_hash:
        mismatches.append("normalized_hash_mismatch")
    elif expected_hash and not actual_hash:
        mismatches.append("normalized_hash_missing")

    result = dict(evidence)
    result["validation_status"] = "accepted" if not mismatches else "mismatch"
    result["validation_mismatches"] = mismatches
    return result


def evaluate_side_channel_contract(case: dict[str, Any], command: dict[str, Any]) -> dict[str, Any] | None:
    contract = command.get("acceptance_contract")
    if not isinstance(contract, dict):
        return None

    kind = str(contract.get("kind") or "")
    if kind != "manager_result_preview_contains":
        return None

    expected_marker = str(contract.get("expected_result_preview_marker") or command.get("expected_marker") or "")
    result_preview = str(case.get("after_result_preview") or "")
    mismatches: list[str] = []
    if case.get("join_status") != "joined":
        mismatches.append("case_not_joined")
    if case.get("result_status") != "ok":
        mismatches.append("result_status_not_ok")
    if not case.get("normalized_hash"):
        mismatches.append("normalized_hash_missing")
    if not expected_marker:
        mismatches.append("expected_result_preview_marker_missing")
    elif expected_marker not in result_preview:
        mismatches.append("result_preview_marker_missing")

    return {
        "schema": "qa-mcp.manager-fixture-v1.case-side-channel-evidence.v1",
        "status": "accepted_side_channel",
        "case_id": case.get("case_id"),
        "kind": kind,
        "evidence_source": contract.get("evidence_source") or "manager_case_event.after.result_preview",
        "expected_result_preview_marker": expected_marker,
        "observed_result_preview": result_preview,
        "manager_frame_range": case.get("manager_chunk_range"),
        "normalized_hash": case.get("normalized_hash"),
        "validation_status": "accepted" if not mismatches else "mismatch",
        "validation_mismatches": mismatches,
    }


def corpus_row_for_case(case: dict[str, Any], command: dict[str, Any], selected_chunks: list[dict[str, Any]]) -> dict[str, Any]:
    manager_range = case.get("manager_chunk_range")
    client_range = case.get("client_chunk_range")
    dynamic_fields = dynamic_fields_for_chunks(selected_chunks)
    preserved_fields = preserved_fields_for_chunks(selected_chunks)
    ambiguous_fields = ambiguous_fields_for_chunks(selected_chunks)
    normalized_signatures = normalized_frame_signatures(selected_chunks)
    frame_range = None
    if manager_range or client_range:
        frame_range = {}
        if manager_range:
            frame_range[MANAGER_TO_CLIENT] = {key: manager_range[key] for key in ("from", "to")}
        if client_range:
            frame_range[CLIENT_TO_MANAGER] = {key: client_range[key] for key in ("from", "to")}

    accepted = bool(case.get("accepted_protocol_mapping"))
    replay_evidence = case.get("replay_evidence")
    side_channel_evidence = case.get("side_channel_evidence")
    acceptance_evidence: list[str] = []
    if accepted and replay_evidence:
        acceptance_evidence.extend(
            [
                "replay_probe_status=accepted_probe",
                f"replay_probe_summary={replay_evidence.get('evidence_path')}",
                f"response_after_send={replay_evidence.get('response_after_send')}",
            ]
        )
    if accepted and side_channel_evidence:
        acceptance_evidence.extend(
            [
                "side_channel_contract_status=accepted",
                f"side_channel_contract_kind={side_channel_evidence.get('kind')}",
                f"result_preview_marker={side_channel_evidence.get('expected_result_preview_marker')}",
            ]
        )

    return {
        "schema": "protocol-corpus-case-row.v1",
        "case_id": case["case_id"],
        "scenario": "manager-fixture-v1-readonly",
        "api_call": command.get("command_kind"),
        "ui_target": command.get("target_fixture_path"),
        "expected_state": f"target_marker={command.get('target_marker')}; expected_marker={command.get('expected_marker')}",
        "acceptance_contract": command.get("acceptance_contract"),
        "safety_class": command.get("safety_class", "read_only"),
        "element_family": command.get("element_family"),
        "availability": "available" if accepted else "pending" if case["join_status"] == "joined" else "unresolved",
        "expected_response_markers": [value for value in [command.get("target_marker"), command.get("expected_marker")] if value],
        "capture_id": case["run_id"],
        "frame_range": frame_range,
        "request_size": byte_count(selected_chunks, MANAGER_TO_CLIENT),
        "response_size": byte_count(selected_chunks, CLIENT_TO_MANAGER),
        "dynamic_fields": dynamic_fields,
        "pre_normalization_hash": raw_hash_for_chunks(selected_chunks),
        "normalized_hash": normalized_hash_for_chunks(selected_chunks),
        "normalization_replacements": dynamic_fields,
        "normalization_strategy": "manager_fixture_v1_binary_frame_signature.v1",
        "normalized_frame_signature_count": len(normalized_signatures),
        "raw_selected_chunk_count": len(selected_chunks),
        "preserved_fields": preserved_fields,
        "ambiguous_fields": ambiguous_fields,
        "operation_token": None,
        "response_markers": response_markers(selected_chunks, command),
        "replay_status": case.get("replay_status") or "pending" if case["join_status"] == "joined" else "not_run",
        "probe_status": "accepted" if accepted else "not_run",
        "replay_evidence": replay_evidence,
        "side_channel_evidence": side_channel_evidence,
        "acceptance_evidence": acceptance_evidence,
        "accepted_protocol_mapping": accepted,
        "join_status": case["join_status"],
        "unresolved_reason": case["unresolved_reason"],
        "notes": (
            "Manager fixture V1 row accepted by retained replay/probe or side-channel evidence."
            if accepted
            else "Manager fixture V1 rows remain non-accepted until replay or direct probe support is reviewed."
        ),
    }


def build_frame_report(
    manifest: dict[str, Any],
    result: dict[str, Any],
    case_events: list[dict[str, Any]],
    traffic_events: list[dict[str, Any]],
    runtime_dir: Path,
    generated_at: str,
    replay_evidence_by_case: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    run_id = str(manifest.get("run_id") or result.get("run_id") or runtime_dir.name)
    traffic_chunks = count_proxy_chunks(traffic_events)
    chunks = chunk_events(traffic_events)
    event_pairs = event_pairs_by_case(case_events)
    windows = command_windows(event_pairs)
    result_status = str(result.get("status") or "unknown")
    is_dry_run = result_status == "dry_run_ok"
    commands = list(manifest.get("commands") or [])

    cases: list[dict[str, Any]] = []
    corpus_rows: list[dict[str, Any]] = []
    replay_evidence_by_case = replay_evidence_by_case or {}
    for command in commands:
        case_id = str(command.get("case_id") or "")
        pair = event_pairs.get(case_id, {})
        before_event = pair.get("before")
        after_event = pair.get("after")
        before_ts = parse_timestamp(before_event.get("timestamp")) if before_event else None
        after_ts = parse_timestamp(after_event.get("timestamp")) if after_event else None
        selected_chunks: list[dict[str, Any]] = []
        manager_range = None
        client_range = None
        timestamp_window_adjustment = None

        if not before_event:
            join_status = "unresolved"
            unresolved_reason = "no_before_event"
        elif not after_event:
            join_status = "unresolved"
            unresolved_reason = "no_after_event"
        elif is_dry_run:
            join_status = "unresolved"
            unresolved_reason = "dry_run_no_proxy_chunks"
        elif not chunks:
            join_status = "unresolved"
            unresolved_reason = "no_proxy_chunks"
        elif before_ts is None or after_ts is None or before_ts > after_ts:
            join_status = "unresolved"
            unresolved_reason = "invalid_event_window"
        elif overlaps_other(case_id, before_ts, after_ts, windows):
            join_status = "unresolved"
            unresolved_reason = "overlapping_case_window"
        else:
            effective_before_ts, effective_after_ts, timestamp_window_adjustment = effective_chunk_window(before_ts, after_ts)
            selected_chunks = traffic_chunks_in_window(chunks, effective_before_ts, effective_after_ts)
            if not selected_chunks:
                join_status = "unresolved"
                unresolved_reason = "no_chunks_in_case_window"
            else:
                manager_range = chunk_range_for_direction(selected_chunks, MANAGER_TO_CLIENT)
                client_range = chunk_range_for_direction(selected_chunks, CLIENT_TO_MANAGER)
                if manager_range is None and client_range is None:
                    join_status = "unresolved"
                    unresolved_reason = "no_directional_chunk_range"
                else:
                    join_status = "joined"
                    unresolved_reason = None

        normalized_hash = normalized_hash_for_chunks(selected_chunks) if selected_chunks else None
        case = {
            "run_id": run_id,
            "case_id": case_id,
            "command_id": command.get("command_id"),
            "command_kind": command.get("command_kind"),
            "phase": "readonly",
            "target_marker": command.get("target_marker"),
            "expected_marker": command.get("expected_marker"),
            "before_event_seen": before_event is not None,
            "after_event_seen": after_event is not None,
            "event_seen": before_event is not None or after_event is not None,
            "result_status": after_event.get("status") if after_event else before_event.get("status") if before_event else "not_run",
            "before_result_preview": before_event.get("result_preview") if before_event else None,
            "after_result_preview": after_event.get("result_preview") if after_event else None,
            "join_status": join_status,
            "manager_chunk_range": manager_range,
            "client_chunk_range": client_range,
            "chunk_count": len(selected_chunks),
            "request_size": byte_count(selected_chunks, MANAGER_TO_CLIENT),
            "response_size": byte_count(selected_chunks, CLIENT_TO_MANAGER),
            "unresolved_reason": unresolved_reason,
            "timestamp_window_adjustment": timestamp_window_adjustment,
            "normalized_hash": normalized_hash,
            "replay_status": "pending" if join_status == "joined" else "not_run",
            "direct_probe_status": "not_run",
            "accepted_protocol_mapping": False,
        }
        replay_evidence = evaluate_replay_evidence(case, replay_evidence_by_case)
        if replay_evidence:
            case["replay_evidence"] = replay_evidence
            if replay_evidence["validation_status"] == "accepted":
                case["replay_status"] = "accepted_probe"
                case["accepted_protocol_mapping"] = True
            else:
                case["replay_status"] = "evidence_mismatch"
        side_channel_evidence = evaluate_side_channel_contract(case, command)
        if side_channel_evidence:
            case["side_channel_evidence"] = side_channel_evidence
            if side_channel_evidence["validation_status"] == "accepted" and not case["accepted_protocol_mapping"]:
                case["replay_status"] = "accepted_side_channel"
                case["direct_probe_status"] = "accepted_side_channel"
                case["accepted_protocol_mapping"] = True
            elif side_channel_evidence["validation_status"] != "accepted" and not case["accepted_protocol_mapping"]:
                case["direct_probe_status"] = "side_channel_mismatch"
        cases.append(case)
        corpus_rows.append(corpus_row_for_case(case, command, selected_chunks))

    accepted_case_ids = [case["case_id"] for case in cases if case.get("accepted_protocol_mapping")]
    return {
        "schema": "qa-mcp.manager-fixture-v1.frame-join-report.v1",
        "generated_at": generated_at,
        "run_id": run_id,
        "source_runtime_dir": str(runtime_dir),
        "traffic_chunk_summary": traffic_chunks,
        "case_count": len(cases),
        "join_status_counts": dict(Counter(case["join_status"] for case in cases)),
        "accepted_case_ids": accepted_case_ids,
        "cases": cases,
        "corpus_rows": corpus_rows,
        "raw_output_policy": RAW_OUTPUT_POLICY,
    }


def synthesize_missing_result(
    manifest: dict[str, Any],
    runtime_dir: Path,
    generated_at: str,
) -> dict[str, Any]:
    invocation = read_json_optional(runtime_dir / "manager_harness_invocation.json") or {}
    commands = list(manifest.get("commands") or [])
    invocation_status = str(invocation.get("status") or "missing")
    if invocation_status == "invoking":
        status = "harness_no_result"
        reason = "manager harness invocation was started, but manager_harness_result.json is missing"
    else:
        status = "missing_manager_harness_result"
        reason = "manager_harness_result.json is missing from the retained runtime directory"

    return {
        "schema": "qa-mcp.manager-fixture-v1.result.v1",
        "run_id": manifest.get("run_id") or runtime_dir.name,
        "scenario": "manager-fixture-v1-readonly",
        "status": status,
        "status_reason": reason,
        "manifest_path": str(runtime_dir / "manager_harness_manifest.json"),
        "case_events_path": str(runtime_dir / "case_events.jsonl"),
        "manager_harness_invocation_path": str(runtime_dir / "manager_harness_invocation.json"),
        "output_dir": str(runtime_dir),
        "command_count": len(commands),
        "completed_count": 0,
        "failed_count": 0,
        "incomplete_count": len(commands),
        "accepted_protocol_mapping": False,
        "incomplete_runtime": True,
        "synthesized_at": generated_at,
    }


def build_summary(
    manifest: dict[str, Any],
    result: dict[str, Any],
    case_events: list[dict[str, Any]],
    frame_report: dict[str, Any],
    runtime_dir: Path,
    output_dir: Path,
    generated_at: str,
) -> dict[str, Any]:
    run_id = str(manifest.get("run_id") or result.get("run_id") or runtime_dir.name)
    bootstrap_events = [event for event in case_events if event.get("phase") == "bootstrap"]
    command_events = [event for event in case_events if event.get("phase") in {"before", "after"}]
    legacy_readonly_events = [event for event in case_events if event.get("phase") == "readonly"]
    commands = list(manifest.get("commands") or [])
    unresolved_reasons = Counter(
        str(case.get("unresolved_reason"))
        for case in frame_report.get("cases", [])
        if case.get("unresolved_reason")
    )
    unresolved_gaps = [
        {
            "gap": reason,
            "owner_route": "project:qa-mcp",
            "reason": f"{count} command(s) unresolved with reason={reason}",
            "residual_risk": "command remains non-accepted until live range, replay or direct probe evidence is retained",
        }
        for reason, count in sorted(unresolved_reasons.items())
    ]
    accepted_case_ids = list(frame_report.get("accepted_case_ids") or [])
    result_status = str(result.get("status") or "unknown")
    if result_status == "runtime_gap":
        unresolved_gaps.insert(
            0,
            {
                "gap": "runtime_gap",
                "owner_route": "project:qa-mcp",
                "reason": str(result.get("status_reason") or "manager fixture live capture did not start"),
                "residual_risk": "no live TCP traffic exists for this run",
            },
        )
    elif result.get("incomplete_runtime") or result_status in {
        "runner_timeout",
        "harness_invocation_failed",
        "harness_no_result",
        "harness_missing_events",
        "missing_manager_harness_result",
    }:
        unresolved_gaps.insert(
            0,
            {
                "gap": result_status,
                "owner_route": "project:qa-mcp",
                "reason": str(result.get("status_reason") or "manager fixture runtime artifacts are incomplete"),
                "residual_risk": "side-channel command windows remain incomplete until the manager harness emits before/after events and a final result",
            },
        )

    return {
        "schema": "qa-mcp.manager-fixture-v1.reviewed-summary.v1",
        "generated_at": generated_at,
        "run_id": run_id,
        "source_runtime_dir": str(runtime_dir),
        "reviewed_output_dir": str(output_dir),
        "fixture_version": manifest.get("fixture_version"),
        "command_catalog_version": manifest.get("schema"),
        "manager_harness": manifest.get("manager_harness"),
        "target_fixture_path": manifest.get("target_fixture_path"),
        "proxy_testclient_port": manifest.get("proxy_testclient_port"),
        "run_status": result.get("status"),
        "status_reason": result.get("status_reason"),
        "bootstrap_status": bootstrap_events[0].get("status") if bootstrap_events else "not_seen",
        "command_count": len(commands),
        "event_count": len(case_events),
        "readonly_event_count": len(command_events) or len(legacy_readonly_events),
        "completed_count": result.get("completed_count", 0),
        "failed_count": result.get("failed_count", 0),
        "case_status_counts": dict(Counter(str(event.get("status") or "unknown") for event in case_events)),
        "frame_join_status_counts": frame_report.get("join_status_counts", {}),
        "accepted_protocol_mapping": bool(accepted_case_ids),
        "accepted_case_ids": accepted_case_ids,
        "output_files": {
            "runtime_manifest": str(runtime_dir / "manager_harness_manifest.json"),
            "runtime_result": str(runtime_dir / "manager_harness_result.json"),
            "runtime_case_events": str(runtime_dir / "case_events.jsonl"),
            "reviewed_summary_markdown": str(output_dir / "runtime_summary.md"),
            "reviewed_summary_json": str(output_dir / "runtime_summary.json"),
            "reviewed_frame_join_markdown": str(output_dir / "frame_join_report.md"),
            "reviewed_frame_join_json": str(output_dir / "frame_join_report.json"),
            "reviewed_corpus_rows": str(output_dir / "corpus_cases.jsonl"),
        },
        "owner_routes": {
            "runtime_apply": "project:qa-mcp",
            "ui_proof": "/opt/vanessa-mcp-stack",
            "bsl_diagnostics": "/opt/edt-lab",
            "frame_join": "project:qa-mcp",
            "replay_or_direct_probe": "project:qa-mcp",
        },
        "unresolved_gaps": unresolved_gaps,
        "raw_output_policy": RAW_OUTPUT_POLICY,
    }


def write_summary_markdown(path: Path, summary: dict[str, Any], frame_report: dict[str, Any]) -> None:
    rows = [
        ["run_id", summary["run_id"]],
        ["run_status", summary["run_status"]],
        ["status_reason", summary["status_reason"]],
        ["fixture_version", summary["fixture_version"]],
        ["command_catalog_version", summary["command_catalog_version"]],
        ["bootstrap_status", summary["bootstrap_status"]],
        ["command_count", summary["command_count"]],
        ["readonly_event_count", summary["readonly_event_count"]],
        ["accepted_protocol_mapping", summary["accepted_protocol_mapping"]],
        ["accepted_case_ids", summary["accepted_case_ids"]],
    ]
    files = [[name, value] for name, value in summary["output_files"].items()]
    gaps = [
        [gap["gap"], gap["owner_route"], gap["reason"], gap["residual_risk"]]
        for gap in summary["unresolved_gaps"]
    ]
    join_counts = [[name, count] for name, count in summary["frame_join_status_counts"].items()]

    acceptance_boundary = (
        "Accepted case ids are published only where retained replay/probe evidence "
        "or typed side-channel evidence matches the command contract while joined "
        "frame range and normalized hash evidence are retained."
        if summary["accepted_case_ids"]
        else "No command from this run is published as an accepted protocol mapping. "
        "Accepted mappings still require frame ranges, dynamic-field evidence, "
        "normalized hashes and replay/probe proof or a typed side-channel contract."
    )

    lines = [
        "# Manager Fixture V1 Runtime Summary",
        "",
        f"- Generated at: `{summary['generated_at']}`",
        f"- Source runtime directory: `{summary['source_runtime_dir']}`",
        f"- Raw output policy: {RAW_OUTPUT_POLICY}.",
        "",
        "## Run",
        "",
        markdown_table(rows, ["field", "value"]),
        "",
        "## Frame Join Counts",
        "",
        markdown_table(join_counts, ["join_status", "count"]) if join_counts else "No command rows were reported.",
        "",
        "## Reviewed And Runtime Files",
        "",
        markdown_table(files, ["file", "path"]),
        "",
        "## Gaps",
        "",
        markdown_table(gaps, ["gap", "owner route", "reason", "residual risk"]),
        "",
        "## Acceptance Boundary",
        "",
        acceptance_boundary,
        "",
        "## Frame Join Report",
        "",
        f"See `{Path(summary['output_files']['reviewed_frame_join_markdown']).name}`.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_frame_markdown(path: Path, frame_report: dict[str, Any]) -> None:
    rows = [
        [
            case["case_id"],
            case["command_id"],
            case["command_kind"],
            case["result_status"],
            case["event_seen"],
            case["join_status"],
            case["timestamp_window_adjustment"],
            case["manager_chunk_range"],
            case["client_chunk_range"],
            case["unresolved_reason"],
            case["replay_status"],
            case["accepted_protocol_mapping"],
        ]
        for case in frame_report["cases"]
    ]
    lines = [
        "# Manager Fixture V1 Frame Join Report",
        "",
        f"- Generated at: `{frame_report['generated_at']}`",
        f"- Run id: `{frame_report['run_id']}`",
        f"- Source runtime directory: `{frame_report['source_runtime_dir']}`",
        f"- Join status counts: `{json.dumps(frame_report['join_status_counts'], ensure_ascii=False)}`",
        f"- Accepted case ids: `{json.dumps(frame_report['accepted_case_ids'], ensure_ascii=False)}`",
        "",
        "## Cases",
        "",
        markdown_table(
            rows,
            [
                "case",
                "command",
                "kind",
                "result",
                "event",
                "join",
                "time adjustment",
                "manager chunks",
                "client chunks",
                "unresolved reason",
                "replay",
                "accepted",
            ],
        ),
        "",
        "## Notes",
        "",
        "- `joined` means side-channel command windows were matched to proxy chunk ranges.",
        "- `blocked` means the retained run did not emit a side-channel event for that catalog command.",
        "- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.",
        "- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.",
        "- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.",
        "- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate(run_dir: Path, output_dir: Path, replay_probe_summary_paths: list[Path] | None = None) -> dict[str, Any]:
    manifest = read_json(run_dir / "manager_harness_manifest.json")
    generated_at = utc_now()
    result = read_json_optional(run_dir / "manager_harness_result.json")
    if result is None:
        result = synthesize_missing_result(manifest, run_dir, generated_at)
    case_events = read_jsonl(run_dir / "case_events.jsonl")
    traffic_events = read_jsonl(run_dir / "traffic.jsonl")
    repo_root = repo_root_from_script()
    replay_evidence_by_case = load_replay_probe_evidence(replay_probe_summary_paths or [], repo_root)

    output_dir.mkdir(parents=True, exist_ok=True)
    frame_report = build_frame_report(
        manifest,
        result,
        case_events,
        traffic_events,
        run_dir,
        generated_at,
        replay_evidence_by_case,
    )
    summary = build_summary(manifest, result, case_events, frame_report, run_dir, output_dir, generated_at)

    write_json(output_dir / "frame_join_report.json", frame_report)
    write_frame_markdown(output_dir / "frame_join_report.md", frame_report)
    write_jsonl(output_dir / "corpus_cases.jsonl", list(frame_report.get("corpus_rows", [])))
    write_json(output_dir / "runtime_summary.json", summary)
    write_summary_markdown(output_dir / "runtime_summary.md", summary, frame_report)

    return {
        "runtime_summary": str(output_dir / "runtime_summary.md"),
        "runtime_summary_json": str(output_dir / "runtime_summary.json"),
        "frame_join_report": str(output_dir / "frame_join_report.md"),
        "frame_join_report_json": str(output_dir / "frame_join_report.json"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish compact manager fixture V1 evidence.")
    parser.add_argument("--run-dir", type=Path, required=True, help="Ignored runtime run directory.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Reviewed evidence output directory.")
    parser.add_argument(
        "--replay-probe-summary",
        type=Path,
        action="append",
        default=[],
        help="Optional manager-fixture-v1 replay/probe summary JSON used to promote accepted rows.",
    )
    args = parser.parse_args()

    result = generate(args.run_dir, args.output_dir, args.replay_probe_summary)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
