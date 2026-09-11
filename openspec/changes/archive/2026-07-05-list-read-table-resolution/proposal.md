## Why

`read_list_grid` and `read_list_column` currently report dynamic-list results as if every list form exposes table `Список`. Tester feedback against `Справочник.Валюты` showed a non-empty form whose descriptor exposes table `Валюты`, while the list tools returned empty data with a misleading "genuinely empty" reason.

## What Changes

- Resolve the target dynamic-list table for `read_list_grid` and `read_list_column` from the live form descriptor instead of assuming `Список`.
- Add an optional `table` argument to both tools so callers can explicitly select the table when a form has multiple tables.
- Retarget the list replay table path as well as the nav-link and column names.
- Return structured, honest diagnostics for unresolved, ambiguous or mismatched table selection; do not claim a refreshed list is genuinely empty unless the tool read the resolved table.
- Add focused offline tests for single-table descriptor resolution, explicit table selection, legacy `Список` forms and diagnostic failure modes. Live Windows/TestClient proof remains a verification row, not a hard local Linux precondition.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-tool-endpoint-contract`: list-reading MCP tools must resolve and report the actual dynamic-list table before interpreting an empty row set as a genuinely empty list.

## Impact

- Touches Python manager/MCP provider code in `src/qa_mcp/mcp_server.py` and `src/qa_mcp/protocol/native_write.py`.
- Adds offline pytest coverage in `tests/test_form_descriptor.py` or adjacent focused tests.
- Does not change 1C metadata, runtime lab configuration, capture corpora or provider setup.
- Requires live 1C/TestClient evidence for final product acceptance on Windows/DemoSSL, but the local implementation can be verified with offline unit tests and OpenSpec validation.
