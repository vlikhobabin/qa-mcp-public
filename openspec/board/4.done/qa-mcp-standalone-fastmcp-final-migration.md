# QA MCP standalone FastMCP final migration

## Status
4.done

## Summary
Migrate qa-mcp from SDK-bundled FastMCP to standalone FastMCP 3.4.2 while
preserving its 68-tool public MCP surface, UTF-8 HTTP body gate, stdio startup
and offline regression behavior.

## Change
- `qa-mcp-standalone-fastmcp-final-migration`

## Scope
- `pyproject.toml`
- `uv.lock`
- `src/qa_mcp/mcp_server.py`
- `tests/test_mcp_server.py`
- `tests/test_clean_tool_surface.py`
- retained schema evidence under `.runtime/changerail/evidence/qa-mcp-fastmcp-final-migration/`

## Verify
- PASS: before snapshot captured `68` tools at `.runtime/changerail/evidence/qa-mcp-fastmcp-final-migration/before-tool-surface.json`.
- PASS: `uv lock` -> `fastmcp==3.4.2`, `fastmcp-slim==3.4.2`, `mcp==1.28.0`.
- PASS: after snapshot comparison retained at `.runtime/changerail/evidence/qa-mcp-fastmcp-final-migration/tool-surface-comparison.json` -> no added, removed or changed tools/schemas.
- PASS: `uv run pytest -q tests/test_mcp_server.py tests/test_delivery_config.py tests/test_clean_tool_surface.py` -> 115 passed.
- PASS: `uv run pytest -q tests/test_mcp_server_live.py` -> 1 passed.
- PASS: `uv run pytest -q -m 'not live and not integration and not slow and not capture'` -> 852 passed, 1 deselected.
- PASS: `openspec validate --all --strict` -> 17 passed before archive.
- PASS: `git diff --check`.

## Result
- Archived at `openspec/changes/archive/2026-07-30-qa-mcp-standalone-fastmcp-final-migration/`.
