## Why

`write_form_fields_by_label` contains a create-form activation retry, but its guard checks for a
`foreground_method` value no production path sets. The retry never runs for actual `create_listreplay` foregrounding,
so first-screenshot render races still fail as plain label misses.

## What Changes

- Wire the retry guard to the foreground method values that production code actually emits, or remove the dead branch if
  the retry is no longer needed.
- Keep the retry bounded to a single activation attempt for create/list foreground races.
- Add offline tests that simulate a first-screenshot miss followed by a successful retry and assert
  `activation_retry` is populated.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: create-form label writes must either run their documented activation retry for actual
  foreground methods or remove unreachable retry metadata from the result contract.

## Impact

- Touches `src/qa_mcp/mcp_server.py`.
- Adds focused offline tests in `tests/test_mcp_server.py`.
- Does not require live runtime by itself, but the card-level write regression still runs after all CR-03 changes.
