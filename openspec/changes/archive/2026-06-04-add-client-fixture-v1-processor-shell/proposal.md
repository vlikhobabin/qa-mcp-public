## Why

The protocol lab needs a stable TestClient fixture form before read-only
control coverage can move beyond the current sales dashboard. Creating a
dedicated processor shell first gives later control and evidence changes a
target-bound metadata object that can be validated independently.

## What Changes

- Add the planned V1 client fixture processor shell to the `client` EDT target.
- Define the default managed form boundary and top-level protocol markers:
  `PF_FORM_MAIN`, `PF_FIXTURE_VERSION` and `protocol-fixture.v1`.
- Add deterministic local state attributes required by later V1 controls:
  `PF_LAST_ACTION`, `PF_ACTION_COUNTER` and `PF_SELECTED_ROW_MARKER`.
- Add a reset command hook as a named inert fixture command, without treating
  command execution as accepted protocol knowledge.
- Keep the change target-bound to `vanessa_client`; no raw TCP parsing,
  business object writes or manager harness code is introduced.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require the V1 client fixture processor shell to be
  target-bound, marker-visible and safe to open before control-family coverage
  is added.

## Impact

- Touches 1C metadata, a managed form and a form module in
  `C:\1C_BASES\EDT\vanessa_qa\vanessa_client`.
- Uses `edt-mcp` target context `client` for binding validation and later EDT
  update/apply work.
- Requires live TestClient or Vanessa UI evidence only for form-open proof;
  it does not create new protocol mappings or accepted descriptors.
- Reviewed evidence remains compact; generated EDT output, raw captures,
  screenshots and platform logs stay under ignored `.artifacts/` or
  `runtime/` paths.
