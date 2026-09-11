## Why

Read-only protocol captures are only useful when every TestManager API command
has a stable case id, target marker and side-channel boundary. The manager V1
harness needs a documented manifest and event-log contract before it executes
the client fixture surface.

## What Changes

- Define the V1 manager run manifest fields, including `run_id`, `case_id`,
  `command_id`, proxy/TestClient port, target fixture path and expected
  markers.
- Define the read-only command catalog for active window, active form, form
  summary, element enumeration, element value/text/caption, visibility,
  enabled/read-only state, tested object class, table rows/columns, command
  bar buttons, groups and pages.
- Define `case_events.jsonl` and `manager_harness_result.json` records with
  timestamps before/after each command, status, target `PF_*` marker, expected
  response marker and exception details.
- Keep V1 command cases read-only; no clicks, text input, page switching,
  table selection, business commands or object writes are accepted.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require stable manager-side read-only command
  manifests and side-channel event records for client fixture corpus cases.

## Impact

- Touches manager harness 1C source and compact protocol-lab documentation.
- Consumes the client fixture V1 target map and live-open evidence.
- Requires live 1C/Vanessa runtime evidence for command execution during
  implementation verification.
- Does not require protocol normalization or Python replay acceptance by
  itself.
