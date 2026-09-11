## Why

Read-only protocol evidence now has explicit unresolved/deferred boundaries,
but the lab still needs a reviewable safety contract before any UI action
traffic is captured. This change defines which non-mutating UI actions may be
studied and which action/write semantics remain excluded.

## What Changes

- Define the first safe UI-action scope as focus/element activation, active
  window activation, tab/page switching and menu expansion only when business
  data is not mutated.
- Record the required pre-state, action, post-state and recovery/cleanup
  expectation for every candidate action case before capture starts.
- Preserve explicit gates from the controlled fixture and read-only element
  hash cards: unresolved read-only evidence may be deferred, but it cannot be
  hidden when selecting action targets.
- Exclude text input, command execution with side effects, checkbox toggles,
  table edits, posting, saves and other business-data mutation.
- This change touches protocol research docs, OpenSpec planning artifacts and
  protocol-lab evidence policy. It requires no live 1C runtime by itself.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: add the safe UI-action scope, precondition gates and
  excluded mutation semantics before action protocol cases can be accepted.

## Impact

- `openspec/specs/qa-mcp-protocol-lab/spec.md` delta requirements.
- `docs/protocol-research/` policy or evidence contract notes during
  implementation.
- Downstream capture and analyzer changes must consume this scope instead of
  broadening directly into clicks, input or writes.
