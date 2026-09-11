## Why

After package primitives and session APIs are promoted, existing research CLIs
must remain usable while sharing the package implementation. This avoids a
fork between exploratory scripts and the reusable runtime code.

## What Changes

- Refactor protocol research scripts to import `qa_mcp.protocol` APIs instead
  of duplicating promoted logic.
- Preserve current CLI behavior, output schemas and Windows-native commands
  where practical.
- Add compatibility tests or smoke checks for existing script entrypoints.
- Update docs so operators know package APIs are the source of reusable
  behavior while raw research outputs still stay under `runtime/`.
- This change touches protocol tools, package imports, tests and docs. Live 1C
  runtime is only needed for optional probe CLI smoke; offline compatibility
  checks are required.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Add requirements for research tool compatibility
  after package promotion.

## Impact

- `tools/protocol-research/python_manager_client.py`
- `tools/protocol-research/python_manager_probe.py`
- other protocol research scripts that import promoted helpers
- `src/qa_mcp/protocol/`
- tests and protocol docs
