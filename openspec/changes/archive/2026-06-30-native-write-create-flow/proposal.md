## Why

Creating a record through a managed form requires multiple field edits and a save command on the same live form session. The current `run_write_scenario_tool` handles only input steps and reports command/save steps as unsupported, so fill-then-save create flows cannot be verified through qa-mcp.

## What Changes

- Extend the write scenario path to execute a stateful create flow on one session.
- Support command steps such as save/write after field input.
- Add persistence verification by read-back/list/data assertion when the caller requests it.
- Preserve fail-closed diagnostics for unsupported or unsafe steps.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: native write scenarios can fill multiple fields, invoke a save/write command, and report retained UI-to-data verification evidence.

## Impact

- Touches `src/qa_mcp/scenario/runner.py`, scenario models/transpilation if needed, write protocol helpers and MCP tool wrapper code.
- Adds tests around stateful write scenario execution.
- Requires explicit live 1C runtime evidence for persisted record creation; offline tests are required before live execution.
