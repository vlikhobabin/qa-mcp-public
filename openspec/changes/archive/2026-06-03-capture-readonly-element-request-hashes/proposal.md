## Why

The audit can identify whether reviewed request hashes are missing, stale or
extractable, but the card is not resolved until the lab either obtains
accepted request-frame evidence for the useful element rows or proves that the
current lab path cannot supply it.

## What Changes

- Capture or extract reviewed manager-to-client request frames for
  `form-element-details` and `typed-input-field-readonly`.
- Use the direct Python-manager probe path and existing frame-template model
  where possible, with the `101..106` short element-details schedule as the
  first target and a full `1..106` schedule only when needed.
- Record capture id, frame range, request and response sizes, normalized hash,
  dynamic fields, operation token, response markers and replay or direct
  Python-manager status in compact reviewed evidence.
- If reviewed request hashes cannot be produced, record whether the blocker is
  missing frames, ambiguous operation join, unsupported fixture state,
  incomplete normalizer coverage or unavailable runtime.
- This change may touch capture/extraction tools under
  `tools/protocol-research/` only when existing tooling cannot emit the
  reviewed hash evidence. It requires live 1C runtime only for fresh capture;
  it does not require EDT/meta snapshots or MCP provider setup.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Add requirements for capturing, extracting or
  explicitly proving unavailable reviewed request hashes for useful read-only
  element probe rows.

## Impact

- `tools/protocol-research/python_manager_probe.py`
- `tools/protocol-research/protocol_corpus_runner.py`
- `tools/protocol-research/compare_corpus_runs.py`
- compact evidence under `docs/protocol-research/evidence/`
- ignored raw output under `runtime/protocol-research/`
- No click, input, safe-action, write or business-data mutation behavior is
  introduced.
