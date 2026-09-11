# 87. General form introspection (form-analysis for any live form)

## Status
5.canceled

## Merged
- 2026-06-17 (board triage): folded into **card 98** (Product boundary) as **change 1** (general form
  introspection). The full plan below is preserved as working detail; card 98 is the active surface.

## Order Index
87

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-16: roadmap card 82, stage 5 — the READ counterpart to capture-free synthesis (86). qa-mcp's reads
  (`read_form_summary`/`read_element`/`read_form_value`) currently lean on capture templates; vanessa-mcp's
  `get_form_analysis` returns the full element tree + Gherkin for ANY form.

## Summary
Introspect ANY live form into a structured descriptor — element tree (names, types, captions, values, enabled/
readonly), plus a Gherkin-style state — capture-free. This descriptor also feeds the capture-free action
synthesis (86) with the element addressing it needs.

## Acceptance
- An MCP tool returns, for the active form of a connected client, the full element tree + values + a Gherkin
  state, for a form NOT covered by a bespoke capture, matching what Vanessa's `get_form_analysis` reports
  (spot-checked against the genuine manager as oracle).
- Output is consumable by the action synthesizer (86) for addressing elements by name/path.

## Change Set
- none yet

## Related
- card 86 (consumes this), card 79 (value read), `src/qa_mcp/protocol/responses.py`,
  `src/qa_mcp/scenario/runner.py` (read kinds). Oracle: the genuine manager `get_form_analysis` (card 81).

## Log
- 2026-06-16T00:00:00Z card created.
