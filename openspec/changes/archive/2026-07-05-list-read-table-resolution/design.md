## Context

The list-reading tools use a full replay capture because dynamic lists need the interaction-ready state that a table-cell splice cannot produce. That replay currently retargets the nav-link and column names, but the MCP result is shaped with `table: "Список"` and the wire path still follows the captured table name.

Tester evidence showed `read_form_descriptor(open_link="e1cib/list/Справочник.Валюты", enumerate_live=true)` returns a single table named `Валюты`, while `read_table_cell(..., table="Валюты", column="Код")` can read the value. The bug is therefore in the list/grid table selection and its empty-list diagnosis, not in the display bridge or in the catalog data.

## Goals / Non-Goals

**Goals:**

- Resolve the dynamic-list table before list replay.
- Let callers pass `table` explicitly for multi-table or diagnostic cases.
- Retarget `Table[...]` in the list replay in addition to nav-link and column.
- Preserve existing behavior for list forms whose table is actually `Список`.
- Keep empty-list reasons honest and table-aware.

**Non-Goals:**

- No change to `read_table_cell` semantics.
- No new protocol capture or raw capture promotion.
- No 1C metadata, infobase mutation or runtime apply.
- No attempt to solve unrelated current-form GUID or host-agent UTF-8 cards.

## Decisions

1. Add a small table resolver in `mcp_server.py`.
   - Inputs: `open_link`, optional `table`, endpoint settings, descriptor capture/templates.
   - It calls the descriptor path for the same `open_link`, extracts `kind == "Table"` names, and returns either a selected table or a structured diagnostic.
   - Selection order: explicit `table`; one descriptor table; table matching the final metadata name from `open_link`; `Список` only when it is actually present; otherwise ambiguous.

2. Keep diagnostics fail-closed.
   - If explicit `table` is absent and multiple tables cannot be ranked, return `ok: false`, `error: "list-table-ambiguous"`.
   - If explicit `table` is not present, return `ok: false`, `error: "list-table-not-found"`.
   - If no table can be read from the descriptor, return `ok: false`, `error: "list-table-unresolved"`.
   - These results include `requested_table`, `available_tables`, `open_link`, and a `reason` that never says "genuinely empty".

3. Retarget the replay table segment in protocol code.
   - Extend `ReadListColumnTemplate` with the captured table name, defaulting to `Список`.
   - Extend `read_list_column_replay`, `read_list_row_replay`, and `read_list_grid_replay` with `table` or `target_table`.
   - Use the existing element-path retargeting helpers to replace the captured `Table[Список]` segment with `Table[<resolved>]` while preserving the column retarget.

4. Treat descriptor resolution as a state-changing UI read and clean up before replay.
   - Descriptor resolution opens the form on the running TestClient. Before the full replay read, run the existing clean-state sweep when a display backend is available and record the result in `list_refresh` or diagnostic metadata.
   - If no display backend is available, continue only when the replay still returns rows; otherwise report the existing no-refresh/cold-boundary uncertainty rather than upgrading the result to "genuinely empty".

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation tool surface | `read_list_grid` and `read_list_column` in `src/qa_mcp/mcp_server.py`; list replay retargeting in `src/qa_mcp/protocol/native_write.py` | Offline pytest with monkeypatched descriptor and replay paths; Windows/DemoSSL smoke command for `Справочник.Валюты` when available | pytest output, structured diagnostic assertions, optional QA/TestClient smoke summary | `.artifacts/openspec/list-read-table-resolution/20260705T1913Z/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | 1C metadata, infobase source import, deployment and data mutation | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | This change edits Python QA tool behavior only and does not change 1C configuration or runtime data. | Live Windows list-form proof can still uncover environment-specific UI timing issues. |

## Risks / Trade-offs

- Descriptor lookup before replay can dirty the open-window state. Mitigation: use the existing clean-state sweep and keep the diagnostic honest when no backend can sweep.
- Multi-table list forms may need a stronger "main table" heuristic later. Mitigation: fail closed with `list-table-ambiguous` unless the caller supplies `table`.
- Retargeting table names in full replay must preserve frame length handling for ASCII and UTF-16 names. Mitigation: reuse element retarget helpers and cover Cyrillic table names in unit tests.
