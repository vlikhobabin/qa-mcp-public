## Why

R5-R2 is published and defines the only safe positive-result core successor,
OSS-04D-R7. Because R7 is a repeated-defect implementation with a hard 300-line
cap, deterministic ChangeRail preflight requires one separately published,
exact authorization source with the minimum machine ceiling 301. Historical A2
is bound to exhausted R5 and cannot be reused.

## What Changes

- Publish one closed six-field authorization object bound exactly from completed
  R5-R2 to future in-progress R7.
- Make R5-R2, A4 and R7 board relations reciprocal and fail closed under any
  id/path/source mismatch.
- Preserve the distinction between machine ceiling 301 and R7's stricter
  at-most-300 production-line cap.
- Prove an isolated finalized exact candidate is accepted and a bounded
  mismatched successor is rejected.

## Capabilities

### New Capabilities

- `qa-mcp-positive-core-operation-boundary-authorization`: exact published A4
  authorization source and reciprocal fail-closed consumption contract for R7.

### Modified Capabilities

- None.

## Impact

OpenSpec and board metadata only. No Python, tests, runtime, protocol, Windows,
Docker, TestClient, live 1C, dependency or external-state change.
