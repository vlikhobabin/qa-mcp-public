## Why

Expanded and repeated corpus runs will expose dynamic fields beyond the first
ACK GUID, sequence, nonce and operation-token ranges. The normalizer needs an
evidence-backed way to add replacements without hiding meaningful protocol
semantics.

## What Changes

- Improve dynamic-field detection and reporting for corpus rows.
- Record before/after hash behavior and replacement ranges for new
  normalizer rules.
- Add guardrails so broad replacements cannot silently make unrelated request
  families look identical.
- This change touches protocol tools, tests and protocol research evidence.
  It can be developed offline from repeated captures, with live 1C runtime
  used to confirm accepted mappings.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Add requirements for evidence-backed dynamic-field
  normalization and ambiguity reporting.

## Impact

- Normalization logic in `tools/protocol-research/protocol_corpus_runner.py`
  and potentially helper modules under `tools/protocol-research/`.
- Focused tests for dynamic-field replacement behavior.
- Compact normalizer evidence under `docs/protocol-research/evidence/`.
