## Why

The pending fixture manifest cannot become live protocol evidence until the
controlled read-only fixture surface is validated or explicitly blocked. This
change prepares the external EDT/runtime boundary for `Button`, `Table`,
`CommandBar`, `Page`, `Label` and `CheckBox` without committing generated
fixture output.

## What Changes

- Validate or author the controlled read-only fixture source in an external
  workspace and retain only compact source/readiness evidence in git.
- Record family-by-family fixture availability for the planned case ids from
  `fixture_case_manifest.json`.
- Preserve the safety boundary: no clicks, command execution, input, checkbox
  toggles, table edits, page navigation with side effects or business-data
  writes.
- Route EDT/meta/Vanessa/provider gaps to their owners instead of accepting
  inferred fixture coverage.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require reviewed fixture-source readiness or an
  explicit provider/lab blocker before live fixture capture is treated as
  actionable.

## Impact

- Touches protocol research docs and compact evidence under
  `docs/protocol-research/evidence/`.
- May use `edt-mcp`, `meta-mcp` or Vanessa UI evidence to validate form shape,
  but raw TCP capture and replay remain independent from those providers.
- Requires no accepted protocol-claim promotion and no committed EDT
  workspace, infobase export, raw capture, provider payload or local runtime
  log.
