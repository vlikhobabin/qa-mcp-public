## Why

Bootstrap can auto-select a newer 1C platform family whose bundled capture slot
is empty, report a green deployment, and leave capture-backed tools to fail
later with opaque `capture-not-found` errors. This is now visible on hosts with
both 8.3.27 and 8.5.1 installed.

## What Changes

- Make Windows bootstrap platform discovery version-aware and prefer the newest
  platform family with direct bundled capture coverage when auto-selecting.
- Keep explicit `-PlatformExe` selection allowed, but emit a loud warning when
  that family has no direct capture bundle and name `-PlatformExe` as the escape
  hatch.
- Encode the epic-112 decision that 8.5 is supported through a validated 8.3
  protocol-data fallback until a real 8.5 protocol drift requires a populated
  `_bundled/8.5` corpus.
- Update delivery docs and tests so support claims, bootstrap behavior and
  Python capture resolution agree.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `qa-mcp-self-hosted-release`: bootstrap platform auto-selection and operator
  diagnostics must reflect capture coverage.
- `qa-mcp-protocol-lab`: runtime capture lookup must use the validated 8.5 to
  8.3 protocol-data fallback explicitly instead of failing later as missing
  capture data.

## Impact

- Touches `delivery/bootstrap.ps1`, delivery documentation, Python manager
  version/capture selection code, bundled-corpus documentation and focused
  tests.
- Does not require new protocol captures, Vanessa MCP, EDT/meta snapshots or
  1C metadata changes.
- Live Windows bootstrap evidence is outside this Linux workspace; offline
  tests prove selection/fallback behavior, and any release smoke must retain an
  8.5 read/tool transcript separately.
