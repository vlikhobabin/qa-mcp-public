## Why

Published OSS-05-I1 defines one bounded decision for the public standalone
bridge API major `1`. Deterministic preflight requires a separate tracked
authorization source containing the canonical closed six-field object before
the OSS-05 successor can proceed to critical review.

## What Changes

- Publish one exact authorization object binding OSS-05-I1 to the current
  OSS-05 `3.inprogress` card.
- Use machine ceiling `301`, preserve the successor's independent `300` LOC
  gate and permit its already investigated API v1 wire contract.
- Add reciprocal investigation/authorization/successor relations and a
  fail-closed mismatch contract.
- Keep the payload metadata-only and non-reusable.

## Capabilities

### New Capabilities

- `qa-mcp-standalone-host-bridge-api-v1-authorization`: Exact published
  authorization source and consumption rules for the OSS-05 API v1 successor.

### Modified Capabilities

- None.

## Impact

OpenSpec and board metadata only. No Python, Go, installer, protocol, Windows,
live 1C, Docker or external-action behavior changes.
