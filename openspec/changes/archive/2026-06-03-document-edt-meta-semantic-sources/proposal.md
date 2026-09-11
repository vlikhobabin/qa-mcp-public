## Why

The protocol lab now needs optional help, metadata and EDT context to interpret
read-only corpus gaps, but the current project docs do not name the approved
source locations or provider boundaries. Without that contract, semantic
labels can drift into protocol proof or generated workspace data can leak into
reviewed changes.

## What Changes

- Document the authoritative help/meta/EDT sources for the demo protocol lab,
  including the expected EDT workspace or metadata snapshot location outside
  git.
- Record how `help-mcp`, `meta-mcp` and `edt-mcp` may be used for corpus case
  selection, semantic labeling and controlled fixture authoring.
- Preserve the rule that TCP capture, normalization, replay and Python-manager
  probing remain independent from metadata services.
- Add compact evidence expectations for provider readiness or skipped-provider
  gaps without committing raw EDT workspaces, infobase exports or local runtime
  output.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: define the semantic-source inventory and provider
  boundary that supports protocol corpus interpretation without replacing wire
  evidence.

## Impact

- Touches protocol research docs, compact evidence indexing and OpenSpec
  planning artifacts.
- Does not change Python manager code, protocol capture tools, MCP provider
  registration or runtime lab configuration.
- Requires no live 1C runtime by default; provider checks may use existing
  `help-mcp`, `meta-mcp` or `edt-mcp` readiness evidence or a fresh sanitized
  provider-readiness summary when available.
