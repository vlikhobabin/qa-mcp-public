## Why

The first OSS-04D-R4 design investigation preserved the correct concurrency,
provenance, output-bound and URL architecture but exhausted review because one
matrix detail—userinfo encoding depths and paired controls through both public
paths—was not carried consistently into its successor handoff. A clean linked
replacement is required; policy forbids another same-card edit or publication
of the exhausted payload.

## What Changes

- Retain exact R3/R4 exhausted lineage and recoverability without restoring
  either failed implementation/design payload wholesale.
- Re-materialize the accepted R4 invariants and seven-row matrix from the safe
  published baseline.
- Make credential-assignment and userinfo hostile cases explicit at every
  encoding depth 1–5, with paired safe controls, through real MCP and
  ScenarioRunner.
- Recreate the one-to-one A2 → R5 → A3 → R6 bounded delivery handoff and keep
  OSS-04E blocked until R6 publishes.

## Capabilities

### New Capabilities

- `qa-mcp-operation-boundary-concurrency-bounds-design`: reviewed replacement
  design for context-local evidence authority, canonical bounds, complete
  hostile/control matrices and bounded successor authorization.

### Modified Capabilities

- None. Runtime behavior remains unchanged until separately delivered runtime
  successors implement the replacement design.

## Impact

This change touches documentation, OpenSpec workflow and board metadata only.
It changes no Python manager code, MCP provider setup, protocol tool, runtime
lab configuration or dependency. It uses retained offline evidence and needs
no live 1C, Vanessa MCP, Windows execution, EDT/meta snapshot, Docker,
host-agent or business-data mutation.
