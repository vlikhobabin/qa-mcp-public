## 1. Replay Engine

- [x] 1.1 Add `src/qa_mcp/protocol/replay.py` with `ReplaySession` and `ReplayOp`.
- [x] 1.2 Route setup replay, operation replay and response observation through the shared engine.
- [x] 1.3 Ensure the engine calls `read_protocol_available` and does not introduce a separate idle-gap receive loop.

## 2. Operation Migration

- [x] 2.1 Convert native write and read-back operations to the shared engine while preserving result dictionaries.
- [x] 2.2 Convert list, dialog and window replay operations to the shared engine.
- [x] 2.3 Keep `WriteRetargetError`, `_retarget_failed_result`, `_write_value_matches_readback`, `ProtocolSendTimeout` and `send_timeout` behavior intact.

## 3. Verification

- [x] 3.1 Add or update focused offline tests for converted replay operations and failure verdicts.
- [x] 3.2 Run `uv run pytest -q`.
- [x] 3.3 Run `rg "socket\\.create_connection|GuidRebinder\\.from_client_chunks|read_protocol_available" src/qa_mcp/protocol/native_write.py src/qa_mcp/protocol/replay.py` and confirm connection/rebinder setup lives in `replay.py` and receive uses `read_protocol_available`.
- [x] 3.4 Live-regression was not run because this delivery used the offline-required gate; retained offline evidence under `.artifacts/openspec/native-write-replay-session/20260702-offline/`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient protocol runtime | native write/list/dialog/window replay engine | Offline pytest plus source check; optional unchanged live-regression when a client is available | source_preflight, scenario_log, qa_testclient_bundle when live client is available | `.artifacts/openspec/native-write-replay-session/20260702-offline/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| BSL and 1C metadata | N/A - Python protocol manager refactor only | No BSL modules, metadata objects, roles, reports or migrations are changed | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change does not edit 1C configuration source or live infobase data. | Runtime behavior is covered by protocol tests and optional live-regression, not BSL diagnostics. |
