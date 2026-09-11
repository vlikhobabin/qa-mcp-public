from __future__ import annotations

import json
import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools" / "protocol-research"
sys.path.insert(0, str(TOOLS_DIR))

from v2_safe_action_proof_summary import generate  # noqa: E402


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_proof_summary_keeps_isolated_safe_action_candidate_without_proof(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus_cases.jsonl"
    output_dir = tmp_path / "proof"
    write_jsonl(
        corpus,
        [
            {
                "case_id": "safe-focus-existing-edit-string",
                "action_id": "safe-focus-existing-edit-string",
                "target_id": "tm-v2-edit-string",
                "target_marker": "PF_EDIT_STRING",
                "allowed_action_family": "focus_existing_element",
                "action_frame_range": {"manager_to_client": {"from": 1, "to": 2}},
                "background_frame_ranges": [],
                "recovery_frame_range": {"manager_to_client": {"from": 3, "to": 3}},
                "request_size": 10,
                "response_size": 12,
                "dynamic_fields": [{"name": "binary_frame_dynamic_bytes"}],
                "normalized_hash": "a" * 64,
                "pre_normalization_hash": "b" * 64,
                "action_result_markers": ["PF_EDIT_STRING", "PF_EDIT_STRING_VALUE"],
                "recovery_result": {"status": "known_state_restored"},
                "non_accepted_reasons": ["replay_or_probe_unavailable"],
                "accepted_protocol_mapping": False,
                "replay_status": "pending",
            }
        ],
    )

    summary = generate(corpus, output_dir)

    assert summary["decision_counts"] == {"candidate": 1}
    [decision] = [
        json.loads(line)
        for line in (output_dir / "proof_decisions.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert decision["status"] == "candidate"
    assert decision["accepted_protocol_mapping"] is False
    assert decision["proof_prerequisites"] == {
        "action_frame_range": True,
        "normalized_hash": True,
        "recovery_evidence": True,
        "action_result_markers": True,
    }
    assert "missing_safe_action_acceptance_proof" in decision["non_accepted_reasons"]
