## Why

The previous changes make remote display routing and the Windows host agent
available, but model-B is only complete when the currently guarded display
tools work end to end against a real Windows-rendered 1C client. The spike
proved `SendInput`; this change turns that proof into retained qa-mcp
verification evidence.

## What Changes

- Wire the ported tools through the remote display backend in model-B mode.
- Live-verify a genuine object-attribute edit with `write_form_value_xtest`
  against the Windows lab.
- Live-verify a real host screenshot via `capture_screenshot`.
- Smoke the remaining display subset: `send_keys`, `get_window_list`,
  `write_form_fields_by_label`, and `set_table_date_cell` where the lab state
  safely allows it.
- Publish a compact evidence bundle and update protocol research docs/indexes.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: model-B remote-client mode includes verified Windows
  host display coverage for the OS input/screenshot subset that cannot run in
  the Linux container.

## Impact

- Touches tests, docs and evidence under `docs/protocol-research/`.
- May touch model-B Docker docs with final run commands.
- Requires live Windows lab runtime and retained evidence.
- Does not require committing raw large captures, full screenshots with
  sensitive data, infobases or platform logs.
