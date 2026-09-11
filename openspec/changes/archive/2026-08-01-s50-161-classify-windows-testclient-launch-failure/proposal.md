## Why

The S50 disposable Windows reruns collapse two different failures into one
`testclient-launch-start-failed` response: a shell-broker/PID handoff failure
and a 1C process that starts but exits before exposing its TPort. That ambiguity
blocks safe diagnosis and causes a full listener timeout after the acknowledged
process has already disappeared.

## What Changes

- Preserve the shell-broker acknowledgement as bounded launch evidence and
  distinguish an invalid/unopenable PID handoff from a 1C process that has
  already exited before TPort readiness.
- Resolve a live requested-TPort owner as the authoritative lifecycle PID when
  the shell acknowledgement names a transient launcher process.
- Return a fail-loud early-exit classification with bounded PID/exit evidence
  instead of reporting a broker start failure or waiting through an unrelated
  listener timeout.
- Add regression tests and a Windows-native proof against the authorized
  `HISTORICAL-LAB-HOST` station without exposing credentials, raw command lines, or
  unrelated process inventory.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: make broker/PID ownership and platform
  early-exit failure classes explicit and secret-safe.
- `qa-mcp-tool-endpoint-contract`: preserve the existing early-exit contract
  when the broker acknowledgement PID disappears before a handle is opened.

## Impact

- Windows host-agent TestClient launcher and focused Go tests.
- Bounded launch metadata returned through the existing Python remote-client
  path; no new endpoint or caller-provided executable surface.
- Requires live Windows 1C runtime on `User@192.0.2.200`; no Vanessa MCP,
  EDT/meta snapshot, protocol-capture change, or customer infobase mutation.
