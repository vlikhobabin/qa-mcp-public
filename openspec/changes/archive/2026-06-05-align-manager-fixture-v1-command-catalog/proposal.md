## Why

The capture runner currently seeds six manager fixture V1 commands, while the
manager harness source defines eleven. A live corpus pipeline needs one
reviewed command catalog so smoke scope, BSL source and evidence summaries do
not drift.

## What Changes

- Define the reviewed V1 read-only command ids and fields in one shared
  catalog source or generation contract.
- Align the PowerShell manifest generator, BSL manager catalog and reviewed
  command evidence with that catalog.
- Add an explicit smoke subset for the first live run.
- Keep action and mutation command kinds outside the V1 accepted catalog.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require the manager fixture V1 command catalog to be
  synchronized across BSL, capture runner manifests and reviewed evidence.

## Impact

- Touches protocol research tooling and external manager BSL source.
- Requires offline catalog/schema checks; live runtime is deferred to the
  capture and smoke changes.
- Does not claim new protocol mappings.
