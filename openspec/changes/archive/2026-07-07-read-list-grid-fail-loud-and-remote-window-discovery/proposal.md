## Why

`read_list_grid` can currently return a normal-looking `row_count: 0` when the
display refresh or clean-state sweep failed in remote-client mode. That is a
P0 correctness bug: callers can treat fabricated emptiness as real data even
though the live Windows 1C form contains visible rows.

## What Changes

- Make dynamic-list reads fail loud when refresh, clean-state sweep, or
  target-window discovery fails and the replay returns no rows.
- Surface top-level `ok: false`, `data_confidence: "unknown"`, and the
  underlying structured refresh/window error for uncertain zero-row list reads.
- Add a remote-client window discovery diagnostic that reports the searched
  target plus discovered Windows-side 1C windows with handle, class, title and
  PID.
- Add an authenticated host-agent visible-list-cell diagnostic path so qa-mcp
  can retain UIA/desktop fallback evidence when protocol grid reads cannot prove
  the intended live window was read.
- Preserve normal all-in-one/Linux Xvfb list reads and confirmed refreshed-empty
  results.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `qa-mcp-tool-endpoint-contract`: list-read endpoints must fail loud for
  uncertain zero-row results and attach the remote window/UI-visible diagnostics.
- `qa-mcp-windows-host-agent-security`: the authenticated host-agent display
  surface must expose bounded 1C window discovery and visible-cell diagnostics
  without weakening its token/origin boundary.

## Impact

- Touches Python manager/MCP code in `src/qa_mcp/mcp_server.py` and
  `src/qa_mcp/protocol/display_backend.py`.
- Touches Windows host-agent Go code under `host-agent/windows-display-agent/`.
- Adds focused Python and Go tests.
- Updates OpenSpec specs and the board card.
- Does not change raw TestClient protocol captures, 1C metadata, Vanessa MCP,
  EDT/meta snapshots, runtime lab configuration, or business-data mutation
  behavior.
- Verification is offline unit coverage plus retained runtime-gap evidence for
  the Windows [redacted third-party configuration] UIA smoke when no operator-owned Windows desktop is
  available from this Linux workspace.
