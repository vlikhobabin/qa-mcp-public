# 83. Wire the commit-capable value-write into the runner + MCP

## Status
4.done

## Order Index
83

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-16: roadmap card 82, stage 1. card 80 produced `qa_mcp.protocol.native_write` (write_form_value /
  NativeWriteSession / derive_write_template) — a COMMIT-capable value-write — but it is standalone; the
  scenario runner's `input_text` still uses the OLD non-committing path (`actions.render_select_row_command`).

## Summary
Connect the proven Fork-2 write into the product surface so a scenario step actually COMMITS a value (and
verifies it), via the MCP `run_scenario`/`run_step` tools — not just standalone probes.

## Acceptance
- The `input_text` scenario kind (or a new `write_form_value` kind) routes to `native_write` and the value
  COMMITS (read-back shows it), driven through `qa_mcp.mcp_server` — no Vanessa.
- A Gherkin step (e.g. «в поле 'X' я ввожу 'Y'» + a read-back assert) runs green end-to-end via the MCP.
- `NativeWriteSession` (open-once / write-many) is the execution model for multiple writes in one scenario.
- `derive_write_template` is reused so the write needs only a per-FIELD-TYPE INPUT capture, not per value.
- Tests: extend `tests/test_native_write.py` + a scenario/runner test for the write kind.

## Change Plan
1. ✅ MCP surface — add `write_form_value` + `write_form_values` tools to `qa_mcp.mcp_server` (commit-capable
   value-write via `derive_write_template` + `NativeWriteSession`). DONE.
2. ✅ Scenario-engine routing — `qa_mcp.scenario.runner.run_write_scenario` executes a WRITE scenario on a
   single `NativeWriteSession` (open-once), routing each `input_text` step to `session.write(new_value)` (field
   from `step.marker`) and verifying by read-back. Exposed as MCP tool `run_write_scenario_tool` (feature_text /
   scenario_json). Session-model reconciliation resolved by BRANCHING: a pure-write scenario runs on the
   full-capture-replay NativeWriteSession (not the read-only synthesized bootstrap); non-write steps are reported
   unsupported (mixed read+write deferred to card 86). DONE.
3. ✅ Tests — 4 runner tests for the write path (`test_write_scenario_*` in tests/test_scenario_runner.py):
   routing input_text→write, open-once multi-write, read-back assertion, uncommitted→error, non-write→unsupported.
   Plus the 9 native_write unit tests. Full suite: 173 passed. DONE.

## Progress (2026-06-16)
- **DONE (step 1):** `write_form_value` / `write_form_values` MCP tools added; server registers 5 tools
  (run_scenario, run_step, transpile, write_form_value, write_form_values). LIVE smoke through the actual MCP
  tool `write_form_values(['MCPWRITE_001','MX','THIRTEEN_CHRS'])` on a fresh TestClient: **all_committed=true**
  (each read-back matches) — multi-write via NativeWriteSession, variable length, no Vanessa. Smoke runner
  `tools/protocol-research/run_mcp_write_smoke.sh`.
- **DONE (steps 2-3):** scenario-engine routing landed — `run_write_scenario` runs a Gherkin/JSON WRITE
  scenario on one NativeWriteSession; MCP tool `run_write_scenario_tool` exposes it (server now registers 6
  tools). LIVE Gherkin E2E through the MCP tool — feature «в поле с именем 'PF_EDIT_STRING' я ввожу текст …»
  ×3 (`GHERKIN_W01`/`SECOND_VAL`/`LAST`) on a fresh TestClient: **status=passed, all 3 committed=True** (read-back
  matches), no Vanessa. Smoke runner `tools/protocol-research/run_gherkin_write_smoke.sh`. 4 new runner tests;
  full suite 173 passed. All acceptance criteria met.

## Change Set
- `src/qa_mcp/mcp_server.py` (+3 tools), `src/qa_mcp/scenario/runner.py` (+`run_write_scenario`),
  `src/qa_mcp/scenario/__init__.py` (export), `tests/test_scenario_runner.py` (+4 write tests),
  `tools/protocol-research/run_mcp_write_smoke.sh`, `tools/protocol-research/run_gherkin_write_smoke.sh`.

## Related
- card 80 (Fork-2 write), `src/qa_mcp/protocol/native_write.py`, `src/qa_mcp/scenario/{runner,actions}.py`,
  `src/qa_mcp/mcp_server.py`.

## Log
- 2026-06-16T00:00:00Z card created.
- 2026-06-16: moved to 3.inprogress. Step 1 DONE — commit-capable write wired into the MCP
  (`write_form_value`/`write_form_values`); live smoke through the MCP tool committed 3/3. Steps 2-3
  (scenario-engine routing + runner test) remain.
- 2026-06-16: steps 2-3 DONE → moved to 4.done. `run_write_scenario` + `run_write_scenario_tool` route
  `input_text` through NativeWriteSession in the runner; live Gherkin E2E committed 3/3 (status=passed);
  4 new runner tests, full suite 173 passed.
