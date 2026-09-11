## Why

Host-agent TestClient launch readiness currently accepts an instantaneous state:
the process is alive and the requested TPort is listening at one probe moment.
The real .205 launch failure binds the TPort briefly and exits seconds later,
so readiness must prove short-term persistence before returning `ready`.

## What Changes

- Add a bounded persistence dwell to the host-agent TestClient readiness
  classifier after the first alive-plus-listening observation.
- Re-check both process liveness and TPort listening after the dwell before
  returning `readiness: "ready"`.
- Return structured failure (`testclient-exited-early` or
  `testclient-not-listening`) when the process exits or the port drops during
  the dwell.
- Keep launch waiting bounded by the existing `timeout_seconds` contract.
- Add offline Go coverage for a fake process that binds its TPort and then
  exits during the dwell; it must not be reported ready.
- Record live .205 confirmation as a qa-mcp provider/runtime gap in this
  delivery run rather than fabricating runtime evidence.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: host-agent TestClient launch readiness
  must survive a bounded dwell before success can be reported.
- `qa-mcp-tool-endpoint-contract`: remote `launch_test_client` readiness
  scenarios must treat host-agent dwell failures as launch failures and keep
  container-side TPort proof required after host readiness.

## Impact

- Touches Windows host-agent Go launch/readiness code under
  `host-agent/windows-display-agent/`.
- Adds focused offline Go tests for persistence-dwell readiness classification.
- Updates OpenSpec artifacts, main specs after sync, card status and delivery
  manifest.
- Does not change native TestClient protocol frames, replay templates, Python
  manager transport semantics, MCP provider setup or runtime lab configuration.
- Live Windows .205 confirmation requires the unavailable real host and remains
  a recorded provider gap for this run.
