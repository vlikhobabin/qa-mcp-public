## 1. Shared receive helper

- [x] 1.1 Add a shared frame-aware receive helper under `src/qa_mcp/protocol/`.
- [x] 1.2 Make the helper use `TAIL_MARKER` detection, monotonic deadlines and an idle fallback for tail-less buffers.
- [x] 1.3 Route `session.read_available` through the shared helper without changing its public signature.
- [x] 1.4 Route `native_mutation._read_available` through the shared helper and remove duplicate drain-loop logic.

## 2. Tests

- [x] 2.1 Add a fake-socket test where the second chunk arrives after the historical idle window and carries the tail marker.
- [x] 2.2 Add a fake-socket test for tail-less buffers proving idle fallback and hard deadline behavior.
- [x] 2.3 Assert an existing response parser can extract a value from the delayed-tail buffer.

## 3. Verification

- [x] 3.1 Run focused frame-aware receive tests.
- [x] 3.2 Run `uv run pytest -q`.
- [x] 3.3 Run `openspec validate frame-aware-receive --strict`.
- [x] 3.4 Run `git diff --check -- openspec/changes/frame-aware-receive src tests`.
- [x] 3.5 Run or record a runtime-gap diagnostic for a Linux live read pass (`read_form_descriptor` or `read_list_grid`) after the offline tests.

## 4. Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Protocol transport | `session.read_available`, `native_mutation._read_available`, shared receive helper | fake socket split response with tail in second chunk | `uv run pytest -q tests/test_protocol_session.py` (6 passed), `uv run pytest -q` (615 passed) | `tests/test_protocol_session.py` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Low: embedded-tail payload ambiguity remains theoretical until corpus evidence says otherwise |
| QA/TestClient live read | `read_form_descriptor` / `read_list_grid` on Linux `vanessa_client` | optional live read pass after offline tests | `uv run python -m qa_mcp.regression ...` GREEN 6/6; `ui.read_descriptor` element_count=46 and `ui.list_grid_after_dirty` row_count=5 | `.artifacts/openspec/frame-aware-receive/2026-07-02/live-read/20260702T062256Z/report.json` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Low: live read pass completed on Linux lab |
| Runtime cleanup | no new process ownership or launch behavior | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | receive-only change does not launch or stop 1C processes | No residual risk; cleanup behavior is unchanged |
