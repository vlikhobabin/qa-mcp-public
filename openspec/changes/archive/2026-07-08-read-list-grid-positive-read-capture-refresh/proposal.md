## Why

`read_list_grid` now fails loud instead of fabricating empty data on the
[redacted third-party configuration] currency list, but the positive read is still blocked by a
manager-handshake mismatch between the shipped capture and the real
8.3.27.2130 / Бухгалтерия 3.0 LAN contour. qa-mcp needs capture metadata,
refresh procedure, and a specific preflight so this class of mismatch is
diagnosed before a list read is trusted.

## What Changes

- Add platform-build and configuration tags to protocol capture metadata and
  expose enough metadata for config-matched selection.
- Document and tool a refresh-capture procedure for the session bootstrap and
  list-open/read templates on a target platform/configuration.
- Add a manager-handshake drift preflight that fails loudly and specifically
  when the live ACK/GUID handshake diverges from the selected capture.
- Keep the [redacted third-party configuration] positive-read proof as an explicit provider gap when the
  real Windows .205 / [redacted third-party configuration] host is unavailable.
- Preserve existing demo10413 and other proven capture behavior through offline
  tests and existing live-regression contracts.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-protocol-lab`: capture/replay metadata, config-matched capture
  selection, refresh-capture procedure, and manager-handshake drift diagnostics.

## Impact

- Touches Python protocol/runtime code under `src/qa_mcp/` and offline tests.
- Touches protocol research tooling under `tools/protocol-research/`.
- Updates `docs/capture-refresh-runbook.md`, OpenSpec artifacts, and the
  `qa-mcp-protocol-lab` spec.
- Does not commit raw captures, Vanessa EPF binaries, infobases, screenshots,
  customer data, or platform logs.
- Live [redacted third-party configuration] runtime acceptance requires the unavailable Windows .205 host
  and remains a recorded provider gap for this delivery.
