## Why

The client fixture V2 surface needs a published target map so downstream safe
action work can identify the new local markers, allowed families and reset
hook without guessing or reading raw runtime payloads.

## What Changes

- Publish reviewed safe-action target rows for the V2 client fixture surface.
- Link each target row to its allowed family, expected local markers, reset
  hook and compact evidence path.
- Keep excluded controls and mutation families out of the safe-action manifest
  and evidence index.
- Make the fixture V2 target map discoverable for later capture and runner
  work.

## Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: V2 fixture target-map and evidence publication now
  describe the safe-action surface explicitly.

## Impact

- Protocol research docs and evidence index entries.
- OpenSpec requirements for the fixture target map.
- No live fixture execution is required for the docs-only publication step.
