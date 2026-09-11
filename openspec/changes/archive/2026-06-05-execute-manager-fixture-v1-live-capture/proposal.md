## Why

The `manager-fixture-v1-readonly` capture scenario exists, but its live branch
currently runs Vanessa MCP smoke probes instead of the custom manager harness.
The first industrial corpus run needs the capture runner to invoke the harness
and preserve proxy traffic, manager events and logs under one run id.

## What Changes

- Update `run_protocol_capture.ps1` so live
  `manager-fixture-v1-readonly` runs invoke the custom manager harness.
- Pass run id, proxy TestClient port, output directory and manifest path to the
  harness.
- Preserve Vanessa MCP probes only as optional bootstrap or fallback evidence.
- Fail closed when the required Vanessa EPF/runtime asset is missing, while
  recording a compact provider/runtime gap.
- Keep PID ownership and cleanup rules unchanged.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require manager fixture V1 live captures to run the
  custom manager harness through the TCP proxy and retain shared run evidence.

## Impact

- Touches Windows-native capture tooling.
- Requires live 1C runtime and the manager/client infobases for verification.
- Depends on the harness run loop and command catalog alignment changes.
- Does not classify protocol frames by itself.
