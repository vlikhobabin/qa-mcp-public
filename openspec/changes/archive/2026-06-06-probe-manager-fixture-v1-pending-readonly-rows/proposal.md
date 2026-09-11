## Why

The pending manager fixture V1 rows cannot be promoted from joined evidence
alone. Rows need replay or direct-probe proof that matches the current cleanup
run case id, frame range and normalized hash.

## What Changes

- Use the pending-row classification to choose replay/direct-probe strategy.
- Run or extend focused read-only probes for pending rows.
- Retain positive and negative proof summaries under compact reviewed evidence
  paths.
- Keep rows non-accepted when proof is absent, mismatched or belongs only to a
  different run.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: pending manager fixture V1 rows require current-run
  replay or direct-probe proof before accepted promotion.

## Impact

- May touch `tools/protocol-research/replay_probe.py`,
  `tools/protocol-research/manager_fixture_marker_probe.py`, reporter code and
  focused tests.
- Requires Windows-native live TestClient replay/probe runs for full evidence.
- Does not change 1C BSL source or accept action/mutation semantics.
