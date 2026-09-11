## Why

The real bound window-list tool can report success with an empty value when its
backend raises a typed display error. The primitive returns a legacy error dict,
which the generic executor wraps as success before the positive schema removes
its diagnostic fields. This obscures an actual runtime failure.

## What Changes

- Translate window-list backend errors into typed operation failure at its trusted
  primitive adapter, preserving the existing safe public failure vocabulary.
- Keep empty/nonempty inventories successful with exact counts, and preserve
  arbitrary successful dictionaries in the generic executor without heuristics.
- Prove real bound/unbound factories, local/Windows-host adapters, ordinary/typed
  failures, secret-safe serialization and deliberate direct legacy compatibility.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `qa-mcp-shared-core-extension`: truthful window-list failure translation and
  separation of primitive verdicts from successful generic data.

## Impact

The window-list adapter and default handler registry in src/qa_mcp/mcp_server.py;
shared executor compatibility tests, focused tests/test_display_failure_verdicts.py,
consumer docs and the shared-core specification. No protocol, live runtime,
new taxonomy, generic artifact trust, active-window DTO or ChangeRail changes.
