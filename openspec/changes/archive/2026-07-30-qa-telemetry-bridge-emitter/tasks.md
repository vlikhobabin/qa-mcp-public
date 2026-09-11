## 1. Emitter Core

- [x] 1.1 Add a qa-mcp telemetry bridge module that resolves trace context from
  proxy env/context file inputs and no-ops safely when context is absent.
- [x] 1.2 Normalize bridge observations through an allowlist with owner
  metadata, bounded evidence path/summary, status, subject and duration fields.
- [x] 1.3 Append observations through agent-core trace-store import with a CLI
  fallback and non-fatal error handling.

## 2. Runtime Wiring

- [x] 2.1 Emit scenario outcome observations from `run_scenario` and
  `run_step` results after existing result recording.
- [x] 2.2 Emit report observations from `write_test_report` without embedding
  report contents.
- [x] 2.3 Emit screenshot observations from `capture_screenshot` without
  embedding image bytes.
- [x] 2.4 Emit verification-summary observations for persistence and cleanup
  evidence that already carries retained artifact paths.

## 3. Tests And Evidence

- [x] 3.1 Add offline tests for context resolution, missing/invalid context
  no-op behavior, bounded observation payloads and mocked append calls.
- [x] 3.2 Add MCP-server wiring tests proving scenario/report/screenshot
  surfaces call the emitter while preserving normal tool results.
- [x] 3.3 Run focused pytest, `openspec validate qa-telemetry-bridge-emitter
  --strict`, `openspec validate --all --strict`, and `git diff --check`.
- [x] 3.4 Retain a real trace append smoke or record why live 1C/Windows-native
  runtime evidence is not required for this component change.

Evidence:
- RED: `uv run pytest -q tests/test_telemetry_bridge.py
  tests/test_mcp_server.py::test_record_result_emits_qa_bridge_observation
  tests/test_mcp_server.py::test_write_test_report_emits_qa_bridge_observation
  tests/test_mcp_server.py::test_capture_screenshot_emits_qa_bridge_observation`
  failed during collection because `qa_mcp.telemetry_bridge` did not exist.
- Focused GREEN: same command passed, `7 passed`.
- Broader focused suite: `uv run pytest -q tests/test_telemetry_bridge.py
  tests/test_mcp_server.py tests/test_reporting.py` passed, `125 passed`.
- Full offline suite: `uv run pytest -q` passed, `860 passed`.
- `openspec validate qa-telemetry-bridge-emitter --strict` passed.
- `openspec validate --all --strict` passed, `19 passed, 0 failed`.
- `git diff --check` passed.
- Real trace append smoke: trace
  `trc_2043f056ef0a42968f032b8f919d512f`, evidence event
  `evt_34da5dea618147bba78d2d439b4fb48f`, JSONL mirror
  `.ai/traces/trc_2043f056ef0a42968f032b8f919d512f/events.jsonl`.
