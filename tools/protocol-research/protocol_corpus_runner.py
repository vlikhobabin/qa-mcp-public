#!/usr/bin/env python3
"""Build marked protocol corpus rows from 1C TestClient captures."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from analyze_capture import Chunk, payload_from_record
from extract_payloads import (
    MANAGER_TO_CLIENT,
    CLIENT_TO_MANAGER,
    ascii_strings,
    strip_tail,
    ui_identifiers,
    utf16le_strings,
)
from report_manager_fixture_v1 import generate as generate_manager_fixture_v1
from report_manager_fixture_v2_safe_action import generate as generate_manager_fixture_v2
from v2_safe_action_tooling import (
    V2_SAFE_ACTION_SCENARIO,
    validate_manifest_data,
)


SCHEMA = "protocol-corpus-run.v1"
CASE_ROW_SCHEMA = "protocol-corpus-case-row.v1"
CASE_EVENTS_SCHEMA = "protocol-corpus-case-events.v1"
UNRESOLVED_STATUSES = {"pending", "unsupported", "partial", "timeout", "rejected", "blocked"}
TAIL_MARKER = bytes.fromhex("6653b2a6")
GUID_ASCII_RE = re.compile(
    rb"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
GUID_UTF16LE_RE = re.compile(
    rb"(?:[0-9a-fA-F]\x00){8}-\x00"
    rb"(?:[0-9a-fA-F]\x00){4}-\x00"
    rb"(?:[0-9a-fA-F]\x00){4}-\x00"
    rb"(?:[0-9a-fA-F]\x00){4}-\x00"
    rb"(?:[0-9a-fA-F]\x00){12}"
)
FRAME_SEPARATOR = b"\n--qa-mcp-corpus-frame--\n"


@dataclass(frozen=True)
class FrameRange:
    manager_from: int
    manager_to: int
    client_from: int
    client_to: int

    @classmethod
    def from_manager(cls, manager_from: int, manager_to: int) -> "FrameRange":
        return cls(
            manager_from=manager_from,
            manager_to=manager_to,
            client_from=manager_from + 1,
            client_to=manager_to + 1,
        )

    def to_json(self) -> dict[str, dict[str, int]]:
        return {
            MANAGER_TO_CLIENT: {"from": self.manager_from, "to": self.manager_to},
            CLIENT_TO_MANAGER: {"from": self.client_from, "to": self.client_to},
        }


@dataclass(frozen=True)
class CorpusCase:
    case_id: str
    scenario: str
    api_call: str
    ui_target: str | None
    expected_state: str
    safety_class: str
    replay_expectation: str
    frame_range: FrameRange | None = None
    element_family: str | None = None
    availability: str = "supported"
    expected_response_markers: tuple[str, ...] = ()
    action_id: str | None = None
    target_id: str | None = None
    target_marker: str | None = None
    pre_state: str | None = None
    action: str | None = None
    post_state: str | None = None
    recovery_expectation: str | None = None
    mutates_business_data: bool | None = None
    allowed_action_family: str | None = None
    expected_action_result_markers: tuple[str, ...] = ()
    action_result_markers: tuple[str, ...] = ()
    action_frame_range: FrameRange | None = None
    background_frame_ranges: tuple[FrameRange, ...] = ()
    notes: str = ""

    def to_manifest_row(self) -> dict[str, Any]:
        row = {
            "case_id": self.case_id,
            "scenario": self.scenario,
            "api_call": self.api_call,
            "ui_target": self.ui_target,
            "expected_state": self.expected_state,
            "safety_class": self.safety_class,
            "replay_expectation": self.replay_expectation,
            "frame_range": self.frame_range.to_json() if self.frame_range else None,
            "element_family": self.element_family,
            "availability": self.availability,
            "expected_response_markers": list(self.expected_response_markers),
            "notes": self.notes,
        }
        if self.safety_class == "safe_ui_action":
            row.update(
                {
                    "action_id": self.action_id,
                    "target_id": self.target_id,
                    "target_marker": self.target_marker,
                    "pre_state": self.pre_state,
                    "action": self.action,
                    "post_state": self.post_state,
                    "recovery_expectation": self.recovery_expectation,
                    "mutates_business_data": self.mutates_business_data,
                    "allowed_action_family": self.allowed_action_family,
                    "expected_action_result_markers": list(self.expected_action_result_markers),
                    "action_result_markers": list(self.action_result_markers),
                    "action_frame_range": (
                        self.action_frame_range.to_json()
                        if self.action_frame_range
                        else self.frame_range.to_json()
                        if self.frame_range
                        else None
                    ),
                    "background_frame_ranges": [
                        frame_range.to_json() for frame_range in self.background_frame_ranges
                    ],
                }
            )
        return row


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def timestamp_name() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def captures_root(repo_root: Path) -> Path:
    return repo_root / "runtime" / "protocol-research" / "captures"


def resolve_capture_dir(value: str | Path, repo_root: Path) -> Path:
    path = Path(value)
    if path.exists():
        return path.resolve()
    candidate = captures_root(repo_root) / str(value)
    if candidate.exists():
        return candidate.resolve()
    raise FileNotFoundError(f"Capture directory not found: {value}")


def repo_relative_path(path: Path, repo_root: Path) -> str:
    resolved = path.resolve()
    if resolved.is_relative_to(repo_root):
        return str(resolved.relative_to(repo_root)).replace("\\", "/")
    return str(resolved)


def readonly_smoke_cases() -> list[CorpusCase]:
    return [
        CorpusCase(
            case_id="active-window-context",
            scenario="readonly-smoke",
            api_call="TestedApplication.GetActiveWindow + TestedClientApplicationWindow read-only properties",
            ui_target="MainFrame/HomePage active window",
            expected_state="TestClient is attached and the start page window is active.",
            safety_class="read_only",
            replay_expectation="python_probe_supported",
            frame_range=FrameRange.from_manager(8, 11),
            expected_response_markers=("HomePage", "MainFrame"),
            notes="Initial active-window context frames observed in the baseline capture and direct Python probe.",
        ),
        CorpusCase(
            case_id="active-form-context",
            scenario="readonly-smoke",
            api_call="TestedApplication.GetActiveForm + TestedForm read-only metadata",
            ui_target="HomePage.ManagedForm sales dashboard report form",
            expected_state="Active form metadata is available without mutating the infobase.",
            safety_class="read_only",
            replay_expectation="python_probe_supported",
            frame_range=FrameRange.from_manager(12, 17),
            expected_response_markers=("ManagedForm", "EditField"),
            notes="Includes active form descriptor and form element summary frames.",
        ),
        CorpusCase(
            case_id="form-element-details",
            scenario="readonly-smoke",
            api_call="TestedForm.FindObject/GetChildObjects + form element read-only property probes",
            ui_target="Two EditField chart controls on the active managed form",
            expected_state="Element captions and references are returned for the selected form elements.",
            safety_class="read_only",
            replay_expectation="python_probe_supported",
            frame_range=FrameRange.from_manager(101, 106),
            element_family="EditField",
            expected_response_markers=("EditField",),
            notes="Known operation token at request offset 51 is echoed in responses at offset 13.",
        ),
    ]


def unsupported_family_case(element_family: str, reason: str) -> CorpusCase:
    case_id = f"{element_family.lower()}-family-readonly-gap"
    return CorpusCase(
        case_id=case_id,
        scenario="expanded-readonly",
        api_call=f"TestedForm read-only property probes for {element_family} controls",
        ui_target=f"{element_family} element on the active managed form",
        expected_state="Current active form should expose the element before a wire mapping can be captured.",
        safety_class="read_only",
        replay_expectation="unsupported",
        frame_range=None,
        element_family=element_family,
        availability="unsupported",
        expected_response_markers=(element_family,),
        notes=reason,
    )


def expanded_readonly_cases() -> list[CorpusCase]:
    reason = (
        "Current sales dashboard probe evidence exposes only EditField form elements; "
        "fixture authoring is required before this family can be captured safely."
    )
    cases = readonly_smoke_cases()
    cases.append(
        CorpusCase(
            case_id="typed-input-field-readonly",
            scenario="expanded-readonly",
            api_call="TestedForm.FindObject/GetChildObjects + typed input EditField read-only property probes",
            ui_target="Two EditField chart controls on the active managed form",
            expected_state="Typed input field descriptors are returned without focus, input or data mutation.",
            safety_class="read_only",
            replay_expectation="python_probe_supported",
            frame_range=FrameRange.from_manager(101, 106),
            element_family="EditField",
            availability="supported",
            expected_response_markers=("EditField",),
            notes="Confirmed by the form-element-details Python-manager probe path for current lab fixture.",
        )
    )
    cases.extend(
        unsupported_family_case(element_family, reason)
        for element_family in ("Button", "Table", "CommandBar", "Page", "Label", "CheckBox")
    )
    return cases


def default_cases(case_set: str = "readonly-smoke") -> list[CorpusCase]:
    if case_set == "readonly-smoke":
        return readonly_smoke_cases()
    if case_set == "expanded-readonly":
        return expanded_readonly_cases()
    raise ValueError(f"Unsupported seeded case set: {case_set}")


def load_case_manifest(path: Path | None, case_set: str) -> list[CorpusCase]:
    if path is None:
        return default_cases(case_set)
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    validation = validate_manifest_data(data, path.resolve())
    rejected = [
        row for row in validation["rows"]
        if row["validation_status"] == "rejected"
        and row["row"].get("safety_class") == "safe_ui_action"
    ]
    if rejected:
        reasons = "; ".join(
            f"{row['case_id']}={','.join(row['reasons'])}" for row in rejected
        )
        raise ValueError(f"Invalid V2 safe-action manifest row(s): {reasons}")
    raw_rows = data.get("cases", []) if isinstance(data, dict) else data if isinstance(data, list) else []
    cases: list[CorpusCase] = []
    for row in raw_rows:
        range_obj = frame_range_from_json(row.get("frame_range"))
        action_range = frame_range_from_json(row.get("action_frame_range"))
        background_ranges = tuple(
            frame_range
            for frame_range in (
                frame_range_from_json(item)
                for item in row.get("background_frame_ranges", [])
            )
            if frame_range is not None
        )
        cases.append(
            CorpusCase(
                case_id=row["case_id"],
                scenario=row.get("scenario", "custom"),
                api_call=row["api_call"],
                ui_target=row.get("ui_target"),
                expected_state=row.get("expected_state", ""),
                safety_class=row.get("safety_class", "read_only"),
                replay_expectation=row.get("replay_expectation", "pending"),
                frame_range=range_obj,
                element_family=row.get("element_family"),
                availability=row.get("availability", "supported"),
                expected_response_markers=tuple(row.get("expected_response_markers", [])),
                action_id=row.get("action_id"),
                target_id=row.get("target_id"),
                target_marker=row.get("target_marker"),
                pre_state=row.get("pre_state"),
                action=row.get("action"),
                post_state=row.get("post_state"),
                recovery_expectation=row.get("recovery_expectation"),
                mutates_business_data=row.get("mutates_business_data"),
                allowed_action_family=row.get("allowed_action_family"),
                expected_action_result_markers=tuple(row.get("expected_action_result_markers", [])),
                action_result_markers=tuple(
                    row.get("action_result_markers", row.get("expected_action_result_markers", []))
                ),
                action_frame_range=action_range,
                background_frame_ranges=background_ranges,
                notes=row.get("notes", ""),
            )
        )
    return cases


def frame_range_from_json(frame_range: Any) -> FrameRange | None:
    if not frame_range:
        return None
    manager_range = frame_range.get(MANAGER_TO_CLIENT, frame_range)
    client_range = frame_range.get(CLIENT_TO_MANAGER)
    manager_from = int(manager_range["from"])
    manager_to = int(manager_range["to"])
    if client_range:
        return FrameRange(
            manager_from=manager_from,
            manager_to=manager_to,
            client_from=int(client_range["from"]),
            client_to=int(client_range["to"]),
        )
    return FrameRange.from_manager(manager_from, manager_to)


def read_traffic_chunks(capture_dir: Path) -> tuple[list[dict[str, Any]], list[Chunk]]:
    traffic_path = capture_dir / "traffic.jsonl"
    if not traffic_path.exists():
        raise FileNotFoundError(f"traffic.jsonl not found: {traffic_path}")

    events: list[dict[str, Any]] = []
    chunks: list[Chunk] = []
    with traffic_path.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            if not line.strip():
                continue
            record = json.loads(line)
            events.append(record)
            if record.get("event") != "chunk":
                continue
            chunks.append(
                Chunk(
                    ts=record["ts"],
                    connection_id=int(record["connection_id"]),
                    direction=record["direction"],
                    chunk_no=int(record["chunk_no"]),
                    byte_count=int(record["byte_count"]),
                    sha256=record.get("sha256", ""),
                    aggregate_offset=int(record.get("aggregate_offset", 0)),
                    aggregate_path=Path(record.get("aggregate_path", "")),
                    payload=payload_from_record(record),
                )
            )
    return events, chunks


def chunks_by_direction(chunks: Iterable[Chunk]) -> dict[str, dict[int, Chunk]]:
    result: dict[str, dict[int, Chunk]] = {
        MANAGER_TO_CLIENT: {},
        CLIENT_TO_MANAGER: {},
    }
    for chunk in chunks:
        result.setdefault(chunk.direction, {})[chunk.chunk_no] = chunk
    return result


def select_chunks(index: dict[str, dict[int, Chunk]], direction: str, start: int, end: int) -> list[Chunk]:
    selected: list[Chunk] = []
    for chunk_no in range(start, end + 1):
        chunk = index.get(direction, {}).get(chunk_no)
        if chunk is not None:
            selected.append(chunk)
    return selected


def replacement_bytes(label: str, length: int) -> bytes:
    seed = f"<{label}>".encode("ascii")
    if len(seed) >= length:
        return seed[:length]
    return seed + (b"_" * (length - len(seed)))


def replace_range(payload: bytearray, start: int, end: int, label: str) -> None:
    if 0 <= start < end <= len(payload):
        payload[start:end] = replacement_bytes(label, end - start)


def replace_regex_ranges(payload: bytearray, pattern: re.Pattern[bytes], label: str) -> None:
    original = bytes(payload)
    for match in pattern.finditer(original):
        replace_range(payload, match.start(), match.end(), label)


def normalize_payload(payload: bytes) -> bytes:
    body = bytearray(strip_tail(payload))
    if len(body) >= 18:
        replace_range(body, 2, 18, "ack_guid_uuid_le")
    if len(body) >= 21:
        replace_range(body, 19, 21, "sequence_uint16_le")
    if len(body) >= 84:
        replace_range(body, 68, 84, "nonce")

    replace_regex_ranges(body, GUID_ASCII_RE, "ascii_guid")
    replace_regex_ranges(body, GUID_UTF16LE_RE, "utf16_guid")
    return bytes(body)


def sha256_hex(payloads: Iterable[bytes]) -> str:
    digest = hashlib.sha256()
    first = True
    for payload in payloads:
        if not first:
            digest.update(FRAME_SEPARATOR)
        digest.update(payload)
        first = False
    return digest.hexdigest()


def dynamic_fields_for_chunk(chunk: Chunk) -> list[dict[str, Any]]:
    body = strip_tail(chunk.payload)
    fields: list[dict[str, Any]] = []
    if len(body) >= 18:
        fields.append(
            {
                "name": "ack_guid_uuid_le",
                "source": "binary",
                "direction": chunk.direction,
                "frame": chunk.chunk_no,
                "offset": 2,
                "length": 16,
                "original_class": "guid",
                "replacement": "<ack_guid_uuid_le>",
                "value_hex": body[2:18].hex(),
            }
        )
    if len(body) >= 21:
        fields.append(
            {
                "name": "sequence_uint16_le",
                "source": "binary",
                "direction": chunk.direction,
                "frame": chunk.chunk_no,
                "offset": 19,
                "length": 2,
                "original_class": "counter",
                "replacement": "<sequence_uint16_le>",
                "value_hex": body[19:21].hex(),
            }
        )
    if len(body) >= 84:
        fields.append(
            {
                "name": "nonce",
                "source": "binary",
                "direction": chunk.direction,
                "frame": chunk.chunk_no,
                "offset": 68,
                "length": 16,
                "original_class": "opaque_bytes",
                "replacement": "<nonce>",
                "value_hex": body[68:84].hex(),
            }
        )
    for match in GUID_ASCII_RE.finditer(body):
        fields.append(
            {
                "name": "ascii_guid",
                "source": "ascii",
                "direction": chunk.direction,
                "frame": chunk.chunk_no,
                "offset": match.start(),
                "length": match.end() - match.start(),
                "original_class": "guid",
                "replacement": "<ascii_guid>",
                "value": match.group(0).decode("ascii", errors="replace"),
            }
        )
    for match in GUID_UTF16LE_RE.finditer(body):
        fields.append(
            {
                "name": "utf16_guid",
                "source": "utf16le",
                "direction": chunk.direction,
                "frame": chunk.chunk_no,
                "offset": match.start(),
                "length": match.end() - match.start(),
                "original_class": "guid",
                "replacement": "<utf16_guid>",
                "value": match.group(0).decode("utf-16-le", errors="replace"),
            }
        )
    return fields


def preserved_fields_for_chunk(chunk: Chunk) -> list[dict[str, Any]]:
    body = strip_tail(chunk.payload)
    if len(body) < 67:
        return []
    return [
        {
            "name": "operation_token",
            "source": "binary",
            "direction": chunk.direction,
            "frame": chunk.chunk_no,
            "offset": 51,
            "length": 16,
            "original_class": "opaque_bytes",
            "normalization_role": "preserved_semantic_token",
            "replacement": None,
            "reason": "Command-like token is kept in the normalized request hash until repeatability evidence proves it is safe to replace.",
            "value_hex": body[51:67].hex(),
        }
    ]


def operation_token_for_chunks(chunks: list[Chunk]) -> dict[str, Any] | None:
    values: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()
    for chunk in chunks:
        body = strip_tail(chunk.payload)
        if len(body) < 67:
            continue
        token = body[51:67].hex()
        key = (chunk.chunk_no, token)
        if key in seen:
            continue
        seen.add(key)
        values.append({"frame": chunk.chunk_no, "offset": 51, "hex": token})
    if not values:
        return None
    return {
        "kind": "operation_token_51_hex",
        "values": values,
        "known_response_echo_offset": 13,
    }


def response_markers_for_chunks(chunks: list[Chunk], limit: int = 20) -> list[str]:
    markers: list[str] = []
    for chunk in chunks:
        body = strip_tail(chunk.payload)
        utf16_values = utf16le_strings(body, limit=12)
        identifiers = ui_identifiers(ascii_strings(body, limit=12), utf16_values)
        for value in identifiers:
            normalized = value.strip()
            if normalized and normalized not in markers:
                markers.append(normalized)
                if len(markers) >= limit:
                    return markers
    return markers


def replay_status_for_case(case: CorpusCase, probe_result: dict[str, Any] | None) -> str:
    if case.availability in UNRESOLVED_STATUSES:
        return case.availability
    if case.replay_expectation in UNRESOLVED_STATUSES:
        return case.replay_expectation
    if probe_result is None:
        return "pending" if case.replay_expectation in {"python_probe_supported", "replay_supported"} else "unsupported"
    if probe_result.get("status") != "ok":
        return "rejected"
    if case.case_id == "active-window-context":
        if any(frame.get("semantic_guess") == "main_frame_with_home_page" for frame in probe_result.get("frames", [])):
            return "accepted"
        return "partial"
    if case.case_id == "active-form-context":
        if probe_result.get("active_form_name") and probe_result.get("managed_form_ref"):
            return "accepted"
        return "partial"
    if case.case_id in {"form-element-details", "typed-input-field-readonly"}:
        if int(probe_result.get("element_detail_count") or 0) > 0:
            return "accepted"
        return "partial"
    return "partial"


def probe_evidence_for_case(
    case: CorpusCase,
    probe_result: dict[str, Any] | None,
    probe_result_path: Path | None,
    repo_root: Path,
    probe_status: str,
) -> dict[str, Any] | None:
    if probe_result is None:
        return None
    source_capture = probe_result.get("capture_dir")
    return {
        "kind": "direct_python_manager",
        "status": probe_status,
        "query": probe_result.get("query") or case.case_id,
        "case_id": case.case_id,
        "case_family": case.element_family or case.case_id,
        "evidence_path": repo_relative_path(probe_result_path, repo_root) if probe_result_path else None,
        "source_capture_id": Path(source_capture).name if source_capture else None,
        "frame_mode": probe_result.get("frame_mode"),
        "response_marker_count": len(probe_result.get("frames", [])),
        "notes": "Compact direct Python-manager probe evidence; raw probe output remains under runtime/protocol-research/.",
    }


def make_case_events(case: CorpusCase, manager_chunks: list[Chunk], client_chunks: list[Chunk], row: dict[str, Any]) -> list[dict[str, Any]]:
    first_ts = manager_chunks[0].ts if manager_chunks else utc_now()
    last_ts = client_chunks[-1].ts if client_chunks else first_ts
    if case.frame_range:
        counters_before = {
            MANAGER_TO_CLIENT: max(0, case.frame_range.manager_from - 1),
            CLIENT_TO_MANAGER: max(0, case.frame_range.client_from - 1),
        }
        counters_after = {
            MANAGER_TO_CLIENT: case.frame_range.manager_to,
            CLIENT_TO_MANAGER: case.frame_range.client_to,
        }
        event_status = "ok" if manager_chunks else "missing_frames"
    else:
        counters_before = {}
        counters_after = {}
        event_status = row["replay_status"]
    common = {
        "schema": CASE_EVENTS_SCHEMA,
        "case_id": case.case_id,
        "scenario": case.scenario,
    }
    events = [
        {
            **common,
            "ts": first_ts,
            "event": "case_start",
            "chunk_counters_before": counters_before,
            "api_call": case.api_call,
            "ui_target": case.ui_target,
            "pre_state": case.pre_state,
        },
        {
            **common,
            "ts": first_ts,
            "event": "case_step",
            "expected_state": case.expected_state,
            "frame_range": case.frame_range.to_json() if case.frame_range else None,
            "action_frame_range": row.get("action_frame_range"),
            "background_frame_ranges": row.get("background_frame_ranges", []),
            "element_family": case.element_family,
            "availability": case.availability,
            "action": case.action,
        },
        {
            **common,
            "ts": last_ts,
            "event": "case_result",
            "chunk_counters_after": counters_after,
            "replay_status": row["replay_status"],
            "normalized_hash": row["normalized_hash"],
            "response_marker_count": len(row["response_markers"]),
            "post_state": case.post_state,
            "action_result_markers": list(case.action_result_markers),
        },
        {
            **common,
            "ts": last_ts,
            "event": "case_end",
            "status": event_status,
            "recovery_expectation": case.recovery_expectation,
        },
    ]
    if case.safety_class == "safe_ui_action":
        events.insert(
            1,
            {
                **common,
                "ts": first_ts,
                "event": "action_start",
                "status": row["replay_status"],
                "action": case.action,
                "pre_state": case.pre_state,
                "action_frame_range": row.get("action_frame_range"),
            },
        )
        events.insert(
            -1,
            {
                **common,
                "ts": last_ts,
                "event": "action_end",
                "status": row["replay_status"],
                "post_state": case.post_state,
                "recovery_expectation": case.recovery_expectation,
                "action_result_markers": list(case.action_result_markers),
                "background_frame_ranges": row.get("background_frame_ranges", []),
            },
        )
    return events


def load_safe_action_result(capture_dir: Path) -> dict[str, Any] | None:
    path = capture_dir / "safe_action_result.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def safe_action_fields(case: CorpusCase, action_result: dict[str, Any] | None = None) -> dict[str, Any]:
    if case.safety_class != "safe_ui_action":
        return {}
    action_range = case.action_frame_range or case.frame_range
    action_result_markers = list(case.action_result_markers)
    if action_result:
        status = action_result.get("status") or "pending"
        action_result_markers = [f"status={status}", "window_title_observed"]
    runtime_result = None
    if action_result:
        pre_title = action_result.get("preWindowTitle")
        target_title = action_result.get("targetWindowTitle")
        post_title = action_result.get("postWindowTitle")
        recovered_title = action_result.get("recoveredWindowTitle")
        runtime_result = {
            "status": action_result.get("status"),
            "target_selected": bool(target_title),
            "post_matches_target": bool(target_title and post_title == target_title),
            "recovered_matches_pre": bool(pre_title and recovered_title == pre_title),
            "title_values_redacted": True,
            "notes": action_result.get("notes"),
        }
    return {
        "action_id": case.action_id or case.case_id,
        "target_id": case.target_id,
        "target_marker": case.target_marker,
        "pre_state": case.pre_state,
        "action": case.action,
        "post_state": case.post_state,
        "recovery_expectation": case.recovery_expectation,
        "mutates_business_data": case.mutates_business_data,
        "allowed_action_family": case.allowed_action_family,
        "expected_action_result_markers": list(case.expected_action_result_markers),
        "action_result_markers": action_result_markers,
        "action_frame_range": action_range.to_json() if action_range else None,
        "background_frame_ranges": [
            frame_range.to_json() for frame_range in case.background_frame_ranges
        ],
        "action_runtime_result": runtime_result,
    }


def make_case_row(
    case: CorpusCase,
    capture_dir: Path,
    evidence_path: str,
    index: dict[str, dict[int, Chunk]],
    probe_result: dict[str, Any] | None,
    probe_result_path: Path | None,
    repo_root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manager_chunks: list[Chunk] = []
    client_chunks: list[Chunk] = []
    if case.frame_range:
        manager_chunks = select_chunks(
            index,
            MANAGER_TO_CLIENT,
            case.frame_range.manager_from,
            case.frame_range.manager_to,
        )
        client_chunks = select_chunks(
            index,
            CLIENT_TO_MANAGER,
            case.frame_range.client_from,
            case.frame_range.client_to,
        )
    dynamic_fields = [
        field
        for chunk in manager_chunks
        for field in dynamic_fields_for_chunk(chunk)
    ]
    preserved_fields = [
        field
        for chunk in manager_chunks
        for field in preserved_fields_for_chunk(chunk)
    ]
    pre_normalization_hash = sha256_hex(strip_tail(chunk.payload) for chunk in manager_chunks) if manager_chunks else None
    normalized_hash = sha256_hex(normalize_payload(chunk.payload) for chunk in manager_chunks) if manager_chunks else None
    probe_status = replay_status_for_case(case, probe_result)
    replay_status = probe_status
    notes = case.notes
    if probe_status == "accepted" and normalized_hash is None:
        replay_status = "partial"
        notes = (
            f"{notes} Direct probe returned expected read-only data, but the reviewed "
            "request-frame hash is incomplete for this corpus row."
        ).strip()
    acceptance_evidence = []
    if replay_status == "accepted":
        acceptance_evidence.append("direct_python_manager_probe_status=accepted")
    row = {
        "schema": CASE_ROW_SCHEMA,
        "case_id": case.case_id,
        "scenario": case.scenario,
        "api_call": case.api_call,
        "ui_target": case.ui_target,
        "expected_state": case.expected_state,
        "safety_class": case.safety_class,
        "element_family": case.element_family,
        "availability": case.availability,
        "expected_response_markers": list(case.expected_response_markers),
        "capture_id": capture_dir.name,
        "frame_range": case.frame_range.to_json() if case.frame_range else None,
        "request_size": sum(chunk.byte_count for chunk in manager_chunks),
        "response_size": sum(chunk.byte_count for chunk in client_chunks),
        "dynamic_fields": dynamic_fields,
        "pre_normalization_hash": pre_normalization_hash,
        "normalized_hash": normalized_hash,
        "normalization_replacements": dynamic_fields,
        "preserved_fields": preserved_fields,
        "ambiguous_fields": [],
        "operation_token": operation_token_for_chunks(manager_chunks),
        "response_markers": response_markers_for_chunks(client_chunks),
        "replay_status": replay_status,
        "probe_evidence": probe_evidence_for_case(case, probe_result, probe_result_path, repo_root, probe_status),
        "acceptance_evidence": acceptance_evidence,
        "evidence_path": evidence_path,
        "semantic_sources": [],
        "notes": notes,
    }
    row.update(safe_action_fields(case, load_safe_action_result(capture_dir)))
    return row, make_case_events(case, manager_chunks, client_chunks, row)


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as file_obj:
        for row in rows:
            file_obj.write(json.dumps(row, ensure_ascii=False) + "\n")


def markdown_table(rows: list[list[Any]], headers: list[str]) -> str:
    def cell(value: Any) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell(value) for value in row) + " |")
    return "\n".join(lines)


def write_report(path: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    def frame_range_text(row: dict[str, Any]) -> str:
        frame_range = row.get("frame_range")
        if not frame_range:
            return "n/a"
        return json.dumps(frame_range[MANAGER_TO_CLIENT], ensure_ascii=False)

    def hash_prefix(row: dict[str, Any]) -> str:
        value = row.get("normalized_hash")
        return value[:16] if value else "n/a"

    table_rows = [
        [
            row["case_id"],
            row.get("element_family") or "",
            row.get("availability", "supported"),
            row["api_call"],
            frame_range_text(row),
            row["request_size"],
            row["response_size"],
            hash_prefix(row),
            row["replay_status"],
            len(row["response_markers"]),
        ]
        for row in rows
    ]
    lines = [
        "# Protocol Corpus Report",
        "",
        f"- Generated at: `{summary['generated_at']}`",
        f"- Capture id: `{summary['capture_id']}`",
        f"- Capture dir: `{summary['capture_dir']}`",
        f"- Case count: `{summary['case_count']}`",
        f"- Case rows: `{summary['case_rows_path']}`",
        f"- Case events: `{summary['case_events_path']}`",
        "",
        "## Case Rows",
        "",
        markdown_table(
            table_rows,
            [
                "case",
                "family",
                "availability",
                "api call",
                "manager frames",
                "request bytes",
                "response bytes",
                "hash prefix",
                "replay",
                "markers",
            ],
        ),
        "",
        "## Notes",
        "",
        "- Case events are side-channel evidence; no markers are injected into the TCP stream.",
        "- Raw traffic remains under `runtime/protocol-research/captures/`.",
        "- `accepted` replay status means the direct Python-manager probe returned the expected read-only data.",
        "- `unsupported` family rows are explicit fixture gaps and intentionally have no frame range.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def load_probe_result(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def run_capture(args: argparse.Namespace, repo_root: Path) -> Path:
    capture_script = repo_root / "tools" / "protocol-research" / "run_protocol_capture.ps1"
    command = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(capture_script),
        "-Scenario",
        args.capture_scenario,
    ]
    optional_args = {
        "-ClientBin": args.client_bin,
        "-ClientInfobasePath": args.client_infobase,
        "-ManagerInfobasePath": args.manager_infobase,
        "-VanessaEpf": args.vanessa_epf,
        "-SafeActionManifestPath": args.safe_action_manifest,
    }
    for key, value in optional_args.items():
        if value:
            command.extend([key, str(value)])
    if args.capture_dry_run:
        command.append("-DryRun")
    completed = subprocess.run(command, cwd=repo_root, text=True, capture_output=True, check=False)
    run_log_dir = repo_root / "runtime" / "protocol-research" / "corpus-runner"
    run_log_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_log_dir / f"capture-{timestamp_name()}.log"
    log_path.write_text(completed.stdout + "\n--- STDERR ---\n" + completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"run_protocol_capture.ps1 failed with exit code {completed.returncode}; log={log_path}")
    for line in completed.stdout.splitlines():
        if line.startswith("capture-dir="):
            return Path(line.split("=", 1)[1].strip()).resolve()
    raise RuntimeError(f"run_protocol_capture.ps1 did not print capture-dir; log={log_path}")


def build_corpus(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = repo_root_from_script()
    capture_dir = run_capture(args, repo_root) if args.run_capture else resolve_capture_dir(args.capture_dir, repo_root)
    if args.capture_scenario == "manager-fixture-v1-readonly":
        evidence_dir = args.evidence_dir
        if evidence_dir is None:
            evidence_dir = (
                repo_root
                / "docs"
                / "protocol-research"
                / "evidence"
                / "manager-fixture-v1-live-join"
                / capture_dir.name
            )
        evidence_dir = evidence_dir.resolve()
        manager_result = generate_manager_fixture_v1(capture_dir, evidence_dir)
        summary = json.loads((evidence_dir / "runtime_summary.json").read_text(encoding="utf-8-sig"))
        return {
            "capture_dir": str(capture_dir),
            "evidence_dir": str(evidence_dir),
            "case_rows_path": str(evidence_dir / "corpus_cases.jsonl"),
            "summary_path": str(evidence_dir / "runtime_summary.json"),
            "report_path": str(evidence_dir / "runtime_summary.md"),
            "case_events_path": str(capture_dir / "case_events.jsonl"),
            "case_manifest_path": str(capture_dir / "manager_harness_manifest.json"),
            "frame_join_report": manager_result["frame_join_report"],
            "case_count": int(summary.get("command_count") or 0),
            "replay_status_counts": {"not_run": int(summary.get("command_count") or 0)},
        }
    if args.capture_scenario == V2_SAFE_ACTION_SCENARIO:
        evidence_dir = args.evidence_dir
        if evidence_dir is None:
            evidence_dir = (
                repo_root
                / "docs"
                / "protocol-research"
                / "evidence"
                / "manager-fixture-v2-safe-action"
                / capture_dir.name
            )
        evidence_dir = evidence_dir.resolve()
        manager_result = generate_manager_fixture_v2(capture_dir, evidence_dir)
        summary = manager_result["summary"]
        return {
            "capture_dir": str(capture_dir),
            "evidence_dir": str(evidence_dir),
            "case_rows_path": manager_result["case_rows_path"],
            "summary_path": manager_result["summary_path"],
            "report_path": manager_result["safe_action_report"],
            "case_events_path": str(capture_dir / "safe_action_phase_events.jsonl"),
            "case_manifest_path": str(capture_dir / "manager_harness_manifest.json"),
            "safe_action_report": manager_result["safe_action_report"],
            "safe_action_report_json": manager_result["safe_action_report_json"],
            "case_count": int(summary.get("row_count") or 0),
            "replay_status_counts": summary.get("status_counts", {}),
        }
    cases = load_case_manifest(args.case_manifest, args.case_set)
    _, chunks = read_traffic_chunks(capture_dir)
    index = chunks_by_direction(chunks)
    probe_result = load_probe_result(args.probe_result)

    evidence_dir = args.evidence_dir
    if evidence_dir is None:
        evidence_dir = repo_root / "docs" / "protocol-research" / "evidence" / "corpus" / f"{capture_dir.name}-{args.case_set}"
    evidence_dir = evidence_dir.resolve()
    evidence_dir.mkdir(parents=True, exist_ok=True)

    output_dir = args.output_dir.resolve() if args.output_dir else capture_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    evidence_path = str(evidence_dir.relative_to(repo_root)).replace("\\", "/")
    rows: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    for case in cases:
        row, case_events = make_case_row(case, capture_dir, evidence_path, index, probe_result, args.probe_result, repo_root)
        rows.append(row)
        events.extend(case_events)

    manifest = {
        "schema": SCHEMA,
        "generated_at": utc_now(),
        "capture_id": capture_dir.name,
        "capture_dir": str(capture_dir),
        "case_set": args.case_set,
        "cases": [case.to_manifest_row() for case in cases],
        "raw_output_dir": str(output_dir),
        "evidence_dir": str(evidence_dir),
        "probe_result": str(args.probe_result.resolve()) if args.probe_result else None,
        "capture_path_policy": "raw traffic and logs stay under ignored runtime/protocol-research paths",
    }

    runtime_manifest_path = output_dir / "case_manifest.json"
    runtime_events_path = output_dir / "case_events.jsonl"
    runtime_manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_jsonl(runtime_events_path, events)

    case_rows_path = evidence_dir / "corpus_cases.jsonl"
    summary_path = evidence_dir / "corpus_summary.json"
    report_path = evidence_dir / "corpus_report.md"
    write_jsonl(case_rows_path, rows)

    summary = {
        "schema": SCHEMA,
        "generated_at": manifest["generated_at"],
        "capture_id": capture_dir.name,
        "capture_dir": str(capture_dir),
        "case_count": len(rows),
        "case_ids": [row["case_id"] for row in rows],
        "replay_status_counts": {
            status: sum(1 for row in rows if row["replay_status"] == status)
            for status in sorted({row["replay_status"] for row in rows})
        },
        "availability_counts": {
            status: sum(1 for row in rows if row["availability"] == status)
            for status in sorted({row["availability"] for row in rows})
        },
        "element_families": sorted({row["element_family"] for row in rows if row.get("element_family")}),
        "supported_case_ids": [row["case_id"] for row in rows if row["availability"] == "supported"],
        "gap_case_ids": [row["case_id"] for row in rows if row["availability"] != "supported"],
        "case_rows_path": str(case_rows_path.relative_to(repo_root)).replace("\\", "/"),
        "case_events_path": str(runtime_events_path.relative_to(repo_root)).replace("\\", "/"),
        "runtime_manifest_path": str(runtime_manifest_path.relative_to(repo_root)).replace("\\", "/"),
        "raw_output_policy": manifest["capture_path_policy"],
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(report_path, summary, rows)

    return {
        "capture_dir": str(capture_dir),
        "evidence_dir": str(evidence_dir),
        "case_rows_path": str(case_rows_path),
        "summary_path": str(summary_path),
        "report_path": str(report_path),
        "case_events_path": str(runtime_events_path),
        "case_manifest_path": str(runtime_manifest_path),
        "case_count": len(rows),
        "replay_status_counts": summary["replay_status_counts"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-dir", default="20260602-084433", help="Capture directory or id under runtime/protocol-research/captures.")
    parser.add_argument("--run-capture", action="store_true", help="Run run_protocol_capture.ps1 first, then build corpus evidence from the new capture.")
    parser.add_argument(
        "--capture-scenario",
        choices=(
            "connect-only",
            "active-window",
            "form-analysis",
            "safe-action",
            "manager-fixture-v1-readonly",
            V2_SAFE_ACTION_SCENARIO,
            "all",
        ),
        default="all",
        help="Scenario passed to run_protocol_capture.ps1 when --run-capture is used.",
    )
    parser.add_argument("--case-set", default="readonly-smoke")
    parser.add_argument("--case-manifest", type=Path, help="Optional JSON case manifest. Defaults to the seeded readonly-smoke matrix.")
    parser.add_argument("--safe-action-manifest", type=Path, help="Reviewed V2 safe-action manifest used by the manager-fixture-v2-safe-action scenario.")
    parser.add_argument("--capture-dry-run", action="store_true", help="Pass -DryRun to the Windows capture runner.")
    parser.add_argument("--probe-result", type=Path, help="Optional python_manager_probe_result.json used to classify replay_status.")
    parser.add_argument("--output-dir", type=Path, help="Runtime output dir for case_manifest.json and case_events.jsonl. Defaults to the capture dir.")
    parser.add_argument("--evidence-dir", type=Path, help="Reviewed compact evidence dir. Defaults to docs/protocol-research/evidence/corpus/<capture>-readonly-smoke.")
    parser.add_argument("--client-bin")
    parser.add_argument("--client-infobase")
    parser.add_argument("--manager-infobase")
    parser.add_argument("--vanessa-epf")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_corpus(args)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"capture_dir={result['capture_dir']}")
        print(f"evidence_dir={result['evidence_dir']}")
        print(f"case_rows={result['case_rows_path']}")
        print(f"case_events={result['case_events_path']}")
        print(f"case_count={result['case_count']}")
        print(f"replay_status_counts={result['replay_status_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
