## Why

The API corpus roadmap treats a help-derived automated-testing inventory as an
input to industrial corpus planning, but no
`docs/protocol-research/api-inventory/automated-testing-*.json` artifact exists
yet. The live pipeline needs that inventory before expanding beyond the first
smoke commands.

## What Changes

- Generate the first automated-testing API inventory from `help-mcp` or the
  approved platform help source.
- Record object, member, constructor, parameter, return-type and default
  safety classification fields where available.
- Store compact reviewed inventory and summary artifacts under
  `docs/protocol-research/api-inventory/`.
- Keep gaps explicit when a help topic or platform version cannot be resolved.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require a reviewed automated-testing API inventory as
  planning input for broad API-driven corpus expansion.

## Impact

- Touches protocol research documentation and inventory artifacts.
- Uses `help-mcp` or approved documentation sources; no live 1C runtime is
  required.
- Does not generate protocol claims or accepted mappings by itself.
