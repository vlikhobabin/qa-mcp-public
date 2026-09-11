## Why

V3 mutation work needs a deterministic local state model before any handler or
recovery behavior can be trusted. The current V2 safe-action boundary proves
that fixture-local UI state can be observed and reset, but it does not yet
define the mutation-oriented state record that V3 scenarios will mutate and
restore.

## What Changes

- Add a fixture-local mutation state model for editable values, checkbox
  state, inert action markers and baseline reset tracking.
- Define stable initial and mutated values for mutation targets so the fixture
  can be reset back to the same V1 baseline after each scenario.
- Keep the state model transient, fixture-local and isolated from business
  objects, registers, external files and external services.
- Provide observable marker transitions that downstream mutation evidence can
  correlate with pre-state, post-state and rollback checks.

## Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: V3 fixture behavior gains a resettable local mutation
  state model that supports deterministic rollback.

## Impact

- Client fixture BSL and managed form code in the `vanessa_client` infobase.
- Protocol research docs and later compact evidence bundles.
- Requires live 1C runtime evidence for verification.
