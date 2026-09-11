## Why

After the audit, capture/extraction and classification changes complete, the
repository needs one publication step that makes the final status visible to
operators and future protocol work. Accepted evidence should update descriptors
and docs; unresolved evidence should keep descriptors conservative with a
sharper reason.

## What Changes

- Publish compact accepted-mapping evidence for `form-element-details` and
  `typed-input-field-readonly` when reviewed request hashes are accepted.
- If accepted evidence is not available, publish a compact unresolved report
  that preserves precise reasons from classification.
- Update `qa_mcp.protocol` descriptors only when accepted evidence changes;
  otherwise preserve `incomplete_hash` or another explicit non-accepted status.
- Update protocol docs and the evidence index so downstream cards know whether
  safe-action work is unblocked.
- This change touches package descriptors, tests, protocol docs and reviewed
  evidence only when the evidence outcome requires it. It does not require live
  1C runtime unless a final smoke is chosen during delivery.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Add requirements for publishing the accepted or
  unresolved outcome of useful read-only element hash resolution.

## Impact

- `src/qa_mcp/protocol/`
- tests under `tests/`
- `docs/protocol-research/evidence-index.md`
- `docs/protocol-research/python-protocol-package.md`
- `docs/protocol-research/protocol-corpus-runner.md`
- compact evidence under `docs/protocol-research/evidence/accepted-mappings/`
  or `docs/protocol-research/evidence/readonly-element-hash-resolution/`
- No safe UI action, click, input, write or business-data mutation behavior is
  introduced.
