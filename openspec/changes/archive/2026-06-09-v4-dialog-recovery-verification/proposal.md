## Why

V4 complex UI scenarios are only useful if failures, cancellations and
expected errors can be recovered without restoring the infobase. The lab needs
a dedicated recovery-proof change before dialog, wait or error evidence can be
trusted.

## What Changes

- Define the V4 recovery evidence sequence for dialog, expected-error and
  bounded-wait scenarios.
- Require every scenario to return to the V1 baseline through documented
  reset or cleanup markers.
- Separate dialog/action, background, expected-error and recovery frame ranges
  in reviewed evidence.
- Fail closed when recovery cannot be proved or when an expected error looks
  like infrastructure failure.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: V4 fixture behavior gains explicit recovery proof and
  expected-failure classification requirements.

## Impact

- Client fixture recovery commands and marker reads in `vanessa_client`.
- Manager runner and protocol capture review that consume V4 phase boundaries.
- Requires live 1C runtime and compact evidence during implementation; this
  planning pass does not run captures.
