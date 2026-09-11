## Why

The fixture plan and source readiness are useful only if the lab captures real
wire evidence and direct Python-manager results for the planned read-only
families. This change runs the Windows-native capture/probe path while keeping
raw traffic in ignored runtime storage.

## What Changes

- Run fixture-derived corpus capture for the planned manifest rows using
  Windows-native tooling and owned-PID cleanup.
- Run direct Python-manager probes or replay confirmation for available
  fixture cases.
- Retain compact corpus/probe evidence for each family or a concrete
  unresolved reason.
- Keep unsafe UI operations out of scope.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require live fixture capture/probe evidence, or an
  explicit unresolved status, before pending read-only fixture rows can move
  toward classification.

## Impact

- Touches protocol research evidence under `docs/protocol-research/evidence/`
  and ignored runtime output under `runtime/protocol-research/`.
- Uses `tools/protocol-research/protocol_corpus_runner.py` and
  `tools/protocol-research/python_manager_probe.py`.
- Requires live 1C runtime and may require Vanessa/TestManager startup; it
  does not require committed provider payloads or raw capture files.
