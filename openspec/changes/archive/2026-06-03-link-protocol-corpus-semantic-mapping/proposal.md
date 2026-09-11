## Why

The expanded read-only corpus shows explicit fixture gaps for several form
element families, but current evidence does not map those gaps back to the
demo configuration forms and elements. A curated semantic map is needed so
future captures can target the right objects while still treating wire
evidence as the source of protocol truth.

## What Changes

- Add a compact semantic mapping artifact that links reviewed corpus case ids
  to available help/meta/EDT references for forms, form elements and tested API
  object-model terms.
- Record which mappings are stable enough to label corpus evidence and which
  remain unresolved because the current capture lacks a stable name, GUID or
  element family.
- Update evidence documentation so semantic mapping rows are connected to
  existing corpus and accepted-mapping evidence without embedding raw provider
  payloads.
- Keep semantic mapping optional for capture, normalization, replay and direct
  Python-manager probing.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require corpus semantic mappings to be compact,
  optional and explicitly linked to primary protocol evidence rows.

## Impact

- Touches protocol research docs and compact evidence artifacts under
  `docs/protocol-research/evidence/`.
- May use `meta-mcp` and `help-mcp` to inspect the demo configuration and
  platform help, with sanitized summaries only.
- Does not require EDT workspace mutation, live TestClient execution, Vanessa
  MCP, Python manager code changes or raw capture output.
- Depends on `document-edt-meta-semantic-sources` for source/boundary policy.
