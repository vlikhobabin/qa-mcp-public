## Why

The repo safety language correctly prefers read-only protocol operations until
write/action semantics are understood, but V2 needs a more precise agent rule.
After the manifest contract exists, an agent should not treat arbitrary clicks,
input or command execution as V2 merely because the user asks for an action.

## What Changes

- Update local agent-facing instructions so V2 safe actions are limited to the
  documented manifest allowlist and `mutates_business_data=false` contract.
- Route text input, checkbox/value toggles, business command clicks, object
  writes, save/post/delete/fill/import/export and external side effects outside
  V2.
- Make protocol research agents fail closed when an action is not represented
  by a reviewed V2 safe-action manifest row.
- Keep the existing runtime cleanup and raw-capture safety rules unchanged.

This change touches local agent instructions and OpenSpec planning artifacts.
It requires no live 1C runtime, Vanessa MCP, EDT/meta snapshots or capture.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: agent instructions enforce the V2 safe-action safety
  boundary and route mutating UI actions to later cards.

## Impact

- `AGENTS.md`
- `.codex/skills/1c-testclient-protocol-research/SKILL.md`
- Other local `.codex/skills/*.md` routing docs only if they imply V2 can
  perform clicks, input, writes or business-command execution.
- No protocol docs, fixture, manager harness or runtime lab config changes
  unless needed to keep instructions consistent.
