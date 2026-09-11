## Why

The mutation state model is not enough by itself: V3 also needs concrete form
handlers that can exercise local editable fields, checkbox toggles and inert
button paths. Without those handlers, the mutation sandbox remains a passive
data shape and cannot generate observable mutation frames.

## What Changes

- Add fixture-local handlers for text input, numeric input, date input,
  checkbox toggles and inert button clicks.
- Route those handlers through the shared mutation state model so updates stay
  deterministic and fixture-local.
- Keep the handlers fail-closed for targets that would trigger business
  commands, writes or external side effects.
- Preserve the V1/V2 reset path so every mutation can return to the same
  baseline state.

## Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: V3 fixture behavior gains local mutation handlers for
  controlled input and inert actions.

## Impact

- Client fixture BSL and managed form code in the `vanessa_client` infobase.
- Later compact evidence bundles and mutation corpus rows.
- Requires live 1C runtime evidence for verification.
