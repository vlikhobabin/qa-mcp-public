## Why

Live fixture output is not useful until each family is classified against the
corpus evidence contract. This change compares the new fixture evidence and
keeps unresolved rows visible instead of promoting weak or incomplete mappings.

## What Changes

- Compare fixture corpus/probe evidence and classify each planned family as
  accepted, partial, pending, unsupported, timeout, rejected or blocked.
- Record repeated-capture stability, normalized hash behavior and probe/replay
  agreement where available.
- Produce compact classification evidence without rewriting historical corpus
  rows.
- Leave families non-accepted when request hashes, frame ranges or probe joins
  are incomplete.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require explicit fixture classification before new
  controlled read-only fixture rows can feed accepted mappings.

## Impact

- Touches compact evidence under `docs/protocol-research/evidence/`.
- Uses `tools/protocol-research/compare_corpus_runs.py` and existing corpus
  evidence contracts.
- Requires no live 1C mutation and does not commit raw capture or probe output.
