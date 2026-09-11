## Why

The current manager fixture V1 cleanup run joined all 17 read-only command
windows, but nine rows remain non-accepted. Before adding probes or changing
manifest markers, the project needs a reviewed row-by-row classification of
what blocks each pending row.

## What Changes

- Classify the nine pending rows from
  `20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`.
- Compare each row's expected marker, observed marker, endpoint, frame range,
  normalized hash and current replay/probe state.
- Publish compact classification evidence under
  `docs/protocol-research/evidence/manager-fixture-v1-pending-readonly/`.
- Keep all rows non-accepted unless later replay/direct-probe proof satisfies
  the current accepted gate.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: manager fixture V1 pending rows must be classified
  before promotion or manifest correction.

## Impact

- Touches protocol research evidence and possibly reporting helpers under
  `tools/protocol-research/`.
- Uses retained cleanup capture and reviewed evidence; no new live 1C runtime
  is required for classification.
- Does not change 1C BSL source, metadata, MCP provider setup or runtime lab
  configuration.
