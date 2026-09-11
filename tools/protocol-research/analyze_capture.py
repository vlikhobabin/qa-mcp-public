#!/usr/bin/env python3
"""Analyze captured 1C TestManager/TestClient proxy traffic."""

from __future__ import annotations

import argparse
import base64
import json
import re
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


BOM_UTF8 = b"\xef\xbb\xbf"
TAIL_MARKER = b"fS\xb2\xa6"
GUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
ASCII_STRING_RE = re.compile(rb"[ -~]{4,}")
TEXT_DIRECTIONS = ("manager_to_client", "client_to_manager")


@dataclass(frozen=True)
class Chunk:
    ts: str
    connection_id: int
    direction: str
    chunk_no: int
    byte_count: int
    sha256: str
    aggregate_offset: int
    aggregate_path: Path
    payload: bytes


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def latest_capture_dir(repo_root: Path) -> Path:
    captures_dir = repo_root / "runtime" / "protocol-research" / "captures"
    candidates = [path for path in captures_dir.iterdir() if path.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"No capture directories found under {captures_dir}")
    return max(candidates, key=lambda path: path.name)


def read_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_traffic(capture_dir: Path) -> tuple[list[dict[str, Any]], list[Chunk]]:
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
            payload = payload_from_record(record)
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
                    payload=payload,
                )
            )
    return events, chunks


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


def text_body(payload: bytes) -> bytes:
    if payload.endswith(TAIL_MARKER):
        return payload[: -len(TAIL_MARKER)]
    return payload


def decoded_printable_ratio(text: str) -> float:
    if not text:
        return 1.0
    printable = 0
    for char in text:
        if char in "\r\n\t" or char.isprintable():
            printable += 1
    return printable / len(text)


def looks_like_utf16le(payload: bytes) -> bool:
    if len(payload) < 8:
        return False
    even_nuls = sum(1 for index in range(0, len(payload), 2) if payload[index] == 0)
    odd_nuls = sum(1 for index in range(1, len(payload), 2) if payload[index] == 0)
    half = max(1, len(payload) // 2)
    return even_nuls / half > 0.35 or odd_nuls / half > 0.35


def decode_text(payload: bytes) -> tuple[str | None, str | None]:
    body = text_body(payload)
    if body.startswith(BOM_UTF8):
        try:
            return body.decode("utf-8-sig"), "utf-8-sig"
        except UnicodeDecodeError:
            return None, None
    try:
        text = body.decode("utf-8")
        if decoded_printable_ratio(text) >= 0.85:
            return text, "utf-8"
    except UnicodeDecodeError:
        pass
    if not looks_like_utf16le(body):
        return None, None
    try:
        text = body.decode("utf-16-le")
        if decoded_printable_ratio(text) >= 0.85:
            return text, "utf-16-le"
        return None, None
    except UnicodeDecodeError:
        return None, None


def printable_ratio(payload: bytes) -> float:
    if not payload:
        return 1.0
    printable = 0
    for byte in payload:
        if byte in (9, 10, 13) or 32 <= byte <= 126 or byte >= 128:
            printable += 1
    return printable / len(payload)


def sanitize_excerpt(text: str | None, limit: int = 240) -> str:
    if not text:
        return ""
    one_line = text.replace("\r", "\\r").replace("\n", "\\n")
    if len(one_line) > limit:
        return one_line[:limit] + "..."
    return one_line


def ascii_strings(payload: bytes, limit: int = 8) -> list[str]:
    strings: list[str] = []
    for match in ASCII_STRING_RE.finditer(payload):
        value = match.group(0).decode("ascii", errors="replace")
        if value not in strings:
            strings.append(value)
        if len(strings) >= limit:
            break
    return strings


def binary_probe(payload: bytes) -> dict[str, Any]:
    body = text_body(payload)
    probe: dict[str, Any] = {
        "first_byte_hex": body[:1].hex(),
        "second_byte_hex": body[1:2].hex(),
    }
    if len(body) >= 18:
        probe["uuid_le_at_2"] = str(uuid.UUID(bytes_le=body[2:18]))
    if len(body) >= 21:
        probe["sequence_le_at_19"] = int.from_bytes(body[19:21], byteorder="little")

    uuid_windows: list[dict[str, Any]] = []
    scan_limit = min(64, max(0, len(body) - 15))
    for offset in range(scan_limit):
        candidate = uuid.UUID(bytes_le=body[offset : offset + 16])
        if candidate.version not in (1, 3, 4, 5):
            continue
        uuid_windows.append(
            {
                "offset": offset,
                "uuid": str(candidate),
                "version": candidate.version,
            }
        )
        if len(uuid_windows) >= 8:
            break
    if uuid_windows:
        probe["uuid_le_windows"] = uuid_windows
    if len(body) >= 104:
        probe["dynamic_block_67_hex"] = body[67:83].hex()
        probe["dynamic_block_88_hex"] = body[88:104].hex()
    elif len(body) >= 84:
        probe["dynamic_block_68_hex"] = body[68:84].hex()
    return probe


def parse_header_fields(text: str | None) -> list[str]:
    if not text:
        return []
    stripped = text.lstrip("\ufeff")
    if not stripped.startswith("{"):
        return []
    first_line = stripped.splitlines()[0]
    first_line = first_line.strip()
    if first_line.endswith("}"):
        first_line = first_line[:-1]
    if first_line.startswith("{"):
        first_line = first_line[1:]
    return [field.strip() for field in first_line.split(",") if field.strip()]


def classify_chunk(chunk: Chunk) -> dict[str, Any]:
    payload = chunk.payload
    text, encoding = decode_text(payload)
    header_fields = parse_header_fields(text)
    text_for_search = text or " ".join(ascii_strings(payload, limit=32))
    guids = GUID_RE.findall(text_for_search)

    if payload.startswith(BOM_UTF8):
        payload_class = "utf8-bom-text"
    elif text and decoded_printable_ratio(text) >= 0.85:
        payload_class = f"{encoding}-text"
    else:
        payload_class = "binary"

    record: dict[str, Any] = {
        "ts": chunk.ts,
        "connection_id": chunk.connection_id,
        "direction": chunk.direction,
        "chunk_no": chunk.chunk_no,
        "byte_count": chunk.byte_count,
        "sha256": chunk.sha256,
        "aggregate_offset": chunk.aggregate_offset,
        "class": payload_class,
        "starts_utf8_bom": payload.startswith(BOM_UTF8),
        "ends_tail_marker": payload.endswith(TAIL_MARKER),
        "tail_hex": payload[-8:].hex() if payload else "",
        "head_hex": payload[:32].hex(),
        "printable_ratio": round(printable_ratio(payload), 3),
        "encoding": encoding,
        "text_excerpt": sanitize_excerpt(text),
        "ascii_strings": ascii_strings(payload),
        "header_fields": header_fields,
        "guids": guids[:12],
    }

    if len(header_fields) >= 3:
        record["header_side"] = header_fields[0]
        record["header_message_id"] = header_fields[1]
        record["header_sequence_or_type"] = header_fields[2]
    if len(header_fields) >= 4:
        record["header_kind"] = header_fields[3]
    if payload_class == "binary":
        record["binary_probe"] = binary_probe(payload)
    return record


def write_frames(capture_dir: Path, frames: Iterable[dict[str, Any]]) -> Path:
    frames_path = capture_dir / "frames.jsonl"
    with frames_path.open("w", encoding="utf-8") as file_obj:
        for frame in frames:
            file_obj.write(json.dumps(frame, ensure_ascii=False) + "\n")
    return frames_path


def load_mcp_results(capture_dir: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in sorted(capture_dir.glob("mcp_*.json")):
        try:
            data = read_json_file(path)
        except Exception as exc:  # noqa: BLE001 - report partial analysis.
            results.append({"file": path.name, "error": repr(exc)})
            continue
        entry: dict[str, Any] = {"file": path.name}
        if isinstance(data, dict):
            entry["id"] = data.get("id")
            if "error" in data:
                entry["status"] = "error"
                entry["message"] = data["error"].get("message", "")
            else:
                entry["status"] = "ok"
                content = data.get("result", {}).get("content", [])
                if content and isinstance(content, list):
                    first = content[0]
                    if isinstance(first, dict):
                        entry["text_excerpt"] = sanitize_excerpt(first.get("text", ""), limit=180)
        results.append(entry)
    return results


def summarize_frames(frames: list[dict[str, Any]]) -> dict[str, Any]:
    by_direction = Counter(frame["direction"] for frame in frames)
    bytes_by_direction = Counter()
    class_counter = Counter()
    tail_counter = Counter()
    header_sides = Counter()
    header_kinds = Counter()
    sequence_values: dict[str, list[str]] = defaultdict(list)
    all_guids = Counter()

    for frame in frames:
        direction = frame["direction"]
        bytes_by_direction[direction] += int(frame["byte_count"])
        class_counter[frame["class"]] += 1
        tail_counter[str(frame["ends_tail_marker"]).lower()] += 1
        if "header_side" in frame:
            header_sides[f"{direction}:{frame['header_side']}"] += 1
        if "header_kind" in frame:
            header_kinds[f"{direction}:{frame['header_kind']}"] += 1
        if "header_sequence_or_type" in frame:
            values = sequence_values[direction]
            if len(values) < 20:
                values.append(frame["header_sequence_or_type"])
        for guid in frame.get("guids", []):
            all_guids[guid.lower()] += 1

    return {
        "chunk_count_by_direction": dict(by_direction),
        "bytes_by_direction": dict(bytes_by_direction),
        "class_counts": dict(class_counter),
        "tail_marker_counts": dict(tail_counter),
        "header_sides": dict(header_sides),
        "header_kinds": dict(header_kinds),
        "first_sequence_values": dict(sequence_values),
        "top_guids": all_guids.most_common(12),
    }


def markdown_table(rows: list[list[Any]], headers: list[str]) -> str:
    def cell(value: Any) -> str:
        text = str(value)
        return text.replace("|", "\\|").replace("\n", " ")

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell(value) for value in row) + " |")
    return "\n".join(lines)


def write_analysis_md(
    capture_dir: Path,
    events: list[dict[str, Any]],
    frames: list[dict[str, Any]],
    summary: dict[str, Any],
    mcp_results: list[dict[str, Any]],
    frames_path: Path,
) -> Path:
    analysis_path = capture_dir / "analysis.md"
    manifest = {}
    manifest_path = capture_dir / "capture_manifest.json"
    if manifest_path.exists():
        manifest = read_json_file(manifest_path)

    first_chunks = frames[:12]
    first_binary_manager_chunks = [
        frame
        for frame in frames
        if frame["direction"] == "manager_to_client" and frame["class"] == "binary"
    ][:8]
    first_rows = [
        [
            frame["chunk_no"],
            frame["direction"],
            frame["byte_count"],
            frame["class"],
            frame["starts_utf8_bom"],
            frame["ends_tail_marker"],
            frame.get("header_fields", [])[:4],
            frame["head_hex"],
            frame["text_excerpt"] or ", ".join(frame["ascii_strings"]),
        ]
        for frame in first_chunks
    ]

    event_rows = [
        [event.get("ts", ""), event.get("event", ""), event.get("connection_id", ""), event.get("direction", "")]
        for event in events
        if event.get("event") != "chunk"
    ][:20]

    mcp_rows = [
        [
            result.get("file", ""),
            result.get("status", ""),
            result.get("id", ""),
            result.get("text_excerpt", result.get("message", "")),
        ]
        for result in mcp_results
    ]

    binary_rows = [
        [
            frame["chunk_no"],
            frame["byte_count"],
            frame.get("binary_probe", {}).get("uuid_le_at_2", ""),
            frame.get("binary_probe", {}).get("sequence_le_at_19", ""),
            frame.get("binary_probe", {}).get("dynamic_block_67_hex", "")
            or frame.get("binary_probe", {}).get("dynamic_block_68_hex", ""),
            frame.get("binary_probe", {}).get("dynamic_block_88_hex", ""),
            frame["head_hex"],
        ]
        for frame in first_binary_manager_chunks
    ]

    lines: list[str] = []
    lines.append("# Protocol Capture Analysis")
    lines.append("")
    lines.append(f"- Generated at: `{utc_now()}`")
    lines.append(f"- Capture dir: `{capture_dir}`")
    lines.append(f"- Frames file: `{frames_path.name}`")
    if manifest:
        lines.append(f"- Scenario: `{manifest.get('scenario', 'unknown')}`")
        lines.append(f"- TestClient port: `{manifest.get('realTestClientPort', 'unknown')}`")
        lines.append(f"- Proxy port: `{manifest.get('proxyPort', 'unknown')}`")
        lines.append(f"- MCP port: `{manifest.get('mcpPort', 'unknown')}`")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(summary, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")

    lines.append("## Non-Chunk Events")
    lines.append("")
    lines.append(markdown_table(event_rows, ["ts", "event", "connection", "direction"]) if event_rows else "No non-chunk events found.")
    lines.append("")

    lines.append("## First Frames")
    lines.append("")
    lines.append(
        markdown_table(
            first_rows,
            ["chunk", "direction", "bytes", "class", "bom", "tail", "header", "head hex", "excerpt"],
        )
    )
    lines.append("")

    lines.append("## First Binary Manager Frames")
    lines.append("")
    lines.append(
        markdown_table(
            binary_rows,
            ["chunk", "bytes", "uuid_le_at_2", "seq_le_at_19", "block_67_or_68", "block_88", "head hex"],
        )
        if binary_rows
        else "No binary manager frames found."
    )
    lines.append("")

    lines.append("## MCP Results")
    lines.append("")
    lines.append(markdown_table(mcp_rows, ["file", "status", "id", "excerpt"]) if mcp_rows else "No MCP result files found.")
    lines.append("")

    lines.append("## Initial Protocol Hypotheses")
    lines.append("")
    lines.append("- Many text-like chunks start with UTF-8 BOM `EF BB BF` and end with marker `66 53 B2 A6`.")
    lines.append("- The first TestClient-to-manager chunk is a 5-byte preface before the text-like frame exchange.")
    lines.append("- Text-like chunks use a brace/comma structure rather than strict JSON; first-line header fields are captured in `header_fields`.")
    lines.append("- Later chunks can be binary even when they still end with the same tail marker.")
    lines.append("- Repeated GUIDs and sequence/header fields should be correlated across multiple captures before implementing replay.")
    lines.append("")

    analysis_path.write_text("\n".join(lines), encoding="utf-8")
    return analysis_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "capture_dir",
        nargs="?",
        type=Path,
        help="Capture directory. Defaults to latest runtime/protocol-research/captures/<timestamp>.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_script()
    capture_dir = args.capture_dir.resolve() if args.capture_dir else latest_capture_dir(repo_root)
    events, chunks = read_traffic(capture_dir)
    frames = [classify_chunk(chunk) for chunk in chunks]
    frames_path = write_frames(capture_dir, frames)
    summary = summarize_frames(frames)
    mcp_results = load_mcp_results(capture_dir)
    analysis_path = write_analysis_md(capture_dir, events, frames, summary, mcp_results, frames_path)

    result = {
        "capture_dir": str(capture_dir),
        "analysis_path": str(analysis_path),
        "frames_path": str(frames_path),
        "chunk_count": len(frames),
        "summary": summary,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"analysis={analysis_path}")
        print(f"frames={frames_path}")
        print(f"chunks={len(frames)}")
        print(f"bytes_by_direction={summary['bytes_by_direction']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
