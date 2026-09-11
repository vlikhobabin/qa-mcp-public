## 1. Table Resolution

- [x] 1.1 Add a table-resolution helper for list reads that consumes the live descriptor table list and returns either a selected table or a structured diagnostic.
- [x] 1.2 Add optional `table` parameters to `read_list_grid` and `read_list_column`.
- [x] 1.3 Thread the resolved table through result shaping and keep `available_tables` / `requested_table` in failure diagnostics.

## 2. Replay Retargeting

- [x] 2.1 Extend the list replay template/model to record the captured table name.
- [x] 2.2 Retarget the `Table[...]` segment in `read_list_column_replay`, `read_list_row_replay`, and `read_list_grid_replay`.
- [x] 2.3 Preserve default behavior for captures and forms whose table is `Список`.

## 3. Diagnostics And State Hygiene

- [x] 3.1 Prevent `list-table-unresolved`, `list-table-not-found`, and `list-table-ambiguous` cases from running a wrong-table replay.
- [x] 3.2 Ensure zero-row reasons only say "genuinely empty" after a table was resolved and a refreshed replay actually read that table.
- [x] 3.3 Account for descriptor-open state by using the existing clean-state sweep or by reporting the no-refresh/cold-boundary uncertainty.

## 4. Tests And Verification

- [x] 4.1 Add offline tests for a single descriptor table named `Валюты`, explicit table selection, legacy `Список`, missing table and ambiguous table diagnostics.
- [x] 4.2 Add protocol retarget tests proving `Table[Список]` can be retargeted to a Cyrillic table while columns still retarget correctly.
- [x] 4.3 Run focused pytest for the affected tests.
- [x] 4.4 Run `openspec validate list-read-table-resolution --strict`.
- [x] 4.5 Run the matrix checker in preflight and archive-gate modes, retaining output under `.artifacts/openspec/list-read-table-resolution/<run-id>/`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation tool surface | `read_list_grid` / `read_list_column` table resolution and replay retargeting | Focused offline pytest plus optional Windows/DemoSSL smoke for `Справочник.Валюты` | pytest output, matrix checker output, optional QA/TestClient smoke summary | `.artifacts/openspec/list-read-table-resolution/20260705T1913Z/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | 1C metadata/runtime data | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | Python-only MCP tool behavior change; no 1C metadata or data mutation is performed. | Live Windows smoke remains the final product proof for the tester scenario. |
