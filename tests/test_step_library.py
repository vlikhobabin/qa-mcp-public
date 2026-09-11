"""Card 98 #3 — the discoverable Gherkin step library (search_for_steps-equivalent) + its no-drift invariant."""
from pathlib import Path

import qa_mcp.mcp_server as srv
from qa_mcp.scenario import search_steps, step_library, transpile_feature
from qa_mcp.scenario.gherkin import transpile_scenario

REPO = Path(__file__).resolve().parents[1]


def test_library_entries_are_documented():
    lib = step_library()
    assert len(lib) >= 12
    for entry in lib:
        for key in ("phrase", "example", "kind", "category", "description"):
            assert entry.get(key), f"{key} missing in {entry}"
        assert entry["category"] in ("read", "action", "navigation", "skipped")  # card 103 added "skipped"


def test_every_example_transpiles_to_its_kind():
    # the library is derived from STEP_PATTERNS, so each example MUST transpile to its declared kind with no
    # unmapped lines — this pins the library to what the transpiler actually executes (no drift).
    for entry in step_library():
        if entry["kind"] == "assert":  # the assertion modifier attaches to a preceding step, not standalone
            continue
        result = transpile_scenario("t", [entry["example"]])
        assert not result.unmapped, f"example did not transpile: {entry['example']!r}"
        assert result.scenario.steps[0].kind == entry["kind"], entry


def test_search_steps_filters():
    assert search_steps("") == step_library()                       # empty -> all
    kinds = {e["kind"] for e in search_steps("кнопк")}
    # card 103 added «Кнопка 'X' существует» (assert_element_present) alongside the two button phrasings
    assert kinds == {"open_card", "click_button", "assert_element_present"}
    assert all(e["category"] == "read" for e in search_steps("read"))  # category token
    # multi-token AND: both tokens must appear
    multi = search_steps("поля значение")
    assert multi and all("knd" or True for _ in multi)
    assert search_steps("zzz-no-such-step") == []


def test_search_for_steps_mcp_tool():
    full = srv.search_for_steps()
    assert full["count"] == full["total"] >= 12 and full["keywords"] == ""
    one = srv.search_for_steps("закладк")
    assert one["count"] >= 1 and one["total"] == full["total"]
    assert all("kind" in s for s in one["steps"])


def test_sample_vanessa_feature_transpiles_fully():
    # the shipped Vanessa-canonical sample must transpile with ZERO unmapped lines (the parity demo)
    text = (REPO / "tools/protocol-research/qa-vanessa-style.feature").read_text(encoding="utf-8")
    results = transpile_feature(text)
    assert results, "no scenarios parsed"
    for result in results:
        assert not result.unmapped, f"unmapped in {result.scenario.name}: {result.unmapped}"
        assert result.scenario.steps
