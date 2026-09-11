## Why

If the selected demo button passes safety classification, the pilot needs a
small guarded runtime capture to learn whether real demo-button action evidence
can be retained under the V2 contract. If classification fails, capture must
publish a blocked result without clicking.

## What Changes

- Execute at most one reviewed demo-button manifest row, and only when the
  classification change marks it capture-eligible.
- Retain pre-read, action-start, action-end, post-read and recovery or
  recovery-read evidence.
- Keep action, background and recovery ranges separate for later publication.
- Fail closed without clicking when the selected row is unsafe, incomplete,
  unavailable or mutating.
- Keep raw captures, platform logs and generated replay payloads under ignored
  runtime paths.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: Demo real-button safe-action pilots have a guarded
  capture step that executes only reviewed non-mutating rows and records phase
  evidence.

## Impact

- Windows-native runtime capture tooling and local lab infobases may be used.
- Runtime output remains under `runtime/protocol-research/captures/<run-id>/`.
- Compact retained evidence belongs under
  `.artifacts/openspec/capture-demo-button-safe-action-pilot/<run-id>/` or
  reviewed docs evidence paths.
- Requires live 1C runtime only when classification produces a capture-eligible
  row.
