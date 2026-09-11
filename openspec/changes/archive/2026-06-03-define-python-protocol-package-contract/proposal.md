## Why

The first accepted read-only mappings now exist, but reusable Python manager
code is still exposed mainly through exploratory scripts. A package-level
contract is needed before moving protocol primitives into `src/qa_mcp` so the
runtime API stays evidence-backed and does not overclaim incomplete mappings.

## What Changes

- Define the public `qa_mcp.protocol` read-only package contract and naming
  boundaries before moving implementation code.
- Record which read-only operations are accepted, supported-but-unresolved or
  unsupported based on compact corpus/probe evidence.
- Require package APIs to reference compact evidence paths, accepted
  normalized hashes and unresolved reasons rather than raw runtime captures.
- Keep the package scope read-only; safe UI actions, writes and business-data
  mutation remain out of scope.
- This change touches Python manager code contracts, docs/specs and planning
  artifacts. It does not require live 1C runtime, Vanessa MCP or EDT/meta
  snapshots; accepted mapping evidence is already committed.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Add requirements for an evidence-aware
  `qa_mcp.protocol` package contract and read-only acceptance boundaries.

## Impact

- Future code under `src/qa_mcp/protocol/`
- `docs/protocol-research/` package/runtime documentation
- Tests under `tests/`
- Existing accepted evidence under `docs/protocol-research/evidence/`
