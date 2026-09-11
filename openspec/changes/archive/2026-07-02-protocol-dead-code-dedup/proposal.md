## Why

After CR-03/CR-04, the remaining dead protocol helpers and duplicate utilities
increase refactor risk without providing runtime behavior. Removing only verified
dead code and collapsing exact duplicates keeps the architecture cleanup small
and reviewable after the functional slices have landed.

## What Changes

- Delete verified-dead symbols: `_CreateForegroundHold`, `_RESOLVE_SF_RE` and
  `_OPEN_LINK_LABEL_ALIASES`.
- Keep `_splice_window_activate_command`; it is live through the CR-03 label
  locate retry path.
- Remove or rename `mutation.py` only if implementation confirms
  `native_mutation` is not on a live import path; otherwise leave it intact and
  record the residual reason.
- Collapse exact duplicate helpers such as date normalization, GUID substitution,
  capture chunk loading or LEB128 decoding only when the shared replacement is
  behavior-identical and covered by tests.
- Keep this as Python manager/protocol cleanup only. It does not change MCP
  provider setup, OpenSpec workflow, runtime lab configuration or 1C metadata.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: protocol implementation contains only live helpers for
  supported protocol behavior and uses shared duplicate utilities where
  behavior is identical.

## Impact

- Affected code: `src/qa_mcp/mcp_server.py`, `src/qa_mcp/protocol/` and tests
  that import removed helpers.
- Affected tests: focused import/behavior tests, dead-symbol `rg` checks and
  full `uv run pytest -q`.
- Live 1C runtime is not required; this is verified by offline tests and source
  checks.
