## Context

`mcp_server.py` registers ~62 tools whose docstrings double as the MCP `tools/list` descriptions FastMCP returns
to every connecting agent. Those docstrings accreted during a long protocol-research effort and carry 185 internal
R&D references (card numbers, `Vanessa`/`vanessa-mcp`, `evidence/` paths). Unlike `protocol/` comments (dropped
from the image by the card-122 Nuitka compile) and `docs/`/`openspec/`/`evidence/` (never shipped), these
docstrings are emitted at runtime in normal product use — the single most exposed research leak. This change is a
documentation rewrite of the shipped tool surface; it is offline and changes no behavior.

## Goals / Non-Goals

**Goals:**
- Every `tools/list` description is product-facing with zero `card \d` / `vanessa` / `evidence` tokens.
- Each description still accurately tells an agent what the tool does and how to use its arguments.
- A durable offline regression test pins the zero-token contract so it cannot silently regress.

**Non-Goals:**
- No behavior, argument, or return-shape change (tool count stays 62).
- No edits to `protocol/` comments, `docs/`, `openspec/`, `evidence/`, the board, or non-docstring logic — the dev
  research corpus stays complete.
- Not hiding comments from the image (that is the sibling change `compile-shipped-nonprotocol-modules`).

## Decisions

- **Rewrite in source, not at build time.** Tool descriptions are the genuine product surface and must read well
  in dev too, so they are cleaned in `mcp_server.py` directly — this is the one part of cards 121/122/123 that is
  an intentional in-repo source edit. (Alternative considered: a build-time docstring strip — rejected because it
  would leave the dev product surface unclean and would blank, not improve, the descriptions.)
- **Relocate, don't delete, useful card trace.** Where a card number documents *why* a tool works a certain way and
  is useful for maintenance, move it to a `#` comment directly above the function. `#` comments never reach
  `tools/list` and are dropped from the image by the sibling compile change, so dev keeps the trace and the product
  stays clean.
- **Gate with an offline token-scan test.** Add a test that enumerates the registered tools (or scans the
  `@mcp.tool` docstrings) and asserts zero case-insensitive `card \d` / `vanessa` / `evidence` matches across all
  descriptions. This is the acceptance gate and runs without a live server. An MCP-client `tools/list` read is the
  equivalent runtime confirmation but is not required for the gating test.

## Risks / Trade-offs

- [A reworded description loses functional guidance an agent relied on] → Preserve every parameter/return note while
  rewording; the rewrite is description-only and the offline suite (which exercises the tools) must stay green.
- [A future tool reintroduces a card/vanessa/evidence token] → The token-scan test fails the build, so regressions
  are caught mechanically rather than by review.
- [Token scan over-matches a legitimate product word] → The tokens are specific (`card` + digits, `vanessa`,
  `evidence/`); none are expected in clean product copy, and any genuine collision is fixed by rewording.

## Migration Plan

Pure documentation change; no runtime migration. Rollback = revert the `mcp_server.py` docstring edits and the test.
