## Why

Before scaling to the full manager fixture V1 command catalog, the lab needs a
small non-dry-run proof that the custom manager harness can generate live
traffic, side-channel events, join evidence and at least one normalized corpus
row.

## What Changes

- Run a bounded live smoke with two or three read-only manager fixture V1
  commands.
- Publish compact reviewed evidence for runtime output, frame/chunk join,
  corpus rows, unresolved gaps and replay/probe attempts.
- Keep raw traffic, logs and generated runtime files under ignored runtime
  paths.
- Record provider/runtime gaps instead of claiming live evidence when the EPF
  or runtime profile is unavailable.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require a bounded live manager fixture V1 smoke
  before expanding the read-only corpus to the full command catalog.

## Impact

- Produces reviewed protocol evidence and documentation.
- Requires the previous harness, catalog, capture and join changes.
- Requires live Windows 1C runtime when not provider-gapped.
- Does not accept safe actions, mutations or full-catalog coverage.
