## Context

`mcp_server.py` is the MCP boundary, but it also contains raw socket protocol
work for foregrounding, field reads, descriptors, table cells and window lists.
That makes tool-wrapper changes risky and keeps protocol helpers hard to reuse.
CR-05 added the endpoint-aware tool decorator, so extraction must preserve the
wrapper layer and move only protocol mechanics.

## Goals / Non-Goals

**Goals:**

- Move raw protocol helpers from `mcp_server.py` into protocol-owned modules.
- Keep MCP tool functions as argument validation, decorator use, docstrings and
  result shaping.
- Preserve attached-endpoint behavior and structured errors for endpoint tools.
- Ensure `mcp_server.py` no longer imports `socket.create_connection` or
  `GuidRebinder` directly.

**Non-Goals:**

- Do not change tool names, arguments, descriptions, count or return shapes.
- Do not change foreground activation retry behavior.
- Do not introduce live runtime-only behavior during extraction.

## Decisions

- Create `protocol/introspection.py` for descriptor, field, table-cell and
  window-list read sweeps plus shared splice helpers.
- Create `protocol/foreground.py` for `_foreground_form_by_link` and bare-create
  foreground/open helpers.
- Keep MCP-facing value equivalence and label-location retry decisions reachable
  from wrappers, but move wire frame construction and socket loops out of the
  server module.
- Convert call sites by preserving function names at the wrapper boundary first,
  then cleaning private helper names once tests pass.

## Risks / Trade-offs

- Moving private helpers can break monkeypatch-based tests -> update tests to
  patch the new protocol module owners when they are testing wire behavior.
- The MCP server may still need small protocol data transformations -> allow
  import of pure data/result helpers, but keep socket and frame-rebinder imports
  out of `mcp_server.py`.
- Tool count can drift accidentally -> run the existing protected image/tool
  surface checks and registry tests.

## Migration Plan

1. Add protocol modules and move helper functions without behavior changes.
2. Replace server-private calls with protocol module calls.
3. Run focused MCP registry/endpoint tests and full pytest.
4. Confirm `rg 'create_connection|GuidRebinder' src/qa_mcp/mcp_server.py`
   returns no matches.
5. Rollback is module-scoped by moving helpers back and restoring imports.

## Open Questions

- none
