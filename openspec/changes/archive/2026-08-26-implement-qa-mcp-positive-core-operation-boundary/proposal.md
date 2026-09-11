## Why

Published R5-R2 and A4 close the positive-result contract and authorize one
bounded R7 implementation. The current shared core still returns executor DTOs
directly, so it has no immutable positive schema, context-local evidence
receipt authority or total bounded reconstruction surface for the later R8
public-path integration.

## What Changes

- Add an application-owned immutable operation-schema catalog containing only
  closed structural nodes and the six published finite scalar classes.
- Add a context-local evidence ledger with exact-operation receipts and frozen
  full-local root/policy authority.
- Add sealed operation provenance admission and a total core result normalizer
  with exact artifact, URL, structure, node and canonical-byte bounds.
- Extend the public core DTO/export surface and shared-core documentation for
  direct R7 use without wiring MCP, ScenarioRunner or lifecycle routes.
- Add a test-first direct Linux matrix and exact-source Windows offline proof;
  no live 1C, protocol capture, Docker or external mutation is required.

## Capabilities

### New Capabilities

- `qa-mcp-positive-core-operation-boundary`: immutable positive schemas,
  context-local receipt authority and total bounded public-result
  reconstruction implemented by the shared core.

### Modified Capabilities

- None. The published concurrency/bounds design and A4 authorization remain
  immutable inputs rather than implementation-owned requirements.

## Impact

- Python shared core under `src/qa_mcp/core/`.
- Direct boundary tests and `docs/shared-core-extension.md`.
- No current MCP/ScenarioRunner routing, lifecycle admission, provider
  settings, wire protocol, protocol tools or runtime-lab configuration.
