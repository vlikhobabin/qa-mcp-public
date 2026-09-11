## Why

S4-R1 passes its clean offline composition and exact S3 control, but its first
passive marker-derivation row exits before a positive receipt. The retained
failure intentionally omits raw output, so a separately publishable test-only
observer is needed to classify the pre-receipt boundary without editing or
publishing the seven blocked S4-R1 paths.

## What Changes

- Add a new-path-only Go test diagnostic that launches the exact composed
  S4-R1 test candidate as an external child and emits one bounded typed
  classification only for argv identity mismatch, child launch failure,
  nonzero child exit without a checkpoint or nonzero child exit with a valid
  failed checkpoint. Harness setup/precondition, receipt freshness/allocation,
  timeout, checkpoint read/validation, unexpected zero exit and unsafe write
  abort fail-closed without an evidence row; `diagnostic_setup` remains a
  reserved validation enum with no live producer.
- Add hostile tests for schema/stage validation, privacy-safe serialization,
  nonzero-exit handling and the rule that a missing receipt or retry cannot be
  success.
- Run one exact S3 control and two passive S4 diagnostic rows on the authorized
  Windows contour, then publish a bounded resume hypothesis, a runbook or
  environment correction, or `NOT-VERIFIABLE` with an exact resume condition.
- Preserve the published base, all blocked S4-R1/S7/OSS-07 bytes, tracked EPFs,
  admission rules and exact-owned cleanup; add no public caller or action.

## Capabilities

### New Capabilities
- `qa-mcp-pre-receipt-marker-derivation-investigation`: Defines the bounded,
  privacy-safe test diagnostic and evidence-backed decision required before
  the blocked S4-R1 marker-derivation certification may resume.

### Modified Capabilities
- None.

## Impact

- Touches OpenSpec workflow, new test-only Go paths, curated protocol-research
  evidence/docs and ignored exact-contour runtime evidence.
- Does not modify protocol tools, Python manager code, MCP provider setup,
  runtime target configuration, public schemas or the blocked S4-R1/S7 payload.
- Requires passive live Windows `8.3.27.2214` evidence on the explicitly
  authorized `vanessa_client` target; Vanessa MCP, EDT/meta snapshots and raw
  protocol capture are not required.
