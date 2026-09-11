## Why

The blocked S4-R1 continuation proved session-0 preflight but received no
session-1 preflight receipt from the exact limited interactive task. A bounded
investigation is required to distinguish task-token, snapshot/read,
metadata-set, and evidence-write boundaries before any real-configuration or
live-row retry can be considered.

## What Changes

- Define privacy-safe typed outcomes for the four preflight failure boundaries
  and for an exact disposable-file pass.
- Dynamically test the exact limited session-1 task token against only
  exact-owned disposable files, with a session-0 control and fail-closed
  cleanup evidence.
- Select session 0 as the least-authority owner of real-target snapshot and
  final metadata restoration; session 1 receives only exact-owned staged
  inputs and cannot read or restore the real configuration.
- Publish a documentation and OpenSpec investigation decision only. No 1C
  process, S3/S4/S5 row, S7 route, production code, provider setup, or runtime
  lab configuration is changed.

## Capabilities

### New Capabilities
- `qa-mcp-session1-metadata-restoration-authority`: Defines the typed,
  privacy-safe investigation boundary and the session-0-owned restoration
  handoff required before S4-R1 may seek another confirmation.

### Modified Capabilities
- none

## Impact

The reviewed payload is limited to OpenSpec workflow artifacts, a durable
protocol-research evidence summary, and the investigation card. Dynamic
evidence uses only `historical-user@192.0.2.201`, exact-owned disposable files, and
one exact limited interactive scheduled task. It requires neither live 1C nor
Vanessa MCP, EDT/meta snapshots, the real 1C configuration, or any public MCP
surface.
