## Why

The current corpus runner records read-only case rows, but safe UI actions
need a richer event boundary so reviewers can distinguish the intended action
from background refresh traffic. Adding the action event contract first keeps
live capture evidence auditable.

## What Changes

- Extend corpus case definitions and side-channel events with pre-state,
  action, post-state, recovery expectation and action result markers.
- Add analyzer support for separating action-related frame ranges from
  background refresh or idle frames.
- Extend compact row output with action-specific fields while preserving the
  existing corpus evidence contract.
- Add offline tests for row/event classification, unsupported action statuses
  and refresh-noise separation.
- This change touches protocol tools and protocol research docs. It should be
  verified offline first and does not require live 1C runtime for completion.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require safe action case events and reviewed action
  row fields before live action captures can be accepted as protocol evidence.

## Impact

- `tools/protocol-research/protocol_corpus_runner.py` and any companion
  analyzer used to build compact corpus rows.
- Tests under `tests/` for event rows, action markers and background refresh
  filtering.
- `docs/protocol-research/corpus-evidence-contract.md` or action-specific
  protocol docs.
- No MCP provider setup, EDT/meta snapshots or runtime lab config changes are
  expected.
