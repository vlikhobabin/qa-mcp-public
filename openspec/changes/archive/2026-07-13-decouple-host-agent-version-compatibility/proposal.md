## Why

The qa image currently accepts host-agent build labels through a hardcoded
exact-string allowlist. A wire-compatible host-agent bump therefore breaks an
already shipped image until the image is rebuilt or an operator pins the new
label manually. The T4 stand reproduced this with image `0.1.4` and host-agent
`0.1.6`; the same UI read succeeded as soon as the exact override was set.

This change touches the Python display backend and doctor, the Go `/version`
response, tests, docs and OpenSpec. It needs only offline HTTP/test fixtures;
the `.201` T4 result is retained live evidence.

## What Changes

- Advertise a stable display-protocol id from authenticated `/version`.
- Default compatibility checks use that protocol, while known legacy agents
  without the field remain accepted.
- Explicit version and SHA pins remain exact.
- Doctor reports a bounded compatibility relationship instead of only success.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-tool-endpoint-contract`: remote display handshake is based on a
  stable protocol id rather than a build-label allowlist.
- `qa-mcp-runtime-configuration`: doctor reports host-agent compatibility
  relationship and protocol without secrets.

## Impact

- `host-agent/windows-display-agent/main.go` and Go tests
- `src/qa_mcp/protocol/display_backend.py`
- `src/qa_mcp/doctor.py`
- display-backend and doctor tests
- `host-agent/README.md`
