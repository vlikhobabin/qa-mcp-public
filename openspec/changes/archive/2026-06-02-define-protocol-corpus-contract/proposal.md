## Why

The protocol research has moved past single-frame discovery into repeatable
read-only TestClient queries, but new claims still risk becoming ad hoc unless
each command has the same evidence shape. We need a corpus contract before
capturing many 1C testing API calls so future analysis can compare cases,
detect dynamic fields and decide what is replayable.

## What Changes

- Define the reviewed corpus evidence contract for marked protocol cases.
- Specify how a case maps a 1C testing API call to frame ranges, normalized
  request shapes, dynamic fields, response markers and replay/probe status.
- Define storage boundaries for raw runtime data versus compact reviewed
  evidence.
- Clarify that EDT/meta/help data may enrich semantic mapping but cannot replace
  capture/replay evidence for protocol claims.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: Add requirements for protocol corpus evidence,
  normalized case rows and replay confirmation.

## Impact

- Touches protocol research docs, OpenSpec requirements and future evidence
  reports.
- Does not implement protocol tooling or Python manager package code.
- Requires only offline capture evidence and existing docs for planning; live
  1C runtime is required later when the corpus runner produces fresh cases.
- Does not require EDT/meta snapshots, though those providers can inform
  semantic labels in later changes.
