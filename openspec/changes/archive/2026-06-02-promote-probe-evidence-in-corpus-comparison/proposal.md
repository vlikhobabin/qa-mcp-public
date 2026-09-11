## Why

The corpus comparison tool currently keeps rows with stable normalized hashes
as `non_accepted` when replay status is still `pending`, even when a direct
Python-manager probe has already confirmed the same read-only family. The
tooling needs to consume compact probe evidence so the first stable read-only
mappings can become accepted dictionary entries.

## What Changes

- Add probe-evidence ingestion or mapping support for reviewed corpus rows.
- Promote repeated stable rows to accepted comparison results only when probe
  evidence confirms the same operation.
- Keep element-detail and typed-input rows explicit when direct probe output
  exists but reviewed request-frame hashes are incomplete.
- Add focused tests for accepted, pending, incomplete and unsupported
  classification behavior.
- Generate compact evidence for the first accepted read-only mappings.
- This change touches protocol tools, tests and reviewed protocol evidence.
  It may reuse existing compact evidence offline; live 1C runtime is only
  needed if fresh probe evidence must be regenerated.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Add requirements for probe-confirmed corpus
  comparison and explicit unresolved direct-probe gaps.

## Impact

- `tools/protocol-research/protocol_corpus_runner.py`
- `tools/protocol-research/compare_corpus_runs.py`
- tests under `tests/`
- compact evidence under `docs/protocol-research/evidence/`
- `docs/protocol-research/evidence-index.md`
