## Why

`write_form_fields_by_label` cannot foreground bare-create links such as
`e1cib/data/Справочник.Валюты`, even though `read_form_descriptor` can open the
same links. This blocks config-agnostic create-form writes before field input
begins.

## What Changes

- Add a bare-create foreground path for `e1cib/data/<Тип>.<Имя>` links without
  `?ref=`.
- Preserve the existing list and record-link foreground behavior.
- Return fail-closed diagnostics when foreground replay/opening diverges,
  times out, or cannot keep the target form active.
- Add offline tests for foreground route selection and result diagnostics.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: native write helpers can foreground bare-create
  managed forms before label-based input.

## Impact

- Touches Python manager/MCP runtime code under `src/qa_mcp/`.
- Touches native write foreground behavior for `write_form_fields_by_label`,
  `write_form_value`, and create scenario setup.
- Requires offline Python tests plus Linux-native TestClient evidence before
  accepting the live runtime claim.
- Does not depend on Vanessa MCP, EDT snapshots, or committed raw captures.
