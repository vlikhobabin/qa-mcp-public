from __future__ import annotations

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools" / "protocol-research"
sys.path.insert(0, str(TOOLS_DIR))

from coverage_report import (  # noqa: E402
    DEFAULT_CASE_MAP,
    DEFAULT_INVENTORY,
    build_coverage,
    classify_mapping,
    load_json,
    render_markdown,
)


def synthetic_inventory() -> dict:
    return {
        "source": {"platform_version": "8.3.27.1786"},
        "objects": [
            {
                "english_name": "TestedApplication",
                "members": [
                    {"english_name": "GetActiveWindow", "kind": "method", "safety_class": "read_only"},
                    {"english_name": "Connect", "kind": "method", "safety_class": "agent_runtime"},
                ],
            },
            {
                "english_name": "TestedForm",
                "members": [
                    {"english_name": "FindObject", "kind": "method", "safety_class": "read_only"},
                ],
            },
        ],
    }


def synthetic_case_map() -> dict:
    return {
        "inventory": "synthetic",
        "updated_at": "2026-06-10",
        "mappings": [
            {
                "api": "TestedApplication.GetActiveWindow",
                "case_ids": ["active-window-context"],
                "proof_status": "accepted",
                "mapping_confidence": "seed",
            },
            {
                "api": "TestedForm.FindObject",
                "case_ids": ["tm-v1-diag-form-find-field-marker"],
                "proof_status": "accepted",
                "mapping_confidence": "reviewed",
            },
        ],
    }


def test_classify_mapping_buckets() -> None:
    assert (
        classify_mapping({"proof_status": "accepted", "mapping_confidence": "reviewed"})
        == "accepted_reviewed"
    )
    assert (
        classify_mapping(
            {"proof_status": "accepted_side_channel", "mapping_confidence": "seed"}
        )
        == "accepted_seed"
    )
    assert (
        classify_mapping({"proof_status": "candidate", "mapping_confidence": "reviewed"})
        == "candidate"
    )


def test_build_coverage_counts_and_unmatched() -> None:
    result = build_coverage(synthetic_inventory(), synthetic_case_map())
    assert result["total_members"] == 3
    assert result["bucket_counts"] == {
        "accepted_reviewed": 1,
        "accepted_seed": 1,
        "candidate": 0,
        "uncovered": 1,
    }
    assert result["unmatched_mappings"] == []

    bad_map = synthetic_case_map()
    bad_map["mappings"].append(
        {
            "api": "TestedForm.NoSuchMember",
            "case_ids": ["x"],
            "proof_status": "accepted",
            "mapping_confidence": "seed",
        }
    )
    result = build_coverage(synthetic_inventory(), bad_map)
    assert result["unmatched_mappings"] == ["TestedForm.NoSuchMember"]


def test_render_markdown_contains_summary_rows() -> None:
    inventory = synthetic_inventory()
    case_map = synthetic_case_map()
    result = build_coverage(inventory, case_map)
    markdown = render_markdown(result, inventory, case_map)
    assert "# Protocol Corpus API Coverage Report" in markdown
    assert "| `accepted_reviewed` | 1 | 33.3% |" in markdown
    assert "| `TestedApplication` | 2 |" in markdown
    assert "`active-window-context`" in markdown


def test_repository_case_map_matches_inventory() -> None:
    inventory = load_json(DEFAULT_INVENTORY)
    case_map = load_json(DEFAULT_CASE_MAP)
    result = build_coverage(inventory, case_map)
    assert result["unmatched_mappings"] == []
    assert result["total_members"] > 0
