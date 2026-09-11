## Why

FastMCP sends every `mcp_server.py` tool **docstring** to every connecting agent on `tools/list`. Those docstrings
currently carry **185** internal R&D references (card numbers, `Vanessa`/`vanessa-mcp`, `evidence/` paths — 68
"Vanessa" alone), so the most research-revealing channel in the whole delivery is exposed in normal product use
with **zero** reverse-engineering. It is the least-protected leak and the cheapest to misuse. Cleaning the
descriptions is also simply better product UX. Compilation (the sibling change) does NOT hide runtime-exposed
docstrings, so this source rewrite is required on its own.

## What Changes

- Rewrite all `@mcp.tool()` docstrings in `src/qa_mcp/mcp_server.py` to be **product-facing**: each describes what
  the tool does for the user/agent, with **zero** `card N`, `Vanessa`/`vanessa-mcp`, or `evidence/` tokens.
- Relocate (do not delete) any maintenance-useful card-trace context to a `#` comment above the function — dev-only
  context that never reaches `tools/list`.
- Preserve each tool's parameter docs, argument names, return-shape notes and behavioral accuracy — this is a
  documentation rewrite, not a logic change. Tool count stays 62.
- Add an offline regression assertion that the shipped tool descriptions contain zero internal R&D tokens.

This touches **Python manager / MCP provider surface** only (tool docstrings). It is **offline** — no live 1C
runtime, Vanessa MCP, or EDT/meta snapshots are needed to verify it. It does not touch `protocol/` comments,
`docs/`, `openspec/`, `evidence/`, the board, or any non-docstring logic.

## Capabilities

### New Capabilities
- `qa-mcp-clean-tool-surface`: the shipped runtime tool-description surface is product-facing and free of internal
  R&D references (card numbers, Vanessa/vanessa-mcp, evidence paths), while preserving each tool's functional
  accuracy.

### Modified Capabilities
<!-- none: this introduces a contract on the tool-description surface; existing capabilities' requirements are unchanged. -->

## Impact

- Code: `src/qa_mcp/mcp_server.py` (tool docstrings + relocated `#` comments only); a new offline test asserting the
  zero-token contract over the registered tool descriptions.
- Behavior: none — same 62 tools, same arguments, same returns. Only the human/agent-readable descriptions change.
- Out of scope / preserved: `protocol/` comments, `docs/`, `openspec/`, `evidence/`, board, git history (dev
  research stays complete).
