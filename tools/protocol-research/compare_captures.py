#!/usr/bin/env python3
"""Compare multiple 1C TestManager/TestClient protocol captures."""

from __future__ import annotations

import argparse
import base64
import json
import re
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MANAGER_TO_CLIENT = "manager_to_client"
CLIENT_TO_MANAGER = "client_to_manager"
TAIL_MARKER = bytes.fromhex("6653b2a6")
GUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
CLIENT_ACK_GUID_RE = re.compile(
    r'\{"#",' + GUID_RE.pattern + r",\s*\r?\n\{(" + GUID_RE.pattern + r")\}",
    re.IGNORECASE,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def timestamp_name() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def captures_root(repo_root: Path) -> Path:
    return repo_root / "runtime" / "protocol-research" / "captures"


def latest_capture_dirs(repo_root: Path, count: int) -> list[Path]:
    root = captures_root(repo_root)
    candidates = [path for path in root.iterdir() if path.is_dir() and (path / "traffic.jsonl").exists()]
    candidates.sort(key=lambda path: path.name)
    if len(candidates) < count:
        raise FileNotFoundError(f"Only {len(candidates)} captures found under {root}, need {count}")
    return candidates[-count:]


def resolve_capture_dir(value: str, repo_root: Path) -> Path:
    path = Path(value)
    if path.exists():
        return path.resolve()
    candidate = captures_root(repo_root) / value
    if candidate.exists():
        return candidate.resolve()
    raise FileNotFoundError(f"Capture directory not found: {value}")


def strip_tail(payload: bytes) -> bytes:
    if payload.endswith(TAIL_MARKER):
        return payload[: -len(TAIL_MARKER)]
    return payload


def payload_from_record(record: dict[str, Any]) -> bytes:
    payload_b64 = record.get("payload_b64")
    if payload_b64:
        return base64.b64decode(payload_b64)

    aggregate_path = Path(record["aggregate_path"])
    offset = int(record["aggregate_offset"])
    byte_count = int(record["byte_count"])
    with aggregate_path.open("rb") as file_obj:
        file_obj.seek(offset)
        return file_obj.read(byte_count)


def read_chunks(capture_dir: Path) -> dict[str, list[bytes]]:
    traffic_path = capture_dir / "traffic.jsonl"
    if not traffic_path.exists():
        raise FileNotFoundError(f"traffic.jsonl not found: {traffic_path}")

    chunks: dict[str, list[bytes]] = {
        MANAGER_TO_CLIENT: [],
        CLIENT_TO_MANAGER: [],
    }
    with traffic_path.open("r", encoding="utf-8") as file_obj:
        for line in file_obj:
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("event") != "chunk":
                continue
            direction = record["direction"]
            if direction in chunks:
                chunks[direction].append(payload_from_record(record))
    return chunks


def decode_text_frame(payload: bytes) -> str | None:
    body = strip_tail(payload)
    try:
        return body.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None


def header_fields(payload: bytes) -> list[str]:
    text = decode_text_frame(payload)
    if not text:
        return []
    first_line = text.lstrip("\ufeff").splitlines()[0].strip()
    if first_line.startswith("{"):
        first_line = first_line[1:]
    if first_line.endswith("}"):
        first_line = first_line[:-1]
    return [field.strip() for field in first_line.split(",") if field.strip()]


def client_ack_guid(payload: bytes) -> str | None:
    text = decode_text_frame(payload)
    if not text:
        return None
    match = CLIENT_ACK_GUID_RE.search(text)
    if not match:
        return None
    return match.group(1).lower()


def hex_slice(payload: bytes, start: int, end: int) -> str:
    body = strip_tail(payload)
    if len(body) < end:
        return ""
    return body[start:end].hex()


def uuid_le_at(payload: bytes, offset: int) -> str:
    body = strip_tail(payload)
    if len(body) < offset + 16:
        return ""
    return str(uuid.UUID(bytes_le=body[offset : offset + 16]))


def uint16_le_at(payload: bytes, offset: int) -> int | None:
    body = strip_tail(payload)
    if len(body) < offset + 2:
        return None
    return int.from_bytes(body[offset : offset + 2], byteorder="little")


def find_positions(haystack: bytes, needle: bytes) -> list[int]:
    if not needle:
        return []
    positions: list[int] = []
    start = 0
    while True:
        offset = haystack.find(needle, start)
        if offset < 0:
            return positions
        positions.append(offset)
        start = offset + 1


def diff_ranges(left: bytes, right: bytes) -> list[dict[str, Any]]:
    limit = min(len(left), len(right))
    ranges: list[dict[str, Any]] = []
    start: int | None = None
    for index in range(limit):
        if left[index] != right[index] and start is None:
            start = index
        if (left[index] == right[index] or index == limit - 1) and start is not None:
            end = index if left[index] == right[index] else index + 1
            ranges.append({"start": start, "end": end, "length": end - start})
            start = None
    if len(left) != len(right):
        ranges.append({"start": limit, "end": max(len(left), len(right)), "length": abs(len(left) - len(right))})
    return ranges


def summarize_capture(capture_dir: Path) -> dict[str, Any]:
    chunks = read_chunks(capture_dir)
    manager = chunks[MANAGER_TO_CLIENT]
    client = chunks[CLIENT_TO_MANAGER]
    if len(manager) < 5 or len(client) < 6:
        raise RuntimeError(f"Capture {capture_dir.name} does not contain enough handshake chunks")

    manager_frame4 = manager[3]
    manager_frame5 = manager[4]
    client_response4 = client[3]
    client_response5 = client[4]
    client_response6 = client[5]
    manager_frame4_fields = header_fields(manager_frame4)

    block67 = bytes.fromhex(hex_slice(manager_frame5, 67, 83))
    block88 = bytes.fromhex(hex_slice(manager_frame5, 88, 104))
    client_response6_body = strip_tail(client_response6)

    sequence4 = None
    if len(manager_frame4_fields) >= 3 and manager_frame4_fields[2].isdigit():
        sequence4 = int(manager_frame4_fields[2])
    frame5_sequence = uint16_le_at(manager_frame5, 19)

    return {
        "name": capture_dir.name,
        "path": str(capture_dir),
        "chunk_count": {
            MANAGER_TO_CLIENT: len(manager),
            CLIENT_TO_MANAGER: len(client),
        },
        "byte_count": {
            MANAGER_TO_CLIENT: sum(len(payload) for payload in manager),
            CLIENT_TO_MANAGER: sum(len(payload) for payload in client),
        },
        "manager_frame4": {
            "byte_count": len(manager_frame4),
            "header_fields": manager_frame4_fields,
            "guid": manager_frame4_fields[1].lower() if len(manager_frame4_fields) >= 2 else "",
            "sequence": sequence4,
        },
        "client_response4": {
            "byte_count": len(client_response4),
            "ack_guid": client_ack_guid(client_response4),
        },
        "client_response5": {
            "byte_count": len(client_response5),
            "text": decode_text_frame(client_response5),
        },
        "manager_frame5": {
            "byte_count": len(manager_frame5),
            "head_hex": manager_frame5[:64].hex(),
            "uuid_le_at_2": uuid_le_at(manager_frame5, 2),
            "sequence_le_at_19": frame5_sequence,
            "sequence_relation_to_frame4": (
                "frame4_sequence_plus_1" if sequence4 is not None and frame5_sequence == sequence4 + 1 else ""
            ),
            "block67_hex": block67.hex(),
            "block88_hex": block88.hex(),
        },
        "client_response6": {
            "byte_count": len(client_response6),
            "head_hex": client_response6[:64].hex(),
            "block30_hex": hex_slice(client_response6, 30, 46),
            "block51_hex": hex_slice(client_response6, 51, 67),
            "manager_block67_positions": find_positions(client_response6_body, block67),
            "manager_block88_positions": find_positions(client_response6_body, block88),
        },
    }


def compare_against_baseline(baseline: Path, other: Path) -> dict[str, Any]:
    baseline_chunks = read_chunks(baseline)
    other_chunks = read_chunks(other)
    comparisons: list[dict[str, Any]] = []
    for direction, chunk_index in [
        (MANAGER_TO_CLIENT, 5),
        (MANAGER_TO_CLIENT, 6),
        (MANAGER_TO_CLIENT, 7),
        (CLIENT_TO_MANAGER, 6),
    ]:
        baseline_payloads = baseline_chunks[direction]
        other_payloads = other_chunks[direction]
        if len(baseline_payloads) < chunk_index or len(other_payloads) < chunk_index:
            continue
        left = baseline_payloads[chunk_index - 1]
        right = other_payloads[chunk_index - 1]
        ranges = diff_ranges(strip_tail(left), strip_tail(right))
        comparisons.append(
            {
                "direction": direction,
                "chunk_index": chunk_index,
                "baseline_byte_count": len(left),
                "other_byte_count": len(right),
                "diff_ranges": ranges,
                "diff_range_count": len(ranges),
            }
        )
    return {
        "baseline": baseline.name,
        "other": other.name,
        "chunks": comparisons,
    }


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


def write_report(output_dir: Path, summaries: list[dict[str, Any]], comparisons: list[dict[str, Any]]) -> Path:
    report_path = output_dir / "compare_report.md"
    rows = [
        [
            item["name"],
            item["manager_frame4"]["sequence"],
            item["manager_frame4"]["guid"],
            item["client_response4"]["ack_guid"],
            item["manager_frame5"]["uuid_le_at_2"],
            item["manager_frame5"]["sequence_le_at_19"],
            item["manager_frame5"]["sequence_relation_to_frame4"],
            item["manager_frame5"]["block67_hex"],
            item["manager_frame5"]["block88_hex"],
            item["client_response6"]["manager_block67_positions"],
            item["client_response6"]["manager_block88_positions"],
        ]
        for item in summaries
    ]

    lines: list[str] = []
    lines.append("# Protocol Capture Comparison")
    lines.append("")
    lines.append(f"- Generated at: `{utc_now()}`")
    lines.append(f"- Capture count: `{len(summaries)}`")
    lines.append("")
    lines.append("## Frame 5 Session Fields")
    lines.append("")
    lines.append(
        markdown_table(
            rows,
            [
                "capture",
                "frame4_seq",
                "frame4_guid",
                "client_ack_guid",
                "frame5_uuid_le_at_2",
                "frame5_seq_le_at_19",
                "seq_relation",
                "frame5_block67",
                "frame5_block88",
                "client6_block67_pos",
                "client6_block88_pos",
            ],
        )
    )
    lines.append("")
    lines.append("## Baseline Diff Ranges")
    lines.append("")
    for comparison in comparisons:
        lines.append(f"### `{comparison['baseline']}` vs `{comparison['other']}`")
        diff_rows = [
            [
                chunk["direction"],
                chunk["chunk_index"],
                chunk["baseline_byte_count"],
                chunk["other_byte_count"],
                chunk["diff_ranges"],
            ]
            for chunk in comparison["chunks"]
        ]
        lines.append(markdown_table(diff_rows, ["direction", "chunk", "baseline bytes", "other bytes", "ranges"]))
        lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture_dirs", nargs="*", help="Capture directories or names under runtime/protocol-research/captures.")
    parser.add_argument("--latest", type=int, help="Compare the latest N capture directories.")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_script()
    if args.latest is not None:
        capture_dirs = latest_capture_dirs(repo_root, args.latest)
    else:
        if len(args.capture_dirs) < 2:
            raise ValueError("Pass at least two capture directories or use --latest N")
        capture_dirs = [resolve_capture_dir(value, repo_root) for value in args.capture_dirs]

    output_dir = args.output_dir
    if output_dir is None:
        output_dir = repo_root / "runtime" / "protocol-research" / "comparisons" / timestamp_name()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    summaries = [summarize_capture(capture_dir) for capture_dir in capture_dirs]
    comparisons = [compare_against_baseline(capture_dirs[0], capture_dir) for capture_dir in capture_dirs[1:]]

    result = {
        "schema": "protocol-capture-comparison.v1",
        "generated_at": utc_now(),
        "output_dir": str(output_dir),
        "baseline": capture_dirs[0].name,
        "capture_count": len(capture_dirs),
        "captures": summaries,
        "comparisons": comparisons,
        "frame5_uuid_counter": Counter(item["manager_frame5"]["uuid_le_at_2"] for item in summaries),
        "frame5_block67_counter": Counter(item["manager_frame5"]["block67_hex"] for item in summaries),
        "frame5_block88_counter": Counter(item["manager_frame5"]["block88_hex"] for item in summaries),
    }
    (output_dir / "compare_summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    report_path = write_report(output_dir, summaries, comparisons)
    result["report_path"] = str(report_path)

    if args.json:
        print(json.dumps({"output_dir": str(output_dir), "report_path": str(report_path)}, ensure_ascii=False, indent=2))
    else:
        print(f"output_dir={output_dir}")
        print(f"report={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
