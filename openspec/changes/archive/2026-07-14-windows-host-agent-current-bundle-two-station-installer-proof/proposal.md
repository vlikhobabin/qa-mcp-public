# Current bundle two-station installer proof

## Why

Independent review accepted the current source-bound Windows artifact and its
cleanup behavior, but found that retained G12 registration and G14 BSL
supervision evidence on both supported Windows versions still belongs to an
older artifact. Inspection also showed that the supported installer exposes
G14 inputs but cannot currently render the host-agent's G12 registry flags.

## What Changes

- Add complete fail-closed bridge-registration inputs to the supported Windows
  host-agent installer.
- Prove the exact current artifact through that installer on both supported
  Windows builds, with staged/running digest equality, registered G12 state and
  ready/restart/windowless G14 state.
- Restore the immutable pre-run station/server state and retain a sanitized
  indexed evidence bundle.

## Capabilities

### Modified Capabilities

- `qa-mcp-self-hosted-release`: the supported Windows installer renders both
  durable bridge registration and BSL supervision for a verified artifact.

## Impact

The installer contract, its focused tests, synchronized release spec, QA cards
and combined delivery manifest are affected. The runtime apply is bounded to
the two authorized T4 Windows stations and is followed by exact cleanup.
