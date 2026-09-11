## 1. Python Refresh Diagnostics

- [x] 1.1 Preserve structured `DisplayBackendError` details from
  `_force_list_refresh` instead of reducing every failure to generic
  reachability text.
- [x] 1.2 Preserve clean-state sweep display-backend failure details in list poll
  metadata without making list reads raise solely because the sweep failed.
- [x] 1.3 Update zero-row list diagnostics so `foreground-denied` and other
  host-agent primitive causes are named separately from unreachable or
  unconfigured display backends.
- [x] 1.4 Keep existing `refresh_method`, `refresh_note`, poll outcome, row-count,
  and table-resolution result compatibility for callers.

## 2. Tests And Evidence

- [x] 2.1 Add focused Python tests for `foreground-denied` propagation from list
  refresh metadata to zero-row diagnostics.
- [x] 2.2 Add focused Python tests that host-agent unreachable/configuration
  errors still keep install or configuration guidance.
- [x] 2.3 Add focused Python tests that refresh/sweep failures remain structured
  MCP results rather than raw exceptions.
- [x] 2.4 Run the 1C verification matrix checker in preflight mode and retain
  output under `.artifacts/openspec/read-list-refresh-diagnostics/20260706T140652Z/`.
- [x] 2.5 Run the focused Python test module(s) changed by this work.
- [x] 2.6 Record the Windows E2E transcript for non-foreground
  `read_list_grid` returning rows when an operator-owned Windows desktop is
  available, or record the runtime gap in the retained evidence summary.
- [x] 2.7 Run the 1C verification matrix checker in archive-gate mode.
- [x] 2.8 Run `openspec validate read-list-refresh-diagnostics --strict`.
- [x] 2.9 Run `git diff --check`.

## 3. OpenSpec Handoff

- [x] 3.1 Sync the `qa-mcp-tool-endpoint-contract` requirement delta into the
  main spec before archive.
- [x] 3.2 Archive `read-list-refresh-diagnostics` after tasks, verification, and
  spec sync are complete.
