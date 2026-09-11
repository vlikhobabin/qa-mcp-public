## Why

V4 needs an explicit dialog and recovery surface model before handlers or
captures can be trusted. Without deterministic dialog markers, warning,
question and modal-form evidence would be hard to separate from infrastructure
noise or accidental business behavior.

## What Changes

- Define a fixture-local V4 dialog state model for warning, question and modal
  form scenarios.
- Add stable `PF_*` marker names for dialog kind, text, selected result,
  lifecycle state and recovery state.
- Classify each planned dialog family as fixture-local, mutation-like or
  requiring special recovery evidence.
- Keep the model isolated from business data, OS dialogs, file dialogs,
  printing and external side effects.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: V4 fixture behavior gains deterministic dialog
  surface markers and classification requirements.

## Impact

- Client fixture managed form and form module in the `vanessa_client` infobase.
- Protocol research documentation and later compact evidence bundles.
- Requires live 1C runtime and Vanessa/EDT evidence during implementation, but
  this planning change does not run runtime captures.
