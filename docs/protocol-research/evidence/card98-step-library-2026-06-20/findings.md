# Card 98 #3 — searchable Gherkin step library + vanessa-mcp compatibility note

**Date:** 2026-06-20. **Result:** SHIPPED (offline). A discoverable Gherkin step vocabulary (the
`search_for_steps`-equivalent, vanessa-mcp parity), a vanessa-mcp→qa-mcp coverage note, and a Vanessa-canonical
`.feature` that transpiles 100% — so an agent can author tests against qa-mcp instead of Vanessa.

## What shipped

- **`search_for_steps(keywords)` MCP tool (#40)** — returns the qa-mcp step library: each recognized step's
  canonical phrasing, example, native Step kind, category (read | action | navigation) and description, optionally
  keyword-filtered (multi-token AND, case-insensitive). Returns `{count, total, keywords, steps[]}`.
- **The library IS the matcher** — `STEP_PATTERNS` (the transpiler registry in `scenario/gherkin.py`) was enriched
  with `phrase` / `example` / `description` / `category`, and `step_library()` / `search_steps()` derive the
  vocabulary from it. So the library never drifts from what `transpile` / `run_scenario` actually execute — a unit
  test pins **every example to its declared kind** (no `unmapped`).
- **Compatibility note** — `docs/vanessa-mcp-parity.md`: the step vocabulary table + a vanessa-mcp tool→qa-mcp
  coverage matrix (✅ covered · 〜 partial · ❌ out-of-scope). Headlines: `get_form_analysis`→`read_form_descriptor`
  (card 98 #1), `search_for_steps_by_keywords`→`search_for_steps` (this card), `run_scenario`/`run_step`/screenshots
  /`activate_window` covered; gaps are test-results aggregation + window enumeration (change 2) and Vanessa-runtime
  internals / debugger / KB / role-matrix (out of scope capture-free).
- **Vanessa-style sample** — `tools/protocol-research/qa-vanessa-style.feature` (Vanessa-canonical phrasings:
  `я нажимаю на кнопку с именем …`, `в поле с именем … я ввожу текст …`, `я перехожу к закладке с именем …`,
  read + `результат содержит` assertion) **transpiles with 0 unmapped** (tested) and is runnable live via
  `run_scenario`.

## Coverage

The library exposes **12 step phrasings** (11 STEP_PATTERNS + the `результат содержит` assertion modifier) across
read / action / navigation. They are Vanessa-canonical, so most existing features transpile unchanged; the
transpiler never silently drops a step (unsupported lines surface in `transpile`'s `unmapped`). The 40 native MCP
tools remain the finer programmatic surface beneath the Gherkin layer.

## Artifacts

- Code: `src/qa_mcp/scenario/gherkin.py` (enriched `StepPattern` + `step_library` / `search_steps`),
  `src/qa_mcp/scenario/__init__.py` (exports), `src/qa_mcp/mcp_server.py` (`search_for_steps` tool). Tests:
  `tests/test_step_library.py` (+5: documented, no-drift, search filters, MCP tool, sample feature; 287 suite).
  Docs: `docs/vanessa-mcp-parity.md`. Sample: `tools/protocol-research/qa-vanessa-style.feature`.
