#!/usr/bin/env python3
"""Summarize focused V2 safe-action proof decisions."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SUMMARY_SCHEMA = "qa-mcp.manager-fixture-v2-safe-action.proof-summary.v1"
DECISION_SCHEMA = "qa-mcp.manager-fixture-v2-safe-action.proof-decision.v1"
RAW_OUTPUT_POLICY = (
    "raw replay/probe payloads, generated request series, platform logs and "
    "full TCP captures stay under ignored runtime/protocol-research paths"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
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


def has_action_frame(row: dict[str, Any]) -> bool:
    return bool(row.get("action_frame_range"))


def has_hash(row: dict[str, Any]) -> bool:
    return bool(row.get("normalized_hash"))


def has_recovery(row: dict[str, Any]) -> bool:
    recovery = row.get("recovery_result")
    if not isinstance(recovery, dict):
        return False
    return str(recovery.get("status") or "").startswith("known_state")


def has_action_markers(row: dict[str, Any]) -> bool:
    return bool(row.get("action_result_markers"))


def route_decision(row: dict[str, Any]) -> dict[str, Any]:
    prerequisites = {
        "action_frame_range": has_action_frame(row),
        "normalized_hash": has_hash(row),
        "recovery_evidence": has_recovery(row),
        "action_result_markers": has_action_markers(row),
    }
    route_status = {
        "replay": "infeasible",
        "direct_python_manager_probe": "infeasible",
        "typed_contract": "insufficient",
    }
    route_reasons = {
        "replay": (
            "existing replay_probe tooling is read-only/bootstrap-oriented and does not "
            "safely replay manifest-gated V2 UI actions with recovery"
        ),
        "direct_python_manager_probe": (
            "current direct Python manager probes cover read-only context/marker queries, "
            "not same-action V2 switch/focus semantics"
        ),
        "typed_contract": (
            "phase markers and runner results prove live candidate execution, but do not "
            "prove that the isolated wire shape independently reproduces the same action"
        ),
    }
    missing: list[str] = []
    if not all(prerequisites.values()):
        missing.extend(name for name, ok in prerequisites.items() if not ok)
    missing.append("accepted_replay_probe_or_typed_contract_proof")

    status = "candidate"
    accepted = False
    replay_status = row.get("replay_status") or "pending"
    if replay_status == "accepted" and row.get("acceptance_evidence"):
        status = "accepted"
        accepted = True
        missing = []
        route_status = {
            "replay": "accepted",
            "direct_python_manager_probe": "not_needed",
            "typed_contract": "not_needed",
        }

    return {
        "schema": DECISION_SCHEMA,
        "case_id": row.get("case_id"),
        "action_id": row.get("action_id"),
        "target_id": row.get("target_id"),
        "target_marker": row.get("target_marker"),
        "allowed_action_family": row.get("allowed_action_family"),
        "status": status,
        "accepted_protocol_mapping": accepted,
        "candidate_reason": None if accepted else "replay_or_probe_or_typed_contract_unavailable",
        "proof_routes": route_status,
        "proof_route_reasons": route_reasons if not accepted else {},
        "proof_prerequisites": prerequisites,
        "missing_for_acceptance": missing,
        "action_frame_range": row.get("action_frame_range"),
        "background_frame_ranges": row.get("background_frame_ranges", []),
        "recovery_frame_range": row.get("recovery_frame_range"),
        "request_size": row.get("request_size", 0),
        "response_size": row.get("response_size", 0),
        "dynamic_field_count": len(row.get("dynamic_fields") or []),
        "normalized_hash": row.get("normalized_hash"),
        "pre_normalization_hash": row.get("pre_normalization_hash"),
        "action_result_markers": row.get("action_result_markers", []),
        "recovery_result": row.get("recovery_result"),
        "non_accepted_reasons": sorted(
            set((row.get("non_accepted_reasons") or []) + ([] if accepted else ["missing_safe_action_acceptance_proof"]))
        ),
    }


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


def write_markdown(path: Path, summary: dict[str, Any], decisions: list[dict[str, Any]]) -> None:
    table = [
        [
            row["case_id"],
            row["status"],
            row["proof_routes"],
            row["normalized_hash"],
            row["request_size"],
            row["response_size"],
            row["missing_for_acceptance"],
        ]
        for row in decisions
    ]
    lines = [
        "# Focused V2 Safe-Action Proof Summary",
        "",
        f"- Generated at: `{summary['generated_at']}`",
        f"- Source corpus: `{summary['source_corpus_cases']}`",
        f"- Decision counts: `{json.dumps(summary['decision_counts'], ensure_ascii=False)}`",
        f"- Raw output policy: {RAW_OUTPUT_POLICY}",
        "",
        markdown_table(
            table,
            [
                "case",
                "decision",
                "routes",
                "normalized hash",
                "request bytes",
                "response bytes",
                "missing for acceptance",
            ],
        ),
        "",
        "## Decision",
        "",
        "No focused V2 safe-action row is promoted to accepted status in this proof pass.",
        "The live capture and frame isolation are retained as candidate evidence; replay, direct Python-manager probe and typed contract proof are not available for same-action V2 semantics yet.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def generate(corpus_cases: Path, output_dir: Path) -> dict[str, Any]:
    repo_root = repo_root_from_script()
    rows = read_jsonl(corpus_cases)
    decisions = [route_decision(row) for row in rows]
    decision_counts = {
        status: sum(1 for row in decisions if row["status"] == status)
        for status in sorted({row["status"] for row in decisions})
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "schema": SUMMARY_SCHEMA,
        "generated_at": utc_now(),
        "source_corpus_cases": repo_relative_path(corpus_cases, repo_root),
        "row_count": len(decisions),
        "decision_counts": decision_counts,
        "accepted_count": decision_counts.get("accepted", 0),
        "candidate_count": decision_counts.get("candidate", 0),
        "raw_output_policy": RAW_OUTPUT_POLICY,
        "output_files": {
            "proof_summary_json": repo_relative_path(output_dir / "proof_summary.json", repo_root),
            "proof_summary_markdown": repo_relative_path(output_dir / "proof_summary.md", repo_root),
            "proof_decisions": repo_relative_path(output_dir / "proof_decisions.jsonl", repo_root),
        },
    }
    write_json(output_dir / "proof_summary.json", summary | {"decisions": decisions})
    write_jsonl(output_dir / "proof_decisions.jsonl", decisions)
    write_markdown(output_dir / "proof_summary.md", summary, decisions)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-cases", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = generate(args.corpus_cases.resolve(), args.output_dir.resolve())
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"status=ok")
        print(f"proof_summary={summary['output_files']['proof_summary_markdown']}")
        print(f"decision_counts={summary['decision_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
