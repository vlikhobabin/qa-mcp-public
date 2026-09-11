## Why

The source-bound S50-120 Windows proof resolves the exact owned empty-title
window, but `/uia/visible_list_cells` returns no marker for either owned native
fixture. The reader or its execution boundary must expose the target's visible
descendants before the blocked lifecycle-window change can be verified.

## What Changes

- Add a Windows-native regression that proves the current UIA reader loses a
  visible marker beneath the exact process-owned empty-title target.
- Correct the narrow reader/execution or fixture contract so the marker is
  returned without caption, wildcard, generic 1C, or foreground fallback.
- Re-run the complete source-bound route, target-refusal, session-diagnostic,
  and exact-cleanup matrix and retain only sanitized ignored evidence.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: require authenticated visible-cell
  reads to observe accessible named descendants of the exact lifecycle/client
  target while retaining fail-closed targeting and desktop-session checks.

## Impact

The change affects the Go Windows display driver, focused Go tests, ignored
Windows proof fixtures/evidence, OpenSpec workflow, and possibly the host-agent
README if the durable reader contract needs clarification. It does not change
Python MCP behavior, native TestManager/TestClient protocol tooling, 1C source
or metadata, runtime lab configuration, or infobase/business data. Verification
uses the authorized Windows workstation and owned native fixtures; it does not
require Vanessa MCP, EDT/meta snapshots, a live 1C runtime, or protocol capture.
