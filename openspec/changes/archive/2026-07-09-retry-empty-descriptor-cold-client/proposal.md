## Why

A heavy 1C configuration ([redacted third-party configuration] / Бухгалтерия 3.0) can return an **empty** live
form descriptor (`opened` falsy, 0 elements) on the FIRST `read_list_grid` right after the
TestClient launches — the managed form is not ready yet over the protocol. Today that surfaces
as `list-table-unresolved` ("the live form descriptor did not expose any Table elements"), a
confusing hard failure for what is really a cold-client warm-up race. Proven live on .201: the
same read succeeds (10 rows) once the client is warm. A genuinely empty catalog is different —
it still exposes a `Table` element with 0 rows — so an empty descriptor is unambiguously
"not rendered yet", safe to retry.

## What Changes

- `_resolve_list_table_for_read` (used by `read_list_grid` / `read_list_column`) retries the
  live descriptor read a bounded number of times while the descriptor is empty
  (`_descriptor_is_empty`: no `opened` AND no elements), with a short delay between attempts.
- New config knobs: `QA_MCP_DESCRIPTOR_WARMUP_ATTEMPTS` (default 3) and
  `QA_MCP_DESCRIPTOR_WARMUP_DELAY_SEC` (default 1.5).
- When every attempt still returns empty, the `list-table-unresolved` diagnostic now reports
  `descriptor_empty: true`, `warmup_attempts`, and a "client may still be warming up (heavy
  configuration)" reason; on success after a retry, `table_resolution.descriptor_warmup_retries`
  records how many warm-up retries were needed.

Out of scope: the empty descriptor was already confirmed NOT to be a regression (v0.2.4 behaves
the same cold, and worse warm — its F5 fails); this change is defensive cold-start hardening only.

## Impact

- Affected capability: `qa-mcp-tool-endpoint-contract`
- Affected code: `src/qa_mcp/config.py`, `src/qa_mcp/mcp_server.py`
- A cold-client first list read self-heals instead of failing; a genuinely empty list is
  untouched (it exposes a Table element, so it is never treated as "empty descriptor").
