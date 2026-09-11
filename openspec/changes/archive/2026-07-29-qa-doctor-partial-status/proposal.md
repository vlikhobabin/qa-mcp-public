## Why

The doctor currently has a single fail/partial status calculation, but optional
probe skips need to be visibly partial without implying installation failure.
Required failures must still set `ok=false`.

## What Changes

- Classify doctor checks as required or optional.
- Keep required probe failures as `ok=false` and `status=fail`.
- Allow optional unavailable probes, such as effective-user discovery, to yield
  `status=partial` with `ok=true` when all required probes pass.
- Cover auth-missing and optional-skipped behavior with offline tests.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-runtime-configuration`: doctor result semantics distinguish required
  failures from optional skipped probes.

## Impact

- Affects Python manager doctor status aggregation and tests.
- Does not require live 1C runtime, Vanessa MCP, EDT/meta snapshots, or protocol
  capture evidence.
