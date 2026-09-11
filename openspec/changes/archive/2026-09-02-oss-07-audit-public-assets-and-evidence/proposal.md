## Why

The tracked tree contains hundreds of curated protocol assets and evidence
files plus historical lab reports. Public readiness needs exact per-path
redistribution/provenance decisions and deterministic secret/privacy checks,
not an unbounded manual assertion.

## What Changes

- Add a deterministic offline audit for high-confidence secrets, personal or
  customer markers, private lab endpoints, unsupported packaged artifacts and
  selected-history disclosure risk without echoing matched values.
- Generate and check a canonical manifest containing every bundled protocol
  asset, protocol UI asset and curated evidence file exactly once with its
  path, digest, size, provenance class, redistribution decision and rationale.
- Sanitize only identified historical evidence markers and remove only exact
  artifacts that lack an admitted redistribution basis.
- Run the published I2 mutation verifier alongside every audit and preserve
  its exact frozen bytes and semantics.

## Capabilities

### New Capabilities

- `qa-mcp-public-provenance`: Defines exhaustive, hash-bound redistribution
  inventory and fail-closed offline disclosure checks for the public source
  snapshot.

### Modified Capabilities

- none.

## Impact

This change affects one small offline repository-audit tool, a generated
provenance manifest, curated evidence redactions/removals and OpenSpec docs. It
does not change Python manager/MCP behavior, release automation, capture/replay
semantics or runtime lab configuration. It uses only repository bytes and Git
metadata; no live, Windows, SSH, 1C, TestClient, Vanessa, EDT/meta or network
work is required.
