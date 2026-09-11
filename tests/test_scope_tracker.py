from __future__ import annotations

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools" / "protocol-research"
sys.path.insert(0, str(TOOLS_DIR))

from scope_tracker import (  # noqa: E402
    DEFAULT_CASE_MAP,
    DEFAULT_INVENTORY,
    DEFAULT_MUTATION_EVIDENCE,
    build_tracker,
    render_markdown,
)


def synthetic_inventory() -> dict:
    return {
        "source": {"platform_version": "8.3.27.1786"},
        "objects": [
            {
                "english_name": "TestedFormButton",
                "members": [
                    {"english_name": "Click", "kind": "method", "safety_class": "mutation"},
                    {"english_name": "Activate", "kind": "method", "safety_class": "safe_ui_action"},
                ],
            },
            {
                "english_name": "TestedApplication",
                "members": [
                    {"english_name": "GetActiveWindow", "kind": "method", "safety_class": "read_only"},
                ],
            },
        ],
    }


def synthetic_case_map() -> dict:
    return {
        "inventory": "synthetic",
        "updated_at": "2026-06-11",
        "mappings": [
            {
                "api": "TestedApplication.GetActiveWindow",
                "case_ids": ["active-window-context"],
                "proof_status": "accepted",
                "mapping_confidence": "seed",
            }
        ],
    }


def synthetic_mutation_evidence() -> dict:
    return {
        "schema": "qa-mcp.mutation-evidence-map.v1",
        "updated_at": "2026-06-11",
        "members": [
            {
                "api": "TestedFormButton.Click",
                "bucket": "candidate",
                "evidence_path": "docs/.../protocol-capture/",
            }
        ],
    }


def test_build_tracker_merges_mutation_evidence() -> None:
    result, unmatched = build_tracker(
        synthetic_inventory(), synthetic_case_map(), synthetic_mutation_evidence()
    )
    assert result["total_members"] == 3
    assert unmatched == []
    assert result["bucket_counts"] == {
        "accepted_reviewed": 0,
        "accepted_seed": 1,
        "candidate": 1,
        "uncovered": 1,
    }
    # mutation member is now a candidate, not uncovered
    assert result["coverage"]["TestedFormButton.Click"]["bucket"] == "candidate"


def test_build_tracker_fails_closed_on_unknown_member() -> None:
    bad = synthetic_mutation_evidence()
    bad["members"].append({"api": "TestedFormButton.NoSuchMember", "bucket": "candidate"})
    _result, unmatched = build_tracker(
        synthetic_inventory(), synthetic_case_map(), bad
    )
    assert unmatched == ["TestedFormButton.NoSuchMember"]


def test_render_markdown_has_full_member_table_and_totals() -> None:
    result, _ = build_tracker(
        synthetic_inventory(), synthetic_case_map(), synthetic_mutation_evidence()
    )
    markdown = render_markdown(result, synthetic_inventory(), synthetic_mutation_evidence())
    assert "# Protocol Corpus API Scope Tracker" in markdown
    assert "## All Members" in markdown
    # every member appears in the full table, including the still-uncovered one
    assert "`TestedFormButton.Click`" in markdown
    assert "`TestedFormButton.Activate`" in markdown
    assert "`TestedApplication.GetActiveWindow`" in markdown
    assert "**TOTAL**" in markdown


def test_repository_sources_match_inventory() -> None:
    from scope_tracker import load_json

    inventory = load_json(DEFAULT_INVENTORY)
    case_map = load_json(DEFAULT_CASE_MAP)
    mutation_evidence = load_json(DEFAULT_MUTATION_EVIDENCE)
    result, unmatched = build_tracker(inventory, case_map, mutation_evidence)
    assert unmatched == []
    assert result["total_members"] == 160
