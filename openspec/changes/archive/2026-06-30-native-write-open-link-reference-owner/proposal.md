## Why

The subordinate contract create form exposes editable `Владелец`, but the
existing reference setter is tied to a fixed fixture capture. The open-link
write flow needs a config-agnostic way to set owner references on the live
foregrounded form.

## What Changes

- Add an open-link reference field write route usable after create-form
  foregrounding.
- Validate reference field requests before live interaction and fail closed on
  unsupported or ambiguous cases.
- Surface actionable diagnostics for missing labels, missing values, and
  selection failures.
- Add offline tests for variable-length reference values and unsupported
  reference routes.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: native write scenarios can set an open-link
  reference field such as `Владелец` during create-form input.

## Impact

- Touches Python manager/MCP runtime code under `src/qa_mcp/`.
- Touches create scenario step routing and write-result summaries.
- Requires the bare-create foreground change before live proof.
- Requires Linux-native TestClient UI evidence for the reference interaction;
  offline tests cover routing and fail-closed behavior.
