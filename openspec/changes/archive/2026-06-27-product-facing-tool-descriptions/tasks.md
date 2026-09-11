## 1. Measure the current leak

- [x] 1.1 Scan `src/qa_mcp/mcp_server.py` tool docstrings for `card \d` / `vanessa` / `evidence` (case-insensitive); record the baseline match count and the affected tools.

## 2. Add the zero-token gate (test-first)

- [x] 2.1 Add an offline test (e.g. `tests/test_clean_tool_surface.py`) that enumerates the registered qa-mcp tools (or scans the `@mcp.tool` docstrings) and asserts zero case-insensitive `card \d` / `vanessa` / `evidence` matches across all descriptions.
- [x] 2.2 Confirm the test FAILS against the current (un-rewritten) docstrings, proving it actually gates the contract.

## 3. Rewrite the tool docstrings product-facing

- [x] 3.1 Rewrite every `@mcp.tool()` docstring in `mcp_server.py` to product-facing text: state what the tool does and how to use its arguments, with zero `card`/`vanessa`/`evidence` tokens, preserving parameter docs, argument names and return-shape notes.
- [x] 3.2 Relocate any maintenance-useful card-trace context to a `#` comment directly above the function (dev-only; never in the docstring).
- [x] 3.3 Spot-read a sample of rewritten descriptions to confirm functional accuracy is preserved (an agent could still call the tool correctly from the description alone).

## 4. Verify

- [x] 4.1 Run the zero-token test — it now PASSES (zero matches across all tool descriptions).
- [x] 4.2 Run the offline suite (`pytest`) — green; tool count unchanged at 62.
- [x] 4.3 (Optional runtime confirmation) Connect an MCP client, read `tools/list`, and confirm no description carries an internal R&D token.
- [x] 4.4 Confirm the dev research corpus is untouched: `protocol/` comments, `docs/`, `openspec/`, `evidence/`, board and git history are unchanged.
