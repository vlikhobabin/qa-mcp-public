## Why

The focused subset needs live phase-aware evidence before action-frame review
or accepted/candidate status decisions can be made. This change captures only
the reviewed rows and keeps raw runtime output out of reviewed git.

## What Changes

- Run the Windows-native `manager-fixture-v2-safe-action` scenario for the
  focused subset produced by `select-focused-v2-safe-action-subset`.
- Retain pre-read, action-start, action-end, post-read and recovery or
  recovery-read events for each attempted row.
- Keep raw captures, process logs and generated replay payloads under ignored
  runtime paths.
- Publish compact capture summaries and failure reasons for the downstream
  frame isolation change.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: The first focused V2 safe-action proof has a live
  capture step that records phase events for reviewed rows only.

## Impact

- Windows capture wrapper and existing manager V2 runner paths may be exercised.
- Runtime output under `runtime/protocol-research/captures/<run-id>/` remains
  ignored.
- Requires live 1C runtime and the manager/client fixture infobases; Vanessa MCP
  or EDT/meta snapshots are not required unless the implementation uses them for
  supplementary readiness checks.
