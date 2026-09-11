## Why

`qa_mcp_doctor` defaults quick probes to a short timeout, so a large file-base
COM doctor can fail even when the project profile already declares a longer
real-base timeout. The doctor should consume that profile by default while
keeping explicit CLI/tool overrides available.

## What Changes

- Add a centralized `QA_MCP_DOCTOR_COM_TIMEOUT_SECONDS` setting.
- Make CLI and MCP doctor calls use that setting by default for COM doctor
  checks.
- Preserve explicit `timeout_sec` arguments as debugging overrides.
- Report the effective COM doctor timeout as a non-secret numeric diagnostic.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-runtime-configuration`: doctor COM timeout is parsed through the
  centralized settings accessor and used as the default doctor timeout.

## Impact

- Affects Python manager config and doctor code plus offline tests.
- Does not change protocol captures, live 1C runtime behavior, Vanessa MCP, EDT,
  metadata snapshots, or raw runtime evidence.
