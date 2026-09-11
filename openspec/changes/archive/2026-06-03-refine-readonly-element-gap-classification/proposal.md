## Why

The current `incomplete_hash` classification is useful but too broad for the
element-detail follow-up. After audit and capture/extraction, the comparison
and reporting path must distinguish missing request frames from ambiguous
joins, unsupported fixture state and incomplete normalizer coverage.

## What Changes

- Refine corpus comparison or related protocol tooling so
  `form-element-details` and `typed-input-field-readonly` unresolved rows carry
  actionable reasons.
- Keep accepted classification conservative: rows are accepted only when
  repeated reviewed request hashes and replay or direct Python-manager proof
  support the same operation.
- Add focused tests for missing frames, ambiguous operation joins, unsupported
  fixture state and incomplete normalizer coverage.
- Generate compact classification evidence from the audit/capture outputs.
- This change touches protocol comparison/classification tools, tests and
  reviewed evidence. It can run offline once compact evidence exists and does
  not require live 1C runtime, EDT/meta snapshots or MCP provider setup.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Add requirements for precise unresolved reasons when
  useful read-only element rows cannot be accepted.

## Impact

- `tools/protocol-research/compare_corpus_runs.py`
- `tools/protocol-research/protocol_corpus_runner.py`
- tests under `tests/`
- compact evidence under `docs/protocol-research/evidence/corpus-comparison/`
- No package descriptor status changes, safe UI actions or write behavior are
  introduced.
