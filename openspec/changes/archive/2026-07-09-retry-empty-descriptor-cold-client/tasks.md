## 1. Cold-client descriptor retry

- [x] 1.1 `config.py`: `descriptor_warmup_attempts` (3) + `descriptor_warmup_delay_sec` (1.5)
      settings, env consts (`QA_MCP_DESCRIPTOR_WARMUP_ATTEMPTS` / `QA_MCP_DESCRIPTOR_WARMUP_DELAY_SEC`), `from_env` wiring
- [x] 1.2 `mcp_server.py`: `_descriptor_is_empty` helper (no `opened` AND 0 elements)
- [x] 1.3 `mcp_server.py`: bounded retry loop in `_resolve_list_table_for_read`; warm-up-aware
      `list-table-unresolved` diagnostic (`descriptor_empty`, `warmup_attempts`) + `descriptor_warmup_retries` on success

## 2. Verify

- [x] 2.1 Offline tests: retry-then-succeed (asserts `descriptor_warmup_retries`) and
      exhaust-then-report (asserts `descriptor_empty` + `warmup_attempts` + no infinite retry)
- [x] 2.2 `uv run pytest` green (798)
- [x] 2.3 `openspec validate <change> --strict`
- [ ] 2.4 Live cold-client re-verify on .201 — deferred (needs image rebuild to compile the
      change into the protected `.so` + hitting the cold window); offline-proven, low-risk
