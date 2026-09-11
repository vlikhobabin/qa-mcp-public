## Why

`form-element-details` and `typed-input-field-readonly` return useful
read-only data through the direct Python-manager path, but current reviewed
evidence still leaves both rows at `incomplete_hash`. Before new capture or
tooling work changes status, the existing compact corpus, comparison and probe
artifacts need one audit against the accepted evidence contract.

## What Changes

- Audit the current compact evidence for `form-element-details` and
  `typed-input-field-readonly` against the corpus evidence contract.
- Record whether each row already has reviewed frame ranges, request and
  response sizes, normalized hashes, dynamic fields, operation tokens,
  response markers, replay/probe status and source evidence paths.
- Classify the current gap for each row as already-reviewed, extractable from
  existing compact evidence, missing request frames, ambiguous operation join,
  unsupported fixture state or incomplete normalizer coverage.
- Produce a compact reviewed audit report under
  `docs/protocol-research/evidence/readonly-element-hash-audit/current-element-hash-gaps/`.
- This change touches protocol research docs/evidence and OpenSpec artifacts
  only. It uses offline curated evidence and does not require live 1C runtime,
  Vanessa MCP, EDT/meta snapshots, MCP provider setup or runtime lab config.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Add requirements for auditing useful read-only
  element direct-probe rows before promotion or final unresolved publication.

## Impact

- `docs/protocol-research/evidence-index.md`
- compact evidence under `docs/protocol-research/evidence/`
- `docs/protocol-research/python-protocol-package.md`
- `openspec/specs/qa-mcp-protocol-lab/spec.md`
- No package descriptors, raw captures, runtime logs, safe actions or write
  behavior are changed by this audit.
