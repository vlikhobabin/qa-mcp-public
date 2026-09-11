## Why

`measure_scenario` can report `scenario_ok: true` even when the scenario failed because it treats the non-empty
`ScenarioResult.to_dict()` payload as truthy when no `ok` key is present. That creates a false green next to coverage
and APDEX data, which is unacceptable for a QA tool.

## What Changes

- Make `measure_scenario` derive `scenario_ok` from the scenario result contract: `status == "passed"`.
- Treat missing or malformed scenario result payloads as not passed instead of truthy.
- Add offline unit coverage for both failed and passed scenario result dictionaries by monkeypatching
  `mcp_server.run_scenario` and the debug/runtime dependencies.
- Keep the debug protocol parsing and coverage/perf report shape unchanged.

This change touches **Python manager code** and **offline tests** only. It does not require live 1C runtime, Vanessa MCP,
EDT/meta snapshots or protocol capture refresh.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `qa-mcp-protocol-lab`: `measure_scenario` must report the measured scenario verdict honestly from the scenario
  result status.

## Impact

- `src/qa_mcp/debug/measure.py` — scenario verdict derivation.
- `tests/test_measure.py` — offline regression coverage for failed and passed scenario verdicts.
- No MCP tool signature change; `src/qa_mcp/mcp_server.py::measure_scenario` continues to return the same keys.
