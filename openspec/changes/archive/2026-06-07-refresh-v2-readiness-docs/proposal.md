## Why

Manager fixture V1 pending rows were first reported as blocking or partially
blocking V2 safe-action work, then later accepted by retained marker-contract
and typed side-channel proof. The project needs the current status docs to
tell that story coherently before downstream V2 implementation cards start.

## What Changes

- Refresh `docs/protocol-research/status-report-2026-06-06.md` so its final
  V2 readiness statement is the source of truth: V1 read-only no longer blocks
  V2 safe-action planning.
- Refresh `docs/protocol-research/safe-ui-action-scope.md` prerequisite gates
  so formerly pending V1 rows are no longer described as unresolved blockers.
- Preserve the evidence caveat that three accepted diagnostic rows are typed
  manager side-channel contract proofs, not direct wire marker observations.
- Keep raw captures, runtime logs and generated replay output outside reviewed
  changes.

This change touches protocol research docs and OpenSpec planning artifacts. It
requires only offline documentation review and validation; it does not require
live 1C runtime, Vanessa MCP, EDT/meta snapshots or protocol capture.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: V2 readiness documentation reflects the accepted V1
  read-only closure and keeps side-channel proof limitations explicit.

## Impact

- `docs/protocol-research/status-report-2026-06-06.md`
- `docs/protocol-research/safe-ui-action-scope.md`
- `openspec/specs/qa-mcp-protocol-lab/spec.md` delta requirements
- No client fixture, manager harness, Python manager or runtime lab config
  changes.
