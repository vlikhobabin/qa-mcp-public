## Why

The expanded read-only corpus can normalize repeated active-window and
active-form requests to stable hashes, but those rows remain `pending` because
direct Python-manager probe evidence is not linked into the corpus acceptance
contract. Before implementation can promote stable primitives into
`src/qa_mcp`, the reviewed evidence model needs explicit rules for
probe-backed accepted mappings and unresolved probe gaps.

## What Changes

- Define how reviewed corpus rows reference compact direct-probe evidence.
- Define when a repeated read-only mapping may be promoted to `accepted`.
- Define how element-detail and typed-input rows record unresolved
  direct-probe request-frame gaps.
- This change touches protocol research docs and OpenSpec requirements only.
  It can be verified offline from curated evidence and does not require live
  1C runtime.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Add requirements for direct-probe evidence links,
  accepted read-only mapping criteria and unresolved probe-gap reporting.

## Impact

- `docs/protocol-research/corpus-evidence-contract.md`
- `docs/protocol-research/protocol-corpus-runner.md`
- `openspec/specs/qa-mcp-protocol-lab/spec.md`
- Future corpus rows and comparison reports that consume direct Python-manager
  probe evidence.
