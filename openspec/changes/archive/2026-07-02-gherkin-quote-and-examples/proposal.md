## Why

The Gherkin transpiler accepts real-world feature text but can silently corrupt it: quoted values containing the other
quote character are truncated, repeated `Примеры:` blocks can become bogus scenarios, and escaped table pipes are not
preserved. A scenario can therefore pass while executing a different value or an extra unintended outline row.

## What Changes

- Require Gherkin quoted captures to use matching delimiters while allowing the other quote character inside the value.
- Keep `Примеры:` parsing scoped per examples block so every block skips its own header row and only data rows expand
  scenarios.
- Preserve `\|` as a literal pipe inside table cells.
- Treat unsupported triple-quoted docstrings explicitly rather than letting their lines masquerade as executable steps.
- Add focused offline regression tests in `tests/test_scenario_gherkin.py`.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Gherkin parsing must preserve quoted values, examples tables and escaped table cells without
  silently corrupting scenario input.

## Impact

- Touches Python manager code under `src/qa_mcp/scenario/gherkin.py`.
- Adds offline tests under `tests/test_scenario_gherkin.py`.
- Does not require live 1C runtime, Vanessa MCP, EDT/meta snapshots, raw captures or runtime lab config.
