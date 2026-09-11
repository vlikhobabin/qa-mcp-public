## Why

Single corpus captures cannot prove that a normalized request shape is stable.
The lab needs repeated-capture comparison so accepted dictionary entries can
separate stable command semantics from session-specific dynamic fields.

## What Changes

- Add comparison behavior for repeated corpus runs of the same case set.
- Report stable normalized hashes, divergent hashes and newly suspected
  dynamic ranges.
- Produce compact repeatability evidence that links every comparison back to
  capture ids and case ids.
- This change touches protocol tools and protocol research evidence. It
  requires live 1C runtime for final comparison evidence, but the analyzer
  should also work offline against retained local captures.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Add requirements for repeatability comparison across
  corpus captures.

## Impact

- `tools/protocol-research/protocol_corpus_runner.py` or a companion
  comparison tool under `tools/protocol-research/`.
- Compact reports under `docs/protocol-research/evidence/`.
- Existing raw capture policy remains unchanged.
