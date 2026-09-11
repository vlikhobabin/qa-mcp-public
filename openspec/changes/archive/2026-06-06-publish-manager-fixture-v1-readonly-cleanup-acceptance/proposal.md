## Why

After pending rows are classified and probed, the project needs one reviewed
manager fixture V1 cleanup state that states which read-only rows are accepted
and whether V2 safe-action planning is unblocked.

## What Changes

- Regenerate the cleanup live-join report with all retained replay/probe
  summaries folded in.
- Publish coherent accepted and pending counts for the 17 joined read-only
  rows.
- Update protocol research docs and evidence index with classification,
  replay/probe and final report paths.
- Preserve raw traffic and replay output under ignored runtime directories.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: manager fixture V1 cleanup acceptance must be
  republished after pending-row classification and probes before V2 triage.

## Impact

- Touches `tools/protocol-research/report_manager_fixture_v1.py` or related
  runner/report docs if needed.
- Updates compact reviewed evidence under `docs/protocol-research/`.
- Consumes retained runtime capture output; does not change 1C BSL source.
