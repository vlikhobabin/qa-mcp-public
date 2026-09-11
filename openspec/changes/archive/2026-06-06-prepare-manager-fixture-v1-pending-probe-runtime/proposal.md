## Why

The previous pending-row review could not run five focused probes because no
fresh live TestClient endpoint was available. Before any pending row can be
promoted, the protocol lab needs a repeatable Windows-native runtime route
that starts or attaches a clean fixture TestClient endpoint, records endpoint
identity, and fails closed with a compact provider/runtime gap when startup is
not available.

## What Changes

- Add or document a focused pending-row probe runtime entrypoint for manager
  fixture V1 read-only cleanup work.
- Preserve endpoint readiness evidence before replay or direct probes run.
- Record provider/runtime gaps when no clean TestClient endpoint can be used.
- Keep owned-process cleanup explicit for TestClient, proxy and manager PIDs.

## Capabilities

### New Capabilities
- `qa-mcp-protocol-lab`: pending-row probe runtime preparation for manager
  fixture V1 read-only rows.

### Modified Capabilities
- none

## Impact

- May touch `tools/protocol-research/run_protocol_capture.ps1`,
  `tools/protocol-research/replay_probe.py`,
  `tools/protocol-research/manager_fixture_marker_probe.py`, and compact
  evidence documentation.
- Requires Windows-native 1C runtime when live endpoint proof is available.
- Does not accept or reject any protocol mapping by itself.
