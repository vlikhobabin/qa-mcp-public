## Why

Connection diagnostics should make a failing Windows/model-B setup easier to
understand, not start heavy Designer metadata dumps that can hang and leave an
extra `1cv8` process beside the real TestClient. The 2026-07-07 real-base
diagnostic run showed that an ad hoc `DESIGNER /DumpConfigToFiles` attempt timed
out and had to be cleaned up manually.

## What Changes

- Make the documented/implemented connection diagnostics contract explicit:
  ordinary qa-mcp diagnostics use health, descriptor, TestClient, and optional
  COM read-smoke routes, and do not invoke Designer metadata dumps.
- Harden host-agent platform command timeout diagnostics so any spawned 1C
  process PID is visible in timeout/cancel responses while the existing process
  group cleanup remains mandatory.
- Retain the existing fail-closed platform command policy for Designer/heavy
  operations: heavy 1C platform commands must go through `/platform/execute`
  with timeout, cleanup, redaction, mutation classification, and operator intent
  where required.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `qa-mcp-tool-endpoint-contract`: connection diagnostics must avoid Designer
  metadata dumps and prefer light-weight health/descriptor/COM routes.
- `qa-mcp-windows-host-agent-security`: platform command timeout responses must
  report spawned process identity while terminating the process group.

## Impact

- Touches Python manager diagnostics, Windows host-agent platform execution,
  tests, OpenSpec specs, and qa-mcp/host-agent documentation.
- Does not introduce a new protocol claim and does not require live 1C runtime
  capture/replay. Offline Python and Go tests are sufficient for the guarded
  behavior; a real Windows host smoke remains useful when an operator-owned
  Windows desktop is available.
