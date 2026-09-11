## Why

The create scenario still reports persistence verification as a provider gap
and lacks a reviewed cleanup route for the demo10413 contract record. A live
save proof is not acceptable until UI-to-data assertion and cleanup evidence
are part of the workflow.

## What Changes

- Replace the persistence verification stub with a real read-back/data
  assertion summary for created records.
- Add cleanup-required gating before mutation proof is accepted.
- Retain cleanup/rollback evidence and unresolved-leftover diagnostics for the
  demo10413 contract create flow.
- Add offline tests for verification summaries, cleanup gating, and failure
  behavior when cleanup evidence is missing.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: native create scenarios can report UI-to-data
  persistence assertions and cleanup evidence for accepted mutation proof.

## Impact

- Touches Python manager/MCP runtime code under `src/qa_mcp/`.
- Touches create scenario verification output, retained evidence summaries, and
  cleanup policy checks.
- Requires the reference-owner change before live end-to-end proof.
- Requires Linux-native TestClient and read-back/cleanup evidence; raw runtime
  logs and local artifacts remain ignored.
