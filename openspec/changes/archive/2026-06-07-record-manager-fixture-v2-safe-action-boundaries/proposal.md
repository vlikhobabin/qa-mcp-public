## Why

Safe-action captures need reviewed phase boundaries so action frames can be
separated from bootstrap, background refresh and cleanup traffic. The manager
runner must write side-channel events precise enough for the existing V2
reporter and comparison tools.

## What Changes

- Emit `pre_read`, `action_start`, `action_end`, `post_read`, `recovery` and
  background phase events for each V2 safe-action row.
- Record action id, target id, action family, result markers and chunk/frame
  counters in `case_events.jsonl`.
- Keep action frame candidates separate from surrounding refresh or cleanup
  ranges.
- Preserve non-accepted statuses when boundaries are missing or ambiguous.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: Manager fixture V2 safe-action runs produce
  phase-aware side-channel events for candidate frame isolation.

## Impact

- Manager harness event output and protocol capture integration.
- V2 reporter input under ignored runtime paths.
- Requires live Windows-native capture evidence during implementation.
